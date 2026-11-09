"""Harness criterion 4 (PREREG section 10, review findings N1, T-P4-4 F-5 and T-P4-5): false positives
of the decision rule in the realistic null world, from the decide.py outputs of null replicates.

A per-fold beat in the null world can come from sorbent-level luck: all clusters of a held-out sorbent
share one random rate draw, so a learned shift of the right sign gives p near 0 inside that fold. The
claim about new sorbents rests on the 7-of-8 count, so the criterion bounds the per-fold beat rate:
P(>= 7 of 8 | rate 0.40) = 0.0085 for independent folds, leaving room for positive dependence between
folds that share training sorbents.

Per learned model, over all its LOSO null fold-fits:
  (a) the one-sided 95 % Clopper-Pearson upper bound on the per-fold beat rate is at most 0.40
      (24 fold-fits: at most 5 beats; 16: at most 2);
  (b) no replicate has 5 or more of its 8 folds beaten (a direct check on fold dependence);
  (c) the mean of r over the null folds is below 2.5 % (a quarter of the 10 % practical margin; "mean
      below 0" would fail half the time for an exactly neutral model, review T-P4-4 F-5).
r is decide.py's r_fold (the smaller per-material r in a parent + composite fold, T-P4-4 F-6).
Criterion 4 passes for a model if (a), (b) and (c) hold.

usage: python -I audit/null_summary.py results/null_summary.json results/null_rep0/decide.json [more ...]
"""
import json
import sys

import numpy as np
from scipy.stats import beta

RATE_UPPER_MAX = 0.40
MAX_BEATS_PER_REP = 4
R_MEAN_MAX = 0.025


def cp_upper(k, n, level=0.95):
    return float(beta.ppf(level, k + 1, n - k)) if k < n else 1.0


def summarise(per, reps):
    n, k = len(per), sum(x["beats"] for x in per)
    r = np.array([x["r"] for x in per])
    up = cp_upper(k, n)
    ca = up <= RATE_UPPER_MAX
    cb = max(reps.values()) <= MAX_BEATS_PER_REP
    mean = float(r.mean())
    cc = mean < R_MEAN_MAX
    return {"fold_fits": n, "beats": k, "beats_per_replicate": reps,
            "a_rate_upper95_clopper_pearson": up, "a_pass": ca,
            "b_max_beats_per_rep": max(reps.values()), "b_pass": cb,
            "c_r_mean": mean, "c_pass": cc, "r_q90_reported": float(np.quantile(r, 0.9)),
            "criterion_4_pass": bool(ca and cb and cc)}


def main():
    out_path, files = sys.argv[1], sys.argv[2:]
    res = {}
    for kind in ("L1", "L2"):
        per, reps = [], {}
        for f in files:
            d = json.load(open(f, encoding="utf-8"))
            for key, v in d["folds"].items():
                if key.startswith("LOSO") and key.endswith("|" + kind):
                    r = v.get("r_fold", v["median_gain"] / v["E_B0"])
                    reps[f] = reps.get(f, 0) + bool(v["beats_B0"])
                    per.append({"file": f, "fold": key, "beats": v["beats_B0"], "r": r,
                                "median_gain": v["median_gain"], "E_B0": v["E_B0"], "E_model": v["E_model"],
                                "p": v["p_signflip"]})
        if not per:
            continue
        s = summarise(per, reps)
        res[kind] = {**s, "folds": per}
        print(f"{kind}: {s['beats']}/{s['fold_fits']} beats (per rep {list(reps.values())}); "
              f"rate bound {s['a_rate_upper95_clopper_pearson']:.3f}; r mean {s['c_r_mean']:.3f}; "
              f"pass {s['criterion_4_pass']}")
    json.dump(res, open(out_path, "w", encoding="utf-8"), indent=1)


if __name__ == "__main__":
    main()
