"""Numbers for the Results section, computed from the confirmatory outputs (frozen protocol, tag prereg-p4-freeze).

Reads results/confirm_R2|R1/{rows.jsonl,decide.json}, results/final_verdict.json and results/prefreeze/checks2.json;
writes results/confirm_summary.json. Everything here is either the pre-registered verdict (copied) or a descriptive
summary named in PREREG sections 2, 7 and 8 (medians over a fold's held-out segments, as in p4/decide.py). Nothing
is fitted.

usage: python -I audit/summarise_confirm.py results/confirm_summary.json
"""
import json
import os
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PARENTS = ["ROS-037", "ROS-039", "ROS-040", "MOF-303", "MIL-160", "CAU-10", "Al-fumarate", "Syloid"]


def load(rule):
    d = json.load(open(os.path.join(ROOT, "results", f"confirm_{rule}", "decide.json"), encoding="utf-8"))
    rows = {r["fold"]: r for r in map(json.loads, open(os.path.join(ROOT, "results", f"confirm_{rule}", "rows.jsonl"),
                                                     encoding="utf-8")) if r["key"].endswith("|physics")}
    return d, rows


def med(x):
    return float(np.nanmedian(np.asarray(x, float)))


def per_rule(rule, F):
    d, rows = load(rule)
    h = d["H4a"]["B2"]
    out = {"verdict": h["verdict"], "loso_beats": h["LOSO_beats"], "loso_folds": h["LOSO_folds"],
           "n_folds_r_ge_10pct": h["n_folds_rel_ge_10pct"], "r_order7": h["rel_improvement_order7"],
           "r_max": max(h["rel_improvement_folds"]), "r_min": min(h["rel_improvement_folds"]),
           "lofo_beats": h["LOFO_beats_nontrivial"], "lofo_folds": h["LOFO_folds_nontrivial"], "sorbents": {}}
    for s in PARENTS:
        p = rows[f"LOSO:{s}"]
        e = {k: med(p["E"][k]) for k in ("B0", "B2", "B0star", "B0_endpoint_oracle", "B1")}
        # pooled figures of a parent + composite fold use the larger of the two floors (PREREG section 6)
        Fp = max(F[m] for m in p["held"])
        out["sorbents"][s] = {**e, "variant": p["B0_variant"], "F": Fp, "B0_over_F": e["B0"] / Fp,
                              "gap_closed_by_own_k": d["H4b"][s]["fraction_of_gap_closed"],
                              "endpoint_rel_reduction": (e["B0"] - e["B0_endpoint_oracle"]) / e["B0"],
                              "own_k_rel_reduction": (e["B0"] - e["B0star"]) / e["B0"],
                              "b": {k: v[1] for k, v in p["B2_ab"].items()}}
    S = out["sorbents"].values()
    out["summary"] = {
        "E_B0_min": min(x["B0"] for x in S), "E_B0_max": max(x["B0"] for x in S),
        "E_B1_min": min(x["B1"] for x in S), "E_B1_max": max(x["B1"] for x in S),
        "B0_over_F_min": min(x["B0_over_F"] for x in S), "B0_over_F_max": max(x["B0_over_F"] for x in S),
        "n_B2_worse_median": sum(x["B2"] > x["B0"] for x in S),
        "gap_closed_min": min(x["gap_closed_by_own_k"] for x in S),
        "gap_closed_max": max(x["gap_closed_by_own_k"] for x in S),
        "n_gap_closed_gt_half": sum(x["gap_closed_by_own_k"] > 0.5 for x in S),
        "n_endpoint_better": sum(x["B0_endpoint_oracle"] < x["B0"] for x in S),
        "endpoint_rel_reduction_min": min(x["endpoint_rel_reduction"] for x in S),
        "endpoint_rel_reduction_max": max(x["endpoint_rel_reduction"] for x in S),
        "endpoint_rel_reduction_median": float(np.median([x["endpoint_rel_reduction"] for x in S])),
        "own_k_rel_reduction_median": float(np.median([x["own_k_rel_reduction"] for x in S])),
        "n_endpoint_beats_own_k": sum(x["B0_endpoint_oracle"] < x["B0star"] for x in S),
        "b_min": min(v for x in S for v in x["b"].values()), "b_max": max(v for x in S for v in x["b"].values()),
        "n_variant_B0": sum(x["variant"] == "B0" for x in S),
        "n_comparator_B0": sum(rows[f"LOSO:{s}"]["comparator"] == "B0" for s in PARENTS),
        # the better of the two oracles, over the noise floor: how far even a correct k'' or end point stays above F
        "best_oracle_over_F_min": min(min(x["B0star"], x["B0_endpoint_oracle"]) / x["F"] for x in S),
    }
    # H4c: each sorbent of the two non-trivial family folds, median E of B0 in its LOFO against its LOSO fold
    fam = {}
    for f in ("LOFO:Al-rod", "LOFO:Zn-triazolate-F"):
        pf = rows[f]
        for s in pf["held"]:
            pl = rows[f"LOSO:{s.replace('_composite', '')}"]
            own = lambda p, key: med([e for e, sid in zip(p["E"][key], p["seg"]) if sid.split("|")[0] == s])
            fam[s] = {"B0_loso": own(pl, "B0"), "B0_lofo": own(pf, "B0"), "B2_loso": own(pl, "B2"), "B2_lofo": own(pf, "B2")}
    out["H4c"] = fam
    out["H4c_summary"] = {"n": len(fam), "n_B0_worse_lofo": sum(v["B0_lofo"] > v["B0_loso"] for v in fam.values()),
                          "n_B2_worse_lofo": sum(v["B2_lofo"] > v["B2_loso"] for v in fam.values())}
    # strata (PREREG section 6: temperature and direction reported separately): median over all LOSO held-out
    # segments of each stratum, B0 and B2; direction from the segment's from>to humidity
    st = {}
    for s in PARENTS:
        p = rows[f"LOSO:{s}"]
        for sid, e0, e2 in zip(p["seg"], p["E"]["B0"], p["E"]["B2"]):
            T = sid.split("|")[1]
            a, b = sid.split("|")[4].split("#")[0].split(">")
            key = f"{T}|{'ads' if float(b) > float(a) else 'des'}"
            st.setdefault(key, {"B0": [], "B2": []})
            st[key]["B0"].append(e0)
            st[key]["B2"].append(e2)
    out["strata"] = {k: {"n_seg": len(v["B0"]), "E_B0": med(v["B0"]), "E_B2": med(v["B2"])} for k, v in sorted(st.items())}
    return out


def main():
    F = json.load(open(os.path.join(ROOT, "results", "prefreeze", "checks2.json"), encoding="utf-8"))["F_within_segment_weighted"]
    fv = json.load(open(os.path.join(ROOT, "results", "final_verdict.json"), encoding="utf-8"))
    res = {"final_verdict": fv, "R2": per_rule("R2", F), "R1": per_rule("R1", F)}
    # between-pan and between-session agreement, reported beside F as a ceiling (PREREG section 6)
    fb = json.load(open(os.path.join(ROOT, "results", "prefreeze", "checks2.json"), encoding="utf-8"))["F_between"]
    pan = [v["F_between_pan"] for v in fb.values() if v.get("F_between_pan") is not None]
    ses = [v["F_between_session"] for v in fb.values() if v.get("F_between_session") is not None]
    res["F_between"] = {"pan_min": min(pan), "pan_max": max(pan), "session_min": min(ses), "session_max": max(ses)}
    # realistic-power worlds of the B2 harness: folds with r >= 10 % (exploratory count; the falsifier needs <= 1)
    hb = json.load(open(os.path.join(ROOT, "results", "harness_b2", "harness_b2.json"), encoding="utf-8"))["worlds"]
    res["K2_folds_r_ge_10pct"] = {w: sum(f["r"] >= 0.10 for f in hb[w]["folds"].values()) for w in ("K2a", "K2b", "K2c")}
    with open(sys.argv[1], "w", encoding="utf-8", newline="\n") as f:
        json.dump(res, f, indent=1)
    for r in ("R2", "R1"):
        print(r, json.dumps(res[r]["summary"]), json.dumps(res[r]["H4c_summary"]))


if __name__ == "__main__":
    main()
