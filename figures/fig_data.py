"""Figure 1 (descriptive, data only; allowed before the freeze, PREREG section 9).

a  adsorption isotherms at 27 C for the eight sorbents (end-points of the isotherm runs);
b  one measured 0 -> 30 % RH uptake step per sorbent at 27 C, as fraction of the step change
   against time (first step-run file, second repeat), showing the spread of time scales;
c  the measured test-retest noise floor F per sorbent and temperature.

Sorbents are coloured by family (hues kept apart from the model colours of figstyle) and
differ by line style within a family.

usage: python -I figures/fig_data.py data_derived/bezrukov2023 results/prefreeze/summary.json figures/out/fig1_data
"""
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from p4 import figstyle as fs  # noqa: E402
from p4.dataset import build_groups  # noqa: E402

import matplotlib.pyplot as plt  # noqa: E402

FAM_COLOUR = {"Al-rod": fs.OI["vermilion"], "Zn-triazolate-F": fs.OI["green"],
              "Cu-glutarate-bpy": fs.OI["purple"], "silica": fs.OI["sky"]}
SORB = [("MOF-303", "Al-rod", "-"), ("MIL-160", "Al-rod", "--"), ("CAU-10", "Al-rod", "-."),
        ("Al-fumarate", "Al-rod", ":"), ("ROS-039", "Zn-triazolate-F", "-"),
        ("ROS-040", "Zn-triazolate-F", "--"), ("ROS-037", "Cu-glutarate-bpy", "-"),
        ("Syloid", "silica", "-")]
LABEL = {"CAU-10": "CAU-10-H", "Syloid": "Syloid AL-1"}


def main():
    root, summary_path, stem = sys.argv[1:4]
    groups = {(g["sorbent"], g["temp"]): g for g in build_groups(root)}
    summ = json.load(open(summary_path, encoding="utf-8"))
    fs.apply()
    fig, axs = plt.subplots(1, 3, figsize=(fs.W2, 64 * fs.MM), gridspec_kw={"wspace": 0.45})
    fig.subplots_adjust(left=0.07, right=0.99, top=0.93, bottom=0.30)
    a, b, c = axs
    for s, fam, ls in SORB:
        g = groups[(s, "27C")]
        col = FAM_COLOUR[fam]
        rh = np.linspace(0, 40, 200)
        a.plot(rh, g["ads"].w_of_rh(rh), color=col, linestyle=ls, label=LABEL.get(s, s))
        # first up-step to 30 % in the first run file, second repeat
        runs = sorted(set(g["run"]))
        sel = [i for i in range(len(g["m"])) if g["run"][i] == runs[0] and g["dir"][i] == 1]
        ups30 = [i for i in sel if np.nanmax(g["rh"][i]) < 45]
        i = ups30[1] if len(ups30) > 1 else ups30[0]
        w = g["w"][i][np.isfinite(g["w"][i])]
        t = np.arange(len(w)) * 0.1
        b.plot(t, (w - w[0]) / (w[-1] - w[0]), color=col, linestyle=ls)
    a.set_xlabel("relative humidity (%)")
    a.set_ylabel("uptake at 27 °C (wt%)")
    a.set_xlim(0, 40)
    fig.legend(*a.get_legend_handles_labels(), loc="lower left", ncol=4, handlelength=2.6,
               bbox_to_anchor=(0.04, -0.01), columnspacing=1.4)
    b.set_xlabel("time after the 0 → 30 % RH step (min)")
    b.set_ylabel("fraction of the step change")
    b.set_xlim(0, 80)
    b.set_ylim(-0.02, 1.05)
    # c: noise floor per sorbent and temperature
    names = [s for s, _, _ in SORB]
    x = np.arange(len(names))
    for j, (T, mk) in enumerate((("27C", "o"), ("60C", "s"))):
        vals = [summ["noise_floor"].get(f"{s}|{T}", {}).get("median_E", np.nan) for s in names]
        c.plot(x + (j - 0.5) * 0.25, vals, linestyle="none", marker=mk, color=fs.OI["dark"],
               markerfacecolor="none" if T == "27C" else fs.OI["dark"], label=T.replace("C", " °C"))
    c.set_xticks(x)
    c.set_xticklabels([LABEL.get(s, s) for s in names], rotation=60, ha="right")
    c.set_ylabel("noise floor F (normalized RMS)")
    c.set_yscale("log")
    # plain tick labels: the superscripts of 10^-3 would print below 5 pt at 6 pt tick size
    from matplotlib.ticker import FixedLocator, NullLocator
    c.yaxis.set_major_locator(FixedLocator([0.001, 0.002, 0.005, 0.01]))
    c.yaxis.set_minor_locator(NullLocator())
    c.set_yticklabels(["0.001", "0.002", "0.005", "0.01"])
    c.legend(loc="upper left")
    for ax, l in zip(axs, "abc"):
        fs.letter(ax, l)
    fs.save(fig, stem, inputs=[summary_path])


if __name__ == "__main__":
    main()
