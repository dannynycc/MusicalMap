"""One-off global venue verification (ex-China) via Google reverse-geocoding.

The catalog's coords are mostly correct, but the discovery scrapers sometimes file a
venue under the WRONG city/country (e.g. "Sydney Opera House" landed under Reading/UK;
several UK Newcastle venues under Australia). Forward re-geocoding can't catch that —
the coord is right, the label is wrong. So we REVERSE-geocode each venue's stored
coordinate (lat,lng → Google's country + locality) and flag every venue whose true
country differs from its stored label, plus any coord that reverse-geocodes to nothing
(a genuinely bad point).

Reverse geocoding = Geocoding API ($5/1000) → ~$24 for ~4,856 venues. Results cache to
data/_geo_rev.json (gitignored) so re-runs are free/resumable.

Output: data/_geo_rev.json (cache) + data/_geo_flags.json (mismatches to fix).
Run: python scrapers/verify_geo.py
"""

import json
import sys
import io
import time
import urllib.request
import urllib.parse
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
GEOCODE = "https://maps.googleapis.com/maps/api/geocode/json"


def load_key():
    f = ROOT / "scrapers" / ".gmaps_key"
    return f.read_text(encoding="utf-8").strip()


# Google country names → our catalog's country labels (only where they differ)
COUNTRY_ALIAS = {
    "United States": "USA", "United Kingdom": "UK", "Czechia": "Czech Republic",
    "South Korea": "South Korea", "Hong Kong": "Hong Kong",
}


def rev(lat, lng, key):
    qs = urllib.parse.urlencode({"latlng": f"{lat},{lng}", "key": key, "language": "en",
                                 "result_type": "country|locality|administrative_area_level_1"})
    try:
        r = json.loads(urllib.request.urlopen(GEOCODE + "?" + qs, timeout=20).read())
    except Exception as e:  # noqa: BLE001
        return {"status": "ERR", "err": str(e)[:60]}
    st = r.get("status")
    if st != "OK":
        return {"status": st}
    country = city = None
    for comp in r["results"][0].get("address_components", []):
        t = comp.get("types", [])
        if "country" in t:
            country = comp["long_name"]
        if "locality" in t and not city:
            city = comp["long_name"]
    return {"status": "OK", "country": country, "city": city}


def main():
    key = load_key()
    ven = json.loads((DATA / "venues_catalog.json").read_text(encoding="utf-8"))
    ven = ven.get("venues", ven) if isinstance(ven, dict) else ven
    non = [v for v in ven if v.get("country") not in ("China", "中國", "PRC")
           and isinstance(v.get("lat"), (int, float))]

    cache_path = DATA / "_geo_rev.json"
    cache = json.loads(cache_path.read_text(encoding="utf-8")) if cache_path.exists() else {}
    print(f"{len(non)} non-China venues; {len(cache)} already cached")

    flags, n_new = [], 0
    for i, v in enumerate(non):
        k = f"{round(v['lat'], 5)},{round(v['lng'], 5)}"
        if k not in cache:
            cache[k] = rev(v["lat"], v["lng"], key)
            n_new += 1
            time.sleep(0.05)
            if n_new % 200 == 0:
                cache_path.write_text(json.dumps(cache, ensure_ascii=False), encoding="utf-8")
                print(f"  …{n_new} new geocoded ({i + 1}/{len(non)})")
        g = cache[k]
        if g.get("status") != "OK":
            flags.append({"name": v.get("name"), "city": v.get("city"), "stored_country": v.get("country"),
                          "lat": v["lat"], "lng": v["lng"], "issue": "no-reverse-geocode:" + g.get("status", "?")})
            continue
        gc = COUNTRY_ALIAS.get(g.get("country"), g.get("country"))
        if gc and gc != v.get("country"):
            flags.append({"name": v.get("name"), "city": v.get("city"), "stored_country": v.get("country"),
                          "true_country": gc, "true_city": g.get("city"),
                          "lat": v["lat"], "lng": v["lng"], "issue": "country-mismatch"})

    cache_path.write_text(json.dumps(cache, ensure_ascii=False), encoding="utf-8")
    (DATA / "_geo_flags.json").write_text(json.dumps(flags, ensure_ascii=False, indent=2), encoding="utf-8")
    from collections import Counter
    print(f"\nnew geocodes this run: {n_new} | flags: {len(flags)}")
    print("flag types:", dict(Counter(f["issue"].split(":")[0] for f in flags)))
    print("country mismatches by stored→true:")
    pairs = Counter((f["stored_country"], f.get("true_country")) for f in flags if f["issue"] == "country-mismatch")
    for (s, t), n in pairs.most_common(20):
        print(f"  {s} → {t}: {n}")


if __name__ == "__main__":
    main()
