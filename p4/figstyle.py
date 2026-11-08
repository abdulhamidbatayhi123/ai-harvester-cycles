"""Paper 4's single figure style (rules in ~/.claude/PAPER_WORKFLOW_LESSONS.md section 5).

Built to Nature Portfolio's artwork rules as read live on 2026-11-05 by the Paper 2 session
(research-figure-guide.nature.com). The target journal for Paper 4 is not chosen yet; when it
is, re-read its artwork rules live and change the constants below if they differ.

- width 89 mm (single column) or 183 mm (double), height at most 170 mm, drawn at 100 %;
- Arial 5-7 pt (body 7, ticks and legends 6), panel letters 8 pt bold lowercase;
- no gridlines and no coloured text; Okabe-Ito colours; every series also differs by line style
  or marker, so figures survive greyscale;
- vector PDF with embedded TrueType fonts (fonttype 42) plus a 600 dpi PNG for review;
- save() ASSERTS the size, the font range and the absence of coloured text, and writes a
  provenance file with the SHA-256 of the drawing script, this module and every input.

Fixed meanings in every Paper 4 figure:
  measured data      light grey markers (open circles)
  B0 (isotherm-only, Bezrukov)   black, solid
  B1 (linear driving force)      grey, dash-dot
  B0* (oracle, own k'')          black, dotted
  L1 (grey box)                  blue, solid with square markers where markers are used
  L2 (black box)                 orange, dashed with triangle markers
  noise floor F                  light grey band
"""
import hashlib
import json
import os
import sys
import time

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

MM = 1 / 25.4
W1, W2 = 89 * MM, 183 * MM
H_MAX = 170 * MM
BODY_PT, SMALL_PT, LETTER_PT, MIN_PT, MAX_PT = 7.0, 6.0, 8.0, 5.0, 8.0
PNG_DPI = 600

OI = {"black": "#000000", "orange": "#E69F00", "sky": "#56B4E9", "green": "#009E73",
      "yellow": "#F0E442", "blue": "#0072B2", "vermilion": "#D55E00", "purple": "#CC79A7",
      "grey": "#8C8C8C", "light": "#DDDDDD", "dark": "#333333"}

MODEL = {
    "data": {"color": "#B0B0B0", "marker": "o", "mfc": "none", "ls": "none"},
    "B0": {"color": OI["black"], "ls": "-", "marker": None},
    "B1": {"color": OI["grey"], "ls": "-.", "marker": None},
    "B0star": {"color": OI["black"], "ls": ":", "marker": None},
    "L1": {"color": OI["blue"], "ls": "-", "marker": "s"},
    "L2": {"color": OI["orange"], "ls": "--", "marker": "^"},
}
FLOOR_BAND = OI["light"]


def apply():
    plt.rcParams.update({
        "font.family": "sans-serif", "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
        "mathtext.fontset": "custom", "mathtext.rm": "Arial", "mathtext.it": "Arial:italic",
        "mathtext.bf": "Arial:bold", "mathtext.default": "regular",
        "font.size": BODY_PT, "axes.labelsize": BODY_PT, "axes.titlesize": BODY_PT,
        "xtick.labelsize": SMALL_PT, "ytick.labelsize": SMALL_PT, "legend.fontsize": SMALL_PT,
        "legend.title_fontsize": SMALL_PT, "legend.frameon": False, "legend.handlelength": 1.8,
        "axes.linewidth": 0.6, "xtick.major.width": 0.6, "ytick.major.width": 0.6,
        "xtick.major.size": 2.5, "ytick.major.size": 2.5, "lines.linewidth": 1.0,
        "lines.markersize": 3.0, "axes.spines.top": False, "axes.spines.right": False,
        "axes.grid": False, "axes.edgecolor": OI["dark"], "axes.labelcolor": "#000000",
        "xtick.color": OI["dark"], "ytick.color": OI["dark"], "text.color": "#000000",
        "axes.titlelocation": "left", "axes.titleweight": "normal",
        "pdf.fonttype": 42, "ps.fonttype": 42, "svg.fonttype": "none",
        "savefig.dpi": PNG_DPI, "figure.dpi": 150})
    os.environ.setdefault("SOURCE_DATE_EPOCH", "0")


def style(model, **over):
    """Line keyword arguments for a model, from the fixed table above."""
    s = dict(MODEL[model])
    kw = {"color": s["color"], "linestyle": s.get("ls", "-")}
    if s.get("marker"):
        kw["marker"] = s["marker"]
    if "mfc" in s:
        kw["markerfacecolor"] = s["mfc"]
    kw.update(over)
    return kw


def letter(ax, s, x=-0.16, y=1.02):
    ax.text(x, y, s, transform=ax.transAxes, fontsize=LETTER_PT, fontweight="bold",
            ha="left", va="bottom", color="#000000")


def font_range(fig):
    from matplotlib.text import Text
    sizes = [t.get_fontsize() for t in fig.findobj(Text) if t.get_visible() and t.get_text().strip()]
    return (min(sizes), max(sizes)) if sizes else (None, None)


def coloured_text(fig):
    from matplotlib.colors import to_hex
    from matplotlib.text import Text
    ok = {"#000000", OI["dark"].lower(), "#ffffff"}
    return [t.get_text()[:30] for t in fig.findobj(Text)
            if t.get_visible() and t.get_text().strip() and to_hex(t.get_color()).lower() not in ok]


def _sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def save(fig, stem, inputs=()):
    """Assert the artwork rules, then write stem.pdf, stem.png and stem.prov.json."""
    w, h = fig.get_size_inches()
    assert w <= W2 + 1e-6, f"{stem}: width {w / MM:.1f} mm > 183 mm"
    assert h <= H_MAX + 1e-6, f"{stem}: height {h / MM:.1f} mm > 170 mm"
    lo, hi = font_range(fig)
    assert lo is None or lo >= MIN_PT - 1e-9, f"{stem}: text at {lo} pt < {MIN_PT} pt"
    assert hi is None or hi <= MAX_PT + 1e-9, f"{stem}: text at {hi} pt > {MAX_PT} pt"
    bad = coloured_text(fig)
    assert not bad, f"{stem}: coloured text {bad}"
    for ax in fig.axes:
        assert not ax.xaxis._major_tick_kw.get("gridOn", False) and not ax.yaxis._major_tick_kw.get("gridOn", False), \
            f"{stem}: gridlines"
    os.makedirs(os.path.dirname(stem) or ".", exist_ok=True)
    meta = {"CreationDate": None, "ModDate": None}
    fig.savefig(stem + ".pdf", metadata=meta)
    fig.savefig(stem + ".png", dpi=PNG_DPI)
    script = os.path.abspath(sys.argv[0]) if sys.argv and sys.argv[0] else None
    prov = {"figure": os.path.basename(stem), "size_mm": [round(w / MM, 1), round(h / MM, 1)],
            "font_pt": [lo, hi], "made": time.strftime("%Y-%m-%d %H:%M:%S"),
            "style_sha256": _sha(__file__),
            "script": os.path.basename(script) if script and os.path.exists(script) else None,
            "script_sha256": _sha(script) if script and os.path.exists(script) else None,
            "inputs": {p: _sha(p) for p in inputs if os.path.exists(p)}}
    with open(stem + ".prov.json", "w", encoding="utf-8") as f:
        json.dump(prov, f, indent=1)
    plt.close(fig)
    return [stem + ".pdf", stem + ".png"]
