"""Learned models of PREREG_P4 section 5: L1 (grey box) and L2 (neural ODE).

Both are integrated with the same limited RK4 as the physics baselines, in torch, batched over
segments of one material, so training can backpropagate through whole trajectories.

The held-out material enters only through its isotherms (adsorption and desorption branches at
the two temperatures), never through its name or kinetics.
"""
from __future__ import annotations

import numpy as np
import torch
from torch import nn

RH_GRID = np.linspace(0.0, 60.0, 11)   # isotherm encoding for L2 (percent RH)


def interp(x, xp, fp):
    """Piecewise-linear interpolation, differentiable in x, clamped at the ends."""
    x = torch.clamp(x, xp[0], xp[-1])
    i = torch.clamp(torch.searchsorted(xp, x.detach()) - 1, 0, len(xp) - 2)
    x0, x1, f0, f1 = xp[i], xp[i + 1], fp[i], fp[i + 1]
    return f0 + (f1 - f0) * (x - x0) / (x1 - x0)


class TorchBranch:
    def __init__(self, rh, w):
        self.rh = torch.as_tensor(np.asarray(rh, float), dtype=torch.float64)
        self.w = torch.as_tensor(np.asarray(w, float), dtype=torch.float64)

    def w_of_rh(self, r):
        return interp(r, self.rh, self.w)

    def rh_of_w(self, w):
        return interp(w, self.w, self.rh)

    def slope_at_w(self, w, h=0.25):
        """dw/dRH at the bed state, by a central difference on the inverse map."""
        r = self.rh_of_w(w)
        return (self.w_of_rh(r + h) - self.w_of_rh(r - h)) / (2 * h)


def mlp(n_in, width, depth, n_out=1):
    layers, d = [], n_in
    for _ in range(depth):
        layers += [nn.Linear(d, width), nn.Tanh()]
        d = width
    layers.append(nn.Linear(d, n_out))
    net = nn.Sequential(*layers).double()
    with torch.no_grad():                 # start as the identity correction / small rate
        net[-1].weight.mul_(0.01)
        net[-1].bias.zero_()
    return net


class L1(nn.Module):
    """dw/dt = k (RH_flow - RH_bed(w)) * exp(2 tanh(g(z))). The factor lies in [e^-2, e^2], is
    positive, and leaves the equilibrium and the sign of the rate unchanged."""

    def __init__(self, width=16, depth=2):
        super().__init__()
        self.g = mlp(7, width, depth)

    def rate(self, w, r, ctx):
        ads, w30 = ctx["ads"], ctx["w30"]
        r_bed = ads.rh_of_w(w)
        d = r - r_bed
        k = torch.where(d > 0, ctx["k_ads"], ctx["k_des"])
        z = torch.stack([w / w30, r / 100, r_bed / 100, ads.slope_at_w(w) * 10 / w30,
                         torch.sign(d), (ctx["temp"] - 27.0) / 33.0, 10.0 / ctx["m"]], -1)
        return k * d * torch.exp(2 * torch.tanh(self.g(z).squeeze(-1)))

    def equilibrium(self, r, ctx):
        e = ctx["ads"].w_of_rh(r)
        return e, e


L2_SCALE = 10.0  # typical k'' (0.2-0.4) times a 30 % RH driving force, so f is of order 1


class L2(nn.Module):
    """Black-box neural ODE: dw/dt = (S / m) * f(z), S = L2_SCALE (fixed, wt% mg per minute).

    z gives the network the same isotherm information as L1, as local features at the current
    state, but none of L1's structure (no sign constraint, no zero rate at equilibrium, no
    limiter): w/w30, RH, equilibrium uptake on both branches at the current RH (/w30), bed RH on
    both branches at the current uptake, the adsorption-branch slope at w, T and 1/m.

    Harness round 2 showed why the first design (a raw 44-number isotherm encoding) is not a fair
    competitor: with six training sorbents the network memorised material identity, fitting the
    training sorbents (loss <= 0.009) but not an unseen one (validation E 0.35 to 0.44)."""

    def __init__(self, width=32, depth=2):
        super().__init__()
        self.f = mlp(9, width, depth)

    def rate(self, w, r, ctx):
        ads, des, w30 = ctx["ads"], ctx.get("des", ctx["ads"]), ctx["w30"]
        z = torch.stack([w / w30, r / 100, ads.w_of_rh(r) / w30, des.w_of_rh(r) / w30,
                         ads.rh_of_w(w) / 100, des.rh_of_w(w) / 100, ads.slope_at_w(w) * 10 / w30,
                         (ctx["temp"] - 27.0) / 33.0, 10.0 / ctx["m"]], -1)
        # Output = water mass flux (S/m maps it to wt% per minute; an identity, since w is
        # 100 * water mass / dry mass). Round 3 scaled the output by w30 instead, a per-sorbent
        # number the network never sees, so it could not get the rate scale of a new sorbent.
        return (L2_SCALE / ctx["m"]) * self.f(z).squeeze(-1)


def integrate(model, rh, w0, ctx, dt=0.1, limit=True):
    """Batched RK4 with the same no-overshoot limiter as p4.physics (when `limit`).
    rh: (n, L) tensor, NaN-padded; returns (n, L) predictions (NaN where padded)."""
    n, L = rh.shape
    ws = [w0]
    y = w0
    for i in range(L - 1):
        r0, r1 = rh[:, i], rh[:, i + 1]
        live = torch.isfinite(r1)
        if not bool(live.any()):
            ws += [torch.full_like(y, float("nan"))] * (L - 1 - i)
            break
        r0 = torch.nan_to_num(r0)
        r1 = torch.nan_to_num(r1)
        rm = 0.5 * (r0 + r1)
        f = lambda yy, rr: model.rate(yy, rr, ctx)
        k1 = f(y, r0)
        k2 = f(y + 0.5 * dt * k1, rm)
        k3 = f(y + 0.5 * dt * k2, rm)
        k4 = f(y + dt * k3, r1)
        yn = y + dt / 6.0 * (k1 + 2 * k2 + 2 * k3 + k4)
        if limit:
            eq_up, eq_dn = model.equilibrium(r1, ctx)
            f1 = f(y, r1)
            yn = torch.where(f1 > 0, torch.minimum(torch.maximum(yn, y), torch.maximum(y, eq_up)), yn)
            yn = torch.where(f1 < 0, torch.maximum(torch.minimum(yn, y), torch.minimum(y, eq_dn)), yn)
        y = torch.where(live, yn, y)
        ws.append(torch.where(live, yn, torch.full_like(yn, float("nan"))))
    return torch.stack(ws, 1)


def isotherm_encoding(branches: dict, w30: float) -> torch.Tensor:
    """branches: {(T, 'ads'|'des'): TorchBranch} for T in (27, 60); returns (1, 44) tensor."""
    g = torch.as_tensor(RH_GRID, dtype=torch.float64)
    parts = [branches[(T, b)].w_of_rh(g) / w30 for T in (27, 60) for b in ("ads", "des")]
    return torch.cat(parts).unsqueeze(0)
