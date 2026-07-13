"""Portugal — source: BOL / Bilheteira Online (bol.pt), Portugal's main ticketing site.

Ticketmaster has zero musicals for Portugal, so we read BOL directly. Every event page
carries a clean JSON-LD Event with name, start/end dates, poster image, and a Place
location that INCLUDES geo coordinates (WGS-84) + city — so no geocoding is needed.

We collect event links from the homepage, keep the ones whose page is in the theatre
category (body class `catTeatro`) AND look like a musical — either the title contains
"musical", or it matches a work registered in data/works.json (so Broadway/West End
tours like Evita / The Phantom of the Opera are caught even without "musical" in the
title). build_shows.py then tags by work origin (registry → else Portugal = 西葡音樂劇).

Output: data/portugal.json   Run: python scrapers/portugal.py
"""

import json
import re
import sys
import io
import time
import unicodedata
import urllib.request
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

DATA = Path(__file__).resolve().parent.parent / "data"
BASE = "https://www.bol.pt"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    return urllib.request.urlopen(req, timeout=25).read().decode("utf-8", "ignore")


def _norm(s):
    s = unicodedata.normalize("NFKD", (s or "").lower())
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+", "", s)


def load_registry_norms():
    """Normalised set of every registered work title + alias, to recognise musicals
    (esp. Broadway tours) whose BOL title doesn't contain the word 'musical'."""
    out = set()
    try:
        works = json.loads((DATA / "works.json").read_text(encoding="utf-8")).get("works", [])
    except Exception:  # noqa: BLE001
        return out
    for w in works:
        for s in [w.get("canonical")] + (w.get("aliases") or []):
            n = _norm(s)
            if len(n) >= 4:
                out.add(n)
    return out


def parse_event(html):
    m = re.search(r'<script type="application/ld\+json">(.*?)</script>', html, re.S)
    if not m:
        return None
    try:
        d = json.loads(m.group(1))
    except Exception:  # noqa: BLE001
        return None
    if d.get("@type") != "Event":
        return None
    loc = d.get("location") or {}
    geo = loc.get("geo") or {}
    addr = loc.get("address") or {}
    try:
        lat, lng = float(geo.get("latitude")), float(geo.get("longitude"))
    except (TypeError, ValueError):
        lat = lng = None
    return {
        "name": (d.get("name") or "").strip(),
        "start": (d.get("startDate") or "")[:10] or None,
        "end": (d.get("endDate") or "")[:10] or None,
        # JSON-LD 的 image 是 185×240 縮圖;同資產有 _grande 大圖(740×960)。
        # 2026-07-14 海報守門抽樣抓到 Grease Lisboa 糊圖案。
        "image": re.sub(r"(/cartaz\d+)(\.jpg)", r"\1_grande\2", d.get("image"))
                 if d.get("image") else None,
        "venue": (loc.get("name") or "").strip().rstrip("."),
        "city": addr.get("addressLocality") or "Lisbon",
        "lat": lat, "lng": lng,
    }


def is_musical(name, reg):
    n = name.lower()
    if "musical" in n:
        return True
    return _norm(name) in reg


def main():
    reg = load_registry_norms()
    hp = fetch(BASE + "/")
    links = sorted(set(re.findall(r"/Comprar/Bilhetes/\d+[A-Za-z0-9_\-]*/?", hp)))
    print(f"{len(links)} event links on homepage")

    shows = {}
    for path in links:
        try:
            html = fetch(BASE + path)
        except Exception:  # noqa: BLE001
            continue
        if "catTeatro" not in html[:600]:        # body class → theatre category only
            continue
        ev = parse_event(html)
        if not ev or not ev["name"] or not is_musical(ev["name"], reg):
            continue
        if ev["lat"] is None:
            continue                              # no coord from BOL → skip (never guess)
        eid = re.search(r"/Bilhetes/(\d+)", path).group(1)
        sid = "bol-" + eid
        shows[sid] = {
            "id": sid, "title": ev["name"], "type": "limited",
            "venue": ev["venue"], "city": ev["city"], "country": "Portugal",
            "lat": ev["lat"], "lng": ev["lng"],
            "start_date": ev["start"], "end_date": ev["end"],
            "ticket_url": BASE + path, "image": ev["image"],
            "tour_name": None, "verified": True, "source": "bol.pt",
        }
        print(f"  {ev['name'][:34]:36s} @ {ev['venue'][:22]:24s} {ev['city']:10s} {ev['start']}~{ev['end']}")
        time.sleep(0.25)

    out = {"meta": {"source": "bol.pt", "count": len(shows)}, "shows": list(shows.values())}
    (DATA / "portugal.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nWrote {len(shows)} shows -> data/portugal.json")


if __name__ == "__main__":
    main()
