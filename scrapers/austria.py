"""Austria — Vienna's Vereinigte Bühnen Wien (musicalvienna.at), the home of the
德奧 megamusicals (Das Phantom der Oper, Maria Theresia, etc.) at the Raimund
Theater and Ronacher. The TM sweep only caught a stray Mamma Mia, missing the VBW
resident productions entirely.

Source is server-rendered: /de/spielplan lists each show as /de/spielplan/{id}/{slug};
each detail page carries og:title + og:image + German performance dates
("28. Juni 2026") + the theatre name. Run = earliest..latest dated performance.

Output: data/austria.json   Run: python scrapers/austria.py
"""

import json
import re
import sys
import io
import html
import hashlib
import urllib.request
from datetime import datetime, timezone, timedelta
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
DATA = Path(__file__).resolve().parent.parent / "data"
BASE = "https://www.musicalvienna.at"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0",
      "Accept-Language": "de"}
CET = timezone(timedelta(hours=1))

# Vienna VBW houses (building-level coords).
VENUES = {
    "raimund": ("Raimund Theater", 48.196900, 16.343800),
    "ronacher": ("Ronacher", 48.207300, 16.376000),
}
DE_MONTH = {"jan": 1, "feb": 2, "mär": 3, "maer": 3, "apr": 4, "mai": 5, "jun": 6,
            "jul": 7, "aug": 8, "sep": 9, "okt": 10, "nov": 11, "dez": 12}
# Not staged book musicals: backstage tours, youth showcase/gala.
SKIP = re.compile(r"fuehrung|führung|workshop|we-are-musical|we are musical|gala", re.I)


def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:
        return r.read().decode("utf-8", "ignore")


def parse_dates(page):
    """All 'DD. Monat YYYY' German dates → (min, max) ISO, or (None, None)."""
    out = []
    for d, mon, y in re.findall(r"(\d{1,2})\.\s*([A-Za-zä]+)\.?\s*(20\d{2})", page):
        m = DE_MONTH.get(mon[:3].lower())
        if m:
            out.append(f"{y}-{m:02d}-{int(d):02d}")
    out.sort()
    return (out[0], out[-1]) if out else (None, None)


def main():
    today = datetime.now(CET).strftime("%Y-%m-%d")
    listing = get(f"{BASE}/de/spielplan")
    slugs = sorted(set(re.findall(r"/de/spielplan/\d+/[A-Za-z][\w\-]*", listing)))
    rows, dropped = [], []
    for path in slugs:
        if SKIP.search(path):
            dropped.append(f"{path} (tour/gala)"); continue
        try:
            page = get(BASE + path)
        except Exception:
            continue
        tm = re.search(r'og:title"\s+content="([^"]+)"', page)
        title = html.unescape(tm.group(1)).split("|")[0].strip() if tm else None
        if not title or SKIP.search(title):
            dropped.append(f"{path} ({title})"); continue
        # venue: whichever VBW house the page mentions most
        vk = max(VENUES, key=lambda k: len(re.findall(k, page, re.I)))
        if not re.search(vk, page, re.I):
            vk = "raimund"
        venue, lat, lng = VENUES[vk]
        start, end = parse_dates(page)
        if not start:
            dropped.append(f"{title} (no dates)"); continue
        if end and end < today:
            dropped.append(f"{title} (ended {end})"); continue
        img = re.search(r'og:image"\s+content="([^"]+)"', page)
        rows.append({
            "id": "at-" + hashlib.md5(f"vbw|{title}|{venue}".encode()).hexdigest()[:8],
            "title": title, "title_en": "",
            "venue": venue, "city": "Vienna", "country": "Austria",
            "lat": lat, "lng": lng, "start_date": start, "end_date": end,
            "image": img.group(1) if img else None,
            "ticket_url": BASE + path, "type": "resident", "verified": True,
            "source": "musicalvienna.at",
        })

    out = {"meta": {"source": "musicalvienna.at (VBW)", "count": len(rows)}, "shows": rows}
    (DATA / "austria.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {len(rows)} -> data/austria.json")
    for s in rows:
        print(f"  keep: {s['title']} @ {s['venue']} {s['start_date']}~{s['end_date']}")
    for d in dropped:
        print("  drop:", d)


if __name__ == "__main__":
    main()
