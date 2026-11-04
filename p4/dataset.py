"""Assemble the primary set P of PREREG_P4 section 3.2 into per-material groups of segments.

A group is one (sorbent, temperature): its isotherm branches (from the pre-registered isotherm
file) and its step segments on the 6 s grid, NaN-padded into (n, L) arrays for batched models.
"""
from __future__ import annotations

import os

import numpy as np

from p4.data import SORBENTS, load_run, plateaus, end_value
from p4.physics import Branch
from p4.segments import DT_MIN, dry_mass_step_run, step_segments

# Pre-registered isotherm choices (section 3.2): substring that identifies the file to use.
ISOTHERM_CHOICE = {
    ("MOF-303", "60C"): "_50-100um_60C_isotherm",
    ("ROS-037_composite", "27C"): "LATEST",
    ("ROS-039_composite", "27C"): "LATEST",
}
# Runs whose dry mass is not established (no drying to constant mass); excluded from P.
EXCLUDE_UNDRIED = ("ROS-037_composite/27C/", "ROS-039_composite/27C/")


def _dry_mass(run):
    m, info = dry_mass_step_run(run)
    if m is not None:
        return m, info
    for a, b in plateaus(run.rh_target):
        if run.rh_target[a] <= 0.5:
            return end_value(run.mass, run.t, a, b), {"end_time_min": float(run.t[b - 1])}
    return None, {}


def isotherm_for(runs, sorbent, temp_dir):
    cands = [r for r in runs if r.kind == "isotherm" and r.sorbent == sorbent and r.temp_dir == temp_dir]
    choice = ISOTHERM_CHOICE.get((sorbent, temp_dir))
    if choice == "LATEST":
        cands = sorted(cands, key=lambda r: r.source)[-1:]
    elif choice:
        cands = [r for r in cands if choice in r.source]
    if len(cands) != 1:
        raise ValueError(f"isotherm choice for {sorbent} {temp_dir} is ambiguous: {[r.source for r in cands]}")
    run = cands[0]
    m_dry, _ = _dry_mass(run)
    pls = plateaus(run.rh_target)
    rh = np.array([end_value(run.rh, run.t, a, b) for a, b in pls])
    w = np.array([100 * (end_value(run.mass, run.t, a, b) - m_dry) / m_dry for a, b in pls])
    tgt = np.array([run.rh_target[a] for a, b in pls])
    top = int(np.argmax(tgt))
    return Branch.from_points(rh[: top + 1], w[: top + 1]), Branch.from_points(rh[top:], w[top:]), run.source


def pad(arrs):
    L = max(len(a) for a in arrs)
    out = np.full((len(arrs), L), np.nan)
    for i, a in enumerate(arrs):
        out[i, : len(a)] = a
    return out


def build_groups(root, min_dw=0.05):
    runs = [load_run(os.path.join(root, f)) for f in sorted(os.listdir(root)) if f.endswith(".npz")]
    groups = []
    for s in SORBENTS:
        for T in ("27C", "60C"):
            steps = [r for r in runs if r.kind == "step" and r.sorbent == s and r.temp_dir == T
                     and not r.source.startswith(EXCLUDE_UNDRIED)]
            if not steps:
                continue
            ads, des, iso_src = isotherm_for(runs, s, T)
            segs = []
            for r in steps:
                m_dry, info = _dry_mass(r)
                for g in step_segments(r, m_dry, DT_MIN, start_after_min=info.get("end_time_min")):
                    if abs(g.w[-1] - g.w[0]) >= min_dw:
                        segs.append(g)
            groups.append({
                "sorbent": s, "temp": T, "iso_source": iso_src, "ads": ads, "des": des, "segments": segs,
                "rh": pad([g.rh for g in segs]), "w": pad([g.w for g in segs]),
                "m": np.array([g.m_dry for g in segs]),
                "dir": np.array([1 if g.rh_to > g.rh_from else -1 for g in segs]),
                "run": np.array([g.source for g in segs]),
            })
    return groups
