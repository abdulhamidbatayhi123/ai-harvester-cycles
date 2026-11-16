"""Build the AIChE Journal submission package (author guidelines read 2026-11-11: LaTeX accepted with a PDF of the
manuscript for review; no directory structure when referencing external files; figures as TIFF or EPS; line art at
600-1200 ppi; supporting files uploaded as "LaTeX Supplementary File").

Writes dist/aiche/ (git-ignored): main.tex and si.tex with every \\includegraphics path flattened to the bare file
name, ms_macros.tex, refs_main.tex, refs_si.tex, the generated tables, every figure as 600 dpi TIFF (from the
600 dpi PNG the figure style writes) plus the vector PDF, the graphical abstract, and the compiled main.pdf and
si.pdf, then compiles the flat copy with tectonic to prove it stands alone. Run after a passing
`python -I paper/tex/build_ms.py --final`.

usage: python -I paper/tex/package_aiche.py
"""
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
OUT = os.path.join(ROOT, "dist", "aiche")
sys.path.insert(0, HERE)
from build_ms import TECTONIC  # noqa: E402


def main():
    from PIL import Image
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)
    figs = {}                                   # source path -> submission name (Figure1..., FigureS1...), in order
    for doc, prefix in (("main.tex", "Figure"), ("si.tex", "FigureS")):
        tex = open(os.path.join(HERE, doc), encoding="utf-8").read()
        n = [0]

        def flat(m):
            path = m.group(2)
            n[0] += 1
            figs.setdefault(path, f"{prefix}{n[0]}")
            return m.group(1) + "{" + figs[path] + ".pdf}"
        tex = re.sub(r"(\\includegraphics(?:\[[^\]]*\])?)\{([^}]*)\}", flat, tex)
        assert "../" not in re.sub(r"%.*", "", tex), f"{doc}: a relative path is left"
        open(os.path.join(OUT, doc), "w", encoding="utf-8", newline="\n").write(tex)
    for f in os.listdir(HERE):
        if f in ("ms_macros.tex", "refs_main.tex", "refs_si.tex") or (f.startswith("tab_") and f.endswith(".tex")):
            shutil.copy2(os.path.join(HERE, f), OUT)
    # figures are named by their number in the article, so the uploaded files match the captions; the repository keeps
    # the script names (the figure_data.zip README maps them). TIFFs are saved as RGB: the PNGs' alpha is opaque.
    for p, name in figs.items():
        src = os.path.normpath(os.path.join(HERE, p))
        shutil.copy2(src, os.path.join(OUT, name + ".pdf"))           # vector PDF, used by the LaTeX source
        png = os.path.splitext(src)[0] + ".png"
        Image.open(png).convert("RGB").save(os.path.join(OUT, name + ".tif"), compression="tiff_lzw", dpi=(600, 600))
    toc = os.path.join(ROOT, "figures", "out", "fig_toc.png")
    Image.open(toc).convert("RGB").save(os.path.join(OUT, "graphical_abstract.tif"), compression="tiff_lzw",
                                        dpi=(600, 600))
    # numerical data of every figure (AIChE J. editorial doi:10.1002/aic.18017), listed in Supporting Note S5
    import zipfile
    figout = os.path.join(ROOT, "figures", "out")
    csvs = sorted(f for f in os.listdir(figout) if f.endswith(".data.csv"))
    need = {os.path.splitext(os.path.basename(p))[0] + ".data.csv" for p in figs if "fig_workflow" not in p}
    need.add("fig_toc.data.csv")
    assert need <= set(csvs), f"figure data missing: {sorted(need - set(csvs))}"
    readme = ("Numerical data of the figures (Supporting Note S5). One CSV per figure, written from the plotted artists.\n"
              "Columns: panel, series, x, y, x_label, y_label, x_tick_labels_if_categorical.\n"
              + "".join(f"{os.path.splitext(os.path.basename(p))[0]}.data.csv = {name.replace('Figure', 'Figure ')}\n"
                        for p, name in figs.items() if "fig_workflow" not in p)
              + "fig_toc.data.csv = graphical abstract. Figure 1 is a schematic without data.\n")
    with zipfile.ZipFile(os.path.join(OUT, "figure_data.zip"), "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("README.txt", readme)
        for f in sorted(need):
            z.write(os.path.join(figout, f), f)
    # documents for the submission form: metadata (public) and, when present on the author's machine, the cover letter
    # and the suggested reviewers (private/, never in git); the cover letter's internal draft heading is dropped
    shutil.copy2(os.path.join(ROOT, "docs", "submission", "aiche_metadata.md"), OUT)
    for f in ("cover_letter_aichej.md", "suggested_reviewers.md"):
        src = os.path.join(ROOT, "private", f)
        if os.path.exists(src):
            text = open(src, encoding="utf-8").read()
            if f.startswith("cover_letter") and text.startswith("# "):
                text = text.split("\n", 1)[1].lstrip("\n")
            open(os.path.join(OUT, f), "w", encoding="utf-8", newline="\n").write(text)
    for doc in ("main.tex", "si.tex"):
        r = subprocess.run([TECTONIC, "-X", "compile", doc], cwd=OUT, capture_output=True, text=True,
                           encoding="utf-8", errors="replace")
        if r.returncode:
            raise SystemExit(f"flat {doc} does not compile: {r.stderr[-800:]}")
    print("package:", OUT)
    for f in sorted(os.listdir(OUT)):
        print(f"  {f:40s} {os.path.getsize(os.path.join(OUT, f)) // 1024:8d} kB")


if __name__ == "__main__":
    main()
