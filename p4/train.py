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
    return {"ads": ads, "des": TorchBranch(g["des"].rh, g["des"].w), "w30": w30, "m": m,
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


def measured_rates(w, dt=DT_MIN, half=3):
    """dw/dt from the measured uptake by a centred difference over +-`half` grid points
    (+-18 s), NaN where the window leaves the segment."""
    r = np.full_like(w, np.nan)
    r[:, half:-half] = (w[:, 2 * half:] - w[:, :-2 * half]) / (2 * half * dt)
    return r


def smoothed_rh(rh, half=3):
    """RH averaged over the same centred window as measured_rates (+-`half` grid points), NaN
    where the window leaves the segment. Stage A pairs each finite-difference rate, an average over
    the window, with this average rather than the instantaneous measured RH: the RH jitter is
    otherwise an error in the input variable, largest relative to the driving force near
    equilibrium (harness round 4 diagnostic, audit/diag/l1_stageA_diag.py: on held-out MOF-303
    in world C, L1 reached E 0.021 with the instantaneous RH, 0.008 with the smoothed RH, 0.007
    with the exact rates)."""
    out = np.full_like(rh, np.nan)
    ok = np.isfinite(rh)
    cs = np.cumsum(np.where(ok, rh, 0.0), axis=1)
    cn = np.cumsum(ok, axis=1)
    pad = lambda a: np.pad(a, ((0, 0), (1, 0)))
    s = cs[:, 2 * half:] - pad(cs)[:, :-2 * half - 1]
    n = cn[:, 2 * half:] - pad(cn)[:, :-2 * half - 1]
    out[:, half:-half] = np.where(n == 2 * half + 1, s / np.maximum(n, 1), np.nan)
    return out


def segment_t63(w, dt=DT_MIN):
    """Time (min) for each segment to reach 63 % of its measured change, at least one grid step."""
    out = np.empty(len(w))
    for i, row in enumerate(w):
        row = row[np.isfinite(row)]
        tot = abs(row[-1] - row[0])
        j = int(np.argmax(np.abs(row - row[0]) >= 0.63 * tot)) if tot > 0 else 1
        out[i] = max(j, 1) * dt
    return out


def train_two_stage(kind, train_groups, val_groups, k2, iso_by_mat, *, width=16, depth=2, wd=1e-4,
                    lr=1e-3, steps_rate=2000, steps_roll=300, window=100, batch_size=64, seed=0,
                    eval_every=100, log=None):
    """Stage A: fit the rate law to measured dw/dt, paired with the RH averaged over the same
    window (smoothed_rh), each point's error weighted by t63 / |dw| of its segment (no
    integration; fast). Stage B: fine-tune on
    open-loop rollouts over random windows of `window` grid steps (10 min), started from the
    measured uptake. Validation (full segments, open loop) selects the best state of stage B,
    or of stage A if B never improves on it."""
    torch.manual_seed(seed)
    rng = np.random.default_rng(seed)
    model = (L1 if kind == "L1" else L2)(width=width, depth=depth)
    limit = kind == "L1"
    opt = torch.optim.Adam(model.parameters(), lr=lr, weight_decay=wd)
    t0 = time.time()
    # stage A: pooled points (w, rh, rate) per group, normalised by the segment's |dw|
    pts = []
    for gi, g in enumerate(train_groups):
        r = measured_rates(g["w"])
        rh_s = smoothed_rh(g["rh"])
        # weight = t63 / |dw| per segment: a rate error times the segment's time scale is the
        # trajectory error it causes, in units of E, so slow and fast segments count alike
        # (harness round 5 diagnostic: weighting by 1/|dw| alone left the slow 27 C releases
        # underfitted, and L1 lost to B0 there)
        dw = (np.abs(np.nanmax(g["w"], 1) - np.nanmin(g["w"], 1)) / segment_t63(g["w"]))[:, None] * np.ones_like(g["w"])
        ok = np.isfinite(r) & np.isfinite(rh_s)
        seg = np.repeat(np.arange(len(g["m"]))[:, None], g["w"].shape[1], 1)
        pts.append((gi, seg[ok], g["w"][ok], rh_s[ok], r[ok], dw[ok]))
    for step in range(1, steps_rate + 1):
        gi, seg, w, rh, r, dw = pts[rng.integers(len(pts))]
        j = rng.integers(0, len(w), size=min(4096, len(w)))
        g = train_groups[gi]
        ctx = make_ctx(g, k2, iso_by_mat, seg[j])
        pred = model.rate(torch.as_tensor(w[j]), torch.as_tensor(rh[j]), ctx)
        loss = ((pred - torch.as_tensor(r[j])) / torch.as_tensor(dw[j]).clamp_min(1e-3)).pow(2).mean()
        opt.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        opt.step()
        if log and step % 500 == 0:
            log(f"A step {step} loss {loss.item():.5f} ({time.time() - t0:.0f}s)")
    best = evaluate(model, kind, val_groups, k2, iso_by_mat)["median_E"] if val_groups else float("inf")
    best_state = {k: x.clone() for k, x in model.state_dict().items()}
    if log:
        log(f"after stage A val_medE {best:.4f} ({time.time() - t0:.0f}s)")
    # stage B: short open-loop windows
    opt = torch.optim.Adam(model.parameters(), lr=lr * 0.3, weight_decay=wd)
    for step in range(1, steps_roll + 1):
        g = train_groups[rng.integers(len(train_groups))]
        n, L = g["w"].shape
        idx = rng.choice(n, size=min(batch_size, n), replace=False)
        lens = np.isfinite(g["w"][idx]).sum(1)
        starts = np.array([rng.integers(0, max(1, l - window)) for l in lens])
        rh = np.full((len(idx), window), np.nan)
        w = np.full((len(idx), window), np.nan)
        for i, (s0, l) in enumerate(zip(starts, lens)):
            e = min(s0 + window, l)
            rh[i, : e - s0] = g["rh"][idx[i], s0:e]
            w[i, : e - s0] = g["w"][idx[i], s0:e]
        dw = np.abs(np.nanmax(g["w"][idx], 1) - np.nanmin(g["w"][idx], 1))
        ctx = make_ctx(g, k2, iso_by_mat, idx)
        rh_t, w_t = torch.as_tensor(rh), torch.as_tensor(w)
        pred = integrate(model, rh_t, w_t[:, 0], ctx, dt=DT_MIN, limit=limit)
        mask = torch.isfinite(w_t)
        err = torch.where(mask, pred - torch.nan_to_num(w_t), torch.zeros_like(pred)).pow(2).sum(1) / mask.sum(1)
        loss = (err / torch.as_tensor(dw).clamp_min(1e-3).pow(2)).mean()
        opt.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        opt.step()
        if val_groups and (step % eval_every == 0 or step == steps_roll):
            v = evaluate(model, kind, val_groups, k2, iso_by_mat)["median_E"]
            if log:
                log(f"B step {step} loss {loss.item():.5f} val_medE {v:.4f} ({time.time() - t0:.0f}s)")
            if v < best:
                best, best_state = v, {k: x.clone() for k, x in model.state_dict().items()}
    model.load_state_dict(best_state)
    return model, best


def beats(E_model, E_b0, F, rel=0.10, n_boot=2000, seed=0):
    """SUPERSEDED (kept to reproduce harness rounds 1-3): the section 7 rule now lives in p4.decide
    (clusters, exact signed-rank test, every material). Old rule: the median over
    segments of the paired difference d = E_B0 - E_model. A model beats B0 if median(d) > F,
    median(d) >= rel * median(E_B0), and the 2.5 % bootstrap quantile of median(d) > 0.
    (Resampling by experiment, with two-pan pairs as one, is applied by the caller through
    `E_model`/`E_b0` aggregated per experiment where required.)"""
    rng = np.random.default_rng(seed)
    d = np.asarray(E_b0) - np.asarray(E_model)
    d = d[np.isfinite(d)]
    gain = float(np.median(d))
    boots = np.array([np.median(d[rng.integers(0, len(d), len(d))]) for _ in range(n_boot)])
    lo = float(np.quantile(boots, 0.025))
    ok = bool(gain > F and gain >= rel * float(np.nanmedian(E_b0)) and lo > 0)
    return ok, {"median_paired_gain": gain, "ci_low": lo, "E_b0": float(np.nanmedian(E_b0)),
                "E_model": float(np.nanmedian(E_model))}


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
