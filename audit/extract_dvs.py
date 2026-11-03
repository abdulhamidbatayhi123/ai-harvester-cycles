"""Convert every DVS export in the Bezrukov et al. 2023 archive to a compact .npz once.

For each .xls/.xlsx in the zip, writes <out>/<path with / replaced by __>.npz holding the
columns time_min, mass_mg, rh_target, rh_actual, temp_target, temp_sample (NaN where the
instrument has no such column), and a JSON string `meta` with every key/value row of the
header block plus the original column names. Values are copied, not transformed: RH stays in
the instrument's own unit (percent, or fraction for the DVS Vacuum files), and that unit is
recorded in meta["rh_unit"].

usage: python -I extract_dvs.py <data.zip> <out_dir>
"""
import gc, io, json, os, sys, zipfile

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from inventory_dvs import rows_xls, rows_xlsx, num, find  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")


def scalar(v):
    if hasattr(v, "isoformat"):
        return v.isoformat()
    if isinstance(v, float) and v != v:
        return None
    return v


def extract(name, blob):
    nrows, row, col, book = (rows_xlsx if name.lower().endswith(".xlsx") else rows_xls)(blob)
    meta, hdr_i = {}, None
    for i in range(min(nrows, 80)):
        r = row(i)
        first = str(r[0]).strip() if r and r[0] is not None else ""
        if first.lower().startswith("time"):
            hdr_i = i
            break
        vals = [scalar(x) for x in (r[1:6] if r else []) if x not in (None, "")]
        if first:
            meta[first.rstrip(":")] = vals[0] if len(vals) == 1 else vals
    meta["instrument_file_type"] = str(row(0)[0]).strip()
    header = [str(h).strip() for h in row(hdr_i)]
    meta["columns"] = header
    cols = {
        "mass_mg": find(header, "mass [mg]") if find(header, "mass [mg]") is not None else find(header, "mass"),
        "rh_target": find(header, "target", "partial pressure") or find(header, "target", "rh") or find(header, "target", "p/po"),
        "rh_actual": find(header, "measured", "partial pressure") or find(header, "actual", "rh") or find(header, "actual", "p/po") or find(header, "measured", "rh"),
        "temp_target": find(header, "target", "sample temp") or find(header, "target", "incubator temp") or find(header, "target", "temp"),
        "temp_sample": find(header, "sorption temp") or find(header, "actual", "temp") or find(header, "measured", "sample temp") or find(header, "measured", "temp"),
    }
    meta["columns_used"] = {k: (header[j] if j is not None else None) for k, j in cols.items()}
    rh_name = (meta["columns_used"]["rh_target"] or "").lower()
    meta["rh_unit"] = "fraction" if "/100" in rh_name else "percent"
    t = np.array([num(v) for v in col(0, hdr_i + 1)])
    ok = ~np.isnan(t)
    out = {"time_min": t[ok]}
    for k, j in cols.items():
        out[k] = np.array([num(v) for v in col(j, hdr_i + 1)])[ok] if j is not None else np.full(ok.sum(), np.nan)
    # Also keep every other numeric column verbatim as c<index> (names in meta["columns"]), so
    # instrument-computed quantities such as "dm (%) - ref" or a flow reading are not lost.
    kept = []
    for j in range(1, len(header)):
        if not header[j] or header[j].lower() == "none":
            continue
        a = np.array([num(v) for v in col(j, hdr_i + 1)])[ok]
        if np.isfinite(a).any():
            out[f"c{j:02d}"] = a
            kept.append(j)
    meta["raw_columns_kept"] = {f"c{j:02d}": header[j] for j in kept}
    if book is not None:
        book.release_resources()
    return out, meta


def main():
    z = zipfile.ZipFile(sys.argv[1])
    out_dir = sys.argv[2]
    os.makedirs(out_dir, exist_ok=True)
    names = [i.filename for i in z.infolist() if i.filename.lower().endswith((".xls", ".xlsx"))]
    for k, n in enumerate(names):
        dst = os.path.join(out_dir, n.replace("/", "__") + ".npz")
        if os.path.exists(dst):
            continue
        arrays, meta = extract(n, z.read(n))
        meta["source_file"] = n
        np.savez_compressed(dst + ".tmp.npz", meta=json.dumps(meta, default=str), **arrays)
        os.replace(dst + ".tmp.npz", dst)
        print(f"[{k + 1}/{len(names)}] {len(arrays['time_min'])} rows {n}", flush=True)
        gc.collect()


if __name__ == "__main__":
    main()
