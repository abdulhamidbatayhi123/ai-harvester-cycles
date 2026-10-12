"""Time constants and repeatability of RH step responses in DVS kinetics exports.

For every plateau of target RH in a file, take the mass trace from the step to the end of the
plateau and report: the step (RH from -> to), plateau length, total mass change, the time to
63 % of that change (t63), the number of samples inside t63, and whether the plateau ended
near equilibrium (last-10 % slope small relative to the mean slope). Nothing is fitted.

usage: python -I step_response.py <data.zip> <out.jsonl> <name-substring> [...]
"""
import json, sys, zipfile

import numpy as np

sys.path.insert(0, __file__.rsplit("\\", 1)[0].rsplit("/", 1)[0])
from inventory_dvs import rows_xls, rows_xlsx, num, find  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")


def load(name, blob):
    nrows, row, col, book = (rows_xlsx if name.lower().endswith(".xlsx") else rows_xls)(blob)
    hdr_i = next(i for i in range(min(nrows, 80)) if str((row(i) or [""])[0]).strip().lower().startswith("time"))
    header = [str(h).strip() for h in row(hdr_i)]
    j_m = find(header, "mass [mg]") if find(header, "mass [mg]") is not None else find(header, "mass")
    j_rht = find(header, "target", "partial pressure") or find(header, "target", "rh") or find(header, "target", "p/po")
    g = lambda j: np.array([num(v) for v in col(j, hdr_i + 1)])
    t, m, r = g(0), g(j_m), g(j_rht)
    if book is not None:
        book.release_resources()
    ok = ~(np.isnan(t) | np.isnan(m) | np.isnan(r))
    return t[ok], m[ok], r[ok]


def steps(t, m, r, tol=0.5):
    edges = np.flatnonzero(np.abs(np.diff(r)) > tol) + 1
    bounds = np.r_[0, edges, len(r)]
    out = []
    for k in range(1, len(bounds) - 1):
        a, b = bounds[k], bounds[k + 1]
        if b - a < 20:
            continue
        tt, mm = t[a:b] - t[a], m[a:b]
        dm = mm[-1] - mm[0]
        if abs(dm) < 1e-3:
            continue
        frac = (mm - mm[0]) / dm
        i63 = int(np.argmax(frac >= 0.632))
        n10 = max(3, (b - a) // 10)
        tail = abs(np.polyfit(tt[-n10:], mm[-n10:], 1)[0]) * (tt[-1])
        out.append({
            "rh_from": float(r[a - 1]), "rh_to": float(r[a]),
            "plateau_min": float(tt[-1]), "dm_mg": float(dm), "m0_mg": float(mm[0]),
            "t63_min": float(tt[i63]), "samples_in_t63": int(i63),
            "dt_s": float(np.median(np.diff(tt)) * 60),
            "tail_slope_ratio": float(tail / abs(dm)),
        })
    return out


def main():
    z = zipfile.ZipFile(sys.argv[1])
    subs = sys.argv[3:]
    with open(sys.argv[2], "a", encoding="utf-8") as fh:
        for n in [i.filename for i in z.infolist() if i.filename.lower().endswith((".xls", ".xlsx"))]:
            if not any(s in n for s in subs):
                continue
            t, m, r = load(n, z.read(n))
            for s in steps(t, m, r):
                s["file"] = n
                fh.write(json.dumps(s) + "\n")
            print("done", n, flush=True)


if __name__ == "__main__":
    main()
