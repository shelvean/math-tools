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
| math.js | 11.7.0 | `vendor/mathjs@11.7.0/math.js` | `registry.npmjs.org/mathjs/-/mathjs-11.7.0.tgz` | Apache-2.0 | 2026-06-09 |
| math.js | 12.0.0 | `vendor/mathjs@12.0.0/math.js` | `registry.npmjs.org/mathjs/-/mathjs-12.0.0.tgz` | Apache-2.0 | 2026-06-09 |
| math.js | 13.1.1 | `vendor/mathjs@13.1.1/math.js` | `registry.npmjs.org/mathjs/-/mathjs-13.1.1.tgz` | Apache-2.0 | 2026-06-09 |
| math.js | 12.4.2 | `vendor/mathjs@12.4.2/math.js` | `registry.npmjs.org/mathjs/-/mathjs-12.4.2.tgz` | Apache-2.0 | 2026-06-09 |
| math.js | 14.6.0 | `vendor/mathjs@14.6.0/math.js` | `registry.npmjs.org/mathjs/-/mathjs-14.6.0.tgz` | Apache-2.0 | 2026-06-09 |
| Google Fonts (woff2) | n/a | `vendor/fonts/` | `fonts.googleapis.com` CSS → `fonts.gstatic.com` woff2 (latin + latin-ext) | OFL-1.1 | 2026-06-09 |
| decimal.js | 10.4.3 | `vendor/decimal.js@10.4.3/decimal.js` | `registry.npmjs.org/decimal.js/-/decimal.js-10.4.3.tgz` | MIT | 2026-06-09 |
| Tailwind CSS (prebuilt) | 2.2.19 | `vendor/tailwindcss@2.2.19/tailwind.min.css` | `registry.npmjs.org/tailwindcss/-/tailwindcss-2.2.19.tgz` | MIT | 2026-06-09 |
| Tailwind CSS (built) | 3.4.17 | `vendor/tailwindcss@3.4.17/tailwind.build.css` | built locally from the 6 JIT pages via `tailwindcss` CLI | MIT | 2026-06-09 |
| math.js | 14.2.1 | `vendor/mathjs@14.2.1/math.js` | `registry.npmjs.org/mathjs/-/mathjs-14.2.1.tgz` | Apache-2.0 | 2026-06-09 |
| function-plot | 1.22.4 | `vendor/function-plot@1.22.4/function-plot.js` | `registry.npmjs.org/function-plot/-/function-plot-1.22.4.tgz` | MIT | 2026-06-09 |
| Vue | 3.5.13 | `vendor/vue@3.5.13/vue.global.js` | `registry.npmjs.org/vue/-/vue-3.5.13.tgz` | MIT | 2026-06-09 |
| D3 | 7.8.5 | `vendor/d3@7.8.5/d3.min.js` | `registry.npmjs.org/d3/-/d3-7.8.5.tgz` | ISC | 2026-06-09 |
| Plotly | 2.27.0 | `vendor/plotly@2.27.0/plotly.min.js` | `registry.npmjs.org/plotly.js-dist-min/-/plotly.js-dist-min-2.27.0.tgz` | MIT | 2026-06-09 |
| Plotly | 2.35.2 | `vendor/plotly@2.35.2/plotly.min.js` | `registry.npmjs.org/plotly.js-dist-min/-/plotly.js-dist-min-2.35.2.tgz` | MIT | 2026-06-09 |
| Plotly | 2.24.1 | `vendor/plotly@2.24.1/plotly.min.js` | `registry.npmjs.org/plotly.js-dist-min/-/plotly.js-dist-min-2.24.1.tgz` | MIT | 2026-06-09 |
| three.js | r128 (0.128.0) | `vendor/three@r128/three.min.js` | `registry.npmjs.org/three/-/three-0.128.0.tgz` | MIT | 2026-06-09 |
| jsPDF | 2.5.1 | `vendor/jspdf@2.5.1/jspdf.umd.min.js` | `registry.npmjs.org/jspdf/-/jspdf-2.5.1.tgz` | MIT | 2026-06-09 |
| topojson | 3.0.2 | `vendor/topojson@3.0.2/topojson.min.js` | `registry.npmjs.org/topojson/-/topojson-3.0.2.tgz` | ISC | 2026-06-09 |
| pdf-lib | 1.17.1 | `vendor/pdf-lib@1.17.1/pdf-lib.min.js` | `registry.npmjs.org/pdf-lib/-/pdf-lib-1.17.1.tgz` | MIT | 2026-06-09 |
| pdf.js (pdfjs-dist) | 3.11.174 | `vendor/pdfjs-dist@3.11.174/build/` (pdf + worker) | `registry.npmjs.org/pdfjs-dist/-/pdfjs-dist-3.11.174.tgz` | Apache-2.0 | 2026-06-09 |
| pdf.js (pdfjs-dist) | 2.11.338 | `vendor/pdfjs-dist@2.11.338/build/pdf.min.js` | `registry.npmjs.org/pdfjs-dist/-/pdfjs-dist-2.11.338.tgz` | Apache-2.0 | 2026-06-09 |
| JSZip | 3.10.1 | `vendor/jszip@3.10.1/jszip.min.js` | `registry.npmjs.org/jszip/-/jszip-3.10.1.tgz` | MIT | 2026-06-09 |
| PapaParse | 5.4.0 | `vendor/papaparse@5.4.0/papaparse.min.js` | `registry.npmjs.org/papaparse/-/papaparse-5.4.0.tgz` | MIT | 2026-06-09 |
| SheetJS (xlsx) | 0.18.5 | `vendor/xlsx@0.18.5/xlsx.full.min.js` | `registry.npmjs.org/xlsx/-/xlsx-0.18.5.tgz` | Apache-2.0 | 2026-06-09 |
| numeric | 1.2.6 | `vendor/numeric@1.2.6/numeric.min.js` | `registry.npmjs.org/numeric/-/numeric-1.2.6.tgz` | MIT* | 2026-06-09 |

\* numeric's npm tarball ships no LICENSE file; the project is MIT-licensed (Sébastien Loisel).

### MathJax footprint + the a11y/CDN gotcha

The full MathJax `es5` tree is ~24 MB. We vendor only the subset the tools use (~2.6 MB):

- `es5/tex-chtml.js` — combined TeX-input + CHTML-output (bundles the font *data*)
- `es5/output/chtml/fonts/woff-v2/` — the actual `.woff` glyph files CHTML fetches
- `es5/a11y/assistive-mml.js` — accessible MathML for screen readers (self-contained)
- `es5/input/tex/extensions/` — autoloaded TeX extensions (e.g. `boldsymbol`,
  `cancel`, `color`). MathJax fetches these **on demand** when a macro like
  `\boldsymbol` appears, so a page can render simple math fine yet fail on richer
  content if they're missing. The render-test exercises `\boldsymbol` to guard this.

MathJax resolves its root — and therefore the font/component directories — from
the `<script src>` location, so `vendor/mathjax@3.2.2/es5/tex-chtml.js` makes it
load everything from the vendored tree. **Do not flatten** the `es5/...` substructure.

> **Important — MathJax config must avoid the SRE path.** MathJax *lazy-loads*
> a11y components at startup based on the page config. Two traps:
> 1. If an enabled component isn't vendored, startup **rejects and nothing renders
>    at all** (math.js/D3 still work, so it looks MathJax-specific).
> 2. The **explorer/speech** path pulls in the Speech Rule Engine (`a11y/sre.js`),
>    which has **hard-coded `cdn.jsdelivr.net` URLs** (speech-rule-engine,
>    sre-mathmaps-ie, wicked-good-xpath) — so it is *not* CDN-independent and can
>    break offline.
>
> Therefore the vendored config keeps **only `enableAssistiveMml`** (self-contained,
> no CDN reach) and omits `enableExplorer` / `a11y.speech`:
> ```js
> options:{ enableAssistiveMml:true, skipHtmlTags:[...] }
> ```
> The smoke-test asserts that whatever a11y features a page enables are vendored;
> the render-test (below) proves the page actually typesets with no CDN reach.

GitHub Pages note: a root `.nojekyll` file is committed so Pages serves the
`vendor/` tree verbatim.

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

It does **not** execute MathJax. For that, use the render-test:

```sh
npm install jsdom              # one-time, not a committed dependency
node scripts/render-test.mjs   # default: vendored tools
```

This actually runs the page's real MathJax config against the vendored files in a
headless DOM, asserts the sample typesets to `mjx-container`, and **fails if
startup reaches any `http(s)://` URL** — i.e. it catches both "doesn't render" and
"secretly hits a CDN". It skips gracefully (exit 0) if jsdom isn't installed.

## Migration status

Vendoring is being rolled out tool by tool. **Vendored so far:**

- `taylorseries.html` — pilot (MathJax, math.js, D3)
- `finitediff.html` (MathJax, Plotly)
- `leastsquaresdata.html` (MathJax, math.js, D3, PapaParse, xlsx)
- `leastsquaresrational.html` (MathJax, math.js, numeric, D3)
- MathJax-only batch: `businessmath`, `linear`, `numerical`, `series`, `duffing`, `poincare`
  (`duffing`/`poincare` use the `tex-mml-chtml` entry, also vendored)
- MathJax-only tier-1 (config normalized to assistive-MathML-only + vendored, 27):
  `bifurcation`, `cmrfactor`, `coupled`, `cr`, `determinants`, `dynamical`,
  `elastic_pendulum`, `ffs`, `finance`, `forcing`, `generalizedinverse`,
  `gramschmidtorthogonal`, `linearequation`, `linearportrait`, `lineartransform`,
  `massspring-horizontal`, `massspring`, `matrixvectorviz`, `projects`, `refsolver`,
  `rref`, `rrefsolver`, `slope`, `svdcompute`, `tipe-cycles-boucles`,
  `transformations2d`, `vanderpol`
- MathJax + Plotly 2.35.2 batch (config normalized + vendored, 10): `cobweb`,
  `convolution`, `laplace`, `logistic`, `lorenzsystem`, `lotkavolterra`,
  `lvcarrying`, `malkus-flywheel`, `newton`, `rossler`
- math.js batch (config normalized + MathJax/math.js/D3/decimal.js vendored, 15):
  `choleskyfactors`, `diag`, `eigenvalues-eigenvectors`, `leastsquaresnormaleqns`,
  `leastsquaresqr`, `leastsquaressvd`, `lufactor`, `qrfactor`, `interpolation` (+D3),
  `phaseline` (+D3, +decimal.js), `multi_pendulum`, `pend`, `pendulum_simulator`,
  `swinging_atwood`, `nonlinearphaseportraits`
- static-Tailwind batch (vendored prebuilt Tailwind 2.2.19 CSS + config normalized, 8):
  `changebasis`, `changebasisviz`, `elementary`, `gradecalc` (no MathJax; D3 + xlsx),
  `inversematrix`, `lineareqn`, `nonlinear` (+math.js), `svd2d`
- stragglers batch (Plotly 2.24.1 / three.js r128 / jsPDF 2.5.1 / topojson 3.0.2 vendored
  + config normalized, 12): `about` (D3+topojson), `statesdata` (D3+topojson),
  `geometry2d` (+D3), `graphtransform` (+D3), `bifurcation-family` (+D3),
  `detviz` (+D3+three.js), `cooling` (+Plotly 2.27.0), `integration` (MathJax tex-svg
  + Plotly 2.27.0), `fourier` (+math.js+Plotly 2.24.1), `bisection`, `pendulum_wave`,
  `seatallocator` (jsPDF+Plotly 2.27.0)

The MathJax `tex-svg.js` entry (SVG output, used by `integration`) is also vendored.
- Google-Fonts batch (self-hosted woff2 + config normalized, 4): `double_potential`,
  `potential` (IBM Plex Sans/Serif), `prod` (Atkinson Hyperlegible, +math.js 12.4.2),
  `odeclassify` (IBM Plex Mono/Sans/Serif)
- PDF tools batch (pdf-lib / pdf.js / JSZip vendored, 4): `pdf_dark` (pdf.js 3.11.174
  + worker, pdf-lib), `pdf_extract` (pdf.js 2.11.338, pdf-lib, JSZip), `pdf_manager`
  (pdf-lib), `pdf_sort` (pdf.js 2.11.338, pdf-lib). For pdf_dark, `workerSrc` is
  repointed to the vendored worker; the v2 tools use pdf.js's main-thread fallback
  (no workerSrc, unchanged). `pdftools.html` is a static page with no libraries.
- Tailwind JIT-runtime batch (6): `corners`, `corners_v1` (+Plotly 2.24.1, +fonts),
  `mathjs` (+math.js 14.2.1), `plotfunction` (+function-plot, +math.js 13.1.1, +D3),
  `slopev1`, `timer` (+Vue 3.5.13, +fonts). The `cdn.tailwindcss.com` in-browser
  compiler was **replaced** by a Tailwind v3 build (`tailwind.build.css`, generated
  by scanning all 6 pages — including their inline JS, so dynamically-applied
  classes are captured). Google Fonts for `corners`/`corners_v1`/`timer` were
  self-hosted into `vendor/fonts/`.

> **The Tailwind JIT runtime can't be vendored as a file** — it compiles utility
> classes in the browser. We instead run the Tailwind CLI over the pages to emit a
> static CSS. To regenerate after editing any of the 6 pages' classes:
> ```sh
> npx tailwindcss@3.4.17 -i in.css -o vendor/tailwindcss@3.4.17/tailwind.build.css --minify \
>   --content "corners.html,corners_v1.html,mathjs.html,plotfunction.html,slopev1.html,timer.html"
> ```
> (`in.css` = the three `@tailwind base/components/utilities` directives.)

**All math/visualization tools are now self-hosted — no third-party CDN at runtime
(only optional, async, non-blocking Google Analytics remains).**

> **Self-hosted fonts:** Google Fonts CSS was fetched and rewritten to load woff2
> from `vendor/fonts/` (latin + latin-ext subsets only — these are English tools).
> Each tool has a small `vendor/fonts/<tool>.css`; woff2 files are shared/deduped.
> Fonts are licensed OFL-1.1 (IBM Plex, Atkinson Hyperlegible).

> **Tailwind, two kinds:** the *prebuilt* `tailwindcss@2.2.19/dist/tailwind.min.css`
> is a complete CSS file, vendored 1:1 (safe). The `cdn.tailwindcss.com` **JIT
> runtime** (used by `corners`, `corners_v1`, `mathjs`, `plotfunction`, `slopev1`,
> `timer`) compiles utility classes in the browser and can't be vendored as-is —
> it needs a Tailwind build producing a CSS file for those pages (a separate task).

Tools not yet migrated still load these libraries from pinned CDN URLs.
Each migrated tool is gated by both `offline-smoke-test.mjs` and `render-test.mjs`.
