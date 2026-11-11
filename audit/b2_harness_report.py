"""Numbers for PREREG section 10b from the evaluated B2 harness (audit/harness_b2.py --evaluate).

Prints and writes results/harness_b2/report.json: per world the beats, median r, median E_B0 and
E_B2 over folds, median b per stratum; the pass criteria; the K2 verdicts that set the wording of a
real falsification; C3; and the within-world correlation of null beats (moment estimator over the
six S worlds, reported only, PREREG section 10b).

usage: python -I audit/b2_harness_report.py results/harness_b2/harness_b2.json results/harness_b2/report.json
"""
import json
import sys

import numpy as np


def rho_moment(counts, n):
    """Intra-world correlation of binary beats from per-world counts (ANOVA moment estimator)."""
    k = len(counts)
    p = sum(counts) / (k * n)
    if p in (0.0, 1.0):
        return None
    msb = n * sum((c / n - p) ** 2 for c in counts) / (k - 1)
    msw = sum(c * (1 - c / n) for c in counts) / (k * (n - 1))
    return float((msb - msw) / (msb + (n - 1) * msw))


def main():
    res = json.load(open(sys.argv[1], encoding="utf-8"))
    W = res["worlds"]
    rep = {"pass": res["pass"], "summary": res["summary"], "worlds": {}}
    for w, v in sorted(W.items()):
        f = v["folds"].values()
        strata = sorted({k for x in f for k in x["b2_ab"]})
        rep["worlds"][w] = {
            "beats": int(sum(x["beats"] for x in f)), "folds": len(v["folds"]),
            "median_r": float(np.median([x["r"] for x in f])),
            "median_E_B0": float(np.median([x["E_B0"] for x in f])),
            "median_E_B2": float(np.median([x["E_B2"] for x in f])),
            "median_b": {s: float(np.median([x["b2_ab"][s][1] for x in f])) for s in strata},
            "beaten_folds": sorted(k for k, x in v["folds"].items() if x["beats"]),
            "max_violation_excess": float(max(x["violation_excess"] for x in f)),
        }
    nulls = [w for w in sorted(W) if w.startswith("S")]
    rep["null_within_world_rho"] = rho_moment([rep["worlds"][w]["beats"] for w in nulls], 8)
    json.dump(rep, open(sys.argv[2], "w", encoding="utf-8"), indent=1)
    print(json.dumps(rep, indent=1))


if __name__ == "__main__":
    main()
