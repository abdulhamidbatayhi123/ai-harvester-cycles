"""Independent re-implementation of the PREREG_P4 section 7 decision rule and of section 10
criterion 4, written from the text of PREREG_P4_draft.md alone (sections 4, 6, 7, 10.4), without
reading p4/decide.py, p4/run_study.py or tests/test_decide.py. Its only purpose is to catch places
where the written rule and the code disagree, before any real result exists.

Usage
    python -E -s audit/independent_decide.py rows.jsonl checks.json out.json
    python -E -s audit/independent_decide.py --criterion4 out_rep0.json out_rep1.json ... [--model L1]
(the second form reads outputs of the first form, one per null replicate).

AMBIGUITIES IN THE TEXT AND THE READING CHOSEN HERE
A1  Which F in condition 1.  Section 7 says "that material's F"; section 6 says "A fold that holds
    out several sorbents uses the largest".  With a parent and composite judged separately the two
    differ.  Chosen: the largest F over the fold's held materials (section 6 says this is "the F
    used in the decision rule", and section 7 points to section 6).  The alternative (each
    material's own F) is computed too (`F_mode="own"`) so the comparison can tell which the code
    uses.
A2  Cluster identity.  "One RH step (from-RH, to-RH) in one session ... within one sorbent".
    Chosen: the segment id up to the first '#', i.e. "sorbent|T|session-stamp|T|from>to"; the two
    pans of a session share the stamp, the repeats share the step string.
A3  "Both are averaged within each cluster" (d and D).  Chosen: arithmetic mean over the
    cluster's segments.  The cluster E of the model and of the comparator (conditions 2 and 4) are
    likewise the mean segment E in the cluster; the text does not say mean vs median.
A4  Condition 2 / r.  "the comparator's median E over the same clusters": chosen as the median of
    the comparator's cluster-mean E.  r = median(d_c) / median(Ecomp_c); condition 2 is r >= 0.10
    evaluated as that ratio (a float boundary case at exactly 10 % could flip with
    med_d >= 0.1*medE).  If median comparator E <= 0, r is undefined: condition 2 false, r = nan
    (never counted as >= 10 %).
A5  Zero cluster differences D = 0 in the signed-rank test.  The text says "exact null over all
    2^n sign vectors, average ranks for ties" but not how zeros are treated.  Chosen: Wilcoxon's
    convention, zeros dropped before ranking, n = number of non-zero D (all-zero -> p = 1).  The
    text's "attainable minimum p is 2^-n for n clusters" is then 2^-(non-zero clusters).
A6  Ties in |D| are exact floating-point equality (no rounding tolerance is specified).
A7  Direction of the one-sided test: H1 is D > 0 (model better).  p = P(W+ >= W+_obs) under the
    sign-flip null, W+ = sum of ranks of positive D.
A8  Which per-segment E is "the comparator".  The physics row stores E["base"] (the chosen
    comparator) and the candidates E["B0"], E["B0-b_or_B0_other"], E["B1"].  Chosen: E["base"]
    for the primary rule.
A9  Admissibility.  "violates ... and neither the measured data nor the comparator does": the
    comparator's violations are taken from `viol_base`.  For the robustness runs against other
    candidates no per-candidate violation flags exist; `viol_base` is used for all of them (the
    text does not say).  "exceed 5 % of a fold's segments": excess / (all held-out segments of the
    fold, both materials pooled) > 0.05, strict.
A10 Held-out-best candidate: "the one with the lowest held-out median E in each fold": chosen as the
    median over all of the fold's held-out segments pooled (section 6's primary metric), ties
    broken in the order B0, B0-b, B1.
A11 Fewer than 8 LOSO folds present (e.g. an unfinished run): counts are over the folds present,
    thresholds unchanged (7 beats; <= 1 fold with r >= 10 %); n_folds is reported.  Missing folds
    are neither beats nor r >= 10 %.
A12 R1 vs R2 "the weaker of the two verdicts": ordered supported > not established > falsified
    (strength of the claim for the model) and the minimum taken.  The other reading (the less
    conclusive one, i.e. "not established" when one says supported and the other falsified) is
    not implemented.
A13 Supported also needs the null study (criterion 4); this script reports the LOSO-count verdict
    and, separately, the verdict given a null-study flag (default: unknown -> reported as
    "supported_pending_null" when the count would support).
A14 Criterion 4 (a): one-sided 95 % Clopper-Pearson upper bound, i.e. the p solving
    P(X <= x | n, p) = 0.05 (1 if x = n), compared <= 0.40.  (b) 5 or more of a replicate's 8
    folds beaten fails.  (c) mean of fold r over all null folds < 0.025 (strict); nan r (A4) would
    make it undefined: treated as failing.  The null fold "beat" is the full fold beat
    (all materials and admissibility), and r is the fold r (smaller per-material value).
A15 Transfer across families: the non-trivial LOFO folds are the LOFO folds holding out more than
    one parent sorbent (aluminium rods; zinc triazolates).
"""
from __future__ import annotations

import json
import math
import sys

import numpy as np

ALPHA = 0.025
PRACTICAL = 0.10
VIOL_MARGIN = 0.05
CANDIDATES = ("B0", "B0-b_or_B0_other", "B1")


# ---------------------------------------------------------------- exact signed-rank test
def avg_ranks(a):
    """Average ranks (1-based) of the values a, ties by exact equality."""
    a = np.asarray(a, float)
    order = np.argsort(a, kind="mergesort")
    ranks = np.empty(len(a))
    i = 0
    while i < len(a):
        j = i
        while j + 1 < len(a) and a[order[j + 1]] == a[order[i]]:
            j += 1
        ranks[order[i:j + 1]] = (i + j) / 2.0 + 1.0
        i = j + 1
    return ranks


def signed_rank_p(D):
    """One-sided (D > 0) exact Wilcoxon signed-rank p, zeros dropped, average ranks."""
    D = np.asarray(D, float)
    D = D[D != 0]
    n = len(D)
    if n == 0:
        return 1.0
    r2 = np.rint(2 * avg_ranks(np.abs(D))).astype(int)  # doubled ranks are integers
    w_obs = int(r2[D > 0].sum())
    S = int(r2.sum())
    counts = np.zeros(S + 1, dtype=object)  # exact Python integers
    counts[:] = 0
    counts[0] = 1
    for r in r2:
        shifted = counts[: S + 1 - r].copy()
        counts[r:] = counts[r:] + shifted
    ge = int(sum(counts[w_obs:]))
    return ge / (2 ** n)


# ---------------------------------------------------------------- helpers
def material_of(seg):
    return seg.split("|", 1)[0]


def cluster_of(seg):
    return seg.split("#", 1)[0]


def clusters(segs, vals):
    """Mean of each column of vals (dict name->array) per cluster, clusters in first-seen order."""
    keys = []
    idx = {}
    for i, s in enumerate(segs):
        c = cluster_of(s)
        if c not in idx:
            idx[c] = []
            keys.append(c)
        idx[c].append(i)
    out = {k: np.array([np.mean(np.asarray(v, float)[idx[c]]) for c in keys]) for k, v in vals.items()}
    return keys, out


def judge_material(segs, e_comp, e_model, dw, F):
    e_comp = np.asarray(e_comp, float)
    e_model = np.asarray(e_model, float)
    d = e_comp - e_model
    D = d * np.abs(np.asarray(dw, float))
    keys, c = clusters(segs, {"d": d, "D": D, "Ec": e_comp, "Em": e_model})
    med_d = float(np.median(c["d"]))
    medEc = float(np.median(c["Ec"]))
    medEm = float(np.median(c["Em"]))
    r = med_d / medEc if medEc > 0 else float("nan")
    p = signed_rank_p(c["D"])
    conds = [med_d > F, (r >= PRACTICAL) if medEc > 0 else False, p <= ALPHA, medEm < medEc]
    return {"n_clusters": len(keys), "n_seg": len(segs), "med_d": med_d, "F": F,
            "medE_comp": medEc, "medE_model": medEm, "r": r, "p": p,
            "conds": [bool(x) for x in conds], "beat": bool(all(conds))}


def judge_fold(phys, model, Fs, comp_key="base", F_mode="max"):
    psegs = list(phys["seg"])
    if sorted(model["seg"]) != sorted(psegs):
        raise ValueError(f"segment sets differ in fold {phys['fold']}")
    mpos = {s: i for i, s in enumerate(model["seg"])}
    mi = np.array([mpos[s] for s in psegs], int)
    e_model = np.asarray(model["E"], float)[mi]
    viol_m = np.asarray(model["viol"], bool)[mi]
    e_comp = np.asarray(phys["E"][comp_key], float)
    dw = np.asarray(phys["dw"], float)
    held = list(phys["held"])
    Fmax = max(Fs[h] for h in held)
    mats = {}
    for h in held:
        sel = np.array([material_of(s) == h for s in psegs])
        F = Fmax if F_mode == "max" else Fs[h]
        mats[h] = judge_material([s for s, k in zip(psegs, sel) if k], e_comp[sel], e_model[sel],
                                 dw[sel], F)
    excess = viol_m & ~np.asarray(phys["viol_data"], bool) & ~np.asarray(phys["viol_base"], bool)
    frac = float(excess.sum()) / len(psegs)
    admissible = not (frac > VIOL_MARGIN)
    rs = [m["r"] for m in mats.values()]
    r = float("nan") if any(math.isnan(x) for x in rs) else min(rs)
    return {"held": held, "materials": mats, "excess_frac": frac, "admissible": admissible,
            "r": r, "beat": bool(all(m["beat"] for m in mats.values()) and admissible)}


def verdict_from_counts(beats, n_r10, null_passed=None):
    if beats >= 7:
        if null_passed is None:
            return "supported_pending_null"
        return "supported" if null_passed else "not_established"
    return "falsified" if n_r10 <= 1 else "not_established"


def weaker(v1, v2):
    order = {"falsified": 0, "not_established": 1, "supported_pending_null": 2, "supported": 2}
    return v1 if order[v1] <= order[v2] else v2


def decide(rows, Fs, F_mode="max", null_passed=None):
    phys = {r["fold"]: r for r in rows if r["key"].endswith("|physics")}
    models = {}
    for r in rows:
        if r["key"].endswith("|ensemble"):
            models.setdefault(r["kind"], {})[r["fold"]] = r
    out = {}
    for kind, fr in models.items():
        res = {"folds": {}, "against": {}}
        for fold, m in fr.items():
            if fold not in phys:
                continue
            res["folds"][fold] = judge_fold(phys[fold], m, Fs, "base", F_mode)
        # robustness: each candidate and the held-out-best one
        for cand in CANDIDATES + ("heldout_best",):
            per = {}
            for fold, m in fr.items():
                if fold not in phys:
                    continue
                p = phys[fold]
                if cand == "heldout_best":
                    meds = [float(np.median(np.asarray(p["E"][c], float))) for c in CANDIDATES]
                    ck = CANDIDATES[int(np.argmin(meds))]
                else:
                    ck = cand
                j = judge_fold(p, m, Fs, ck, F_mode)
                per[fold] = {"cand": ck, "beat": j["beat"], "r": j["r"]}
            loso = [f for f in per if f.startswith("LOSO")]
            res["against"][cand] = {"folds": per, "loso_beats": sum(per[f]["beat"] for f in loso)}
        loso = sorted(f for f in res["folds"] if f.startswith("LOSO"))
        beats = sum(res["folds"][f]["beat"] for f in loso)
        n_r10 = sum(1 for f in loso if res["folds"][f]["r"] >= PRACTICAL)
        v = verdict_from_counts(beats, n_r10, null_passed)
        lofo = [f for f in res["folds"] if f.startswith("LOFO")
                and len([h for h in res["folds"][f]["held"] if "composite" not in h]) > 1]
        lofo_beats = sum(res["folds"][f]["beat"] for f in lofo)
        wording = None
        if v.startswith("supported"):
            wording = ("supported; beats the held-out-best isotherm-driven candidate"
                       if res["against"]["heldout_best"]["loso_beats"] >= 7 else
                       "supported against the comparator chosen on the training sorbents only")
        res["H4a"] = {"n_loso_folds": len(loso), "loso_beats": beats, "n_r_ge_10": n_r10,
                      "verdict": v, "wording": wording, "lofo_nontrivial": sorted(lofo),
                      "lofo_beats": lofo_beats,
                      "transfers": (lofo_beats == 2) if v.startswith("supported") else None}
        out[kind] = res
    return out


# ---------------------------------------------------------------- criterion 4
def cp_upper(x, n, conf=0.95):
    if x >= n:
        return 1.0
    def cdf(p):
        return sum(math.comb(n, k) * p ** k * (1 - p) ** (n - k) for k in range(x + 1))
    lo, hi = 0.0, 1.0
    for _ in range(200):
        mid = (lo + hi) / 2
        if cdf(mid) > 1 - conf:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def criterion4(replicates):
    """replicates: list of lists of (beat: bool, r: float), one inner list per null replicate."""
    allf = [f for rep in replicates for f in rep]
    n = len(allf)
    x = sum(1 for b, _ in allf if b)
    ub = cp_upper(x, n)
    a = ub <= 0.40
    per_rep = [sum(1 for b, _ in rep if b) for rep in replicates]
    b = all(k < 5 for k in per_rep)
    rs = [r for _, r in allf]
    mean_r = float("nan") if any(math.isnan(r) for r in rs) else float(np.mean(rs))
    c = (not math.isnan(mean_r)) and mean_r < 0.025
    return {"n_fold_fits": n, "beats": x, "cp_upper": ub, "a": a, "beats_per_rep": per_rep, "b": b,
            "mean_r": mean_r, "c": c, "pass": bool(a and b and c)}


def main(argv):
    if argv and argv[0] == "--criterion4":
        model = "L1"
        files = argv[1:]
        if "--model" in files:
            i = files.index("--model")
            model = files[i + 1]
            files = files[:i] + files[i + 2:]
        reps = []
        for f in files:
            o = json.load(open(f))[model]
            reps.append([(v["beat"], v["r"]) for k, v in o["folds"].items() if k.startswith("LOSO")])
        print(json.dumps(criterion4(reps), indent=1))
        return
    rows_path, checks_path, out_path = argv[:3]
    rows = [json.loads(l) for l in open(rows_path) if l.strip()]
    Fs = json.load(open(checks_path))["F_within_segment_weighted"]
    F_mode = "own" if "--F-own" in argv else "max"
    out = decide(rows, Fs, F_mode)
    json.dump(out, open(out_path, "w"), indent=1, default=float)


if __name__ == "__main__":
    main(sys.argv[1:])
