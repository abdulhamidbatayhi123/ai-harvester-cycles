"""Apply the pre-registered decision rules (PREREG_P4 section 7) to the runner's rows.

Per fold, learned model and held-out MATERIAL (a parent and its composite are judged
separately, and both must pass; review finding C2), segment values are averaged within each
cluster (one RH step in one measuring session: both pans and all repeats). The model beats the
comparator on that material if
  1. median over clusters of d = E_base - E_model exceeds the material's F,
  2. median d >= 10 % of the comparator's median E over the same clusters, and
  3. a one-sided exact Wilcoxon signed-rank test over clusters of D = (E_base - E_model) * |dw|,
     the difference in unnormalised RMS error (wt%), gives p <= 0.025. Ranking D rather than d
     keeps the smallest steps from dominating the ranks (review finding C1).
A beat also needs physical admissibility: the share of segments where the model violates and
neither the data nor the comparator does is at most 5 points (review finding O3).
E_base is the comparator chosen among B0, B0-b and B1 (section 5).

H4a, L1 primary and L2 secondary: supported if the model beats the comparator on >= 7 of 8 LOSO
folds; falsified if at most one of the 8 LOSO folds has a relative improvement r = median d /
median E_base of at least 10 % (the 7th order statistic of r is then a one-sided 96.5 % upper
bound on the median of r below 10 %; review finding O1); otherwise not established. Transfer
across families requires both non-trivial LOFO folds (Al-rod, Zn-triazolate-F).
H4b (descriptive): the fraction of (E_B0 - F) that B0*, fitted by median E, closes per sorbent.

usage: python -E -s -m p4.decide <rows.jsonl> <results/prefreeze/checks2.json> <out.json>
(run from the repo root; -I would also hide the p4 package from -m)
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict

import numpy as np

REL = 0.10
ALPHA = 0.025
VIOL_MARGIN = 0.05
# The silica and Cu-glutarate LOFO folds hold out the same sorbents as their LOSO folds (review
# finding M6), so the family rule rests on the two folds that hold out a whole family.
NONTRIVIAL_LOFO = ("LOFO:Al-rod", "LOFO:Zn-triazolate-F")


def sorbent_F(checks2):
    """One F per sorbent: the segment-weighted mean of its within-file floors at 27 and 60 C
    (PREREG section 6), as computed before the freeze by audit/prefreeze_checks2.py."""
    return {s: float(v) for s, v in checks2["F_within_segment_weighted"].items()}


def material_of(sid):
    """The segment id starts with the experiment id '<sorbent>|<T>|<stamp>|...'."""
    return sid.split("|")[0]


def cluster_level(seg_ids, e_b0, e_m, dw=None):
    """Cluster means of E_base, E_model and of D = (E_base - E_model) * |dw| (NaN if dw is None),
    with the material of each cluster."""
    by = defaultdict(list)
    dw = [np.nan] * len(seg_ids) if dw is None else dw
    for sid, a, b, w in zip(seg_ids, e_b0, e_m, dw):
        if np.isfinite(a) and np.isfinite(b):
            by[sid.split("#")[0]].append((a, b, (a - b) * w))
    keys = list(by)
    b0 = np.array([np.mean([x[0] for x in by[k]]) for k in keys])
    m = np.array([np.mean([x[1] for x in by[k]]) for k in keys])
    D = np.array([np.mean([x[2] for x in by[k]]) for k in keys])
    mat = np.array([material_of(k) for k in keys])
    return b0, m, D, mat


def signflip_p(d, **_):
    """One-sided exact Wilcoxon signed-rank test of d > 0 over clusters. The statistic is the sum
    of the ranks of |d| over positive d (average ranks for ties). Its null distribution over all
    2**n sign vectors is computed exactly for any n by counting subset sums of the (doubled,
    hence integer) ranks; the attainable minimum p is 2**-n. The median is not used as the
    statistic: it ties heavily under sign flips (six equal gains give p = 0.34 instead of 1/64)."""
    from scipy.stats import rankdata
    d = np.asarray(d, float)
    d = d[d != 0]
    n = len(d)
    if n == 0:
        return 1.0
    r2 = np.rint(2 * rankdata(np.abs(d))).astype(int)      # average ranks are multiples of 1/2
    obs = int(r2[d > 0].sum())
    counts = [0] * (int(r2.sum()) + 1)                       # exact integer counts of subset sums
    counts[0] = 1
    top = 0
    for x in r2:
        for s in range(top, -1, -1):
            if counts[s]:
                counts[s + x] += counts[s]
        top += int(x)
    return float(sum(counts[obs:])) / float(2 ** n)


def rule(e_b0, e_m, F, D=None):
    """Section 7 for one material. D: cluster values of the unnormalised difference for the
    test; without it (old rows) the test falls back to d."""
    d = e_b0 - e_m
    gain = float(np.median(d))
    p = signflip_p(d if D is None or not np.all(np.isfinite(D)) else D)
    ok = bool(gain > F and gain >= REL * float(np.median(e_b0)) and p <= ALPHA)
    return ok, {"median_gain": gain, "p_signflip": p, "E_B0": float(np.median(e_b0)),
                "E_model": float(np.median(e_m)), "F": F, "n_clusters": int(len(d)),
                "min_attainable_p": float(2.0 ** -len(d))}


def main():
    rows = [json.loads(l) for l in open(sys.argv[1], encoding="utf-8")]
    F = sorbent_F(json.load(open(sys.argv[2], encoding="utf-8")))
    phys = {r["fold"]: r for r in rows if r["key"].endswith("|physics")}
    ens = {(r["fold"], r["kind"]): r for r in rows if r["key"].endswith("|ensemble")}
    out = {"folds": {}, "H4a": {}, "H4b": {}}
    for (fold, kind), r in sorted(ens.items()):
        p = phys[fold]
        assert p["seg"] == r["seg"], f"segment order differs in {fold}"
        held = p["held"]
        b0, m, D, mat = cluster_level(r["seg"], p["E"].get("base", p["E"]["B0"]), r["E"], p.get("dw"))
        per_mat = {}
        for s in held:
            sel = mat == s
            if sel.any():
                per_mat[s] = rule(b0[sel], m[sel], F.get(s, 0.0), D[sel])
        ok = bool(per_mat) and all(v[0] for v in per_mat.values())
        _, info = rule(b0, m, max(F.get(s, 0.0) for s in held), D)     # pooled, reported
        # physical admissibility (section 7, review finding O3): violations the model adds beyond
        # both the data and the comparator on the same segment
        vm = np.asarray(r.get("viol") or [], bool)
        vd = np.asarray(p.get("viol_data") or [False] * len(vm), bool)
        vb = np.asarray(p.get("viol_base") or [False] * len(vm), bool)
        excess = float(np.mean(vm & ~vd & ~vb)) if len(vm) else None
        admissible = excess is None or excess <= VIOL_MARGIN
        b2 = p["E"].get("B2")
        out["folds"][f"{fold}|{kind}"] = {
            "beats_B0": bool(ok and admissible), "rule_met": ok,
            "per_material": {s: {"rule_met": v[0], **v[1]} for s, v in per_mat.items()},
            "violation_rate": float(np.mean(vm)) if len(vm) else None,
            "violation_rate_data": float(np.mean(vd)) if len(vd) else None,
            "violation_rate_comparator": float(np.mean(vb)) if len(vb) else None,
            "violation_excess": excess, "admissible": admissible,
            "comparator": p.get("comparator", "B0"),
            "E_B2": float(np.nanmedian(b2)) if b2 else None, **info}
    for kind in ("L1", "L2"):
        loso_v = [v for k, v in out["folds"].items() if k.startswith("LOSO") and k.endswith(kind)]
        loso = [v["beats_B0"] for v in loso_v]
        lofo = [v["beats_B0"] for k, v in out["folds"].items() if k.startswith("LOFO") and k.endswith(kind)
                and k.split("|")[0] in NONTRIVIAL_LOFO]
        n = sum(loso)
        # falsification (review finding O1): at most one LOSO fold with r >= REL, so that the
        # 7th order statistic of r, a one-sided 96.5 % upper bound on its median, is below REL
        rel = np.array([v["median_gain"] / v["E_B0"] for v in loso_v]) if loso_v else np.array([])
        n_rel = int(np.sum(rel >= REL))
        verdict = ("supported" if n >= 7 else "falsified" if n_rel <= 1 else "not established") if len(loso) == 8 else "incomplete"
        out["H4a"][kind] = {"role": "primary" if kind == "L1" else "secondary", "LOSO_beats": n,
                            "LOSO_folds": len(loso), "verdict": verdict,
                            "rel_improvement_mean": float(rel.mean()) if len(rel) else None,
                            "rel_improvement_folds": rel.tolist(), "n_folds_rel_ge_10pct": n_rel,
                            "rel_improvement_order7": float(np.sort(rel)[6]) if len(rel) == 8 else None,
                            "LOFO_beats_nontrivial": sum(lofo), "LOFO_folds_nontrivial": len(lofo),
                            "transfers_across_families": (sum(lofo) == 2) if len(lofo) == 2 else None}
    closes = 0
    for fold, p in phys.items():
        if not fold.startswith("LOSO"):
            continue
        s = p["held"][0]
        e_b0 = np.nanmedian(p["E"]["B0"])
        e_star = np.nanmedian(p["E"]["B0star"])
        frac = (e_b0 - e_star) / max(e_b0 - F.get(s, 0.0), 1e-12)
        out["H4b"][s] = {"E_B0": float(e_b0), "E_B0star": float(e_star), "fraction_of_gap_closed": float(frac)}
        closes += frac > 0.5
    # H4b is descriptive (review finding F1): an in-sample version was seen before the freeze
    out["H4b"]["n_closing_more_than_half"] = int(closes)
    json.dump(out, open(sys.argv[3], "w", encoding="utf-8"), indent=1)
    print(json.dumps({"H4a": out["H4a"], "H4b_n_closing_more_than_half": out["H4b"]["n_closing_more_than_half"]}, indent=1))


if __name__ == "__main__":
    main()
