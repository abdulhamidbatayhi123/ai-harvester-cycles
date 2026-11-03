"""Pre-freeze data checks of PREREG_P4 section 9. Data only; no model is fitted here.

Writes results/prefreeze/summary.json and summary.md with:
  1. dry mass of every step and isotherm run (activation stage found or not);
  2. isotherm end-points per sorbent and temperature;
  3. the test-retest noise floor F per sorbent and temperature (and per step type);
  4. mismatch between equilibrated step end-points and the isotherm at the same measured RH;
  5. the logged total gas flow per run (sccm), against the paper's 200 mL/min;
  6. two-pan pairs (runs sharing a start timestamp).

usage: python -I audit/prefreeze_checks.py data_derived/bezrukov2023 results/prefreeze
"""
import json, os, re, sys
from collections import defaultdict

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from p4.data import load_run, plateaus, end_value  # noqa: E402
from p4.physics import Branch  # noqa: E402
from p4.segments import dry_mass_step_run, noise_floor_pairs, step_segments  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")


def dry_mass_any(run):
    m, info = dry_mass_step_run(run)
    if m is not None:
        return m, "activation", info
    # fallback for runs without a heated activation: end of the first 0 % plateau
    for a, b in plateaus(run.rh_target):
        if run.rh_target[a] <= 0.5:
            return end_value(run.mass, run.t, a, b), "first-0%-plateau", {"end_time_min": float(run.t[b - 1])}
    return None, "none", {}


def total_flow(run):
    for k, h in run.meta.get("raw_columns_kept", {}).items():
        if "total gas flow" in h.lower():
            return k
    return None


def run_stamp(source):
    m = re.search(r"(\d{4}-\d{2}-\d{2} \d{2}-\d{2}-\d{2})", source)
    return m.group(1) if m else None


def main():
    src, out = sys.argv[1], sys.argv[2]
    os.makedirs(out, exist_ok=True)
    files = sorted(f for f in os.listdir(src) if f.endswith(".npz"))
    rep = {"runs": [], "isotherms": {}, "noise_floor": {}, "endpoint_mismatch": {}, "pairs": []}
    iso_runs, step_runs = [], []
    for f in files:
        run = load_run(os.path.join(src, f))
        z = np.load(os.path.join(src, f))
        fk = total_flow(run)
        flow = sorted(set(np.round(z[fk][np.isfinite(z[fk])], 0).tolist())) if fk else None
        m_dry, how, info = dry_mass_any(run) if run.kind in ("step", "isotherm") else (None, "n/a", {})
        rec = {"source": run.source, "sorbent": run.sorbent, "temp_dir": run.temp_dir, "kind": run.kind,
               "m_dry": m_dry, "dry_rule": how, "flow_sccm": flow, "stamp": run_stamp(run.source),
               "instrument": run.meta.get("Instrument Name"), "sample_number": run.meta.get("Sample Number")}
        rep["runs"].append(rec)
        if run.kind == "isotherm" and m_dry:
            iso_runs.append((run, m_dry))
        if run.kind == "step" and m_dry:
            step_runs.append((run, m_dry, info))
        del z
    # 2. isotherms: end-points of every plateau
    branches = {}
    for run, m_dry in iso_runs:
        pls = plateaus(run.rh_target)
        rh = [end_value(run.rh, run.t, a, b) for a, b in pls]
        w = [100 * (end_value(run.mass, run.t, a, b) - m_dry) / m_dry for a, b in pls]
        tgt = [float(run.rh_target[a]) for a, b in pls]
        top = int(np.argmax(tgt))
        key = f"{run.sorbent}|{run.temp_dir}|{os.path.basename(run.source)}"
        rep["isotherms"][key] = {"ads": [rh[: top + 1], w[: top + 1]], "des": [rh[top:], w[top:]], "m_dry": m_dry}
        branches.setdefault((run.sorbent, run.temp_dir), []).append(
            (run.source, Branch.from_points(rh[: top + 1], w[: top + 1]), Branch.from_points(rh[top:], w[top:])))
    # 3 and 4
    nf = defaultdict(list)
    mism = defaultdict(list)
    for run, m_dry, info in step_runs:
        segs = step_segments(run, m_dry, start_after_min=info.get("end_time_min"))
        for E, f_, to, n in noise_floor_pairs(segs):
            nf[(run.sorbent, run.temp_dir)].append({"E": E, "step": f"{f_}->{to}", "n": n, "run": run.source})
        isos = branches.get((run.sorbent, run.temp_dir))
        if not isos:
            continue
        _, ads, des = isos[0]
        for s in segs:
            n10 = max(5, len(s.w) // 10)
            tail = np.polyfit(s.t[-n10:], s.w[-n10:], 1)[0] * s.t[-1]
            dw = abs(s.w[-1] - s.w[0])
            if dw < 0.5 or abs(tail) > 0.02 * dw:      # keep only equilibrated plateaus
                continue
            rh_end = float(np.median(s.rh[-n10:]))
            br = ads if s.rh_to > s.rh_from else des
            mism[(run.sorbent, run.temp_dir)].append(
                {"rh": rh_end, "w_step": float(s.w[-1]), "w_iso": float(br.w_of_rh(rh_end)),
                 "diff": float(s.w[-1] - br.w_of_rh(rh_end)), "dir": "ads" if s.rh_to > s.rh_from else "des"})
    for k, v in nf.items():
        e = np.array([x["E"] for x in v])
        rep["noise_floor"]["|".join(k)] = {"median_E": float(np.median(e)), "p90_E": float(np.quantile(e, 0.9)),
                                           "n_pairs": len(v), "pairs": v}
    for k, v in mism.items():
        d = np.array([x["diff"] for x in v])
        rep["endpoint_mismatch"]["|".join(k)] = {"median_diff_wt%": float(np.median(d)),
                                                 "max_abs_diff_wt%": float(np.max(np.abs(d))), "n": len(v), "points": v}
    # 6. pairs
    by_stamp = defaultdict(list)
    for r in rep["runs"]:
        if r["stamp"]:
            by_stamp[(r["sorbent"], r["stamp"])].append(r["source"])
    rep["pairs"] = [v for v in by_stamp.values() if len(v) > 1]
    json.dump(rep, open(os.path.join(out, "summary.json"), "w", encoding="utf-8"), indent=1, default=float)
    # markdown digest
    L = ["# Pre-freeze data checks", "", "## Noise floor F (median normalised RMS between repeats)", "",
         "| Sorbent | T | median F | 90th pct | pairs |", "|---|---|---|---|---|"]
    for k, v in sorted(rep["noise_floor"].items()):
        s, T = k.split("|")
        L.append(f"| {s} | {T} | {v['median_E']:.4f} | {v['p90_E']:.4f} | {v['n_pairs']} |")
    L += ["", "## Step end-points minus isotherm at the same measured RH (wt%)", "",
          "| Sorbent | T | median | max abs | n |", "|---|---|---|---|---|"]
    for k, v in sorted(rep["endpoint_mismatch"].items()):
        s, T = k.split("|")
        L.append(f"| {s} | {T} | {v['median_diff_wt%']:+.2f} | {v['max_abs_diff_wt%']:.2f} | {v['n']} |")
    flows = defaultdict(int)
    for r in rep["runs"]:
        flows[str(r["flow_sccm"])] += 1
    L += ["", "## Logged total gas flow (sccm): number of runs", ""] + [f"- {k}: {v}" for k, v in sorted(flows.items())]
    rules = defaultdict(int)
    for r in rep["runs"]:
        if r["kind"] in ("step", "isotherm"):
            rules[(r["kind"], r["dry_rule"])] += 1
    L += ["", "## Dry-mass rule used", ""] + [f"- {k[0]}, {k[1]}: {v}" for k, v in sorted(rules.items())]
    L += ["", f"## Two-pan pairs: {len(rep['pairs'])} groups sharing a start timestamp"]
    open(os.path.join(out, "summary.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
