"""EXPLORATORY (post hoc; final review 2026-11-16): numbers asked for by the editor-level and statistics reviews,
computed from frozen inputs with the stored confirmatory parameters (no refit, no new model):

1. dry_mass: range and median of the dry mass (mg) of the samples whose segments enter the primary set P, under R2;
2. metric_cv: coefficient of variation (sample SD / mean) of the eight parent sorbents' own rate constants fitted by
   the scored metric (k2_own_metric in results/prefreeze/reproduce_b0.json), beside the least-squares values that
   reproduce_b0.json already gives (k2_cv_across_8_sample_sd);
3. t63_B0: B0's error in the time to 63 % of a step on the held-out sorbents (fold's pooled k'' from
   results/confirm_R2/rows.jsonl, exactly as audit/secondary_metrics.py): signed relative error
   (t63_pred - t63_meas) / t63_meas, its median, the share of segments where B0 predicts a slower step, the 90th
   percentile of the absolute error, all over held-out segments, and the median over folds of the per-fold median
   absolute error.

usage: python -I audit/exploratory_review_20261116.py data_derived/bezrukov2023 results/exploratory/review_20261116.json
(from the repository root)
"""
import json
import os
import statistics
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from p4.dataset import build_groups  # noqa: E402
from p4.physics import simulate_b0  # noqa: E402
from p4.run_study import COMPOSITE_OF, PRIMARY8, folds, physics_pred  # noqa: E402
from p4.segments import normalised_rms  # noqa: E402
from p4.train import segment_t63  # noqa: E402

PARENTS = ["ROS-037", "ROS-039", "ROS-040", "MOF-303", "MIL-160", "CAU-10", "Al-fumarate", "Syloid"]


def main():
    data, out_path = sys.argv[1], sys.argv[2]
    out = {"about": __doc__.split("\n\n")[0], "rule": "R2"}
    groups = [g for g in build_groups(data, rule="R2") if g["sorbent"] in PRIMARY8 + list(COMPOSITE_OF.values())]

    # 1. dry mass of the samples (one value per run) in P
    per_run = {}
    for g in groups:
        for run, m in zip(g["run"], g["m"]):
            per_run[str(run)] = float(m)
    ms = sorted(per_run.values())
    out["dry_mass"] = {"n_runs": len(ms), "min_mg": ms[0], "max_mg": ms[-1], "median_mg": statistics.median(ms)}

    # 2. CV of own k'' across the eight parents, both fits
    rows = json.load(open(os.path.join(ROOT, "results", "prefreeze", "reproduce_b0.json"), encoding="utf-8"))
    out["metric_cv"], out["ls_cv"] = {}, {}
    for T in ("27C", "60C"):
        for d in ("ads", "des"):
            for key, dst in (("k2_own_metric", "metric_cv"), ("k2_own", "ls_cv")):
                x = [next(r[key] for r in rows["per_material"] if r["sorbent"] == s and r["temp"] == T
                          and r["dir"] == d) for s in PARENTS]
                out[dst][f"{T}|{d}"] = statistics.stdev(x) / statistics.mean(x)
            assert abs(out["ls_cv"][f"{T}|{d}"] - rows["pooled"][f"{T}|{d}"]["k2_cv_across_8_sample_sd"]) < 1e-9

    # 3. signed t63 error of B0 on held-out sorbents
    crow = {r["fold"]: r for r in map(json.loads, open(os.path.join(ROOT, "results", "confirm_R2", "rows.jsonl"),
                                                       encoding="utf-8")) if r["key"].endswith("|physics")}
    signed, fold_med = [], {}
    for fold, held in folds():
        if not fold.startswith("LOSO"):
            continue
        p = crow[fold]
        assert p["B0_variant"] == "B0"
        te = [g for g in groups if g["sorbent"] in held]
        k2 = {tuple(k.split("|")): v for k, v in p["k2"].items()}
        pred = physics_pred(te, simulate_b0, k2, False)
        e = [normalised_rms(pp[:int(np.isfinite(ww).sum())], ww[:int(np.isfinite(ww).sum())])
             for g, P in zip(te, pred) for ww, pp in zip(g["w"], P)]
        assert np.allclose(e, p["E"]["B0"], rtol=1e-9, atol=1e-12, equal_nan=True), f"{fold}: B0 not reproduced"
        s_f = []
        for g, P in zip(te, pred):
            tm = segment_t63(g["w"])
            tp = segment_t63(np.where(np.isfinite(g["w"]), P, np.nan))
            s_f += [(tp[i] - tm[i]) / tm[i] for i in range(len(tm))]
        signed += s_f
        fold_med[fold] = float(np.nanmedian(np.abs(s_f)))
    s = np.asarray(signed, float)
    s = s[np.isfinite(s)]
    out["t63_B0"] = {"n_segments": int(s.size),
                     "median_abs": float(np.median(np.abs(s))),
                     "median_signed": float(np.median(s)),
                     "share_pred_slower": float(np.mean(s > 0)),
                     "p90_abs": float(np.percentile(np.abs(s), 90)),
                     "fold_medians_abs": fold_med,
                     "median_over_folds_abs": float(statistics.median(fold_med.values()))}
    sec = json.load(open(os.path.join(ROOT, "results", "secondary_metrics_R2.json"), encoding="utf-8"))
    assert abs(out["t63_B0"]["median_abs"] - sec["all"]["t63_B0"]) < 1e-9, "pooled median not reproduced"
    with open(out_path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(out, fh, indent=1)
    print(json.dumps({k: v for k, v in out.items() if k != "about"}, indent=1))


if __name__ == "__main__":
    main()
