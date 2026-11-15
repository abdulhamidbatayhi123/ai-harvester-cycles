"""Recompute results/rh50.json (B2's descriptor RH50: the RH at which the adsorption branch reaches half its uptake at
30 % RH, p4.physics.rh50, on the pre-registered isotherms under the primary dry-mass rule R2) for every material and
temperature in the frozen file, and check that the values agree. With --write, write the recomputed table instead.

usage: python -E -s audit/rh50_table.py data_derived/bezrukov2023 [--write]     (run from the repo root)
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from p4.data import data_files, load_run  # noqa: E402
from p4.dataset import isotherm_for  # noqa: E402
from p4.physics import rh50  # noqa: E402


def main():
    root = sys.argv[1]
    out_p = os.path.join(ROOT, "results", "rh50.json")
    frozen = json.load(open(out_p, encoding="utf-8"))
    runs = [load_run(os.path.join(root, f)) for f in data_files(root)]
    new = {s: {T: rh50(isotherm_for(runs, s, T, "R2")[0]) for T in temps} for s, temps in frozen["rh50"].items()}
    diff = max(abs(new[s][T] - frozen["rh50"][s][T]) for s in new for T in new[s])
    print(f"{sum(len(v) for v in new.values())} values; max |recomputed - frozen| = {diff:.3g}")
    if "--write" in sys.argv:
        with open(out_p, "w", encoding="utf-8", newline="\n") as f:
            json.dump({"description": frozen["description"], "rh50": new}, f, indent=1)
    sys.exit(0 if diff < 1e-9 else 1)


if __name__ == "__main__":
    main()
