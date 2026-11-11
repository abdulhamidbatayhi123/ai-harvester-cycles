"""Generate the LaTeX tables of the Paper 4 manuscript from the results files (build_ms.py gate G8 compares each
\\input{tab_*} file with a fresh generation, so a table can never drift from its source).

    python -I paper/tex/make_tables.py        # writes every table in TABLES next to this file
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
BS = chr(92)


def sig(x, n=2):
    """n significant figures, plain decimal (no exponent) for the magnitudes in these tables."""
    if x is None:
        return "--"
    if x == 0:
        return "0"
    from math import floor, log10
    d = max(n - 1 - int(floor(log10(abs(x)))), 0)
    return f"{x:.{d}f}"


def pval(p):
    if p is None:
        return "--"
    if p < 1e-3:
        m, e = f"{p:.1e}".split("e")
        return f"${m}" + BS + f"times10^{{{int(e)}}}$"
    return f"{p:.3f}" if p < 0.1 else f"{p:.2f}"


def ratio(x):
    return f"{x:.2f}" if x < 10 else f"{x:.0f}"


def kerr(x):
    """Largest relative error of the recovered k'' over the four strata, world N only (criterion 1), in %."""
    return "--" if x["k_err"] is None or x["model"] != "L1" else f"{100 * x['k_err']:.2f}"


def harness_rows():
    """One row per (round, world, held-out sorbent, model) of the learned-model harness (PREREG section 10)."""
    files = [(r, os.path.join(ROOT, "results", f"harness_round{r}", "harness.json")) for r in range(1, 8)]
    files.append(("7*", os.path.join(ROOT, "results", "harness_alfu", "harness.json")))
    rows = []
    for r, f in files:
        h = json.load(open(f, encoding="utf-8"))
        for key, v in h["cases"].items():
            world, held = key.split("|")
            k_err = max(abs(x) for x in v["k_rel_err"].values()) if world == "N" and v.get("k_rel_err") else None
            for kind in ("L1", "L2"):
                if kind not in v:
                    continue
                L = v[kind]
                eb = L.get("E_B0", L.get("E_b0"))
                rows.append({"round": str(r), "world": world, "held": held, "model": kind,
                             "E_model": L["E_model"], "E_B0": eb, "ratio": L["E_model"] / eb,
                             "p": L.get("p_signflip"), "beat": bool(L["beats_B0"]), "k_err": k_err})
    return rows


def tab_harness_l1():
    out = ["% written by paper/tex/make_tables.py from results/harness_round1-7/harness.json and "
           "results/harness_alfu/harness.json; do not edit",
           BS + "begin{longtable}{lllccccccc}",
           BS + "toprule",
           "Round & World & Held out & Model & $E$ model & $E$ B0 & Ratio & $p$ & Beat & $k''$ error (" + BS + "%)" + BS + BS,
           BS + "midrule", BS + "endhead"]
    for x in harness_rows():
        rnd = x["round"].replace("7*", "7" + BS + "textsuperscript{a}")
        out.append(f"{rnd} & {x['world']} & {x['held']} & {x['model']} & {sig(x['E_model'])} & {sig(x['E_B0'])} & "
                   f"{ratio(x['ratio'])} & {pval(x['p'])} & {'yes' if x['beat'] else 'no'} & {kerr(x)}" + BS + BS)
    out += [BS + "bottomrule", BS + "end{longtable}", ""]
    return "\n".join(out)


TABLES = {"tab_harness_l1.tex": tab_harness_l1}


def main():
    for name, fn in TABLES.items():
        with open(os.path.join(HERE, name), "w", encoding="utf-8", newline="\n") as f:
            f.write(fn())
        print("wrote", name)


if __name__ == "__main__":
    main()
