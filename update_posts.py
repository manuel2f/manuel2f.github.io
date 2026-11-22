"""Regenerate the "Publicaciones / Writing" section of index.html and en/index.html from posts.json.

Usage: python3 update_posts.py
The section lives between the <!-- POSTS:START --> and <!-- POSTS:END --> markers.
Only the latest MAX_POSTS entries are shown, newest first.
"""

import html
import json
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).parent
MAX_POSTS = 5
MONTHS = {
    "es": ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"],
    "en": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
}
TEXT = {
    "es": {"h2": "Publicaciones.", "sub": "Lo último que he compartido en LinkedIn.",
           "read": "Leer en LinkedIn", "all": "Todas en LinkedIn", "lang_note": ""},
    "en": {"h2": "Writing.", "sub": "The latest things I've shared on LinkedIn.",
           "read": "Read on LinkedIn", "all": "All on LinkedIn", "lang_note": " (in Spanish)"},
}
PROFILE = "https://www.linkedin.com/in/manuel-f-409496b/recent-activity/all/"


def fmt_date(iso: str, lang: str) -> str:
    d = date.fromisoformat(iso)
    m = MONTHS[lang][d.month - 1]
    return f"{d.day} {m} {d.year}" if lang == "es" else f"{m} {d.day}, {d.year}"


def render(posts: list, lang: str) -> str:
    t = TEXT[lang]
    items = []
    for p in posts:
        note = t["lang_note"] if p.get("lang", "es") != lang else ""
        items.append(
            f'        <li>\n'
            f'          <time datetime="{p["date"]}">{fmt_date(p["date"], lang)}</time>\n'
            f'          <h3>{html.escape(p["title"][lang])}</h3>\n'
            f'          <p>{html.escape(p["summary"][lang])}</p>\n'
            f'          <a class="more" href="{html.escape(p["url"])}">{t["read"]}{note}</a>\n'
            f'        </li>'
        )
    return (
        '<!-- POSTS:START -->\n'
        '  <section id="publicaciones" aria-labelledby="posts-t">\n'
        '    <div class="wrap">\n'
        '      <div class="head">\n'
        f'        <h2 id="posts-t">{t["h2"]}</h2>\n'
        f'        <p>{t["sub"]}</p>\n'
        '      </div>\n'
        '      <ol class="posts">\n'
        + "\n".join(items) + "\n"
        '      </ol>\n'
        f'      <p class="all"><a class="more" href="{PROFILE}">{t["all"]}</a></p>\n'
        '    </div>\n'
        '  </section>\n'
        '  <!-- POSTS:END -->'
    )


def main() -> None:
    posts = json.loads((ROOT / "posts.json").read_text(encoding="utf-8"))
    posts = sorted(posts, key=lambda p: p["date"], reverse=True)[:MAX_POSTS]
    for lang, path in (("es", ROOT / "index.html"), ("en", ROOT / "en" / "index.html")):
        src = path.read_text(encoding="utf-8")
        new, n = re.subn(r"<!-- POSTS:START -->.*?<!-- POSTS:END -->", render(posts, lang), src, flags=re.S)
        if n != 1:
            raise SystemExit(f"Markers not found exactly once in {path}")
        path.write_text(new, encoding="utf-8")
        print(f"Updated {path.relative_to(ROOT)} with {len(posts)} posts")


if __name__ == "__main__":
    main()
