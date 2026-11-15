"""EXPLORATORY (post hoc; internal referee review 2026-11-15, item 1): the relative improvement r of the oracle B0*
(each held-out sorbent's own k'', fitted on its own data by the scored metric) over the pooled B0 of the same
variant, computed with the decision rule's own definition (p4.decide: cluster means of the segment values, r = median
cluster d over the median cluster E of B0, the smaller per-material value in a parent + composite fold). B2 changes
only k'' relative to B0, so the oracle shows what any per-sorbent rate constant could reach under the rule: H4a' needs
r >= 10 % on at least 7 of the 8 LOSO folds to be supported.

usage: python -E -s audit/exploratory_oracle_r.py results/confirm_R2/rows.jsonl results/prefreeze/checks2.json \
           results/exploratory/oracle_r_R2.json
(run from the repo root; the same for R1)
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from p4.decide import REL, cluster_level, rule, sorbent_F  # noqa: E402


def main():
    rows_p, checks_p, out_p = sys.argv[1:4]
    rows = [json.loads(line) for line in open(rows_p, encoding="utf-8")]
    F = sorbent_F(json.load(open(checks_p, encoding="utf-8")))
    phys = {r["fold"]: r for r in rows if r["key"].endswith("|physics")}
    folds = {}
    for fold, p in sorted(phys.items()):
        if p["E"].get("B0star") is None:
            continue
        b0, m, D, mat, dd = cluster_level(p["seg"], p["E"]["B0"], p["E"]["B0star"], p.get("dw"), with_d=True)
        per = {}
        for s in p["held"]:
            sel = mat == s
            if sel.any():
                ok, info = rule(b0[sel], m[sel], F.get(s, 0.0), D[sel], dd[sel])
                per[s] = {"r": info["r"], "rule_met": bool(ok), "n_clusters": info["n_clusters"]}
        if per:
            folds[fold] = {"per_material": per, "r_fold": min(v["r"] for v in per.values()),
                           "rule_met": all(v["rule_met"] for v in per.values())}
    loso = {k: v for k, v in folds.items() if k.startswith("LOSO:")}
    out = {"about": __doc__.split("\n\n")[0], "rows": rows_p, "margin": REL, "folds": folds,
           "summary": {"n_loso": len(loso),
                       "n_loso_r_ge_margin": int(sum(v["r_fold"] >= REL for v in loso.values())),
                       "n_loso_rule_met": int(sum(v["rule_met"] for v in loso.values())),
                       "r_fold_min": min(v["r_fold"] for v in loso.values()),
                       "r_fold_max": max(v["r_fold"] for v in loso.values())}}
    with open(out_p, "w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, indent=1)
    for k, v in loso.items():
        print(f"{k:24s} r_fold {100 * v['r_fold']:6.1f} %  rule met: {v['rule_met']}")
    print(json.dumps(out["summary"]))


if __name__ == "__main__":
    main()
