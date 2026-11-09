"""Compare audit/independent_decide.py (written from the PREREG_P4 text alone) with p4/decide.py on
the archived null replicate and on randomly generated rows files that stress the boundaries of the
section 7 rule. Light: numpy only, a few MB; p4.decide is called in-process through its main().

usage (repo root): .venv/Scripts/python.exe -E -s audit/compare_decide.py [n_random=240] [seed=20261110]
writes results/independent_decide_check.json
"""
from __future__ import annotations

import contextlib
import io
import json
import math
import os
import sys
import tempfile
import warnings

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "audit"))
import independent_decide as IND  # noqa: E402
import p4.decide as PD  # noqa: E402

warnings.filterwarnings("ignore", category=RuntimeWarning)
CHECKS = os.path.join(ROOT, "results", "prefreeze", "checks2.json")
FS = json.load(open(CHECKS))["F_within_segment_weighted"]

LOSO = {"LOSO:ROS-037": ["ROS-037", "ROS-037_composite"], "LOSO:ROS-039": ["ROS-039", "ROS-039_composite"],
        "LOSO:ROS-040": ["ROS-040"], "LOSO:MOF-303": ["MOF-303"], "LOSO:MIL-160": ["MIL-160"],
        "LOSO:CAU-10": ["CAU-10"], "LOSO:Al-fumarate": ["Al-fumarate"], "LOSO:Syloid": ["Syloid"]}
LOFO = {"LOFO:Al-rod": ["MOF-303", "MIL-160", "CAU-10", "Al-fumarate"],
        "LOFO:Zn-triazolate-F": ["ROS-039", "ROS-040", "ROS-039_composite"],
        "LOFO:ROS-037": ["ROS-037", "ROS-037_composite"], "LOFO:Syloid": ["Syloid"]}
STEPS = ["0>30", "30>0", "0>11", "11>30", "30>60", "60>11", "11>60", "60>0", "0>60", "30>11"]


def run_code(rows_path):
    out = rows_path + ".code.json"
    argv = sys.argv
    sys.argv = ["p4.decide", rows_path, CHECKS, out]
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            PD.main()
    finally:
        sys.argv = argv
    return json.load(open(out))


# ---------------------------------------------------------------- generator
def gen_material(rng, mat, scen):
    """Segments of one held-out material; returns lists seg, dw, Ebase, Emodel, Ecands, vd, vb, vm."""
    if scen["empty"] and mat.endswith("composite"):
        return [], [], [], [], {c: [] for c in IND.CANDIDATES}
    nc = int(rng.choice([1, 2, 3, 5, 6, 7, 9, 14, 26])) if scen["tiny"] else int(rng.integers(6, 40))
    F = FS[mat]
    segs, dws, eb = [], [], []
    for c in range(nc):
        stamp = f"2021-0{1 + c % 2}-1{c % 7} 10-00-0{c % 3}"
        step = STEPS[c % len(STEPS)] if c < len(STEPS) else f"{c}>{c + 1}"
        T = "27C" if c % 2 == 0 else "60C"
        nseg = int(rng.integers(1, 5))
        base_e = float(np.exp(rng.normal(np.log(0.05), 0.6)))
        for k in range(nseg):
            segs.append(f"{mat}|{T}|{stamp}|{T}|{step}#{mat}/{T}/file{k % 2}-{stamp}.xls#{len(segs) + 1}")
            dws.append(float(rng.choice([5.0, 10.0, 20.0])) if scen["quant"] else float(rng.uniform(4, 40)))
            e = base_e if scen["exact10"] else base_e * float(np.exp(rng.normal(0, 0.2)))
            eb.append(round(e, 3) if scen["quant"] else e)
    eb = np.array(eb)
    g = scen["gain"]
    n = len(eb)
    if scen["exact10"]:
        em = eb * (1 - 0.1)
    elif scen["Fedge"]:
        em = eb - (F + float(rng.choice([-1e-12, 0.0, 1e-12])))
    elif scen["eqmed"]:
        em = eb.copy()
        rng.shuffle(em)  # same multiset: per-segment medians tie; cluster medians often tie
        em = em * (1 - g)
    else:
        em = eb * (1 - g + rng.normal(0, scen["noise"], n))
        if scen["quant"]:
            em = np.round(em, 3)
    if scen["zeros"]:
        z = rng.random(n) < 0.4
        em[z] = eb[z]
    em = np.maximum(em, 1e-4)
    cands = {}
    for c in IND.CANDIDATES:
        cands[c] = eb * float(np.exp(rng.normal(0, 0.15))) * np.exp(rng.normal(0, 0.05, n))
    return segs, dws, eb.tolist(), em.tolist(), {c: v.tolist() for c, v in cands.items()}


def gen_rows(rng, case_i):
    scen = {"tiny": rng.random() < 0.35, "quant": rng.random() < 0.35, "exact10": rng.random() < 0.12,
            "Fedge": rng.random() < 0.12, "eqmed": rng.random() < 0.12, "zeros": rng.random() < 0.2,
            "gain": float(rng.choice([0.0, 0.05, 0.1, 0.15, 0.3, 0.6])), "noise": float(rng.choice([0.0, 0.05, 0.3])),
            "viol": rng.random() < 0.4, "lofo": rng.random() < 0.3, "empty": False, "nfold8": rng.random() < 0.9}
    folds = dict(LOSO)
    if not scen["nfold8"]:
        folds.pop(list(LOSO)[int(rng.integers(8))])
    if scen["lofo"]:
        folds.update(LOFO)
    rows = []
    for fold, held in folds.items():
        S, DW, EB, EM, C = [], [], [], [], {c: [] for c in IND.CANDIDATES}
        for m in held:
            s, dw, eb, em, cand = gen_material(rng, m, scen)
            S += s; DW += dw; EB += eb; EM += em
            for c in IND.CANDIDATES:
                C[c] += cand[c]
        n = len(S)
        comp = str(rng.choice(["B0", "B0-b", "B1"]))
        # the stored "base" is the chosen comparator; make one candidate equal to it
        key = {"B0": "B0", "B0-b": "B0-b_or_B0_other", "B1": "B1"}[comp]
        C[key] = list(EB)
        vd = (rng.random(n) < 0.05).tolist()
        vb = (rng.random(n) < 0.05).tolist()
        vm = np.zeros(n, bool)
        if scen["viol"] and n:
            free = [i for i in range(n) if not vd[i] and not vb[i]]
            k = int(round(0.05 * n)) + int(rng.choice([-1, 0, 0, 1]))
            k = max(0, min(k, len(free)))
            vm[rng.choice(free, k, replace=False)] = True
            extra = [i for i in range(n) if vd[i] or vb[i]]
            if extra:
                vm[extra[: int(rng.integers(0, len(extra) + 1))]] = True
        rows.append({"key": f"{fold}|physics", "fold": fold, "held": held, "seg": S, "dw": DW,
                     "viol_data": vd, "viol_base": vb, "comparator": comp,
                     "E": {**C, "base": EB, "B2": EB, "B0star": EB}})
        rows.append({"key": f"{fold}|L1|ensemble", "fold": fold, "kind": "L1", "seg": S, "E": EM,
                     "viol": vm.tolist()})
    return rows, scen


# ---------------------------------------------------------------- comparison
def close(a, b, tol=1e-12):
    if a is None or b is None:
        return a is b
    if isinstance(a, float) and isinstance(b, float) and math.isnan(a) and math.isnan(b):
        return True
    return abs(a - b) <= tol * max(1.0, abs(a), abs(b))


def compare(rows, code, F_mode):
    ind = IND.decide(rows, FS, F_mode)["L1"]
    diffs = []
    for fold, mine in ind["folds"].items():
        c = code["folds"].get(f"{fold}|L1")
        if c is None:
            diffs.append({"fold": fold, "what": "fold missing in code"}); continue
        for m, x in mine["materials"].items():
            cm = c["per_material"].get(m)
            if cm is None:
                diffs.append({"fold": fold, "material": m, "what": "material missing in code (no segments)",
                              "mine_beat": x["beat"]}); continue
            if x["beat"] != cm["rule_met"]:
                diffs.append({"fold": fold, "material": m, "what": "material beat", "mine": x["beat"],
                              "code": cm["rule_met"], "mine_conds": x["conds"], "med_d": x["med_d"],
                              "medE_comp": x["medE_comp"], "F_mine": x["F"], "F_code": cm["F"],
                              "r": x["r"], "p": x["p"]})
            if not close(x["p"], cm["p_signflip"]):
                diffs.append({"fold": fold, "material": m, "what": "p", "mine": x["p"], "code": cm["p_signflip"]})
            r_code = cm["median_gain"] / cm["E_B0"] if cm["E_B0"] else float("nan")
            if not close(x["r"], r_code):
                diffs.append({"fold": fold, "material": m, "what": "material r", "mine": x["r"], "code": r_code})
        if mine["beat"] != c["beats_B0"]:
            diffs.append({"fold": fold, "what": "fold beat", "mine": mine["beat"], "code": c["beats_B0"],
                          "excess_mine": mine["excess_frac"], "excess_code": c["violation_excess"]})
        if not close(mine["r"], c["r_fold"]):
            diffs.append({"fold": fold, "what": "fold r", "mine": mine["r"], "code": c["r_fold"]})
        for cand in IND.CANDIDATES:
            a = ind["against"][cand]["folds"][fold]
            if cand in c["candidates"]:
                # code's candidate rule_met excludes admissibility; mine includes it
                mine_rule = a["beat"]
                code_rule = c["candidates"][cand]["rule_met"] and c["admissible"]
                if mine_rule != code_rule:
                    diffs.append({"fold": fold, "what": f"beat vs candidate {cand}", "mine": mine_rule, "code": code_rule})
        hb = ind["against"]["heldout_best"]["folds"][fold]
        if hb["cand"] != c["heldout_best_candidate"]:
            diffs.append({"fold": fold, "what": "held-out-best candidate", "mine": hb["cand"], "code": c["heldout_best_candidate"]})
        if hb["beat"] != c["beats_heldout_best"]:
            diffs.append({"fold": fold, "what": "beat vs held-out best", "mine": hb["beat"], "code": c["beats_heldout_best"]})
    h, ch = ind["H4a"], code["H4a"]["L1"]
    mv = {"supported_pending_null": "supported", "not_established": "not established", "falsified": "falsified"}[h["verdict"]]
    if h["n_loso_folds"] != 8:
        mv = "incomplete"  # A11: the text assumes 8 folds; the code's 'incomplete' is accepted
    for what, a, b in (("LOSO beats", h["loso_beats"], ch["LOSO_beats"]), ("n r>=10%", h["n_r_ge_10"], ch["n_folds_rel_ge_10pct"]),
                       ("verdict", mv, ch["verdict"]),
                       ("heldout-best LOSO beats", ind["against"]["heldout_best"]["loso_beats"], ch["LOSO_beats_vs_heldout_best_candidate"]),
                       ("LOFO non-trivial beats", h["lofo_beats"], ch["LOFO_beats_nontrivial"])):
        if a != b:
            diffs.append({"what": f"H4a {what}", "mine": a, "code": b})
    wm = None if h["wording"] is None or mv != "supported" else ("restricted" if "only" in h["wording"] else "full")
    wc = None if ch["claim_wording"] is None else ("restricted" if "only" in ch["claim_wording"] else "full")
    if wm != wc:
        diffs.append({"what": "H4a wording", "mine": wm, "code": wc})
    return diffs, ind


def minimal_material(rows, fold, mat):
    p = next(r for r in rows if r["key"] == f"{fold}|physics")
    m = next(r for r in rows if r["key"] == f"{fold}|L1|ensemble")
    idx = [i for i, s in enumerate(p["seg"]) if s.split("|")[0] == mat]
    return {"n_seg": len(idx), "seg": [p["seg"][i].split("#")[0] for i in idx],
            "E_comp": [p["E"]["base"][i] for i in idx], "E_model": [m["E"][i] for i in idx],
            "dw": [p["dw"][i] for i in idx]}


def special_cases():
    """Hand-made minimal cases for boundaries the random sweep may hit only by chance."""
    out = []
    def fold_rows(fold, held, per_mat, vd=None, vb=None, vm=None):
        S, DW, EB, EM = [], [], [], []
        for mat, (eb, em, dw) in zip(held, per_mat):
            for i, (a, b, w) in enumerate(zip(eb, em, dw)):
                S.append(f"{mat}|27C|2021-05-25 14-51-36|27C|{i}>{i + 1}#f.xls#{len(S) + 1}")
                EB.append(a); EM.append(b); DW.append(w)
        n = len(S)
        vd = vd or [False] * n; vb = vb or [False] * n; vm = vm or [False] * n
        return [{"key": f"{fold}|physics", "fold": fold, "held": held, "seg": S, "dw": DW, "viol_data": vd,
                 "viol_base": vb, "comparator": "B0",
                 "E": {"B0": EB, "B0-b_or_B0_other": [x * 2 for x in EB], "B1": [x * 3 for x in EB],
                       "base": EB, "B2": EB, "B0star": EB}},
                {"key": f"{fold}|L1|ensemble", "fold": fold, "kind": "L1", "seg": S, "E": EM, "viol": vm}]
    strong = lambda n: ([0.1] * n, [0.05] * n, [10.0] * n)  # noqa: E731
    # S1: parent strongly better; composite gain between the parent's F and the composite's F
    #     (ROS-037 F = 0.00397, composite F = 0.00615): own-F vs largest-F reading
    g = 0.005
    out.append(("S1 F reading (own vs largest)", fold_rows("LOSO:ROS-037", ["ROS-037", "ROS-037_composite"],
                [strong(8), ([0.04] * 8, [0.04 - g] * 8, [10.0] * 8)])))
    # S1b the same with the parent's gain in between the two Fs and the composite's above both
    out.append(("S1b F reading, parent in between", fold_rows("LOSO:ROS-037", ["ROS-037", "ROS-037_composite"],
                [([0.04] * 8, [0.035] * 8, [10.0] * 8), strong(8)])))
    # S2: exactly 10 %: E 0.3, model 0.27 (0.3 - 0.27 = 0.030000000000000027 > 0.1*0.3 = 0.030000000000000002)
    #     and E 0.7, model 0.63 (0.7-0.63 = 0.06999999999999995 < 0.07)
    for e in (0.3, 0.7, 0.1, 0.5):
        out.append((f"S2 exact 10 % at E={e}", fold_rows("LOSO:MOF-303", ["MOF-303"], [([e] * 8, [e * 0.9] * 8, [10.0] * 8)])))
    # S3: composite present in 'held' but without segments
    out.append(("S3 held composite without segments", fold_rows("LOSO:ROS-037", ["ROS-037", "ROS-037_composite"],
                [strong(8), ([], [], [])])))
    # S4: model E NaN on one segment (a diverged rollout)
    eb, em, dw = strong(8)
    em = em[:]; em[0] = float("nan")
    out.append(("S4 NaN model E on one segment", fold_rows("LOSO:MOF-303", ["MOF-303"], [(eb, em, dw)])))
    # S5: excess violations exactly 5 % (1 of 20) and just above (2 of 20 -> 10 %; 2 of 40 = 5 %)
    for n, k in ((20, 1), (40, 2), (40, 3)):
        eb, em, dw = strong(n)
        out.append((f"S5 excess violations {k}/{n}", fold_rows("LOSO:MOF-303", ["MOF-303"], [(eb, em, dw)],
                    vm=[True] * k + [False] * (n - k))))
    # S6: 6 clusters, all equal gains -> p = 1/64 = 0.0156 (beat); 5 clusters -> p = 1/32 (no beat)
    for n in (5, 6):
        out.append((f"S6 {n} equal gains", fold_rows("LOSO:MOF-303", ["MOF-303"], [strong(n)])))
    # S7: median cluster E equal for model and comparator, paired gain positive
    eb = [0.02, 0.03, 0.05, 0.08, 0.12, 0.2, 0.3]
    em = [0.02, 0.03, 0.05, 0.08, 0.06, 0.1, 0.15]
    out.append(("S7 equal median E", fold_rows("LOSO:MOF-303", ["MOF-303"], [(eb, em, [10.0] * 7)])))
    return out


def criterion4_check(n=500, seed=3):
    """Criterion 4 (section 10): independent version vs audit/null_summary.py."""
    import null_summary as NS
    rng = np.random.default_rng(seed)
    cp_bad = [(k, m) for m in (8, 16, 24, 32) for k in range(m + 1)
              if abs(IND.cp_upper(k, m) - NS.cp_upper(k, m)) > 1e-9
              or (IND.cp_upper(k, m) <= 0.4) != (NS.cp_upper(k, m) <= 0.4)]
    bad = []
    for t in range(n):
        q = float(rng.choice([0.1, 0.3, 0.5]))
        reps = [[(bool(rng.random() < q), float(rng.normal(0.02, 0.05))) for _ in range(8)]
                for _ in range(int(rng.choice([2, 3, 4])))]
        a = IND.criterion4(reps)
        per = [{"beats": b, "r": r} for rep in reps for b, r in rep]
        s = NS.summarise(per, {i: sum(b for b, _ in rep) for i, rep in enumerate(reps)})
        if (a["a"], a["b"], a["c"], a["pass"]) != (s["a_pass"], s["b_pass"], s["c_pass"], s["criterion_4_pass"]):
            bad.append({"case": t, "reps": reps})
    return {"cases": n, "cp_upper_mismatches": cp_bad, "disagreements": bad}


def main():
    if "--c4-only" in sys.argv:
        out = os.path.join(ROOT, "results", "independent_decide_check.json")
        rep = json.load(open(out))
        rep["criterion4"] = criterion4_check()
        json.dump(rep, open(out, "w", encoding="utf-8"), indent=1, default=float)
        print(rep["criterion4"]["cases"], len(rep["criterion4"]["disagreements"]))
        return
    n_random = int(sys.argv[1]) if len(sys.argv) > 1 else 240
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else 20261110
    tmp = tempfile.mkdtemp(prefix="cmp_decide_")
    report = {"n_random": n_random, "seed": seed, "modes": {}, "real": {}, "special": {}}

    def one(rows, label):
        path = os.path.join(tmp, f"{label}.jsonl")
        with open(path, "w", encoding="utf-8") as f:
            for r in rows:
                f.write(json.dumps(r) + "\n")
        try:
            code = run_code(path)
        except Exception as e:  # noqa: BLE001
            return {"code_error": f"{type(e).__name__}: {e}"}
        res = {}
        for mode in ("max", "own"):
            try:
                d, ind = compare(rows, code, mode)
                if mode == "own":
                    res["_ind_own"] = ind
            except Exception as e:  # noqa: BLE001
                d = [{"what": "independent error", "err": f"{type(e).__name__}: {e}"}]
            res[mode] = d
        return res

    # (i) the archived null replicate
    rows = [json.loads(l) for l in open(os.path.join(ROOT, "results", "null_rep0_preD", "rows.jsonl"))]
    report["real"]["null_rep0_preD"] = one(rows, "real")
    report["real"]["null_rep0_preD"].pop("_ind_own", None)
    # (iii) special cases
    for label, rows in special_cases():
        report["special"][label] = one(rows, "special")
        report["special"][label].pop("_ind_own", None)
    # (ii) random cases
    rng = np.random.default_rng(seed)
    stats = {m: {"cases": 0, "cases_agree": 0, "fold_comparisons": 0, "material_comparisons": 0,
                 "by_what": {}, "examples": {}} for m in ("max", "own")}
    beats_seen = {"material_beats": 0, "fold_beats": 0, "supported": 0, "falsified": 0, "not_established": 0}
    for i in range(n_random):
        rows, scen = gen_rows(rng, i)
        res = one(rows, f"rand{i}")
        ind = res.pop("_ind_own", None) or IND.decide(rows, FS, "own")["L1"]
        beats_seen["material_beats"] += sum(x["beat"] for f in ind["folds"].values() for x in f["materials"].values())
        beats_seen["fold_beats"] += sum(f["beat"] for f in ind["folds"].values())
        v = ind["H4a"]["verdict"].replace("supported_pending_null", "supported")
        beats_seen[v] = beats_seen.get(v, 0) + 1
        for mode in ("max", "own"):
            st = stats[mode]
            st["cases"] += 1
            st["fold_comparisons"] += len(ind["folds"])
            st["material_comparisons"] += sum(len(f["materials"]) for f in ind["folds"].values())
            d = res.get(mode, [{"what": "code error", "err": res.get("code_error")}])
            if not d:
                st["cases_agree"] += 1
            else:
                # classify: does any material of the case sit on the 10 % boundary (|r - 0.1| < 1e-9),
                # or between its own F and the fold's largest F?
                own = IND.decide(rows, FS, "own")["L1"] if mode == "max" else ind
                rr = [x["r"] for f in own["folds"].values() for x in f["materials"].values()]
                boundary = any(abs(r - 0.1) < 1e-9 for r in rr if r == r)
                st.setdefault("all", []).append({"case": i, "on_10pct_boundary": boundary,
                                                 "what": sorted({x["what"] for x in d})})
            for x in d:
                w = x["what"]
                st["by_what"][w] = st["by_what"].get(w, 0) + 1
                nseg = None
                if "material" in x:
                    mm = minimal_material(rows, x["fold"], x["material"])
                    nseg = mm["n_seg"]
                ex = st["examples"].get(w)
                if ex is None or (nseg is not None and nseg < ex.get("n_seg", 1e9)):
                    rec = {"case": i, "scenario": scen, "diff": x}
                    if nseg is not None:
                        rec["n_seg"] = nseg
                        rec["minimal_material_data"] = mm
                    st["examples"][w] = rec
    report["modes"] = stats
    report["criterion4"] = criterion4_check()
    report["random_coverage"] = beats_seen
    out = os.path.join(ROOT, "results", "independent_decide_check.json")
    json.dump(report, open(out, "w", encoding="utf-8"), indent=1, default=float)
    for m in ("max", "own"):
        print(m, {k: stats[m][k] for k in ("cases", "cases_agree", "fold_comparisons", "material_comparisons", "by_what")})
    print("coverage", beats_seen)
    print("real", {m: len(v) for m, v in report["real"]["null_rep0_preD"].items()} if "max" in report["real"]["null_rep0_preD"] else report["real"])
    for k, v in report["special"].items():
        print(k, v if "code_error" in v else {m: [x["what"] for x in d] for m, d in v.items()})


if __name__ == "__main__":
    main()
