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
    """rh: (n, L) forcing on a uniform grid (NaN after a segment ends); returns w (n, L).
    When the rows happen to be sorted by length (longest first), only the rows still running are
    integrated; the result is the same as integrating all rows."""
    rh = np.atleast_2d(np.asarray(rh, float))
    n, L = rh.shape
    w = np.full((n, L), np.nan)
    w[:, 0] = w0
    k_ads = np.broadcast_to(np.asarray(k_ads, float), (n,))
    k_des = np.broadcast_to(np.asarray(k_des, float), (n,))
    lens = np.isfinite(rh).sum(1)
    contiguous = bool(np.all(np.isfinite(rh) == (np.arange(L)[None, :] < lens[:, None])))
    prefix_ok = contiguous and bool(np.all(np.diff(lens) <= 0))
    for i in range(L - 1):
        if prefix_ok:
            k = int(np.searchsorted(-lens, -(i + 2), side="right"))   # rows with lens >= i + 2
            if k == 0:
                break
        else:
            k = n
        r0, r1 = rh[:k, i], rh[:k, i + 1]
        live = np.isfinite(r1)
        if not live.any():
            break
        a_k, d_k = ads, des
        ka, kd = k_ads[:k], k_des[:k]
        r0, r1 = np.where(live, r0, 0.0), np.where(live, r1, 0.0)
        rm = 0.5 * (r0 + r1)
        y = w[:k, i]
        f = lambda yy, rr: rate(yy, rr, ka, kd, a_k, d_k)
        k1 = f(y, r0)
        k2 = f(y + 0.5 * dt * k1, rm)
        k3 = f(y + 0.5 * dt * k2, rm)
        k4 = f(y + dt * k3, r1)
        yn = y + dt / 6.0 * (k1 + 2 * k2 + 2 * k3 + k4)
        f1 = f(y, r1)
        up = f1 > 0
        dn = f1 < 0
        eq_up = a_k.w_of_rh(r1)
        eq_dn = (a_k if d_k is None else d_k).w_of_rh(r1)
        yn = np.where(up, np.clip(yn, y, np.maximum(y, eq_up)), yn)
        yn = np.where(dn, np.clip(yn, np.minimum(y, eq_dn), y), yn)
        yn = np.where(~up & ~dn, y, yn)
        w[:k, i + 1] = np.where(live, yn, np.nan)
    return w


def simulate_b0(rh, w0, k_ads, k_des, ads: Branch, des: Branch | None = None, dt=0.1):
    """Bezrukov's model: dw/dt = k (RH_flow - RH_bed(w)); k_ads for uptake, k_des for release.
    RH_bed from the adsorption branch (B0) or, during release, the desorption branch (B0-b)."""
    return _integrate(_b0_rate, rh, w0, k_ads, k_des, ads, des, dt)


def simulate_b1(rh, w0, k_ads, k_des, ads: Branch, des: Branch | None = None, dt=0.1):
    """Linear driving force: dw/dt = k (w*(RH_flow) - w)."""
    return _integrate(_b1_rate, rh, w0, k_ads, k_des, ads, des, dt)


def _k_dir(k_rows, direction):
    return (k_rows, 0.0) if direction == "ads" else (0.0, k_rows)


def _preds(groups, simulate, k, direction, dt, k_of=None):
    """Predictions per group for pooled k'' (or k_of(group) giving k'' per group)."""
    for g in groups:
        kk = (k if k_of is None else k_of(g)) / np.asarray(g["m"], float)
        yield g, simulate(g["rh"], g["w"][:, 0], *_k_dir(kk, direction), g["ads"], g.get("des"), dt=dt)


def _seg_E(pred, w):
    """Per-segment scored metric E (section 6); NaN where the measured change is 0."""
    n = np.isfinite(w).sum(1)
    last = w[np.arange(len(w)), np.maximum(n - 1, 0)]
    dw = np.abs(last - w[:, 0])
    rms = np.sqrt(np.nanmean((pred - w) ** 2, axis=1))
    with np.errstate(invalid="ignore", divide="ignore"):
        return np.where(dw > 0, rms / dw, np.nan)


def fit_scale(groups, simulate, direction, dt=0.1, bounds=(1e-4, 1e3)):
    """Fit one material-independent constant k'' (rate constant = k''/m) for one direction.

    groups: list of dicts, one per material, with rh (n, L), w (n, L) measured, m (n,) dry
    masses, ads, des. Loss: mean over all segments of the mean squared trajectory error.
    """
    def loss(logk):
        se, cnt = 0.0, 0
        for g, pred in _preds(groups, simulate, np.exp(logk), direction, dt):
            seg_mse = np.nanmean((pred - g["w"]) ** 2, axis=1)
            se += float(np.sum(seg_mse))
            cnt += len(seg_mse)
        return se / max(cnt, 1)
    r = minimize_scalar(loss, bounds=(np.log(bounds[0]), np.log(bounds[1])), method="bounded",
                        options={"xatol": 1e-4})
    return float(np.exp(r.x))


def _median_E(groups, simulate, direction, dt, k=None, k_of=None):
    E = np.concatenate([_seg_E(p, g["w"]) for g, p in _preds(groups, simulate, k, direction, dt, k_of)])
    E = E[np.isfinite(E)]
    return float(np.median(E)) if len(E) else float("inf")


def fit_scale_metric(groups, simulate, direction, dt=0.1, k_start=None, half_width=0.5, n_grid=11,
                     max_shifts=6):
    """Fit by the SCORED metric (review findings F1, N5): the k'' that minimises the median over
    segments of E = RMS(pred - meas) / |measured change|. Used for the oracle B0* and for every
    physics comparator. The median is not smooth, so a log grid of `n_grid` points over
    +-`half_width` decades around `k_start` (default: the least-squares fit) is searched first; if
    the best point is at an edge, the window moves by one width (at most `max_shifts` times); a
    bounded scalar search then refines inside the best grid cell."""
    if k_start is None:
        k_start = fit_scale(groups, simulate, direction, dt=dt)
    med_e = lambda logk: _median_E(groups, simulate, direction, dt, k=np.exp(logk))
    c, hw = np.log(k_start), half_width * np.log(10)
    seen = {}
    for _ in range(max_shifts + 1):
        grid = np.linspace(c - hw, c + hw, n_grid)
        vals = [seen.setdefault(round(x, 9), med_e(x)) for x in grid]
        i = int(np.argmin(vals))
        if 0 < i < n_grid - 1:
            break
        c = grid[i] + (hw if i == n_grid - 1 else -hw)
    lo, hi = grid[max(i - 1, 0)], grid[min(i + 1, n_grid - 1)]
    r = minimize_scalar(med_e, bounds=(lo, hi), method="bounded", options={"xatol": 1e-4})
    best = r.x if r.fun <= vals[i] else grid[i]
    return float(np.exp(best))


def rh50(ads: Branch) -> float:
    """B2's isotherm descriptor: the RH (%) at which the adsorption branch reaches half of its
    uptake at 30 % RH."""
    return float(ads.rh_of_w(0.5 * float(ads.w_of_rh(30.0))))


def fit_b2(groups, direction, dt=0.1, metric=False):
    """B2 (H4a'): log k'' = a + b * (rh50/30 - xbar), fitted over the training groups of one
    temperature and direction, by least squares or (metric=True) by the median of E. xbar is the
    mean of rh50/30 over the training groups, so a and b are not correlated through an uncentred
    x, and Nelder-Mead starts from the pooled fit with an explicit simplex whose step in b is 0.5
    (SciPy's default step for a zero entry is 0.00025, which left b near 0; red-team M10,
    2026-11-10). groups: dicts as for fit_scale, each with one material's 'ads' (and 'des' for the
    B0-b variant). Returns (a, b, xbar, converged)."""
    from scipy.optimize import minimize
    xs = {id(g): rh50(g["ads"]) / 30.0 for g in groups}
    xbar = float(np.mean(list(xs.values())))
    k_of = lambda p: (lambda g: np.exp(p[0] + p[1] * (xs[id(g)] - xbar)))

    def loss(p):
        if metric:
            return _median_E(groups, simulate_b0, direction, dt, k_of=k_of(p))
        se, cnt = 0.0, 0
        for g, pred in _preds(groups, simulate_b0, None, direction, dt, k_of(p)):
            seg = np.nanmean((pred - g["w"]) ** 2, axis=1)
            se += float(np.sum(seg))
            cnt += len(seg)
        return se / max(cnt, 1)
    k0 = (fit_scale_metric if metric else fit_scale)(groups, simulate_b0, direction, dt=dt)
    a0 = float(np.log(k0))
    r = minimize(loss, [a0, 0.0], method="Nelder-Mead",
                 options={"xatol": 1e-3, "fatol": 1e-9 if not metric else 1e-6, "maxiter": 400,
                          "initial_simplex": np.array([[a0, 0.0], [a0 + 0.1, 0.0], [a0, 0.5]])})
    return float(r.x[0]), float(r.x[1]), xbar, bool(r.success)


def violations(traj, rh, dirs, ads: Branch = None, des: Branch = None, window=10, tol=0.05):
    """Physical violations per segment (PREREG section 6), defined without the isotherm: within
    a step whose set-point went up (dirs = +1), uptake falls, or within a step whose set-point
    went down (-1), uptake rises, by more than `tol` wt% over any non-overlapping window of
    `window` grid points (1 minute at 6 s). Tests against the isotherm-derived driving force or
    the isotherm itself are not used: the measured data fail them in 50 to 100 % of segments,
    because measured equilibria differ from the isotherm (section 12). `ads`/`des` are unused
    and kept for the call signature. Returns a boolean array (n,)."""
    traj = np.atleast_2d(traj)
    out = np.zeros(len(traj), bool)
    for i, (w, d) in enumerate(zip(traj, dirs)):
        w = w[np.isfinite(w)]
        n = (len(w) - 1) // window
        if n < 1:
            continue
        ch = w[window: n * window + 1: window] - w[0: n * window: window]
        out[i] = bool(np.any(ch * d < -tol))
    return out
