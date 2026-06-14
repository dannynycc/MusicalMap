"""Per-show tour sweep via the Ticketmaster attraction API.

For EVERY show already in shows.json, search TM for its attraction(s) and pull
ALL of that attraction's events worldwide, aggregated into per-venue stops.
This catches tours that no listing source carries (e.g. the Beetlejuice North
American tour, absent from broadway.org). Matching is strict: an attraction is
accepted only if its normalized name equals the show's group key — no fuzzy
guesses. Dates are TM availability windows (onsale_only), same semantics as
ticketmaster.py.

Needs TICKETMASTER_API_KEY.  Output: data/tm_tours.json
"""

import json
import os
import re
import sys
import io
import time
import unicodedata
import urllib.request
import urllib.parse
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

DATA = Path(__file__).resolve().parent.parent / "data"
_KEYFILE = Path(__file__).resolve().parent / ".tm_key"   # gitignored local key
KEY = os.environ.get("TICKETMASTER_API_KEY") or (
    _KEYFILE.read_text(encoding="utf-8").strip() if _KEYFILE.exists() else "")
ATTR_API = "https://app.ticketmaster.com/discovery/v2/attractions.json"
EV_API = "https://app.ticketmaster.com/discovery/v2/events.json"


def norm(title):
    t = re.sub(r"[–—]", "-", title or "")
    t = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode().lower().strip()
    t = re.sub(r"^the\s+", "", t)
    t = re.sub(r"^disney(?:'s| presents)\s+", "", t)
    t = re.sub(r"\s*\((?:touring|australia|uk|us|usa|broadway|the musical)\)", "", t)
    t = re.sub(r"\s*[:\-]\s*[^:]*musical.*$", "", t)
    t = re.sub(r"\s+(?:the\s+)?(?:[\w'!\-]+\s+){0,4}musical$", "", t)
    t = re.sub(r"[^a-z0-9]+", " ", t).strip()
    return t


def get(url, params):
    params["apikey"] = KEY
    req = urllib.request.Request(url + "?" + urllib.parse.urlencode(params),
                                 headers={"User-Agent": "Mozilla/5.0"})
    return json.loads(urllib.request.urlopen(req, timeout=30).read().decode("utf-8"))


def main():
    if not KEY:
        print("✗ TICKETMASTER_API_KEY not set — skipped (no output written)")
        return
    shows = json.load(open(DATA / "shows.json", encoding="utf-8"))["shows"]
    groups = {}
    for s in shows:
        g = s.get("group") or norm(s["title"])
        groups.setdefault(g, s["title"])
    print(f"{len(groups)} distinct shows to sweep")

    runs, matched, n_cancel = {}, 0, 0
    for g, title in sorted(groups.items()):
        try:
            data = get(ATTR_API, {"keyword": title, "classificationName": "Musical", "size": 5})
        except Exception:
            time.sleep(0.5)
            continue
        atts = [a for a in data.get("_embedded", {}).get("attractions", [])
                if norm(a.get("name")) == g]
        time.sleep(0.25)
        if not atts:
            continue
        matched += 1
        for a in atts[:3]:
            page = 0
            while page < 5:
                try:
                    ev = get(EV_API, {"attractionId": a["id"], "size": 200, "page": page,
                                      "sort": "date,asc"})
                except Exception:
                    break
                events = ev.get("_embedded", {}).get("events", [])
                if not events:
                    break
                for e in events:
                    status = ((e.get("dates", {}).get("status") or {}).get("code") or "").lower()
                    if status in ("cancelled", "canceled", "postponed"):
                        n_cancel += 1
                        continue                          # dead listings (404 / "event canceled")
                    v = (e.get("_embedded", {}).get("venues") or [{}])[0]
                    loc = v.get("location") or {}
                    venue = (v.get("name") or "").strip()
                    date = (e.get("dates", {}).get("start", {}) or {}).get("localDate")
                    if not venue or not loc.get("latitude") or not date:
                        continue
                    key = (g, venue.lower())
                    r = runs.get(key)
                    if not r:
                        runs[key] = {
                            "id": "tmt-" + re.sub(r"[^a-z0-9]+", "-", f"{g}-{venue}".lower()).strip("-"),
                            "title": title, "type": "tour",
                            "venue": venue,
                            "city": (v.get("city") or {}).get("name") or "",
                            "country": (v.get("country") or {}).get("name") or "",
                            "lat": round(float(loc["latitude"]), 6),
                            "lng": round(float(loc["longitude"]), 6),
                            "start_date": date, "end_date": date,
                            "ticket_url": a.get("url") or e.get("url"),   # stable attraction page, not expiring event URL
                            "attraction_url": a.get("url"),
                            "image": None,  # inherit the show's poster at build
                            "tour_name": None, "verified": True,
                            "onsale_only": True,
                            "source": "ticketmaster",
                        }
                    else:
                        if date < r["start_date"]:
                            r["start_date"] = date
                        if date > r["end_date"]:
                            r["end_date"] = date
                page += 1
                time.sleep(0.25)

    out = {"meta": {"source": "ticketmaster attraction sweep",
                    "shows_swept": len(groups), "shows_matched": matched,
                    "stops": len(runs)},
           "shows": list(runs.values())}
    (DATA / "tm_tours.json").write_text(json.dumps(out, ensure_ascii=False, indent=2),
                                        encoding="utf-8")
    print(f"matched {matched} shows on TM; wrote {len(runs)} venue-stops -> data/tm_tours.json")
    print(f"  skipped {n_cancel} cancelled/postponed event(s) (zombie listings)")


if __name__ == "__main__":
    main()
