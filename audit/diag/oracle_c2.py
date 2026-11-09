"""Diagnostic (after harness round 6): does the true C2 rate law, run through L1's own evaluation
path (p4.train.evaluate: make_ctx, RK4 with the no-overshoot limiter), reproduce the synthetic
data of a held-out sorbent? It should, to the noise level (sd 0.01 wt%). If not, the pipeline,
not L1, is what fails.  usage: python -I audit/diag/oracle_c2.py data_derived/bezrukov2023 C2"""
import os, sys
import numpy as np
import torch
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(HERE))); sys.path.insert(0, os.path.dirname(HERE))
from p4.dataset import build_groups
from p4.train import evaluate, isotherms_by_material
from p4.run_study import seg_ids
from synthetic_harness import PRIMARY8, Truth, b0_E, fit_k2, synthesise

world = {"C": True, "C2": "C2", "N": False}[sys.argv[2]]
real = [g for g in build_groups(sys.argv[1]) if g["sorbent"] in PRIMARY8]
k_true = fit_k2(real)
syn = synthesise(real, k_true, world, seed=1)
iso = isotherms_by_material(syn)
for held in ("MOF-303", "ROS-039"):
    te = [g for g in syn if g["sorbent"] == held]
    ids = seg_ids(te)
    for kind, lab in (("L1", "limiter on"), ("L2", "limiter off")):
        E = evaluate(Truth(world), kind, te, k_true, iso)["E"]
        print(held, "truth via evaluate,", lab, "median E", round(float(np.nanmedian(E)), 5), "max", round(float(np.nanmax(E)), 4), flush=True)
        if kind == "L1":
            for s, e in sorted(zip(ids, E), key=lambda x: -x[1])[:6]:
                print("    worst", s[-50:], round(float(e), 4))
    print(held, "B0 with k_true median E", round(float(np.nanmedian(b0_E(te, k_true))), 5), flush=True)
