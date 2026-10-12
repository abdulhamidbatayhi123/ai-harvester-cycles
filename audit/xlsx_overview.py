import sys, openpyxl
wb = openpyxl.load_workbook(sys.argv[1], read_only=True, data_only=True)
for ws in wb.worksheets:
    print("=== SHEET", ws.title, ws.max_row, "x", ws.max_column)
    for i, row in enumerate(ws.iter_rows(max_row=6, values_only=True)):
        print("  ", [c for c in row[:14]])
