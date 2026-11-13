"""Render a poster spec to an image."""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw

from poster_kreator.fit import ContentDoesNotFit, fit_image, fit_text, font
from poster_kreator.layout import Box, equal_grid
from poster_kreator.model import Cell, ImageContent, Poster

OUTLINE_COLOR = "#000000"
PADDING_RATIO = 0.08


def load_spec(path: Path) -> Poster:
    """Read a JSON spec; image paths are resolved relative to the spec's folder."""
    poster = Poster.model_validate(json.loads(path.read_text(encoding="utf-8")))
    cells = [
        cell.model_copy(
            update={
                "content": cell.content.model_copy(update={"path": path.parent / cell.content.path})
            }
        )
        if isinstance(cell.content, ImageContent) and not cell.content.path.is_absolute()
        else cell
        for cell in poster.cells
    ]
    return poster.model_copy(update={"cells": cells})


def _inner(box: Box, outline: int) -> Box:
    pad = max(outline + 1, round(min(box.w, box.h) * PADDING_RATIO))
    return Box(box.x + pad, box.y + pad, box.w - 2 * pad, box.h - 2 * pad)


def _outline_px(poster: Poster) -> int:
    return max(1, poster.page.px(0.02))


def _draw_cell(canvas: Image.Image, cell: Cell, box: Box, outline: int, index: int) -> None:
    draw = ImageDraw.Draw(canvas)
    draw.rectangle(
        (box.x, box.y, box.right - 1, box.bottom - 1),
        fill=cell.fill,
        outline=OUTLINE_COLOR,
        width=outline,
    )
    inner = _inner(box, outline)
    content = cell.content
    try:
        if isinstance(content, ImageContent):
            with Image.open(content.path) as source:
                picture = fit_image(source.convert("RGBA"), inner.w, inner.h)
            x = inner.x + (inner.w - picture.width) // 2
            y = inner.y + (inner.h - picture.height) // 2
            canvas.paste(picture, (x, y), picture)
            return
        fitted = fit_text(content.text, inner.w, inner.h)
    except ContentDoesNotFit as err:
        raise ContentDoesNotFit(f"shape {index + 1}: {err}") from err
    face = font(fitted.size)
    y = inner.y + (inner.h - fitted.height) // 2
    for line in fitted.lines:
        x = inner.x + (inner.w - round(face.getlength(line))) // 2
        draw.text((x, y), line, font=face, fill=content.color)
        y += fitted.line_height


def render(poster: Poster) -> Image.Image:
    """Lay out the cells in an evenly spaced grid and draw each one."""
    page = poster.page
    canvas = Image.new("RGB", (page.width_px, page.height_px), page.background)
    boxes = equal_grid(len(poster.cells), page, poster.columns)
    outline = _outline_px(poster)
    for index, (cell, box) in enumerate(zip(poster.cells, boxes, strict=True)):
        _draw_cell(canvas, cell, box, outline, index)
    return canvas


def render_to_file(poster: Poster, out: Path) -> Path:
    """Render and save as PNG, recording the print resolution in the file."""
    out.parent.mkdir(parents=True, exist_ok=True)
    dpi = poster.page.dpi
    render(poster).save(out, format="PNG", dpi=(dpi, dpi))
    return out
