"""Workflow of the study: a map of the paper (schematic; reads no data, carries no result).

Row 1: data -> the isotherm-driven model -> held-out tests and the decision rule.
Row 2: the result blocks, each tagged: black chip = pre-registered hypothesis with a decision rule,
       white chip = gate (must pass first) or descriptive.
Row 3: what the paper concludes from them.
Every box restates the pre-registration (PREREG_P4_draft.md sections 2-10b); nothing is claimed here
that the text does not state. The script refuses to save if any text leaves its box or two texts
overlap (layout check, PAPER_WORKFLOW_LESSONS section 5).

usage: python -I figures/fig_workflow.py figures/out/fig_workflow
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from p4 import figstyle as fs  # noqa: E402

import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch  # noqa: E402

W, H = 183.0, 92.0
ROW1 = [("Data", ["dynamic vapour sorption archive:", "eight sorbents, two composites,",
                  "step runs and isotherms", "at two temperatures"], "Methods: data", "sky"),
        ("Isotherm-driven model", ["rate set by the humidity gap", "to the isotherm; one rate",
                                   "constant shared by all", "training sorbents (B0)"], "Methods: models", "orange"),
        ("Held-out tests", ["leave one sorbent out (8 folds),", "leave one family out;", "noise floor, practical margin,",
                            "signed-rank test, 7 of 8 folds"], "Methods: decision rule", "blue")]
ROW2 = [("Learned correction", ["grey-box network on", "the rate; synthetic", "harness, seven rounds"], "H4a: not tested", True),
        ("Harness for B2", ["known truths: no effect,", "realistic effect, nulls,", "form error"], "gate", False),
        ("Isotherm-predicted k″", ["rate constant from", "the isotherm (B2)", "against shared k″"], "H4a′", True),
        ("Where B0's error lies", ["own k″ (oracle) and", "own end point:", "share of B0's error"], "descriptive", False),
        ("Whole families", ["leave one family out", "against one sorbent", "out"], "descriptive", False)]


def main():
    stem = sys.argv[1]
    fs.apply()
    fig = plt.figure(figsize=(W * fs.MM, H * fs.MM))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, W)
    ax.set_ylim(0, H)
    ax.axis("off")
    FS, FS2 = fs.BODY_PT, fs.SMALL_PT
    boxes, texts = [], []

    def tint(c, a):
        from matplotlib.colors import to_rgb
        r, g, b = to_rgb(c)
        return (1 - a + a * r, 1 - a + a * g, 1 - a + a * b)

    def box(x, y, w, h, fc, ec, lw=0.8, owner=True):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=1.4", fc=fc, ec=ec, lw=lw))
        if owner:
            boxes.append((x, y, w, h))
        return len(boxes) - 1

    def text(x, y, s, b, **kw):
        texts.append((ax.text(x, y, s, **kw), b))

    def arrow(p, q):
        ax.add_patch(FancyArrowPatch(p, q, arrowstyle="-|>,head_length=2.0,head_width=1.0", color=fs.OI["dark"],
                                     lw=0.8, shrinkA=0, shrinkB=0, mutation_scale=1.0))

    # row 1
    n, gap, x0 = 3, 8.0, 1.5
    bw = (W - 2 * x0 - (n - 1) * gap) / n
    y1, h1 = 60.0, 30.0
    for i, (title, lines, ref, col) in enumerate(ROW1):
        x = x0 + i * (bw + gap)
        c = fs.OI[col]
        b = box(x, y1, bw, h1, tint(c, 0.15), c)
        text(x + bw / 2, y1 + h1 - 2.5, title, b, fontsize=FS, fontweight="bold", ha="center", va="top")
        for k, s in enumerate(lines):
            text(x + bw / 2, y1 + h1 - 8.0 - 3.4 * k, s, b, fontsize=FS2, ha="center", va="top")
        text(x + bw / 2, y1 + 1.8, ref, b, fontsize=FS2, ha="center", va="bottom", style="italic", color=fs.OI["dark"])
        if i < n - 1:
            arrow((x + bw + 0.5, y1 + h1 / 2), (x + bw + gap - 0.5, y1 + h1 / 2))
    # row 2
    y2, h2 = 15.0, 27.0
    outer = box(x0, y2 - 2.0, W - 2 * x0, h2 + 9.0, tint(fs.OI["black"], 0.04), fs.OI["grey"], lw=0.6, owner=False)
    ax.text(W / 2, y2 + h2 + 1.6, "Results", fontsize=FS, fontweight="bold", ha="center", va="bottom")
    arrow((x0 + 2 * (bw + gap) + bw / 2, y1 - 0.3), (x0 + 2 * (bw + gap) + bw / 2, y2 + h2 + 6.6))
    m, g2 = 5, 2.6
    cw = (W - 2 * x0 - 4.0 - (m - 1) * g2) / m
    for j, (title, lines, chip, reg) in enumerate(ROW2):
        x = x0 + 2.0 + j * (cw + g2)
        b = box(x, y2, cw, h2 - 1.0, "white", fs.OI["grey"], lw=0.7)
        text(x + cw / 2, y2 + h2 - 3.6, title, b, fontsize=FS2, ha="center", va="top", fontweight="bold")
        for k, s in enumerate(lines):
            text(x + cw / 2, y2 + h2 - 8.6 - 3.3 * k, s, b, fontsize=FS2, ha="center", va="top")
        cwid = 4.0 + 1.35 * len(chip)
        ax.add_patch(FancyBboxPatch((x + cw / 2 - cwid / 2, y2 + 1.5), cwid, 4.4, boxstyle="round,pad=0,rounding_size=0.8",
                                    fc=fs.OI["black"] if reg else "white", ec=fs.OI["black"] if reg else fs.OI["grey"], lw=0.6))
        text(x + cw / 2, y2 + 3.7, chip, b, fontsize=FS2, ha="center", va="center",
             color="#ffffff" if reg else fs.OI["dark"], fontweight="bold" if reg else "normal",
             style="normal" if reg else "italic")
    # row 3
    y3, h3 = 1.0, 8.5
    arrow((W / 2, y2 - 2.3), (W / 2, y3 + h3 + 0.3))
    b = box(W / 2 - 62.0, y3, 124.0, h3, tint(fs.OI["green"], 0.15), fs.OI["green"])
    text(W / 2, y3 + h3 / 2, "Can an unseen sorbent's dynamics be predicted from its isotherm?", b, fontsize=FS,
         fontweight="bold", ha="center", va="center")
    # layout check: every text inside its box, no two texts overlapping
    fig.canvas.draw()
    inv = ax.transData.inverted()
    bb = []
    for t, k in texts:
        e = t.get_window_extent()
        (ax0, ay0), (ax1, ay1) = inv.transform([[e.x0, e.y0], [e.x1, e.y1]])
        x, y, w, h = boxes[k]
        assert x + 0.4 <= ax0 and ax1 <= x + w - 0.4 and y + 0.3 <= ay0 and ay1 <= y + h - 0.3, \
            f"text leaves its box: {t.get_text()!r}"
        bb.append((ax0, ay0, ax1, ay1, t.get_text()))
    for i in range(len(bb)):
        for j in range(i + 1, len(bb)):
            a, c = bb[i], bb[j]
            assert a[2] <= c[0] or c[2] <= a[0] or a[3] <= c[1] or c[3] <= a[1], f"texts overlap: {a[4]!r} / {c[4]!r}"
    fs.save(fig, stem, inputs=[])


if __name__ == "__main__":
    main()
