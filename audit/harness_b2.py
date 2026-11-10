"""Synthetic harness for H4a' (PREREG section 10b): can the section 7 rule, applied to B2
(log k'' = a + b * (RH50/30 - mean) per temperature and direction, B0 otherwise) against the
pooled B0 of the same form, find a rate constant that the isotherm predicts, how often would it
find one of the measured size, and does it stay silent when the rate constant varies between
sorbents for reasons the isotherm does not carry?

Version 2, 2026-11-10, after an independent red-team review of version 1 (da52584), whose single
run was stopped before any result was read (results/harness_b2_aborted_unread/, kept unread).
Written before any B2 fit on held-out real data. Changes from version 1: realistic-power worlds
K2a-c (red-team B1), six null worlds instead of three (M9), the real per-sorbent F (M11), the
admissibility check (m15), a form-error world C3 reported as a confound check (M5, M8), and the
better-conditioned B2 fit in p4.physics.fit_b2 (M10).

Worlds, all on the real forcing, real isotherms and real dry masses of the primary set and the two
composites, AR(1) noise (0.01 wt%, phi 0.9), truth integrated with the B0 integrator unless stated:

  N    truth = B0 with the pooled k'' of the real data (least squares).
  K    log k''_s,T,dir = log k''_T,dir + 1.5 (RH50_s,T - mean_T RH50) / 30, the mean over the 8
       primary sorbents: across-sorbent SD of log k'' 0.27 at 27 C, 0.33 at 60 C. No offsets. The
       truth is inside B2's class: a plumbing check.
  K2a, K2b, K2c  realistic power: the same form with BETA_T chosen so that the across-sorbent SD
       of BETA_T * RH50/30 equals the real in-sample SD of log k'' (0.089 at 27 C, 0.300 at 60 C),
       plus the equilibrium offsets of the null worlds (own draws). This is the largest effect
       of the measured size that the isotherm could carry. Reported; sets the wording of a real
       "falsified".
  S0 ... S5  structure-free null (cs T-P4-5 R1 without the shape term): log k''_s,T shifted by
       b ~ N(0, SD_B(T)^2) independent of the isotherm, one b per sorbent and temperature for
       both directions; equilibrium = isotherm x (1 + eps), |eps| resampled from the 18 measured
       group offsets, random sign, |eps w30| <= 3.128 wt%. Any beat is a false positive of a null
       without model-form error.
  C3   form error, reported only: the L1 harness world C3 (audit/synthetic_harness.py, seed 1), a
       rate law shared by every material but not of B0's form. A B2 beat here would come from
       isotherm shape changing B0's best effective k'', not from a material-dependent k''.

Draws: b and eps from default_rng([2000 + j, crc32("sorbent|T")]) for null world j and
([3000 + j, ...]) for K2 world j (offsets only); noise from default_rng(world_seed + 10), world
seeds N 1, K 1, K2a-c 21-23, S0-S5 0-5 (N and K share noise; the S worlds do not share with them
except S1, whose noise seed 11 equals N's: harmless, the truths differ). Composites get their own
draws and their own RH50.

Each world runs the 8 LOSO folds (composites held with their parent). Per fold, B0 and B2 are
fitted on the training sorbents by the scored metric and the rule of p4.decide is applied with
each material's real F (results/prefreeze/checks2.json), plus the admissibility check of section 7.

Pass criteria (fixed before any run of this version):
  1. world N: no fold beaten;
  2. world K: at least 7 of 8 folds beaten, and the median over folds and strata of
     |b_fit / 1.5 - 1| at most 0.25;
  3. worlds S0-S5 (48 fold-fits): one-sided 95 % Clopper-Pearson upper bound on the per-fold
     beat rate at most 0.40; no world with 5 or more of 8 folds beaten; median r below 0.025.
Reported, not pass conditions: per K2 world the number of beaten folds and the H4a' verdict it
would give (supported / falsified / not established); C3 likewise.

usage: python -I audit/harness_b2.py data_derived/bezrukov2023 <out_dir> <world,world,...>
       python -I audit/harness_b2.py --evaluate <out.json> <harness_b2.json> [<harness_b2.json> ...]
"""
import json
import os
import sys
import time
import zlib

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from p4.dataset import build_groups  # noqa: E402
from p4.decide import REL, VIOL_MARGIN, cluster_level, rule, sorbent_F  # noqa: E402
from p4.physics import Branch, fit_scale, fit_scale_metric, rh50, simulate_b0  # noqa: E402
from p4.run_study import b2_E, folds, seg_dw, seg_E, seg_ids, sub, viol  # noqa: E402
from p4.segments import DT_MIN  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PRIMARY8 = ["ROS-037", "ROS-039", "ROS-040", "MOF-303", "MIL-160", "CAU-10", "Al-fumarate", "Syloid"]
F = sorbent_F(json.load(open(os.path.join(ROOT, "results", "prefreeze", "checks2.json"), encoding="utf-8")))
BETA = 1.5
SD_B = {"27C": 0.089, "60C": 0.300}          # real in-sample SD of log k'' (section 10)
EPS = (0.001, 0.452, 0.000, 0.007, -0.005, -0.036, 0.038, 0.060, -0.011, 0.006, 0.059, -0.037,
       -0.038, 0.012, -0.007, 0.023, -0.024, 0.221)
OFFSET_MAX_WT = 3.128
NOISE_SD, NOISE_PHI = 0.01, 0.9
SEED = {"N": 1, "K": 1, "K2a": 21, "K2b": 22, "K2c": 23, "C3": 1, **{f"S{j}": j for j in range(6)}}
NULLS = [f"S{j}" for j in range(6)]
POWER = ["K2a", "K2b", "K2c"]


def ar1(rng, shape):
    e = rng.normal(0, NOISE_SD * np.sqrt(1 - NOISE_PHI ** 2), shape)
    x = np.empty(shape)
    x[:, 0] = rng.normal(0, NOISE_SD, shape[0])
    for i in range(1, shape[1]):
        x[:, i] = NOISE_PHI * x[:, i - 1] + e[:, i]
    return x


def fit_k2(groups, metric):
    k2 = {}
    for T in ("27C", "60C"):
        for d in ("ads", "des"):
            gs = [{**g, "des": None} for g in sub(groups, T, d)]
            k2[(T, d)] = (fit_scale_metric if metric else fit_scale)(gs, simulate_b0, d, dt=DT_MIN)
    return k2


def draw(s, T, base, j):
    rng = np.random.default_rng([base + j, zlib.crc32(f"{s}|{T}".encode("utf-8"))])
    b = float(rng.normal(0, SD_B[T]))
    eps = float(rng.choice(np.abs(EPS))) * (1.0 if rng.random() < 0.5 else -1.0)
    return b, eps


def capped(eps, ads):
    w30 = float(ads.w_of_rh(30.0))
    return float(np.sign(eps)) * OFFSET_MAX_WT / w30 if abs(eps) * w30 > OFFSET_MAX_WT else eps


def synthesise(real, k_true, world):
    if world == "C3":
        sys.path.insert(0, os.path.join(ROOT, "audit"))
        from synthetic_harness import synthesise as syn_l1      # torch truth of the L1 harness
        return syn_l1(real, k_true, "C3", seed=SEED["C3"]), {"world": "C3 of audit/synthetic_harness.py"}, None
    per = {(g["sorbent"], g["temp"]): rh50(g["ads"]) / 30.0 for g in real if g["sorbent"] in PRIMARY8}
    mean = {T: float(np.mean([v for (s, t), v in per.items() if t == T])) for T in ("27C", "60C")}
    sd = {T: float(np.std([v for (s, t), v in per.items() if t == T], ddof=1)) for T in ("27C", "60C")}
    beta = {T: (BETA if world == "K" else SD_B[T] / sd[T] if world in POWER else 0.0) for T in ("27C", "60C")}
    rng = np.random.default_rng(SEED[world] + 10)
    out, info = [], {"beta": beta, "mean_x": mean}
    for g in real:
        T, ads = g["temp"], g["ads"]
        x = rh50(ads) / 30.0
        lf, eps = beta[T] * (x - mean[T]), 0.0
        if world in NULLS:
            lf, eps = draw(g["sorbent"], T, 2000, SEED[world])
        elif world in POWER:
            eps = draw(g["sorbent"], T, 3000, SEED[world])[1]
        eps = capped(eps, ads) if eps else 0.0
        info[f"{g['sorbent']}|{T}"] = {"log_factor": lf, "eps": eps}
        truth_ads = Branch.from_points(ads.rh, ads.w * (1.0 + eps)) if eps else ads
        f = np.exp(lf)
        w = simulate_b0(g["rh"], g["w"][:, 0], f * k_true[(T, "ads")] / g["m"], f * k_true[(T, "des")] / g["m"],
                        truth_ads, None, dt=DT_MIN)
        w = np.where(np.isfinite(g["w"]), w, np.nan)
        w = w + np.nan_to_num(ar1(rng, w.shape)) * np.isfinite(w)
        out.append({**g, "w": w})
    return out, info, beta


def judge(te, E_b2, E_b0, pred_b2, pred_b0):
    b0, m, D, mat, dd = cluster_level(seg_ids(te), E_b0, E_b2, seg_dw(te), with_d=True)
    per = {}
    for s in sorted({g["sorbent"] for g in te}):
        sel = mat == s
        per[s] = rule(b0[sel], m[sel], F[s], D[sel], dd[sel]) if sel.any() else (False, {"r": -np.inf})
    vm = np.array(viol(te, pred_b2), bool)
    vd = np.array(viol(te, [g["w"] for g in te]), bool)
    vb = np.array(viol(te, pred_b0), bool)
    excess = float(np.mean(vm & ~vd & ~vb))
    ok = all(v[0] for v in per.values()) and excess <= VIOL_MARGIN
    r = float(min(v[1]["r"] for v in per.values()))
    return ok, r, excess, {s: v[1] for s, v in per.items()}


def verdict(folds_):
    n = sum(f["beats"] for f in folds_.values())
    n_rel = sum(f["r"] >= REL for f in folds_.values())
    return "supported" if n >= 7 else "falsified" if n_rel <= 1 else "not established"


def run(root, out, worlds):
    os.makedirs(out, exist_ok=True)
    path = os.path.join(out, "harness_b2.json")
    res = json.load(open(path, encoding="utf-8")) if os.path.exists(path) else {"version": 2, "worlds": {}}
    log = lambda s: print(f"{time.strftime('%H:%M:%S')} {s}", flush=True)
    real = [g for g in build_groups(root) if g["sorbent"] in PRIMARY8 or g["sorbent"].endswith("_composite")]
    k_true = fit_k2([g for g in real if g["sorbent"] in PRIMARY8], metric=False)
    res["k_true"] = {f"{a}|{b}": v for (a, b), v in k_true.items()}
    loso = [f for f in folds() if f[0].startswith("LOSO")]
    for world in worlds:
        syn, info, _ = synthesise(real, k_true, world)
        W = res["worlds"].setdefault(world, {"truth": info, "folds": {}})
        for name, held in loso:
            if name in W["folds"]:
                continue
            t0 = time.time()
            tr = [g for g in syn if g["sorbent"] not in held]
            te = [g for g in syn if g["sorbent"] in held]
            k_fit = fit_k2(tr, metric=True)
            pred_b0 = [simulate_b0(g["rh"], g["w"][:, 0], k_fit[(g["temp"], "ads")] / g["m"],
                                   k_fit[(g["temp"], "des")] / g["m"], g["ads"], None, dt=DT_MIN) for g in te]
            E_b0 = sum((seg_E(p, g["w"]) for g, p in zip(te, pred_b0)), [])
            E_b2, ab, pred_b2 = b2_E(tr, te, return_pred=True)
            ok, r, excess, per = judge(te, np.array(E_b2), np.array(E_b0), pred_b2, pred_b0)
            W["folds"][name] = {"beats": ok, "r": r, "violation_excess": excess, "per_material": per,
                                "b2_ab": ab, "E_B0": float(np.nanmedian(E_b0)), "E_B2": float(np.nanmedian(E_b2)),
                                "s": time.time() - t0}
            log(f"{world} {name}: beats={ok} r={r:.3f} E_B0={np.nanmedian(E_b0):.4f} E_B2={np.nanmedian(E_b2):.4f} "
                f"b={ {k: round(v[1], 3) for k, v in ab.items()} } ({time.time() - t0:.0f}s)")
            json.dump(res, open(path, "w", encoding="utf-8"), indent=1, default=float)
    log("done")


def cp_upper(k, n, a=0.05):
    from scipy.stats import beta
    return 1.0 if k >= n else float(beta.ppf(1 - a, k + 1, n - k))


def evaluate(out_path, paths):
    Wd = {}
    for p in paths:
        Wd.update(json.load(open(p, encoding="utf-8"))["worlds"])
    need = ["N", "K", *NULLS]
    missing = [w for w in need + POWER + ["C3"] if w not in Wd or len(Wd[w]["folds"]) < 8]
    if any(w in missing for w in need):
        print(f"incomplete ({missing}): criteria not evaluated", flush=True)
        return
    c1 = not any(f["beats"] for f in Wd["N"]["folds"].values())
    kb = sum(f["beats"] for f in Wd["K"]["folds"].values())
    berr = float(np.median([abs(ab[1] / BETA - 1) for f in Wd["K"]["folds"].values() for ab in f["b2_ab"].values()]))
    sb = [sum(f["beats"] for f in Wd[w]["folds"].values()) for w in NULLS]
    rs = [f["r"] for w in NULLS for f in Wd[w]["folds"].values()]
    ub = cp_upper(sum(sb), 8 * len(NULLS))
    res = {"summary": {"N_beats": sum(f["beats"] for f in Wd["N"]["folds"].values()), "K_beats": kb,
                       "K_median_rel_err_b": berr, "S_beats_per_world": sb, "S_cp95_upper": ub,
                       "S_median_r": float(np.median(rs)), "S_r_q90": float(np.quantile(rs, 0.9)),
                       "power_K2": {w: {"beats": sum(f["beats"] for f in Wd[w]["folds"].values()),
                                        "verdict": verdict(Wd[w]["folds"])} for w in POWER if w not in missing},
                       "C3_reported": ({"beats": sum(f["beats"] for f in Wd["C3"]["folds"].values()),
                                        "verdict": verdict(Wd["C3"]["folds"])} if "C3" not in missing else None),
                       "missing_reported_worlds": [w for w in missing if w not in need]},
           "pass": {"1_no_beat_in_N": c1, "2_K_found": kb >= 7 and berr <= 0.25,
                    "3_null_S": ub <= 0.40 and max(sb) <= 4 and float(np.median(rs)) < 0.025},
           "worlds": Wd}
    json.dump(res, open(out_path, "w", encoding="utf-8"), indent=1, default=float)
    print(f"SUMMARY {res['summary']}\nPASS criteria: {res['pass']}", flush=True)


if __name__ == "__main__":
    if sys.argv[1] == "--evaluate":
        evaluate(sys.argv[2], sys.argv[3:])
    else:
        run(sys.argv[1], sys.argv[2], sys.argv[3].split(","))
