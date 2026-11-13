"""Equal-spacing layout: where each shape sits on the page.

Every shape gets the same size box, every gap between boxes is the same, and the grid
is centered inside the page margins. A short last row is centered with the same gap.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from poster_kreator.model import Page


@dataclass(frozen=True)
class Box:
    """A shape's bounding box in pixels: top-left corner, width and height."""

    x: int
    y: int
    w: int
    h: int

    @property
    def right(self) -> int:
        return self.x + self.w

    @property
    def bottom(self) -> int:
        return self.y + self.h


class LayoutError(ValueError):
    """The requested layout cannot fit on the page."""


def _cell_size(count: int, columns: int, page: Page) -> tuple[int, int, int]:
    """Return (rows, cell width, cell height) in whole pixels for a column count."""
    rows = math.ceil(count / columns)
    gap = page.px(page.gap_in)
    usable_w = page.width_px - 2 * page.px(page.margin_in)
    usable_h = page.height_px - 2 * page.px(page.margin_in)
    cell_w = (usable_w - (columns - 1) * gap) // columns
    cell_h = (usable_h - (rows - 1) * gap) // rows
    return rows, cell_w, cell_h


def choose_columns(count: int, page: Page) -> int:
    """Pick the column count that makes the shapes largest.

    The score is a cell's shorter side; ties go to fewer empty slots, then to the
    arrangement that follows the page's orientation.
    """
    if count < 1:
        raise LayoutError("a layout needs at least one shape")
    best: tuple[int, int, int] | None = None
    best_columns = 1
    for columns in range(1, count + 1):
        rows, cell_w, cell_h = _cell_size(count, columns, page)
        empty = rows * columns - count
        follows_page = int((columns >= rows) == (page.width_px >= page.height_px))
        score = (min(cell_w, cell_h), -empty, follows_page)
        if best is None or score > best:
            best, best_columns = score, columns
    return best_columns


def equal_grid(count: int, page: Page, columns: int | None = None) -> list[Box]:
    """Lay out `count` equal boxes in an evenly spaced grid, row by row."""
    if count < 1:
        raise LayoutError("a layout needs at least one shape")
    cols = choose_columns(count, page) if columns is None else min(columns, count)
    rows, cell_w, cell_h = _cell_size(count, cols, page)
    if cell_w < 1 or cell_h < 1:
        raise LayoutError(
            f"{count} shapes in {cols} columns do not fit on the page: "
            "reduce the margin or gap, or use fewer shapes"
        )
    gap = page.px(page.gap_in)
    grid_h = rows * cell_h + (rows - 1) * gap
    top = (page.height_px - grid_h) // 2
    boxes: list[Box] = []
    for row in range(rows):
        in_row = min(cols, count - row * cols)
        row_w = in_row * cell_w + (in_row - 1) * gap
        left = (page.width_px - row_w) // 2
        y = top + row * (cell_h + gap)
        boxes.extend(Box(left + i * (cell_w + gap), y, cell_w, cell_h) for i in range(in_row))
    return boxes
