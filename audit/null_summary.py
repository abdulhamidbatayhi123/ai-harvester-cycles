"""Harness criterion 4 (PREREG section 10, review finding N1): false positives of the decision
rule in the realistic null world, from the decide.py outputs of null replicates.

Per learned model, over all its LOSO null fold-fits:
  (i)   no replicate has more than 2 of 8 beats;
  (ii)  the 90th percentile of r (median d / comparator median E per fold) is below 10 % and the
        mean of r is below 0;
  (iii) reported, not a pass condition: k beats in n fold-fits and the one-sided 95 %
        Clopper-Pearson upper bound on the per-fold beat rate.
Criterion 4 passes for a model if (i) and (ii) hold.

usage: python -I audit/null_summary.py results/null_summary.json results/null_rep0/decide.json [more ...]
"""
import json
import sys

import numpy as np
from scipy.stats import beta

MAX_BEATS_PER_REP = 2
R_Q90_MAX = 0.10
R_MEAN_MAX = 0.0


def main():
    out_path, files = sys.argv[1], sys.argv[2:]
    res = {}
    for kind in ("L1", "L2"):
        per, reps = [], {}
        for f in files:
            d = json.load(open(f, encoding="utf-8"))
            for key, v in d["folds"].items():
                if key.startswith("LOSO") and key.endswith("|" + kind):
                    r = v["median_gain"] / v["E_B0"]
                    reps[f] = reps.get(f, 0) + bool(v["beats_B0"])
                    per.append({"file": f, "fold": key, "beats": v["beats_B0"], "r": r,
                                "median_gain": v["median_gain"], "E_B0": v["E_B0"], "E_model": v["E_model"],
                                "p": v["p_signflip"]})
        if not per:
            continue
        n, k = len(per), sum(x["beats"] for x in per)
        r = np.array([x["r"] for x in per])
        c1 = max(reps.values()) <= MAX_BEATS_PER_REP
        q90, mean = float(np.quantile(r, 0.9)), float(r.mean())
        c2 = q90 < R_Q90_MAX and mean < R_MEAN_MAX
        p_up = float(beta.ppf(0.95, k + 1, n - k)) if k < n else 1.0
        res[kind] = {"fold_fits": n, "beats": k, "beats_per_replicate": reps,
                     "i_max_beats_per_rep_le_2": c1, "r_q90": q90, "r_mean": mean,
                     "ii_r_q90_lt_10pct_and_mean_lt_0": c2, "iii_rate_upper95_clopper_pearson": p_up,
                     "criterion_4_pass": bool(c1 and c2), "folds": per}
        print(f"{kind}: {k}/{n} beats (per rep {list(reps.values())}); r q90 {q90:.3f}, mean {mean:.3f}; "
              f"rate bound {p_up:.3f}; pass {c1 and c2}")
    json.dump(res, open(out_path, "w", encoding="utf-8"), indent=1)


if __name__ == "__main__":
    main()
