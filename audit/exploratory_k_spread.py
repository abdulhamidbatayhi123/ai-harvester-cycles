"""EXPLORATORY (post hoc; internal referee review 2026-11-15, item 1): the across-sorbent spread of ln k'' per
temperature, computed from results/prefreeze/reproduce_b0.json for both kinds of in-sample fit: least squares
(k2_own) and the scored metric (k2_own_metric, the fit used everywhere else in the paper). Spread = root mean square
of the two directions' sample standard deviations of ln k'' over the eight parent sorbents. The B2 harness's
realistic-power worlds used the spreads fixed in the protocol from the least-squares fits (0.089 at 27 C, 0.300 at
60 C; audit/harness_b2.py SD_B); this file shows how the metric fits compare.

usage: python -I audit/exploratory_k_spread.py results/exploratory/k_spread.json
"""
import json
import math
import os
import statistics
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PARENTS = ["ROS-037", "ROS-039", "ROS-040", "MOF-303", "MIL-160", "CAU-10", "Al-fumarate", "Syloid"]


def main():
    rows = json.load(open(os.path.join(ROOT, "results", "prefreeze", "reproduce_b0.json"),
                          encoding="utf-8"))["per_material"]
    out = {"about": __doc__.split("\n\n")[0], "least_squares": {}, "metric": {}, "per_direction_sd": {}}
    for kind, key in (("least_squares", "k2_own"), ("metric", "k2_own_metric")):
        for T in ("27C", "60C"):
            sds = {}
            for d in ("ads", "des"):
                x = [math.log(next(r[key] for r in rows if r["sorbent"] == s and r["temp"] == T and r["dir"] == d))
                     for s in PARENTS]
                sds[d] = statistics.stdev(x)
            out["per_direction_sd"][f"{kind}|{T}"] = sds
            out[kind][T] = math.sqrt((sds["ads"] ** 2 + sds["des"] ** 2) / 2)
    with open(sys.argv[1], "w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, indent=1)
    print(json.dumps({k: out[k] for k in ("least_squares", "metric")}, indent=1))


if __name__ == "__main__":
    main()
