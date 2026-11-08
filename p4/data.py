"""Data layer for Paper 4: load extracted DVS runs, find dry mass, segment, build isotherms.

Every rule here is a pre-registered data rule (PREREG_P4 section 3). Functions are pure and
take the arrays written by audit/extract_dvs.py.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field

import numpy as np

SORBENTS = ["ROS-037", "ROS-039", "ROS-040", "MOF-303", "MIL-160", "CAU-10", "Al-fumarate", "Syloid",
            "ROS-037_composite", "ROS-039_composite"]
PARENT = {"ROS-037_composite": "ROS-037", "ROS-039_composite": "ROS-039"}
FAMILY = {"MOF-303": "Al-rod", "MIL-160": "Al-rod", "CAU-10": "Al-rod", "Al-fumarate": "Al-rod",
          "ROS-039": "Zn-triazolate-F", "ROS-040": "Zn-triazolate-F", "ROS-039_composite": "Zn-triazolate-F",
          "ROS-037": "Cu-glutarate-bpy", "ROS-037_composite": "Cu-glutarate-bpy", "Syloid": "silica"}


@dataclass
class Run:
    source: str
    sorbent: str | None
    temp_dir: str | None
    kind: str                      # "isotherm" | "step" | "cycling" | "other"
    t: np.ndarray                  # minutes
    mass: np.ndarray               # mg
    rh_target: np.ndarray          # percent
    rh: np.ndarray                 # measured, percent
    temp: np.ndarray               # measured sample temperature, deg C (NaN if not logged)
    preheater_target: np.ndarray   # deg C (NaN if not logged)
    meta: dict = field(repr=False, default_factory=dict)


def _col(z, meta, *names):
    """Return the raw column whose header contains all given lowercase substrings."""
    for key, header in meta.get("raw_columns_kept", {}).items():
        h = header.lower()
        if all(n in h for n in names):
            return z[key]
    return None


def load_run(path: str) -> Run:
    z = np.load(path, allow_pickle=False)
    meta = json.loads(str(z["meta"]))
    src = meta["source_file"]
    parts = src.split("/")
    sorbent = parts[0] if parts[0] in SORBENTS else None
    temp_dir = parts[1] if len(parts) > 2 and parts[1] in ("27C", "60C") else None
    rh_t, rh_a = z["rh_target"].astype(float), z["rh_actual"].astype(float)
    if meta.get("rh_unit") == "fraction":
        rh_t, rh_a = rh_t * 100.0, rh_a * 100.0
    pre = _col(z, meta, "target preheater")
    n_levels = len(np.unique(np.round(rh_t[np.isfinite(rh_t)])))
    if n_levels >= 6:
        kind = "isotherm"
    elif "eatmap" in src:
        kind = "cycling"
    elif sorbent is not None and temp_dir is not None:
        kind = "step"
    else:
        kind = "other"
    return Run(src, sorbent, temp_dir, kind, z["time_min"].astype(float), z["mass_mg"].astype(float),
               rh_t, rh_a, z["temp_sample"].astype(float),
               pre.astype(float) if pre is not None else np.full(len(rh_t), np.nan), meta)


_DUP_CACHE: dict = {}


def duplicate_files(root: str) -> set:
    """Extracted files whose mass trace is identical to an earlier file's (found 2026-11-08: the
    Zenodo archive holds 8 such copies, among them the MOF-303 60 C 5 mg step run under two file
    names and each composite's 27 C isotherm in two folders). The copy kept is the first in
    sorted file-name order, the one in the sorbent's main folder; every other copy is listed."""
    import hashlib
    key = os.path.abspath(root)
    if key not in _DUP_CACHE:
        seen, dup = set(), set()
        for f in sorted(os.listdir(root)):
            if f.endswith(".npz"):
                with np.load(os.path.join(root, f)) as z:
                    h = hashlib.sha256(np.ascontiguousarray(z["mass_mg"]).tobytes()).hexdigest()
                (dup.add(f) if h in seen else seen.add(h))
        _DUP_CACHE[key] = dup
    return _DUP_CACHE[key]


def data_files(root: str) -> list[str]:
    """Sorted .npz file names of the extracted archive, exact duplicates removed."""
    dup = duplicate_files(root)
    return [f for f in sorted(os.listdir(root)) if f.endswith(".npz") and f not in dup]


def load_all(root: str) -> list[Run]:
    return [load_run(os.path.join(root, f)) for f in data_files(root)]


def plateaus(rh_target: np.ndarray, tol: float = 0.5) -> list[tuple[int, int]]:
    """Index ranges [a, b) of constant target RH."""
    edges = np.flatnonzero(np.abs(np.diff(rh_target)) > tol) + 1
    b = np.r_[0, edges, len(rh_target)]
    return [(int(b[i]), int(b[i + 1])) for i in range(len(b) - 1) if b[i + 1] > b[i]]


def end_value(x: np.ndarray, t: np.ndarray, a: int, b: int, window_min: float = 1.0) -> float:
    """Median of x over the last `window_min` minutes of the index range [a, b)."""
    sel = slice(a, b)
    tt = t[sel]
    m = tt >= tt[-1] - window_min
    return float(np.median(x[sel][m]))


@dataclass
class Isotherm:
    """Equilibrium end-points of an isotherm run, in percent RH and wt% uptake."""
    rh_ads: np.ndarray
    w_ads: np.ndarray
    rh_des: np.ndarray
    w_des: np.ndarray
    temp_set: float
    dry_mass: float
    source: str


def isotherm_from_run(run: Run, dry_mass: float) -> Isotherm:
    """End-point of every RH plateau; ascending plateaus form the adsorption branch, descending
    ones the desorption branch. The 0 % plateaus close both branches."""
    pls = plateaus(run.rh_target)
    rh = np.array([end_value(run.rh, run.t, a, b) for a, b in pls])
    w = np.array([100.0 * (end_value(run.mass, run.t, a, b) - dry_mass) / dry_mass for a, b in pls])
    tgt = np.array([run.rh_target[a] for a, b in pls])
    i_top = int(np.argmax(tgt))
    ads = slice(0, i_top + 1)
    des = slice(i_top, len(tgt))
    temp = run.temp[np.isfinite(run.temp)]
    t_meas = float(np.median(temp)) if temp.size else float("nan")
    return Isotherm(rh[ads], w[ads], rh[des][::-1], w[des][::-1], t_meas, dry_mass, run.source)
