"""The `poster` command line."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer
from pydantic import ValidationError

from poster_kreator import __version__
from poster_kreator.fit import ContentDoesNotFit
from poster_kreator.layout import LayoutError, equal_grid
from poster_kreator.model import ShapeKind
from poster_kreator.render import load_spec, render_to_file

app = typer.Typer(help="Arrange equally spaced shapes on a page.", no_args_is_help=True)


@app.command()
def version() -> None:
    """Print the version."""
    typer.echo(__version__)


@app.command()
def shapes() -> None:
    """List the shapes this version can place."""
    typer.echo(" ".join(kind.value for kind in ShapeKind))


@app.command()
def layout(spec: Path) -> None:
    """Print where each shape will sit (pixels: x y width height)."""
    poster = load_spec(spec)
    boxes = equal_grid(len(poster.cells), poster.page, poster.columns)
    for number, box in enumerate(boxes, start=1):
        typer.echo(f"{number}: {box.x} {box.y} {box.w} {box.h}")


@app.command()
def render(
    spec: Path,
    out: Annotated[Path, typer.Option("--out", "-o", help="Where to write the PNG.")] = Path(
        "poster.png"
    ),
) -> None:
    """Render a JSON spec to a print-resolution PNG."""
    try:
        written = render_to_file(load_spec(spec), out)
    except (ValidationError, ContentDoesNotFit, LayoutError, FileNotFoundError) as err:
        typer.echo(f"error: {err}", err=True)
        raise typer.Exit(code=1) from err
    typer.echo(f"wrote {written}")
