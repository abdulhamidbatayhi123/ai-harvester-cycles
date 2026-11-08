"""In-sample version of H4b (PREREG section 2, review finding F1a), seen before the freeze and
therefore descriptive only: per sorbent, the fraction of the gap between the pooled B0 and the
noise floor F that a sorbent-specific k'' closes, with both k'' fitted by the scored metric
(results/prefreeze/reproduce_b0.json, E_pooled_metric and E_own_metric) and F from checks2.json.
Per stratum (temperature x direction) and the segment-weighted mean per sorbent.

usage: python -I audit/h4b_insample.py results/prefreeze/reproduce_b0.json results/prefreeze/checks2.json results/prefreeze/h4b_insample.json
"""
import json
import sys
from collections import defaultdict

import numpy as np


def main():
    rep = json.load(open(sys.argv[1], encoding="utf-8"))
    F = json.load(open(sys.argv[2], encoding="utf-8"))["F_within_segment_weighted"]
    per = defaultdict(list)
    for r in rep["per_material"]:
        s = r["sorbent"]
        gap = r["E_pooled_metric"] - F[s]
        frac = (r["E_pooled_metric"] - r["E_own_metric"]) / gap if gap > 0 else float("nan")
        per[s].append({"stratum": f"{r['temp']}|{r['dir']}", "n_seg": r["n_seg"], "fraction": frac,
                       "E_pooled_metric": r["E_pooled_metric"], "E_own_metric": r["E_own_metric"]})
    out = {}
    for s, rows in per.items():
        w = np.array([x["n_seg"] for x in rows], float)
        f = np.array([x["fraction"] for x in rows])
        out[s] = {"strata": rows, "fraction_weighted": float(np.nansum(w * f) / w[np.isfinite(f)].sum()),
                  "fraction_max_stratum": float(np.nanmax(f))}
        print(f"{s:20s} weighted {out[s]['fraction_weighted']:.3f}  max stratum {out[s]['fraction_max_stratum']:.3f}")
    json.dump(out, open(sys.argv[3], "w", encoding="utf-8"), indent=1)


if __name__ == "__main__":
    main()
