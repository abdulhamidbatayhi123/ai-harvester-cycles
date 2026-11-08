"""Second round of data-only pre-freeze checks, answering the Claude Science review of
2026-11-08 (hub message 20261108-1619-cs-to-cc-prereg-review.md). No model is fitted here.

  M10  per-plateau total gas flow of every step and cycling plateau in the primary set P;
  M5   cluster counts per sorbent and temperature (step files, two-pan sessions, segments);
  m10  whether any two-pan session combines different sorbents;
  M2   F_between: the same step compared across files (other pan, same session; and other
       sessions) of one sorbent and temperature, next to the within-file F;
  M8   isotherm-free check of the dry-mass rules: mass drift (% of m_dry per hour, linear fit
       over the last 10 min) and sample temperature at the end of the R1 and R2 windows;
  m1   E_own / F per stratum (B0 with its own k'', R2, results/prefreeze/reproduce_b0.json);
  m2   k'' coefficient of variation across the 8 sorbents, population and sample SD.

Runs are loaded one at a time (the machine is short of memory).

usage: python -I audit/prefreeze_checks2.py data_derived/bezrukov2023 results/prefreeze
"""
import itertools
import json
import os
import re
import sys
from collections import Counter, defaultdict

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from p4.data import PARENT, SORBENTS, data_files, load_run, plateaus  # noqa: E402
from p4.dataset import EXCLUDE_UNDRIED, _dry_mass  # noqa: E402
from p4.segments import DT_MIN, dry_mass_post_activation, dry_mass_step_run, is_scored, normalised_rms, step_segments  # noqa: E402

PRIMARY8 = ["ROS-037", "ROS-039", "ROS-040", "MOF-303", "MIL-160", "CAU-10", "Al-fumarate", "Syloid"]
MIN_DW = 0.05


def stamp(source):
    m = re.search(r"(\d{4}-\d{2}-\d{2} \d{2}-\d{2}-\d{2})", source)
    return m.group(1) if m else source


def flow_key(run):
    for k, h in run.meta.get("raw_columns_kept", {}).items():
        if "total gas flow" in h.lower():
            return k
    return None


def drift_at(run, t_lo, t_end, span=10.0):
    """Linear-fit slope of mass over [max(t_lo, t_end - span), t_end], in % of the end mass per hour,
    and the median sample temperature over the last minute."""
    sel = (run.t >= max(t_lo, t_end - span)) & (run.t <= t_end + 1e-9) & np.isfinite(run.mass)
    if sel.sum() < 3:
        return None, None, None
    t, m = run.t[sel], run.mass[sel]
    slope = np.polyfit(t, m, 1)[0]  # mg per min
    m_end = float(np.median(m[t >= t_end - 1.0]))
    last = sel & (run.t >= t_end - 1.0) & np.isfinite(run.temp)
    temp = float(np.median(run.temp[last])) if last.any() else None
    return float(100 * slope * 60 / m_end), float(t[-1] - t[0]), temp


def index(root):
    out = []
    for f in data_files(root):
        r = load_run(os.path.join(root, f))
        out.append({"path": os.path.join(root, f), "source": r.source, "kind": r.kind,
                    "sorbent": r.sorbent, "temp": r.temp_dir})
        del r
    return out


def in_P(rec):
    if rec["sorbent"] not in SORBENTS or rec["temp"] is None:
        return False
    if rec["kind"] == "step":
        return not rec["source"].startswith(EXCLUDE_UNDRIED)
    return rec["kind"] == "cycling" and rec["temp"] == "27C"


def med(x):
    x = [v for v in x if v is not None and np.isfinite(v)]
    return float(np.median(x)) if x else None


def main():
    root, out = sys.argv[1], sys.argv[2]
    idx = index(root)
    res = {"flow": {}, "clusters": {}, "two_pan_mixed_sorbents": [], "F_between": {}, "drift": {},
           "E_own_over_F": {}, "k2_cv": {}}

    # ---------- M10 flow per plateau, M5 clusters, M2 between-file pairs, M8 drift ----------
    flow_count = Counter()
    off400 = []
    stamp_sorbents = defaultdict(set)
    drift_rows = []
    groups_seg = defaultdict(list)   # (sorbent, T) -> list of (source, stamp, key, ordinal, w)
    for rec in idx:
        p_run = in_P(rec)
        dry_check = p_run and rec["kind"] == "step"
        iso_check = rec["kind"] == "isotherm" and rec["sorbent"] in SORBENTS
        if not (p_run or iso_check):
            continue
        run = load_run(rec["path"])
        # flow
        if p_run:
            fk = flow_key(run)
            z = np.load(rec["path"]) if fk else None
            fl = z[fk].astype(float) if fk else None
            t_dry = None
            if rec["kind"] == "step":
                m_dry, info = _dry_mass(run, "R2")
                t_dry = info.get("end_time_min")
            for k, (a, b) in enumerate(plateaus(run.rh_target)):
                if rec["kind"] == "step" and (k == 0 or (t_dry is not None and run.t[a] < t_dry)):
                    continue  # activation / dry reference, not a kinetic plateau
                if fl is None:
                    v = None
                else:
                    seg = fl[a:b][np.isfinite(fl[a:b])]
                    v = sorted(set(np.round(seg, 0).tolist())) if seg.size else None
                lab = str(v)
                flow_count[(rec["kind"], lab)] += 1
                if v != [400.0]:
                    off400.append({"run": rec["source"], "kind": rec["kind"], "plateau": k,
                                   "set_point": float(run.rh_target[a]), "flow_sccm": v})
            if z is not None:
                del z, fl
        if rec["kind"] == "step" and p_run:
            stamp_sorbents[stamp(rec["source"])].add(rec["sorbent"])
        # drift at the end of the R1 and R2 windows (step runs in P and isotherm runs)
        if dry_check or iso_check:
            row = {"run": rec["source"], "kind": rec["kind"], "sorbent": rec["sorbent"], "temp": rec["temp"]}
            m1, i1 = dry_mass_step_run(run)
            if m1 is not None:
                row["R1_drift_pct_h"], row["R1_fit_min"], row["R1_temp_C"] = drift_at(
                    run, i1["end_time_min"] - i1["activation_min"], i1["end_time_min"])
            m2, i2 = dry_mass_post_activation(run)
            if m2 is not None:
                row["R2_drift_pct_h"], row["R2_fit_min"], row["R2_temp_C"] = drift_at(
                    run, i2["end_time_min"] - i2["stretch_min"], i2["end_time_min"])
                row["R2_stretch_min"] = i2["stretch_min"]
            drift_rows.append(row)
        # segments for clusters and F_between
        if rec["kind"] == "step" and p_run:
            m_dry, info = _dry_mass(run, "R2")
            ordinal = Counter()
            for g in step_segments(run, m_dry, DT_MIN, start_after_min=info.get("end_time_min")):
                key = (round(g.rh_from, 1), round(g.rh_to, 1))
                ordinal[key] += 1
                if not is_scored(g):         # PREREG section 6 inclusion rule (review finding C1)
                    continue
                groups_seg[(rec["sorbent"], rec["temp"])].append(
                    (rec["source"], stamp(rec["source"]), key, ordinal[key], g.w.astype(np.float32),
                     float(abs(g.w[-1] - g.w[0]))))
        del run

    res["flow"] = {"plateaus_by_kind_and_flow": {f"{k}|{f}": n for (k, f), n in sorted(flow_count.items())},
                   "not_400_or_missing": off400}
    res["two_pan_mixed_sorbents"] = {s: sorted(v) for s, v in stamp_sorbents.items() if len(v) > 1}

    # clusters and F_between per group
    summ = json.load(open(os.path.join(out, "summary.json"), encoding="utf-8"))
    for (s, T), segs in sorted(groups_seg.items()):
        files = sorted({x[0] for x in segs})
        sess = sorted({x[1] for x in segs})
        res["clusters"][f"{s}|{T}"] = {
            "step_files": len(files), "two_pan_sessions": len(sess),
            "experiments": len({(x[1], x[2], x[3]) for x in segs}),
            "segments_up": sum(1 for x in segs if x[2][1] > x[2][0]),
            "segments_down": sum(1 for x in segs if x[2][1] < x[2][0]),
            # inference clusters of section 4: one RH step in one session
            "inference_clusters": len({(x[1], x[2]) for x in segs}),
            "abs_dw_wt_pct_quantiles_0_10_50_90_100": [float(q) for q in np.quantile([x[5] for x in segs], [0, .1, .5, .9, 1])],
            "files": files}
        pan, sesn = [], []
        by_key = defaultdict(list)
        for x in segs:
            if x[3] >= 2:          # from the second repeat on, as for the within-file F
                by_key[(x[2], x[3])].append(x)
        for (key, o), xs in by_key.items():
            for a, b in itertools.combinations(xs, 2):
                if a[0] == b[0]:
                    continue
                n = min(len(a[4]), len(b[4]))
                ea, eb = a[4][:n] - a[4][0], b[4][:n] - b[4][0]
                if abs(ea[-1]) < MIN_DW:
                    continue
                e = normalised_rms(ea.astype(float), eb.astype(float))
                (pan if a[1] == b[1] else sesn).append(e)
        F_w = summ["noise_floor"].get(f"{s}|{T}", {})
        res["F_between"][f"{s}|{T}"] = {
            "F_within": F_w.get("median_E"), "n_within": F_w.get("n_pairs"),
            "F_between_pan": med(pan), "n_pan": len(pan),
            "F_between_session": med(sesn), "n_session": len(sesn)}
        del segs
    # segment-weighted F per sorbent across temperatures
    wF = {}
    for s in SORBENTS:
        num = den = 0.0
        for T in ("27C", "60C"):
            c = res["clusters"].get(f"{s}|{T}")
            f = res["F_between"].get(f"{s}|{T}", {}).get("F_within")
            if c and f is not None:
                n = c["segments_up"] + c["segments_down"]
                num += n * f
                den += n
        if den:
            wF[s] = num / den
    res["F_within_segment_weighted"] = wF

    # drift summary
    res["drift"]["runs"] = drift_rows
    dsum = {}
    for key, rows in itertools.groupby(sorted(drift_rows, key=lambda r: (r["kind"], r["sorbent"], r["temp"])),
                                       key=lambda r: (r["kind"], r["sorbent"], r["temp"])):
        rows = list(rows)
        dsum["|".join(key)] = {
            "n": len(rows),
            "R1_drift_median": med([r.get("R1_drift_pct_h") for r in rows]),
            "R2_drift_median": med([r.get("R2_drift_pct_h") for r in rows]),
            "R1_temp_median": med([r.get("R1_temp_C") for r in rows]),
            "R2_temp_median": med([r.get("R2_temp_C") for r in rows]),
            "n_R2": sum(1 for r in rows if "R2_drift_pct_h" in r)}
    res["drift"]["summary"] = dsum

    # ---------- m1, m2 from reproduce_b0.json ----------
    rb = json.load(open(os.path.join(out, "reproduce_b0.json"), encoding="utf-8"))
    ratios = {}
    for r in rb["per_material"]:
        if r["sorbent"] not in PRIMARY8:
            continue
        F = summ["noise_floor"].get(f"{r['sorbent']}|{r['temp']}", {}).get("median_E")
        if F:
            ratios[f"{r['sorbent']}|{r['temp']}|{r['dir']}"] = r["E_own"] / F
    lo = min(ratios, key=ratios.get)
    hi = max(ratios, key=ratios.get)
    res["E_own_over_F"] = {"per_stratum": ratios, "min": [lo, ratios[lo]], "max": [hi, ratios[hi]],
                           "median": float(np.median(list(ratios.values())))}
    for T in ("27C", "60C"):
        for d in ("ads", "des"):
            k = np.array([r["k2_own"] for r in rb["per_material"]
                          if r["temp"] == T and r["dir"] == d and r["sorbent"] in PRIMARY8])
            res["k2_cv"][f"{T}|{d}"] = {"n": int(len(k)), "mean": float(k.mean()),
                                        "min": float(k.min()), "max": float(k.max()),
                                        "cv_population": float(k.std(ddof=0) / k.mean()),
                                        "cv_sample": float(k.std(ddof=1) / k.mean())}

    json.dump(res, open(os.path.join(out, "checks2.json"), "w", encoding="utf-8"), indent=1)
    write_md(res, os.path.join(out, "checks2.md"))


def f4(x):
    return "n/a" if x is None else f"{x:.4f}"


def f2(x):
    return "n/a" if x is None else f"{x:.2f}"


def write_md(res, path):
    L = ["# Pre-freeze checks, round 2 (data only)", "",
         "Answers the Claude Science review of 2026-11-08 (M2, M5, M8, M10, m1, m2, m10). Dry-mass rule R2.",
         "Made by audit/prefreeze_checks2.py; full numbers in checks2.json.", "",
         "## M10: total gas flow per plateau in P (sccm)", "",
         "Kinetic plateaus only: step runs after the dry reference, all plateaus of the 27 °C cycling runs.",
         "Plateau = run of constant set-point on the raw time base.", ""]
    for k, n in res["flow"]["plateaus_by_kind_and_flow"].items():
        L.append(f"- {k}: {n}")
    off = res["flow"]["not_400_or_missing"]
    L += ["", f"Plateaus not at 400 sccm or without a flow value: {len(off)}", ""]
    for o in off:
        L.append(f"- {o['run']} | plateau {o['plateau']} | set-point {o['set_point']:.1f} % | flow {o['flow_sccm']}")
    L += ["", "## M5, C1: clusters per sorbent and temperature (step runs in P; scored segments: |Δm| ≥ 0.05 mg "
          "with the sign of the RH step)", "",
          "| group | step files | two-pan sessions | inference clusters | up segments | down segments | "
          "|Δw| wt% min / 10 % / median / 90 % / max |",
          "|---|---|---|---|---|---|---|"]
    for g, c in res["clusters"].items():
        q = " / ".join(f"{v:.2f}" for v in c["abs_dw_wt_pct_quantiles_0_10_50_90_100"])
        L.append(f"| {g} | {c['step_files']} | {c['two_pan_sessions']} | {c['inference_clusters']} | "
                 f"{c['segments_up']} | {c['segments_down']} | {q} |")
    mix = res["two_pan_mixed_sorbents"]
    L += ["", "m10: two-pan sessions (shared start stamp) that combine different sorbents: "
          + ("none." if not mix else "; ".join(f"{s}: {', '.join(v)}" for s, v in mix.items())), ""]
    L += ["## M2: test-retest floor within a file against between files", "",
          "Same step and same repeat number (from the second repeat on), responses compared as changes",
          "from their own start (as for the within-file F). 'pan' = the other pan of the same session;",
          "'session' = a different session.", "",
          "| group | F within (n) | F between pans (n) | F between sessions (n) |", "|---|---|---|---|"]
    for g, f in res["F_between"].items():
        L.append(f"| {g} | {f4(f['F_within'])} ({f['n_within']}) | {f4(f['F_between_pan'])} ({f['n_pan']}) | "
                 f"{f4(f['F_between_session'])} ({f['n_session']}) |")
    L += ["", "Segment-weighted within-file F per sorbent (both temperatures): "
          + "; ".join(f"{s} {v:.4f}" for s, v in res["F_within_segment_weighted"].items()), ""]
    L += ["## M8: mass drift at the end of the dry-mass windows (isotherm-free)", "",
          "Slope of a linear fit over the last 10 min of each window, in % of m_dry per hour (negative = still",
          "losing mass); temperature = median sample temperature over the last minute.", "",
          "| kind | group | runs | R1 drift | R2 drift (runs) | R1 temp °C | R2 temp °C |", "|---|---|---|---|---|---|---|"]
    for k, d in res["drift"]["summary"].items():
        kind, s, T = k.split("|")
        L.append(f"| {kind} | {s} {T} | {d['n']} | {f2(d['R1_drift_median'])} | {f2(d['R2_drift_median'])} "
                 f"({d['n_R2']}) | {f2(d['R1_temp_median'])} | {f2(d['R2_temp_median'])} |")
    r1 = [abs(r["R1_drift_pct_h"]) for r in res["drift"]["runs"] if r.get("R1_drift_pct_h") is not None]
    r2 = [abs(r["R2_drift_pct_h"]) for r in res["drift"]["runs"] if r.get("R2_drift_pct_h") is not None]
    L += ["", f"All runs: median |drift| R1 {np.median(r1):.3f} %/h (n {len(r1)}, max {max(r1):.3f}); "
          f"R2 {np.median(r2):.3f} %/h (n {len(r2)}, max {max(r2):.3f}).", ""]
    e = res["E_own_over_F"]
    L += ["## m1: B0 with its own k'' against the noise floor (R2)", "",
          f"E_own / F over the 32 strata of the 8 sorbents: min {e['min'][1]:.1f} ({e['min'][0]}), "
          f"median {e['median']:.1f}, max {e['max'][1]:.1f} ({e['max'][0]}).", "",
          "## m2: k'' across the 8 sorbents (R2)", "",
          "| stratum | mean | range | CV (population SD) | CV (sample SD) |", "|---|---|---|---|---|"]
    for k, c in res["k2_cv"].items():
        L.append(f"| {k} | {c['mean']:.3f} | {c['min']:.3f} to {c['max']:.3f} | {c['cv_population']:.3f} | "
                 f"{c['cv_sample']:.3f} |")
    open(path, "w", encoding="utf-8").write("\n".join(L) + "\n")


if __name__ == "__main__":
    main()
