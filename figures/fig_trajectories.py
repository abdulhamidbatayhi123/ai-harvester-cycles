"""Held-out predictions against the measurements (R2), chosen by a fixed rule so that no panel is picked by eye:
the held-out sorbents with the lowest, the middle (lower median of eight) and the highest median B0 error, and for
each the segment whose B0 error is closest to that sorbent's median B0 error (a typical segment, not a good or bad
one). Models: B0 (pooled k'' of the training sorbents), B2 (isotherm-predicted k''), both with the parameters stored
in the confirmatory rows, and the oracle B0* (own k'', refitted on the held-out sorbent as in p4.run_study).

usage: python -E -s figures/fig_trajectories.py data_derived/bezrukov2023 results/confirm_R2/rows.jsonl figures/out/fig_trajectories
"""
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from p4 import figstyle as fs  # noqa: E402
from p4.dataset import build_groups  # noqa: E402
from p4.physics import rh50, simulate_b0  # noqa: E402
from p4.run_study import COMPOSITE_OF, PRIMARY8, fit_physics, physics_pred  # noqa: E402
from p4.segments import DT_MIN, normalised_rms  # noqa: E402

import matplotlib.pyplot as plt  # noqa: E402

LABEL = {"CAU-10": "CAU-10-H", "Syloid": "Syloid AL-1"}


def b2_pred(te, ab):
    out = []
    for g in te:
        x = rh50(g["ads"]) / 30.0
        pa, pd = ab[f"{g['temp']}|ads"], ab[f"{g['temp']}|des"]
        out.append(simulate_b0(g["rh"], g["w"][:, 0], np.exp(pa[0] + pa[1] * (x - pa[2])) / g["m"],
                               np.exp(pd[0] + pd[1] * (x - pd[2])) / g["m"], g["ads"], None, dt=DT_MIN))
    return out


def main():
    data, rows_p, stem = sys.argv[1:4]
    rows = {r["fold"]: r for r in map(json.loads, open(rows_p, encoding="utf-8")) if r["key"].endswith("|physics")}
    groups = [g for g in build_groups(data, rule="R2") if g["sorbent"] in PRIMARY8 + list(COMPOSITE_OF.values())]
    medE = {s: float(np.nanmedian(rows[f"LOSO:{s}"]["E"]["B0"])) for s in PRIMARY8}
    order = sorted(PRIMARY8, key=lambda s: medE[s])
    chosen = [order[0], order[3], order[-1]]
    fs.apply()
    fig, axes = plt.subplots(1, 3, figsize=(fs.W2, 58 * fs.MM))
    picks = []
    for ax, s, letter in zip(axes, chosen, "abc"):
        p = rows[f"LOSO:{s}"]
        own = [g for g in groups if g["sorbent"] == s]
        k2 = {tuple(k.split("|")): v for k, v in p["k2"].items()}
        pb0 = physics_pred(own, simulate_b0, k2, False)
        pb2 = b2_pred(own, p["B2_ab"])
        pst = physics_pred(own, simulate_b0, fit_physics(own, simulate_b0, False), False)
        cand = []
        for gi, g in enumerate(own):
            for i, ww in enumerate(g["w"]):
                n = int(np.isfinite(ww).sum())
                cand.append((abs(normalised_rms(pb0[gi][i][:n], ww[:n]) - medE[s]), gi, i, n))
        _, gi, i, n = min(cand)
        g = own[gi]
        t = np.arange(n) * DT_MIN
        ax.plot(t[::5], g["w"][i][:n][::5], **fs.style("data"), ms=2.2, label="measured")
        ax.plot(t, pb0[gi][i][:n], **fs.style("B0"), label="B0 (shared k″)")
        ax.plot(t, pb2[gi][i][:n], color=fs.OI["blue"], ls="--", label="B2 (from isotherm)")
        ax.plot(t, pst[gi][i][:n], **fs.style("B0star"), label="B0* (own k″)")
        rf, rt = float(np.median(g["rh"][i][:5])), float(np.median(g["rh"][i][n - 5:n]))
        ax.set_title(f"{LABEL.get(s, s)}, {g['temp'][:2]} °C, {rf:.0f} → {rt:.0f} % RH", fontsize=fs.SMALL_PT)
        ax.set_xlabel("Time in the step (min)")
        fs.letter(ax, letter, x=-0.2)
        picks.append({"sorbent": s, "temp": g["temp"], "segment_index_in_group": i, "rh_from": rf, "rh_to": rt,
                      "median_E_B0_sorbent": medE[s]})
    axes[0].set_ylabel("Uptake (wt%)")
    axes[1].legend(loc="upper right", fontsize=fs.SMALL_PT)
    fig.subplots_adjust(left=0.07, right=0.99, bottom=0.2, top=0.86, wspace=0.3)
    fs.save(fig, stem, inputs=[rows_p])
    with open(stem + ".picks.json", "w", encoding="utf-8", newline="\n") as f:
        json.dump(picks, f, indent=1)


if __name__ == "__main__":
    main()
