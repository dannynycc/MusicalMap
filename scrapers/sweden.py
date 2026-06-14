"""Swedish musicals — Showtic.se (the official ticketing platform for the
2Entertain / Scala family of commercial musical houses: Oscarsteatern, China
Teatern, Göta Lejon, Intiman, Lorensbergsteatern, …).

Showtic is a Next.js + Sanity CMS app. The page HTML embeds the full dataset in
the <script id="__NEXT_DATA__"> tag, but there is an even cleaner route: the
internal JSON API `/api/shows?limit=100` returns ALL current shows in one call as
`{"data":[...], "metadata":{"total":N}}` — no headless browser needed, just a
browser User-Agent.

Each show carries: title, slug.current, genres[].name / secondaryGenres[].name,
firstEvent / lastEvent ({dateAndTime, venue.{displayName, city}}) and
posterImage.asset._ref (a Sanity image ref we turn into a CDN URL).

The /forestallningar/musikal URL is genre-filtered server-side but is *loose*
(it includes shows merely tagged "Show"/"Konsert" alongside Musikal, and misses
some). So we pull the whole catalogue and post-filter on the genre array
ourselves: keep only shows tagged "Musikal".

Output: data/sweden.json     Run: python scrapers/sweden.py
"""

import json
import sys
import io
import hashlib
import urllib.request
from datetime import datetime, timezone, timedelta
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
DATA = Path(__file__).resolve().parent.parent / "data"
# Swedish local time (CEST in summer); only used to compute "today" for the
# end_date >= today future filter, so the exact DST offset is not critical.
CET = timezone(timedelta(hours=2))
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0",
      "Accept-Language": "sv"}

SHOWS_API = "https://showtic.se/api/shows?limit=100"
SANITY_PROJECT = "3553xkck"  # Showtic's Sanity project id (cdn.sanity.io/images/<id>/production/...)

# Building-level coordinates, looked up by hand. Matched by substring against the
# venue displayName (so "Wallmans Stockholm" etc. still resolve if a key is a
# substring). Keys are the displayName as Showtic returns it.
# The first six are the requested Scala-family houses; GöteborgsOperan and Malmö
# Opera are included per spec in case they ever appear (Showtic does not carry
# them today). The remainder are other venues Showtic actually lists musicals at.
VENUES = {
    # --- Stockholm ---
    "Oscarsteatern":      (59.3299, 18.0686),  # Kungsgatan 63, Stockholm
    "China Teatern":      (59.3318, 18.0700),  # Berzelii Park 9, Stockholm
    "Göta Lejon":         (59.3146, 18.0721),  # Götgatan 55, Stockholm
    "Intiman":            (59.3417, 18.0507),  # Odengatan 81, Stockholm
    "Cirkus":             (59.3268, 18.1003),  # Djurgårdsslätten 43-45, Stockholm
    # --- Göteborg ---
    "Lorensbergsteatern": (57.6986, 11.9809),  # Lorensbergsparken, Göteborg
    "GöteborgsOperan":    (57.7113, 11.9667),  # Christina Nilssons Gata, Göteborg
    "Rondo":              (57.6962, 11.9869),  # Liseberg, Örgrytevägen 5, Göteborg
    # --- Malmö ---
    "Malmö Opera":        (55.5953, 13.0049),  # Östra Rönneholmsvägen 20, Malmö
    # --- other Showtic musical venues ---
    "Sara Kulturhus":     (64.7505, 20.9527),  # Skellefteå
    "Höga Kusten Friluftsteater": (62.9870, 18.0780),  # Lövvik, Västernorrland
    "Brunnsparken, Ronneby":      (56.2030, 15.2790),  # Ronneby Brunnspark
}


def get(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", "ignore")


def poster_url(poster):
    """Sanity image ref -> CDN URL.
    ref looks like 'image-<hash>-<WxH>-<ext>'  ->
    https://cdn.sanity.io/images/<project>/production/<hash>-<WxH>.<ext>
    (strip the leading 'image-', turn the final '-<ext>' into '.<ext>')."""
    try:
        ref = poster["asset"]["_ref"]
    except (TypeError, KeyError):
        return None
    if not ref.startswith("image-"):
        return None
    body = ref[len("image-"):]
    base, ext = body.rsplit("-", 1)          # base = '<hash>-<WxH>', ext = 'jpg'
    return f"https://cdn.sanity.io/images/{SANITY_PROJECT}/production/{base}.{ext}"


def genres_of(show):
    """Flat set of every genre name on the show (primary + secondary)."""
    names = set()
    for key in ("genres", "secondaryGenres"):
        for g in show.get(key) or []:
            if isinstance(g, dict) and g.get("name"):
                names.add(g["name"])
    return names


def coords_for(display_name):
    """Substring match venue displayName -> (lat, lng); unknown -> (None, None)."""
    if not display_name:
        return None, None
    for key, (lat, lng) in VENUES.items():
        if key in display_name:
            return lat, lng
    return None, None


def scrape_showtic():
    data = json.loads(get(SHOWS_API)).get("data", [])
    today = datetime.now(CET).strftime("%Y-%m-%d")
    out, dropped = [], []
    for s in data:
        title = (s.get("title") or "").strip()
        genres = genres_of(s)

        # MUSICAL FILTER: must be tagged Musikal, else drop (logging the reason).
        if "Musikal" not in genres:
            dropped.append(f"{title} (非音樂劇: {','.join(sorted(genres)) or '無 genre'})")
            continue

        fe = s.get("firstEvent") or {}
        le = s.get("lastEvent") or {}
        venue = (fe.get("venue") or {}).get("displayName")
        city = (fe.get("venue") or {}).get("city")
        start = (fe.get("dateAndTime") or "")[:10]   # YYYY-MM-DD
        end = (le.get("dateAndTime") or "")[:10] or start

        if not start:
            dropped.append(f"{title} (無日期)")
            continue
        # FUTURE/CURRENT only: drop runs whose last performance is already past.
        if end < today:
            dropped.append(f"{title} (已結束 {end})")
            continue

        slug = (s.get("slug") or {}).get("current")
        url = (f"https://showtic.se/forestallningar/{slug}" if slug
               else "https://showtic.se/forestallningar")
        lat, lng = coords_for(venue)

        out.append({
            "title": title, "venue": venue, "city": city,
            "start": start, "end": end,
            "image": poster_url(s.get("posterImage")),
            "url": url, "lat": lat, "lng": lng,
        })
    return out, dropped


def main():
    rows, dropped = [], []
    try:
        rows, dropped = scrape_showtic()
        print(f"  scrape_showtic: {len(rows)} kept", flush=True)
    except Exception as e:
        print(f"  scrape_showtic failed: {e}", flush=True)

    shows = []
    for s in rows:
        sid = "se-" + hashlib.md5(
            f"showtic.se|{s['title']}|{s['venue']}".encode()).hexdigest()[:8]
        shows.append({
            "id": sid, "title": s["title"], "title_en": "",
            "venue": s["venue"], "city": s["city"], "country": "Sweden",
            "lat": s["lat"], "lng": s["lng"],
            "start_date": s["start"], "end_date": s["end"],
            "image": s["image"], "ticket_url": s["url"],
            "type": "tour", "verified": True, "source": "showtic.se",
        })

    out = {"meta": {"source": "showtic.se", "count": len(shows)}, "shows": shows}
    (DATA / "sweden.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Wrote {len(shows)} -> data/sweden.json", flush=True)
    with_coords = sum(1 for s in shows if s["lat"] is not None)
    print(f"  coords: {with_coords}/{len(shows)} resolved, "
          f"{len(shows) - with_coords} null", flush=True)
    for s in shows:
        flag = "" if s["lat"] is not None else "  [no coords]"
        print(f"    keep: {s['title']} @ {s['venue']} ({s['city']}) "
              f"{s['start_date']}~{s['end_date']}{flag}", flush=True)
    print(f"  dropped {len(dropped)}:", flush=True)
    for d in dropped:
        print("    drop:", d, flush=True)


if __name__ == "__main__":
    main()
