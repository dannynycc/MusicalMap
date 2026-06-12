"""Generate data/venues_catalog.json — the client-side autocomplete dictionary
for the personal "log a musical" form.

Sources:
  1. every distinct venue (with city/country/coords) in data/shows.json
  2. every distinct city and show title in shows.json
  3. a curated list of major theatres the musical dataset doesn't cover
     (Taiwan / Asia / classic houses) so e.g. typing 國家 surfaces 國家戲劇院 …

Run: python scrapers/gen_catalog.py
"""

import json
import sys
import io
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
DATA = Path(__file__).resolve().parent.parent / "data"

# Curated venues missing from the musical dataset (name, city, country, lat, lng)
CURATED = [
    # Taiwan
    ("國家戲劇院", "臺北", "Taiwan", 25.0360, 121.5168),
    ("國家音樂廳", "臺北", "Taiwan", 25.0349, 121.5167),
    ("臺北表演藝術中心", "臺北", "Taiwan", 25.0578, 121.5256),
    ("臺中國家歌劇院", "臺中", "Taiwan", 24.1631, 120.6406),
    ("衛武營國家藝術文化中心", "高雄", "Taiwan", 22.6045, 120.3349),
    ("臺北小巨蛋", "臺北", "Taiwan", 25.0515, 121.5510),
    ("臺北流行音樂中心", "臺北", "Taiwan", 25.0530, 121.5910),
    ("城市舞台", "臺北", "Taiwan", 25.0510, 121.5530),
    # Hong Kong / Singapore
    ("Hong Kong Cultural Centre", "Hong Kong", "Hong Kong", 22.2940, 114.1700),
    ("Hong Kong Academy for Performing Arts", "Hong Kong", "Hong Kong", 22.2790, 114.1720),
    ("Esplanade Theatre", "Singapore", "Singapore", 1.2897, 103.8559),
    ("Sands Theatre, Marina Bay Sands", "Singapore", "Singapore", 1.2847, 103.8590),
    # Japan extras (beyond Shiki/Takarazuka)
    ("帝国劇場", "Tokyo", "Japan", 35.6759, 139.7626),
    ("日生劇場", "Tokyo", "Japan", 35.6736, 139.7616),
    ("東急シアターオーブ", "Tokyo", "Japan", 35.6590, 139.7036),
    ("梅田芸術劇場", "Osaka", "Japan", 34.7068, 135.4985),
    # Korea extras
    ("예술의전당 (Seoul Arts Center)", "Seoul", "South Korea", 37.4786, 127.0119),
    ("세종문화회관 (Sejong Center)", "Seoul", "South Korea", 37.5725, 126.9760),
    # Classic Western houses often visited
    ("Sydney Opera House", "Sydney", "Australia", -33.8568, 151.2153),
    ("Théâtre du Châtelet", "Paris", "France", 48.8576, 2.3470),
    ("Teatro alla Scala", "Milan", "Italy", 45.4674, 9.1895),
    ("Raimund Theater", "Vienna", "Austria", 48.1969, 16.3438),
    ("Ronacher", "Vienna", "Austria", 48.2073, 16.3760),
]


def main():
    shows = json.loads((DATA / "shows.json").read_text(encoding="utf-8"))["shows"]
    venues, cities, titles = {}, set(), set()
    for s in shows:
        if s.get("venue") and isinstance(s.get("lat"), (int, float)):
            key = (s["venue"], s.get("city") or "")
            venues.setdefault(key, {
                "name": s["venue"], "city": s.get("city") or "",
                "country": s.get("country") or "", "lat": s["lat"], "lng": s["lng"],
            })
        if s.get("city"):
            cities.add((s["city"], s.get("country") or ""))
        if s.get("title"):
            titles.add(s["title"])
    for name, city, country, lat, lng in CURATED:
        venues.setdefault((name, city), {"name": name, "city": city,
                                         "country": country, "lat": lat, "lng": lng})

    out = {
        "venues": sorted(venues.values(), key=lambda v: v["name"]),
        "cities": sorted([{"city": c, "country": k} for c, k in cities], key=lambda x: x["city"]),
        "titles": sorted(titles),
    }
    (DATA / "venues_catalog.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"venues {len(out['venues'])}, cities {len(out['cities'])}, titles {len(out['titles'])}"
          f" -> data/venues_catalog.json")


if __name__ == "__main__":
    main()
