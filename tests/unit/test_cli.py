import json
from pathlib import Path
from typing import Any

from typer.testing import CliRunner

from poster_kreator import __version__
from poster_kreator.cli import app

runner = CliRunner()


def _spec(tmp_path: Path, cells: list[Any]) -> Path:
    spec = tmp_path / "spec.json"
    spec.write_text(json.dumps({"cells": cells}), encoding="utf-8")
    return spec


def test_version() -> None:
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert result.stdout.strip() == __version__


def test_shapes() -> None:
    result = runner.invoke(app, ["shapes"])
    assert result.exit_code == 0
    assert result.stdout.split() == ["rectangle"]


def test_layout_prints_one_line_per_shape(tmp_path: Path) -> None:
    cells = [{"content": {"kind": "text", "text": str(n)}} for n in range(4)]
    result = runner.invoke(app, ["layout", str(_spec(tmp_path, cells))])
    assert result.exit_code == 0
    assert [line.split(":")[0] for line in result.stdout.splitlines()] == ["1", "2", "3", "4"]


def test_render_writes_the_png(tmp_path: Path) -> None:
    spec = _spec(tmp_path, [{"content": {"kind": "text", "text": "hello"}}])
    out = tmp_path / "out.png"
    result = runner.invoke(app, ["render", str(spec), "-o", str(out)])
    assert result.exit_code == 0, result.output
    assert out.exists()


def test_render_reports_a_bad_spec(tmp_path: Path) -> None:
    spec = _spec(tmp_path, [{"content": {"kind": "text", "text": "- a bullet"}}])
    result = runner.invoke(app, ["render", str(spec), "-o", str(tmp_path / "x.png")])
    assert result.exit_code == 1
    assert "error:" in result.output


def test_render_reports_a_missing_image(tmp_path: Path) -> None:
    spec = _spec(tmp_path, [{"content": {"kind": "image", "path": "missing.png"}}])
    result = runner.invoke(app, ["render", str(spec), "-o", str(tmp_path / "x.png")])
    assert result.exit_code == 1
