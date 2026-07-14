"""China multi-city musicals ??discovery via the ?巨蝵?(ypiao.com) aggregator.

The flagship venue (Shanghai Culture Square) is scraped officially in china.py;
this fills in OTHER cities. Damai / Maoyan / Poly / Tianqiao sites are all SPA +
anti-bot walled, so for nationwide discovery we read ypiao.com's musical listings
(per-city + national index), which are plain server-rendered HTML.

ypiao is a THIRD-PARTY aggregator, so we treat it as a discovery source only:
 ??keep only items whose title is a staged musical  ?喃??扼艾? (drops the concerts
   / 瞍隡?/ ?Ｙ?喃?隡?that share the listing pages),
 ??take title / city / venue / run-dates from the listing row,
 ??resolve coordinates ONLY from data/cn_venues.json (Google-geocoded, GCJ?GS84
   already applied). A show whose venue we can't map to a known coord is SKIPPED ??   better to omit it than to place it at a guessed/wrong location.
 ??posters: ypiao detail pages carry only placeholders, so none here; registered
   works (e.g. ?折擳蔣 ??Phantom) inherit a poster by group in build_shows.py.

Work-origin tagging is decided in build_shows.py (registry ??else China = 銝剖??).

Output: data/china_ypiao.json   Run: python scrapers/china_ypiao.py
"""

import json
import re
import sys
import io
import urllib.request
from pathlib import Path

try:
    from opencc import OpenCC
    _T2S = OpenCC("t2s")
    def t2s(s): return _T2S.convert(s or "")
except Exception:  # noqa: BLE001 ??OpenCC optional; fall back to identity
    def t2s(s): return s or ""

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

DATA = Path(__file__).resolve().parent.parent / "data"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120 Safari/537.36")
# City slug ??English city name. ypiao musical pages: /yanchu/yinyueju{slug}/ ; plus
# the national index /yanchu/yinyueju/.
CITY_EN = {
    "beijing": "Beijing", "shanghai": "Shanghai", "guangzhou": "Guangzhou",
    "shenzhen": "Shenzhen", "wuhan": "Wuhan", "hangzhou": "Hangzhou",
    "nanjing": "Nanjing", "chengdu": "Chengdu", "suzhou": "Suzhou", "xian": "Xi'an",
    "chongqing": "Chongqing", "tianjin": "Tianjin", "guangzhou1": "Guangzhou",
}
CN_CITY_EN = {"?漪": "Beijing", "銝絲": "Shanghai", "撟踹?": "Guangzhou", "瘛勗": "Shenzhen",
              "甇行?": "Wuhan", "?剖?": "Hangzhou", "?漪": "Nanjing", "?": "Chengdu",
              "??": "Suzhou", "镼踹?": "Xi'an", "??": "Chongqing", "憭拇揖": "Tianjin"}


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    return urllib.request.urlopen(req, timeout=25).read().decode("utf-8", "ignore")


def parse_dates(s):
    """'2026.07.30-08.02' / '2026.08.26-09.05' / '2026.08.01' ??ISO start,end
    (the end often omits its year ??inherit the start's, roll forward if before it)."""
    m = re.search(r"(\d{4})\.(\d{1,2})\.(\d{1,2})", s)
    if not m:
        return None, None
    sy, sm, sd = int(m.group(1)), int(m.group(2)), int(m.group(3))
    start = f"{sy}-{sm:02d}-{sd:02d}"
    e = re.search(r"[-~]\s*(?:(\d{4})\.)?(\d{1,2})\.(\d{1,2})", s)
    if not e:
        return start, start
    ey = int(e.group(1)) if e.group(1) else sy
    em, ed = int(e.group(2)), int(e.group(3))
    if not e.group(1) and (em, ed) < (sm, sd):
        ey += 1
    return start, f"{ey}-{em:02d}-{ed:02d}"


def load_venue_coords():
    """native(folded) ??(display_native, lat, lng). Folded = simplified, separators
    stripped, trailing hall qualifier removed, so '憭拇‘?箸銝剖?-憭批?? matches
    '?漪憭拇???銝剖? 憭批???."""
    vl = json.loads((DATA / "cn_venues.json").read_text(encoding="utf-8"))
    out = {}
    for x in vl:
        out[_fold(x["native"])] = (x["native"], x["lat"], x["lng"])
    return out


def _fold(s):
    s = re.sub(r"[\s\-嚗愍", "", t2s(s))
    return re.sub(r"(憭批?漏甇??喃??銝剖?漏撠?漏甇?└憭批?Ｗ之?批)$", "", s)


def match_venue(raw, coords):
    f = _fold(raw)
    if not f:
        return None
    for k, v in coords.items():
        if k and (f in k or k in f):
            return v
    return None


def main():
    coords = load_venue_coords()
    pages = ["https://www.ypiao.com/yanchu/yinyueju/"]
    pages += [f"https://www.ypiao.com/yanchu/yinyueju{s}/" for s in
              ("beijing", "shanghai", "guangzhou", "shenzhen", "wuhan", "hangzhou",
               "nanjing", "chengdu", "suzhou", "xian", "chongqing", "tianjin")]
    rows = {}
    for url in pages:
        try:
            html = fetch(url)
        except Exception as e:  # noqa: BLE001
            print(f"  [skip] {url}: {e}")
            continue
        for href, inner in re.findall(r'<a[^>]+href="(/t_\d+)/?"[^>]*>(.*?)</a>', html, re.S):
            txt = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", inner)).strip()
            if "?喃??扼? not in txt and "?單??? not in txt:
                continue
            title = re.search(r"??[^?+)??, txt)
            venue = re.search(r"?粹?[:嚗\s*(\S+)", txt)
            city = re.search(r"\[([^\]]+)\]", txt)
            date = re.search(r"\d{4}\.\d{1,2}\.\d{1,2}[^ ]*", txt)
            if not (title and venue):
                continue
            rows[href] = (title.group(1).strip(), venue.group(1),
                          city.group(1) if city else "", date.group(0) if date else "")

    shows, skipped = {}, []
    for href, (title, venue, city_cn, dstr) in rows.items():
        coord = match_venue(venue, coords)
        if not coord:
            skipped.append((title, venue))
            continue
        _, lat, lng = coord
        start, end = parse_dates(dstr)
        tid = href.strip("/").replace("t_", "")
        sid = f"ypiao-{tid}"
        shows[sid] = {
            "id": sid, "title": title, "type": "limited",
            "venue": venue, "city": CN_CITY_EN.get(city_cn, city_cn or "China"), "city_cn": city_cn or None,
            "country": "China", "lat": lat, "lng": lng,
            "start_date": start, "end_date": end,
            "ticket_url": f"https://www.ypiao.com{href}",
            "image": None, "tour_name": None, "verified": True,
            "source": "ypiao.com",
        }
        print(f"  {title[:20]:22s} @ {venue[:18]:20s} {shows[sid]['city']:10s} {start}~{end}")
    if skipped:
        print(f"\n  skipped {len(skipped)} (venue not in cn_venues.json ??no verified coord):")
        for t, v in skipped:
            print(f"    - {t} @ {v}")

    out = {"meta": {"source": "ypiao.com", "count": len(shows)}, "shows": list(shows.values())}
    (DATA / "china_ypiao.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nWrote {len(shows)} shows -> data/china_ypiao.json")


if __name__ == "__main__":
    main()
