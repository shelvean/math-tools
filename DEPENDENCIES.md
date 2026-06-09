# Vendored dependencies

To keep the tools durable, runtime libraries are **self-hosted** in `/vendor`
instead of loaded from third-party CDNs. A CDN going away, renaming, or shipping
a breaking release can no longer break a vendored tool — the only runtime
dependency is this repository's own host. Vendored tools also work fully offline.

Each library lives under `vendor/<name>@<exact-version>/` with its upstream
`LICENSE`. All are permissively licensed (Apache-2.0 / ISC), which allows
redistribution.

## Manifest

| Library | Version | Vendored path | Source (npm tarball) | License | Date |
|---|---|---|---|---|---|
| MathJax (CHTML) | 3.2.2 | `vendor/mathjax@3.2.2/es5/` | `registry.npmjs.org/mathjax/-/mathjax-3.2.2.tgz` | Apache-2.0 | 2026-06-09 |
| math.js | 11.9.1 | `vendor/mathjs@11.9.1/math.js` | `registry.npmjs.org/mathjs/-/mathjs-11.9.1.tgz` | Apache-2.0 | 2026-06-09 |
| D3 | 7.8.5 | `vendor/d3@7.8.5/d3.min.js` | `registry.npmjs.org/d3/-/d3-7.8.5.tgz` | ISC | 2026-06-09 |

### MathJax footprint note

The full MathJax `es5` tree is ~24 MB (SVG output, MathML input, multiple font
formats). We vendor only the subset the tools actually use (~6 MB):

- `es5/tex-chtml.js` — combined TeX-input + CHTML-output (bundles the font *data*)
- `es5/output/chtml/fonts/woff-v2/` — the actual `.woff` glyph files CHTML fetches
- `es5/a11y/` and `es5/sre/` — accessibility components (assistive MathML,
  explorer, speech rules)

MathJax resolves its root — and therefore the font and component directories —
from the `<script src>` location, so the relative path
`vendor/mathjax@3.2.2/es5/tex-chtml.js` makes it load everything from the vendored
tree automatically. **Do not flatten** the `es5/...` substructure.

> **Why `a11y/` + `sre/` are required, not optional:** the tools' MathJax config
> sets `enableExplorer`, `enableAssistiveMml`, and `a11y.speech`. MathJax
> *lazy-loads* those components at startup; if they're missing, the startup
> promise rejects and **nothing renders at all** (math.js/D3 still work, so the
> failure looks MathJax-specific). The smoke-test asserts that every a11y feature
> enabled in a page's config has its component vendored.

GitHub Pages note: a root `.nojekyll` file is committed so Pages serves the
`vendor/` tree verbatim (Jekyll otherwise has special handling for some paths).

## How to vendor a new library

The sandbox network policy allows `registry.npmjs.org` and `raw.githubusercontent.com`
(not the public CDNs), so vendor from npm tarballs:

```sh
curl -sSO "https://registry.npmjs.org/<pkg>/-/<pkg>-<version>.tgz"
tar -xzf "<pkg>-<version>.tgz"           # extracts to package/
mkdir -p "vendor/<pkg>@<version>"
cp package/<dist-file> "vendor/<pkg>@<version>/"
cp package/LICENSE*    "vendor/<pkg>@<version>/"
```

Then point the tool's `<script src>` / `<link href>` at the relative
`vendor/...` path and add a row to the manifest above.

## Verifying a vendored tool (offline smoke-test)

`scripts/offline-smoke-test.mjs` is a browser-free, dependency-free Node check
that a tool's bundle is genuinely self-contained:

```sh
node scripts/offline-smoke-test.mjs            # default: vendored tools
node scripts/offline-smoke-test.mjs foo.html   # a specific file
```

It verifies that every runtime `<script src>` / stylesheet `<link>` resolves to a
local file (no library/CDN URLs), that each local `.js` parses, that vendored
math.js actually evaluates expressions, and that MathJax's `woff-v2` fonts are
present. Non-blocking analytics (loaded `async` and guarded) is reported as a
warning, not a failure — it can't break the tool. Exit code is non-zero on any
real failure, so it can be wired into CI or a SessionStart hook.

It does **not** render MathJax in a real browser, so a quick visual spot-check of
formula rendering is still worthwhile after vendoring.

## Migration status

Vendoring is being rolled out tool by tool. **Vendored so far:**

- `taylorseries.html` — pilot (MathJax, math.js, D3)

Tools not yet migrated still load these libraries from pinned CDN URLs.
