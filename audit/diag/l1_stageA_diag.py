"""Diagnostic (harness round 4, world C): which stage-A loss lets L1 learn the injected
correction against a metric-fitted B0? Stage A only (no rollout), on the synthetic measured rates,
then open loop on the held-out sorbent, judged by the section 7 rule (audit/synthetic_harness.beats).

Variants of the per-point weight in the squared rate error:
  dw     current: 1 / |segment change|
  rel    relative to B0's own rate: 1 / (|rate_B0| + eps), eps = 0.05 wt%/min
  dw6k   current weight, 6000 steps instead of 2000

usage: python -I audit/diag/l1_stageA_diag.py data_derived/bezrukov2023 results/diag_l1.json
"""
import json, os, sys, time

import numpy as np
import torch

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.dirname(HERE))
from p4.dataset import build_groups  # noqa: E402
from p4.learned import L1  # noqa: E402
from p4.physics import simulate_b0  # noqa: E402
from p4.train import evaluate, isotherms_by_material, make_ctx, measured_rates  # noqa: E402
from synthetic_harness import PRIMARY8, Truth, b0_E, beats, fit_k2, synthesise  # noqa: E402

torch.set_num_threads(2)
EPS = 0.05
WORLD = {"C": True, "C2": "C2"}[os.environ.get("DIAG_WORLD", "C")]     # world C2 added after round 6
TAU_CAP = float(os.environ.get("DIAG_TAU_CAP", "10"))   # cap on tau, in units of the segment's t63
MASK = [int(i) for i in os.environ.get("DIAG_MASK", "").split(",") if i]   # L1 input columns set to 0


class L1m(L1):
    """L1 with some inputs zeroed (diagnostic): 0 w/w30, 1 RH, 2 RH_bed, 3 slope, 4 sign d, 5 T, 6 1/m, 7 d/30."""

    def rate(self, w, r, ctx):
        ads, w30 = ctx["ads"], ctx["w30"]
        r_bed = ads.rh_of_w(w)
        d = r - r_bed
        k = torch.where(d > 0, ctx["k_ads"], ctx["k_des"])
        z = torch.stack([w / w30, r / 100, r_bed / 100, ads.slope_at_w(w) * 10 / w30,
                         torch.sign(d), (ctx["temp"] - 27.0) / 33.0, 10.0 / ctx["m"], d / 30.0], -1)
        if MASK:
            z = z.clone(); z[..., MASK] = 0.0
        return k * d * torch.exp(2 * torch.tanh(self.g(z).squeeze(-1)))


def stage_a(tr, k, iso, weight, steps, seed=0, exact_k=None, half=3, smooth_rh=False):
    torch.manual_seed(seed)
    rng = np.random.default_rng(seed)
    model = L1m(width=16, depth=2)
    opt = torch.optim.Adam(model.parameters(), lr=1e-3, weight_decay=1e-4)
    pts = []
    for g in tr:
        r = measured_rates(g["w"], half=half)
        rh_in = g["rh"]
        if smooth_rh:                 # RH averaged over the same window as the rate (errors in variables)
            rh_in = np.full_like(g["rh"], np.nan)
            cs = np.nancumsum(np.nan_to_num(g["rh"]), axis=1)
            rh_in[:, half:-half] = (cs[:, 2 * half:] - np.pad(cs, ((0, 0), (1, 0)))[:, :-2 * half - 1]) / (2 * half + 1)
        ok = np.isfinite(r) & np.isfinite(rh_in)
        if exact_k is not None:      # exact truth rate at the synthetic states (no finite difference, no noise)
            sg = np.repeat(np.arange(len(g["m"]))[:, None], g["w"].shape[1], 1)[ok]
            with torch.no_grad():
                r = r.copy()
                r[ok] = Truth(WORLD).rate(torch.as_tensor(g["w"][ok]), torch.as_tensor(g["rh"][ok]),
                                         make_ctx(g, exact_k, iso, sg)).numpy()
        seg = np.repeat(np.arange(len(g["m"]))[:, None], g["w"].shape[1], 1)[ok]
        dw = (np.nanmax(g["w"], 1) - np.nanmin(g["w"], 1))[seg]
        ctx = make_ctx(g, k, iso, seg)
        d = torch.as_tensor(rh_in[ok]) - ctx["ads"].rh_of_w(torch.as_tensor(g["w"][ok]))
        rb = (torch.where(d > 0, ctx["k_ads"], ctx["k_des"]) * d).abs().numpy()
        if weight == "tau":        # rate error x B0's local relaxation time |w - w_eq(RH)| / |rate_B0|, / |dw|
            t63 = np.empty(len(g["m"]))
            for i, row in enumerate(g["w"]):
                row = row[np.isfinite(row)]
                ch = np.abs(row - row[0]); tot = abs(row[-1] - row[0])
                j = int(np.argmax(ch >= 0.63 * tot)) if tot > 0 else 1
                t63[i] = max(j, 1) * 0.1
            weq = ctx["ads"].w_of_rh(torch.as_tensor(rh_in[ok])).numpy()
            tau = np.abs(g["w"][ok] - weq) / np.maximum(rb, 1e-9)
            tau = np.clip(tau, 0.1, TAU_CAP * t63[seg])
            wt = tau / np.maximum(dw, 1e-3)
        elif weight == "t63":        # rate error x t63 / |dw|: the trajectory error it causes, in units of E
            t63 = np.empty(len(g["m"]))
            for i, row in enumerate(g["w"]):
                row = row[np.isfinite(row)]
                ch = np.abs(row - row[0]); tot = abs(row[-1] - row[0])
                j = int(np.argmax(ch >= 0.63 * tot)) if tot > 0 else 1
                t63[i] = max(j, 1) * 0.1
            wt = t63[seg] / np.maximum(dw, 1e-3)
        else:
            wt = 1.0 / np.maximum(dw, 1e-3) if weight == "dw" else 1.0 / (rb + EPS)
        pts.append((g, seg, g["w"][ok], rh_in[ok], r[ok], wt))
    for step in range(steps):
        g, seg, w, rh, r, wt = pts[rng.integers(len(pts))]
        j = rng.integers(0, len(w), size=min(4096, len(w)))
        ctx = make_ctx(g, k, iso, seg[j])
        pred = model.rate(torch.as_tensor(w[j]), torch.as_tensor(rh[j]), ctx)
        loss = ((pred - torch.as_tensor(r[j])) * torch.as_tensor(wt[j])).pow(2).mean()
        opt.zero_grad(); loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        opt.step()
    return model


def main():
    root, out = sys.argv[1], sys.argv[2]
    real = [g for g in build_groups(root) if g["sorbent"] in PRIMARY8]
    k_true = fit_k2(real)
    syn = synthesise(real, k_true, corrected=WORLD, seed=1)
    iso = isotherms_by_material(syn)
    res = {}
    for held in (sys.argv[4].split(",") if len(sys.argv) > 4 else ("MOF-303",)):
        tr = [g for g in syn if g["sorbent"] not in (held, "Syloid")]
        te = [g for g in syn if g["sorbent"] == held]
        k = fit_k2([g for g in syn if g["sorbent"] != held], metric=True)
        E_b = b0_E(te, k)
        variants = [(a, a, 2000, None) for a in ("dw",)] + [("exact", "dw", 2000, k_true), ("exact_rel", "rel", 2000, k_true), ("exact_t63", "t63", 2000, k_true), ("exact_tau", "tau", 2000, k_true)]
        variants += [(f"{wt}_h{h}", wt, 2000, None, h) for h in (6, 12, 25) for wt in ("dw", "rel")]
        variants = [v if len(v) == 5 else v + (3,) for v in variants]
        variants = [v + (False,) for v in variants] + [(f"{wt}_srh{h}", wt, 2000, None, h, True) for h in (3, 6) for wt in ("dw", "rel", "t63", "tau")]
        if len(sys.argv) > 3:
            variants = [v for v in variants if v[0] in sys.argv[3].split(",")]
        for name, weight, steps, ek, h, srh in variants:
            t0 = time.time()
            m = stage_a(tr, k, iso, weight, steps, exact_k=ek, half=h, smooth_rh=srh)
            E_m = evaluate(m, "L1", te, k, iso)["E"]
            ok, info = beats(te, E_m, E_b, 0.003)
            from p4.decide import cluster_level
            from p4.run_study import seg_dw, seg_ids
            ids = seg_ids(te)
            b0c, mc, Dc, _ = cluster_level(ids, E_b, E_m, seg_dw(te))
            keys = list(dict.fromkeys(s.split("#")[0] for s, a, b in zip(ids, E_b, E_m) if np.isfinite(a) and np.isfinite(b)))
            for kk, a, b, D in sorted(zip(keys, b0c, mc, Dc), key=lambda x: x[3]):
                print(f"   {kk:60s} E_B0 {a:.4f} E_L1 {b:.4f} D {D:+.4f}", flush=True)
            res[f"{held}|{name}"] = {"beats": ok, "E_B0": float(np.nanmedian(E_b)), "E_L1": float(np.nanmedian(E_m)),
                                     "p": info["p_signflip"], "median_gain": info["median_gain"], "s": time.time() - t0}
            print(held, name, res[f"{held}|{name}"], flush=True)
            json.dump(res, open(out, "w"), indent=1)


if __name__ == "__main__":
    main()
