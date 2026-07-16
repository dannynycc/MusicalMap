"""Enrich venues with a Google place_id so map links open the venue's SINGLE place card
directly (?api=1&query=<name>&query_place_id=<pid>) — proven 2026-07-16 that this
resolves to the exact place card (e.g. Broadway Theatre 1681 Broadway) rather than a
results list, which plain name/coord queries cannot do for generic names.

Selection (fixed 2026-07-16 after Arena Zagreb regression — the correct venue was
Google's #2 result behind a same-named mall, and a distance-only #1 check wrongly
rejected it):
  * request up to 5 candidates (not 1) with locationBias around the venue's coords;
  * if the NEAREST candidate is <=60 m, take it — coord agreement means it's the venue
    (handles the common exact-match case, and beats a same-name POI a few hundred m away);
  * else take the nearest candidate whose NAME matches ours (distinctive Latin token or
    CJK substring overlap) within 2 km — a large distance is usually a coord / GCJ-02
    datum gap, not a wrong match, and the place_id is datum-independent;
  * else leave it unresolved (frontend falls back). This correctly recovers Arena Zagreb
    (name matches at 0 m) while rejecting Shanghai's AIA Grand Theatre (Google only
    returns People's-Square theatres 3.7 km away that don't name-match).

STORAGE: data/venue_place_ids.json (persistent, keyed by "lat,lng" 6dp), NOT the catalog
(a build artifact; gen_catalog.py merges pids in). Mirrors venue_coords.json.

COST SAFETY (user's Google free-trial credit; must never exceed the ~$300 / NT$9,422):
  * each venue attempted at most once per mode; result persisted, never blindly retried.
  * HARD CAP MAX_CALLS aborts the run — a deterministic runaway guard. Actual cost is
    read from the Cloud Billing console, never a computed estimate (observed 2026-07-16:
    ~NT$0.11/call, i.e. the first full 5.4k-venue pass drew ~NT$617 of the credit).

KEY: env GOOGLE_MAPS_KEY else scrapers/.gmaps_key (gitignored).
Test:   python -u scrapers/enrich_place_ids.py --match "Arena Zagreb"
New:    python -u scrapers/enrich_place_ids.py            # only venues not yet attempted
Refine: python -u scrapers/enrich_place_ids.py --refine   # re-do null + resolved-with-m>10
"""

import io
import json
import math
import os
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
CATALOG = DATA / "venues_catalog.json"
STORE = DATA / "venue_place_ids.json"
SEARCH = "https://places.googleapis.com/v1/places:searchText"

NEAR_M = 60          # nearest candidate within this → accept on coord agreement alone
NAME_CAP_M = 2000    # accept a name-matching candidate up to this far (coord/GCJ-02 gap)
CLOSE_KEEP_M = 10    # in --refine, resolved entries at/under this are trusted (not redone)
BIAS_M = 600.0
MAX_CALLS = 6000     # HARD runaway cap
SLEEP = 0.08

_GENERIC = {"theatre", "theater", "teatro", "theatre", "grand", "national", "royal", "state",
            "city", "new", "old", "center", "centre", "hall", "opera", "house", "arts",
            "arena", "performing", "auditorium", "stadium", "palace", "park", "the", "for",
            "de", "la", "los", "el"}
_CJK = re.compile(r"[㐀-鿿]{2,}")


def load_key():
    k = os.environ.get("GOOGLE_MAPS_KEY", "").strip()
    if k:
        return k
    f = ROOT / "scrapers" / ".gmaps_key"
    if f.exists():
        return f.read_text(encoding="utf-8").strip()
    sys.exit("No API key: set GOOGLE_MAPS_KEY or write scrapers/.gmaps_key")


def dist_m(a, b, c, d):
    R = 6371008.8
    p = math.pi / 180
    h = 0.5 - math.cos((c - a) * p) / 2 + math.cos(a * p) * math.cos(c * p) * (1 - math.cos((d - b) * p)) / 2
    return 2 * R * math.asin(math.sqrt(h))


def ckey(lat, lng):
    return f"{round(float(lat), 6)},{round(float(lng), 6)}"


def _latin_toks(s):
    return [w for w in re.sub(r"[^a-z0-9 ]", " ", (s or "").lower()).split()
            if len(w) > 2 and w not in _GENERIC]


def name_match(venue, got):
    """True if `got` (Google's name) shares a distinctive Latin token OR a CJK substring
    with our venue name — tolerant of bilingual names and hall/type suffixes."""
    gt = set(_latin_toks(got))
    if gt and any(w in gt for w in _latin_toks(venue)):
        return True
    for run in _CJK.findall(venue or ""):
        for L in range(len(run), 1, -1):
            for i in range(len(run) - L + 1):
                if run[i:i + L] in (got or ""):
                    return True
    return False


def candidates(name, lat, lng, key):
    """Up to 5 (distance, name_match, pid, google_name) | ('DENIED', msg) | []."""
    payload = {"textQuery": name, "maxResultCount": 5,
               "locationBias": {"circle": {"center": {"latitude": lat, "longitude": lng}, "radius": BIAS_M}}}
    req = urllib.request.Request(SEARCH, data=json.dumps(payload).encode(), method="POST", headers={
        "Content-Type": "application/json", "X-Goog-Api-Key": key,
        "X-Goog-FieldMask": "places.id,places.location,places.displayName"})
    try:
        r = json.loads(urllib.request.urlopen(req, timeout=25).read())
    except urllib.error.HTTPError as e:
        return ("DENIED", e.read().decode("utf-8", "ignore")[:200]) if e.code in (400, 403) else []
    except Exception:
        return []
    out = []
    for p in r.get("places") or []:
        loc = p.get("location") or {}
        if "latitude" not in loc or not p.get("id"):
            continue
        nm = (p.get("displayName") or {}).get("text", "")
        out.append((dist_m(lat, lng, loc["latitude"], loc["longitude"]), name_match(name, nm), p["id"], nm))
    return out


def pick(name, lat, lng, key):
    """Return {'pid','name','m'} | ('DENIED',msg) | None."""
    cands = candidates(name, lat, lng, key)
    if isinstance(cands, tuple) and cands[0] == "DENIED":
        return cands
    if not cands:
        return None
    near = [c for c in cands if c[0] <= NEAR_M]
    chosen = min(near) if near else None          # coord agreement wins (incl. correct #2/#3)
    if chosen is None:
        named = [c for c in cands if c[1] and c[0] <= NAME_CAP_M]
        chosen = min(named) if named else None    # far but name matches → real venue (datum gap)
    if chosen is None:
        return None
    return {"pid": chosen[2], "name": chosen[3], "m": round(chosen[0], 1)}


def main():
    key = load_key()
    refine = "--refine" in sys.argv
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    match = sys.argv[sys.argv.index("--match") + 1].lower() if "--match" in sys.argv else None

    cat = json.loads(CATALOG.read_text(encoding="utf-8"))
    venues = cat["venues"]
    store = json.loads(STORE.read_text(encoding="utf-8")) if STORE.exists() else {}

    todo = []
    for v in venues:
        if v.get("lat") is None or v.get("lng") is None:
            continue
        k = ckey(v["lat"], v["lng"])
        cur = store.get(k, "MISSING")
        if refine:
            # re-do the null ones and any resolved farther than CLOSE_KEEP_M; trust the rest
            if cur != "MISSING" and cur is not None and cur.get("m", 999) <= CLOSE_KEEP_M:
                continue
        else:
            if cur != "MISSING":          # already attempted
                continue
        if match and match not in (v.get("name", "").lower()):
            continue
        todo.append((k, v))
    if limit:
        todo = todo[:limit]

    print(f"venues={len(venues)} store={len(store)} to_process={len(todo)} "
          f"mode={'refine' if refine else 'new'} (hard cap {MAX_CALLS})", flush=True)
    if not todo:
        print("nothing to do.", flush=True)
        return

    calls = resolved = none = 0
    recovered = 0
    for i, (k, v) in enumerate(todo, 1):
        if calls >= MAX_CALLS:
            print(f"!! HARD CAP {MAX_CALLS} reached — aborting.", flush=True)
            break
        was = store.get(k)
        res = pick(v["name"], v["lat"], v["lng"], key)
        calls += 1
        time.sleep(SLEEP)
        if isinstance(res, tuple) and res[0] == "DENIED":
            print(f"!! DENIED (stopping): {res[1][:160]}", flush=True)
            break
        store[k] = res
        if res:
            resolved += 1
            if not was:                 # was null/absent, now has a pid
                recovered += 1
        else:
            none += 1
        if i % 25 == 0:
            STORE.write_text(json.dumps(store, ensure_ascii=False, indent=0), encoding="utf-8")
            print(f"  [{i}/{len(todo)}] calls={calls} resolved={resolved} none={none} recovered={recovered}", flush=True)

    STORE.write_text(json.dumps(store, ensure_ascii=False, indent=0), encoding="utf-8")
    tot = sum(1 for x in store.values() if x)
    print(f"\nDONE  calls={calls}  resolved-this-run={resolved}  none={none}  newly-recovered={recovered}", flush=True)
    print(f"  store total resolved: {tot}/{len(store)} -> {STORE}", flush=True)
    print("  >> COST: read the ACTUAL amount from the Cloud Billing console; never trust a computed guess.", flush=True)


if __name__ == "__main__":
    main()
