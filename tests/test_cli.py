"""Command-line interface."""

from __future__ import annotations

from qrace.bench.cli import main


def test_cli_roundtrip(tmp_path, capsys):
    out = tmp_path / "suite"
    assert main(["list"]) == 0
    assert main(["build", "--spec", "smoke", "--out", str(out), "--families", "F1", "F3"]) == 0
    assert (out / "manifest.json").exists()
    assert main(["summary", str(out)]) == 0
    assert main(["verify", str(out)]) == 0
    text = capsys.readouterr().out
    assert '"passed": true' in text
