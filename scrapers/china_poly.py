"""China nationwide musicals — 保利票务 (Poly Theatre chain, weixin.polyt.cn).

Poly runs ~80 theatres across China and — unlike Damai/Maoyan (anti-bot walled)
— its WeChat-H5 ticketing backend exposes an OPEN JSON API (no captcha on reads).
Reverse-engineered from the H5 bundle:

  base = https://weixin.polyt.cn/platform-backend   (header Channel: theatre_wx)
  POST /good/search-products-data   {keyword, page, size}  -> paged product list
       (MyBatis-Plus IPage; the working page param is `page`, NOT pageIndex)
  GET  /dictionary/product/categories  -> 音乐剧 categoryId = 1099120000000000004

We page through keyword="音乐剧", keep records whose categoryName is a musical, and
emit one show per product. This is OFFICIAL Poly data (title, run dates, city,
venue, and a real poster) — far richer than the ypiao aggregator.

Coordinates come ONLY from data/cn_venues.json (Google-geocoded, GCJ→WGS84). A
product whose venue isn't in that table is SKIPPED — never placed at a guess. (Run
the one-off geocoding enrichment to add new Poly venues, then they appear.)

Work-origin tagging is decided in build_shows.py (registry → else China=中國原創).

Output: data/china_poly.json   Run: python scrapers/china_poly.py
"""

import json
import re
import sys
import io
import gzip
import time
import urllib.request
import urllib.parse
from pathlib import Path

try:
    from opencc import OpenCC
    _conv = OpenCC("t2s").convert
except Exception:  # noqa: BLE001
    def _conv(s): return s or ""

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

DATA = Path(__file__).resolve().parent.parent / "data"
BASE = "https://weixin.polyt.cn/platform-backend"
UA = ("Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 "
      "(KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0")
HDR = {"User-Agent": UA, "Accept-Encoding": "gzip", "Channel": "theatre_wx",
       "City-Code": "", "Content-Type": "application/json"}
# English names for the cities Poly serves (fallback: keep the Chinese name).
CITY_EN = {
    "北京": "Beijing", "上海": "Shanghai", "广州": "Guangzhou", "深圳": "Shenzhen",
    "天津": "Tianjin", "重庆": "Chongqing", "武汉": "Wuhan", "南京": "Nanjing",
    "杭州": "Hangzhou", "苏州": "Suzhou", "成都": "Chengdu", "西安": "Xi'an",
    "沈阳": "Shenyang", "哈尔滨": "Harbin", "青岛": "Qingdao", "济南": "Jinan",
    "郑州": "Zhengzhou", "长沙": "Changsha", "南昌": "Nanchang", "合肥": "Hefei",
    "福州": "Fuzhou", "厦门": "Xiamen", "太原": "Taiyuan", "海口": "Haikou",
    "南宁": "Nanning", "银川": "Yinchuan", "无锡": "Wuxi", "宁波": "Ningbo",
    "常州": "Changzhou", "淄博": "Zibo", "潍坊": "Weifang", "烟台": "Yantai",
    "珠海": "Zhuhai", "东莞": "Dongguan", "廊坊": "Langfang", "马鞍山": "Ma'anshan",
    "黄冈": "Huanggang", "慈溪": "Cixi", "诸暨": "Zhuji", "衢州": "Quzhou",
    "昆山": "Kunshan", "张家港": "Zhangjiagang", "启东": "Qidong", "衡阳": "Hengyang",
    "泰州": "Taizhou", "南通": "Nantong", "延边": "Yanbian", "延吉": "Yanji",
    "长春": "Changchun", "大连": "Dalian", "贵阳": "Guiyang", "昆明": "Kunming",
    "南充": "Nanchong", "临平": "Linping",
}
MUSICAL_CAT = "音乐剧"


def _get(path, data):
    req = urllib.request.Request(BASE + path, data=json.dumps(data).encode(), headers=HDR)
    resp = urllib.request.urlopen(req, timeout=30)
    raw = resp.read()
    if resp.headers.get("Content-Encoding") == "gzip":
        raw = gzip.decompress(raw)
    return json.loads(raw.decode("utf-8", "ignore"))


def clean_title(name):
    """'（粤海街道文体中心）…|沉浸式音乐剧《Ash亚斯》' → 'Ash亚斯' ; strip leading venue
    brackets / 'X音乐剧' genre prefixes, take the 《…》 core, drop 中文版/巡演 tails."""
    m = re.search(r"《([^》]+)》", name)
    t = m.group(1) if m else re.sub(r"^.*?音[乐樂]剧", "", name)
    t = re.sub(r"[（(][^（()）]*[)）]", "", t)                    # inline parentheticals
    t = re.sub(r"(中文版|中文|巡演版?|.{0,3}站合作|大剧场.*|镜框式.*)$", "", t).strip()
    return t or name.strip()


def parse_dates(s):
    """'2026.06.05-2027.06.27' / '2026.06.17-06.18' / '2026.06.16 星期二' → ISO start,end."""
    if not s:
        return None, None
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


def _fold(s):
    s = re.sub(r"[\s\-－—·【】\[\]()（）]", "", _conv(s or ""))
    return re.sub(r"(大剧场|歌剧厅|音乐厅|中剧场|小剧场|歌剧院)$", "", s)


def load_coords():
    vl = json.loads((DATA / "cn_venues.json").read_text(encoding="utf-8"))
    return [(_fold(x["native"]), x["lat"], x["lng"]) for x in vl]


def match_venue(raw, reg):
    f = _fold(raw)
    if not f:
        return None
    for k, lat, lng in reg:
        if k and (f in k or k in f):
            return lat, lng
    return None


def main():
    reg = load_coords()
    products = {}
    for pg in range(1, 16):
        try:
            d = _get("/good/search-products-data", {"keyword": "音乐剧", "page": pg, "size": 30}).get("data") or {}
        except Exception as e:  # noqa: BLE001
            print(f"  [page {pg}] {e}")
            break
        recs = d.get("records") or []
        if not recs:
            break
        for r in recs:
            if MUSICAL_CAT in (r.get("categoryName") or ""):
                products[r["productId"]] = r
        if pg >= (d.get("pages") or 1):
            break
        time.sleep(0.15)
    print(f"{len(products)} unique musical products")

    shows, skipped = {}, []
    for pid, r in products.items():
        venue = r.get("placeCname") or ""
        coord = match_venue(venue, reg)
        if not coord:
            skipped.append((r.get("cityName"), venue, clean_title(r["productNameShort"])))
            continue
        lat, lng = coord
        start, end = parse_dates(r.get("productShowTime"))
        # Resident/immersive spaces (保利剧聚空间…) carry a year-long booking WINDOW as
        # productShowTime, but tickets only go on sale in short batches — so a hard
        # far-future end (e.g. 2027-06-27) overstates a confirmed run. Treat any run
        # longer than ~4 months as open-ended (end=null): the frontend then applies
        # its rolling ~12-month horizon, same as Broadway/West End resident long-runners.
        if start and end:
            try:
                from datetime import date as _d
                if (_d.fromisoformat(end) - _d.fromisoformat(start)).days > 120:
                    end = None
            except ValueError:
                pass
        city_cn = r.get("cityName") or ""
        sid = f"poly-{pid}"
        title = clean_title(r["productNameShort"])
        # Poly's own weixin.polyt.cn detail page is a WeChat-only SPA — in a normal
        # browser it just renders the blank shell, so it's useless as a web link.
        # Point instead at a Damai search for the show title: Damai is China's main
        # ticketing platform and the search page works for real browsers (its bot
        # wall only blocks automation, not human clicks), so users land on a real
        # buy page. Search uses the Chinese title (before build canonicalises it).
        ticket = "https://search.damai.cn/search.htm?keyword=" + urllib.parse.quote(title)
        shows[sid] = {
            "id": sid, "title": title, "type": "limited",
            "venue": venue, "city": CITY_EN.get(city_cn, city_cn), "country": "China",
            "lat": lat, "lng": lng, "start_date": start, "end_date": end,
            "ticket_url": ticket,
            "image": r.get("verticalPictureUrl") or r.get("productImg") or None,
            "tour_name": None, "verified": True, "source": "polyt.cn",
        }
        print(f"  {shows[sid]['title'][:18]:20s} @ {venue[:16]:18s} {shows[sid]['city']:10s} {start}~{end}")

    if skipped:
        print(f"\n  skipped {len(skipped)} (venue not in cn_venues.json — no verified coord):")
        for c, v, t in skipped:
            print(f"    - [{c}] {t} @ {v}")

    out = {"meta": {"source": "polyt.cn", "count": len(shows)}, "shows": list(shows.values())}
    (DATA / "china_poly.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nWrote {len(shows)} shows -> data/china_poly.json")


if __name__ == "__main__":
    main()
