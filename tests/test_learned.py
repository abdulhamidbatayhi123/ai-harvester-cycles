import numpy as np
import pytest

torch = pytest.importorskip("torch")

from p4.learned import L1, L2, TorchBranch, integrate, isotherm_encoding  # noqa: E402
from p4.physics import Branch, simulate_b0  # noqa: E402

DT = 0.1


def s_iso(step=12.0, wmax=30.0):
    rh = np.linspace(0, 90, 46)
    w = wmax / (1 + np.exp(-(rh - step) / 1.5)) - wmax / (1 + np.exp(step / 1.5))
    return rh, w


def forcing(lo, hi, minutes):
    t = np.arange(0, minutes + DT / 2, DT)
    return np.where(t < 0.3, lo + (hi - lo) * t / 0.3, hi)


def ctx_for(rh_iso, w_iso, k_ads, k_des, m, n):
    b = Branch.from_points(rh_iso, w_iso)
    tb = TorchBranch(b.rh, b.w)
    return b, {"ads": tb, "w30": torch.tensor(float(b.w_of_rh(30.0)), dtype=torch.float64),
               "k_ads": torch.full((n,), k_ads, dtype=torch.float64),
               "k_des": torch.full((n,), k_des, dtype=torch.float64),
               "temp": torch.full((n,), 27.0, dtype=torch.float64),
               "m": torch.full((n,), 10.0, dtype=torch.float64)}


def test_l1_with_zero_correction_equals_b0():
    rh_iso, w_iso = s_iso()
    r = np.vstack([forcing(0, 30, 60), forcing(30, 0, 60)])
    w0 = np.array([0.0, 25.0])
    b, ctx = ctx_for(rh_iso, w_iso, 0.05, 0.03, 10.0, 2)
    model = L1()
    with torch.no_grad():
        for p in model.g.parameters():
            p.zero_()
        pred = integrate(model, torch.as_tensor(r), torch.as_tensor(w0), ctx, dt=DT).numpy()
    ref = simulate_b0(r, w0, 0.05, 0.03, b, dt=DT)
    assert np.allclose(pred, ref, atol=1e-8)


def test_l1_never_moves_against_driving_force_even_with_random_weights():
    torch.manual_seed(0)
    rh_iso, w_iso = s_iso()
    r = torch.as_tensor(np.vstack([forcing(0, 30, 80)]))
    _, ctx = ctx_for(rh_iso, w_iso, 0.08, 0.05, 10.0, 1)
    model = L1(width=16)
    with torch.no_grad():
        for p in model.g.parameters():
            p.normal_(0, 1.0)
        pred = integrate(model, r, torch.zeros(1, dtype=torch.float64), ctx, dt=DT)[0].numpy()
    assert np.all(np.diff(pred) >= -1e-12)
    assert pred.max() <= float(np.interp(30.0, rh_iso, w_iso)) + 1e-6


def test_gradients_flow_and_l2_runs():
    rh_iso, w_iso = s_iso()
    r = torch.as_tensor(np.vstack([forcing(0, 30, 10)]))
    _, ctx = ctx_for(rh_iso, w_iso, 0.08, 0.05, 10.0, 1)
    tb = ctx["ads"]
    ctx["enc"] = isotherm_encoding({(T, b): tb for T in (27, 60) for b in ("ads", "des")}, float(ctx["w30"]))
    for model, limit in [(L1(), True), (L2(), False)]:
        pred = integrate(model, r, torch.zeros(1, dtype=torch.float64), ctx, dt=DT, limit=limit)
        loss = (pred[:, -1] - 10.0).pow(2).sum()
        loss.backward()
        grads = [p.grad for p in model.parameters() if p.grad is not None]
        assert grads and all(torch.isfinite(g).all() for g in grads)
