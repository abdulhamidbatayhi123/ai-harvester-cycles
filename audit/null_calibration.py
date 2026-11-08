"""Size check of the realistic null world (PREREG section 10, review finding F2): B0's median E
on synthetic null data, per sorbent, for replicates 0-2, with k'' refitted on the null data.

usage: python -I audit/null_calibration.py data_derived/bezrukov2023 results/null_calibration.json
"""
import json, os, sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from p4.dataset import build_groups  # noqa: E402
from synthetic_harness import PRIMARY8, b0_E, fit_k2, synthesise_null  # noqa: E402


def main():
    root, out = sys.argv[1:3]
    real = [g for g in build_groups(root) if g["sorbent"] in PRIMARY8]
    k_true = fit_k2(real)
    res = {}
    for rep in range(3):
        syn, draws = synthesise_null(real, k_true, seed=rep)
        k_fit = fit_k2(syn)
        per = {s: float(np.nanmedian(b0_E([g for g in syn if g["sorbent"] == s], k_fit))) for s in PRIMARY8}
        res[rep] = {"draws_a_b": draws, "median_E_B0": per, "overall": float(np.median(list(per.values())))}
        print(rep, json.dumps(res[rep]), flush=True)
    json.dump(res, open(out, "w"), indent=1)


if __name__ == "__main__":
    main()
