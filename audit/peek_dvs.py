import sys, zipfile, io, time, psutil, pandas as pd
sys.stdout.reconfigure(encoding="utf-8")
z = zipfile.ZipFile(sys.argv[1]); name = sys.argv[2]
t0 = time.time()
df = pd.read_excel(io.BytesIO(z.read(name)), sheet_name=None, header=None, nrows=60)
for sh, d in df.items():
    print("== sheet", sh, d.shape)
    for i in range(min(len(d), 60)):
        row = [x for x in d.iloc[i].tolist()[:12] if x == x]
        if row: print(i, row)
print("time", round(time.time()-t0,1), "rss MB", psutil.Process().memory_info().rss//2**20)
