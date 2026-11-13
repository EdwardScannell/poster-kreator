# Roadmap

poster-kreator is built in small phases. Each lands as its own pull request with tests,
and CI stays green on every commit. Each shape is its own phase because the way content
fits inside it is different geometry.

0. [x] **Skeleton.** Package, the poster spec (page, cells, plain text or image), the
   `poster` command line, CI on Python 3.11 to 3.13.
1. [x] **Rectangles, equally spaced.** Any number of rectangles on one page in an evenly
   spaced grid (the engine picks rows and columns, or you set them). Each holds a text
   blob, wrapped and shrunk to fit, or an image, scaled without distortion. Rendered to
   PNG from a JSON spec.
2. [ ] **Triangles, equally spaced.** Text fits the largest rectangle inside the triangle.
3. [ ] **Squares, equally spaced.** Square cells in a grid of any page shape.
4. [ ] **Ovals, equally spaced.** Text fits the inscribed rectangle; images are masked to
   the oval.
5. [ ] **Diamonds, equally spaced.**
6. [ ] **Hexagons, equally spaced,** including an offset honeycomb row option.
7. [ ] **Stars, equally spaced.** A five-point star is concave: content fits the inner
   pentagon and the points stay decorative. The hard fit case.
8. [ ] **Mixed shapes** in one layout, still equally spaced.

Later:

- [ ] Colored borders per shape
- [ ] Optional header and footer banners (any shape, or none)
- [ ] Per-shape size and rotation
- [ ] Portrait and landscape presets, and paper sizes
- [ ] Radial layout (a cycle or wheel diagram) and strip layout
- [ ] Print-ready export: PDF, high resolution, bleed-aware
- [ ] Templates: classroom word wall, event sign, poster, cork board
- [ ] Published as an installable package

## Never

- Rich text, bullets or markup inside a shape: one plain blob or one image.
- Silently clipped content: it fits, or the render fails and names the shape.
- Network calls.
