"""Geo sanity audit — flag venues whose coordinates fall outside their stated
country's bounding box (catches gross geocoding errors: wrong country/continent,
swapped lat/lng, landmark-instead-of-venue matches that landed far away).

Run: python scrapers/audit_geo.py
Offline (no network) — pure bounding-box check over data/shows.json.
"""

import json
import re
import sys
import io
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
DATA = Path(__file__).resolve().parent.parent / "data"

# (lat_min, lat_max, lng_min, lng_max) — generous national bounding boxes,
# incl. outlying states/territories (e.g. USA covers Hawaii + Alaska).
BBOX = {
    "USA": (18.0, 72.0, -180.0, -66.0),
    "UK": (49.5, 61.0, -8.8, 2.1),
    "Ireland": (51.3, 55.5, -10.7, -5.9),
    "Spain": (27.5, 43.9, -18.3, 4.4),       # incl. Canary Is.
    "South Korea": (33.0, 38.7, 124.5, 131.0),
    "Japan": (24.0, 45.6, 122.9, 146.0),
    "Australia": (-43.7, -10.0, 112.9, 153.7),
    "Canada": (41.6, 83.2, -141.1, -52.5),
    "Belgium": (49.4, 51.6, 2.5, 6.5),
    "Germany": (47.2, 55.1, 5.8, 15.1),
    "New Zealand": (-47.5, -34.0, 166.3, 178.7),
    "Denmark": (54.5, 57.8, 8.0, 15.2),
    "Italy": (35.4, 47.1, 6.6, 18.6),
    "France": (41.3, 51.2, -5.2, 9.7),
    "Mexico": (14.3, 32.8, -118.5, -86.5),
    "Sweden": (55.1, 69.1, 10.9, 24.2),
    "Norway": (57.9, 71.4, 4.5, 31.2),
    "Austria": (46.3, 49.1, 9.5, 17.2),
    "Netherlands": (50.7, 53.7, 3.3, 7.3),
    "China": (18.1, 53.6, 73.4, 135.1),
    "Czech Republic": (48.5, 51.1, 12.0, 18.9),
    "UAE": (22.6, 26.1, 51.5, 56.4),
    "Switzerland": (45.8, 47.8, 5.9, 10.5),
    "Hong Kong": (22.1, 22.6, 113.8, 114.5),
    "Singapore": (1.1, 1.5, 103.6, 104.1),
    "Taiwan": (21.9, 25.3, 119.3, 122.1),
}


def main():
    shows = json.loads((DATA / "shows.json").read_text(encoding="utf-8"))["shows"]
    no_bbox = set()
    bad = {}     # (venue, city, country) -> (lat, lng)
    checked = 0
    for s in shows:
        lat, lng = s.get("lat"), s.get("lng")
        country = s.get("country")
        if not isinstance(lat, (int, float)) or not isinstance(lng, (int, float)):
            continue
        box = BBOX.get(country)
        if not box:
            no_bbox.add(country)
            continue
        checked += 1
        la0, la1, ln0, ln1 = box
        if not (la0 <= lat <= la1 and ln0 <= lng <= ln1):
            bad[(s.get("venue"), s.get("city"), country)] = (lat, lng)

    print(f"checked {checked} located shows against {len(BBOX)} country boxes")
    if no_bbox:
        print(f"  (no bbox for: {', '.join(sorted(x for x in no_bbox if x))})")
    print(f"OUT-OF-COUNTRY venues: {len(bad)}")
    for (v, c, co), (la, ln) in sorted(bad.items(), key=lambda x: x[0][2] or ""):
        print(f"::warning::geo out-of-country: {co} {c or '?'} {v or '?'} -> {la}, {ln}")
    if not bad:
        print("  ✓ all located shows fall inside their country's bounding box")
    audit_venue_coords()


def audit_venue_coords():
    """venue_coords.json(場館級座標修正表)自體體檢。

    2026-07-10 實案:南昌/啟東/衡陽保利被批次貼上「上海保利(嘉定)」座標(錯 616-989km)、
    蘇州/衢州保利貼成常熟保利——修正表本身錯會污染該場館所有戲,而國界框抓不到
    (同在中國境內)。兩個偵測:
    1. 不同城市鍵、不同場館名共用完全相同座標(複製貼上指紋);同館多廳/母城別名放行。
    2. 與 cn_venues.json(Google 實測權威值)差 >20km 的中國場館。
    """
    vc_path = DATA / "venue_coords.json"
    if not vc_path.exists():
        return
    v = {k: val for k, val in json.loads(vc_path.read_text(encoding="utf-8")).items()
         if not k.startswith("_") and isinstance(val, list) and len(val) == 2}
    warn = 0

    by_coord = {}
    for k, val in v.items():
        by_coord.setdefault((round(val[0], 5), round(val[1], 5)), []).append(k)
    for co, ks in by_coord.items():
        if len(ks) < 2:
            continue
        cities = {k.split("|")[1] for k in ks}
        if len(cities) < 2:
            continue
        # 同館多廳/兩種鍵寫法(「臺中國家歌劇院」vs「…大劇院」、「regent theatre」vs
        # 「regent theatre, stoke」)→ 最短名是其他名的字首=同一館,放行
        names = sorted({re.sub(r"^the\s+", "", re.sub(r"[,\s]+", " ", k.split("|")[0]).strip())
                        for k in ks}, key=len)
        if all(n.startswith(names[0][:max(6, len(names[0]) // 2)]) for n in names[1:]):
            continue
        warn += 1
        print(f"::warning::venue_coords 跨城市同座標(疑複製貼上): {ks} -> {co}")

    cn_path = DATA / "cn_venues.json"
    if cn_path.exists():
        import math
        cn = json.loads(cn_path.read_text(encoding="utf-8"))
        arr = cn if isinstance(cn, list) else cn.get("venues", [])
        auth = {x["native"].lower(): (x["lat"], x["lng"]) for x in arr if x.get("lat")}
        for k, val in v.items():
            name = k.split("|")[0]
            # 子字串比對:表鍵常帶廳名尾綴(「衢州保利大剧院大剧场」vs 權威「衢州保利大剧院」),
            # 精確比對會漏(2026-07-10 Google 誤配保利連鎖實案就是這樣漏掉的)
            a = auth.get(name) or next(
                (co for an, co in auth.items() if len(an) >= 5 and (an in name or name in an)), None)
            if a:
                d = math.hypot((val[0] - a[0]) * 111,
                               (val[1] - a[1]) * 111 * math.cos(math.radians(a[0])))
                if d > 20:
                    warn += 1
                    print(f"::warning::venue_coords vs cn_venues 差 {round(d)}km: {k} 表={val} 權威={list(a)}")
    print(f"venue_coords audit: {len(v)} 條,{'全過 ✓' if warn == 0 else f'{warn} 項告警'}")


if __name__ == "__main__":
    main()
