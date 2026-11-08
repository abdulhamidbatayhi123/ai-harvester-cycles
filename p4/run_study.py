"""Confirmatory runner of PREREG_P4 (sections 4, 5, 7 and 11). Run on real data ONLY after the
freeze; before it, only with --synthetic (plumbing check on synthetic uptake).

For each outer fold (8 LOSO and the 2 LOFO folds that differ from them):
  1. physics, all fitted by the scored metric (median E; section 5): fit B0, B0-b and B1 on the
     training sorbents (validation sorbent included) and choose the comparator by the median
     over those sorbents of the per-sorbent median E; B2 and the oracle B0* (k'' fitted on the
     held-out sorbent itself, H4b); per-segment |dw| and violation flags of data and comparator;
  2. for L1 and L2: train each grid configuration (seed 0), choose on the validation sorbent,
     then train 5 seeds of the chosen configuration; the prediction is the seed mean;
  3. score every model on the held-out groups: per-segment E (section 6).
Rows go to <out>/rows.jsonl, one per (fold, model, config, seed) step; finished steps are skipped
on restart. Seed predictions are cached in <out>/pred/.

usage: python -E -s -m p4.run_study <data_derived/bezrukov2023> <out_dir> [--synthetic [N|null] [--rep k]]
       [--fast] [--rule R1|R2] [--seeds n] [--grid n] [--loso-only] [--configs-from rows.jsonl]
(--rule R1 runs the pre-registered dry-mass sensitivity analysis into a separate out_dir)
"""
from __future__ import annotations

import json
import os
import sys
import time

import numpy as np
import torch

from p4.dataset import build_groups
from p4.physics import fit_b2, fit_scale, fit_scale_metric, rh50, simulate_b0, simulate_b1, violations
from p4.segments import DT_MIN, normalised_rms
from p4.train import isotherms_by_material, predict, train_two_stage

PRIMARY8 = ["ROS-037", "ROS-039", "ROS-040", "MOF-303", "MIL-160", "CAU-10", "Al-fumarate", "Syloid"]
COMPOSITE_OF = {"ROS-037": "ROS-037_composite", "ROS-039": "ROS-039_composite"}
FAMILIES = {
    "Al-rod": ["MOF-303", "MIL-160", "CAU-10", "Al-fumarate"],
    "Zn-triazolate-F": ["ROS-039", "ROS-040", "ROS-039_composite"],
    "Cu-glutarate-bpy": ["ROS-037", "ROS-037_composite"],
    "silica": ["Syloid"],
}
GRID = [{"width": w, "depth": 2, "wd": wd, "lr": 1e-3} for w in (16, 32) for wd in (1e-4, 1e-3)]
SEEDS = [0, 1, 2, 3, 4]


def folds():
    """8 LOSO folds and the LOFO folds that differ from every LOSO fold. The silica and
    Cu-glutarate LOFO folds hold out exactly the Syloid and ROS-037 LOSO sorbents, so they are
    not trained again; p4.decide reads their LOSO rows (review finding M6)."""
    out = []
    for s in PRIMARY8:
        out.append(("LOSO:" + s, [s] + ([COMPOSITE_OF[s]] if s in COMPOSITE_OF else [])))
    loso_sets = [set(h) for _, h in out]
    for fam, members in FAMILIES.items():
        if set(members) not in loso_sets:
            out.append(("LOFO:" + fam, members))
    return out


def val_sorbent(held):
    for cand in ("Syloid", "ROS-040", "CAU-10"):
        if cand not in held:
            return cand
    raise ValueError(held)


def sub(groups, T, d):
    out = []
    for g in groups:
        if g["temp"] != T:
            continue
        s = g["dir"] == (1 if d == "ads" else -1)
        if s.any():
            out.append({"rh": g["rh"][s], "w": g["w"][s], "m": g["m"][s], "ads": g["ads"], "des": g["des"]})
    return out


def fit_physics(groups, simulate, use_des, metric=True):
    """k'' per temperature and direction, fitted by the scored metric, the median of E (review
    findings F1 and N5: the learned models are validated on that metric, so the comparators and
    the oracle B0* are fitted on it too). metric=False gives the least-squares fit."""
    k2 = {}
    for T in ("27C", "60C"):
        for d in ("ads", "des"):
            gs = sub(groups, T, d)
            if not gs:
                continue
            if not use_des:
                gs = [{**g, "des": None} for g in gs]
            k2[(T, d)] = (fit_scale_metric if metric else fit_scale)(gs, simulate, d, dt=DT_MIN)
    return k2


def physics_pred(groups, simulate, k2, use_des):
    out = []
    for g in groups:
        ka, kd = k2[(g["temp"], "ads")] / g["m"], k2[(g["temp"], "des")] / g["m"]
        out.append(simulate(g["rh"], g["w"][:, 0], ka, kd, g["ads"], g["des"] if use_des else None, dt=DT_MIN))
    return out


def physics_E(groups, simulate, k2, use_des, preds=None):
    preds = physics_pred(groups, simulate, k2, use_des) if preds is None else preds
    return sum((seg_E(p, g["w"]) for g, p in zip(groups, preds)), [])


def seg_dw(groups):
    """|measured change| per segment (wt%), for the section 7 test on unnormalised errors."""
    out = []
    for g in groups:
        for w in g["w"]:
            w = w[np.isfinite(w)]
            out.append(float(abs(w[-1] - w[0])))
    return out


def b2_E(train, te):
    """B2: log k'' = a + b * rh50/30 per temperature and direction, fitted on `train` by the
    scored metric."""
    ab = {}
    for T in ("27C", "60C"):
        for d in ("ads", "des"):
            gs = [{**g, "des": None} for g in sub(train, T, d)]
            if gs:
                ab[(T, d)] = fit_b2(gs, d, dt=DT_MIN, metric=True)
    E = []
    for g in te:
        x = rh50(g["ads"]) / 30.0
        ka = np.exp(ab[(g["temp"], "ads")][0] + ab[(g["temp"], "ads")][1] * x) / g["m"]
        kd = np.exp(ab[(g["temp"], "des")][0] + ab[(g["temp"], "des")][1] * x) / g["m"]
        E += seg_E(simulate_b0(g["rh"], g["w"][:, 0], ka, kd, g["ads"], None, dt=DT_MIN), g["w"])
    return E, {f"{a}|{b}": v for (a, b), v in ab.items()}


CANDIDATES = {"B0": (simulate_b0, False), "B0-b": (simulate_b0, True), "B1": (simulate_b1, False)}


def choose_comparator(fit_on, k_fit):
    """Comparator choice on the fold's training sorbents (review finding O2), not on one
    validation sorbent: each candidate, fitted on all training sorbents by the scored metric, is
    scored by the median over training sorbents of its per-sorbent median E; the lowest wins.
    The three candidates have the same four parameters (one k'' per temperature and direction),
    so an in-sample comparison does not favour a more flexible one. Inner leave-one-sorbent-out
    was costed and rejected (PREREG section 11). Returns (choice, {candidate: score},
    {candidate: per-sorbent scores})."""
    mats = sorted({g["sorbent"] for g in fit_on})
    per = {c: {} for c in CANDIDATES}
    for c, (sim, des) in CANDIDATES.items():
        for s in mats:
            gs = [g for g in fit_on if g["sorbent"] == s]
            per[c][s] = float(np.nanmedian(physics_E(gs, sim, k_fit[c], des)))
    score = {c: float(np.median(list(v.values()))) for c, v in per.items()}
    return min(score, key=score.get), score, per


def viol(groups, preds):
    """Per-segment physical-violation flags (PREREG section 6) for predictions (list per group)."""
    out = []
    for g, p in zip(groups, preds):
        out += violations(p, g["rh"], g["dir"], g["ads"], g["des"]).tolist()
    return out


def seg_E(pred, w):
    out = []
    for p, ww in zip(pred, w):
        n = int(np.isfinite(ww).sum())
        out.append(normalised_rms(p[:n], ww[:n]))
    return out


def seg_ids(groups):
    """One id per held-out segment: '<session>|<temperature>|<from>><to>#<run file>#<plateau>'.
    The part before the first '#' is the inference cluster of PREREG section 7: one RH step in one
    measuring session, so the two pans of a pair and the repeats of a step within a file fall in
    one cluster (review finding M5: whole sessions are too few, MOF-303 has one per temperature).
    g["exp"] ends in the plateau number; it is dropped here, or every repeat would be its own cluster."""
    return [f"{e.rsplit('|', 1)[0]}|{g['temp']}|{s.rh_from:.0f}>{s.rh_to:.0f}#{r}#{s.index}"
            for g in groups for e, r, s in zip(g["exp"], g["run"], g["segments"])]


class Rows:
    def __init__(self, path):
        self.path = path
        self.done = {}
        if os.path.exists(path):
            for line in open(path, encoding="utf-8"):
                r = json.loads(line)
                self.done[r["key"]] = r

    def get(self, key):
        return self.done.get(key)

    def put(self, row):
        with open(self.path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(row, default=float) + "\n")
        self.done[row["key"]] = row


def main():
    root, out = sys.argv[1], sys.argv[2]
    synthetic, fast = "--synthetic" in sys.argv, "--fast" in sys.argv
    world = sys.argv[sys.argv.index("--synthetic") + 1] if synthetic and len(sys.argv) > sys.argv.index("--synthetic") + 1         and not sys.argv[sys.argv.index("--synthetic") + 1].startswith("--") else "N"
    arg = lambda name, default: int(sys.argv[sys.argv.index(name) + 1]) if name in sys.argv else default
    rep, n_seeds, n_grid = arg("--rep", 0), arg("--seeds", None), arg("--grid", None)
    loso_only = "--loso-only" in sys.argv
    # R1 sensitivity run (PREREG section 11): reuse each fold's configuration chosen under R2
    cfg_from = {}
    if "--configs-from" in sys.argv:
        for line in open(sys.argv[sys.argv.index("--configs-from") + 1], encoding="utf-8"):
            r = json.loads(line)
            if r["key"].endswith("|ensemble"):
                cfg_from[(r["fold"], r["kind"])] = GRID.index(r["cfg"])
    rule = sys.argv[sys.argv.index("--rule") + 1] if "--rule" in sys.argv else "R2"
    os.makedirs(os.path.join(out, "pred"), exist_ok=True)
    torch.set_num_threads(2)
    log = lambda s: print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} {s}", flush=True)
    groups = [g for g in build_groups(root, rule=rule) if g["sorbent"] in PRIMARY8 + list(COMPOSITE_OF.values())]
    log(f"dry-mass rule {rule}; {sum(len(g['m']) for g in groups)} segments in {len(groups)} groups")
    if synthetic:
        sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "audit"))
        from synthetic_harness import fit_k2, synthesise, synthesise_null
        k_true = fit_k2([g for g in groups if g["sorbent"] in PRIMARY8])
        if world == "null":
            groups, draws = synthesise_null(groups, k_true, seed=rep)
            with open(os.path.join(out, "null_world.json"), "w", encoding="utf-8") as fh:
                json.dump({"rep": rep, "draws": draws, "k_true": {f"{a}|{b}": v for (a, b), v in k_true.items()}}, fh, indent=1)
            log(f"null world, replicate {rep}")
        else:
            groups = synthesise(groups, k_true, corrected=False, seed=7)
    iso = isotherms_by_material(groups)
    rows = Rows(os.path.join(out, "rows.jsonl"))
    kw = {"steps_rate": 200, "steps_roll": 20, "eval_every": 10} if fast else {}
    grid = GRID[:1] if fast else GRID[:n_grid] if n_grid else GRID
    seeds = SEEDS[:2] if fast else SEEDS[:n_seeds] if n_seeds else SEEDS
    flist = folds()[:2] if fast else folds()
    if loso_only:
        flist = [f for f in flist if f[0].startswith("LOSO")]
    for fold, held in flist:
        vs = val_sorbent(held)
        tr = [g for g in groups if g["sorbent"] not in held and g["sorbent"] != vs]
        va = [g for g in groups if g["sorbent"] == vs]
        te = [g for g in groups if g["sorbent"] in held]
        ids = seg_ids(te)
        # 1. physics
        key = f"{fold}|physics"
        if not rows.get(key):
            fit_on = tr + va
            t0 = time.time()
            k_fit = {c: fit_physics(fit_on, sim, des) for c, (sim, des) in CANDIDATES.items()}
            base, inner_score, inner_per = choose_comparator(fit_on, k_fit)
            use_des = bool(inner_score["B0-b"] < inner_score["B0"])
            pred = {c: physics_pred(te, sim, k_fit[c], des) for c, (sim, des) in CANDIDATES.items()}
            E = {c: physics_E(te, None, None, None, preds=pred[c]) for c in CANDIDATES}
            b0v = "B0-b" if use_des else "B0"
            oracle = {}
            for s in held:
                own = [g for g in te if g["sorbent"] == s]
                if own:
                    k_own = fit_physics(own, simulate_b0, use_des)
                    oracle[s] = physics_E(own, simulate_b0, k_own, use_des)
            E_b2, ab2 = b2_E(fit_on, te)
            rows.put({"key": key, "fold": fold, "held": held, "val": vs, "B0_variant": b0v,
                      "B2_ab": ab2, "viol_data": viol(te, [g["w"] for g in te]),
                      "viol_base": viol(te, pred[base]), "dw": seg_dw(te),
                      "comparator": base, "k2": {f"{a}|{b}": v for (a, b), v in k_fit[b0v].items()},
                      "k2_all": {c: {f"{a}|{b}": v for (a, b), v in k.items()} for c, k in k_fit.items()},
                      "choice_score": inner_score, "choice_per_sorbent": inner_per, "seg": ids,
                      "E": {"B0": E[b0v], "B0-b_or_B0_other": E["B0" if use_des else "B0-b"], "B1": E["B1"],
                            "base": E[base], "B2": E_b2,
                            "B0star": sum((oracle[s] for s in held if s in oracle), [])},
                      "s": time.time() - t0})
            log(f"{fold}: physics done ({b0v}; comparator {base}; {time.time() - t0:.0f}s)")
        ph = rows.get(key)
        k2 = {tuple(k.split("|")): v for k, v in ph["k2"].items()}
        # 2. learned models
        for kind in ("L1", "L2"):
            best_cfg, best_v = cfg_from.get((fold, kind)), float("inf")
            for ci, cfg in enumerate(grid if best_cfg is None else []):
                k = f"{fold}|{kind}|cfg{ci}|tune"
                if not rows.get(k):
                    t0 = time.time()
                    _, v = train_two_stage(kind, tr, va, k2, iso, seed=0, **cfg, **kw)
                    rows.put({"key": k, "fold": fold, "kind": kind, "cfg": cfg, "val_medE": v, "s": time.time() - t0})
                    log(f"{fold} {kind} cfg{ci} val {v:.4f}")
                if rows.get(k)["val_medE"] < best_v:
                    best_cfg, best_v = ci, rows.get(k)["val_medE"]
            preds = []
            for seed in seeds:
                pf = os.path.join(out, "pred", f"{fold.replace(':', '_')}_{kind}_s{seed}.npz")
                k = f"{fold}|{kind}|seed{seed}"
                if not (rows.get(k) and os.path.exists(pf)):
                    t0 = time.time()
                    model, v = train_two_stage(kind, tr, va, k2, iso, seed=seed, **GRID[best_cfg], **kw)
                    arrs = {f"g{i}": predict(model, kind, g, k2, iso)[0] for i, g in enumerate(te)}
                    np.savez_compressed(pf, **arrs)
                    rows.put({"key": k, "fold": fold, "kind": kind, "cfg": best_cfg, "seed": seed, "val_medE": v,
                              "s": time.time() - t0})
                    log(f"{fold} {kind} seed {seed} val {v:.4f}")
                z = np.load(pf)
                preds.append([z[f"g{i}"] for i in range(len(te))])
            k = f"{fold}|{kind}|ensemble"
            if not rows.get(k):
                E, means = [], []
                for i, g in enumerate(te):
                    mean = np.mean([p[i] for p in preds], axis=0)
                    means.append(mean)
                    E += seg_E(mean, g["w"])
                rows.put({"key": k, "fold": fold, "kind": kind, "cfg": GRID[best_cfg], "n_seeds": len(preds),
                          "seg": ids, "E": E, "viol": viol(te, means)})
                log(f"{fold} {kind} ensemble median E {np.nanmedian(E):.4f}")
    log("done")


if __name__ == "__main__":
    main()
