#!/usr/bin/env node
// Offline smoke-test for vendored tools — no browser, no npm deps (pure Node).
//
// For each HTML file given (default: the vendored tools), it verifies the page
// is genuinely self-contained at runtime:
//   1. every runtime <script src> / stylesheet <link href> is a LOCAL path
//      (zero http(s):// or protocol-relative CDN URLs),
//   2. each referenced local file exists on disk,
//   3. each local .js parses (node --check),
//   4. vendored math.js is FUNCTIONALLY exercised (evaluate / parse / factorial),
//   5. if MathJax is used, tex-chtml.js and its woff-v2 font dir are present.
//
// Exit code 0 = all good; non-zero = at least one failure. Meta/SEO tags
// (canonical, og:*, twitter:*, JSON-LD) are intentionally NOT checked — those
// are allowed to stay absolute.
//
// Usage:  node scripts/offline-smoke-test.mjs [file.html ...]

import { readFileSync, existsSync, statSync, readdirSync } from 'node:fs';
import { execFileSync } from 'node:child_process';
import { dirname, resolve, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const TARGETS = process.argv.slice(2).length ? process.argv.slice(2) : ['taylorseries.html'];

let failures = 0;
const fail = (m) => { failures++; console.log('  \x1b[31m✗\x1b[0m ' + m); };
const pass = (m) => console.log('  \x1b[32m✓\x1b[0m ' + m);
const warn = (m) => console.log('  \x1b[33m!\x1b[0m ' + m);

const isExternal = (u) => /^(https?:)?\/\//i.test(u) || /^data:/i.test(u);
// Hosts that are non-blocking telemetry: loaded async + guarded, so the tool
// still works if they're blocked/dead. Flagged as a warning, not a failure.
const ANALYTICS_HOSTS = [/googletagmanager\.com/i, /google-analytics\.com/i];
const isAnalytics = (u) => ANALYTICS_HOSTS.some((re) => re.test(u));

// Pull <script src="..."> and stylesheet <link ... href="..."> — the runtime deps.
function runtimeRefs(html) {
  const refs = [];
  for (const m of html.matchAll(/<script\b[^>]*\bsrc=["']([^"']+)["'][^>]*>/gi))
    refs.push({ kind: 'script', url: m[1] });
  for (const m of html.matchAll(/<link\b[^>]*>/gi)) {
    const tag = m[0];
    const rel = (tag.match(/\brel=["']([^"']+)["']/i) || [])[1] || '';
    const href = (tag.match(/\bhref=["']([^"']+)["']/i) || [])[1];
    if (!href) continue;
    if (/stylesheet/i.test(rel) || (/preload/i.test(rel) && /\bas=["'](script|style|font)["']/i.test(tag)))
      refs.push({ kind: 'link(' + rel + ')', url: href });
  }
  return refs;
}

function checkJsParses(absPath) {
  try { execFileSync(process.execPath, ['--check', absPath], { stdio: 'pipe' }); return true; }
  catch (e) { return false; }
}

async function smokeMathjs(absPath) {
  const mod = await import('file://' + absPath);
  const math = mod.default || mod;
  const checks = [
    ['evaluate("2+3*4")===14', math.evaluate('2+3*4') === 14],
    ['factorial(5)===120', math.factorial(5) === 120],
    ['parse("sin(x)").compile().evaluate({x:0})===0',
      math.parse('sin(x)').compile().evaluate({ x: 0 }) === 0],
  ];
  return checks;
}

function checkMathjaxFonts(htmlDir, scriptUrl) {
  // scriptUrl like vendor/mathjax@3.2.2/es5/tex-chtml.js -> fonts under es5/output/chtml/fonts/woff-v2
  const es5 = resolve(htmlDir, dirname(scriptUrl));
  const fontDir = join(es5, 'output', 'chtml', 'fonts', 'woff-v2');
  if (!existsSync(fontDir)) return fail('MathJax font dir missing: ' + fontDir);
  const fonts = readdirSync(fontDir).filter((f) => /\.woff2?$/.test(f));
  if (!fonts.length) return fail('MathJax font dir has no .woff/.woff2 files');
  if (!fonts.some((f) => /Main-Regular/.test(f)))
    return fail('MathJax core font MathJax_Main-Regular missing');
  pass(`MathJax fonts present (${fonts.length} files, incl. Main-Regular)`);
}

// If the page's MathJax config enables a11y features, those components are
// lazy-loaded at startup from the vendored es5 tree — if missing, MathJax fails
// to render at all. Assert each enabled feature's component is present.
function checkMathjaxComponents(htmlDir, scriptUrl, html) {
  const es5 = resolve(htmlDir, dirname(scriptUrl));
  const need = [];
  if (/enableAssistiveMml\s*:\s*true/.test(html)) need.push(['assistiveMml', 'a11y/assistive-mml.js']);
  if (/enableExplorer\s*:\s*true/.test(html)) {
    need.push(['explorer', 'a11y/explorer.js']);
    need.push(['explorer→semantic-enrich', 'a11y/semantic-enrich.js']);
  }
  if (/\bspeech\s*:\s*true/.test(html)) need.push(['speech (SRE)', 'sre']);
  if (!need.length) return;
  for (const [feat, rel] of need) {
    const p = join(es5, rel);
    const ok = existsSync(p) && (statSync(p).isFile() || readdirSync(p).length > 0);
    ok ? pass(`MathJax a11y component for ${feat}: ${rel}`)
       : fail(`MathJax config enables ${feat} but component missing: ${rel} (MathJax will fail to render)`);
  }
}

for (const rel of TARGETS) {
  const htmlPath = resolve(ROOT, rel);
  console.log('\n\x1b[1m' + rel + '\x1b[0m');
  if (!existsSync(htmlPath)) { fail('file not found'); continue; }
  const html = readFileSync(htmlPath, 'utf8');
  const htmlDir = dirname(htmlPath);
  const refs = runtimeRefs(html);

  const external = refs.filter((r) => isExternal(r.url));
  const blocking = external.filter((r) => !isAnalytics(r.url));
  const telemetry = external.filter((r) => isAnalytics(r.url));
  if (blocking.length) blocking.forEach((r) => fail(`external library/CDN runtime dep (${r.kind}): ${r.url}`));
  else pass(`no external library/CDN runtime deps (${refs.length - external.length} local runtime refs)`);
  telemetry.forEach((r) => warn(`non-blocking telemetry (async, guarded): ${r.url}`));

  for (const r of refs.filter((x) => !isExternal(x.url))) {
    const abs = resolve(htmlDir, r.url.split(/[?#]/)[0]);
    if (!existsSync(abs) || !statSync(abs).isFile()) { fail(`missing local file: ${r.url}`); continue; }
    if (abs.endsWith('.js')) {
      if (checkJsParses(abs)) pass(`parses: ${r.url}`);
      else { fail(`parse error: ${r.url}`); continue; }
      if (/mathjs.*\.js$/.test(abs) || /\/math\.js$/.test(abs)) {
        try {
          const checks = await smokeMathjs(abs);
          checks.forEach(([d, ok]) => ok ? pass('math.js ' + d) : fail('math.js ' + d));
        } catch (e) { fail('math.js failed to load/run: ' + e.message); }
      }
    } else {
      pass(`present: ${r.url}`);
    }
    if (/tex-chtml\.js$/.test(abs)) { checkMathjaxFonts(htmlDir, r.url); checkMathjaxComponents(htmlDir, r.url, html); }
  }
}

console.log('\n' + (failures ? `\x1b[31mFAILED: ${failures} issue(s)\x1b[0m` : '\x1b[32mALL CHECKS PASSED\x1b[0m'));
process.exit(failures ? 1 : 0);
