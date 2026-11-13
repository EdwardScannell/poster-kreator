import json
from pathlib import Path

import pytest
from PIL import Image

from poster_kreator.fit import ContentDoesNotFit
from poster_kreator.layout import equal_grid
from poster_kreator.model import Cell, ImageContent, Page, Poster, TextContent
from poster_kreator.render import load_spec, render, render_to_file

PAGE = Page(width_in=6, height_in=4, dpi=72)


def _text(text: str, **kw: str) -> Cell:
    return Cell(content=TextContent(text=text), **kw)


@pytest.fixture
def red_square(tmp_path: Path) -> Path:
    path = tmp_path / "red.png"
    Image.new("RGB", (50, 50), "#FF0000").save(path)
    return path


def test_canvas_matches_the_page() -> None:
    image = render(Poster(page=PAGE, cells=[_text("hi")]))
    assert image.size == (PAGE.width_px, PAGE.height_px)
    assert image.getpixel((1, 1)) == (255, 255, 255)


@pytest.mark.parametrize("count", [4, 6])
def test_every_shape_is_drawn_with_its_fill(count: int) -> None:
    cells = [_text(f"word {n}", fill="#00FF00") for n in range(count)]
    poster = Poster(page=PAGE, cells=cells)
    image = render(poster)
    for box in equal_grid(count, PAGE):
        assert image.getpixel((box.x, box.y)) == (0, 0, 0)  # outline
        assert image.getpixel((box.x + 3, box.y + 3)) == (0, 255, 0)  # fill


def test_text_is_drawn_inside_its_shape() -> None:
    poster = Poster(page=PAGE, cells=[_text("WWWW")])
    image = render(poster)
    box = equal_grid(1, PAGE)[0]
    inside = image.crop((box.x + 3, box.y + 3, box.right - 3, box.bottom - 3))
    assert (0, 0, 0) in {color for _, color in inside.getcolors(maxcolors=100_000) or []}


def test_image_is_centered_in_its_shape(red_square: Path) -> None:
    poster = Poster(page=PAGE, cells=[Cell(content=ImageContent(path=red_square))])
    image = render(poster)
    box = equal_grid(1, PAGE)[0]
    assert image.getpixel((box.x + box.w // 2, box.y + box.h // 2)) == (255, 0, 0)
    assert image.getpixel((box.x + 3, box.y + box.h // 2)) == (255, 255, 255)


def test_render_is_deterministic() -> None:
    poster = Poster(page=PAGE, cells=[_text("same"), _text("every time")])
    assert render(poster).tobytes() == render(poster).tobytes()


def test_overflow_names_the_shape() -> None:
    cells = [_text("fine"), _text("pneumonoultramicroscopicsilicovolcanoconiosis")]
    with pytest.raises(ContentDoesNotFit, match="shape 2"):
        render(Poster(page=Page(width_in=3, height_in=2, dpi=36, margin_in=0.1), cells=cells))


def test_spec_image_paths_are_relative_to_the_spec(tmp_path: Path, red_square: Path) -> None:
    spec = tmp_path / "spec.json"
    spec.write_text(
        json.dumps({"cells": [{"content": {"kind": "image", "path": red_square.name}}]}),
        encoding="utf-8",
    )
    poster = load_spec(spec)
    content = poster.cells[0].content
    assert isinstance(content, ImageContent)
    assert content.path == red_square


def test_absolute_and_text_cells_are_left_alone(red_square: Path, tmp_path: Path) -> None:
    spec = tmp_path / "spec.json"
    cells = [
        {"content": {"kind": "image", "path": str(red_square)}},
        {"content": {"kind": "text", "text": "x"}},
    ]
    spec.write_text(json.dumps({"cells": cells}), encoding="utf-8")
    poster = load_spec(spec)
    assert poster.cells[0].content == ImageContent(path=red_square)
    assert poster.cells[1].content == TextContent(text="x")


def test_render_to_file_writes_a_png_with_its_dpi(tmp_path: Path) -> None:
    out = render_to_file(Poster(page=PAGE, cells=[_text("hi")]), tmp_path / "a" / "b.png")
    with Image.open(out) as saved:
        assert saved.format == "PNG"
        assert round(saved.info["dpi"][0]) == PAGE.dpi
