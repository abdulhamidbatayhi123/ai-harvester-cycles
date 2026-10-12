import sys, openpyxl
sys.stdout.reconfigure(encoding="utf-8")
wb = openpyxl.load_workbook(sys.argv[1], read_only=True, data_only=True)
r = list(wb["Figure 5A"].iter_rows(values_only=True))
cyc = [(x[3], x[4]) for x in r[1:] if x[3] is not None]
print("5A cycles:", len(cyc), cyc[:3], cyc[-3:])
print("5A col beyond:", [x for x in r[:3]])
for n in ["Figure 4B", "Figure 2"]:
    for x in wb[n].iter_rows(values_only=True): print(n, x)
for n in ["Figure 5C", "Figure 5D", "Figure 4A", "Figure 5B"]:
    rows = [x for x in wb[n].iter_rows(values_only=True)][1:]
    rows = [x for x in rows if x[0] is not None]
    print(n, len(rows), "first", rows[-1], "last", rows[0])
s = list(wb["Figure S28 + S30"].iter_rows(values_only=True))
print([x[:9] for x in s if x[8] is not None][:12])
print([x[:9] for x in s if x[7] is not None])
r = list(wb["Figure S22"].iter_rows(values_only=True)); print("S22", r[0], len(r))
