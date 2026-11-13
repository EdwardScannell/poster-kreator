from pathlib import Path

import pytest
from pydantic import ValidationError

from poster_kreator.model import (
    Cell,
    ImageContent,
    Orientation,
    Page,
    Poster,
    ShapeKind,
    TextContent,
)


def test_text_whitespace_is_collapsed() -> None:
    assert TextContent(text="  big   ideas\n grow  ").text == "big ideas grow"


@pytest.mark.parametrize("blob", ["- one\n- two", "* item", "1. first", "• dot", "a\n2) b"])
def test_text_refuses_lists(blob: str) -> None:
    with pytest.raises(ValidationError, match="plain blob"):
        TextContent(text=blob)


def test_text_refuses_empty() -> None:
    with pytest.raises(ValidationError, match="empty"):
        TextContent(text="   ")


def test_hyphenated_words_are_plain_text() -> None:
    assert TextContent(text="well-known half-life").text == "well-known half-life"


def test_bad_color_is_refused() -> None:
    with pytest.raises(ValidationError):
        TextContent(text="x", color="red")


def test_page_pixels_and_orientation() -> None:
    page = Page()
    assert (page.width_px, page.height_px) == (1650, 1275)
    assert page.orientation is Orientation.LANDSCAPE
    assert Page(width_in=8.5, height_in=11).orientation is Orientation.PORTRAIT


def test_cell_content_is_discriminated() -> None:
    cell = Cell.model_validate({"content": {"kind": "image", "path": "a.png"}})
    assert isinstance(cell.content, ImageContent)
    assert cell.content.path == Path("a.png")
    assert cell.shape is ShapeKind.RECTANGLE


def test_poster_needs_a_cell() -> None:
    with pytest.raises(ValidationError):
        Poster(cells=[])


def test_unknown_fields_are_refused() -> None:
    with pytest.raises(ValidationError):
        Poster.model_validate({"cells": [{"content": {"kind": "text", "text": "x"}}], "x": 1})
