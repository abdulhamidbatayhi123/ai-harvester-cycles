import sys, openpyxl
sys.stdout.reconfigure(encoding="utf-8")
wb = openpyxl.load_workbook(sys.argv[1], read_only=True, data_only=True)
names = sys.argv[2:] or wb.sheetnames
for n in names:
    ws = wb[n]
    rows = list(ws.iter_rows(values_only=True))
    print("=== SHEET", n, len(rows), "rows")
    for r in rows[:4]: print("  ", r)
    # columns that are non-empty and count
    ncol = max(len(r) for r in rows)
    cnt = [sum(1 for r in rows if c < len(r) and r[c] is not None) for c in range(ncol)]
    print("   nonnull per col:", cnt)
