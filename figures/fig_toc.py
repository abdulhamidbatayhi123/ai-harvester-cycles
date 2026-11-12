"""Graphical abstract for AIChE Journal (must fit 50 mm x 60 mm and be legible at that size; guidelines read
2026-11-11): the relative improvement r of the isotherm-predicted rate constant (B2) over the shared one (B0) for each
held-out sorbent, under both dry-mass rules, against the 10 % practical margin. Same data as Fig. 3a.

usage: python -I figures/fig_toc.py results/confirm_R2/decide.json results/confirm_R1/decide.json figures/out/fig_toc
"""
import json
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from p4 import figstyle as fs  # noqa: E402

import matplotlib.pyplot as plt  # noqa: E402

ORDER = ["MOF-303", "MIL-160", "CAU-10", "Al-fumarate", "ROS-039", "ROS-040", "ROS-037", "Syloid"]


def main():
    d2, d1 = (json.load(open(p, encoding="utf-8")) for p in sys.argv[1:3])
    stem = sys.argv[3]
    fs.apply()
    fig = plt.figure(figsize=(50 * fs.MM, 60 * fs.MM))
    ax = fig.add_axes([0.24, 0.17, 0.72, 0.52])
    col = fs.OI["blue"]
    ys = []
    for dec, mk, dx in ((d2, "o", -0.15), (d1, "s", 0.15)):
        for i, s in enumerate(ORDER):
            r = 100 * dec["folds"][f"LOSO:{s}|B2"]["r_fold"]
            ys.append(r)
            ax.plot(i + dx, r, ls="none", marker=mk, ms=3, mec=col, mfc="white", mew=0.7,
                    gid=f"r (%) {'R2' if dec is d2 else 'R1'} {s}")
    ax.axhline(0, color=fs.OI["grey"], lw=0.5)
    ax.axhline(10, color=fs.OI["dark"], lw=0.7, ls="--")
    ax.text(7.4, 10.8, "10 % margin", fontsize=fs.SMALL_PT, ha="right", va="bottom")
    ax.set_xticks(range(len(ORDER)))
    ax.set_xticklabels([])
    ax.set_xlabel("8 held-out sorbents", fontsize=fs.SMALL_PT)
    ax.set_ylabel("Gain over shared k″ (%)", fontsize=fs.SMALL_PT)
    lo = 5 * math.floor((min(ys) - 2) / 5)
    ax.set_ylim(lo, 16)
    ax.set_xlim(-0.6, len(ORDER) - 0.4)
    fig.text(0.5, 0.97, "Does the isotherm predict", fontsize=fs.BODY_PT, ha="center", va="top", fontweight="bold")
    fig.text(0.5, 0.905, "a sorbent's uptake rate?", fontsize=fs.BODY_PT, ha="center", va="top", fontweight="bold")
    beaten = max(d["H4a"]["B2"]["LOSO_beats"] for d in (d2, d1))      # from the decide outputs, not typed
    folds = d2["H4a"]["B2"]["LOSO_folds"]
    fig.text(0.5, 0.80, f"Pre-registered test: {beaten} of {folds} beaten", fontsize=fs.SMALL_PT, ha="center", va="top")
    fig.text(0.5, 0.025, "circles, squares: two dry-mass rules", fontsize=fs.SMALL_PT, ha="center", va="bottom")
    fs.save(fig, stem, inputs=sys.argv[1:3])


if __name__ == "__main__":
    main()
