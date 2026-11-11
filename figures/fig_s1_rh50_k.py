"""Supplementary Fig. S1 (EXPLORATORY): each sorbent's own rate constant (in-sample metric fit, R2,
results/prefreeze/reproduce_b0.json) against its half-loading humidity RH50 (results/rh50.json), per temperature and
direction, with the Spearman rank correlation over the eight parent sorbents and its exact p
(results/exploratory/rh50_vs_k.json, audit/exploratory_rh50_vs_k.py). Composites shown as open markers, not counted.

usage: python -I figures/fig_s1_rh50_k.py results/exploratory/rh50_vs_k.json figures/out/fig_s1
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from p4 import figstyle as fs  # noqa: E402

import matplotlib.pyplot as plt  # noqa: E402

TITLE = {"27C|ads": "27 °C, uptake", "27C|des": "27 °C, release", "60C|ads": "60 °C, uptake", "60C|des": "60 °C, release"}


def main():
    src, stem = sys.argv[1:3]
    d = json.load(open(src, encoding="utf-8"))["strata"]
    fs.apply()
    fig, axes = plt.subplots(1, 4, figsize=(fs.W2, 50 * fs.MM))
    for ax, key, letter in zip(axes, TITLE, "abcd"):
        st = d[key]
        for s, (x, y) in st["points"].items():
            comp = s.endswith("_composite")
            ax.plot(x, y, ls="none", marker="o", ms=3.2, mec=fs.OI["dark"],
                    mfc="white" if comp else fs.OI["dark"])
        ax.set_title(TITLE[key], fontsize=fs.SMALL_PT)
        ax.text(0.04, 0.96, f"ρ = {st['rho']:.2f}, p = {st['p_exact']:.2f}", transform=ax.transAxes,
                fontsize=fs.SMALL_PT, va="top")
        ax.set_xlabel("RH₅₀ (% RH)")
        fs.letter(ax, letter, x=-0.32)
    axes[0].set_ylabel("Own k″ (wt% mg min⁻¹ %RH⁻¹)")
    fig.subplots_adjust(left=0.08, right=0.99, bottom=0.24, top=0.85, wspace=0.45)
    fs.save(fig, stem, inputs=[src])


if __name__ == "__main__":
    main()
