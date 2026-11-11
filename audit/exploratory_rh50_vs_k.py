"""EXPLORATORY (post hoc; internal referee review 2026-11-11, minor 7): does a sorbent's own rate constant line up with
the descriptor RH50 at all? Own k'' per sorbent, temperature and direction is the in-sample metric fit of
results/prefreeze/reproduce_b0.json (R2; seen before the freeze, so this is descriptive only); RH50 from
results/rh50.json. Spearman rank correlation over the eight parent sorbents per stratum, with its exact two-sided
p (all 8! orderings), and the composites shown but not counted.

usage: python -I audit/exploratory_rh50_vs_k.py results/exploratory/rh50_vs_k.json
"""
import itertools
import json
import os
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PARENTS = ["ROS-037", "ROS-039", "ROS-040", "MOF-303", "MIL-160", "CAU-10", "Al-fumarate", "Syloid"]


def ranks(x):
    return np.argsort(np.argsort(x)).astype(float)


def spearman_exact(x, y):
    rx, ry = ranks(np.asarray(x)), ranks(np.asarray(y))
    rho = float(np.corrcoef(rx, ry)[0, 1])
    perm = [float(np.corrcoef(rx, np.array(p))[0, 1]) for p in itertools.permutations(ry)]
    p = float(np.mean([abs(v) >= abs(rho) - 1e-12 for v in perm]))
    return rho, p


def main():
    k = json.load(open(os.path.join(ROOT, "results", "prefreeze", "reproduce_b0.json"), encoding="utf-8"))["per_material"]
    rh = json.load(open(os.path.join(ROOT, "results", "rh50.json"), encoding="utf-8"))["rh50"]
    out = {"about": __doc__.split("\n\n")[0], "strata": {}}
    for T in ("27C", "60C"):
        for d in ("ads", "des"):
            pts = {r["sorbent"]: r["k2_own_metric"] for r in k if r["temp"] == T and r["dir"] == d}
            xs = [rh[s][T] for s in PARENTS]
            ys = [pts[s] for s in PARENTS]
            rho, p = spearman_exact(xs, ys)
            out["strata"][f"{T}|{d}"] = {"rho": rho, "p_exact": p,
                                         "points": {s: [rh[s][T], pts[s]] for s in pts if T in rh.get(s, {})}}
            print(T, d, round(rho, 3), round(p, 3))
    with open(sys.argv[1], "w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, indent=1)


if __name__ == "__main__":
    main()
