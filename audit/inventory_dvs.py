"""Summarise every DVS export (.xls/.xlsx) in the Bezrukov et al. 2023 archive.

Reads the zip in place, one file at a time, and writes one JSON line per export with the
instrument, sample, sampling interval, duration, the programme of target RH and temperature,
and the measured ranges. Nothing is fitted; this is an inventory.

usage: python -I inventory_dvs.py <data.zip> <out.jsonl> [name-substring ...]
"""
import gc, io, json, sys, time, zipfile

import numpy as np
import openpyxl
import psutil
import xlrd

sys.stdout.reconfigure(encoding="utf-8")


def rows_xls(blob):
    book = xlrd.open_workbook(file_contents=blob, on_demand=True)
    sh = book.sheet_by_name("DVS Data")
    return sh.nrows, (lambda i: sh.row_values(i)), (lambda j, start: sh.col_values(j, start)), book


def rows_xlsx(blob):
    wb = openpyxl.load_workbook(io.BytesIO(blob), read_only=True, data_only=True)
    ws = wb["DVS Data"]
    rows = [list(r) for r in ws.iter_rows(values_only=True)]
    wb.close()
    return len(rows), (lambda i: rows[i]), (lambda j, start: [r[j] if j < len(r) else None for r in rows[start:]]), None


def num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return np.nan


def find(header, *keys):
    for j, h in enumerate(header):
        hs = str(h).lower()
        if all(k in hs for k in keys):
            return j
    return None


def plateaus(x, tol=0.5):
    """Collapse a setpoint series into its sequence of distinct plateaus."""
    out = []
    for v in x:
        if np.isnan(v):
            continue
        if not out or abs(v - out[-1][0]) > tol:
            out.append([v, 1])
        else:
            out[-1][1] += 1
    return out


def summarise(name, blob):
    nrows, row, col, book = (rows_xlsx if name.lower().endswith(".xlsx") else rows_xls)(blob)
    meta, hdr_i = {}, None
    for i in range(min(nrows, 80)):
        r = row(i)
        first = str(r[0]).strip() if r else ""
        if first.lower().startswith("time"):
            hdr_i = i
            break
        if first and len(r) > 1 and r[1] not in (None, ""):
            meta[first.rstrip(":")] = r[1] if not hasattr(r[1], "isoformat") else r[1].isoformat()
    instrument = str(row(0)[0]).strip()
    if hdr_i is None:
        return {"file": name, "error": "no header row", "instrument": instrument}
    header = [str(h).strip() for h in row(hdr_i)]
    j_t = 0
    j_m = find(header, "mass [mg]") if find(header, "mass [mg]") is not None else find(header, "mass")
    j_dm = find(header, "delta mass") if find(header, "delta mass") is not None else find(header, "change in mass")
    j_rht = find(header, "target", "partial pressure") or find(header, "target", "rh") or find(header, "target", "p/po")
    j_rha = find(header, "measured", "partial pressure") or find(header, "actual", "rh") or find(header, "actual", "p/po") or find(header, "measured", "rh")
    j_tt = find(header, "target", "temp") if find(header, "target", "sample temp") is None else find(header, "target", "sample temp")
    j_ts = (find(header, "sorption temp") or find(header, "actual", "temp")
            or find(header, "measured", "sample temp") or find(header, "measured", "temp"))
    get = lambda j: np.array([num(v) for v in col(j, hdr_i + 1)]) if j is not None else None
    t = get(j_t)
    ok = ~np.isnan(t)
    t = t[ok]
    sel = lambda j: (get(j)[ok] if j is not None else None)
    m, dm, rht, rha, tt, ts = (sel(j) for j in (j_m, j_dm, j_rht, j_rha, j_tt, j_ts))
    if book is not None:
        book.release_resources()
    dt = np.diff(t) * 60.0
    rh_pl = plateaus(rht) if rht is not None else []
    t_pl = plateaus(tt, tol=1.0) if tt is not None else []
    rh_seq = [round(p[0], 1) for p in rh_pl]
    ups = sum(1 for a, b in zip(rh_seq, rh_seq[1:]) if b > a)
    downs = sum(1 for a, b in zip(rh_seq, rh_seq[1:]) if b < a)
    dwell = [p[1] for p in rh_pl]
    med_dt = float(np.median(dt)) if dt.size else np.nan
    rng = lambda a: [float(np.nanmin(a)), float(np.nanmax(a))] if a is not None and np.isfinite(a).any() else None
    return {
        "file": name,
        "instrument": instrument,
        "sample": meta.get("Sample Name") or meta.get("Sample Name"),
        "method": meta.get("Method Name"),
        "sequence": meta.get("Sequence Name"),
        "initial_mass_mg": num(meta.get("Initial Mass [mg]", meta.get("Initial Mass"))),
        "save_interval_s": num(meta.get("Data Saving Interval [seconds]")),
        "columns": header[:20],
        "cols_used": {"mass": header[j_m] if j_m is not None else None,
                      "rh_target": header[j_rht] if j_rht is not None else None,
                      "rh_actual": header[j_rha] if j_rha is not None else None,
                      "temp_target": header[j_tt] if j_tt is not None else None,
                      "temp_sample": header[j_ts] if j_ts is not None else None},
        "n_points": int(t.size),
        "duration_min": float(t[-1] - t[0]) if t.size else 0.0,
        "median_dt_s": med_dt,
        "rh_target_plateaus": len(rh_seq),
        "rh_target_up_steps": ups,
        "rh_target_down_steps": downs,
        "rh_target_values": sorted(set(rh_seq)),
        "rh_target_seq_head": rh_seq[:30],
        "median_plateau_min": float(np.median(dwell) * med_dt / 60.0) if dwell and np.isfinite(med_dt) else None,
        "rh_actual_range": rng(rha),
        "temp_target_values": sorted(set(round(p[0], 1) for p in t_pl)),
        "temp_sample_range": rng(ts),
        "mass_range_mg": rng(m),
        "delta_mass_range_pct": rng(dm),
    }


def main():
    zpath, out = sys.argv[1], sys.argv[2]
    filt = sys.argv[3:]
    z = zipfile.ZipFile(zpath)
    names = [i.filename for i in z.infolist()
             if i.filename.lower().endswith((".xls", ".xlsx")) and (not filt or any(f in i.filename for f in filt))]
    done = set()
    try:
        with open(out, encoding="utf-8") as fh:
            done = {json.loads(l)["file"] for l in fh if l.strip()}
    except FileNotFoundError:
        pass
    proc = psutil.Process()
    with open(out, "a", encoding="utf-8") as fh:
        for k, n in enumerate(names):
            if n in done:
                continue
            t0 = time.time()
            try:
                rec = summarise(n, z.read(n))
            except Exception as e:  # record and continue; an unreadable file is itself a finding
                rec = {"file": n, "error": repr(e)}
            rec["parse_s"] = round(time.time() - t0, 1)
            rec["rss_mb"] = proc.memory_info().rss // 2**20
            fh.write(json.dumps(rec, default=str) + "\n")
            fh.flush()
            print(f"[{k + 1}/{len(names)}] {rec['parse_s']}s {rec['rss_mb']}MB {n}", flush=True)
            gc.collect()


if __name__ == "__main__":
    main()
