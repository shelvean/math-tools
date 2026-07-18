# Zenodo DOIs for Math Tools

This repository is set up to mint [Zenodo](https://zenodo.org) DOIs two ways.
Pick whichever you need — or do both.

| | What you get | Effort | Token/API needed |
|---|---|---|---|
| **A. Repository DOI** | One citable archive of the whole site, with a concept DOI (always-latest) plus a DOI per GitHub release. | One-time setup, then automatic on each release. | None |
| **B. Per-tool DOIs** | A separate Zenodo record + DOI for *each* interactive tool, embedded in that tool's "Cite this tool" box. | Runs the uploader script over ~90 tools. | Zenodo API token |

Files already in the repo:

- `.zenodo.json` — metadata Zenodo reads when it archives a GitHub release (flow A).
- `CITATION.cff` — GitHub's native citation file (shows a "Cite this repository" button).
- `zenodo_upload.py` — the per-tool uploader (flow B).
- `add_citation.py` — already wired to embed per-tool DOIs once they exist.

---

## A. One DOI for the whole repository (GitHub release integration)

This is the standard "make your software citable" path. Zenodo watches the
repo and archives every GitHub Release automatically.

1. **Connect the repo.** Sign in at <https://zenodo.org> with GitHub, go to
   <https://zenodo.org/account/settings/github/>, and flip the switch **on**
   for `shelvean/math-tools`. (First time, you may need to click *Sync* so the
   repo appears.)
2. **Cut a release on GitHub.** Tag e.g. `v1.0.0`, give it a title and notes,
   and publish. Zenodo receives the webhook, archives the tarball using
   `.zenodo.json`, and **mints the DOI** within a minute or two.
3. **Grab the DOI badge.** Back on the Zenodo GitHub settings page, the repo
   now shows a DOI badge. There are two DOIs:
   - a **concept DOI** that always resolves to the newest version (cite this
     one in general), and
   - a **version DOI** unique to `v1.0.0`.
4. **Record the concept DOI in the repo:**
   - Uncomment the `doi:`/`identifiers:` lines at the bottom of `CITATION.cff`
     and paste the concept DOI.
   - Update the DOI badge placeholder in `README.md` (see the "Citation & DOI"
     section there).

Every later release automatically gets its own version DOI under the same
concept DOI — no further setup.

> ORCID: add your iD in `CITATION.cff` (and `.zenodo.json` `creators`) so the
> DOI is linked to your researcher profile.

---

## B. A DOI per tool (Zenodo REST API)

Use `zenodo_upload.py` to give every interactive tool its own Zenodo record
and DOI. The DOIs are saved to `zenodo_dois.json`, and `add_citation.py` reads
that file to drop each DOI straight into the tool's on-page citation block.

**These are metadata-only records — no file is uploaded.** The tools depend on
vendored JS/CSS and don't run when downloaded from Zenodo, so each record is a
citable, DOI-bearing landing page whose metadata links to the live, working
tool (via a `related_identifiers` entry). This uses Zenodo's newer InvenioRDM
`/api/records` endpoint with `files.enabled = false`.

### 1. Get an API token

Create a personal access token with the **`deposit:write`** and
**`deposit:actions`** scopes:

- Production: <https://zenodo.org/account/settings/applications/tokens/new>
- Sandbox (for testing): <https://sandbox.zenodo.org/account/settings/applications/tokens/new>

```bash
export ZENODO_TOKEN=your_token_here
```

### 2. Test on the sandbox first

The sandbox issues throwaway DOIs and is periodically wiped — perfect for a
dry run. (Sandbox needs its *own* token from the sandbox site.)

```bash
python3 zenodo_upload.py --sandbox --only newton.html --publish
```

Check the record looks right at <https://sandbox.zenodo.org/me/uploads>.

### 3. Discard any old file-based drafts

If you previously ran the older uploader, you may have file-based drafts
recorded in `zenodo_dois.json`. Delete them so they can be recreated as
metadata-only (this only deletes **unpublished** records, then removes them
from the file):

```bash
python3 zenodo_upload.py --discard-old
```

### 4. Create metadata-only drafts, review, then publish

```bash
# Create drafts for every tool — nothing public yet, DOIs only "reserved":
python3 zenodo_upload.py

# Review the drafts at https://zenodo.org/me/uploads, then publish for real.
# Publishing is IRREVERSIBLE — a published DOI is permanent.
python3 zenodo_upload.py --publish
```

The script is **idempotent**: published tools are skipped, and an existing
draft is published in place when you pass `--publish`. Safe to stop and
re-run. Useful flags:

- `--only file1.html file2.html` — target specific tools
- `--limit N` — process at most N tools this run (good for batching)
- `--new-version` — archive an updated tool as a new version under its
  existing concept DOI
- `--discard-old` — delete unpublished drafts and clear them from the file
- `--sandbox` — use sandbox.zenodo.org

### 5. Embed the DOIs on the pages

Once DOIs are published, regenerate the citation blocks:

```bash
python3 add_citation.py
```

Each tool's "Cite this tool" box now shows a `DOI: https://doi.org/…` link,
and the APA / MLA / BibTeX entries use the DOI as the canonical URL (BibTeX
also gets a `doi` field).

### 6. Commit

```bash
git add zenodo_dois.json *.html
git commit -m "Publish Zenodo DOIs and embed them in tool citations"
```

> **No file is uploaded.** Each record is metadata-only and links to the live
> page via a `related_identifiers` entry (`isIdenticalTo`). The DOI resolves to
> a Zenodo landing page that points at the working tool. If you ever want an
> archived, downloadable copy instead, bundle each tool's assets into a
> self-contained file first (out of scope for this script).

### Metadata sources & InvenioRDM field IDs

- **Title** — the page's `<h1>` (falls back to `<title>`).
- **Description** — the page's `<meta name="description">`.
- **Keywords** — the tool's hub-page tags (sent as InvenioRDM `subjects`),
  plus a couple of site-wide defaults.
- **Creator / license** — `Shelvean Kapita` / `mit`.

The InvenioRDM controlled-vocabulary IDs are constants near the top of
`zenodo_upload.py`: `RESOURCE_TYPE_ID` (`software`), `LICENSE_ID` (`mit`),
`RELATION_ID` (`isidenticalto`), `KEYWORDS_BASE`. If a sandbox test rejects
one, the server's error message names the offending field — adjust the
constant and re-run.

> **Test on the sandbox first.** Because this uses the records API, always run
> `python3 zenodo_upload.py --sandbox --only newton.html --publish` and confirm
> the record at <https://sandbox.zenodo.org/me/uploads> before doing all tools
> on production.
