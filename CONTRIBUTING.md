# Contributing

## Setup

```bash
python -m venv .venv && . .venv/bin/activate
make install
make check           # lint, strict types, tests with coverage (must stay >= 90%)
```

## The rules for changes

1. **Equal spacing is the contract.** Every layout keeps the same gap between shapes and
   the same margin around the page; a test proves it for each new layout.
2. **Plain content only.** A shape holds one plain text blob or one image. No rich text,
   no bullets, no markup.
3. **Content never spills.** Text is wrapped and shrunk to fit its shape, or the render
   fails with a clear error naming the shape. It is never silently clipped.
4. **Deterministic output.** The same spec renders the same image on every run.
5. **One shape per phase.** Each new shape lands with its own fit rule and tests.
6. **Every bug gets a regression test first**, in `tests/regression/`, named after it.
7. **Keep the public API typed.** `mypy --strict` must pass.

## Pull requests

- One topic per PR, with a test that fails before the change and passes after.
- Update `CHANGELOG.md` and tick the phase in `ROADMAP.md` when it is complete.

## Fixtures

Sample images are generated or made for this repository. Do not add images you do not
have the right to share.
