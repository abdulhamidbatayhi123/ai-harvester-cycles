"""The H4a verdict of PREREG section 7, combining what p4.decide cannot see on its own:
the verdict under the primary dry-mass rule R2, the verdict under the sensitivity rule R1, and
criterion 4 of the null study (section 10; audit/null_summary.py over the pre-freeze null worlds
plus the full-procedure replicate).

- Supported only if p4.decide gives "supported" under R2 AND R1 AND criterion 4 passes; the claim
  wording comes from the comparator-robustness line (section 7) under R2.
- A supported-looking result with criterion 4 failed is "not established" (verdict table row 3).
- If R1 and R2 give different verdicts, the result is "not established" and flagged as not
  robust to the dry-mass definition.
- Otherwise the common verdict of R1 and R2 (falsified or not established).
Transfer across families is reported for a supported model (both non-trivial LOFO folds).

usage: python -E -s -m p4.final_verdict <decide_R2.json> <decide_R1.json> <null_summary.json> <out.json> [kind=L1]
"""
from __future__ import annotations

import json
import sys


def combine(r2, r1, null, kind="L1"):
    a, b = r2["H4a"][kind], r1["H4a"][kind]
    c4 = bool(null.get(kind, {}).get("criterion_4_pass", False))
    out = {"kind": kind, "verdict_R2": a["verdict"], "verdict_R1": b["verdict"], "criterion_4_pass": c4,
           "robust_to_dry_mass_rule": a["verdict"] == b["verdict"]}
    if "incomplete" in (a["verdict"], b["verdict"]):
        out["verdict"] = "incomplete"
    elif a["verdict"] != b["verdict"]:
        out["verdict"] = "not established"
    elif a["verdict"] == "supported":
        out["verdict"] = "supported" if c4 else "not established"
        if not c4:
            out["note"] = "7 or more LOSO beats, but the null study failed criterion 4 (section 7, verdict table)"
    else:
        out["verdict"] = a["verdict"]
    if out["verdict"] == "supported":
        out["claim_wording"] = a.get("claim_wording")
        out["transfers_across_families"] = bool(a.get("transfers_across_families")) and bool(b.get("transfers_across_families"))
    return out


def main():
    r2, r1, null = (json.load(open(f, encoding="utf-8")) for f in sys.argv[1:4])
    kind = sys.argv[5] if len(sys.argv) > 5 else "L1"
    res = combine(r2, r1, null, kind)
    json.dump(res, open(sys.argv[4], "w", encoding="utf-8"), indent=1)
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
