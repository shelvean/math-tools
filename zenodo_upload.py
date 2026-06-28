#!/usr/bin/env python3
"""Mint a Zenodo DOI for each interactive tool via the Zenodo REST API.

For every tool page (the same set add_citation.py cites), this script:

  1. Creates a new deposition draft (or a new version of an existing one).
  2. Uploads the tool's HTML file to the deposition.
  3. Sets metadata: title (from the page <h1>), description (from the
     page <meta name="description">), creator, license, keywords (from
     hub-page tags), and a related identifier pointing at the live page.
  4. Optionally publishes the deposition, which MINTS the DOI.
  5. Records {filename: {...doi info...}} in zenodo_dois.json, which
     add_citation.py reads to embed each DOI in the on-page citations.

Quick start
-----------
  # 1. Create a personal access token with the "deposit:write" and
  #    "deposit:actions" scopes:
  #      https://zenodo.org/account/settings/applications/tokens/new
  #      (use https://sandbox.zenodo.org/... for the sandbox)
  export ZENODO_TOKEN=xxxxxxxxxxxxxxxxxxxx

  # 2. Dry run against the sandbox to make sure everything looks right
  #    (sandbox DOIs are fake and records are wiped periodically):
  python3 zenodo_upload.py --sandbox --only newton.html --publish

  # 3. Create real drafts (no DOI minted yet) and review them in the UI:
  python3 zenodo_upload.py

  # 4. When happy, publish for real (IRREVERSIBLE — DOIs are permanent):
  python3 zenodo_upload.py --publish

State & idempotency
-------------------
Progress is tracked in zenodo_dois.json. A tool already recorded there is
skipped, so the script is safe to re-run after an interruption. To archive
an updated tool as a *new version* under the same concept DOI, pass
--new-version (optionally with --only to target specific tools).

Only the Python standard library is used (urllib) — no third-party deps.
"""
import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request

# Reuse the citation pipeline's config and HTML parsing so titles, the
# skip-list, author, and site URL stay in lock-step with add_citation.py.
from add_citation import (
    AUTHOR_FIRST,
    AUTHOR_LAST,
    BASE,
    SITE_URL,
    SKIP_PAGES,
    clean,
    extract_title,
)

STATE_FILE = os.path.join(BASE, 'zenodo_dois.json')

PROD_API = 'https://zenodo.org/api'
SANDBOX_API = 'https://sandbox.zenodo.org/api'

# Zenodo open-license id (SPDX-style). The HTML/JS/CSS that makes up each
# tool is MIT-licensed; educational prose is additionally CC BY 4.0 (noted
# in the description). One license id per record, so MIT is used here.
LICENSE_ID = 'MIT'
UPLOAD_TYPE = 'software'

KEYWORDS_BASE = [
    'mathematics education',
    'interactive visualization',
]

# Hub pages whose tool-cards carry the per-tool tag assignments. Mirrors
# generate_labels.py so keywords match the site's own taxonomy.
HUB_PAGES = [
    'projects.html', 'dynamical.html', 'linear.html',
    'numerical.html', 'optim.html', 'pdftools.html',
    'businessmath.html',
]


def build_tag_index():
    """Map tool filename -> sorted list of tag strings, by parsing the
    tool-card markup on the hub pages."""
    index = {}
    card_re = re.compile(r'<article class="tool-card".*?</article>', re.DOTALL)
    link_re = re.compile(r'<a href="([^"]+)"[^>]*class="card-link"')
    tag_re = re.compile(r'class="tag">([^<]+)</a>')
    for hub in HUB_PAGES:
        path = os.path.join(BASE, hub)
        if not os.path.exists(path):
            continue
        with open(path, encoding='utf-8') as f:
            html = f.read()
        for card in card_re.findall(html):
            link = link_re.search(card)
            if not link:
                continue
            fname = os.path.basename(link.group(1).split('#')[0].split('?')[0])
            tags = [clean(t) for t in tag_re.findall(card)]
            tags = [t for t in tags if t]
            if not tags:
                continue
            index.setdefault(fname, [])
            for t in tags:
                if t not in index[fname]:
                    index[fname].append(t)
    return index


def extract_description(html, title):
    """Use the page's meta description; fall back to a generic sentence."""
    m = re.search(
        r'<meta\s+name=["\']description["\']\s+content=["\'](.*?)["\']\s*/?>',
        html, flags=re.IGNORECASE | re.DOTALL,
    )
    desc = clean(m.group(1)) if m else ''
    if not desc:
        desc = f'{title} — an interactive math teaching tool.'
    lic = ('Source code is MIT-licensed; educational content is licensed '
           'under CC BY 4.0.')
    return f'<p>{desc}</p><p>{lic}</p>'


# --------------------------------------------------------------------------
# Minimal Zenodo REST client (stdlib only)
# --------------------------------------------------------------------------
class Zenodo:
    def __init__(self, token, api):
        self.token = token
        self.api = api.rstrip('/')

    def _req(self, method, url, data=None, headers=None, raw=None):
        if not url.startswith('http'):
            url = self.api + url
        hdrs = {'Authorization': f'Bearer {self.token}'}
        body = None
        if data is not None:
            body = json.dumps(data).encode('utf-8')
            hdrs['Content-Type'] = 'application/json'
        elif raw is not None:
            body = raw
            hdrs['Content-Type'] = 'application/octet-stream'
        if headers:
            hdrs.update(headers)
        req = urllib.request.Request(url, data=body, headers=hdrs, method=method)
        last_err = None
        for attempt in range(4):
            try:
                with urllib.request.urlopen(req) as resp:
                    payload = resp.read()
                    return json.loads(payload) if payload else {}
            except urllib.error.HTTPError as e:
                detail = e.read().decode('utf-8', 'replace')
                # Retry transient server/rate-limit errors with backoff.
                if e.code in (429, 500, 502, 503, 504) and attempt < 3:
                    wait = 2 ** (attempt + 1)
                    time.sleep(wait)
                    last_err = e
                    continue
                raise RuntimeError(f'{method} {url} -> HTTP {e.code}: {detail}')
            except urllib.error.URLError as e:
                if attempt < 3:
                    time.sleep(2 ** (attempt + 1))
                    last_err = e
                    continue
                raise RuntimeError(f'{method} {url} -> {e}')
        raise RuntimeError(f'{method} {url} failed: {last_err}')

    def create(self):
        return self._req('POST', '/deposit/depositions', data={})

    def new_version(self, record_id):
        r = self._req('POST',
                       f'/deposit/depositions/{record_id}/actions/newversion')
        # The draft of the new version lives at links.latest_draft.
        draft_url = r.get('links', {}).get('latest_draft')
        return self._req('GET', draft_url)

    def upload_file(self, deposition, path):
        bucket = deposition.get('links', {}).get('bucket')
        fname = os.path.basename(path)
        with open(path, 'rb') as f:
            raw = f.read()
        if bucket:  # modern files API
            return self._req('PUT', f'{bucket}/{fname}', raw=raw)
        # Fallback: legacy multipart files API
        dep_id = deposition['id']
        return self._req('POST', f'/deposit/depositions/{dep_id}/files',
                         raw=raw, headers={'Content-Type':
                                           'application/octet-stream'})

    def set_metadata(self, dep_id, metadata):
        return self._req('PUT', f'/deposit/depositions/{dep_id}',
                         data={'metadata': metadata})

    def publish(self, dep_id):
        return self._req('POST',
                         f'/deposit/depositions/{dep_id}/actions/publish')


def make_metadata(title, description, keywords, live_url):
    return {
        'title': title,
        'upload_type': UPLOAD_TYPE,
        'description': description,
        'creators': [{'name': f'{AUTHOR_LAST}, {AUTHOR_FIRST}'}],
        'license': LICENSE_ID,
        'access_right': 'open',
        'keywords': keywords,
        'related_identifiers': [
            {'identifier': live_url, 'relation': 'isIdenticalTo',
             'scheme': 'url', 'resource_type': 'software'},
        ],
    }


def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, encoding='utf-8') as f:
            return json.load(f)
    return {}


def save_state(state):
    with open(STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(state, f, indent=2, sort_keys=True)
        f.write('\n')


def tool_pages():
    import glob
    pages = []
    for path in sorted(glob.glob(os.path.join(BASE, '*.html'))):
        name = os.path.basename(path)
        if name in SKIP_PAGES:
            continue
        pages.append(name)
    return pages


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--sandbox', action='store_true',
                    help='use sandbox.zenodo.org (fake DOIs, for testing)')
    ap.add_argument('--publish', action='store_true',
                    help='publish the deposition (MINTS the DOI, irreversible)')
    ap.add_argument('--only', nargs='+', metavar='FILE',
                    help='restrict to specific tool filenames')
    ap.add_argument('--new-version', action='store_true',
                    help='archive a new version of tools already recorded')
    ap.add_argument('--limit', type=int, default=0,
                    help='process at most N tools this run (0 = no limit)')
    args = ap.parse_args()

    token = os.environ.get('ZENODO_TOKEN')
    if not token:
        sys.exit('error: set ZENODO_TOKEN (see the docstring / docs/ZENODO.md)')

    api = SANDBOX_API if args.sandbox else PROD_API
    zen = Zenodo(token, api)
    state = load_state()
    tags = build_tag_index()

    targets = args.only if args.only else tool_pages()
    done = 0
    for name in targets:
        path = os.path.join(BASE, name)
        if not os.path.exists(path):
            print(f'  MISS {name} (no such file)')
            continue
        if name in SKIP_PAGES:
            print(f'  SKIP {name} (hub/personal page)')
            continue

        existing = state.get(name)
        if existing and not args.new_version:
            print(f'  HAVE {name} -> {existing.get("doi")}')
            continue
        if args.limit and done >= args.limit:
            print(f'  STOP reached --limit {args.limit}')
            break

        with open(path, encoding='utf-8') as f:
            html = f.read()
        title = extract_title(html)
        description = extract_description(html, title)
        keywords = list(dict.fromkeys(
            KEYWORDS_BASE + tags.get(name, [])))
        live_url = SITE_URL + name

        try:
            if existing and args.new_version:
                dep = zen.new_version(existing['record_id'])
                action = 'new version'
            else:
                dep = zen.create()
                action = 'draft'
            zen.upload_file(dep, path)
            dep = zen.set_metadata(
                dep['id'],
                make_metadata(title, description, keywords, live_url))

            reserved = (dep.get('metadata', {})
                          .get('prereserve_doi', {}) or {}).get('doi')

            if args.publish:
                pub = zen.publish(dep['id'])
                doi = pub.get('doi') or pub.get('metadata', {}).get('doi')
                concept = (pub.get('conceptdoi')
                           or pub.get('metadata', {}).get('conceptdoi'))
                record_id = pub['id']
                html_url = pub.get('links', {}).get('record_html')
                status = f'PUB  {name} -> {doi}'
            else:
                doi = reserved
                concept = None
                record_id = dep['id']
                html_url = dep.get('links', {}).get('html')
                status = f'{action.upper():4.4s} {name} -> reserved {doi} (draft)'

            state[name] = {
                'doi': doi,
                'concept_doi': concept,
                'record_id': record_id,
                'url': html_url,
                'published': bool(args.publish),
                'sandbox': bool(args.sandbox),
                'title': title,
            }
            save_state(state)  # persist after each tool — crash-safe
            print(f'  {status}')
            done += 1
        except Exception as e:  # noqa: BLE001 - report and continue
            print(f'  FAIL {name}: {e}')

    pub_n = sum(1 for v in state.values() if v.get('published'))
    print(f'\nDone. {done} processed this run; '
          f'{pub_n} published DOIs recorded in {os.path.basename(STATE_FILE)}.')
    if not args.publish:
        print('These are DRAFTS — review them on Zenodo, then re-run with '
              '--publish to mint the DOIs.')
    print('Next: run  python3 add_citation.py  to embed the DOIs on each page.')


if __name__ == '__main__':
    main()
