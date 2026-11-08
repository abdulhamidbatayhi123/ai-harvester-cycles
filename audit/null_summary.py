"""Harness criterion 4 (PREREG section 10): false-positive rate of the decision rule in the
realistic null world, from the decide.py outputs of all null replicates.

Per learned model: k beats in n null fold-fits; the one-sided 95 % Clopper-Pearson upper bound
p_up of the per-fold rate; and P(>= 7 of 8 beats) at p_up under independent folds. The criterion
passes for a model if that probability is <= 0.05.

usage: python -I audit/null_summary.py results/null_summary.json results/null_rep0/decide.json [more ...]
"""
import json
import sys

from scipy.stats import beta, binom


def main():
    out_path, files = sys.argv[1], sys.argv[2:]
    res = {}
    for kind in ("L1", "L2"):
        k = n = 0
        per = []
        for f in files:
            d = json.load(open(f, encoding="utf-8"))
            for key, v in d["folds"].items():
                if key.startswith("LOSO") and key.endswith("|" + kind):
                    n += 1
                    k += bool(v["beats_B0"])
                    per.append({"file": f, "fold": key, "beats": v["beats_B0"], "median_gain": v["median_gain"],
                                "E_B0": v["E_B0"], "E_model": v["E_model"], "p": v["p_signflip"]})
        if n == 0:
            continue
        p_up = float(beta.ppf(0.95, k + 1, n - k)) if k < n else 1.0
        p7 = float(binom.sf(6, 8, p_up))
        res[kind] = {"beats": k, "fold_fits": n, "p_upper95": p_up, "P_ge7_of_8_at_p_upper": p7,
                     "criterion_4_pass": p7 <= 0.05, "folds": per}
        print(f"{kind}: {k}/{n} null beats; p_up {p_up:.3f}; P(>=7/8) {p7:.2e}; pass {p7 <= 0.05}")
    json.dump(res, open(out_path, "w", encoding="utf-8"), indent=1)


if __name__ == "__main__":
    main()
