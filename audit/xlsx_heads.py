import sys, openpyxl
sys.stdout.reconfigure(encoding="utf-8")
wb = openpyxl.load_workbook(sys.argv[1], read_only=True, data_only=True)
for ws in wb.worksheets:
    n = 0; heads = []
    for i, r in enumerate(ws.iter_rows(values_only=True)):
        if i < 3: heads.append([c for c in r[:12] if c is not None])
        n += 1
    print("==", ws.title, n, "rows |", heads)
