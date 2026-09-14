# Counting preprint downloads in Google Analytics

The front page (`index.html`) sends a custom event to Google Analytics 4
(property `G-LEQE004C92`) every time a visitor clicks a preprint link in the
Recent News list. The script lives between the `link-tracking:start` and
`link-tracking:end` markers near the bottom of `index.html`.

## What is sent

| Link kind | Event name          | Parameters                                                      |
|-----------|---------------------|-----------------------------------------------------------------|
| preprint  | `preprint_download` | `preprint_name`, `file_name`, `link_url`, `event_label`         |
| code      | `code_click`        | `repo_name`, `link_url`, `event_label`                          |

`preprint_name` is the link's `data-track-label` attribute (the paper title,
kept under GA4's 100-character limit for parameter values) or, failing that,
the link text. `file_name` is the PDF's basename, e.g.
`Kapita_C1_Bernstein_QuasiTrefftz_Helmholtz.pdf`.

Any link tagged `data-track="preprint"` is counted wherever it appears on the
page, and any `.pdf` or arXiv link inside `.news-list` is counted even
without the tag, so new entries need no extra wiring beyond a
`data-track-label` with the paper's name.

## One-time setup in GA4 (required to see counts per paper)

GA4 only reports on event parameters that are registered as custom
dimensions. Without this step the Events report shows the total number of
`preprint_download` events but cannot split them by paper.

1. Open the property, then **Admin → Data display → Custom definitions**.
2. Click **Create custom dimension** and enter:
   - Dimension name: `Preprint name`
   - Scope: **Event**
   - Event parameter: `preprint_name`
3. Repeat for `File name` with event parameter `file_name` if you also want
   counts keyed by PDF file (useful if a title changes but the file does not).
4. Save. Data collected from this point on is attributed to the dimension.
   Custom dimensions are not retroactive, so earlier clicks stay unsplit.

## Reading the counts

- **Reports → Engagement → Events**, click `preprint_download`. Once the
  custom dimension exists, the event detail page gains a card that breaks
  the event count down by `Preprint name`.
- For a table you can sort or export: **Explore → Blank**, add dimension
  `Preprint name` (and optionally `File name`) and metric **Event count**,
  then filter Event name to `preprint_download`.
- **Realtime** shows the event within a minute of a click, which is the
  quickest way to confirm the setup works: open the site, click a preprint,
  and watch for `preprint_download` under Event count by Event name.

## Historical counts before the custom dimension existed

GA4's enhanced measurement records an automatic `file_download` event for
every PDF click, with built-in `file_name` and `link_url` dimensions that need
no registration. In **Explore**, use dimension **File name** with metric
**Event count** and filter Event name to `file_download` to see per-file
download counts for the whole retention window. Note that this counts by
file, so a renamed PDF appears under both its old and new names.

## What cannot be counted

Analytics runs as JavaScript inside HTML pages, so it sees only clicks made
on this site. A visitor who opens a PDF URL directly, from an email, a search
result, or an arXiv listing, never loads the page script and is not counted.
GitHub Pages does not expose server logs, so there is no way to count those
direct fetches from this repository.
