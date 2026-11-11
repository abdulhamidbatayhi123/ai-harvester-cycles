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
        for v in ("supported", "falsified", "not established"):
            assert combine(_b2(v), _b2(v), bad, "B2")["verdict"] == "not tested"
    assert combine(_b2("falsified"), _b2("falsified"), {}, "B2")["verdict"] == "not tested"
    assert combine(_b2("falsified"), _b2("falsified"), ok, "B2")["verdict"] == "falsified"


def test_b2_wording_rules_from_the_harness_summary():
    """Sections 7 and 10b (pre-freeze review 2026-11-11): a falsification takes the weaker wording when B2
    was not supported in every realistic-power world; a support carries the C3 form-error caveat."""
    summ = {"power_K2": {"K2a": {"verdict": "supported"}, "K2b": {"verdict": "supported"},
                         "K2c": {"verdict": "not established"}}, "C3_reported": {"beats": 6}}
    ok = {"pass": {"1_no_beat_in_N": True, "2_K_found": True, "3_null_S": True}, "summary": summ}
    f = combine(_b2("falsified"), _b2("falsified"), ok, "B2")
    assert f["verdict"] == "falsified" and "missed in 1 of 3" in f["wording"]
    s = combine(_b2("supported"), _b2("supported"), ok, "B2")
    assert s["verdict"] == "supported" and "6 of 8" in s["form_error_caveat"] and "wording" not in s
    all_k2 = {**ok, "summary": {**summ, "power_K2": {k: {"verdict": "supported"} for k in ("K2a", "K2b", "K2c")}}}
    assert "wording" not in combine(_b2("falsified"), _b2("falsified"), all_k2, "B2")
    n = combine(_b2("not established"), _b2("not established"), ok, "B2")
    assert "wording" not in n and "form_error_caveat" not in n
