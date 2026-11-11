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
  provenance file with the SHA-256 of the drawing script, this module and every input
  (repository-relative paths, text LF-normalised) and the list of those files that git sees as
  uncommitted (the manuscript build refuses a figure drawn from uncommitted files).

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
import re
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


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEXT_EXT = (".py", ".json", ".jsonl", ".csv", ".md", ".txt", ".tex")
SUB_MIN_PT = 5.0   # mathtext prints sub- and superscripts at 70 % of the text size; the manuscript build (G2c) refuses printed text below 5 pt


def _sha(path):
    """SHA-256 of a file; text files with line endings normalised to LF, so a Windows checkout
    (CRLF) and the repository blob give the same hash (lessons file, section 10)."""
    with open(path, "rb") as f:
        b = f.read()
    if path.lower().endswith(TEXT_EXT):
        b = b.replace(b"\r\n", b"\n")
    return hashlib.sha256(b).hexdigest()


def _rel(path):
    """Repository-relative path with forward slashes (the provenance must not name the machine)."""
    p = os.path.abspath(path)
    try:
        return os.path.relpath(p, ROOT).replace(os.sep, "/")
    except ValueError:
        return p.replace(os.sep, "/")


def _git_dirty(paths):
    """Files among `paths` with uncommitted changes or untracked (None if git is unavailable)."""
    import subprocess
    try:
        r = subprocess.run(["git", "-C", ROOT, "status", "--porcelain", "--"] + [_rel(p) for p in paths],
                           capture_output=True, text=True, timeout=60)
    except (OSError, subprocess.SubprocessError):
        return None
    if r.returncode:
        return None
    return sorted(ln[3:].strip() for ln in r.stdout.splitlines() if ln.strip())


def small_scripts(fig):
    """Visible mathtext with a sub- or superscript whose script would print below SUB_MIN_PT."""
    from matplotlib.text import Text
    out = []
    for t in fig.findobj(Text):
        s = t.get_text()
        if t.get_visible() and "$" in s and re.search(r"[_^]", s) and 0.7 * t.get_fontsize() < SUB_MIN_PT - 1e-9:
            out.append(s[:30])
    return out


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
    small = small_scripts(fig)
    assert not small, f"{stem}: sub- or superscripts below {SUB_MIN_PT} pt {small}"
    for ax in fig.axes:
        assert not ax.xaxis._major_tick_kw.get("gridOn", False) and not ax.yaxis._major_tick_kw.get("gridOn", False), \
            f"{stem}: gridlines"
    os.makedirs(os.path.dirname(stem) or ".", exist_ok=True)
    meta = {"CreationDate": None, "ModDate": None}
    fig.savefig(stem + ".pdf", metadata=meta)
    fig.savefig(stem + ".png", dpi=PNG_DPI)
    script = os.path.abspath(sys.argv[0]) if sys.argv and sys.argv[0] else None
    have = bool(script and os.path.exists(script))
    missing = [p for p in inputs if not os.path.exists(p)]
    assert not missing, f"{stem}: inputs not found {missing}"
    # data_raw/ and data_derived/ are third-party data kept out of git by design: hashed, not git-checked
    tracked = [__file__] + ([script] if have else []) + [
        p for p in inputs if not _rel(p).startswith(("data_raw/", "data_derived/"))]
    prov = {"figure": os.path.basename(stem), "size_mm": [round(w / MM, 1), round(h / MM, 1)],
            "font_pt": [lo, hi], "made": time.strftime("%Y-%m-%d %H:%M:%S"),
            "hash": "sha256, text files LF-normalised",
            "style": _rel(__file__), "style_sha256": _sha(__file__),
            "script": _rel(script) if have else None,
            "script_sha256": _sha(script) if have else None,
            "inputs": {_rel(p): _sha(p) for p in inputs},
            "git_dirty_files": _git_dirty(tracked)}
    with open(stem + ".prov.json", "w", encoding="utf-8") as f:
        json.dump(prov, f, indent=1)
    plt.close(fig)
    return [stem + ".pdf", stem + ".png"]
