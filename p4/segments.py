"""Resampling, segmentation, dry mass, noise floor (PREREG_P4 sections 3.3, 3.5 and 6).

Pure functions on p4.data.Run objects. Nothing here involves a model.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from p4.data import Run, plateaus

DT_MIN = 0.1  # 6 s grid


def resample(run: Run, dt: float = DT_MIN) -> dict:
    """Linear resampling of mass, measured RH, set-point RH and temperature to a uniform grid.
    The set-point is resampled by previous value (it is piecewise constant)."""
    t = run.t
    ok = np.isfinite(t) & np.isfinite(run.mass) & np.isfinite(run.rh)
    t, m, rh, tg = t[ok], run.mass[ok], run.rh[ok], run.rh_target[ok]
    order = np.argsort(t, kind="stable")
    t, m, rh, tg = t[order], m[order], rh[order], tg[order]
    keep = np.r_[True, np.diff(t) > 0]
    t, m, rh, tg = t[keep], m[keep], rh[keep], tg[keep]
    grid = np.arange(t[0], t[-1] + 1e-9, dt)
    idx = np.clip(np.searchsorted(t, grid, side="right") - 1, 0, len(t) - 1)
    temp = run.temp[ok][order][keep]
    return {
        "t": grid,
        "mass": np.interp(grid, t, m),
        "rh": np.interp(grid, t, rh),
        "rh_target": tg[idx],
        "temp": np.interp(grid, t, temp) if np.isfinite(temp).any() else np.full(len(grid), np.nan),
    }


def dry_mass_post_activation(run: Run, min_preheat: float = 50.0, window_min: float = 1.0,
                             min_len_min: float = 5.0):
    """Rule R2: the 0 % RH stretch that follows the heated activation within the same 0 % set-point
    (preheater off, so gas and temperature are those of the rest of the run). m_dry is the median
    mass over its last `window_min` minutes. Applies only if that stretch lasts >= `min_len_min`.
    Returns (m_dry, info) or (None, reason)."""
    pre = run.preheater_target
    if not np.isfinite(pre).any():
        return None, "no preheater column"
    hot = (pre >= min_preheat) & (run.rh_target <= 0.5)
    if not hot.any():
        return None, "no activation stage"
    i1 = int(np.argmax(hot))
    while i1 + 1 < len(hot) and hot[i1 + 1]:
        i1 += 1
    j = i1 + 1
    while j < len(run.rh_target) and run.rh_target[j] <= 0.5 and not (np.isfinite(pre[j]) and pre[j] >= min_preheat):
        j += 1
    if j - (i1 + 1) < 2 or run.t[j - 1] - run.t[i1 + 1] < min_len_min:
        return None, "no 0 % stretch after activation"
    tt = run.t[i1 + 1:j]
    sel = tt >= tt[-1] - window_min
    return float(np.median(run.mass[i1 + 1:j][sel])), {"end_time_min": float(tt[-1]),
                                                      "activation_end_min": float(run.t[i1]),
                                                      "stretch_min": float(tt[-1] - tt[0])}


def dry_mass_first_desorption(run: Run, min_preheat: float = 50.0, window_min: float = 1.0):
    """Rule R3 (the rule the first R2 implementation actually measured, 2026-11-08): the end of
    the first unheated 0 % plateau after activation, i.e. the end of the first desorption step."""
    m_act, info = dry_mass_step_run(run, min_preheat, window_min)
    if m_act is None:
        return None, info
    t_end = info["end_time_min"]
    pre = run.preheater_target
    for a, b in plateaus(run.rh_target):
        hot = np.isfinite(pre[a]) and pre[a] >= min_preheat
        if run.t[a] >= t_end - 1e-6 and run.rh_target[a] <= 0.5 and not hot:
            sel = run.t[a:b] >= run.t[b - 1] - window_min
            return float(np.median(run.mass[a:b][sel])), {"end_time_min": float(run.t[b - 1]),
                                                          "activation_end_min": t_end}
    return None, "no unheated 0 % plateau after activation"


def dry_mass_step_run(run: Run, min_preheat: float = 50.0, window_min: float = 1.0):
    """Dry mass of a step run: median mass over the last `window_min` minutes of the initial
    activation stage (preheater set-point >= `min_preheat` deg C at 0 % RH). Returns
    (m_dry, info) or (None, reason)."""
    pre = run.preheater_target
    if not np.isfinite(pre).any():
        return None, "no preheater column"
    hot = (pre >= min_preheat) & (run.rh_target <= 0.5)
    if not hot.any():
        return None, "no activation stage"
    i0 = int(np.argmax(hot))
    i1 = i0
    while i1 + 1 < len(hot) and hot[i1 + 1]:
        i1 += 1
    seg_t = run.t[i0:i1 + 1]
    sel = seg_t >= seg_t[-1] - window_min
    m = float(np.median(run.mass[i0:i1 + 1][sel]))
    return m, {"activation_min": float(seg_t[-1] - seg_t[0]), "end_time_min": float(seg_t[-1])}


@dataclass
class Segment:
    source: str
    index: int            # plateau number in the run
    rh_from: float        # set-point before
    rh_to: float          # set-point during
    t: np.ndarray         # minutes since the set-point change
    rh: np.ndarray        # measured RH, percent
    temp: np.ndarray
    w: np.ndarray         # uptake, wt% (NaN-free)
    m_dry: float


def step_segments(run: Run, m_dry: float, dt: float = DT_MIN, start_after_min: float | None = None):
    """Split a resampled step run into plateaus of constant set-point. Plateaus that begin
    before `start_after_min` (the end of activation) are skipped."""
    r = resample(run, dt)
    out = []
    for k, (a, b) in enumerate(plateaus(r["rh_target"])):
        if k == 0 or b - a < 5:
            continue
        if start_after_min is not None and r["t"][a] < start_after_min:
            continue
        w = 100.0 * (r["mass"][a:b] - m_dry) / m_dry
        out.append(Segment(run.source, k, float(r["rh_target"][a - 1]), float(r["rh_target"][a]),
                           r["t"][a:b] - r["t"][a], r["rh"][a:b], r["temp"][a:b], w, m_dry))
    return out


def normalised_rms(pred: np.ndarray, meas: np.ndarray) -> float:
    """PREREG metric E: RMS(pred - meas) / |measured change over the segment|."""
    n = min(len(pred), len(meas))
    dw = abs(meas[n - 1] - meas[0])
    if dw <= 0:
        return float("nan")
    return float(np.sqrt(np.mean((pred[:n] - meas[:n]) ** 2)) / dw)


MIN_DM_MG = 0.05      # AUDIT.md section 2.3: a step counts if |dm| >= 0.05 mg with the sign of the RH step


def is_scored(seg: Segment, min_mg: float = MIN_DM_MG) -> bool:
    """PREREG section 6 inclusion rule (review finding C1): the measured mass change over the
    segment is at least `min_mg` and has the sign of the set-point change."""
    dw = float(seg.w[-1] - seg.w[0])
    return abs(dw) * seg.m_dry / 100.0 >= min_mg and np.sign(dw) == np.sign(seg.rh_to - seg.rh_from)


def noise_floor_pairs(segments: list[Segment], min_dw: float | None = None):
    """Test-retest pairs within one run: same (rh_from, rh_to), consecutive repeats from the
    second repeat on, both scored by the section 6 inclusion rule (is_scored; `min_dw` in wt%
    restores the old 0.05 wt% rule). Returns list of (E, rh_from, rh_to, n_points)."""
    by_step: dict[tuple, list[Segment]] = {}
    for s in segments:
        by_step.setdefault((round(s.rh_from, 1), round(s.rh_to, 1)), []).append(s)
    out = []
    for (f, to), segs in by_step.items():
        segs = sorted(segs, key=lambda s: s.index)
        for a, b in zip(segs[1:], segs[2:]):
            n = min(len(a.w), len(b.w))
            if min_dw is not None and abs(a.w[n - 1] - a.w[0]) < min_dw:
                continue
            if min_dw is None and not (is_scored(a) and is_scored(b)):
                continue
            # compare the two responses as changes from their own start
            ea = a.w[:n] - a.w[0]
            eb = b.w[:n] - b.w[0]
            out.append((normalised_rms(ea, eb), f, to, n))
    return out
