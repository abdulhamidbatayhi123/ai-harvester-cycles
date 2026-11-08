"""Pre-freeze reproduction check (PREREG_P4 section 9): fit Bezrukov's B0 in-sample.

For every (sorbent, temperature) and direction, fit k'' on that material alone (the published
per-material fit), and also one k'' pooled over all eight sorbents (the "material independent"
claim). Reports k'' per material, its spread across materials, and the in-sample median
normalised error E of each. In-sample by design; no learned model, no held-out evaluation.

Also fits the oracle by the scored metric (median E, review finding F1), E_own_metric.

usage: python -I audit/reproduce_b0.py data_derived/bezrukov2023 results/prefreeze [R1|R2]
"""
import json, os, sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from p4.dataset import build_groups  # noqa: E402
from p4.physics import fit_scale, fit_scale_metric, simulate_b0  # noqa: E402
from p4.segments import DT_MIN, normalised_rms  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")
PRIMARY8 = ["ROS-037", "ROS-039", "ROS-040", "MOF-303", "MIL-160", "CAU-10", "Al-fumarate", "Syloid"]


def sub(g, direction):
    sel = g["dir"] == (1 if direction == "ads" else -1)
    return {"rh": g["rh"][sel], "w": g["w"][sel], "m": g["m"][sel], "ads": g["ads"], "des": None}


def median_E(g, direction, k):
    s = sub(g, direction)
    if len(s["m"]) == 0:
        return float("nan")
    kk = k / s["m"]
    ka, kd = (kk, 0.0) if direction == "ads" else (0.0, kk)
    pred = simulate_b0(s["rh"], s["w"][:, 0], ka, kd, s["ads"], None, dt=DT_MIN)
    E = []
    for p, w in zip(pred, s["w"]):
        n = int(np.isfinite(w).sum())
        E.append(normalised_rms(p[:n], w[:n]))
    return float(np.nanmedian(E))


def main():
    rule = sys.argv[3] if len(sys.argv) > 3 else "R2"
    groups = build_groups(sys.argv[1], rule=rule)
    out = {"per_material": [], "pooled": {}}
    for T in ("27C", "60C"):
        for d in ("ads", "des"):
            gs = [g for g in groups if g["temp"] == T and g["sorbent"] in PRIMARY8]
            pooled = fit_scale([sub(g, d) for g in gs], simulate_b0, d, dt=DT_MIN)
            # pooled k'' by the scored metric, as the confirmatory comparator is fitted (section 5)
            pooled_m = fit_scale_metric([sub(g, d) for g in gs], simulate_b0, d, dt=DT_MIN, k_start=pooled)
            ks = []
            for g in groups:
                if g["temp"] != T:
                    continue
                s = sub(g, d)
                if len(s["m"]) == 0:
                    continue
                k = fit_scale([s], simulate_b0, d, dt=DT_MIN)
                km = fit_scale_metric([s], simulate_b0, d, dt=DT_MIN, k_start=k)
                rec = {"sorbent": g["sorbent"], "temp": T, "dir": d, "n_seg": int(len(s["m"])),
                       "k2_own": k, "E_own": median_E(g, d, k), "E_pooled": median_E(g, d, pooled),
                       "k2_own_metric": km, "E_own_metric": median_E(g, d, km),
                       "E_pooled_metric": median_E(g, d, pooled_m)}
                out["per_material"].append(rec)
                if g["sorbent"] in PRIMARY8:
                    ks.append(k)
                print(f"{T} {d} {g['sorbent']:18s} n={rec['n_seg']:3d} k''={k:8.4f}  E_own={rec['E_own']:.3f}  E_pooled={rec['E_pooled']:.3f}  E_own_metric={rec['E_own_metric']:.3f}", flush=True)
            ks = np.array(ks)
            out["pooled"][f"{T}|{d}"] = {"k2_pooled": pooled, "k2_pooled_metric": pooled_m, "k2_cv_across_8": float(ks.std() / ks.mean()),
                                         "k2_cv_across_8_sample_sd": float(ks.std(ddof=1) / ks.mean()),
                                         "k2_min": float(ks.min()), "k2_max": float(ks.max())}
            print(f"== {T} {d}: pooled k''={pooled:.4f}; across 8 sorbents CV={ks.std()/ks.mean():.2f}, range {ks.min():.4f}-{ks.max():.4f}", flush=True)
    os.makedirs(sys.argv[2], exist_ok=True)
    out["rule"] = rule
    name = "reproduce_b0.json" if rule == "R2" else f"reproduce_b0_{rule}.json"
    json.dump(out, open(os.path.join(sys.argv[2], name), "w"), indent=1)


if __name__ == "__main__":
    main()
