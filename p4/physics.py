"""Physics baselines of PREREG_P4 section 5: B0 / B0-b (Bezrukov 2023) and B1 (linear driving force).

Models integrate dw/dt on the measured forcing with classical RK4 on a uniform time grid
(6 s after resampling), forcing linearly interpolated inside a step, for a batch of segments
of one material at once (rows = segments, NaN-padded at the end).

Where the isotherm is flat, dRH_bed/dw is large and the equation is stiff; plain RK4 then
overshoots equilibrium and drives uptake against the driving force. The exact solution for a
fixed RH never crosses equilibrium, so each step is limited to lie between the current uptake
and the equilibrium uptake for the RH at the end of the step. Away from equilibrium the limiter
is inactive.

Units: uptake w in wt%, RH in percent, time in minutes, dry mass m in mg.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.optimize import minimize_scalar


@dataclass
class Branch:
    """One isotherm branch as monotone piecewise-linear maps RH -> w and w -> RH."""
    rh: np.ndarray
    w: np.ndarray

    @classmethod
    def from_points(cls, rh, w):
        o = np.argsort(rh)
        rh = np.asarray(rh, float)[o]
        w = np.maximum.accumulate(np.asarray(w, float)[o])   # monotone non-decreasing
        w = w + np.arange(len(w)) * 1e-9                       # strictly increasing for the inverse
        return cls(rh, w)

    def w_of_rh(self, rh):
        return np.interp(rh, self.rh, self.w)

    def rh_of_w(self, w):
        return np.interp(w, self.w, self.rh)


def _b0_rate(w, r, k_ads, k_des, ads, des):
    d_ads = r - ads.rh_of_w(w)
    d_rel = d_ads if des is None else r - des.rh_of_w(w)
    return np.where(d_ads > 0, k_ads * d_ads, k_des * np.minimum(d_rel, 0.0))


def _b1_rate(w, r, k_ads, k_des, ads, des):
    d_ads = ads.w_of_rh(r) - w
    d_rel = d_ads if des is None else des.w_of_rh(r) - w
    return np.where(d_ads > 0, k_ads * d_ads, k_des * np.minimum(d_rel, 0.0))


def _integrate(rate, rh, w0, k_ads, k_des, ads, des, dt):
    """rh: (n, L) forcing on a uniform grid (NaN after a segment ends); returns w (n, L)."""
    rh = np.atleast_2d(np.asarray(rh, float))
    n, L = rh.shape
    w = np.full((n, L), np.nan)
    w[:, 0] = w0
    k_ads = np.broadcast_to(np.asarray(k_ads, float), (n,))
    k_des = np.broadcast_to(np.asarray(k_des, float), (n,))
    eq_up = lambda r: ads.w_of_rh(r)
    eq_dn = lambda r: (ads if des is None else des).w_of_rh(r)
    for i in range(L - 1):
        r0, r1 = rh[:, i], rh[:, i + 1]
        live = np.isfinite(r1)
        if not live.any():
            break
        r0, r1 = np.where(live, r0, 0.0), np.where(live, r1, 0.0)
        rm = 0.5 * (r0 + r1)
        y = w[:, i]
        f = lambda yy, rr: rate(yy, rr, k_ads, k_des, ads, des)
        k1 = f(y, r0)
        k2 = f(y + 0.5 * dt * k1, rm)
        k3 = f(y + 0.5 * dt * k2, rm)
        k4 = f(y + dt * k3, r1)
        yn = y + dt / 6.0 * (k1 + 2 * k2 + 2 * k3 + k4)
        up = f(y, r1) > 0
        dn = f(y, r1) < 0
        yn = np.where(up, np.clip(yn, y, np.maximum(y, eq_up(r1))), yn)
        yn = np.where(dn, np.clip(yn, np.minimum(y, eq_dn(r1)), y), yn)
        yn = np.where(~up & ~dn, y, yn)
        w[:, i + 1] = np.where(live, yn, np.nan)
    return w


def simulate_b0(rh, w0, k_ads, k_des, ads: Branch, des: Branch | None = None, dt=0.1):
    """Bezrukov's model: dw/dt = k (RH_flow - RH_bed(w)); k_ads for uptake, k_des for release.
    RH_bed from the adsorption branch (B0) or, during release, the desorption branch (B0-b)."""
    return _integrate(_b0_rate, rh, w0, k_ads, k_des, ads, des, dt)


def simulate_b1(rh, w0, k_ads, k_des, ads: Branch, des: Branch | None = None, dt=0.1):
    """Linear driving force: dw/dt = k (w*(RH_flow) - w)."""
    return _integrate(_b1_rate, rh, w0, k_ads, k_des, ads, des, dt)


def fit_scale(groups, simulate, direction, dt=0.1, bounds=(1e-4, 1e3)):
    """Fit one material-independent constant k'' (rate constant = k''/m) for one direction.

    groups: list of dicts, one per material, with rh (n, L), w (n, L) measured, m (n,) dry
    masses, ads, des. Loss: mean over all segments of the mean squared trajectory error.
    """
    def loss(logk):
        k = np.exp(logk)
        se, cnt = 0.0, 0
        for g in groups:
            kk = k / np.asarray(g["m"], float)
            ka, kd = (kk, 0.0) if direction == "ads" else (0.0, kk)
            pred = simulate(g["rh"], g["w"][:, 0], ka, kd, g["ads"], g.get("des"), dt=dt)
            err = (pred - g["w"]) ** 2
            seg_mse = np.nanmean(err, axis=1)
            se += float(np.sum(seg_mse))
            cnt += len(seg_mse)
        return se / max(cnt, 1)
    r = minimize_scalar(loss, bounds=(np.log(bounds[0]), np.log(bounds[1])), method="bounded",
                        options={"xatol": 1e-4})
    return float(np.exp(r.x))
