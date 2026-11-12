"""Harness record of the learned models (PREREG section 10; synthetic data only).

a  L1: median E of L1 over median E of B0 refitted on the training sorbents, per harness round,
   world and held-out sorbent. Marker shape = world (N no correction; C, C2, C3 correction
   worlds), filled = a beat by the decision rule in force in that round, open = no beat;
   sorbents are offset within a round (MOF-303 left, ROS-039 middle, Al-fumarate right, round 7
   only). Lines at 1 (no change) and 0.5 (the halving that criterion 2 required from round 3).
b  L2 (black box), rounds 1 to 4, worlds N and C; dropped after round 4.

Round 3 ran L2 only; round 1 ran world C on MOF-303 only.

usage: python -I figures/fig_harness_l1.py figures/out/fig_harness_l1
"""
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from p4 import figstyle as fs  # noqa: E402

import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILES = {r: os.path.join(ROOT, "results", f"harness_round{r}", "harness.json") for r in range(1, 8)}
ALFU = os.path.join(ROOT, "results", "harness_alfu", "harness.json")
WORLD_MARK = {"N": "o", "C": "s", "C2": "D", "C3": "^"}
OFFSET = {"MOF-303": -0.18, "ROS-039": 0.0, "Al-fumarate": 0.18}


def rows():
    out = []
    for r, f in FILES.items():
        h = json.load(open(f, encoding="utf-8"))
        for key, v in h["cases"].items():
            world, held = key.split("|")
            for kind in ("L1", "L2"):
                if kind in v:
                    L = v[kind]
                    eb = L.get("E_B0", L.get("E_b0"))
                    out.append((r, world, held, kind, L["E_model"] / eb, bool(L["beats_B0"])))
    h = json.load(open(ALFU, encoding="utf-8"))
    for key, v in h["cases"].items():
        world, held = key.split("|")
        out.append((7, world, held, "L1", v["L1"]["E_model"] / v["L1"]["E_B0"], bool(v["L1"]["beats_B0"])))
    return out


def ticks(ax, vals):
    from matplotlib.ticker import FixedLocator, NullLocator
    ax.yaxis.set_major_locator(FixedLocator(vals))
    ax.yaxis.set_minor_locator(NullLocator())
    ax.set_yticklabels([f"{v:g}" for v in vals])


def main():
    stem = sys.argv[1]
    fs.apply()
    R = rows()
    fig, (a, b) = plt.subplots(1, 2, figsize=(fs.W2, 70 * fs.MM), gridspec_kw={"width_ratios": [2.4, 1]})
    col1, col2 = fs.MODEL["L1"]["color"], fs.MODEL["L2"]["color"]
    for ax in (a, b):
        ax.axhline(1.0, color=fs.OI["grey"], lw=0.6, ls="-")
        ax.set_yscale("log")
    a.axhline(0.5, color=fs.OI["grey"], lw=0.6, ls="--")
    for r, world, held, kind, ratio, beat in R:
        if kind != "L1":
            continue
        a.plot(r + OFFSET[held], ratio, ls="none", marker=WORLD_MARK[world], ms=4, mec=col1,
               gid=f"L1/B0 round {r} world {world} {held} beat={beat}",
               mfc=col1 if beat else "white", mew=0.8)
    # the one judged case that failed in round 7
    for r, world, held, kind, ratio, beat in R:
        if kind == "L1" and r == 7 and world == "C3" and held == "MOF-303":
            a.annotate("MOF-303", (r + OFFSET[held], ratio), xytext=(-34, 16), textcoords="offset points",
                       fontsize=fs.SMALL_PT, arrowprops={"arrowstyle": "-", "lw": 0.5, "color": fs.OI["dark"]})
    a.set_xticks(range(1, 8))
    a.set_xlim(0.5, 7.6)
    a.set_ylim(0.08, 4)
    ticks(a, [0.1, 0.2, 0.5, 1, 2])
    a.set_xlabel("Harness round")
    a.set_ylabel("Median $E$, L1 / B0")
    a.text(0.55, 0.5, "halving", fontsize=fs.SMALL_PT, ha="left", va="bottom")
    a.text(0.55, 1.0, "no change", fontsize=fs.SMALL_PT, ha="left", va="bottom")
    hand = [Line2D([], [], ls="none", marker=WORLD_MARK[w], ms=4, mec=col1, mfc="white", mew=0.8, label=lab)
            for w, lab in (("N", "N (no correction)"), ("C", "C"), ("C2", "C2"), ("C3", "C3"))]
    hand += [Line2D([], [], ls="none", marker="o", ms=4, mec=col1, mfc=col1, label="filled: beat")]
    a.legend(handles=hand, loc="upper left", ncol=5, columnspacing=0.8, handletextpad=0.3, bbox_to_anchor=(0, 1.13))
    fs.letter(a, "a", x=-0.09)
    for r, world, held, kind, ratio, beat in R:
        if kind != "L2":
            continue
        b.plot(r + OFFSET[held], ratio, ls="none", marker=WORLD_MARK[world], ms=4, mec=col2,
               gid=f"L2/B0 round {r} world {world} {held} beat={beat}",
               mfc=col2 if beat else "white", mew=0.8)
    b.set_xticks(range(1, 5))
    b.set_xlim(0.5, 4.5)
    b.set_ylim(0.5, 2000)
    ticks(b, [1, 10, 100, 1000])
    b.set_xlabel("Harness round")
    b.set_ylabel("Median $E$, L2 / B0")
    fs.letter(b, "b", x=-0.3)
    fig.subplots_adjust(left=0.07, right=0.985, bottom=0.17, top=0.86, wspace=0.32)
    fs.save(fig, stem, inputs=list(FILES.values()) + [ALFU])


if __name__ == "__main__":
    main()
