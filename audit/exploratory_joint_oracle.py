"""EXPLORATORY (post hoc, after the confirmatory result; not pre-registered). Asked by the internal referee review of
2026-11-11 (finding M5): the two oracles of PREREG sections 2 and 8 are applied one at a time, so their effects need
not add. This applies both at once: B0 with the held-out sorbent's own end points (the eps_hat of the confirmatory
rows, unchanged) AND its own k'' fitted on those scaled isotherms by the scored metric, exactly as B0* is fitted
(p4.run_study.fit_physics). Uses held-out data: an oracle, never a prediction.

Writes results/exploratory/joint_oracle_<rule>.json: per LOSO fold the median E (over the fold's held-out segments) of
B0, the end-point oracle, B0* and the joint oracle, and the noise floor.

usage: python -E -s -m audit.exploratory_joint_oracle data_derived/bezrukov2023 R2   (run from the repository root)
"""
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from p4.dataset import build_groups  # noqa: E402
from p4.physics import Branch, simulate_b0  # noqa: E402
from p4.run_study import COMPOSITE_OF, PRIMARY8, fit_physics, folds, physics_E  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    data, rule = sys.argv[1], sys.argv[2]
    rows = {r["fold"]: r for r in map(json.loads, open(os.path.join(ROOT, "results", f"confirm_{rule}", "rows.jsonl"),
                                                     encoding="utf-8")) if r["key"].endswith("|physics")}
    groups = [g for g in build_groups(data, rule=rule) if g["sorbent"] in PRIMARY8 + list(COMPOSITE_OF.values())]
    out = {"about": __doc__.split("\n\n")[0], "rule": rule, "folds": {}}
    for fold, held in folds():
        if not fold.startswith("LOSO"):
            continue
        p = rows[fold]
        assert p["B0_variant"] == "B0", "the joint oracle is written for the plain variant, which every fold used"
        eps = {k: v for k, v in p["eps_hat"].items()}
        te = [g for g in groups if g["sorbent"] in held]
        E_joint = []
        for s in held:
            own = [g for g in te if g["sorbent"] == s]
            scaled = []
            for g in own:
                ea = eps.get(f"{g['sorbent']}|{g['temp']}", [None])[0]
                if ea is None:
                    break
                scaled.append({**g, "ads": Branch.from_points(g["ads"].rh, g["ads"].w * (1.0 + ea))})
            if len(scaled) != len(own):
                E_joint += [float("nan")] * sum(len(g["w"]) for g in own)
                continue
            k_own = fit_physics(scaled, simulate_b0, False)
            E_joint += physics_E(scaled, simulate_b0, k_own, False)
        med = lambda x: float(np.nanmedian(np.asarray(x, float)))
        out["folds"][fold] = {"held": held, "E_B0": med(p["E"]["B0"]), "E_endpoint": med(p["E"]["B0_endpoint_oracle"]),
                              "E_B0star": med(p["E"]["B0star"]), "E_joint": med(E_joint),
                              "n_nan_joint": int(np.isnan(np.asarray(E_joint, float)).sum())}
        print(fold, out["folds"][fold], flush=True)
    os.makedirs(os.path.join(ROOT, "results", "exploratory"), exist_ok=True)
    with open(os.path.join(ROOT, "results", "exploratory", f"joint_oracle_{rule}.json"), "w", encoding="utf-8",
              newline="\n") as f:
        json.dump(out, f, indent=1)


if __name__ == "__main__":
    main()
