"""Diagnostic (harness round 4, L2 failure): can L2 represent and transfer the world-N truth?

World N truth = B0 with pooled k''. L2 is fitted by regression to the EXACT truth rate at the
synthetic states of the training sorbents (no noise, no rollout), then evaluated open loop on the
held-out sorbent. Also reports L2's rate at equilibrium on the held-out sorbent, where the truth is 0.

usage: python -I audit/diag/l2_transfer_diag.py data_derived/bezrukov2023 results/diag_l2.json [variant]
variant: base (current L2 inputs) | drive (adds the driving forces r - RH_bed on both branches)
"""
import json, os, sys, time

import numpy as np
import torch

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.dirname(HERE))
from p4.dataset import build_groups  # noqa: E402
from p4.learned import L2, L2_SCALE, mlp  # noqa: E402
from p4.train import evaluate, isotherms_by_material, make_ctx  # noqa: E402
from synthetic_harness import PRIMARY8, Truth, b0_E, fit_k2, synthesise  # noqa: E402

torch.set_num_threads(2)


class L2drive(L2):
    def __init__(self, width=32, depth=2):
        super().__init__(width, depth)
        self.f = mlp(11, width, depth)

    def rate(self, w, r, ctx):
        ads, des, w30 = ctx["ads"], ctx.get("des", ctx["ads"]), ctx["w30"]
        ra, rd = ads.rh_of_w(w), des.rh_of_w(w)
        z = torch.stack([w / w30, r / 100, ads.w_of_rh(r) / w30, des.w_of_rh(r) / w30,
                         ra / 100, rd / 100, ads.slope_at_w(w) * 10 / w30,
                         (ctx["temp"] - 27.0) / 33.0, 10.0 / ctx["m"], (r - ra) / 100, (r - rd) / 100], -1)
        return (L2_SCALE / ctx["m"]) * self.f(z).squeeze(-1)


class L2anchor(L2):
    """f(z(w, r)) - f(z(w_eq(r), r)): zero rate exactly on the adsorption isotherm, nothing else imposed."""

    def feats(self, w, r, ctx):
        ads, des, w30 = ctx["ads"], ctx.get("des", ctx["ads"]), ctx["w30"]
        return torch.stack([w / w30, r / 100, ads.w_of_rh(r) / w30, des.w_of_rh(r) / w30,
                            ads.rh_of_w(w) / 100, des.rh_of_w(w) / 100, ads.slope_at_w(w) * 10 / w30,
                            (ctx["temp"] - 27.0) / 33.0, 10.0 / ctx["m"]], -1)

    def rate(self, w, r, ctx):
        w_eq = ctx["ads"].w_of_rh(r)
        f = self.f(self.feats(w, r, ctx)) - self.f(self.feats(w_eq, r, ctx))
        return (L2_SCALE / ctx["m"]) * f.squeeze(-1)


def main():
    root, out = sys.argv[1], sys.argv[2]
    variant = sys.argv[3] if len(sys.argv) > 3 else "base"
    real = [g for g in build_groups(root) if g["sorbent"] in PRIMARY8]
    k = fit_k2(real)
    syn = synthesise(real, k, corrected=False, seed=1)
    iso = isotherms_by_material(syn)
    res = {}
    for held in ("MOF-303", "ROS-039"):
        tr = [g for g in syn if g["sorbent"] not in (held, "Syloid")]
        te = [g for g in syn if g["sorbent"] == held]
        truth = Truth(False)
        pts = []
        for g in tr:
            ok = np.isfinite(g["w"]) & np.isfinite(g["rh"])
            seg = np.repeat(np.arange(len(g["m"]))[:, None], g["w"].shape[1], 1)[ok]
            ctx = make_ctx(g, k, iso, seg)
            with torch.no_grad():
                r_true = truth.rate(torch.as_tensor(g["w"][ok]), torch.as_tensor(g["rh"][ok]), ctx).numpy()
            dw = (np.nanmax(g["w"], 1) - np.nanmin(g["w"], 1))[seg]
            pts.append((g, seg, g["w"][ok], g["rh"][ok], r_true, dw))
        torch.manual_seed(0)
        rng = np.random.default_rng(0)
        model = {"drive": L2drive, "anchor": L2anchor}.get(variant, L2)(width=32, depth=2)
        opt = torch.optim.Adam(model.parameters(), lr=1e-3, weight_decay=1e-4)
        t0 = time.time()
        for step in range(1, 4001):
            g, seg, w, rh, r, dw = pts[rng.integers(len(pts))]
            j = rng.integers(0, len(w), size=min(4096, len(w)))
            ctx = make_ctx(g, k, iso, seg[j])
            pred = model.rate(torch.as_tensor(w[j]), torch.as_tensor(rh[j]), ctx)
            loss = ((pred - torch.as_tensor(r[j])) / torch.as_tensor(dw[j]).clamp_min(1e-3)).pow(2).mean()
            opt.zero_grad(); loss.backward(); opt.step()
        # rate at equilibrium on the held-out sorbent: w on the isotherm at the segment's final RH
        eq = []
        for g in te:
            fin = [row[np.isfinite(row)][-1] for row in g["rh"]]
            w_eq = np.array([float(g["ads"].w_of_rh(x)) for x in fin])
            ctx = make_ctx(g, k, iso)
            with torch.no_grad():
                eq += model.rate(torch.as_tensor(w_eq), torch.as_tensor(np.array(fin)), ctx).abs().numpy().tolist()
        E_m = evaluate(model, "L2", te, k, iso)["E"]
        E_b = b0_E(te, k)
        res[held] = {"variant": variant, "final_loss": float(loss.detach()), "median_E_L2": float(np.nanmedian(E_m)),
                     "median_E_B0": float(np.nanmedian(E_b)), "median_abs_rate_at_eq_wtpct_min": float(np.median(eq)),
                     "s": time.time() - t0}
        print(held, res[held], flush=True)
    json.dump(res, open(out, "w"), indent=1)


if __name__ == "__main__":
    main()
