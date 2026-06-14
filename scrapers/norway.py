"""Norwegian musicals — Norway's resident musical houses are NOT in the Ticketmaster
Discovery API, so the global scrapers miss almost the entire scene. Built
source-by-source like easteurope.py / japan.py (stdlib only, UTF-8 stdout).

Sources (all static HTML / public JSON; no headless needed):

  - Folketeateret (folketeateret.no, Oslo) — the flagship musical house. The home
    page links every running production at /forestilling/{slug}; each detail page
    carries a JSON-LD block (schema.org WebSite: name + image) and lists every
    performance as Norwegian text "DD. mon YYYY" → first..last = the run. The house
    only stages musicals; we keep shows whose page mentions musikal/musikkteater and
    drop anything tagged as a pure concert/revue/stand-up.

  - Det Norske Teatret (detnorsketeatret.no, Oslo) — the genre listing page
    /framsyningar/musikal-og-musikkteater already filters to musicals, so its slugs
    ARE the musical set (no per-page genre guessing). Each /framsyningar/{slug} page
    embeds the full performance schedule as schema.org Events in JSON-LD; their
    "startDate" values give the complete run (the visible "day-and-time" widget only
    shows the next ~5 dates, and a naive ISO scan also catches the build/cache
    timestamp — so we read startDate). Poster via imgix.

  - Trøndelag Teater (trondelag-teater.no, Trondheim) — WordPress. The public REST
    endpoint /wp-json/wp/v2/calendar returns every performance keyed by date with
    name + slug + venue, giving a clean run range per show. The API exposes NO
    machine-readable genre, so we keep only slugs in a small known-musical allowlist
    (currently Matilda) rather than risk false positives.

  - Chateau Neuf (Moulin Rouge!, Chicago): SKIPPED — the site's TLS certificate is
    misconfigured (hostname mismatch) so it can't be fetched cleanly, and its big
    titles (Moulin Rouge!) are already covered by the Ticketmaster.no feed.

Output: data/norway.json     Run: python scrapers/norway.py
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
CET = timezone(timedelta(hours=2))  # Norway summer time; only used for "today"
TODAY = datetime.now(CET).strftime("%Y-%m-%d")
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0",
      "Accept-Language": "nb,nn,en"}

# Norwegian month abbreviations used by Folketeateret ("03. sep 2026").
NO_MONTHS = {"jan": "01", "feb": "02", "mar": "03", "apr": "04", "mai": "05",
             "jun": "06", "jul": "07", "aug": "08", "sep": "09", "okt": "10",
             "nov": "11", "des": "12"}

# Words that, in a TITLE, mark a non-musical event (concert / revue / stand-up /
# talk / guided tour). Deliberately narrow: words like "opera", "dans" or "ballett"
# are NOT here because licensed musical titles contain them (e.g. "Phantom of the
# Opera"). Genre proper is handled per-source, this is only a title sanity guard.
NON_MUSICAL = re.compile(
    r"\b(konsert|revy|stand-?up|standup|foredrag|omvisning|julekonsert|nytt[åa]rskonsert)\b",
    re.I)

# Building-level coordinates for the resident houses (web-looked-up).
VENUES = {
    "Folketeateret":        (59.9133, 10.7497, "Oslo"),     # Storgata 21-23, Oslo
    "Det Norske Teatret":   (59.9114, 10.7370, "Oslo"),     # Kristian IVs gate 8
    "Chateau Neuf":         (59.9270, 10.7170, "Oslo"),     # Slemdalsveien 15
    "Trøndelag Teater":     (63.4297, 10.3960, "Trondheim"),  # Prinsens gate 18-20
    "Den Nationale Scene":  (60.3897, 5.3220,  "Bergen"),    # Engen 1, Bergen
}


def get(url):
    """Fetch a URL as UTF-8 text (stdlib only)."""
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=40) as r:
        return r.read().decode("utf-8", "ignore")


def coords_for(venue):
    """Match a venue name (substring) to building-level lat/lng/city; unknown → nulls."""
    for key, (lat, lng, city) in VENUES.items():
        if key.lower() in venue.lower():
            return lat, lng, city
    return None, None, None


# ---------------------------------------------------------------- Folketeateret
def scrape_folketeateret():
    base = "https://www.folketeateret.no"
    home = get(base + "/")
    slugs = list(dict.fromkeys(re.findall(r"/forestilling/([\w-]+)", home)))
    out, dropped = [], []
    for slug in slugs:
        try:
            d = get(f"{base}/forestilling/{slug}")
        except Exception:
            continue
        # Title + poster come from the JSON-LD WebSite block.
        title, image = slug.replace("-", " ").title(), None
        m = re.search(r'application/ld\+json[^>]*>(.*?)</script>', d, re.S)
        if m:
            try:
                g = json.loads(m.group(1)).get("@graph", [])
                site = next((o for o in g if o.get("@type") == "WebSite"), {})
                title = html.unescape(site.get("name", title)).strip()
                img = site.get("image")
                if isinstance(img, dict):
                    image = img.get("url")
            except Exception:
                pass
        # Musical guard: this is a musical house, but skip anything explicitly a
        # concert/revue/etc. and require some musikal/musikkteater signal.
        if NON_MUSICAL.search(title):
            dropped.append(f"{title} (tittel ikke musikal)"); continue
        if "musikal" not in d.lower() and "musikkteater" not in d.lower():
            dropped.append(f"{title} (ingen musikal-markør)"); continue
        # Performance dates: "DD. mon YYYY" Norwegian text → ISO; range = min..max.
        iso = sorted({f"{y}-{NO_MONTHS[mon.lower()[:3]]}-{int(dd):02d}"
                      for dd, mon, y in re.findall(
                          r"(\d{1,2})\.\s*(jan|feb|mar|apr|mai|jun|jul|aug|sep|okt|nov|des)\w*\.?\s*(20\d{2})",
                          d, re.I)})
        future = [x for x in iso if x >= TODAY]
        if not future:
            dropped.append(f"{title} (ingen framtidige datoer)"); continue
        out.append({"title": title, "venue": "Folketeateret",
                    "start": future[0], "end": future[-1], "image": image,
                    "url": f"{base}/forestilling/{slug}", "source": "folketeateret.no"})
    return out, dropped


# ---------------------------------------------------- Det Norske Teatret (Oslo)
def scrape_detnorsketeatret():
    base = "https://www.detnorsketeatret.no"
    cat = get(base + "/framsyningar/musikal-og-musikkteater")
    # The genre page is pre-filtered to musicals; its slugs are the musical set.
    slugs = [s for s in dict.fromkeys(re.findall(r"/framsyningar/([\w-]+)", cat))
             if s != "musikal-og-musikkteater"]
    out, dropped = [], []
    for slug in slugs:
        try:
            d = get(f"{base}/framsyningar/{slug}")
        except Exception:
            continue
        # Title from <title> "Name | Framsyningar | Det Norske Teatret".
        tm = re.search(r"<title>(.*?)</title>", d, re.S)
        title = html.unescape(tm.group(1)).split("|")[0].strip() if tm else slug
        # Full run = startDate of every schema.org Event in the page's JSON-LD.
        iso = sorted({m[:10] for m in re.findall(
            r'"startDate":"(20\d{2}-\d{2}-\d{2})', d)})
        future = [x for x in iso if x >= TODAY]
        if not future:
            dropped.append(f"{title} (ingen framtidige datoer)"); continue
        img = re.search(r"(https://detnorsketeatret\.imgix\.net/[\w./?=&%.-]+)", d)
        image = html.unescape(img.group(1)).split("&amp")[0] if img else None
        out.append({"title": title, "venue": "Det Norske Teatret",
                    "start": future[0], "end": future[-1], "image": image,
                    "url": f"{base}/framsyningar/{slug}", "source": "detnorsketeatret.no"})
    return out, dropped


# ------------------------------------------- Trøndelag Teater (Trondheim, WP API)
# The calendar API has no genre field, so keep only known-musical slugs. Extend
# this set as new musicals are announced.
TT_MUSICAL_SLUGS = {"matilda"}


def scrape_trondelag():
    base = "https://www.trondelag-teater.no"
    cal = json.loads(get(base + "/wp-json/wp/v2/calendar?per_page=400"))
    # calendar shape: {date: {venue: {time: [events]}}}, but some days are lists.
    runs = {}  # slug -> {dates:set, name, place}

    def walk(node, sink):
        if isinstance(node, dict):
            if "name" in node and "time" in node:
                sink.append(node)
            else:
                for v in node.values():
                    walk(v, sink)
        elif isinstance(node, list):
            for v in node:
                walk(v, sink)

    for day, node in cal.items():
        events = []
        walk(node, events)
        for ev in events:
            slug = ev.get("performance_slug") or ev.get("name", "")
            r = runs.setdefault(slug, {"dates": set(), "name": ev.get("name"), "place": ""})
            r["dates"].add(day[:10])
            r["place"] = ev.get("place") or r["place"]

    out, dropped = [], []
    for slug, r in runs.items():
        if slug not in TT_MUSICAL_SLUGS:
            dropped.append(f"{r['name']} (ikke i musikal-liste)"); continue
        future = sorted(x for x in r["dates"] if x >= TODAY)
        if not future:
            dropped.append(f"{r['name']} (ingen framtidige datoer)"); continue
        # Poster from the show's detail page (og:image).
        image = None
        try:
            dp = get(f"{base}/forestillinger/{slug}/")
            im = re.search(r'property=["\']og:image["\']\s+content=["\']([^"\']+)', dp)
            image = im.group(1) if im else None
        except Exception:
            pass
        out.append({"title": html.unescape(r["name"]).strip(), "venue": "Trøndelag Teater",
                    "start": future[0], "end": future[-1], "image": image,
                    "url": f"{base}/forestillinger/{slug}/", "source": "trondelag-teater.no"})
    return out, dropped


def main():
    rows, dropped = [], []
    for fn in (scrape_folketeateret, scrape_detnorsketeatret, scrape_trondelag):
        try:
            r, d = fn()
            rows += r
            dropped += d
            print(f"  {fn.__name__}: {len(r)} kept, {len(d)} dropped", flush=True)
        except Exception as e:
            print(f"  {fn.__name__} failed: {e}", flush=True)

    shows = []
    for s in rows:
        lat, lng, city = coords_for(s["venue"])
        sid = "no-" + hashlib.md5(f"{s['source']}|{s['title']}|{s['venue']}".encode()).hexdigest()[:8]
        shows.append({
            "id": sid, "title": s["title"], "title_en": "",
            "venue": s["venue"], "city": city, "country": "Norway",
            "lat": lat, "lng": lng,
            "start_date": s["start"], "end_date": s["end"],
            "image": s["image"], "ticket_url": s["url"],
            "type": "resident", "verified": True, "source": s["source"],
        })

    out = {"meta": {"source": "norway", "count": len(shows)}, "shows": shows}
    (DATA / "norway.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Wrote {len(shows)} -> data/norway.json", flush=True)
    have = sum(1 for s in shows if s["lat"] is not None)
    print(f"coords: {have} located / {len(shows) - have} null", flush=True)
    for s in shows:
        print(f"    keep: {s['title']} @ {s['venue']} {s['start_date']}~{s['end_date']} "
              f"[{'coord' if s['lat'] else 'NO-COORD'}]", flush=True)
    for d in dropped:
        print("    drop:", d, flush=True)


if __name__ == "__main__":
    main()
