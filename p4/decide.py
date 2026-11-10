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


def cluster_level(seg_ids, e_b0, e_m, dw=None, with_d=False):
    """Cluster means of E_base, E_model, of d = E_base - E_model and of D = d * |dw| (NaN if dw is
    None), with the material of each cluster. d is the mean of the segment differences, so the
    cluster gain is not a difference of two rounded means (independent-scorer check, 2026-11-10).

    A segment whose comparator E is not finite is dropped (no reference to compare with). A
    segment whose model E is not finite (a diverged rollout) counts as an infinite loss for the
    model, never as a missing value: dropping it would favour a model that diverges."""
    by = defaultdict(list)
    dw = [np.nan] * len(seg_ids) if dw is None else dw
    for sid, a, b, w in zip(seg_ids, e_b0, e_m, dw):
        if not np.isfinite(a):
            continue
        b = b if np.isfinite(b) else np.inf
        by[sid.split("#")[0]].append((a, b, a - b, (a - b) * w))
    keys = list(by)
    b0 = np.array([np.mean([x[0] for x in by[k]]) for k in keys])
    m = np.array([np.mean([x[1] for x in by[k]]) for k in keys])
    d = np.array([np.mean([x[2] for x in by[k]]) for k in keys])
    D = np.array([np.mean([x[3] for x in by[k]]) for k in keys])
    mat = np.array([material_of(k) for k in keys])
    return (b0, m, D, mat, d) if with_d else (b0, m, D, mat)


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


CANDIDATE_KEYS = ("B0", "B0-b_or_B0_other", "B1")   # as stored by run_study (review T-P4-4 F-7)


def rule(e_b0, e_m, F, D=None, d=None):
    """Section 7 for one material. D: cluster values of the unnormalised difference for the
    test; without it (old rows) the test falls back to d. d: cluster mean differences (from
    cluster_level); without it, e_b0 - e_m."""
    d = e_b0 - e_m if d is None else d
    gain = float(np.median(d))
    p = signflip_p(d if D is None or np.isnan(D).any() else D)
    # r is computed once and used both here (condition 2) and for "falsified", so the two cannot
    # disagree at r = 10 % through rounding (independent-scorer check, 2026-11-10)
    e_ref = float(np.median(e_b0))
    r = gain / e_ref if e_ref > 0 else (np.inf if gain > 0 else -np.inf)
    # condition 4 (added 2026-11-09 after harness round 6): the model's own median cluster E must be
    # below the comparator's. A paired median can favour a model that is far better on the hard
    # steps but several times worse on the easy ones (world C2, ROS-039: median d +0.012 while the
    # model's median E was 0.034 against B0's 0.013); such a model has not beaten the comparator.
    ok = bool(gain > F and r >= REL and p <= ALPHA
              and float(np.median(e_m)) < e_ref)
    return ok, {"median_gain": gain, "r": float(r), "p_signflip": p, "E_B0": e_ref,
                "E_model": float(np.median(e_m)), "F": F, "n_clusters": int(len(d)),
                "min_attainable_p": float(2.0 ** -len(d))}


def main():
    rows = [json.loads(l) for l in open(sys.argv[1], encoding="utf-8")]
    F = sorbent_F(json.load(open(sys.argv[2], encoding="utf-8")))
    phys = {r["fold"]: r for r in rows if r["key"].endswith("|physics")}
    ens = {(r["fold"], r["kind"]): r for r in rows if r["key"].endswith("|ensemble")}
    # H4a' (PREREG section 2, added 2026-11-10 after L1 failed the harness): B2 is judged by the same
    # rule as a learned model, against the same comparator, from the physics row of each fold
    for fold, p in phys.items():
        if p["E"].get("B2") is not None:
            ens[(fold, "B2")] = {"seg": p["seg"], "E": p["E"]["B2"], "viol": p.get("viol_B2")}
    out = {"folds": {}, "H4a": {}, "H4b": {}}
    for (fold, kind), r in sorted(ens.items()):
        p = phys[fold]
        assert p["seg"] == r["seg"], f"segment order differs in {fold}"
        held = p["held"]
        b0, m, D, mat, dd = cluster_level(r["seg"], p["E"].get("base", p["E"]["B0"]), r["E"], p.get("dw"), with_d=True)
        per_mat = {}
        for s in held:
            sel = mat == s
            if sel.any():
                per_mat[s] = rule(b0[sel], m[sel], F.get(s, 0.0), D[sel], dd[sel])
            else:
                # a held material without scored segments cannot pass: "both must pass" (section 7)
                per_mat[s] = (False, {"median_gain": float("nan"), "r": float("nan"), "p_signflip": 1.0,
                                      "E_B0": float("nan"), "E_model": float("nan"), "F": F.get(s, 0.0),
                                      "n_clusters": 0, "min_attainable_p": 1.0})
        ok = bool(per_mat) and all(v[0] for v in per_mat.values())
        _, info = rule(b0, m, max(F.get(s, 0.0) for s in held), D, dd)     # pooled, reported
        # review T-P4-4 F-6: in a parent + composite fold the relative improvement r is the smaller of
        # the two per-material values (consistent with "both must pass"); the pooled r is reported
        r_fold = float(np.min([v[1]["r"] for v in per_mat.values()])) if per_mat else float("nan")
        r_fold = -np.inf if np.isnan(r_fold) else r_fold          # a material without segments
        # review T-P4-4 F-7: robustness against every comparator candidate, and against the candidate
        # with the lowest held-out median E (descriptive; it decides only the wording of the claim)
        cand = {}
        for c in CANDIDATE_KEYS:
            if p["E"].get(c) is None:
                continue
            cb, cm, cD, cmat, cd = cluster_level(r["seg"], p["E"][c], r["E"], p.get("dw"), with_d=True)
            res = [bool((cmat == s).any()) and rule(cb[cmat == s], cm[cmat == s], F.get(s, 0.0), cD[cmat == s],
                                                    cd[cmat == s])[0] for s in held]
            cand[c] = {"rule_met": bool(res) and all(res), "E_heldout": float(np.nanmedian(p["E"][c]))}
        best = min(cand, key=lambda c: cand[c]["E_heldout"]) if cand else None
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
            "E_B2": float(np.nanmedian(b2)) if b2 else None,
            "r_fold": r_fold, "r_pooled": info["r"],
            "candidates": cand, "heldout_best_candidate": best,
            "beats_heldout_best": bool(best is not None and cand[best]["rule_met"] and admissible), **info}
    for kind in ("L1", "L2", "B2"):
        loso_v = [v for k, v in out["folds"].items() if k.startswith("LOSO") and k.endswith(kind)]
        loso = [v["beats_B0"] for v in loso_v]
        lofo = [v["beats_B0"] for k, v in out["folds"].items() if k.startswith("LOFO") and k.endswith(kind)
                and k.split("|")[0] in NONTRIVIAL_LOFO]
        n = sum(loso)
        # falsification (review finding O1): at most one LOSO fold with r >= REL, so that the
        # 7th order statistic of r, a one-sided 96.5 % upper bound on its median, is below REL
        rel = np.array([v["r_fold"] for v in loso_v]) if loso_v else np.array([])
        n_best = sum(v["beats_heldout_best"] for v in loso_v)
        n_rel = int(np.sum(rel >= REL))
        verdict = ("supported" if n >= 7 else "falsified" if n_rel <= 1 else "not established") if len(loso) == 8 else "incomplete"
        if not loso_v:
            continue
        role = {"L1": "learned (not tested: failed the synthetic harness, section 10)",
                "L2": "learned (dropped after harness round 4)", "B2": "H4a' (primary from 2026-11-10)"}[kind]
        out["H4a"][kind] = {"role": role, "LOSO_beats": n,
                            "LOSO_folds": len(loso), "verdict": verdict,
                            "rel_improvement_mean": float(rel.mean()) if len(rel) else None,
                            "rel_improvement_folds": rel.tolist(), "n_folds_rel_ge_10pct": n_rel,
                            "rel_improvement_order7": float(np.sort(rel)[6]) if len(rel) == 8 else None,
                            "LOSO_beats_vs_heldout_best_candidate": n_best,
                            "claim_wording": (None if verdict != "supported" else "beats the isotherm-driven models"
                                              if n_best >= 7 else "supported against the comparator chosen on the training sorbents only"),
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
