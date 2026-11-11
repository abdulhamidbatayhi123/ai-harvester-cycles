"""Secondary metrics of PREREG section 6 for the physics models, computed after the confirmatory runs (pre-registered
as secondary; no verdict). For each LOSO fold, with the fitted parameters stored in the confirmatory rows (pooled k''
of the fold's variant, B2's a, b, xbar; no refit) and B0* refitted on the held-out sorbent exactly as in
p4.run_study (fast, by the scored metric):

- the relative error in time-to-63 % per segment, |t63_pred - t63_meas| / t63_meas (p4.train.segment_t63);
- E truncated at five times the segment's measured time-to-63 %;
- physical violations, from the stored flags (share of held-out segments; data, B0, B2).

Writes results/secondary_metrics_<rule>.json with medians per held-out fold and over all held-out segments.

usage: python -E -s audit/secondary_metrics.py data_derived/bezrukov2023 R2     (from the repository root)
"""
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from p4.dataset import build_groups  # noqa: E402
from p4.physics import rh50, simulate_b0  # noqa: E402
from p4.run_study import COMPOSITE_OF, PRIMARY8, fit_physics, folds, physics_pred  # noqa: E402
from p4.segments import DT_MIN, normalised_rms  # noqa: E402
from p4.train import segment_t63  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def b2_pred(te, ab):
    out = []
    for g in te:
        x = rh50(g["ads"]) / 30.0
        pa, pd = ab[f"{g['temp']}|ads"], ab[f"{g['temp']}|des"]
        ka = np.exp(pa[0] + pa[1] * (x - pa[2])) / g["m"]
        kd = np.exp(pd[0] + pd[1] * (x - pd[2])) / g["m"]
        out.append(simulate_b0(g["rh"], g["w"][:, 0], ka, kd, g["ads"], None, dt=DT_MIN))
    return out


def seg_metrics(groups, preds):
    t63e, etr = [], []
    for g, p in zip(groups, preds):
        tm = segment_t63(g["w"])
        tp = segment_t63(np.where(np.isfinite(g["w"]), p, np.nan))
        for i, (ww, pp) in enumerate(zip(g["w"], p)):
            n = int(np.isfinite(ww).sum())
            t63e.append(abs(tp[i] - tm[i]) / tm[i])
            m = max(2, min(n, int(round(5 * tm[i] / DT_MIN)) + 1))
            etr.append(normalised_rms(pp[:m], ww[:m]))
    return t63e, etr


def main():
    data, rule = sys.argv[1], sys.argv[2]
    rows = {r["fold"]: r for r in map(json.loads, open(os.path.join(ROOT, "results", f"confirm_{rule}", "rows.jsonl"),
                                                     encoding="utf-8")) if r["key"].endswith("|physics")}
    groups = [g for g in build_groups(data, rule=rule) if g["sorbent"] in PRIMARY8 + list(COMPOSITE_OF.values())]
    med = lambda x: float(np.nanmedian(np.asarray(x, float)))
    out = {"rule": rule, "folds": {}, "all": {}}
    pool = {k: [] for k in ("t63_B0", "t63_B2", "t63_B0star", "Etr_B0", "Etr_B2", "Etr_B0star")}
    for fold, held in folds():
        if not fold.startswith("LOSO"):
            continue
        p = rows[fold]
        assert p["B0_variant"] == "B0"
        te = [g for g in groups if g["sorbent"] in held]
        k2 = {tuple(k.split("|")): v for k, v in p["k2"].items()}
        res = {}
        pb0, pb2 = physics_pred(te, simulate_b0, k2, False), b2_pred(te, p["B2_ab"])
        # the recomputed predictions must reproduce the confirmatory errors exactly (same parameters, same code)
        for key, pr in (("B0", pb0), ("B2", pb2)):
            e = [normalised_rms(pp[:int(np.isfinite(ww).sum())], ww[:int(np.isfinite(ww).sum())])
                 for g, P in zip(te, pr) for ww, pp in zip(g["w"], P)]
            assert np.allclose(e, p["E"][key], rtol=1e-9, atol=1e-12, equal_nan=True), f"{fold}: {key} not reproduced"
        res["B0"] = seg_metrics(te, pb0)
        res["B2"] = seg_metrics(te, pb2)
        star_t, star_e = [], []
        for s in held:
            own = [g for g in te if g["sorbent"] == s]
            k_own = fit_physics(own, simulate_b0, False)
            a, b = seg_metrics(own, physics_pred(own, simulate_b0, k_own, False))
            star_t += a
            star_e += b
        res["B0star"] = (star_t, star_e)
        f = {}
        for m, (t, e) in res.items():
            f[f"t63_relerr_{m}"], f[f"E_trunc_{m}"] = med(t), med(e)
            pool[f"t63_{m}"] += t
            pool[f"Etr_{m}"] += e
        n = len(p["viol_B2"])
        f["viol_share"] = {"data": sum(p["viol_data"]) / n, "B0": sum(p["viol_B0"]) / n, "B2": sum(p["viol_B2"]) / n}
        out["folds"][fold] = f
        print(fold, json.dumps(f), flush=True)
    out["all"] = {k: med(v) for k, v in pool.items()}
    out["all"]["n_folds_B2_t63_worse"] = sum(v["t63_relerr_B2"] > v["t63_relerr_B0"] for v in out["folds"].values())
    out["all"]["n_folds_B2_Etr_worse"] = sum(v["E_trunc_B2"] > v["E_trunc_B0"] for v in out["folds"].values())
    with open(os.path.join(ROOT, "results", f"secondary_metrics_{rule}.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(out, fh, indent=1)
    print("ALL", json.dumps(out["all"]))


if __name__ == "__main__":
    main()
