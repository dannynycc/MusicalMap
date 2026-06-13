"""Eastern Europe musicals — a region with a huge scene (esp. Hungary) that the
global scrapers miss. Built source-by-source like japan.py.

  - Hungary: jegy.hu musical subcategory (the platform genre-filters to ミュージカル,
    so everything is a musical). The category page lists each show (schema.org Event:
    name + image + the /program/ detail URL) and the venue inline; the detail page
    carries every performance date (plain YYYY-MM-DD) → first..last = the run.

Czech (colosseumticket.cz) / Poland (Teatr Roma) are planned as further sources.

Output: data/easteurope.json    Run: python scrapers/easteurope.py
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
CET = timezone(timedelta(hours=1))
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0",
      "Accept-Language": "en"}
# Hungarian/EE venue-name tail words, to pull the venue out of the listing box.
VENUE_RE = re.compile(
    r"[A-ZÁÉÍÓÖŐÚÜŰ][\wÁÉÍÓÖŐÚÜŰáéíóöőúüű .'’&-]{2,34}?"
    r"(?:Színház|Aréna|Csarnok|Színpad|Stúdió|Theatre|Theater|Palota|Ház)")


def get(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", "ignore")


def scrape_hungary():
    cat = get("https://www.jegy.hu/event/subcategory/musical-4")
    boxes = re.split(r'<div class="programBox large', cat)[1:]
    today = datetime.now(CET).strftime("%Y-%m-%d")
    out, dropped, seen = [], [], set()
    for b in boxes:
        nm = re.search(r'itemprop="name" content="([^"]+)"', b)        # 1st = the Event name
        url = re.search(r'href="(https://www\.jegy\.hu/program/[\w-]+)"', b)
        if not nm or not url or url.group(1) in seen:
            continue
        seen.add(url.group(1))
        title = html.unescape(nm.group(1)).strip()
        img = re.search(r'itemprop="image" content="([^"]+)"', b)
        place = re.search(r'<a class="place"[^>]*>([^<]+)</a>', b)      # clean venue name
        addr = re.search(r'itemprop="address" content="([^"]+)"', b)
        venue = html.unescape(place.group(1)).strip() if place else None
        city = "Budapest"
        if addr:                                                        # "1073 Budapest, …" / "9021 Győr, …"
            cm = re.search(r"\d{4}\s+([A-ZÁÉÍÓÖŐÚÜŰ][\wÁÉÍÓÖŐÚÜŰáéíóöőúüű.\- ]+?)[,.]",
                           html.unescape(addr.group(1)))
            if cm:
                city = cm.group(1).strip().replace("ô", "ő").replace("û", "ű")
        if not venue:
            dropped.append(f"{title} (無場館)"); continue
        try:
            d = get(url.group(1))
        except Exception:
            continue
        future = [x for x in sorted(set(re.findall(r"20\d{2}-\d{2}-\d{2}", d))) if x >= today]
        if not future:
            dropped.append(f"{title} (已結束/無未來場)"); continue
        out.append({"title": title, "venue": venue, "city": city, "country": "Hungary",
                    "start": future[0], "end": future[-1], "image": img.group(1) if img else None,
                    "url": url.group(1), "source": "jegy.hu"})
    return out, dropped


def main():
    rows, dropped = [], []
    for fn in (scrape_hungary,):
        try:
            r, d = fn()
            rows += r; dropped += d
            print(f"  {fn.__name__}: {len(r)} kept", flush=True)
        except Exception as e:
            print(f"  {fn.__name__} failed: {e}", flush=True)
    shows = []
    for s in rows:
        sid = "ee-" + hashlib.md5(f"{s['source']}|{s['title']}|{s['venue']}".encode()).hexdigest()[:8]
        shows.append({
            "id": sid, "title": s["title"], "title_en": "",
            "venue": s["venue"], "city": s["city"], "country": s["country"],
            "lat": None, "lng": None, "start_date": s["start"], "end_date": s["end"],
            "image": s["image"], "ticket_url": s["url"],
            "type": "tour", "verified": True, "source": s["source"],
        })
    out = {"meta": {"source": "easteurope (jegy.hu+)", "count": len(shows)}, "shows": shows}
    (DATA / "easteurope.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {len(shows)} -> data/easteurope.json", flush=True)
    for s in shows:
        print(f"    keep: {s['title']} @ {s['venue']} {s['start_date']}~{s['end_date']}", flush=True)
    for d in dropped[:20]:
        print("    drop:", d, flush=True)


if __name__ == "__main__":
    main()
