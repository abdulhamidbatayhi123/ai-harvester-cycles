import matplotlib.pyplot as plt
import pytest

from p4 import figstyle as fs


def test_save_accepts_a_compliant_figure(tmp_path):
    fs.apply()
    fig, ax = plt.subplots(figsize=(fs.W1, 60 * fs.MM))
    ax.plot([0, 1], [0, 1], label="B0", **fs.style("B0"))
    ax.plot([0, 1], [0, 0.9], label="L1", **fs.style("L1"))
    ax.set_xlabel("time (min)")
    fs.letter(ax, "a")
    ax.legend()
    out = fs.save(fig, str(tmp_path / "ok"))
    assert all((tmp_path / p.split("\\")[-1].split("/")[-1]).exists() for p in out)
    assert (tmp_path / "ok.prov.json").exists()


@pytest.mark.parametrize("bad", ["wide", "tiny_font", "coloured_text"])
def test_save_rejects_rule_breaks(tmp_path, bad):
    fs.apply()
    fig, ax = plt.subplots(figsize=(200 * fs.MM if bad == "wide" else fs.W1, 50 * fs.MM))
    ax.plot([0, 1], [0, 1])
    if bad == "tiny_font":
        ax.set_xlabel("x", fontsize=4)
    if bad == "coloured_text":
        ax.text(0.5, 0.5, "red words", color="#D55E00")
    with pytest.raises(AssertionError):
        fs.save(fig, str(tmp_path / bad))
