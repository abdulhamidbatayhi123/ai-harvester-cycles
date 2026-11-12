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
    figs = set()
    for doc in ("main.tex", "si.tex"):
        tex = open(os.path.join(HERE, doc), encoding="utf-8").read()

        def flat(m):
            path = m.group(2)
            figs.add(path)
            return m.group(1) + "{" + os.path.basename(path) + "}"
        tex = re.sub(r"(\\includegraphics(?:\[[^\]]*\])?)\{([^}]*)\}", flat, tex)
        assert "../" not in re.sub(r"%.*", "", tex), f"{doc}: a relative path is left"
        open(os.path.join(OUT, doc), "w", encoding="utf-8", newline="\n").write(tex)
    for f in os.listdir(HERE):
        if f in ("ms_macros.tex", "refs_main.tex", "refs_si.tex") or (f.startswith("tab_") and f.endswith(".tex")):
            shutil.copy2(os.path.join(HERE, f), OUT)
    for p in sorted(figs):
        src = os.path.normpath(os.path.join(HERE, p))
        shutil.copy2(src, OUT)                                        # vector PDF, used by the LaTeX source
        png = os.path.splitext(src)[0] + ".png"
        tif = os.path.join(OUT, os.path.splitext(os.path.basename(src))[0] + ".tif")
        Image.open(png).save(tif, compression="tiff_lzw", dpi=(600, 600))
    toc = os.path.join(ROOT, "figures", "out", "fig_toc.png")
    Image.open(toc).save(os.path.join(OUT, "graphical_abstract.tif"), compression="tiff_lzw", dpi=(600, 600))
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
