#!/usr/bin/env python3
"""Mint a Zenodo DOI for each interactive tool — as a METADATA-ONLY record.

The interactive tools don't run when downloaded from Zenodo (they depend on
vendored JS/CSS), so each Zenodo record carries no file: it is a citable,
DOI-bearing landing page whose metadata points at the live, working tool via
a related identifier. This uses Zenodo's newer InvenioRDM REST API
(`/api/records` with `files.enabled = false`).

For every tool page (the same set add_citation.py cites), this script:

  1. Creates a metadata-only draft record (no file upload).
  2. Sets metadata: title (page <h1>), description (page <meta description>),
     creator, license, keywords (hub-page tags), and a related identifier
     pointing at the live page.
  3. Reserves the DOI (draft) or publishes (mints the DOI permanently).
  4. Records {filename: {...doi info...}} in zenodo_dois.json, which
     add_citation.py reads to embed each published DOI in the on-page
     citations.

Quick start
-----------
  # 1. Token with the "deposit:write" + "deposit:actions" scopes:
  #      https://zenodo.org/account/settings/applications/tokens/new
  #      (sandbox needs its OWN token from https://sandbox.zenodo.org/...)
  export ZENODO_TOKEN=xxxxxxxxxxxxxxxxxxxx

  # 2. Validate one record end-to-end on the sandbox FIRST (fake DOIs):
  python3 zenodo_upload.py --sandbox --only newton.html --publish

  # 3. If you have leftover file-based drafts from the old uploader, discard
  #    them so they can be recreated as metadata-only (deletes UNPUBLISHED
  #    records listed in zenodo_dois.json, then clears them from the file):
  python3 zenodo_upload.py --discard-old

  # 4. Create metadata-only drafts for every tool (nothing public yet):
  python3 zenodo_upload.py

  # 5. Review at https://zenodo.org/me/uploads, then publish for real
  #    (IRREVERSIBLE — a published DOI is permanent):
  python3 zenodo_upload.py --publish

State & idempotency
-------------------
Progress is tracked in zenodo_dois.json. A published tool is skipped; an
existing draft is published in place when --publish is given. Safe to
re-run after an interruption.

Only the Python standard library is used (urllib) — no third-party deps.
"""
import argparse
import datetime
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

PROD_HOST = 'https://zenodo.org'
SANDBOX_HOST = 'https://sandbox.zenodo.org'

# InvenioRDM controlled-vocabulary ids. If a sandbox test rejects one of
# these, the server error names the bad field — adjust here and re-run.
RESOURCE_TYPE_ID = 'software'          # interactive tools
LICENSE_ID = 'mit'                     # SPDX id, lowercase
RELATION_ID = 'isidenticalto'         # this record <-> the live page
SCHEME_URL = 'url'

KEYWORDS_BASE = [
    'mathematics education',
    'interactive visualization',
]

# Hub pages whose tool-cards carry the per-tool tag assignments.
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
    """Use the page's meta description; fall back to a generic sentence.
    Appends a line linking the live, runnable tool."""
    m = re.search(
        r'<meta\s+name=["\']description["\']\s+content=["\'](.*?)["\']\s*/?>',
        html, flags=re.IGNORECASE | re.DOTALL,
    )
    desc = clean(m.group(1)) if m else ''
    if not desc:
        desc = f'{title} — an interactive math teaching tool.'
    note = ('This is a metadata-only record for an interactive, browser-based '
            'tool that runs live (it is not a downloadable file). '
            'Source code is MIT-licensed; educational content is licensed '
            'under CC BY 4.0.')
    return f'<p>{desc}</p><p>{note}</p>'


# --------------------------------------------------------------------------
# Minimal InvenioRDM REST client (stdlib only)
# --------------------------------------------------------------------------
class Zenodo:
    def __init__(self, token, host):
        self.token = token
        self.host = host.rstrip('/')

    def _req(self, method, url, data=None):
        if not url.startswith('http'):
            url = self.host + url
        hdrs = {'Authorization': f'Bearer {self.token}',
                'Accept': 'application/json'}
        body = None
        if data is not None:
            body = json.dumps(data).encode('utf-8')
            hdrs['Content-Type'] = 'application/json'
        req = urllib.request.Request(url, data=body, headers=hdrs,
                                     method=method)
        last_err = None
        for attempt in range(4):
            try:
                with urllib.request.urlopen(req) as resp:
                    payload = resp.read()
                    return json.loads(payload) if payload else {}
            except urllib.error.HTTPError as e:
                detail = e.read().decode('utf-8', 'replace')
                if e.code in (429, 500, 502, 503, 504) and attempt < 3:
                    time.sleep(2 ** (attempt + 1))
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

    # -- records API (metadata-only) --
    def create_draft(self, metadata):
        body = {
            'access': {'record': 'public', 'files': 'public'},
            'files': {'enabled': False},
            'metadata': metadata,
        }
        return self._req('POST', '/api/records', data=body)

    def get_draft(self, rec_id):
        return self._req('GET', f'/api/records/{rec_id}/draft')

    def reserve_doi(self, draft):
        link = (draft.get('links', {}) or {}).get('reserve_doi')
        if not link:
            return draft
        try:
            self._req('POST', link)
        except RuntimeError:
            pass  # some instances auto-assign; ignore reserve failures
        # Re-fetch to pick up the reserved DOI.
        return self.get_draft(draft['id'])

    def publish(self, draft):
        link = (draft.get('links', {}) or {}).get('publish')
        if not link:
            link = f"/api/records/{draft['id']}/draft/actions/publish"
        return self._req('POST', link)

    def new_version(self, rec_id):
        nv = self._req('POST', f'/api/records/{rec_id}/versions')
        return self.get_draft(nv['id'])

    def delete_draft(self, rec_id):
        """Delete an unpublished draft. Tries the records API, then the
        legacy deposit endpoint (for drafts made by the old uploader)."""
        try:
            return self._req('DELETE', f'/api/records/{rec_id}/draft')
        except RuntimeError:
            return self._req('DELETE', f'/api/deposit/depositions/{rec_id}')


def dois_of(rec):
    """(version DOI, concept DOI) from a record/draft payload."""
    doi = ((rec.get('pids', {}) or {}).get('doi', {}) or {}).get('identifier')
    concept = ((((rec.get('parent', {}) or {}).get('pids', {}) or {})
                .get('doi', {}) or {}).get('identifier'))
    return doi, concept


def make_metadata(title, description, keywords):
    md = {
        'resource_type': {'id': RESOURCE_TYPE_ID},
        'title': title,
        'creators': [{
            'person_or_org': {
                'type': 'personal',
                'family_name': AUTHOR_LAST,
                'given_name': AUTHOR_FIRST,
            },
        }],
        'publication_date': datetime.date.today().isoformat(),
        'publisher': 'Zenodo',
        'description': description,
        'rights': [{'id': LICENSE_ID}],
        'related_identifiers': [{
            'identifier': SITE_URL,  # overwritten per tool below
            'relation_type': {'id': RELATION_ID},
            'scheme': SCHEME_URL,
        }],
    }
    if keywords:
        md['subjects'] = [{'subject': k} for k in keywords]
    return md


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
    return [os.path.basename(p)
            for p in sorted(glob.glob(os.path.join(BASE, '*.html')))
            if os.path.basename(p) not in SKIP_PAGES]


def discard_old(zen, state):
    """Delete every UNPUBLISHED record in the state file, then drop it."""
    removed = 0
    for name in list(state):
        rec = state[name]
        if rec.get('published'):
            print(f'  KEEP {name} (published — not deleting)')
            continue
        rid = rec.get('record_id')
        try:
            if rid:
                zen.delete_draft(rid)
            del state[name]
            save_state(state)
            removed += 1
            print(f'  DEL  {name} (draft {rid})')
        except Exception as e:  # noqa: BLE001
            print(f'  FAIL {name}: {e}')
    print(f'\nDiscarded {removed} draft(s).')


def main():
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--sandbox', action='store_true',
                    help='use sandbox.zenodo.org (fake DOIs, for testing)')
    ap.add_argument('--publish', action='store_true',
                    help='publish (MINTS the DOI, irreversible)')
    ap.add_argument('--only', nargs='+', metavar='FILE',
                    help='restrict to specific tool filenames')
    ap.add_argument('--new-version', action='store_true',
                    help='archive a new version of tools already published')
    ap.add_argument('--discard-old', action='store_true',
                    help='delete unpublished drafts in zenodo_dois.json and '
                         'remove them from the file (use to clear old '
                         'file-based drafts before recreating metadata-only)')
    ap.add_argument('--limit', type=int, default=0,
                    help='process at most N tools this run (0 = no limit)')
    args = ap.parse_args()

    token = os.environ.get('ZENODO_TOKEN')
    if not token:
        sys.exit('error: set ZENODO_TOKEN (see the docstring / docs/ZENODO.md)')

    host = SANDBOX_HOST if args.sandbox else PROD_HOST
    zen = Zenodo(token, host)
    state = load_state()

    if args.discard_old:
        discard_old(zen, state)
        return

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

        if existing and existing.get('published') and not args.new_version:
            print(f'  HAVE {name} -> {existing.get("doi")} (published)')
            continue

        if args.limit and done >= args.limit:
            print(f'  STOP reached --limit {args.limit}')
            break

        # Publish an existing draft in place.
        if existing and not args.new_version:
            if not args.publish:
                print(f'  DRFT {name} -> {existing.get("doi")} '
                      f'(draft exists; re-run with --publish to mint)')
                continue
            try:
                draft = zen.get_draft(existing['record_id'])
                rec = zen.publish(draft)
                doi, concept = dois_of(rec)
                existing.update({
                    'doi': doi or existing.get('doi'),
                    'concept_doi': concept or existing.get('concept_doi'),
                    'url': rec.get('links', {}).get('self_html',
                                                    existing.get('url')),
                    'published': True,
                })
                state[name] = existing
                save_state(state)
                print(f'  PUB  {name} -> {existing["doi"]}')
                done += 1
            except Exception as e:  # noqa: BLE001
                print(f'  FAIL {name} (publish): {e}')
            continue

        # Create a fresh metadata-only record.
        with open(path, encoding='utf-8') as f:
            html = f.read()
        title = extract_title(html)
        description = extract_description(html, title)
        keywords = list(dict.fromkeys(KEYWORDS_BASE + tags.get(name, [])))
        metadata = make_metadata(title, description, keywords)
        metadata['related_identifiers'][0]['identifier'] = SITE_URL + name

        try:
            if existing and args.new_version:
                draft = zen.new_version(existing['record_id'])
                # Carry forward updated metadata on the new version.
                draft = zen._req('PUT', f"/api/records/{draft['id']}/draft",
                                 data={'access': {'record': 'public',
                                                  'files': 'public'},
                                       'files': {'enabled': False},
                                       'metadata': metadata})
                action = 'new version'
            else:
                draft = zen.create_draft(metadata)
                action = 'draft'

            draft = zen.reserve_doi(draft)
            reserved, _ = dois_of(draft)

            if args.publish:
                rec = zen.publish(draft)
                doi, concept = dois_of(rec)
                record_id = rec['id']
                html_url = rec.get('links', {}).get('self_html')
                status = f'PUB  {name} -> {doi}'
            else:
                doi, concept = reserved, None
                record_id = draft['id']
                html_url = draft.get('links', {}).get('self_html')
                status = (f'{action.upper():4.4s} {name} -> '
                          f'reserved {doi} (draft)')

            state[name] = {
                'doi': doi,
                'concept_doi': concept,
                'record_id': record_id,
                'url': html_url,
                'published': bool(args.publish),
                'sandbox': bool(args.sandbox),
                'metadata_only': True,
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
