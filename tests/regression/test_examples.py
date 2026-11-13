"""The example specs in the README must keep rendering."""

from pathlib import Path

import pytest

from poster_kreator.render import load_spec, render

EXAMPLES = Path(__file__).resolve().parents[2] / "examples"


@pytest.mark.regression
@pytest.mark.parametrize("name", ["word_wall.json", "four_square.json"])
def test_example_renders(name: str) -> None:
    poster = load_spec(EXAMPLES / name)
    image = render(poster)
    assert image.size == (poster.page.width_px, poster.page.height_px)
