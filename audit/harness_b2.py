"""Synthetic harness for H4a' (PREREG section 10b): can the section 7 rule, applied to B2
(log k'' = a + b * RH50/30 per temperature and direction) against B0, find a material-dependent
rate constant that the isotherm predicts, and does it stay silent when the rate constant varies
between sorbents for reasons the isotherm does not carry?

Written on 2026-11-10 after L1 failed harness round 7, before any B2 fit on held-out real data
(B2 has been run only inside the synthetic null replicate results/null_rep0_preD). Worlds, all on
the real forcing, real isotherms and real dry masses of the primary set, AR(1) noise (0.01 wt%,
phi 0.9), truth integrated with the same B0 integrator:

  N   truth = B0 with the pooled k'' of the real data.
  K   log k''_s,T,dir = log k''_T,dir + BETA * (RH50_s,T - mean_T RH50) / 30, mean over the 8
      primary sorbents. BETA = 1.5 gives an across-sorbent SD of log k'' of 0.33 at 60 C (real
      in-sample SD 0.30) and 0.27 at 27 C (real 0.089), over the 8 sorbents: an effect of the measured size that
      the isotherm carries by construction.
  S0, S1, S2  structure-free null (cs T-P4-5 R1 without the shape term): log k''_s,T =
      log k''_T,dir + b_s,T, b ~ N(0, SD_B(T)^2) per sorbent and temperature, independent of
      the isotherm; equilibrium offset eps with a random sign, |eps| resampled from the 18
      measured group offsets and capped at 3.128 wt% absolute. Any beat is a false positive.

Each world runs the 8 LOSO folds (composites held with their parent). Per fold B0 is fitted on
the training sorbents by the scored metric, B2 likewise (p4.run_study.b2_E), and the rule of
p4.decide is applied with the synthetic floor F = 0.003 for every material.

Pass criteria (fixed before any run of this script):
  1. world N: no fold beaten;
  2. world K: at least 7 of 8 folds beaten (the claim level of H4a'), and the median over folds
     and strata of |b_fit / BETA - 1| at most 0.25;
  3. worlds S0-S2 (24 fold-fits): one-sided 95 % Clopper-Pearson upper bound on the per-fold beat
     rate at most 0.40; no world with 5 or more of 8 folds beaten; median r over the 24 fold-fits
     below 0.025.

usage: python -E -s audit/harness_b2.py data_derived/bezrukov2023 results/harness_b2 [worlds]
"""
import json
import os
import sys
import time
import zlib

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from p4.dataset import build_groups  # noqa: E402
from p4.decide import cluster_level, rule  # noqa: E402
from p4.physics import Branch, fit_scale, fit_scale_metric, rh50, simulate_b0  # noqa: E402
from p4.run_study import b2_E, folds, seg_dw, seg_ids, seg_E, sub  # noqa: E402
from p4.segments import DT_MIN  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")
PRIMARY8 = ["ROS-037", "ROS-039", "ROS-040", "MOF-303", "MIL-160", "CAU-10", "Al-fumarate", "Syloid"]
F_SYN = 0.003
BETA = 1.5
SD_B = {"27C": 0.089, "60C": 0.300}          # as the L1 null world (section 10)
EPS = (0.001, 0.452, 0.000, 0.007, -0.005, -0.036, 0.038, 0.060, -0.011, 0.006, 0.059, -0.037,
       -0.038, 0.012, -0.007, 0.023, -0.024, 0.221)
OFFSET_MAX_WT = 3.128
NOISE_SD, NOISE_PHI = 0.01, 0.9


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


def null_draw(s, T, seed):
    rng = np.random.default_rng([2000 + seed, zlib.crc32(f"{s}|{T}".encode("utf-8"))])
    b = float(rng.normal(0, SD_B[T]))
    eps = float(rng.choice(np.abs(EPS))) * (1.0 if rng.random() < 0.5 else -1.0)
    return b, eps


def synthesise(real, k_true, world):
    per = {(g["sorbent"], g["temp"]): rh50(g["ads"]) for g in real if g["sorbent"] in PRIMARY8}
    mean50 = {T: float(np.mean([v for (s, t), v in per.items() if t == T])) for T in ("27C", "60C")}
    seed = int(world[1:]) if world.startswith("S") else 1
    rng = np.random.default_rng(seed + 10)
    out, info = [], {}
    for g in real:
        T, ads = g["temp"], g["ads"]
        if world == "K":
            lf, eps = BETA * (rh50(ads) - mean50[T]) / 30.0, 0.0
        elif world.startswith("S"):
            lf, eps = null_draw(g["sorbent"], T, seed)
            w30 = float(ads.w_of_rh(30.0))
            if abs(eps) * w30 > OFFSET_MAX_WT:
                eps = float(np.sign(eps)) * OFFSET_MAX_WT / w30
        else:
            lf, eps = 0.0, 0.0
        info[f"{g['sorbent']}|{T}"] = {"log_factor": lf, "eps": eps}
        truth_ads = Branch.from_points(ads.rh, ads.w * (1.0 + eps)) if eps else ads
        f = np.exp(lf)
        w = simulate_b0(g["rh"], g["w"][:, 0], f * k_true[(T, "ads")] / g["m"], f * k_true[(T, "des")] / g["m"],
                        truth_ads, None, dt=DT_MIN)
        w = np.where(np.isfinite(g["w"]), w, np.nan)
        w = w + np.nan_to_num(ar1(rng, w.shape)) * np.isfinite(w)
        out.append({**g, "w": w})
    return out, info, mean50


def judge(te, E_b2, E_b0):
    b0, m, D, mat, dd = cluster_level(seg_ids(te), E_b0, E_b2, seg_dw(te), with_d=True)
    per = {str(s): rule(b0[mat == s], m[mat == s], F_SYN, D[mat == s], dd[mat == s]) for s in sorted(set(mat))}
    ok = bool(per) and all(v[0] for v in per.values())
    r = min(v[1]["r"] for v in per.values())
    return ok, float(r), {s: v[1] for s, v in per.items()}


def main():
    root, out = sys.argv[1], sys.argv[2]
    worlds = sys.argv[3].split(",") if len(sys.argv) > 3 else ["N", "K", "S0", "S1", "S2"]
    os.makedirs(out, exist_ok=True)
    path = os.path.join(out, "harness_b2.json")
    res = json.load(open(path)) if os.path.exists(path) else {"worlds": {}}
    log = lambda s: print(f"{time.strftime('%H:%M:%S')} {s}", flush=True)
    real = [g for g in build_groups(root) if g["sorbent"] in PRIMARY8 or g["sorbent"].endswith("_composite")]
    k_true = fit_k2([g for g in real if g["sorbent"] in PRIMARY8], metric=False)
    res["k_true"] = {f"{a}|{b}": v for (a, b), v in k_true.items()}
    loso = [f for f in folds() if f[0].startswith("LOSO")]
    for world in worlds:
        syn, info, mean50 = synthesise(real, k_true, world)
        W = res["worlds"].setdefault(world, {"truth": info, "mean_rh50": mean50, "folds": {}})
        for name, held in loso:
            if name in W["folds"]:
                continue
            t0 = time.time()
            tr = [g for g in syn if g["sorbent"] not in held]
            te = [g for g in syn if g["sorbent"] in held]
            k_fit = fit_k2(tr, metric=True)
            E_b0 = []
            for g in te:
                E_b0 += seg_E(simulate_b0(g["rh"], g["w"][:, 0], k_fit[(g["temp"], "ads")] / g["m"],
                                          k_fit[(g["temp"], "des")] / g["m"], g["ads"], None, dt=DT_MIN), g["w"])
            E_b2, ab = b2_E(tr, te)
            ok, r, per = judge(te, np.array(E_b2), np.array(E_b0))
            W["folds"][name] = {"beats": ok, "r": r, "per_material": per, "b2_ab": ab,
                                "E_B0": float(np.nanmedian(E_b0)), "E_B2": float(np.nanmedian(E_b2)),
                                "s": time.time() - t0}
            log(f"{world} {name}: beats={ok} r={r:.3f} E_B0={np.nanmedian(E_b0):.4f} E_B2={np.nanmedian(E_b2):.4f} "
                f"b={ {k: round(v[1], 3) for k, v in ab.items()} } ({time.time() - t0:.0f}s)")
            json.dump(res, open(path, "w"), indent=1, default=float)
    evaluate(res)
    json.dump(res, open(path, "w"), indent=1, default=float)


def cp_upper(k, n, a=0.05):
    from scipy.stats import beta
    return 1.0 if k >= n else float(beta.ppf(1 - a, k + 1, n - k))


def evaluate(res):
    Wd = res["worlds"]
    need = {"N", "K", "S0", "S1", "S2"}
    if not need <= set(Wd) or any(len(Wd[w]["folds"]) < 8 for w in need):
        print("incomplete: criteria not evaluated", flush=True)
        return
    c1 = not any(f["beats"] for f in Wd["N"]["folds"].values())
    kb = sum(f["beats"] for f in Wd["K"]["folds"].values())
    berr = float(np.median([abs(ab[1] / BETA - 1) for f in Wd["K"]["folds"].values() for ab in f["b2_ab"].values()]))
    c2 = kb >= 7 and berr <= 0.25
    sb = [sum(f["beats"] for f in Wd[w]["folds"].values()) for w in ("S0", "S1", "S2")]
    rs = [f["r"] for w in ("S0", "S1", "S2") for f in Wd[w]["folds"].values()]
    ub = cp_upper(sum(sb), 24)
    c3 = ub <= 0.40 and max(sb) <= 4 and float(np.median(rs)) < 0.025
    res["summary"] = {"N_beats": sum(f["beats"] for f in Wd["N"]["folds"].values()), "K_beats": kb,
                      "K_median_rel_err_b": berr, "S_beats_per_world": sb, "S_cp95_upper": ub,
                      "S_median_r": float(np.median(rs)), "S_r_q90": float(np.quantile(rs, 0.9))}
    res["pass"] = {"1_no_beat_in_N": c1, "2_K_found": c2, "3_null_S": c3}
    print(f"SUMMARY {res['summary']}\nPASS criteria: {res['pass']}", flush=True)


if __name__ == "__main__":
    main()
