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


def num(s):
    """A formatted number in math mode, so a negative value prints with a true minus sign."""
    return f"${s}$"


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


def tab_harness_b2():
    """B2 harness per world (PREREG section 10b), from results/harness_b2/report.json."""
    rep = json.load(open(os.path.join(ROOT, "results", "harness_b2", "report.json"), encoding="utf-8"))
    order = ["N", "K", "K2a", "K2b", "K2c", "S0", "S1", "S2", "S3", "S4", "S5", "C3"]
    role = {"N": "no effect", "K": "plumbing", "K2a": "realistic power", "K2b": "realistic power",
            "K2c": "realistic power", "C3": "form error"}
    strata = ["27C|ads", "27C|des", "60C|ads", "60C|des"]
    out = ["% written by paper/tex/make_tables.py from results/harness_b2/report.json; do not edit",
           BS + "begin{tabular}{llcccccccc}", BS + "toprule",
           " & & Folds & & & & " + BS + "multicolumn{4}{c}{Median fitted $b$}" + BS + BS,
           BS + "cmidrule(l){7-10}",
           "World & Role & beaten & Median $r$ & $E$ B0 & $E$ B2 & 27 ads & 27 des & 60 ads & 60 des" + BS + BS,
           BS + "midrule"]
    for w in order:
        v = rep["worlds"][w]
        b = [num(f"{v['median_b'][s]:.2f}") for s in strata]
        out.append(f"{w} & {role.get(w, 'null')} & {v['beats']}/{v['folds']} & {num(format(v['median_r'], '.3f'))} & "
                   f"{sig(v['median_E_B0'])} & {sig(v['median_E_B2'])} & " + " & ".join(b) + BS + BS)
    out += [BS + "bottomrule", BS + "end{tabular}", ""]
    return "\n".join(out)


CONFIRM = os.environ.get("P4_CONFIRM_DIR", os.path.join(ROOT, "results"))   # smoke tests point this elsewhere
ORDER = ["MOF-303", "MIL-160", "CAU-10", "Al-fumarate", "ROS-039", "ROS-040", "ROS-037", "Syloid"]
LABEL = {"CAU-10": "CAU-10-H", "Syloid": "Syloid AL-1"}


def _dec(rule):
    return json.load(open(os.path.join(CONFIRM, f"confirm_{rule}", "decide.json"), encoding="utf-8"))


def _rows(rule):
    p = os.path.join(CONFIRM, f"confirm_{rule}", "rows.jsonl")
    return {r["fold"]: r for r in map(json.loads, open(p, encoding="utf-8")) if r["key"].endswith("|physics")}


def _r(v):
    import math
    r = v["r_fold"]
    if r is None:
        return "--"
    if not math.isfinite(r):
        return "$-" + BS + "infty$"
    s = f"{100 * r:.1f}"
    return num("0.0" if s == "-0.0" else s)          # a value that rounds to zero carries no sign


def share(v, p):
    """Share of the oracle's gain that B2 achieves (decide field share_of_oracle_gain; descriptive). Printed only
    where the oracle gains at all (median E of B0* below B0's); otherwise the ratio has no meaning and '--' is shown
    (the caption says so)."""
    import numpy as np
    x = v.get("share_of_oracle_gain")
    e0, es = (float(np.nanmedian(np.asarray(p["E"][k], float))) for k in ("B0", "B0star"))
    # below a 5 % oracle gain the ratio's denominator is near zero and the share means nothing (review round 2)
    return "--" if x is None or not es < 0.95 * e0 else num(f"{x:.2f}")


def tab_h4a():
    """H4a' per LOSO fold under R2 and R1 (PREREG section 7), from the confirmatory decide outputs."""
    import numpy as np
    d2, d1, rows = _dec("R2"), _dec("R1"), _rows("R2")
    ext = json.load(open(os.path.join(ROOT, "results", "extrapolation_flags.json"), encoding="utf-8"))["flags"]
    out = ["% written by paper/tex/make_tables.py from results/confirm_R2|R1/decide.json and rows.jsonl; do not edit",
           BS + "begin{tabular}{lcccccccccc}", BS + "toprule",
           " & " + BS + "multicolumn{2}{c}{$r$ (" + BS + "%)} & " + BS + "multicolumn{2}{c}{Beaten} & "
           + BS + "multicolumn{3}{c}{Median $E$ (R2)} & & " + BS + BS,
           BS + "cmidrule(lr){2-3}" + BS + "cmidrule(lr){4-5}" + BS + "cmidrule(lr){6-8}",
           "Held out & R2 & R1 & R2 & R1 & B0 & B2 & B0* & Share & Extrap." + BS + BS, BS + "midrule"]
    # every fold used the plain variant (asserted, so the caption's statement stays true)
    assert all(rows[f"LOSO:{s}"]["B0_variant"] == "B0" for s in ORDER if f"LOSO:{s}" in rows)
    for s in ORDER:
        k = f"LOSO:{s}"
        a, b, p = d2["folds"].get(k + "|B2"), d1["folds"].get(k + "|B2"), rows.get(k)
        if a is None or b is None or p is None:
            continue
        med = lambda key: sig(float(np.nanmedian(np.asarray(p["E"][key], float))))
        fl = ", ".join(f"{x['temp'][:2]}" for x in ext.get(k, []))
        out.append(f"{LABEL.get(s, s)} & {_r(a)} & {_r(b)} & {'yes' if a['beats_B0'] else 'no'} & "
                   f"{'yes' if b['beats_B0'] else 'no'} & {med('B0')} & {med('B2')} & {med('B0star')} & {share(a, p)} & {fl or '--'}"
                   + BS + BS)
    out += [BS + "bottomrule", BS + "end{tabular}", ""]
    return "\n".join(out)


def tab_h4c():
    """H4c (PREREG section 7): for each sorbent of the two non-trivial LOFO folds, median E of B0 and B2 in its
    LOFO fold against its LOSO fold (R2; pooled over the sorbent's own segments; descriptive, no test)."""
    import numpy as np
    rows = _rows("R2")
    out = ["% written by paper/tex/make_tables.py from results/confirm_R2/rows.jsonl; do not edit",
           BS + "begin{tabular}{llcccc}", BS + "toprule",
           " & & " + BS + "multicolumn{2}{c}{B0} & " + BS + "multicolumn{2}{c}{B2}" + BS + BS,
           BS + "cmidrule(lr){3-4}" + BS + "cmidrule(lr){5-6}",
           "Family fold & Sorbent & LOSO & LOFO & LOSO & LOFO" + BS + BS, BS + "midrule"]

    def own(p, s, key):
        seg = [x.split("|")[0] for x in p["seg"]]
        e = np.asarray(p["E"][key], float)
        sel = np.array([x == s for x in seg])
        return float(np.nanmedian(e[sel])) if sel.any() else None

    for fam in ("LOFO:Al-rod", "LOFO:Zn-triazolate-F"):
        pf = rows.get(fam)
        if pf is None:
            continue
        for s in pf["held"]:
            parent = s.replace("_composite", "")
            pl = rows.get(f"LOSO:{parent}")
            if pl is None:
                continue
            name = LABEL.get(parent, parent) + (" composite" if s.endswith("_composite") else "")
            vals = [own(pl, s, "B0"), own(pf, s, "B0"), own(pl, s, "B2"), own(pf, s, "B2")]
            out.append(f"{fam.split(':')[1]} & {name} & " + " & ".join(sig(v) for v in vals) + BS + BS)
    out += [BS + "bottomrule", BS + "end{tabular}", ""]
    return "\n".join(out)


def tab_secondary():
    """Strata (PREREG section 6) and secondary metrics (time-to-63 % error, E truncated at 5 t63), B0, B2 and B0*,
    under R2 and R1, from results/confirm_summary.json (secondary_metrics_<rule>.json via the summary)."""
    s = json.load(open(os.path.join(ROOT, "results", "confirm_summary.json"), encoding="utf-8"))
    sec = s["exploratory_and_secondary"]
    out = ["% written by paper/tex/make_tables.py from results/confirm_summary.json; do not edit",
           BS + "begin{tabular}{llcccccc}", BS + "toprule",
           " & & " + BS + "multicolumn{3}{c}{R2} & " + BS + "multicolumn{3}{c}{R1}" + BS + BS,
           BS + "cmidrule(lr){3-5}" + BS + "cmidrule(lr){6-8}",
           "Quantity & Subset & B0 & B2 & B0* & B0 & B2 & B0*" + BS + BS, BS + "midrule"]
    names = {"27C|ads": "27 \\textdegree C, uptake", "27C|des": "27 \\textdegree C, release",
             "60C|ads": "60 \\textdegree C, uptake", "60C|des": "60 \\textdegree C, release"}
    for k, lab in names.items():
        a, b = s["R2"]["strata"][k], s["R1"]["strata"][k]
        out.append(f"Median $E$ & {lab} (n = {a['n_seg']}) & {sig(a['E_B0'])} & {sig(a['E_B2'])} & -- & "
                   f"{sig(b['E_B0'])} & {sig(b['E_B2'])} & --" + BS + BS)
    a, b = sec["secondary_R2"], sec["secondary_R1"]
    out.append(f"$t_{{63}}$ relative error & all held-out segments & {a['t63_B0']:.3f} & {a['t63_B2']:.3f} & "
               f"{a['t63_B0star']:.3f} & {b['t63_B0']:.3f} & {b['t63_B2']:.3f} & {b['t63_B0star']:.3f}" + BS + BS)
    out.append(f"$E$ to $5\\,t_{{63}}$ & all held-out segments & {sig(a['Etr_B0'])} & {sig(a['Etr_B2'])} & "
               f"{sig(a['Etr_B0star'])} & {sig(b['Etr_B0'])} & {sig(b['Etr_B2'])} & {sig(b['Etr_B0star'])}" + BS + BS)
    out += [BS + "bottomrule", BS + "end{tabular}", ""]
    return "\n".join(out).replace("\\\\textdegree", BS + "textdegree")


TABLES = {"tab_harness_l1.tex": tab_harness_l1, "tab_harness_b2.tex": tab_harness_b2,
          "tab_h4a.tex": tab_h4a, "tab_h4c.tex": tab_h4c, "tab_secondary.tex": tab_secondary}


def main():
    for name, fn in TABLES.items():
        try:
            text = fn()
        except FileNotFoundError as e:          # confirmatory results not there yet
            print("skipped", name, "(missing input:", os.path.relpath(e.filename, ROOT) + ")")
            continue
        with open(os.path.join(HERE, name), "w", encoding="utf-8", newline="\n") as f:
            f.write(text)
        print("wrote", name)


if __name__ == "__main__":
    main()
