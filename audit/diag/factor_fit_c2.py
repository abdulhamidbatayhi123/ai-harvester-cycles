"""Diagnostic (after harness round 6): can L1 represent and transfer the world-C2 correction?
Fit L1's log-factor 2 tanh g(z) directly to the needed log(k_true/k_fit) + 0.8 tanh(d/15) at the
synthetic states of the training sorbents (possible only in a synthetic world), then score open
loop on the held-out sorbent with the section 7 rule.  usage: python -I audit/diag/factor_fit_c2.py data_derived/bezrukov2023"""
import os, sys
os.environ["DIAG_WORLD"] = "C2"
import numpy as np
import torch
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(HERE))); sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
from p4.dataset import build_groups
from p4.learned import L1
from p4.train import evaluate, isotherms_by_material, make_ctx
from synthetic_harness import PRIMARY8, b0_E, beats, fit_k2, synthesise
from p4.learned import mlp
torch.set_num_threads(2)
DIN = os.environ.get("FF_DIN", "0") == "1"           # add d / 30 as an 8th input
STEPS = int(os.environ.get("FF_STEPS", "3000"))
WIDTH = int(os.environ.get("FF_WIDTH", "16"))


class L1d(L1):
    def __init__(self, width=16, depth=2):
        super().__init__(width, depth)
        self.g = mlp(8 if DIN else 7, width, depth)

    def feats(self, w, r, ctx):
        ads, w30 = ctx["ads"], ctx["w30"]
        rb = ads.rh_of_w(w); d = r - rb
        z = [w / w30, r / 100, rb / 100, ads.slope_at_w(w) * 10 / w30, torch.sign(d),
             (ctx["temp"] - 27.0) / 33.0, 10.0 / ctx["m"]] + ([d / 30] if DIN else [])
        return torch.stack(z, -1), d

    def rate(self, w, r, ctx):
        z, d = self.feats(w, r, ctx)
        k = torch.where(d > 0, ctx["k_ads"], ctx["k_des"])
        return k * d * torch.exp(2 * torch.tanh(self.g(z).squeeze(-1)))

real = [g for g in build_groups(sys.argv[1]) if g["sorbent"] in PRIMARY8]
k_true = fit_k2(real)
syn = synthesise(real, k_true, "C2", seed=1)
iso = isotherms_by_material(syn)
for held in ("MOF-303", "ROS-039"):
    tr = [g for g in syn if g["sorbent"] not in (held, "Syloid")]
    te = [g for g in syn if g["sorbent"] == held]
    k = fit_k2([g for g in syn if g["sorbent"] != held], metric=True)
    pts = []
    for g in tr:
        ok = np.isfinite(g["w"]) & np.isfinite(g["rh"])
        sg = np.repeat(np.arange(len(g["m"]))[:, None], g["w"].shape[1], 1)[ok]
        pts.append((g, sg, g["w"][ok], g["rh"][ok]))
    torch.manual_seed(0); rng = np.random.default_rng(0)
    model = L1d(width=WIDTH, depth=2)
    opt = torch.optim.Adam(model.parameters(), lr=1e-3, weight_decay=1e-4)
    for step in range(STEPS):
        g, sg, w, r = pts[rng.integers(len(pts))]
        j = rng.integers(0, len(w), size=min(4096, len(w)))
        ctx = make_ctx(g, k, iso, sg[j])
        wt, rt = torch.as_tensor(w[j]), torch.as_tensor(r[j])
        z, d = model.feats(wt, rt, ctx)
        kr = torch.where(d > 0, torch.as_tensor(k_true[(g["temp"], "ads")] / k[(g["temp"], "ads")]),
                         torch.as_tensor(k_true[(g["temp"], "des")] / k[(g["temp"], "des")]))
        need = torch.log(kr) + 0.8 * torch.tanh(d / 15)
        loss = (2 * torch.tanh(model.g(z).squeeze(-1)) - need).pow(2).mean()
        opt.zero_grad(); loss.backward(); opt.step()
        if step % 1000 == 999:
            print(held, "step", step + 1, "log-factor mse", round(loss.item(), 5), flush=True)
    E_b = b0_E(te, k)
    E_m = evaluate(model, "L1", te, k, iso)["E"]
    ok, info = beats(te, E_m, E_b, 0.003)
    print(held, "factor-fit L1: beats", ok, "E_B0", round(info["E_B0"], 4), "E_L1", round(info["E_model"], 4), "p", info["p_signflip"], flush=True)
