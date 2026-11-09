"""Diagnostic (after harness round 6): L1 fitted to the exact C2 rates (t63 weight). Compare its
learned log-factor with the needed one, log(k_true/k_fit) + 0.8 tanh(d/15), at the synthetic
states, binned by direction and d, in sample (training sorbents) and on held-out ROS-039.
usage: python -I audit/diag/factor_c2.py data_derived/bezrukov2023"""
import os, sys
os.environ["DIAG_WORLD"] = "C2"
import numpy as np
import torch
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(HERE))); sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
from p4.dataset import build_groups
from p4.train import isotherms_by_material, make_ctx
from synthetic_harness import PRIMARY8, fit_k2, synthesise
from l1_stageA_diag import stage_a

held = "ROS-039"
real = [g for g in build_groups(sys.argv[1]) if g["sorbent"] in PRIMARY8]
k_true = fit_k2(real)
syn = synthesise(real, k_true, "C2", seed=1)
iso = isotherms_by_material(syn)
tr = [g for g in syn if g["sorbent"] not in (held, "Syloid")]
te = [g for g in syn if g["sorbent"] == held]
k = fit_k2([g for g in syn if g["sorbent"] != held], metric=True)
model = stage_a(tr, k, iso, "t63", 2000, exact_k=k_true)

def table(groups, label):
    rows = []
    for g in groups:
        ok = np.isfinite(g["w"]) & np.isfinite(g["rh"])
        sg = np.repeat(np.arange(len(g["m"]))[:, None], g["w"].shape[1], 1)[ok]
        ctx = make_ctx(g, k, iso, sg)
        w = torch.as_tensor(g["w"][ok]); r = torch.as_tensor(g["rh"][ok])
        with torch.no_grad():
            rb = ctx["ads"].rh_of_w(w); d = r - rb
            got = model.rate(w, r, ctx) / (torch.where(d > 0, ctx["k_ads"], ctx["k_des"]) * d)
            kt = torch.where(d > 0, torch.as_tensor(k_true[(g["temp"], "ads")] / k[(g["temp"], "ads")]),
                             torch.as_tensor(k_true[(g["temp"], "des")] / k[(g["temp"], "des")]))
            need = torch.log(kt) + 0.8 * torch.tanh(d / 15)
        rows.append(np.c_[d.numpy(), torch.log(got).numpy(), need.numpy(), np.full(len(d), g["sorbent"] == held)])
    a = np.vstack(rows)
    print(f"== {label}  n={len(a)}")
    for lo, hi in ((-70, -15), (-15, -5), (-5, -1), (-1, -0.1), (0.1, 1), (1, 5), (5, 15), (15, 70)):
        s = (a[:, 0] >= lo) & (a[:, 0] < hi)
        if s.sum():
            print(f"  d in [{lo:5},{hi:5}): n {int(s.sum()):7d}  learned {np.median(a[s,1]):+.3f}  needed {np.median(a[s,2]):+.3f}  "
                  f"|err| median {np.median(np.abs(a[s,1]-a[s,2])):.3f}")

table(tr, "training sorbents (in sample)")
table(te, "held-out ROS-039")
z03 = []
for g in te:
    for i in range(len(g["m"])):
        rh = g["rh"][i][np.isfinite(g["rh"][i])]
        print("  ROS-039 seg", i, g["temp"], "rh", round(float(rh[0]),1), "->", round(float(rh[-1]),1), "w", round(float(np.nanmin(g["w"][i])),2), "->", round(float(np.nanmax(g["w"][i])),2)) if i < 0 else None
