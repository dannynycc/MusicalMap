"""Global musicals via the Ticketmaster Discovery API.

⚠️ REQUIRES A FREE API KEY — set env var TICKETMASTER_API_KEY.
   Get one at https://developer.ticketmaster.com (register an app → Consumer Key).
   Without the key every endpoint returns 401, so this scraper is UNTESTED until
   a key is supplied; once it is, run it and verify the output before trusting it.

Covers countries the other scrapers miss (Australia, NZ, much of Europe, etc.).
Ticketmaster returns one event per performance date, so we aggregate events that
share a show + venue into a single run (min start date → max end date).

Output: data/ticketmaster.json   Run: TICKETMASTER_API_KEY=xxx python scrapers/ticketmaster.py
"""

import json
import os
import re
import sys
import io
import time
import urllib.request
import urllib.parse
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

DATA = Path(__file__).resolve().parent.parent / "data"
API = "https://app.ticketmaster.com/discovery/v2/events.json"
KEY = os.environ.get("TICKETMASTER_API_KEY")
# One Discovery API spans every national Ticketmaster site; we sweep each market
# by ISO country code. Dedupe is by (show, venue) so the same production showing
# up under multiple country sites collapses into one record (collecting each
# region's ticket link). Extend this list to widen coverage.
# Only sweep countries the curated sources DON'T cover (US/UK/JP/DE/ES/FR/MX/NL
# are already covered and dropped at build anyway). Smaller volumes here let us
# fetch ALL pages, so end_date = the real last scheduled performance.
# GB included: London is curated (londontheatre.co.uk) but the UK REGIONAL
# touring circuit (Manchester/Glasgow/…) isn't — build keeps TM GB records for
# non-London cities only. (Lesson from missing the Miss Saigon UK tour.)
# US included not for new markers (Broadway/tours are curated) but so build can
# ATTACH Ticketmaster purchase links to existing records (link enrichment).
COUNTRIES = ["AU", "NZ", "GB", "IE", "CA", "BE", "DK", "SE", "NO", "FI",
             "AT", "CH", "PL", "IT", "PT", "CZ", "SG", "US"]


def clean_title(t):
    """Normalize the noisy event names Ticketmaster uses so the same production
    collapses to one record (accessibility/preview performances, region tags,
    promoter prefixes, ALL-CAPS)."""
    t = (t or "").strip()
    if re.search(r"do not purchase|test event", t, re.I):
        return ""  # junk/test listings
    # promoter prefixes
    t = re.sub(r"^(disney\s+presents\s+|disney'?s\s+|cameron\s+mackintosh'?s\s+)", "", t, flags=re.I)
    # region / version parenthetical anywhere, e.g. "(Australia)", "(UK)", "(Touring)"
    t = re.sub(r"\s*\((?:australia|uk|us|usa|touring|broadway|the\s+musical)\)", "", t, flags=re.I)
    # accessibility / performance-type qualifiers after a dash (drop to end)
    t = re.sub(
        r"\s*[-–]\s*(auslan|audio[- ]?desc|relaxed|opening night|night with|previews?|"
        r"captioned|matinee|sensory|signed|the broadway musical|the musical|broadway)\b.*$",
        "", t, flags=re.I)
    # trailing accessibility words without a dash
    t = re.sub(r"\s+(relaxed performance|captioned.*|audio desc.*)$", "", t, flags=re.I)
    # bare trailing "the musical"
    t = re.sub(r"\s*(?:[-–:]\s*)?the\s+musical$", "", t, flags=re.I)
    t = t.strip(" -–:")
    if len(t) > 4 and t.isupper():       # de-shout ALL-CAPS titles
        t = t.title()
    return t


def fetch(params):
    url = API + "?" + urllib.parse.urlencode(params)
    with urllib.request.urlopen(url, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))


def sweep_country(cc):
    """Yield raw musical events for one country, paginating."""
    page = 0
    while True:
        data = fetch({
            "apikey": KEY,
            "classificationName": "Musical",
            "segmentName": "Arts & Theatre",
            "countryCode": cc,
            "size": 100,
            "page": page,
            "sort": "date,asc",
        })
        for ev in data.get("_embedded", {}).get("events", []):
            yield ev
        info = data.get("page", {})
        page += 1
        if page >= info.get("totalPages", 0) or page > 24:  # gap countries are small; fetch (nearly) all
            break
        time.sleep(0.25)


def main():
    if not KEY:
        print("✗ TICKETMASTER_API_KEY not set — get a free key at "
              "https://developer.ticketmaster.com and re-run. (no output written)")
        return

    runs = {}  # (show, venue) -> aggregated record
    for cc in COUNTRIES:
        try:
            for ev in sweep_country(cc):
                # classification gating: keep only genuine musicals
                cl = (ev.get("classifications") or [{}])[0]
                genre = ((cl.get("genre") or {}).get("name") or "").lower()
                sub = ((cl.get("subGenre") or {}).get("name") or "").lower()
                seg = ((cl.get("segment") or {}).get("name") or "").lower()
                # "Musical" is the subGenre under genre "Theatre"
                if seg != "arts & theatre" or "musical" not in (genre + " " + sub):
                    continue
                v = (ev.get("_embedded", {}).get("venues") or [{}])[0]
                loc = v.get("location") or {}
                title = clean_title(ev.get("name") or "")
                venue = (v.get("name") or "").strip()
                date = (ev.get("dates", {}).get("start", {}) or {}).get("localDate")
                if not title or not venue or not loc.get("latitude"):
                    continue
                key = (title.lower(), venue.lower())
                rec = runs.get(key)
                if not rec:
                    att = (ev.get("_embedded", {}).get("attractions") or [{}])[0]
                    imgs = sorted(ev.get("images", []), key=lambda i: -(i.get("width") or 0))
                    runs[key] = {
                        "id": "tm-" + re.sub(r"[^a-z0-9]+", "-", f"{title}-{venue}".lower()).strip("-"),
                        "title": title, "type": "tour",  # TM runs are limited engagements / tour stops
                        "venue": venue,
                        "city": (v.get("city") or {}).get("name") or "",
                        "country": (v.get("country") or {}).get("name") or cc,
                        "lat": round(float(loc["latitude"]), 6),
                        "lng": round(float(loc["longitude"]), 6),
                        "start_date": date, "end_date": date,
                        "ticket_url": ev.get("url"),
                        # stable show-level page (e.g. /ragtime-ny-tickets/artist/123) —
                        # used when attaching TM as an extra purchase link
                        "attraction_url": att.get("url"),
                        # one ticket link per region/country, shown in the card
                        "ticket_links": ([{"country": cc, "url": ev["url"]}] if ev.get("url") else []),
                        "image": imgs[0]["url"] if imgs else None,
                        "tour_name": None, "verified": True,
                        "source": "ticketmaster",
                    }
                else:  # widen the run's date range + collect this region's link
                    if date and (not rec["start_date"] or date < rec["start_date"]):
                        rec["start_date"] = date
                    if date and (not rec["end_date"] or date > rec["end_date"]):
                        rec["end_date"] = date
                    if ev.get("url") and not any(l["country"] == cc for l in rec["ticket_links"]):
                        rec["ticket_links"].append({"country": cc, "url": ev["url"]})
            print(f"  {cc}: {len(runs)} cumulative runs")
        except Exception as e:  # noqa: BLE001
            print(f"  [{cc}] failed: {e}")

    # NOTE: start_date is the earliest *available* performance (the API drops
    # expired dates), end_date the last scheduled performance. We keep them as-is
    # (no faking) — for a "what's playing on date X" view, the real available
    # window is the honest answer. onsale_only flags that these are availability
    # dates, not a confirmed opening→closing run, so the UI can label them right.
    for r in runs.values():
        r["onsale_only"] = True

    shows = list(runs.values())
    out = {"meta": {"source": "ticketmaster", "count": len(shows)}, "shows": shows}
    (DATA / "ticketmaster.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nWrote {len(shows)} runs -> data/ticketmaster.json")


if __name__ == "__main__":
    main()
