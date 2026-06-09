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

The full MathJax `es5` tree is ~24 MB (SVG output, input components, multiple
font formats). CHTML output only needs the combined `es5/tex-chtml.js` plus the
fonts in `es5/output/chtml/fonts/woff-v2/`, so only that minimal set (~1.5 MB) is
vendored. MathJax resolves its root — and therefore the font directory — from the
`<script src>` location, so the relative path `vendor/mathjax@3.2.2/es5/tex-chtml.js`
makes it load fonts from the vendored tree automatically. **Do not flatten** the
`es5/output/chtml/fonts/woff-v2/` path.

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

## Migration status

Vendoring is being rolled out tool by tool. **Vendored so far:**

- `taylorseries.html` — pilot (MathJax, math.js, D3)

Tools not yet migrated still load these libraries from pinned CDN URLs.
