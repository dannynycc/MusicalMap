"""Fill the end_date of open-ended long-runners from real ticketing data.

Resident shows (Broadway / West End / EU long-runs) don't announce a closing date,
so sources give end_date = null. Treating "no end" as "runs forever" wrongly kept
them on the map years out (Buena Vista Social Club still showing at 2029 though it's
only booked through Jan 2027). Ticketmaster IS the ticketing system, so its LAST
on-sale performance is the authoritative booking horizon — we query it sorted by
date descending and take that latest date as end_date.

Reads data/shows.json (post-build), writes data/booking_horizon.json = {id: "YYYY-MM-DD"}.
build_shows.py applies it to any show whose end_date is still null.

KEY: env TICKETMASTER_API_KEY, else scrapers/.tm_key (both gitignored).
Run: python scrapers/booking_horizon.py
"""

import json
import os
import re
import sys
import io
import time
import urllib.request
import urllib.parse
from datetime import datetime
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
_KEYFILE = Path(__file__).resolve().parent / ".tm_key"
KEY = os.environ.get("TICKETMASTER_API_KEY") or (
    _KEYFILE.read_text(encoding="utf-8").strip() if _KEYFILE.exists() else "")
API = "https://app.ticketmaster.com/discovery/v2/events.json"

# country (our display form) -> Ticketmaster ISO country code
CC = {"USA": "US", "UK": "GB", "Germany": "DE", "Spain": "ES", "France": "FR",
      "Netherlands": "NL", "Mexico": "MX", "Japan": "JP", "Austria": "AT",
      "Switzerland": "CH", "Ireland": "IE", "Canada": "CA", "Australia": "AU"}


def norm(s):
    return re.sub(r"[^a-z0-9]", "", (s or "").lower())


def city_key(c):
    return norm((c or "").split(",")[0])


def tm_events(title, cc):
    """Latest-first theatre events for a title in a country."""
    q = urllib.parse.urlencode({
        "keyword": title, "countryCode": cc, "segmentName": "Arts & Theatre",
        "size": 30, "sort": "date,desc", "apikey": KEY})
    try:
        with urllib.request.urlopen(API + "?" + q, timeout=30) as r:
            d = json.loads(r.read().decode("utf-8"))
    except Exception as e:
        print(f"    TM error: {str(e)[:80]}", flush=True)
        return []
    return d.get("_embedded", {}).get("events", [])


def last_date(show):
    """The latest TM on-sale performance date that matches this show's city/venue."""
    cc = CC.get(show.get("country"))
    if not cc:
        return None
    evs = tm_events(show["title"], cc)
    time.sleep(0.15)
    sv, sc = norm(show.get("venue")), city_key(show.get("city"))
    best = None
    for e in evs:
        d = e.get("dates", {}).get("start", {}).get("localDate")
        if not d:
            continue
        ven = e.get("_embedded", {}).get("venues", [{}])[0]
        ev_v, ev_c = norm(ven.get("name")), city_key((ven.get("city") or {}).get("name"))
        # match on city, and on venue when both names are present (TM naming varies)
        if sc and ev_c and sc != ev_c:
            continue
        if sv and ev_v and sv not in ev_v and ev_v not in sv:
            continue
        if best is None or d > best:
            best = d
    return best


def main():
    if not KEY:
        sys.exit("No Ticketmaster key: set TICKETMASTER_API_KEY or write scrapers/.tm_key")
    shows = json.loads((DATA / "shows.json").read_text(encoding="utf-8"))["shows"]
    open_runs = [s for s in shows if not s.get("end_date") and s.get("start_date")]
    print(f"Resolving booking horizon for {len(open_runs)} open-ended show(s) via Ticketmaster", flush=True)
    today = datetime.now().strftime("%Y-%m-%d")
    out, found = {}, 0
    for s in open_runs:
        d = last_date(s)
        if d and d > today and d < "2032-01-01":      # sane future window
            out[s["id"]] = d
            found += 1
            print(f"  ✓ {d}  {s['title'][:32]} @ {s.get('venue')} ({s.get('city')})", flush=True)
        else:
            print(f"  – no TM date  {s['title'][:32]} ({s.get('city')}, {s.get('country')})", flush=True)
    (DATA / "booking_horizon.json").write_text(
        json.dumps({"_comment": "open-ended shows' last on-sale date (Ticketmaster); applied as end_date by build_shows",
                    **out}, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\nWrote {found}/{len(open_runs)} booking horizons -> data/booking_horizon.json", flush=True)


if __name__ == "__main__":
    main()
