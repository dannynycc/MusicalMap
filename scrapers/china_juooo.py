"""China nationwide musicals ????蝵?(Juooo, juooo.com).

Juooo is a major Mainland musical producer/ticketer. Its H5 backend exposes OPEN
JSON APIs (no captcha, no signature on the show-list path ??unlike Damai/Maoyan
which are BaXia-walled). Reverse-engineered from the m.juooo.com bundle:

  city list : POST https://api.juooo.com/city/city/getCityList        -> all cities
  show list : POST https://gw.juooo.com/gw/show/showSearch            (form-urlencoded)
              body {cate_parent_id:79, city_id, page, pageSize}  ->  result.list[]
              (cate_parent_id 79 = ?喃??? city_id from the city list ??the list is
              per-city, so we sweep EVERY city so any city's musicals get picked up)
  coords    : POST https://gw.juooo.com/gw/show/showDetail {show_id}
              -> result.show.venue.coordinate "lng,lat" (GCJ-02) -> WGS-84 here

All endpoints carry ?version=...&referer=1 and header JUOOO-SESSIONID (may be empty).
Coordinates come straight from Juooo (GCJ-02) and are converted to WGS-84 for the
OSM basemap ??so this scraper is self-geocoding (no cn_venues.json dependency). A
show whose detail yields no coordinate is skipped (never placed at a guess).

Work-origin tagging is decided in build_shows.py (registry ??else China=銝剖??).

Output: data/china_juooo.json   Run: python scrapers/china_juooo.py
"""

import io
import json
import math
import re
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

DATA = Path(__file__).resolve().parent.parent / "data"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120 Safari/537.36")
HDR = {"User-Agent": UA, "Referer": "https://m.juooo.com/", "Origin": "https://m.juooo.com",
       "JUOOO-SESSIONID": "", "Content-Type": "application/x-www-form-urlencoded"}
QS = "?version=6.3.25&referer=1"
MUSICAL_CATE_ID = 79          # ?喃???(cate_parent_id), confirmed via /gw/show/showCategory

# ---- GCJ-02 -> WGS-84 (Juooo, like all Chinese apps, serves GCJ-02 coords) ----
_A, _EE = 6378245.0, 0.00669342162296594323
def _tf_lat(x, y):
    r = -100 + 2*x + 3*y + 0.2*y*y + 0.1*x*y + 0.2*math.sqrt(abs(x))
    r += (20*math.sin(6*x*math.pi) + 20*math.sin(2*x*math.pi)) * 2/3
    r += (20*math.sin(y*math.pi) + 40*math.sin(y/3*math.pi)) * 2/3
    r += (160*math.sin(y/12*math.pi) + 320*math.sin(y*math.pi/30)) * 2/3
    return r
def _tf_lng(x, y):
    r = 300 + x + 2*y + 0.1*x*x + 0.1*x*y + 0.1*math.sqrt(abs(x))
    r += (20*math.sin(6*x*math.pi) + 20*math.sin(2*x*math.pi)) * 2/3
    r += (20*math.sin(x*math.pi) + 40*math.sin(x/3*math.pi)) * 2/3
    r += (150*math.sin(x/12*math.pi) + 300*math.sin(x/30*math.pi)) * 2/3
    return r
def gcj02_to_wgs84(lat, lng):
    if not (73.66 < lng < 135.05 and 3.86 < lat < 53.55):
        return lat, lng
    dlat = _tf_lat(lng - 105.0, lat - 35.0)
    dlng = _tf_lng(lng - 105.0, lat - 35.0)
    rad = lat / 180.0 * math.pi
    magic = 1 - _EE * math.sin(rad) ** 2
    sq = math.sqrt(magic)
    dlat = (dlat * 180.0) / ((_A * (1 - _EE)) / (magic * sq) * math.pi)
    dlng = (dlng * 180.0) / (_A / sq * math.cos(rad) * math.pi)
    return lat - dlat, lng - dlng

# English names for the cities Juooo serves (fallback: keep the Chinese name).
CITY_EN = {
    "?漪": "Beijing", "銝絲": "Shanghai", "撟踹?": "Guangzhou", "瘛勗": "Shenzhen",
    "憭拇揖": "Tianjin", "??": "Chongqing", "甇行?": "Wuhan", "?漪": "Nanjing",
    "?剖?": "Hangzhou", "??": "Suzhou", "?": "Chengdu", "镼踹?": "Xi'an",
    "瘝": "Shenyang", "??皛?: "Harbin", "??": "Qingdao", "瘚?": "Jinan",
    "??": "Zhengzhou", "?踵?": "Changsha", "??": "Nanchang", "?": "Hefei",
    "蝳?": "Fuzhou", "?阡": "Xiamen", "憭芸?": "Taiyuan", "瘚瑕": "Haikou",
    "??": "Nanning", "?嗅?": "Yinchuan", "?": "Wuxi", "摰郭": "Ningbo",
    "撣詨?": "Changzhou", "銝?": "Dongguan", "?絲": "Zhuhai", "雿控": "Foshan",
    "??": "Kunming", "韐菟": "Guiyang", "憭扯?": "Dalian", "?踵": "Changchun",
}


def _post(host, path, body):
    req = urllib.request.Request(f"https://{host}{path}{QS}",
                                 data=urllib.parse.urlencode(body).encode(), headers=HDR)
    raw = urllib.request.urlopen(req, timeout=30).read()
    return json.loads(raw.decode("utf-8", "ignore"))


def city_list():
    """Flatten /city/city/getCityList (grouped by letter/province) to [(id, name)]."""
    data = _post("api.juooo.com", "/city/city/getCityList", {}).get("data", {})
    out = []
    def walk(x):
        if isinstance(x, dict):
            if "id" in x and "name" in x:
                out.append((x["id"], x["name"]))
            for v in x.values():
                walk(v)
        elif isinstance(x, list):
            for v in x:
                walk(v)
    walk(data.get("city_list", data))
    # de-dup, keep first occurrence
    return list(dict.fromkeys(out))


def clean_title(name):
    """'瘜祗???喃??扼滯???? / '?臬?撘???銵銋?函??箄??? -> the ?艾?core,
    else strip a leading 'X?喃??? genre prefix; drop trailing 銝剜???撌⊥?/-??蝡?"""
    m = re.search(r"??[^?+)??, name or "")
    t = m.group(1) if m else re.sub(r"^.*??訥銋?]??, "", name or "")
    t = re.sub(r"[嚗?][^嚗?)嚗*[)嚗", "", t)
    t = re.sub(r"(銝剜??銝剜?|撌⊥???|-\s*\w+?蝡憭批??*|??撘?*)$", "", t).strip()
    return t or (name or "").strip()


def iso(ts):
    try:
        ts = int(ts)
        if ts <= 0:
            return None
        return datetime.fromtimestamp(ts, tz=timezone.utc).astimezone().strftime("%Y-%m-%d")
    except (TypeError, ValueError):
        return None


def show_detail(show_id):
    """showDetail -> (wgs_lat, wgs_lng, venue_name, schedular_id) or (None, ??.
    Coordinate is GCJ-02 'lng,lat'; schedular_id (first session) builds the ticket URL
    m.juooo.com/ticket/{schedular_id} ??the show_id alone is NOT the page id."""
    try:
        resp = _post("gw.juooo.com", "/gw/show/showDetail", {"show_id": show_id})
        v = (resp.get("data", {}).get("result", {}) or {}).get("show", {}).get("venue", {}) or {}
        coord = v.get("coordinate") or ""
        if "," not in coord:
            return None, None, None, None
        lng, lat = (float(x) for x in coord.split(",")[:2])
        wlat, wlng = gcj02_to_wgs84(lat, lng)
        m = re.search(r'"schedular_id"\s*:\s*(\d+)', json.dumps(resp, ensure_ascii=False))
        return round(wlat, 6), round(wlng, 6), v.get("venue_name"), (m.group(1) if m else None)
    except Exception:  # noqa: BLE001 ??one bad detail must not kill the sweep
        return None, None, None, None


def main():
    cities = city_list()
    print(f"{len(cities)} cities to sweep for ?喃???)
    found = {}            # show_id -> showSearch record (de-duped across cities)
    for cid, _cn in cities:
        page = 1
        while True:
            try:
                res = _post("gw.juooo.com", "/gw/show/showSearch",
                            {"cate_parent_id": MUSICAL_CATE_ID, "city_id": cid,
                             "page": page, "pageSize": 50}).get("data", {}).get("result", {})
            except Exception:  # noqa: BLE001
                break
            if not isinstance(res, dict):   # some cities return result:[] (no musicals) ??skip
                break
            lst = res.get("list") or []
            for s in lst:
                found.setdefault(s["show_id"], s)
            total = res.get("total") or 0
            if page * 50 >= total or not lst:
                break
            page += 1
            time.sleep(0.1)
        time.sleep(0.06)
    print(f"{len(found)} unique musical(s) across all cities")

    shows, skipped = {}, []
    for sid, s in found.items():
        title = clean_title(s.get("show_name"))
        lat, lng, vname, sched = show_detail(sid)
        time.sleep(0.1)
        if lat is None:
            skipped.append((s.get("city_name"), title))
            continue
        city_cn = s.get("city_name") or ""
        # Real Juooo ticket page is m.juooo.com/ticket/{schedular_id}; fall back to the
        # project route by show_id if a session id wasn't found.
        ticket = (f"https://m.juooo.com/ticket/{sched}" if sched
                  else f"https://m.juooo.com/next/project/detail/{sid}")
        # Offer BOTH the Juooo page (works in browser) and a Damai search (China's main
        # ticketing site ??many buyers prefer it). 憭折漸 by title, same as the Poly source.
        damai = "https://search.damai.cn/search.htm?keyword=" + urllib.parse.quote(title)
        shows[f"juooo-{sid}"] = {
            "id": f"juooo-{sid}", "title": title, "type": "limited",
            "venue": vname or s.get("venue_name") or "", "city": CITY_EN.get(city_cn, city_cn), "city_cn": city_cn or None,
            "country": "China", "lat": lat, "lng": lng,
            "start_date": iso(s.get("show_start_time")), "end_date": iso(s.get("show_end_time")),
            "ticket_url": ticket,
            "ticket_links": [
                {"label": "??", "url": ticket, "kind": "ticketing"},
                {"label": "憭折漸", "url": damai, "kind": "ticketing"},
            ],
            "image": s.get("pic") or None,
            "tour_name": None, "verified": True, "source": "juooo.com",
        }
        print(f"  {title[:20]:22s} @ {(vname or '')[:18]:20s} {shows[f'juooo-{sid}']['city']:10s} "
              f"{shows[f'juooo-{sid}']['start_date']}~{shows[f'juooo-{sid}']['end_date']}")

    if skipped:
        print(f"\n  skipped {len(skipped)} (no coordinate from detail):")
        for c, t in skipped:
            print(f"    - [{c}] {t}")

    out = {"meta": {"source": "juooo.com", "count": len(shows)}, "shows": list(shows.values())}
    (DATA / "china_juooo.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nWrote {len(shows)} shows -> data/china_juooo.json")


if __name__ == "__main__":
    main()
