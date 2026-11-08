"""Apply the pre-registered decision rules (PREREG_P4 section 7) to the runner's rows.

Per fold and learned model, the paired difference d = E_base - E_model is averaged within each
cluster, and the rule is applied to the cluster-level d: median(d) > F of the held-out sorbent, median(d) >= 10 % of median E_base,
and a one-sided exact Wilcoxon signed-rank test of d over clusters gives p <= 0.025. A cluster is
one RH step in one measuring session (both pans and all repeats of that step averaged). E_base is the comparator
chosen on the validation sorbent among B0, B0-b and B1 (rows written before that change: B0).

H4a, L1 primary and L2 secondary: supported if the model beats the comparator on >= 7 of 8 LOSO
folds; falsified only if the 95 % bootstrap interval over the LOSO folds of the mean relative
improvement lies wholly below 10 %; otherwise not established. Transfer across families requires
both non-trivial LOFO folds (Al-rod, Zn-triazolate-F).
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
N_BOOT = 5000


def sorbent_F(checks2):
    """One F per sorbent: the segment-weighted mean of its within-file floors at 27 and 60 C
    (PREREG section 6), as computed before the freeze by audit/prefreeze_checks2.py."""
    return {s: float(v) for s, v in checks2["F_within_segment_weighted"].items()}


def cluster_level(seg_ids, e_b0, e_m):
    by = defaultdict(list)
    for sid, a, b in zip(seg_ids, e_b0, e_m):
        if np.isfinite(a) and np.isfinite(b):
            by[sid.split("#")[0]].append((a, b))
    b0 = np.array([np.mean([x[0] for x in v]) for v in by.values()])
    m = np.array([np.mean([x[1] for x in v]) for v in by.values()])
    return b0, m


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


def rule(e_b0, e_m, F, seed=0):
    d = e_b0 - e_m
    gain = float(np.median(d))
    p = signflip_p(d)
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
        Fh = max(F.get(s, 0.0) for s in held)        # the larger floor when a fold holds several
        b0, m = cluster_level(r["seg"], p["E"].get("base", p["E"]["B0"]), r["E"])
        ok, info = rule(b0, m, Fh)
        # physical admissibility (section 7): violation rate at most the data's own + 5 points
        v_m = float(np.mean(r["viol"])) if r.get("viol") else None
        v_d = float(np.mean(p["viol_data"])) if p.get("viol_data") else None
        admissible = v_m is None or v_d is None or v_m <= v_d + VIOL_MARGIN
        b2 = p["E"].get("B2")
        out["folds"][f"{fold}|{kind}"] = {"beats_B0": bool(ok and admissible), "rule_met": ok,
                                          "violation_rate": v_m, "violation_rate_data": v_d,
                                          "admissible": admissible, "comparator": p.get("comparator", "B0"),
                                          "E_B2": float(np.nanmedian(b2)) if b2 else None, **info}
    for kind in ("L1", "L2"):
        loso_v = [v for k, v in out["folds"].items() if k.startswith("LOSO") and k.endswith(kind)]
        loso = [v["beats_B0"] for v in loso_v]
        lofo = [v["beats_B0"] for k, v in out["folds"].items() if k.startswith("LOFO") and k.endswith(kind)
                and k.split("|")[0] in NONTRIVIAL_LOFO]
        n = sum(loso)
        # falsification needs an interval (review finding M3): the 95 % bootstrap interval, over
        # the 8 LOSO folds, of the mean relative improvement must lie wholly below REL
        rel = np.array([v["median_gain"] / v["E_B0"] for v in loso_v]) if loso_v else np.array([])
        rng = np.random.default_rng(1)
        hi = float(np.quantile([rng.choice(rel, len(rel)).mean() for _ in range(N_BOOT)], 0.975)) if len(rel) else float("nan")
        verdict = ("supported" if n >= 7 else "falsified" if hi < REL else "not established") if len(loso) == 8 else "incomplete"
        out["H4a"][kind] = {"role": "primary" if kind == "L1" else "secondary", "LOSO_beats": n,
                            "LOSO_folds": len(loso), "verdict": verdict,
                            "rel_improvement_mean": float(rel.mean()) if len(rel) else None,
                            "rel_improvement_upper95": hi,
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
