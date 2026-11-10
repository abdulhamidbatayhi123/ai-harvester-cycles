import json

import numpy as np

from p4 import decide


def _rows(gain, n_clusters=8, viol=0.0):
    rows = []
    folds = [f"LOSO:S{i}" for i in range(8)] + ["LOFO:Al-rod", "LOFO:Zn-triazolate-F"]
    rng = np.random.default_rng(0)
    for f in folds:
        held = [f.split(":")[1]]
        seg = [f"{held[0]}|27C|sess{c}|{c}|27C|0>30#run{c}#{k}" for c in range(n_clusters) for k in range(2)]
        e_b = list(0.10 + 0.01 * rng.random(len(seg)))
        e_m = [e - gain for e in e_b]
        rows.append({"key": f"{f}|physics", "fold": f, "held": held, "seg": seg, "comparator": "B0",
                     "dw": list(1.0 + rng.random(len(seg))),
                     "viol_data": [False] * len(seg), "viol_B2": [False] * len(seg),
                     "E": {"B0": e_b, "base": e_b, "B2": e_b, "B0star": e_b}})
        for kind in ("L1", "L2"):
            rows.append({"key": f"{f}|{kind}|ensemble", "fold": f, "kind": kind, "seg": seg, "E": e_m,
                         "viol": [i < viol * len(seg) for i in range(len(seg))]})
    return rows


def _run(tmp_path, rows):
    rp, cp, op = tmp_path / "rows.jsonl", tmp_path / "c.json", tmp_path / "out.json"
    rp.write_text("\n".join(json.dumps(r) for r in rows))
    cp.write_text(json.dumps({"F_within_segment_weighted": {f"S{i}": 0.003 for i in range(8)}}))
    import sys
    sys.argv = ["decide", str(rp), str(cp), str(op)]
    decide.main()
    return json.loads(op.read_text())


def test_clear_gain_is_supported(tmp_path):
    out = _run(tmp_path, _rows(0.03))
    assert out["H4a"]["L1"]["verdict"] == "supported"
    assert out["H4a"]["L1"]["transfers_across_families"] is True


def test_no_gain_is_falsified(tmp_path):
    out = _run(tmp_path, _rows(0.0))
    assert out["H4a"]["L1"]["verdict"] == "falsified"


def test_too_few_clusters_cannot_beat(tmp_path):
    out = _run(tmp_path, _rows(0.03, n_clusters=5))
    assert out["H4a"]["L1"]["LOSO_beats"] == 0


def test_violations_block_a_beat(tmp_path):
    out = _run(tmp_path, _rows(0.03, viol=0.5))
    assert out["H4a"]["L2"]["LOSO_beats"] == 0


def test_composite_must_pass_too(tmp_path):
    """Review finding C2: a parent fold with a composite is beaten only if both materials pass."""
    rows = _rows(0.03)
    for r in rows:
        if r["fold"] == "LOSO:S0":
            r["held"] = ["S0", "S0_composite"]
            if r["key"].endswith("physics"):
                n = len(r["seg"])
                r["seg"] = r["seg"] + [s.replace("S0|", "S0_composite|", 1) for s in r["seg"]]
                for k in r["E"]:
                    r["E"][k] = r["E"][k] * 2
                r["dw"], r["viol_data"], r["viol_B2"] = r["dw"] * 2, r["viol_data"] * 2, r["viol_B2"] * 2
            else:
                r["seg"] = r["seg"] + [s.replace("S0|", "S0_composite|", 1) for s in r["seg"]]
                base = [x + 0.03 for x in r["E"]]
                r["E"] = r["E"] + base          # no gain at all on the composite
                r["viol"] = r["viol"] * 2
    out = _run(tmp_path, rows)
    f = out["folds"]["LOSO:S0|L1"]
    assert f["per_material"]["S0"]["rule_met"] and not f["per_material"]["S0_composite"]["rule_met"]
    assert not f["beats_B0"]


def test_one_good_fold_still_falsified(tmp_path):
    """Review finding O1: falsified when at most one LOSO fold reaches r >= 10 %."""
    rows = _rows(0.0)
    for r in rows:
        if r["fold"] == "LOSO:S0" and r["key"].endswith("ensemble"):
            r["E"] = [e - 0.03 for e in r["E"]]
    out = _run(tmp_path, rows)
    assert out["H4a"]["L1"]["n_folds_rel_ge_10pct"] == 1 and out["H4a"]["L1"]["verdict"] == "falsified"


def test_seg_ids_cluster_merges_pans_and_repeats():
    """PREREG section 4: one cluster per RH step per session; both pans and all repeats merge."""
    from types import SimpleNamespace as NS
    import numpy as np
    from p4.run_study import seg_ids
    segs = [NS(rh_from=0, rh_to=30, index=3), NS(rh_from=0, rh_to=30, index=7),
            NS(rh_from=0, rh_to=30, index=3), NS(rh_from=30, rh_to=0, index=4)]
    g = {"temp": "27C", "segments": segs,
         "exp": np.array(["X|27C|S1|3", "X|27C|S1|7", "X|27C|S1|3", "X|27C|S1|4"]),
         "run": np.array(["pan5mg", "pan5mg", "pan8mg", "pan5mg"])}
    keys = [s.split("#")[0] for s in seg_ids([g])]
    assert len(set(keys)) == 2 and keys[0] == keys[1] == keys[2]


def test_paired_gain_with_worse_typical_error_is_not_a_beat():
    """Harness round 6 (world C2, held-out ROS-039; results/diag/c2_clusters): L1 is far better on
    the desorption clusters and up to twelve times worse on the 0>30 adsorption clusters. The paired
    median and the signed-rank test favour it; condition 4 must refuse it."""
    b0 = np.array([0.0024, 0.0099, 0.0029, 0.0021, 0.0087, 0.0027, 0.0097, 0.0037, 0.0063, 0.0073,
                   0.0076, 0.0110, 0.0111, 0.0155, 0.0689, 0.0835, 0.1026, 0.1027, 0.1148, 0.1153,
                   0.0878, 0.0913, 0.1028, 0.1016, 0.1788, 0.1843])
    m = np.array([0.0296, 0.0359, 0.0263, 0.0250, 0.0313, 0.0252, 0.0103, 0.0028, 0.0045, 0.0043,
                  0.0013, 0.0014, 0.0013, 0.0022, 0.0432, 0.0525, 0.0704, 0.0673, 0.0786, 0.0755,
                  0.0440, 0.0432, 0.0516, 0.0484, 0.1212, 0.1258])
    ok, info = decide.rule(b0, m, 0.003, D=b0 - m)
    assert info["median_gain"] > 0.003 and info["p_signflip"] <= 0.025
    assert info["E_model"] > 2 * info["E_B0"]
    assert not ok


def test_composite_only_gain_does_not_count_as_r(tmp_path):
    """Review T-P4-4 F-6: r of a parent + composite fold is the smaller per-material r, so a gain on
    the composite alone cannot move a fold to r >= 10 % (pooled r is only reported)."""
    rows = _rows(0.0)
    for r in rows:
        if r["fold"] == "LOSO:S0":
            r["held"] = ["S0", "S0_composite"]
            comp = [s.replace("S0|", "S0_composite|", 1) for s in r["seg"]]
            comp = comp + [s.replace("#run", "#xrun") for s in comp]          # composite: 2x the clusters' segments
            comp = [c.replace("sess", "csess") for c in comp]
            if r["key"].endswith("physics"):
                n = len(comp)
                r["seg"] = r["seg"] + comp
                for k in r["E"]:
                    r["E"][k] = r["E"][k] + [0.10] * n
                r["dw"], r["viol_data"], r["viol_B2"] = r["dw"] + [1.0] * n, r["viol_data"] + [False] * n, r["viol_B2"] + [False] * n
            else:
                n = len(comp)
                r["seg"] = r["seg"] + comp
                r["E"] = r["E"] + [0.07] * n          # 30 % gain on the composite only
                r["viol"] = r["viol"] + [False] * n
    out = _run(tmp_path, rows)
    f = out["folds"]["LOSO:S0|L1"]
    assert f["r_pooled"] >= 0.10 and abs(f["r_fold"]) < 1e-9
    assert not f["beats_B0"] and out["H4a"]["L1"]["n_folds_rel_ge_10pct"] == 0


def test_claim_wording_when_another_candidate_wins_on_heldout(tmp_path):
    """Review T-P4-4 F-7: supported against the chosen comparator but not against the candidate with
    the lowest held-out E -> the claim is worded as against the training-chosen comparator only."""
    rows = _rows(0.03)
    for r in rows:
        if r["key"].endswith("physics"):
            r["E"]["B1"] = [e - 0.05 for e in r["E"]["B0"]]       # B1 better than the learned model
    out = _run(tmp_path, rows)
    h = out["H4a"]["L1"]
    assert h["verdict"] == "supported" and h["LOSO_beats_vs_heldout_best_candidate"] == 0
    assert h["claim_wording"] == "supported against the comparator chosen on the training sorbents only"
    out = _run(tmp_path, _rows(0.03))
    assert out["H4a"]["L1"]["claim_wording"] == "beats the isotherm-driven models"


def test_diverged_model_segments_count_as_losses(tmp_path):
    """Independent-scorer check 2026-11-10: a non-finite model E is an infinite loss, not a dropped
    segment; a model that diverges on most clusters cannot beat the comparator."""
    rows = _rows(0.03)
    for r in rows:
        if r["fold"] == "LOSO:S0" and r["key"].endswith("L1|ensemble"):
            r["E"] = [float("nan") if i % 4 else e for i, e in enumerate(r["E"])]
    out = _run(tmp_path, rows)
    f = out["folds"]["LOSO:S0|L1"]
    assert not f["beats_B0"] and f["r_fold"] < 0


def test_held_composite_without_segments_fails(tmp_path):
    """Independent-scorer check 2026-11-10: "both must pass" also when a held material has no
    scored segment at all."""
    rows = _rows(0.03)
    for r in rows:
        if r["fold"] == "LOSO:S0":
            r["held"] = ["S0", "S0_composite"]
    out = _run(tmp_path, rows)
    f = out["folds"]["LOSO:S0|L1"]
    assert f["per_material"]["S0"]["rule_met"] and not f["per_material"]["S0_composite"]["rule_met"]
    assert not f["beats_B0"]


def _b2_rows(gain, viol_b2=0.0):
    rows = _rows(0.0)
    for r in rows:
        if r["key"].endswith("|physics"):
            r["E"]["B2"] = [e - gain for e in r["E"]["base"]]
            r["viol_B2"] = [i < viol_b2 * len(r["seg"]) for i in range(len(r["seg"]))]
    return rows


def test_b2_is_judged_from_the_physics_row(tmp_path):
    """H4a' (2026-11-10): B2 is scored by the same rule as a learned model, from the physics row."""
    out = _run(tmp_path, _b2_rows(0.03))
    assert out["H4a"]["B2"]["verdict"] == "supported" and out["H4a"]["B2"]["LOSO_beats"] == 8
    assert out["H4a"]["L1"]["verdict"] == "falsified"          # the learned rows are untouched
    out = _run(tmp_path, _b2_rows(0.0))
    assert out["H4a"]["B2"]["verdict"] == "falsified"


def test_b2_violations_block_a_beat(tmp_path):
    out = _run(tmp_path, _b2_rows(0.03, viol_b2=0.5))
    assert out["H4a"]["B2"]["LOSO_beats"] == 0
