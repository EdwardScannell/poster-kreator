import pytest
from PIL import Image

from poster_kreator.fit import (
    MIN_FONT_PX,
    ContentDoesNotFit,
    _fits,
    fit_image,
    fit_text,
    font,
    wrap,
)


def test_short_text_gets_a_large_font() -> None:
    fitted = fit_text("Welcome", 400, 200)
    assert fitted.lines == ("Welcome",)
    assert fitted.size > 40


def test_fitted_text_stays_inside_the_area() -> None:
    text = "Plants turn light, water and carbon dioxide into sugar and oxygen."
    fitted = fit_text(text, 300, 300)
    face = font(fitted.size)
    assert all(face.getlength(line) <= 300 for line in fitted.lines)
    assert fitted.height <= 300
    assert " ".join(fitted.lines) == text


def test_one_size_larger_would_not_fit() -> None:
    text = "The green pigment that catches the light."
    fitted = fit_text(text, 250, 250)
    assert _fits(text, fitted.size + 1, 250, 250) is None


def test_longer_text_gets_a_smaller_font() -> None:
    assert fit_text("one two", 300, 300).size > fit_text("one two " * 20, 300, 300).size


def test_word_wider_than_the_area_does_not_fit() -> None:
    with pytest.raises(ContentDoesNotFit, match=f"{MIN_FONT_PX} px"):
        fit_text("pneumonoultramicroscopicsilicovolcanoconiosis", 40, 400)


def test_zero_area_does_not_fit() -> None:
    with pytest.raises(ContentDoesNotFit):
        fit_text("x", 0, 10)


def test_wrap_returns_none_for_an_overlong_word() -> None:
    assert wrap("tiny enormousword", 40, 30) is None


@pytest.mark.parametrize(("w", "h", "expected"), [(100, 100, (100, 50)), (40, 100, (40, 20))])
def test_image_keeps_its_proportions(w: int, h: int, expected: tuple[int, int]) -> None:
    assert fit_image(Image.new("RGB", (200, 100)), w, h).size == expected


def test_image_needs_an_area() -> None:
    with pytest.raises(ContentDoesNotFit):
        fit_image(Image.new("RGB", (10, 10)), 0, 10)
