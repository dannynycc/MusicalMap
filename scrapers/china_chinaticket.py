"""China — 中票在线 / 中演院线 (chinaticket.com), the 中国对外文化集团 ticketing site.

A nationwide complement to the Poly chain (china_poly.py): 中演院线 runs venues Poly
doesn't (广州大剧院, 上海大宁剧院, 厦门闽南大戏院, …). Unlike Damai/Maoyan, chinaticket
is plain server-rendered HTML with NO anti-bot, so we read it directly:

  listing  https://www.chinaticket.com/wenyi/yinleju/   (musical category)
           -> <li class="ticket_list_tu"> rows: title + poster + /view/{id}.html
  detail   https://www.chinaticket.com/view/{id}.html
           -> "地点：<venue>（<full street address>）" + "时间：<date range>"

Only rows whose title is a staged 音乐剧 are kept. Coordinates come ONLY from
data/cn_venues.json (Google-geocoded from the detail-page address, GCJ→WGS84); a
venue with no verified coord is SKIPPED (never placed at a guess). build_shows.py
then cross-source-dedups against Poly/Culture Square by (group, city, venue).

Output: data/china_chinaticket.json   Run: python scrapers/china_chinaticket.py
"""

import json
import re
import sys
import io
import time
import urllib.request
from pathlib import Path

try:
    from opencc import OpenCC
    _conv = OpenCC("t2s").convert
except Exception:  # noqa: BLE001
    def _conv(s): return s or ""

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

DATA = Path(__file__).resolve().parent.parent / "data"
BASE = "https://www.chinaticket.com"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"
# province/municipality prefixes → English city (best-effort; falls back to the Chinese
# 市 token parsed from the address).
CITY_EN = {
    "北京": "Beijing", "上海": "Shanghai", "广州": "Guangzhou", "深圳": "Shenzhen",
    "天津": "Tianjin", "重庆": "Chongqing", "武汉": "Wuhan", "南京": "Nanjing",
    "杭州": "Hangzhou", "苏州": "Suzhou", "成都": "Chengdu", "西安": "Xi'an",
    "厦门": "Xiamen", "广西": "Nanning", "南宁": "Nanning",
}


def fetch(url):
    return urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=25).read().decode("utf-8", "ignore")


def clean_title(raw):
    m = re.search(r"《([^》]+)》", raw)
    t = m.group(1) if m else re.sub(r"^.*?音[乐樂]剧", "", raw)
    return re.sub(r"[（(]?中文版[)）]?$", "", t).strip() or raw.strip()


def parse_dates(s):
    if not s or "待定" in s:
        return None, None
    ds = re.findall(r"(\d{4})[.\-/](\d{1,2})[.\-/](\d{1,2})", s)
    if not ds:
        return None, None
    start = f"{int(ds[0][0])}-{int(ds[0][1]):02d}-{int(ds[0][2]):02d}"
    end = f"{int(ds[-1][0])}-{int(ds[-1][1]):02d}-{int(ds[-1][2]):02d}"
    return start, end


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


def city_from_address(addr):
    m = re.search(r"([一-龥]{2,4})市", addr or "")
    if m:
        cn = m.group(1)
        return CITY_EN.get(cn, cn)
    for cn, en in CITY_EN.items():
        if cn in (addr or ""):
            return en
    return None


def main():
    reg = load_coords()
    html = fetch(BASE + "/wenyi/yinleju/")
    block = re.search(r"s_ticket_list(.*?)(?:s_page|footer|</body>)", html, re.S)
    block = block.group(1) if block else html
    rows = re.findall(r'<li class="ticket_list_tu[^>]*>.*?<img src="([^"]+)"[^>]*>.*?href="(https://www\.chinaticket\.com/view/\d+\.html)"[^>]*title="([^"]+)"', block, re.S)
    print(f"{len(rows)} listing rows")

    shows, skipped = {}, []
    for img, link, raw_title in rows:
        if "音乐剧" not in raw_title and "音樂劇" not in raw_title:
            continue
        try:
            d = fetch(link)
        except Exception as e:  # noqa: BLE001
            print(f"  [skip] {link}: {e}")
            continue
        loc = re.search(r"地点：\s*([^（(]+)[（(]([^）)]+)[）)]", re.sub(r"<[^>]+>", "", d))
        if not loc:
            continue
        venue, addr = loc.group(1).strip(), loc.group(2).strip()
        tm = re.search(r"时间：?\s*([0-9.\-~ 至]+)", re.sub(r"<[^>]+>", " ", d))
        start, end = parse_dates(tm.group(1) if tm else "")
        coord = match_venue(venue, reg)
        if not coord:
            skipped.append((venue, addr))
            continue
        lat, lng = coord
        vid = re.search(r"/view/(\d+)", link).group(1)
        sid = f"zct-{vid}"
        shows[sid] = {
            "id": sid, "title": clean_title(raw_title), "type": "limited",
            "venue": venue, "city": city_from_address(addr) or "China", "country": "China",
            "lat": lat, "lng": lng, "start_date": start, "end_date": end,
            "ticket_url": link, "image": img if img.startswith("http") else None,
            "tour_name": None, "verified": True, "source": "chinaticket.com",
        }
        print(f"  {shows[sid]['title'][:18]:20s} @ {venue[:16]:18s} {shows[sid]['city']:10s} {start}~{end}")
        time.sleep(0.2)

    if skipped:
        print(f"\n  skipped {len(skipped)} (venue not in cn_venues.json):")
        for v, a in skipped:
            print(f"    - {v}  |  {a}")

    out = {"meta": {"source": "chinaticket.com", "count": len(shows)}, "shows": list(shows.values())}
    (DATA / "china_chinaticket.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nWrote {len(shows)} shows -> data/china_chinaticket.json")


if __name__ == "__main__":
    main()
