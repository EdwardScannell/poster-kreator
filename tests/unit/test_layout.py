import itertools

import pytest

from poster_kreator.layout import Box, LayoutError, choose_columns, equal_grid
from poster_kreator.model import Page

LANDSCAPE = Page()
PORTRAIT = Page(width_in=8.5, height_in=11)


def _gaps(boxes: list[Box]) -> set[int]:
    gaps: set[int] = set()
    for a, b in itertools.pairwise(boxes):
        if a.y == b.y:
            gaps.add(b.x - a.right)
    rows = sorted({box.y for box in boxes})
    height = boxes[0].h
    gaps.update(lower - (upper + height) for upper, lower in itertools.pairwise(rows))
    return gaps


@pytest.mark.parametrize(
    ("count", "page", "expected"),
    [(1, LANDSCAPE, 1), (4, LANDSCAPE, 2), (4, PORTRAIT, 2), (6, LANDSCAPE, 3), (6, PORTRAIT, 2)],
)
def test_columns_follow_the_page(count: int, page: Page, expected: int) -> None:
    assert choose_columns(count, page) == expected


@pytest.mark.parametrize("count", [1, 2, 3, 4, 5, 6, 7, 8, 9, 12])
@pytest.mark.parametrize("page", [LANDSCAPE, PORTRAIT])
def test_boxes_are_equal_and_equally_spaced(count: int, page: Page) -> None:
    boxes = equal_grid(count, page)
    assert len(boxes) == count
    assert len({(box.w, box.h) for box in boxes}) == 1
    if count > 1:
        assert _gaps(boxes) == {page.px(page.gap_in)}


@pytest.mark.parametrize("page", [LANDSCAPE, PORTRAIT])
def test_boxes_stay_inside_the_margins(page: Page) -> None:
    margin = page.px(page.margin_in)
    for box in equal_grid(6, page):
        assert box.x >= margin and box.y >= margin
        assert box.right <= page.width_px - margin
        assert box.bottom <= page.height_px - margin


def test_grid_is_centered() -> None:
    boxes = equal_grid(4, LANDSCAPE)
    left = boxes[0].x
    right = LANDSCAPE.width_px - max(box.right for box in boxes)
    assert abs(left - right) <= 1


def test_short_last_row_is_centered() -> None:
    boxes = equal_grid(5, LANDSCAPE)
    last = [box for box in boxes if box.y == boxes[-1].y]
    assert len(last) == 2
    left = last[0].x
    right = LANDSCAPE.width_px - last[-1].right
    assert abs(left - right) <= 1


def test_columns_can_be_set() -> None:
    boxes = equal_grid(6, LANDSCAPE, columns=2)
    assert len({box.x for box in boxes}) == 2
    assert len({box.y for box in boxes}) == 3


def test_more_columns_than_shapes_is_clamped() -> None:
    assert len({box.y for box in equal_grid(3, LANDSCAPE, columns=10)}) == 1


def test_zero_shapes_is_an_error() -> None:
    with pytest.raises(LayoutError):
        equal_grid(0, LANDSCAPE)
    with pytest.raises(LayoutError):
        choose_columns(0, LANDSCAPE)


def test_too_many_shapes_is_an_error() -> None:
    tiny = Page(width_in=1, height_in=1, dpi=36, margin_in=0.4, gap_in=0.1)
    with pytest.raises(LayoutError, match="do not fit"):
        equal_grid(40, tiny, columns=40)
