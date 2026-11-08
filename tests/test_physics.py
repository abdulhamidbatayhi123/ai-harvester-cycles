import numpy as np

from p4.physics import Branch, fit_scale, simulate_b0, simulate_b1

DT = 0.1  # minutes (6 s)


def s_isotherm(step_rh=12.0, wmax=30.0):
    rh = np.linspace(0, 90, 46)
    w = wmax / (1 + np.exp(-(rh - step_rh) / 1.5)) - wmax / (1 + np.exp(step_rh / 1.5))
    return Branch.from_points(rh, w)


def step_forcing(lo, hi, minutes=60.0):
    t = np.arange(0, minutes + DT / 2, DT)
    rh = np.where(t < 0.3, lo + (hi - lo) * t / 0.3, hi)   # 18 s ramp like the instrument
    return t, rh


def test_branch_inverse_roundtrip():
    b = s_isotherm()
    w = np.linspace(0.5, 29, 20)
    assert np.allclose(b.w_of_rh(b.rh_of_w(w)), w, atol=1e-6)


def test_b0_reaches_equilibrium_without_overshoot_and_is_zero_order_on_step():
    b = s_isotherm()
    t, rh = step_forcing(0.0, 30.0, minutes=200)
    w = simulate_b0(rh, 0.0, 0.05, 0.05, b, dt=DT)[0]
    assert abs(w[-1] - b.w_of_rh(30.0)) < 0.05
    assert np.all(np.diff(w) >= -1e-12)          # never against the driving force
    assert np.all(w <= b.w_of_rh(30.0) + 1e-9)   # never beyond equilibrium
    mid = (w > 5) & (w < 20)
    rate = np.gradient(w, t)[mid]
    assert rate.std() / rate.mean() < 0.1         # S-shaped isotherm -> near-constant rate


def test_release_is_monotone_and_ends_at_low_uptake():
    b = s_isotherm()
    t, rh = step_forcing(30.0, 0.0, minutes=300)
    w = simulate_b0(rh, float(b.w_of_rh(30.0)), 0.05, 0.03, b, dt=DT)[0]
    assert np.all(np.diff(w) <= 1e-12)
    assert w[-1] < 0.5


def test_limiter_inactive_away_from_equilibrium():
    # linear isotherm, LDF: exact exponential; the limiter must not change the answer
    b = Branch.from_points(np.array([0.0, 100.0]), np.array([0.0, 50.0]))
    t = np.arange(0, 100 + DT / 2, DT)
    k = 0.1
    w = simulate_b1(np.full_like(t, 40.0), 0.0, k, k, b, dt=DT)[0]
    assert np.allclose(w, 20.0 * (1 - np.exp(-k * t)), atol=1e-6)


def test_batch_matches_single_and_handles_padding():
    b = s_isotherm()
    _, r1 = step_forcing(0.0, 30.0, minutes=50)
    _, r2 = step_forcing(0.0, 60.0, minutes=30)
    batch = np.full((2, len(r1)), np.nan)
    batch[0], batch[1, :len(r2)] = r1, r2
    wb = simulate_b0(batch, [0.0, 0.0], [0.04, 0.02], [0.03, 0.03], b, dt=DT)
    w1 = simulate_b0(r1, 0.0, 0.04, 0.03, b, dt=DT)[0]
    w2 = simulate_b0(r2, 0.0, 0.02, 0.03, b, dt=DT)[0]
    assert np.allclose(wb[0], w1)
    assert np.allclose(wb[1, :len(r2)], w2) and np.all(np.isnan(wb[1, len(r2):]))


def test_fit_recovers_material_independent_constant():
    rng = np.random.default_rng(0)
    k_true = 0.6                                # k'' in wt%·mg/(min·%RH)
    groups = []
    for step_rh, masses in [(8.0, [5.0, 9.0]), (12.0, [10.0, 14.0]), (20.0, [15.0, 20.0])]:
        b = s_isotherm(step_rh)
        _, rh = step_forcing(0.0, 30.0, minutes=150)
        R = np.vstack([rh, rh])
        m = np.array(masses)
        w = simulate_b0(R, [0.0, 0.0], k_true / m, 0.0, b, dt=DT) + rng.normal(0, 0.02, R.shape)
        groups.append({"rh": R, "w": w, "m": m, "ads": b})
    k_hat = fit_scale(groups, simulate_b0, "ads", dt=DT)
    assert abs(k_hat / k_true - 1) < 0.02


def test_signflip_exact():
    import numpy as np
    from p4.decide import signflip_p
    assert abs(signflip_p(np.ones(6)) - 1 / 64) < 1e-12
    assert signflip_p(np.array([1.0, -1.0, 1.0, -1.0])) > 0.3
