"""Scan a binary for runs of plausible little-endian float64 values (heuristic)."""
import sys, numpy as np
b = open(sys.argv[1], "rb").read()
minrun = int(sys.argv[2]) if len(sys.argv) > 2 else 40
runs = []
for off in range(8):
    n = (len(b) - off) // 8
    a = np.frombuffer(b[off:off + 8 * n], dtype="<f8")
    ok = np.isfinite(a) & (np.abs(a) < 1e6) & ((np.abs(a) > 1e-6) | (a == 0))
    i = 0
    while i < n:
        if ok[i]:
            j = i
            while j < n and ok[j]: j += 1
            if j - i >= minrun: runs.append((off + 8 * i, j - i, a[i:j]))
            i = j
        else: i += 1
runs.sort()
for start, ln, v in runs:
    print(f"@{start} n={ln} min={v.min():.4g} max={v.max():.4g} first={np.round(v[:6],4).tolist()}")
print("total runs", len(runs), "total values", sum(r[1] for r in runs))
