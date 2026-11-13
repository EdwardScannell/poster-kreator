"""Fitting content into a box: text is wrapped and shrunk, images are scaled.

Text uses the font bundled with Pillow, so the same spec renders the same way on every
machine.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache

from PIL import Image, ImageFont

MIN_FONT_PX = 8
LINE_SPACING = 1.15


class ContentDoesNotFit(ValueError):
    """The content cannot fit its shape even at the smallest size."""


@dataclass(frozen=True)
class FittedText:
    size: int
    lines: tuple[str, ...]
    line_height: int

    @property
    def height(self) -> int:
        return self.line_height * len(self.lines)


@lru_cache(maxsize=256)
def font(size: int) -> ImageFont.FreeTypeFont:
    """Pillow's bundled scalable font at `size` pixels."""
    loaded = ImageFont.load_default(size=size)
    if not isinstance(loaded, ImageFont.FreeTypeFont):  # pragma: no cover - build without FreeType
        raise RuntimeError("Pillow was built without FreeType; scalable text is unavailable")
    return loaded


def _line_height(size: int) -> int:
    ascent, descent = font(size).getmetrics()
    return max(1, round((ascent + descent) * LINE_SPACING))


def wrap(text: str, size: int, width: int) -> tuple[str, ...] | None:
    """Greedy word wrap at `size`; None if a single word is wider than `width`."""
    face = font(size)
    lines: list[str] = []
    current = ""
    for word in text.split(" "):
        if face.getlength(word) > width:
            return None
        candidate = f"{current} {word}" if current else word
        if face.getlength(candidate) <= width:
            current = candidate
        else:
            lines.append(current)
            current = word
    lines.append(current)
    return tuple(lines)


def _fits(text: str, size: int, width: int, height: int) -> FittedText | None:
    lines = wrap(text, size, width)
    if lines is None:
        return None
    fitted = FittedText(size, lines, _line_height(size))
    return fitted if fitted.height <= height else None


def fit_text(text: str, width: int, height: int) -> FittedText:
    """The largest font size at which `text` wraps inside width x height pixels."""
    best = _fits(text, MIN_FONT_PX, width, height) if width > 0 and height > 0 else None
    if best is None:
        raise ContentDoesNotFit(
            f"text does not fit a {width}x{height} px area even at {MIN_FONT_PX} px: "
            "shorten it, use fewer shapes, or a larger page"
        )
    low, high = MIN_FONT_PX, max(MIN_FONT_PX, height)
    while low < high:
        mid = (low + high + 1) // 2
        candidate = _fits(text, mid, width, height)
        if candidate is None:
            high = mid - 1
        else:
            low, best = mid, candidate
    return best


def fit_image(image: Image.Image, width: int, height: int) -> Image.Image:
    """Scale `image` to the largest size inside width x height, keeping its proportions."""
    if width < 1 or height < 1:
        raise ContentDoesNotFit(f"an image cannot fit a {width}x{height} px area")
    scale = min(width / image.width, height / image.height)
    size = (max(1, round(image.width * scale)), max(1, round(image.height * scale)))
    return image.resize(size, Image.Resampling.LANCZOS)
