"""Data-only floor for the physical-violation rule (PREREG sections 6 and 7): the fraction of
measured step segments in P whose uptake moves against the direction of the set-point step by
more than 0.05 wt% over any 1-minute window (p4.physics.violations), per sorbent, under rule R2.

usage: python -I audit/violation_floor.py data_derived/bezrukov2023 results/prefreeze/violation_floor.json
"""
import json, os, sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from p4.dataset import build_groups  # noqa: E402
from p4.physics import violations  # noqa: E402


def main():
    out = {}
    for g in build_groups(sys.argv[1]):
        v = violations(g["w"], g["rh"], g["dir"], g["ads"], g["des"])
        out[f"{g['sorbent']}|{g['temp']}"] = {"n": int(len(v)), "fraction": float(v.mean()) if len(v) else None}
        print(g["sorbent"], g["temp"], len(v), round(float(v.mean()), 3) if len(v) else None, flush=True)
    by = {}
    for k, r in out.items():
        by.setdefault(k.split("|")[0], []).append(r)
    out["per_sorbent"] = {s: sum(r["n"] * r["fraction"] for r in rs) / sum(r["n"] for r in rs) for s, rs in by.items()}
    json.dump(out, open(sys.argv[2], "w"), indent=1)


if __name__ == "__main__":
    main()
