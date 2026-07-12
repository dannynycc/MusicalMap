"""Authoritative venue geocoding via Google — building-level coords (target <=30m).

Primary:  Places API (New) Text Search  (places.googleapis.com/v1/places:searchText)
          — POI/establishment point, building-level, 5,000 free calls/month.
Fallback: Geocoding API  (maps.googleapis.com/maps/api/geocode/json)
          — used per-venue if Places (New) is disabled or returns nothing.
          10,000 free calls/month. location_type recorded for transparency.

547 venues is far below every free cap, so a one-time run costs $0.

Results whose returned name doesn't match the venue are NOT trusted — listed under
`needs_review` for manual satellite check, never silently accepted.

KEY (never committed): env GOOGLE_MAPS_KEY, else scrapers/.gmaps_key (both gitignored).
Run: python -u scrapers/geocode_google.py
Out: data/venue_coords.json (authoritative) + data/_geo_google_report.json
"""

import json
import math
import os
import re
import sys
import io
import time
import urllib.parse
import urllib.request
import urllib.error
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
PLACES_NEW = "https://places.googleapis.com/v1/places:searchText"
GEOCODE = "https://maps.googleapis.com/maps/api/geocode/json"
NEAR_M = 30


def load_key():
    k = os.environ.get("GOOGLE_MAPS_KEY", "").strip()
    if k:
        return k
    f = ROOT / "scrapers" / ".gmaps_key"
    if f.exists():
        return f.read_text(encoding="utf-8").strip()
    sys.exit("No API key: set GOOGLE_MAPS_KEY or write scrapers/.gmaps_key")


def places_new(query, key, language=None):
    """Returns (lat, lng, name, addr, 'places-new') | ('DENIED', msg) | None.
    `language` (e.g. 'en') asks Google for the place name in that language."""
    payload = {"textQuery": query, "maxResultCount": 1}
    if language:
        payload["languageCode"] = language
    body = json.dumps(payload).encode()
    req = urllib.request.Request(PLACES_NEW, data=body, method="POST", headers={
        "Content-Type": "application/json", "X-Goog-Api-Key": key,
        "X-Goog-FieldMask": "places.location,places.displayName,places.formattedAddress"})
    try:
        r = json.loads(urllib.request.urlopen(req, timeout=25).read())
    except urllib.error.HTTPError as e:
        msg = e.read().decode("utf-8", "ignore")[:200]
        return ("DENIED", msg) if e.code in (403, 400) else None
    except Exception:
        return None
    places = r.get("places") or []
    if not places:
        return None
    p = places[0]
    loc = p.get("location") or {}
    if "latitude" not in loc:
        return None
    return (loc["latitude"], loc["longitude"],
            (p.get("displayName") or {}).get("text", ""), p.get("formattedAddress", ""), "places-new")


def geocode_api(query, key):
    """Returns (lat, lng, name, addr+loctype, 'geocode') | ('DENIED', msg) | None."""
    qs = urllib.parse.urlencode({"address": query, "key": key})
    try:
        r = json.loads(urllib.request.urlopen(GEOCODE + "?" + qs, timeout=25).read())
    except Exception:
        return None
    st = r.get("status")
    if st == "REQUEST_DENIED":
        return ("DENIED", r.get("error_message", ""))
    res = r.get("results") or []
    if not res:
        return None
    g = res[0]
    loc = g["geometry"]["location"]
    lt = g["geometry"].get("location_type", "")
    return (loc["lat"], loc["lng"], g.get("formatted_address", ""),
            f"{g.get('formatted_address','')} [{lt}]", f"geocode:{lt}")


def dist_m(a, b, c, d):
    R = 6371008.8; p = math.pi / 180
    h = 0.5 - math.cos((c - a) * p) / 2 + math.cos(a * p) * math.cos(c * p) * (1 - math.cos((d - b) * p)) / 2
    return 2 * R * math.asin(math.sqrt(h))


def norm(s):
    return re.sub(r"[^a-z0-9 ]", " ", (s or "").lower())


def name_ok(venue, got):
    vt = [w for w in norm(venue).split() if len(w) > 3 and w not in
          ("theatre", "theater", "centre", "center", "hall", "arts", "opera", "house")]
    gn = norm(got)
    if not vt:
        return norm(venue).strip() in gn
    return sum(1 for w in vt if w in gn) >= max(1, len(vt) // 2)


def vkey(venue, city):
    return f"{(venue or '').strip().lower()}|{(city or '').lower().split(',')[0].strip()}"


def main():
    key = load_key()
    force = "--all" in sys.argv          # re-geocode everything (default: only new venues)
    coords_path = DATA / "venue_coords.json"
    existing = json.loads(coords_path.read_text(encoding="utf-8")) if coords_path.exists() else {}
    have = {k for k in existing if not k.startswith("_")}

    shows = json.loads((DATA / "shows.json").read_text(encoding="utf-8"))["shows"]

    # 中國大陸場館:Google 大陸資料=GCJ 偏移+同名連鎖(保利/聚橙)極易誤配——2026-07-10
    # 實案:「衢州保利大剧院大剧场」被 Google 配到上海保利(嘉定)、name_ok 因同含「保利
    # 大剧院」而放行,錯 57km。cn_venues.json(專用管線 Google+GCJ→WGS84)才是大陸權威;
    # 有權威值(子字串比對)就直接採用,不問 Google。
    # cn_venues 的 native 簡繁混雜(上海大劇院/合肥大剧院並存),來源資料(大麥等)是簡體——
    # 子字串比對必須先把兩邊摺疊到同一字系,否則「上海大劇院」比不中「上海大剧院-大剧场」
    # (2026-07-12 實測:44 個缺座標場館,原樣中 11、轉繁中另 11、兩批零重疊)。
    # 統一摺疊成簡體(t2s 對簡體是恆等);無 opencc 時退回原樣比對(=舊行為)。
    try:
        from opencc import OpenCC
        _fold = OpenCC("t2s").convert
    except ImportError:
        _fold = lambda s: s
    cn_auth = {}
    cn_path = DATA / "cn_venues.json"
    if cn_path.exists():
        _cn = json.loads(cn_path.read_text(encoding="utf-8"))
        for x in (_cn if isinstance(_cn, list) else _cn.get("venues", [])):
            if x.get("lat"):
                cn_auth[_fold(x["native"])] = (x["lat"], x["lng"])

    def cn_authority(venue):
        v = _fold(venue)
        for an, co in cn_auth.items():
            if len(an) >= 5 and (an in v or v in an):
                return co
        return None

    venues = {}
    pre_resolved = {}
    for s in shows:
        v, c, co = s.get("venue"), s.get("city"), s.get("country")
        if v and (v, c) not in venues and (v, c) not in pre_resolved:
            if force or vkey(v, c) not in have:      # incremental: skip already-known venues
                if co == "China":
                    a = cn_authority(v)
                    if a:
                        pre_resolved[(v, c)] = a
                        continue
                venues[(v, c)] = (s.get("lat"), s.get("lng"), co)
    if pre_resolved:
        print(f"  {len(pre_resolved)} China venue(s) resolved from cn_venues authority (Google skipped)", flush=True)
    if not venues and not pre_resolved:
        print("No new venues to geocode (all present in venue_coords.json). Use --all to force.", flush=True)
        return

    # pick the engine that the key actually has enabled (one probe call)
    probe_q = "Apollo Victoria Theatre, London, UK"
    engine = places_new(probe_q, key)
    if isinstance(engine, tuple) and engine[0] == "DENIED":
        print(f"  Places (New) unavailable ({engine[1][:80]}…) → trying Geocoding API", flush=True)
        g = geocode_api(probe_q, key)
        if isinstance(g, tuple) and g[0] == "DENIED":
            sys.exit(f"Both APIs denied. Enable 'Places API (New)' or 'Geocoding API' + billing. ({g[1][:120]})")
        lookup = geocode_api
        print("  engine = Geocoding API", flush=True)
    else:
        lookup = places_new
        print("  engine = Places API (New)", flush=True)

    total = len(venues)
    print(f"Google-geocoding {total} venues (target <= {NEAR_M} m)", flush=True)
    coords, moved, needs_review = {}, [], []
    for i, ((v, c), (la, ln, co)) in enumerate(sorted(venues.items()), 1):
        res = lookup(f"{v}, {c}, {co}", key)
        time.sleep(0.06)
        if isinstance(res, tuple) and res[0] == "DENIED":
            print(f"  DENIED mid-run: {res[1][:100]}", flush=True); break
        if not res:
            needs_review.append({"venue": v, "city": c, "country": co, "reason": "no-result", "stored": [la, ln]})
            print(f"  [{i}/{total}] ? no-result  {v} ({c}, {co})", flush=True); continue
        glat, glng, gname, gaddr, gsrc = round(res[0], 6), round(res[1], 6), res[2], res[3], res[4]
        if not name_ok(v, gname):
            needs_review.append({"venue": v, "city": c, "country": co, "reason": "name-mismatch",
                                 "google_name": gname, "google_addr": gaddr,
                                 "google_coord": [glat, glng], "stored": [la, ln]})
            print(f"  [{i}/{total}] ⚠ name≠ '{gname}'  for  {v} ({c})", flush=True); continue
        coords[vkey(v, c)] = [glat, glng]
        if isinstance(la, (int, float)) and (la or ln):
            d = dist_m(la, ln, glat, glng)
            if d > NEAR_M:
                moved.append({"venue": v, "city": c, "country": co, "m": round(d),
                              "from": [la, ln], "to": [glat, glng], "src": gsrc, "google": gaddr})
        if i % 50 == 0:
            print(f"  [{i}/{total}] … ok {len(coords)}, review {len(needs_review)}", flush=True)

    # merge: keep all previously-verified venues, add/refresh the ones we just did
    merged = {k: v for k, v in existing.items() if not k.startswith("_")}
    merged.update(coords)
    for (v, c), (la, ln) in pre_resolved.items():   # 大陸權威值直入(見上)
        merged[vkey(v, c)] = [la, ln]
    out = {"_comment": "Authoritative venue coords (Google, building-level ~<=30m), keyed by "
                       "'venue|city'. Applied in build_shows.py. Regenerate: scrapers/geocode_google.py "
                       "(incremental; --all to re-do every venue)."}
    out.update(dict(sorted(merged.items())))
    (DATA / "venue_coords.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    (DATA / "_geo_google_report.json").write_text(json.dumps(
        {"checked": total, "geocoded": len(coords),
         "moved_over_30m_vs_source": sorted(moved, key=lambda r: -r["m"]),
         "needs_review": needs_review}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nDONE: {total} venues | geocoded {len(coords)} | "
          f"moved >{NEAR_M}m vs source: {len(moved)} | needs_review: {len(needs_review)}", flush=True)
    print("  -> data/venue_coords.json + data/_geo_google_report.json", flush=True)


if __name__ == "__main__":
    main()
