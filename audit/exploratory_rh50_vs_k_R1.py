"""EXPLORATORY (post hoc; internal referee review 2026-11-15, item 2): the in-sample rank correlation of Supporting
Figure S1 under the sensitivity dry-mass rule R1. Own k'' per sorbent, temperature and direction is the in-sample
metric fit of results/prefreeze/reproduce_b0_R1.json; RH50 is recomputed from the pre-registered isotherms under R1
(the isotherm uptake depends on the dry mass), and under R2 the same way as a check against results/rh50.json.
Spearman rank correlation over the eight parent sorbents per stratum with its exact two-sided p (all 8! orderings),
as in audit/exploratory_rh50_vs_k.py.

usage: python -E -s audit/exploratory_rh50_vs_k_R1.py data_derived/bezrukov2023 results/exploratory/rh50_vs_k_R1.json
(run from the repo root)
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "audit"))
from exploratory_rh50_vs_k import PARENTS, spearman_exact  # noqa: E402
from p4.data import data_files, load_run  # noqa: E402
from p4.dataset import isotherm_for  # noqa: E402
from p4.physics import rh50  # noqa: E402


def main():
    root, out_p = sys.argv[1:3]
    runs = [load_run(os.path.join(root, f)) for f in data_files(root)]
    rh = {rule: {s: {T: rh50(isotherm_for(runs, s, T, rule)[0]) for T in ("27C", "60C")} for s in PARENTS}
          for rule in ("R1", "R2")}
    ref = json.load(open(os.path.join(ROOT, "results", "rh50.json"), encoding="utf-8"))["rh50"]
    check = max(abs(rh["R2"][s][T] - ref[s][T]) for s in PARENTS for T in ("27C", "60C"))
    k = json.load(open(os.path.join(ROOT, "results", "prefreeze", "reproduce_b0_R1.json"),
                       encoding="utf-8"))["per_material"]
    out = {"about": __doc__.split("\n\n")[0], "rh50_R1": rh["R1"], "rh50_R2_recomputed_max_abs_diff": check,
           "strata": {}}
    for T in ("27C", "60C"):
        for d in ("ads", "des"):
            pts = {r["sorbent"]: r["k2_own_metric"] for r in k if r["temp"] == T and r["dir"] == d}
            xs = [rh["R1"][s][T] for s in PARENTS]
            ys = [pts[s] for s in PARENTS]
            rho, p = spearman_exact(xs, ys)
            out["strata"][f"{T}|{d}"] = {"rho": rho, "p_exact": p, "points": {s: [rh["R1"][s][T], pts[s]] for s in PARENTS}}
            print(T, d, round(rho, 3), round(p, 3))
    out["summary"] = {"rho_min": min(v["rho"] for v in out["strata"].values()),
                      "rho_max": max(v["rho"] for v in out["strata"].values()),
                      "p_min": min(v["p_exact"] for v in out["strata"].values())}
    print("R2 RH50 recomputed vs results/rh50.json, max |diff|:", check)
    with open(out_p, "w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, indent=1)


if __name__ == "__main__":
    main()
