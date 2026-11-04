"""Training and evaluation of L1 / L2 on groups from p4.dataset (PREREG_P4 section 5).

Context per group: the material's isotherms (torch branches), w30, the per-segment rate
constants of the fold's B0 (k''/m, fitted on the training sorbents only), temperature and dry
mass. The loss is the mean over segments of mean squared trajectory error divided by the
segment's squared change, the square of the pre-registered metric E.
"""
from __future__ import annotations

import time

import numpy as np
import torch

from p4.learned import L1, L2, TorchBranch, integrate, isotherm_encoding
from p4.segments import DT_MIN, normalised_rms

T_OF = {"27C": 27.0, "60C": 60.0}


def make_ctx(g, k2, iso_by_mat, idx=None):
    """k2: {(T, 'ads'|'des'): k''}. iso_by_mat: {sorbent: {(T, branch): Branch}}."""
    sel = slice(None) if idx is None else idx
    m = torch.as_tensor(g["m"][sel], dtype=torch.float64)
    ads = TorchBranch(g["ads"].rh, g["ads"].w)
    w30 = torch.tensor(float(g["ads"].w_of_rh(30.0)), dtype=torch.float64)
    T = T_OF[g["temp"]]
    tb = {(TT, b): TorchBranch(br.rh, br.w) for (TT, b), br in iso_by_mat[g["sorbent"]].items()}
    return {"ads": ads, "w30": w30, "m": m,
            "k_ads": k2[(g["temp"], "ads")] / m, "k_des": k2[(g["temp"], "des")] / m,
            "temp": torch.full_like(m, T), "enc": isotherm_encoding(tb, float(w30))}


def isotherms_by_material(groups):
    out = {}
    for g in groups:
        T = int(T_OF[g["temp"]])
        out.setdefault(g["sorbent"], {})[(T, "ads")] = g["ads"]
        out[g["sorbent"]][(T, "des")] = g["des"]
    for s, d in out.items():          # a material measured at one temperature only reuses it
        for T in (27, 60):
            for b in ("ads", "des"):
                d.setdefault((T, b), d.get((87 - T, b)))
    return out


def batch(g, idx, max_len):
    rh = torch.as_tensor(g["rh"][idx, :max_len])
    w = torch.as_tensor(g["w"][idx, :max_len])
    return rh, w


def seg_loss(pred, w):
    mask = torch.isfinite(w)
    n_last = mask.sum(1) - 1
    w0 = w[:, 0]
    w_end = w.gather(1, n_last.unsqueeze(1)).squeeze(1)
    dw2 = (w_end - w0).pow(2).clamp_min(1e-6)
    err = torch.where(mask, pred - torch.nan_to_num(w), torch.zeros_like(pred)).pow(2).sum(1) / mask.sum(1)
    return (err / dw2).mean()


def train(kind, train_groups, val_groups, k2, iso_by_mat, *, width=16, depth=2, wd=1e-4, lr=1e-3,
          steps=300, batch_size=16, max_len=600, eval_every=50, seed=0, log=None):
    torch.manual_seed(seed)
    rng = np.random.default_rng(seed)
    model = (L1 if kind == "L1" else L2)(width=width, depth=depth)
    opt = torch.optim.Adam(model.parameters(), lr=lr, weight_decay=wd)
    limit = kind == "L1"
    best, best_state, t0 = float("inf"), None, time.time()
    for step in range(1, steps + 1):
        g = train_groups[rng.integers(len(train_groups))]
        n = len(g["m"])
        idx = rng.choice(n, size=min(batch_size, n), replace=False)
        rh, w = batch(g, idx, max_len)
        ctx = make_ctx(g, k2, iso_by_mat, idx)
        pred = integrate(model, rh, w[:, 0], ctx, dt=DT_MIN, limit=limit)
        loss = seg_loss(pred, w)
        opt.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        opt.step()
        if val_groups and (step % eval_every == 0 or step == steps):
            v = evaluate(model, kind, val_groups, k2, iso_by_mat, max_len=max_len)["median_E"]
            if log:
                log(f"step {step} loss {loss.item():.4f} val_medE {v:.4f} ({time.time() - t0:.0f}s)")
            if v < best:
                best, best_state = v, {k: x.clone() for k, x in model.state_dict().items()}
    if best_state is not None:
        model.load_state_dict(best_state)
    return model, best


@torch.no_grad()
def predict(model, kind, g, k2, iso_by_mat, max_len=None):
    idx = np.arange(len(g["m"]))
    L = g["rh"].shape[1] if max_len is None else max_len
    rh, w = batch(g, idx, L)
    ctx = make_ctx(g, k2, iso_by_mat, idx)
    return integrate(model, rh, w[:, 0], ctx, dt=DT_MIN, limit=(kind == "L1")).numpy(), w.numpy()


def evaluate(model, kind, groups, k2, iso_by_mat, max_len=None):
    E = []
    for g in groups:
        pred, w = predict(model, kind, g, k2, iso_by_mat, max_len)
        for p, ww in zip(pred, w):
            n = int(np.isfinite(ww).sum())
            E.append(normalised_rms(p[:n], ww[:n]))
    E = np.array(E)
    return {"median_E": float(np.nanmedian(E)), "E": E}
