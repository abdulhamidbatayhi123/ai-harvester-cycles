"""Apply the pre-registered decision rules (PREREG_P4 section 7) to the runner's rows.

Per fold and learned model, the paired difference d = E_base - E_model is averaged within each
experiment (the two pans of a pair are one experiment), and the rule is applied to the
experiment-level d: median(d) > F of the held-out sorbent, median(d) >= 10 % of median E_base,
and the 2.5 % bootstrap quantile of median(d) over experiments > 0. E_base is the comparator
chosen on the validation sorbent among B0, B0-b and B1 (rows written before that change: B0).

H4a, L1 primary and L2 secondary: supported if the model beats the comparator on >= 7 of 8 LOSO
folds; falsified only if the 95 % bootstrap interval over the LOSO folds of the mean relative
improvement lies wholly below 10 %; otherwise not established. Transfer across families requires
both non-trivial LOFO folds (Al-rod, Zn-triazolate-F).
H4b (descriptive): the fraction of (E_B0 - F) that B0*, fitted by median E, closes per sorbent.

usage: python -I -m p4.decide <rows.jsonl> <results/prefreeze/summary.json> <out.json>
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict

import numpy as np

REL = 0.10
# The silica and Cu-glutarate LOFO folds hold out the same sorbents as their LOSO folds (review
# finding M6), so the family rule rests on the two folds that hold out a whole family.
NONTRIVIAL_LOFO = ("LOFO:Al-rod", "LOFO:Zn-triazolate-F")
N_BOOT = 5000


def sorbent_F(summary):
    pairs = defaultdict(list)
    for key, v in summary["noise_floor"].items():
        s = key.split("|")[0]
        pairs[s] += [p["E"] for p in v["pairs"]]
    return {s: float(np.median(e)) for s, e in pairs.items()}


def experiment_level(seg_ids, e_b0, e_m):
    by = defaultdict(list)
    for sid, a, b in zip(seg_ids, e_b0, e_m):
        if np.isfinite(a) and np.isfinite(b):
            by[sid.split("#")[0]].append((a, b))
    b0 = np.array([np.mean([x[0] for x in v]) for v in by.values()])
    m = np.array([np.mean([x[1] for x in v]) for v in by.values()])
    return b0, m


def rule(e_b0, e_m, F, seed=0):
    rng = np.random.default_rng(seed)
    d = e_b0 - e_m
    gain = float(np.median(d))
    boots = np.array([np.median(d[rng.integers(0, len(d), len(d))]) for _ in range(N_BOOT)])
    lo = float(np.quantile(boots, 0.025))
    ok = bool(gain > F and gain >= REL * float(np.median(e_b0)) and lo > 0)
    return ok, {"median_gain": gain, "ci_low": lo, "E_B0": float(np.median(e_b0)),
                "E_model": float(np.median(e_m)), "F": F, "n_exp": int(len(d))}


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
        b0, m = experiment_level(r["seg"], p["E"].get("base", p["E"]["B0"]), r["E"])
        ok, info = rule(b0, m, Fh)
        out["folds"][f"{fold}|{kind}"] = {"beats_B0": ok, **info}
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
