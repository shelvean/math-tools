#!/usr/bin/env node
// Headless RENDER test for vendored MathJax tools.
//
// The offline smoke-test proves files exist and parse; it does NOT prove the
// page renders. This one actually executes the vendored MathJax (in jsdom) with
// the page's real config and asserts that math typesets to `mjx-container` and
// that no startup fetch escapes to a CDN. That is the check that catches a
// missing/CDN-reaching a11y component, which static checks miss.
//
// Requires jsdom:  npm install jsdom   (not a committed dependency)
// Usage:  node scripts/render-test.mjs [file.html ...]
//
// Exit 0 = rendered; non-zero = render failure. If jsdom is not installed it
// SKIPS with a warning (exit 0) so it never blocks an environment without it.

import { readFileSync, existsSync } from 'node:fs';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const TARGETS = process.argv.slice(2).length ? process.argv.slice(2) : ['taylorseries.html'];

let JSDOM;
try { ({ JSDOM } = await import('jsdom')); }
catch { console.log('! jsdom not installed — skipping render test (npm install jsdom to enable)'); process.exit(0); }

const SAMPLE = '\\(T_3(x)=x-\\dfrac{1}{6}x^3+\\dfrac{1}{120}x^5\\)';
let failures = 0;

function extract(html, re) { const m = html.match(re); return m ? m[0] : null; }

function renderOne(rel) {
  return new Promise((res) => {
    const htmlPath = resolve(ROOT, rel);
    if (!existsSync(htmlPath)) { console.log(`  ✗ ${rel}: file not found`); return res(false); }
    const src = readFileSync(htmlPath, 'utf8');
    const cfg = extract(src, /window\.MathJax\s*=\s*\{[\s\S]*?\n\s*\};/);
    const mj = extract(src, /vendor\/[^"']*tex-chtml\.js/);
    if (!mj) { console.log(`  – ${rel}: no vendored MathJax (skipped)`); return res(true); }

    const page = `<!DOCTYPE html><html><head>${cfg ? '<script>' + cfg + '</script>' : ''}` +
      `<script src="${mj}"></script></head><body><p id="m">${SAMPLE}</p></body></html>`;
    const dom = new JSDOM(page, { runScripts: 'dangerously', resources: 'usable',
      pretendToBeVisual: true, url: 'file://' + ROOT + '/__rendertest.html' });
    const { window } = dom;

    // Trip a flag if MathJax tries to reach any non-local URL during startup.
    let cdnHit = null;
    const origCreate = window.document.createElement.bind(window.document);
    window.document.createElement = (tag) => {
      const el = origCreate(tag);
      if (String(tag).toLowerCase() === 'script') {
        const setSrc = Object.getOwnPropertyDescriptor(window.HTMLScriptElement.prototype, 'src');
        try {
          Object.defineProperty(el, 'src', {
            set(v) { if (/^https?:\/\//i.test(v)) cdnHit = v; setSrc.set.call(this, v); },
            get() { return setSrc.get.call(this); }, configurable: true,
          });
        } catch {}
      }
      return el;
    };

    let done = false;
    const finish = (ok, msg) => { if (done) return; done = true; try { dom.window.close(); } catch {}
      console.log(`  ${ok ? '✓' : '✗'} ${rel}: ${msg}`); if (!ok) failures++; res(ok); };
    const poll = setInterval(() => {
      const M = window.MathJax;
      if (M && M.startup && M.startup.promise) {
        clearInterval(poll);
        M.startup.promise.then(() => M.typesetPromise && M.typesetPromise()).then(() => {
          const h = window.document.getElementById('m').innerHTML;
          const rendered = h.includes('mjx-container');
          if (cdnHit) return finish(false, `startup reached CDN: ${cdnHit}`);
          finish(rendered, rendered
            ? `rendered${h.includes('assistive-mml') ? ' (+assistive MathML)' : ''}`
            : 'NO mjx-container produced');
        }).catch((e) => finish(false, `startup/typeset rejected: ${e && e.message || e}`));
      }
    }, 150);
    setTimeout(() => { clearInterval(poll); finish(false, 'TIMEOUT (startup never resolved — likely a blocked component fetch)'); }, 30000);
  });
}

console.log('Headless MathJax render test');
for (const t of TARGETS) await renderOne(t);
console.log(failures ? `\nFAILED: ${failures} render failure(s)` : '\nRENDER OK');
process.exit(failures ? 1 : 0);
