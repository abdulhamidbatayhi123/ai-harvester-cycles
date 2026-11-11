"""Which held-out groups lie outside B2's training range of the descriptor RH50 (PREREG section 2,
"Reported with the verdict"). Isotherm feature only: no kinetic outcome is read.

Rule: in each LOSO fold, a held-out material's RH50 at temperature T is an extrapolation if it lies outside
[min, max] of RH50 at T over every group B2 is fitted on (all non-held materials, the validation sorbent and
the composites of non-held parents included; p4.run_study fits B2 on train + validation).

usage: python -I audit/extrapolation_flags.py results/rh50.json results/extrapolation_flags.json
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from p4.run_study import folds  # noqa: E402


def flags(rh50):
    out = {}
    for fold, held in folds():
        if not fold.startswith("LOSO"):
            continue
        rows = []
        for s in held:
            for T, v in rh50.get(s, {}).items():
                train = [rh50[o][T] for o in rh50 if o not in held and T in rh50[o]]
                lo, hi = min(train), max(train)
                if not lo <= v <= hi:
                    rows.append({"material": s, "temp": T, "rh50": v, "train_min": lo, "train_max": hi})
        out[fold] = rows
    return out


def main():
    rh50 = json.load(open(sys.argv[1], encoding="utf-8"))["rh50"]
    res = {"rule": __doc__.split("Rule: ")[1].split("\n\n")[0].replace("\n", " "), "flags": flags(rh50)}
    with open(sys.argv[2], "w", encoding="utf-8", newline="\n") as f:
        json.dump(res, f, indent=1)
    for k, v in res["flags"].items():
        for r in v:
            print(k, r)


if __name__ == "__main__":
    main()
