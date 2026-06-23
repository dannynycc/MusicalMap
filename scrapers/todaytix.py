"""TodayTix matcher — map our shows to their TodayTix deep link (for affiliate re-point).

TodayTix (Broadway / West End / + 11 more cities) has an OPEN JSON API (no auth, no
anti-bot) and is an Impact affiliate (~1-2% — far above Ticketmaster's flat ~$0.30 on
theatre). This does NOT add new shows; it produces a side-map of
  group_key -> [ {loc, city, country, url, name} ]
so build_shows.py can attach a TodayTix ticket_link to shows we ALREADY list. The link
is a clean URL; js/app.js wraps it with the affiliate code at render time (dormant until
the TodayTix Impact program is approved + its ids are in config — link still works).

Matching is CONSERVATIVE + automated (no manual review): exact normalised-title match
(group_key, after stripping 'on Broadway/West End/the musical' tails) AND the show's
city/country must match the TodayTix location. Low-confidence cases are simply not
matched (logged). Run: python scrapers/todaytix.py   Out: data/todaytix.json
"""

import json
import re
import time
import urllib.request
from pathlib import Path

# group_key + utf-8 stdout come from build_shows (importing it sets stdout; don't
# re-wrap here or the orphaned wrapper GC-closes the buffer — see china_poly.py).
from build_shows import group_key

DATA = Path(__file__).resolve().parent.parent / "data"
API = "https://api.todaytix.com/api/v2"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120 Safari/537.36")

# TodayTix location id -> the city it sells for (matched against OUR show's city,
# comma-stripped + lowercased, so "Washington" matches our "Washington, DC"). We match
# on CITY only (never country) so an SF link never lands on a Chicago show.
LOC_CITY = {
    1: "New York", 2: "London", 3: "Chicago", 4: "San Francisco",
    5: "Los Angeles", 6: "Washington", 7: "Boston", 17: "Sydney",
    18: "Melbourne", 19: "Brisbane", 93: "Perth", 95: "Adelaide",
    # 98 "Other Cities" intentionally skipped — too ambiguous to match safely.
}


def _city_key(c):
    return (c or "").split(",")[0].strip().lower()


def _get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    return json.loads(urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "ignore"))


def clean_name(name):
    """TodayTix titles carry venue/market tails — strip them so the group_key matches
    our clean title: '& Juliet on Broadway' -> '& Juliet', 'Kinky Boots The Musical'."""
    n = name or ""
    n = re.sub(r"\s*[-–]\s*(the musical|on broadway|on the west end).*$", "", n, flags=re.I)
    n = re.sub(r"\s+(on broadway|on the west end|the musical|in concert|on stage)$", "", n, flags=re.I)
    return n.strip()


def main():
    # build group_key -> {city,country} set for OUR shows, so we only keep TodayTix
    # entries we can actually attach to (and verify the location matches).
    our = json.loads((DATA / "shows.json").read_text(encoding="utf-8"))["shows"]
    our_keys = {}   # group_key -> set of comma-stripped lowercased city names
    for s in our:
        our_keys.setdefault(group_key(s["title"]), set()).add(_city_key(s.get("city")))

    mapping, total_tt, matched = {}, 0, 0
    for loc_id, city in LOC_CITY.items():
        ck = city.lower()
        offset = 0
        while True:
            url = (f"{API}/shows?fieldset=SHOW_SUMMARY&sortBy=RECENT_TRANSACTION_COUNT"
                   f"&sortOrder=DESC&location={loc_id}&context=MERCHANDISING&limit=100&offset={offset}")
            try:
                resp = _get(url)
            except Exception as e:  # noqa: BLE001
                print(f"  [loc {loc_id} offset {offset}] {e}")
                break
            rows = resp.get("data") or []
            for x in rows:
                if (x.get("category") or {}).get("name") != "Musicals":
                    continue
                total_tt += 1
                gk = group_key(clean_name(x.get("name") or x.get("displayName") or ""))
                # CONSERVATIVE: same work AND we list it in this exact city
                if not gk or gk not in our_keys or ck not in our_keys[gk]:
                    continue
                slug = x.get("slug") or x.get("customSlug")
                sid = x.get("id")
                # slug may be null — /shows/{id} 301-redirects to the canonical slug url
                tail = f"{sid}-{slug}" if slug else f"{sid}"
                url_show = f"https://www.todaytix.com/{x.get('locationSeoName')}/shows/{tail}"
                mapping.setdefault(gk, [])
                if not any(e["url"] == url_show for e in mapping[gk]):
                    mapping[gk].append({"loc": x.get("locationSeoName"), "city": city,
                                        "url": url_show, "name": x.get("name")})
                    matched += 1
            page = resp.get("pagination") or {}
            if offset + 100 >= (page.get("totalCount") or len(rows)) or not rows:
                break
            offset += 100
            time.sleep(0.15)
        time.sleep(0.1)

    out = {"meta": {"source": "todaytix.com", "tt_musicals_seen": total_tt,
                    "matched_links": matched, "matched_works": len(mapping)}, "map": mapping}
    (DATA / "todaytix.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"TodayTix musicals seen {total_tt}; matched {matched} link(s) across "
          f"{len(mapping)} work(s) -> data/todaytix.json")
    for gk, entries in sorted(mapping.items()):
        print(f"  {gk}: " + ", ".join(f"{e['loc']}" for e in entries))


if __name__ == "__main__":
    main()
