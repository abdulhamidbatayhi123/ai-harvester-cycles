"""Size check of the realistic null world (PREREG section 10, review findings F2 and N3), for
replicates 0-2, against the real data, all computed by the same code:
  - B0's median E per sorbent, k'' refitted on the data in question (pooled over the 8 sorbents);
  - the within-file test-retest floor F per sorbent-temperature group (p4.segments.noise_floor_pairs
    on the scored segments of each run), so that the null world's noise can be compared with F.

usage: python -I audit/null_calibration.py data_derived/bezrukov2023 results/null_calibration.json
"""
import json, os, sys
from collections import defaultdict
from dataclasses import replace

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from p4.dataset import build_groups  # noqa: E402
from p4.segments import noise_floor_pairs  # noqa: E402
from synthetic_harness import PRIMARY8, b0_E, fit_k2, synthesise_null  # noqa: E402


def group_F(groups):
    """Median within-file F per 'sorbent|T', with each segment's uptake taken from g['w']."""
    out = {}
    for g in groups:
        by_run = defaultdict(list)
        for seg, row in zip(g["segments"], g["w"]):
            by_run[seg.source].append(replace(seg, w=np.asarray(row[np.isfinite(row)], float)))
        E = [e for segs in by_run.values() for e, *_ in noise_floor_pairs(segs)]
        out[f"{g['sorbent']}|{g['temp']}"] = {"F": float(np.median(E)) if E else None, "pairs": len(E)}
    return out


def summary(groups, k):
    per = {s: float(np.nanmedian(b0_E([g for g in groups if g["sorbent"] == s], k))) for s in PRIMARY8}
    return {"median_E_B0": per, "overall": float(np.median(list(per.values()))), "F": group_F(groups)}


def main():
    root, out = sys.argv[1:3]
    real = [g for g in build_groups(root) if g["sorbent"] in PRIMARY8]
    k_true = fit_k2(real)
    res = {"real": summary(real, k_true)}
    print("real", json.dumps(res["real"]), flush=True)
    for rep in range(3):
        syn, draws = synthesise_null(real, k_true, seed=rep)
        res[rep] = {"draws": draws, **summary(syn, fit_k2(syn))}
        print(rep, json.dumps({k: v for k, v in res[rep].items() if k != "draws"}), flush=True)
    json.dump(res, open(out, "w"), indent=1)


if __name__ == "__main__":
    main()
