import numpy as np

from p4.data import Run
from p4.segments import dry_mass_step_run, noise_floor_pairs, normalised_rms, resample, step_segments


def synthetic_step_run(noise=0.0, seed=0):
    """Activation (preheater 100 C, 0 % RH, 30 min), then 0-30-0-30-0-30-0 % RH, 20 min each,
    2 s sampling, first-order response with tau = 3 min, 10 mg dry, 25 wt% at 30 % RH."""
    rng = np.random.default_rng(seed)
    dt = 2 / 60
    t = np.arange(0, 30 + 7 * 20, dt)
    rh_t = np.zeros_like(t)
    pre = np.where(t < 30, 100.0, 0.0)
    for j in range(7):
        a = 30 + 20 * j
        rh_t[(t >= a) & (t < a + 20)] = 30.0 if j % 2 == 1 else 0.0
    w = np.zeros_like(t)
    for i in range(1, len(t)):
        w_eq = 25.0 * rh_t[i] / 30.0
        w[i] = w[i - 1] + dt * (w_eq - w[i - 1]) / 3.0
    m = 10.0 * (1 + w / 100) + rng.normal(0, noise, len(t))
    return Run("X/27C/synthetic.xls", "X", "27C", "step", t, m, rh_t, rh_t.copy(),
               np.full_like(t, 27.0), pre, {})


def test_resample_uniform_and_monotone():
    r = resample(synthetic_step_run())
    assert np.allclose(np.diff(r["t"]), 0.1)
    assert set(np.unique(r["rh_target"])) <= {0.0, 30.0}


def test_dry_mass_from_activation():
    m, info = dry_mass_step_run(synthetic_step_run())
    assert abs(m - 10.0) < 1e-9 and abs(info["activation_min"] - 30) < 0.1


def test_segments_and_uptake():
    run = synthetic_step_run()
    m, info = dry_mass_step_run(run)
    segs = step_segments(run, m, start_after_min=info["end_time_min"])
    ups = [s for s in segs if s.rh_to == 30.0]
    assert len(ups) == 3
    for s in ups:
        assert abs(s.w[-1] - 25.0 * (1 - np.exp(-20 / 3))) < 0.2   # reached ~equilibrium


def test_noise_floor_zero_for_identical_repeats_and_positive_with_noise():
    run = synthetic_step_run()
    m, info = dry_mass_step_run(run)
    pairs = noise_floor_pairs(step_segments(run, m, start_after_min=info["end_time_min"]))
    assert pairs and max(p[0] for p in pairs) < 0.02
    noisy = synthetic_step_run(noise=0.002, seed=1)
    pairs_n = noise_floor_pairs(step_segments(noisy, m, start_after_min=info["end_time_min"]))
    assert all(p[0] > 0 for p in pairs_n)


def test_normalised_rms():
    meas = np.linspace(0, 10, 101)
    assert normalised_rms(meas + 1.0, meas) == 0.1
