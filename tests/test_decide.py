import json

import numpy as np

from p4 import decide


def _rows(gain, n_clusters=8, viol=0.0):
    rows = []
    folds = [f"LOSO:S{i}" for i in range(8)] + ["LOFO:Al-rod", "LOFO:Zn-triazolate-F"]
    rng = np.random.default_rng(0)
    for f in folds:
        seg = [f"sess{c}|27C|0>30#run{c}#{k}" for c in range(n_clusters) for k in range(2)]
        e_b = list(0.10 + 0.01 * rng.random(len(seg)))
        e_m = [e - gain for e in e_b]
        held = [f.split(":")[1]]
        rows.append({"key": f"{f}|physics", "fold": f, "held": held, "seg": seg, "comparator": "B0",
                     "viol_data": [False] * len(seg), "E": {"B0": e_b, "base": e_b, "B2": e_b, "B0star": e_b}})
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
