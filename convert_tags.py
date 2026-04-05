#!/usr/bin/env python3
"""Convert <span class="tag"> to <a class="tag" href="labels/SLUG.html"> in hub pages."""

import re, os

def slug(label):
    """Convert label to filename-safe slug."""
    # Decode HTML entities first
    label = label.replace('&amp;', '&')
    return re.sub(r'[^a-z0-9]+', '-', label.lower()).strip('-')

def convert_tags(html, prefix="labels/"):
    """Replace <span class="tag">LABEL</span> with <a href="labels/SLUG.html" class="tag">LABEL</a>"""
    def replacer(m):
        label_html = m.group(1)  # may contain &amp; etc.
        label_text = label_html.replace('&amp;', '&')
        s = slug(label_text)
        return f'<a href="{prefix}{s}.html" class="tag">{label_html}</a>'
    return re.sub(r'<span class="tag">(.*?)</span>', replacer, html)

hub_pages = [
    'projects.html',
    'linear.html',
    'numerical.html',
    'optim.html',
    'pdftools.html',
]

base = '/home/user/math-tools'

for page in hub_pages:
    path = os.path.join(base, page)
    with open(path, 'r') as f:
        html = f.read()

    updated = convert_tags(html)

    with open(path, 'w') as f:
        f.write(updated)

    count = updated.count('class="tag"')
    print(f"  {page}: {count} tags converted")

print("\nDone.")
