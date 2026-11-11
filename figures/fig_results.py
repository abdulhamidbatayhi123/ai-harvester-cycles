"""Key results figure (written 2026-11-11, BEFORE the freeze and before any confirmatory result existed, so its
design cannot be tuned to the outcome; PAPER_WORKFLOW_LESSONS checklist 1b).

a  H4a': relative improvement r of B2 over the pooled B0 of the same variant, per LOSO fold (held-out sorbent),
   under the primary dry-mass rule R2 (circles) and the sensitivity rule R1 (squares). Filled = the fold is beaten
   by the PREREG section 7 rule (four conditions on every held-out material and admissible), open = not beaten.
   Lines at r = 0 and at the 10 % practical margin. r below the axis floor is drawn at the floor as a downward
   triangle (value printed in the provenance file, never hidden).
b  Where B0's error lies (H4b and the end-point oracle, descriptive), R2: per held-out sorbent, the median E of B0
   (pooled k'', no refit), of B0 with the held-out sorbent's own end point (end-point oracle) and of B0 with its own
   k'' (B0*), and the sorbent's noise floor F (horizontal bar). Medians are over every segment of the fold, as in
   p4/decide.py H4b.

Changes after the results (presentation only; no model, point or line added or removed): panel a starts 5 points
below the lowest r instead of at the clipping floor (the floor stays the clipping threshold); panel b's upper
limit has headroom above the highest point, which the decade rule had put on the axis edge (ROS-037, 0.0996).

usage: python -I figures/fig_results.py results/confirm_R2/decide.json results/confirm_R1/decide.json \
           results/confirm_R2/rows.jsonl results/prefreeze/checks2.json figures/out/fig_results
"""
import json
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from p4 import figstyle as fs  # noqa: E402

import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402

ORDER = ["MOF-303", "MIL-160", "CAU-10", "Al-fumarate", "ROS-039", "ROS-040", "ROS-037", "Syloid"]  # families together
LABEL = {"CAU-10": "CAU-10-H", "Syloid": "Syloid AL-1"}
R_FLOOR = -50.0     # % ; fixed before any result
MARGIN = 10.0       # % ; PREREG section 7


def loso_r(dec, s):
    v = dec["folds"].get(f"LOSO:{s}|B2")
    if v is None:
        return None, None
    r = v["r_fold"]
    return (100.0 * r if r is not None and math.isfinite(r) else -math.inf), bool(v["beats_B0"])


def main():
    d2_p, d1_p, rows_p, checks_p, stem = sys.argv[1:6]
    d2 = json.load(open(d2_p, encoding="utf-8"))
    d1 = json.load(open(d1_p, encoding="utf-8"))
    rows = {r["fold"]: r for r in map(json.loads, open(rows_p, encoding="utf-8")) if r["key"].endswith("|physics")}
    F = json.load(open(checks_p, encoding="utf-8"))["F_within_segment_weighted"]
    fs.apply()
    fig, (a, b) = plt.subplots(1, 2, figsize=(fs.W2, 68 * fs.MM), gridspec_kw={"width_ratios": [1, 1.15]})
    x = np.arange(len(ORDER))
    col = fs.OI["blue"]
    clipped = []
    # a: H4a'
    a.axhline(0.0, color=fs.OI["grey"], lw=0.6)
    a.axhline(MARGIN, color=fs.OI["grey"], lw=0.6, ls="--")
    ys = []
    for j, (dec, mk, dx) in enumerate(((d2, "o", -0.14), (d1, "s", 0.14))):
        for i, s in enumerate(ORDER):
            r, beat = loso_r(dec, s)
            if r is None:
                continue
            ys.append(r)
            y = max(r, R_FLOOR)
            m = mk if r >= R_FLOOR else "v"
            if r < R_FLOOR:
                clipped.append({"rule": "R2" if j == 0 else "R1", "sorbent": s,
                                "r_percent": r if math.isfinite(r) else "-inf (a held material without scored segments)"})
            a.plot(x[i] + dx, y, ls="none", marker=m, ms=4, mec=col, mfc=col if beat else "white", mew=0.8)
    top = max([MARGIN + 10.0] + [y + 5.0 for y in ys if math.isfinite(y)])
    fin = [y for y in ys if math.isfinite(y) and y >= R_FLOOR]
    bottom = R_FLOOR - 3.0 if clipped or not fin else max(R_FLOOR - 3.0, min(fin) - 5.0)
    a.set_ylim(bottom, top)
    a.set_xlim(-0.6, len(ORDER) - 0.4)
    a.set_xticks(x)
    a.set_xticklabels([LABEL.get(s, s) for s in ORDER], rotation=60, ha="right")
    a.set_ylabel("$r$ of B2 over B0 (%)")
    a.text(len(ORDER) - 0.45, MARGIN, "margin", fontsize=fs.SMALL_PT, ha="right", va="bottom")
    hand = [Line2D([], [], ls="none", marker="o", ms=4, mec=col, mfc="white", mew=0.8, label="R2"),
            Line2D([], [], ls="none", marker="s", ms=4, mec=col, mfc="white", mew=0.8, label="R1"),
            Line2D([], [], ls="none", marker="o", ms=4, mec=col, mfc=col, mew=0.8, label="filled: fold beaten")]
    a.legend(handles=hand, loc="upper left", ncol=3, columnspacing=0.8, handletextpad=0.3, bbox_to_anchor=(0, 1.14))
    fs.letter(a, "a", x=-0.17)
    # b: where B0's error lies (R2)
    series = (("B0", "B0", fs.style("B0", marker="o", ms=3.5, linestyle="none")),
              ("B0_endpoint_oracle", "own end point", {"color": fs.OI["vermilion"], "marker": "D", "ms": 3.2, "ls": "none"}),
              ("B0star", "own k″ (B0*)", {"color": fs.OI["black"], "marker": "o", "ms": 3.5, "ls": "none",
                                             "markerfacecolor": "white"}))
    vals = []
    for i, s in enumerate(ORDER):
        p = rows.get(f"LOSO:{s}")
        if p is None:
            continue
        for k, (key, _, kw) in enumerate(series):
            e = p["E"].get(key)
            if e:
                v = float(np.nanmedian(np.asarray(e, float)))
                vals.append(v)
                b.plot(x[i] + (k - 1) * 0.2, v, **kw)
        b.plot([x[i] - 0.32, x[i] + 0.32], [F[s]] * 2, color=fs.OI["grey"], lw=1.2, solid_capstyle="butt")
        vals.append(F[s])
    b.set_yscale("log")
    if vals:
        lo, hi = min(vals), max(vals)
        b.set_ylim(10 ** math.floor(math.log10(lo)), max(10 ** math.ceil(math.log10(hi)), 1.6 * hi))
    from matplotlib.ticker import FixedLocator, NullLocator
    lo_e, hi_e = (int(round(math.log10(t))) for t in b.get_ylim())
    tv = [10.0 ** e for e in range(lo_e, hi_e + 1)]
    b.yaxis.set_major_locator(FixedLocator(tv))
    b.yaxis.set_minor_locator(NullLocator())
    b.set_yticklabels([f"{t:g}" for t in tv])
    b.set_xlim(-0.6, len(ORDER) - 0.4)
    b.set_xticks(x)
    b.set_xticklabels([LABEL.get(s, s) for s in ORDER], rotation=60, ha="right")
    b.set_ylabel("Median held-out error $E$")
    hand = [Line2D([], [], label=lab, **kw) for _, lab, kw in series]
    hand.append(Line2D([], [], color=fs.OI["grey"], lw=1.2, label="noise floor $F$"))
    b.legend(handles=hand, loc="upper left", ncol=4, columnspacing=0.8, handletextpad=0.3, bbox_to_anchor=(0, 1.14))
    fs.letter(b, "b", x=-0.15)
    fig.subplots_adjust(left=0.07, right=0.99, bottom=0.27, top=0.86, wspace=0.28)
    fs.save(fig, stem, inputs=[d2_p, d1_p, rows_p, checks_p])
    with open(stem + ".clipped.json", "w", encoding="utf-8") as f:
        json.dump(clipped, f, indent=1)


if __name__ == "__main__":
    main()
