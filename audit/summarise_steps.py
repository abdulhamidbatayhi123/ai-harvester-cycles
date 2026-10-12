"""Section 2.3 numbers from results/bezrukov_steps.jsonl.

A step counts if its mass change has the sign of the RH change and |dm| >= 0.05 mg. Step runs
and 5-minute cycling files are reported separately (cycling t63 is cut short by the plateau).
"""
import json, sys, collections
import numpy as np
sys.stdout.reconfigure(encoding="utf-8")
S = [json.loads(l) for l in open(sys.argv[1])]
ok = lambda s: abs(s["dm_mg"]) >= 0.05 and np.sign(s["dm_mg"]) == np.sign(s["rh_to"] - s["rh_from"])
rows = collections.defaultdict(lambda: collections.defaultdict(list))
excluded = 0
for s in S:
    p = s["file"].split("/")
    if len(p) < 3 or p[1] not in ("27C", "60C"):
        continue
    if not ok(s):
        excluded += 1
        continue
    kind = "cyc" if "eatmap" in s["file"] else "step"
    rows[(kind, p[1])][(p[0], "up" if s["dm_mg"] > 0 else "down")].append(s)
for key in sorted(rows):
    print("==", key)
    allmin = []
    for (mat, d), ss in sorted(rows[key].items()):
        t = [x["t63_min"] for x in ss]; n = [x["samples_in_t63"] for x in ss]
        allmin.append(min(n))
        print(f"  {mat:18s} {d:4s} n={len(ss):3d} t63 median {np.median(t):5.1f} min [{min(t):5.1f}, {max(t):6.1f}]  fewest samples in t63 {min(n)}")
    print("  fewest samples in t63 over all:", min(allmin))
print("steps excluded by the rule:", excluded)
