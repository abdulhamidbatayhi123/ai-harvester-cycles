"""Confirmatory runner of PREREG_P4 (sections 4, 5, 7 and 11). Run on real data ONLY after the
freeze; before it, only with --synthetic (plumbing check on synthetic uptake).

For each outer fold (8 LOSO, 4 LOFO):
  1. fit B0, B0-b and B1 on the training sorbents (k'' per temperature and direction);
     choose B0 or B0-b on the validation sorbent (section 5);
  2. for L1 and L2: train each grid configuration (seed 0), choose on the validation sorbent,
     then train 5 seeds of the chosen configuration; the prediction is the seed mean;
  3. score every model on the held-out groups: per-segment E (section 6), plus the oracle B0*
     (k'' fitted on the held-out sorbent itself, H4b).
Rows go to <out>/rows.jsonl, one per (fold, model, config, seed) step; finished steps are skipped
on restart. Seed predictions are cached in <out>/pred/.

usage: python -I -m p4.run_study <data_derived/bezrukov2023> <out_dir> [--synthetic [N|null] [--rep k]]
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


def fit_physics(groups, simulate, use_des, metric=False):
    """k'' per temperature and direction. metric=True fits the oracle B0* by the scored metric
    (median E) instead of least squares (review finding F1)."""
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


def physics_E(groups, simulate, k2, use_des):
    E = []
    for g in groups:
        ka, kd = k2[(g["temp"], "ads")] / g["m"], k2[(g["temp"], "des")] / g["m"]
        pred = simulate(g["rh"], g["w"][:, 0], ka, kd, g["ads"], g["des"] if use_des else None, dt=DT_MIN)
        E += seg_E(pred, g["w"])
    return E


def b2_E(train, te):
    """B2: log k'' = a + b * rh50/30 per temperature and direction, fitted on `train`."""
    ab = {}
    for T in ("27C", "60C"):
        for d in ("ads", "des"):
            gs = [{**g, "des": None} for g in sub(train, T, d)]
            if gs:
                ab[(T, d)] = fit_b2(gs, d, dt=DT_MIN)
    E = []
    for g in te:
        x = rh50(g["ads"]) / 30.0
        ka = np.exp(ab[(g["temp"], "ads")][0] + ab[(g["temp"], "ads")][1] * x) / g["m"]
        kd = np.exp(ab[(g["temp"], "des")][0] + ab[(g["temp"], "des")][1] * x) / g["m"]
        E += seg_E(simulate_b0(g["rh"], g["w"][:, 0], ka, kd, g["ads"], None, dt=DT_MIN), g["w"])
    return E, {f"{a}|{b}": v for (a, b), v in ab.items()}


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
                json.dump({"rep": rep, "draws_a_b": draws, "k_true": {f"{a}|{b}": v for (a, b), v in k_true.items()}}, fh, indent=1)
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
            k_b0 = fit_physics(fit_on, simulate_b0, False)
            k_b0b = fit_physics(fit_on, simulate_b0, True)
            k_b1 = fit_physics(fit_on, simulate_b1, False)
            v_b0 = np.nanmedian(physics_E(va, simulate_b0, k_b0, False))
            v_b0b = np.nanmedian(physics_E(va, simulate_b0, k_b0b, True))
            v_b1 = np.nanmedian(physics_E(va, simulate_b1, k_b1, False))
            use_des = bool(v_b0b < v_b0)
            k_base = k_b0b if use_des else k_b0
            # comparator for H4a (review finding M7): the best isotherm-only physics model on the
            # validation sorbent, among B0, B0-b and B1
            base = min((("B0", v_b0), ("B0-b", v_b0b), ("B1", v_b1)), key=lambda x: x[1])[0]
            E_b0 = physics_E(te, simulate_b0, k_base, use_des)
            E_b1 = physics_E(te, simulate_b1, k_b1, False)
            oracle = {}
            for s in held:
                own = [g for g in te if g["sorbent"] == s]
                if own:
                    k_own = fit_physics(own, simulate_b0, use_des, metric=True)
                    oracle[s] = physics_E(own, simulate_b0, k_own, use_des)
            E_b2, ab2 = b2_E(fit_on, te)
            rows.put({"key": key, "fold": fold, "held": held, "val": vs, "B0_variant": "B0-b" if use_des else "B0",
                      "B2_ab": ab2, "viol_data": viol(te, [g["w"] for g in te]),
                      "comparator": base, "k2": {f"{a}|{b}": v for (a, b), v in k_base.items()},
                      "val_E": {"B0": v_b0, "B0-b": v_b0b, "B1": v_b1}, "seg": ids,
                      "E": {"B0": E_b0, "B1": E_b1, "base": E_b1 if base == "B1" else E_b0,
                            "B2": E_b2, "B0star": sum((oracle[s] for s in held if s in oracle), [])}})
            log(f"{fold}: physics done ({'B0-b' if use_des else 'B0'}; comparator {base})")
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
