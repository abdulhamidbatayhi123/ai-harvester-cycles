"""Brute force over every combination of the inputs of p4.final_verdict (PAPER_WORKFLOW_LESSONS:
enumerate every verdict table): R2 verdict x R1 verdict x criterion 4 x wording x transfer."""
import itertools

from p4.final_verdict import combine

V = ("supported", "falsified", "not established", "incomplete")
W = ("beats the isotherm-driven models", "supported against the comparator chosen on the training sorbents only")


def _d(v, w, t):
    return {"H4a": {"L1": {"verdict": v, "claim_wording": w if v == "supported" else None,
                           "transfers_across_families": t}}}


def test_every_combination():
    n = 0
    for v2, v1, c4, w, t2, t1 in itertools.product(V, V, (True, False), W, (True, False), (True, False)):
        res = combine(_d(v2, w, t2), _d(v1, w, t1), {"L1": {"criterion_4_pass": c4}})
        n += 1
        if "incomplete" in (v2, v1):
            assert res["verdict"] == "incomplete"
        elif v2 != v1:
            assert res["verdict"] == "not established" and not res["robust_to_dry_mass_rule"]
        elif v2 == "supported":
            assert res["verdict"] == ("supported" if c4 else "not established")
            if c4:
                assert res["claim_wording"] == w and res["transfers_across_families"] == (t2 and t1)
        else:
            assert res["verdict"] == v2
        # never "supported" unless both rules say so and the null study passed
        if res["verdict"] == "supported":
            assert v2 == v1 == "supported" and c4
    assert n == 4 * 4 * 2 * 2 * 2 * 2


def test_missing_null_summary_is_not_a_pass():
    res = combine(_d("supported", W[0], True), _d("supported", W[0], True), {})
    assert res["verdict"] == "not established"


def _b2(v):
    return {"H4a": {"B2": {"verdict": v, "claim_wording": "beats the isotherm-driven models" if v == "supported" else None,
                           "transfers_across_families": True}}}


def test_b2_needs_every_harness_criterion():
    ok = {"pass": {"1_no_beat_in_N": True, "2_K_found": True, "3_null_S": True}}
    assert combine(_b2("supported"), _b2("supported"), ok, "B2")["verdict"] == "supported"
    for k in ok["pass"]:
        bad = {"pass": {**ok["pass"], k: False}}
        assert combine(_b2("supported"), _b2("supported"), bad, "B2")["verdict"] == "not established"
    assert combine(_b2("supported"), _b2("supported"), {}, "B2")["verdict"] == "not established"
    assert combine(_b2("falsified"), _b2("falsified"), ok, "B2")["verdict"] == "falsified"
