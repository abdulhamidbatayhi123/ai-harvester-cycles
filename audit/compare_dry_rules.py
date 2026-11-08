"""Data-only choice between two dry-mass rules (PREREG_P4 section 3.3): which rule makes the
equilibrated end-points of the step runs agree better with the isotherm at the same measured RH?
R1 = end of the heated activation; R2 = end of the first 0 % plateau after activation (same gas
and temperature as the rest of the run). Runs without activation use their first 0 % plateau
under both rules. No model is fitted.

usage: python -I audit/compare_dry_rules.py data_derived/bezrukov2023 results/prefreeze/dry_rules.json
"""
import json, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from p4.data import load_run, plateaus, end_value  # noqa: E402
from p4.physics import Branch  # noqa: E402
from p4.segments import dry_mass_step_run, dry_mass_post_activation, dry_mass_first_desorption, step_segments  # noqa: E402
from p4.dataset import ISOTHERM_CHOICE, EXCLUDE_UNDRIED  # noqa: E402
sys.stdout.reconfigure(encoding="utf-8")


def dry(run, rule):
    if rule in ("R2", "R3"):
        f = dry_mass_post_activation if rule == "R2" else dry_mass_first_desorption
        m, info = f(run)
        if m is not None:
            return m, info
    m, info = dry_mass_step_run(run)
    if m is not None:
        return m, {**info, "activation_end_min": info["end_time_min"]}
    for a, b in plateaus(run.rh_target):
        if run.rh_target[a] <= 0.5:
            return end_value(run.mass, run.t, a, b), {"end_time_min": float(run.t[b - 1])}
    return None, {}


def iso_branches(run, m, t_act):
    pls = [(a, b) for a, b in plateaus(run.rh_target) if run.t[a] >= t_act - 1e-6]
    rh = [end_value(run.rh, run.t, a, b) for a, b in pls]
    w = [100 * (end_value(run.mass, run.t, a, b) - m) / m for a, b in pls]
    tgt = [run.rh_target[a] for a, b in pls]
    top = int(np.argmax(tgt))
    return Branch.from_points(rh[: top + 1], w[: top + 1]), Branch.from_points(rh[top:], w[top:])


def main():
    src, out = sys.argv[1], sys.argv[2]
    runs = [load_run(os.path.join(src, f)) for f in sorted(os.listdir(src)) if f.endswith(".npz")]
    res = {}
    for rule in ("R1", "R2", "R3"):
        diffs = {}
        for s in sorted({r.sorbent for r in runs if r.sorbent}):
            for T in ("27C", "60C"):
                isos = [r for r in runs if r.kind == "isotherm" and r.sorbent == s and r.temp_dir == T]
                ch = ISOTHERM_CHOICE.get((s, T))
                if ch == "LATEST":
                    isos = sorted(isos, key=lambda r: r.source)[-1:]
                elif ch:
                    isos = [r for r in isos if ch in r.source]
                steps = [r for r in runs if r.kind == "step" and r.sorbent == s and r.temp_dir == T
                         and not r.source.startswith(EXCLUDE_UNDRIED)]
                if len(isos) != 1 or not steps:
                    continue
                mi, info_i = dry(isos[0], rule)
                ads, des = iso_branches(isos[0], mi, info_i.get("activation_end_min", -np.inf))
                d = []
                for r in steps:
                    m, info = dry(r, rule)
                    for g in step_segments(r, m, start_after_min=info.get("end_time_min")):
                        n10 = max(5, len(g.w) // 10)
                        dw = abs(g.w[-1] - g.w[0])
                        tail = np.polyfit(g.t[-n10:], g.w[-n10:], 1)[0] * g.t[-1]
                        if dw < 0.5 or abs(tail) > 0.02 * dw:
                            continue
                        rh = float(np.median(g.rh[-n10:]))
                        br = ads if g.rh_to > g.rh_from else des
                        d.append(float(g.w[-1] - br.w_of_rh(rh)))
                if d:
                    diffs[f"{s}|{T}"] = {"median": float(np.median(d)), "median_abs": float(np.median(np.abs(d))), "n": len(d)}
        allabs = [v["median_abs"] for v in diffs.values()]
        res[rule] = {"per_group": diffs, "median_of_group_median_abs": float(np.median(allabs)),
                     "max_group_median_abs": float(np.max(allabs))}
        print(rule, "median over groups of median |end-point - isotherm| =", round(res[rule]["median_of_group_median_abs"], 3),
              "wt%; worst group", round(res[rule]["max_group_median_abs"], 3))
    for k in res["R1"]["per_group"]:
        cells = []
        for rule in ("R1", "R2", "R3"):
            v = res[rule]["per_group"].get(k, {})
            cells.append(f"{rule} |{v.get('median_abs', float('nan')):.2f}|")
        print(f"  {k:24s} " + "  ".join(cells))
    json.dump(res, open(out, "w"), indent=1)


if __name__ == "__main__":
    main()
