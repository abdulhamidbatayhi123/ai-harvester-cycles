"""Synthetic harness test of PREREG_P4 section 10 (must pass before the freeze).

Synthetic uptake is generated on the REAL forcing and REAL isotherms of the primary set, from
a known truth, and the full fold pipeline is run on it:

  case N (no correction): truth = B0 with the pooled k'' of the real data.
  case C (correction):    truth = B0 x exp(-0.7 w / w30), a material-independent slow-down
                          near saturation that a model given only the isotherm can learn.

Gaussian noise of 0.01 wt% is added. Held-out folds for the test: MOF-303 and ROS-039.
Pass criteria (section 10):
  1. case N: B0 refitted on the training sorbents recovers the true k'' within 2 %;
  2. case C: L1 "beats" B0 on both held-out sorbents by the section 7 rule;
  3. case N: neither L1 nor L2 "beats" B0 on either held-out sorbent (false-positive check).

usage: python -I audit/synthetic_harness.py data_derived/bezrukov2023 results/harness
"""
import json, os, sys, time

import numpy as np
import torch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from p4.dataset import build_groups  # noqa: E402
from p4.learned import TorchBranch, integrate  # noqa: E402
from p4.physics import fit_scale, simulate_b0  # noqa: E402
from p4.segments import DT_MIN, normalised_rms  # noqa: E402
from p4.train import beats, evaluate, isotherms_by_material, train_two_stage  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")
torch.set_num_threads(2)
PRIMARY8 = ["ROS-037", "ROS-039", "ROS-040", "MOF-303", "MIL-160", "CAU-10", "Al-fumarate", "Syloid"]
HELD = ["MOF-303", "ROS-039"]
VAL = "Syloid"
F_SYN = 0.003          # the synthetic noise floor stands in for F in the beat rule


class Truth(torch.nn.Module):
    def __init__(self, corrected):
        super().__init__()
        self.corrected = corrected

    def rate(self, w, r, ctx):
        d = r - ctx["ads"].rh_of_w(w)
        k = torch.where(d > 0, ctx["k_ads"], ctx["k_des"])
        f = torch.exp(-0.7 * w / ctx["w30"]) if self.corrected else torch.ones_like(w)
        return k * d * f

    def equilibrium(self, r, ctx):
        e = ctx["ads"].w_of_rh(r)
        return e, e


def synthesise(groups, k2, corrected, seed):
    rng = np.random.default_rng(seed)
    truth = Truth(corrected)
    out = []
    for g in groups:
        m = torch.as_tensor(g["m"])
        ctx = {"ads": TorchBranch(g["ads"].rh, g["ads"].w), "w30": torch.tensor(float(g["ads"].w_of_rh(30.0))),
               "k_ads": k2[(g["temp"], "ads")] / m, "k_des": k2[(g["temp"], "des")] / m}
        with torch.no_grad():
            w = integrate(truth, torch.as_tensor(g["rh"]), torch.as_tensor(g["w"][:, 0]), ctx, dt=DT_MIN).numpy()
        w = w + rng.normal(0, 0.01, w.shape) * np.isfinite(w)
        out.append({**g, "w": w})
    return out


def b0_E(groups, k2):
    E = []
    for g in groups:
        kk_a, kk_d = k2[(g["temp"], "ads")] / g["m"], k2[(g["temp"], "des")] / g["m"]
        pred = simulate_b0(g["rh"], g["w"][:, 0], kk_a, kk_d, g["ads"], None, dt=DT_MIN)
        for p, w in zip(pred, g["w"]):
            n = int(np.isfinite(w).sum())
            E.append(normalised_rms(p[:n], w[:n]))
    return np.array(E)


def fit_k2(groups):
    k2 = {}
    for T in ("27C", "60C"):
        for d in ("ads", "des"):
            sel = []
            for g in groups:
                if g["temp"] != T:
                    continue
                s = g["dir"] == (1 if d == "ads" else -1)
                sel.append({"rh": g["rh"][s], "w": g["w"][s], "m": g["m"][s], "ads": g["ads"], "des": None})
            k2[(T, d)] = fit_scale(sel, simulate_b0, d, dt=DT_MIN)
    return k2


def main():
    root, out = sys.argv[1], sys.argv[2]
    os.makedirs(out, exist_ok=True)
    log = lambda s: print(f"{time.strftime('%H:%M:%S')} {s}", flush=True)
    real = [g for g in build_groups(root) if g["sorbent"] in PRIMARY8]
    k_true = fit_k2(real)                     # the truth's rate constants
    log(f"k_true {k_true}")
    res = {"k_true": {f"{a}|{b}": v for (a, b), v in k_true.items()}, "cases": {}}
    for case, corrected in (("N", False), ("C", True)):
        syn = synthesise(real, k_true, corrected, seed=1)
        iso = isotherms_by_material(syn)
        for held in HELD:
            tr = [g for g in syn if g["sorbent"] not in (held, VAL)]
            va = [g for g in syn if g["sorbent"] == VAL]
            te = [g for g in syn if g["sorbent"] == held]
            k_fit = fit_k2([g for g in syn if g["sorbent"] != held])
            rec = {"k_fit": {f"{a}|{b}": v for (a, b), v in k_fit.items()},
                   "k_rel_err": {f"{a}|{b}": k_fit[(a, b)] / k_true[(a, b)] - 1 for (a, b) in k_true}}
            E_b0 = b0_E(te, k_fit)
            for kind in ("L1", "L2"):
                t0 = time.time()
                model, best = train_two_stage(kind, tr, va, k_fit, iso,
                                              log=lambda s: log(f"{case} {held} {kind} {s}"))
                E_m = evaluate(model, kind, te, k_fit, iso)["E"]
                ok, info = beats(E_m, E_b0, F_SYN)
                rec[kind] = {"beats_B0": ok, **info, "train_s": time.time() - t0}
                log(f"case {case} held {held} {kind}: beats={ok} {info} ({time.time() - t0:.0f}s)")
            res["cases"][f"{case}|{held}"] = rec
            json.dump(res, open(os.path.join(out, "harness.json"), "w"), indent=1)
    c1 = all(abs(v) < 0.02 for h in HELD for v in res["cases"][f"N|{h}"]["k_rel_err"].values())
    c2 = all(res["cases"][f"C|{h}"]["L1"]["beats_B0"] for h in HELD)
    c3 = not any(res["cases"][f"N|{h}"][k]["beats_B0"] for h in HELD for k in ("L1", "L2"))
    res["pass"] = {"1_k_recovered": c1, "2_L1_finds_correction": c2, "3_no_false_positive": c3}
    json.dump(res, open(os.path.join(out, "harness.json"), "w"), indent=1)
    log(f"PASS criteria: {res['pass']}")


if __name__ == "__main__":
    main()
