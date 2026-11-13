"""The poster spec: a page, and the shapes laid out on it.

A shape holds exactly one thing: a plain text blob or an image. No rich text, no bullets.
"""

from __future__ import annotations

import re
from enum import StrEnum
from pathlib import Path
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

HEX_COLOR = r"^#[0-9A-Fa-f]{6}$"
_BULLET = re.compile(r"(^|\n)\s*([-*+•]|\d+[.)])\s+")


class ShapeKind(StrEnum):
    """The shapes the layout engine can place. New shapes land one per roadmap phase."""

    RECTANGLE = "rectangle"


class Orientation(StrEnum):
    PORTRAIT = "portrait"
    LANDSCAPE = "landscape"


class Page(BaseModel):
    """The printed page. Sizes are in inches; the pixel size follows from `dpi`."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    width_in: float = Field(default=11.0, gt=0)
    height_in: float = Field(default=8.5, gt=0)
    dpi: int = Field(default=150, ge=36, le=600)
    margin_in: float = Field(default=0.5, ge=0)
    gap_in: float = Field(default=0.25, ge=0)
    background: str = Field(default="#FFFFFF", pattern=HEX_COLOR)

    @property
    def orientation(self) -> Orientation:
        if self.width_in >= self.height_in:
            return Orientation.LANDSCAPE
        return Orientation.PORTRAIT

    def px(self, inches: float) -> int:
        """Convert inches to whole pixels at this page's resolution."""
        return round(inches * self.dpi)

    @property
    def width_px(self) -> int:
        return self.px(self.width_in)

    @property
    def height_px(self) -> int:
        return self.px(self.height_in)


class TextContent(BaseModel):
    """A plain text blob. Whitespace is collapsed; list markers are refused."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    kind: Literal["text"] = "text"
    text: str
    color: str = Field(default="#000000", pattern=HEX_COLOR)

    @field_validator("text")
    @classmethod
    def _plain(cls, value: str) -> str:
        if _BULLET.search(value):
            raise ValueError(
                "text must be a plain blob: bullets and numbered lists are not allowed"
            )
        collapsed = " ".join(value.split())
        if not collapsed:
            raise ValueError("text must not be empty")
        return collapsed


class ImageContent(BaseModel):
    """An image file, scaled to fit its shape without distortion."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    kind: Literal["image"] = "image"
    path: Path


Content = Annotated[TextContent | ImageContent, Field(discriminator="kind")]


class Cell(BaseModel):
    """One shape on the page and the one thing it holds."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    shape: ShapeKind = ShapeKind.RECTANGLE
    content: Content
    fill: str = Field(default="#FFFFFF", pattern=HEX_COLOR)


class Poster(BaseModel):
    """A page and the shapes on it. `columns` is optional: by default the engine picks it."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    page: Page = Page()
    cells: list[Cell] = Field(min_length=1)
    columns: int | None = Field(default=None, ge=1)
