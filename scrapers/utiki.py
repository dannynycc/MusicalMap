"""Taiwan musicals from the utiki ticketing engine (寬宏售票 KHAM + udn售票 UDN).

Both sites run the same ASP.NET "UTK" engine on different skins:
  - listing page lists product ids + titles (KHAM: category 音樂劇=80; UDN: name search 音樂劇)
  - a per-product session page carries the real run dates + venue (the marketing
    detail page is polluted with refund boilerplate / cross-sell, so we ignore it)

KHAM session page  UTK02/UTK0201_00.aspx  -> an eventTABLE, one <tr> per session:
    <td>2026/06/18(四)14:30</td> <td>…<span id="PLACE_NAME">國家戲劇院</span>… q=<address></td>
UDN  session page  UTK02/UTK0203_.aspx    -> a yd_orderShow block:
    演出日期：2026/11/20 ~ 2026/11/29   演出地點：臺北表演藝術中心 大劇院

A program may tour several venues -> we emit one show per distinct venue with that
venue's own date range. Coordinates are left to Google geocoding (geocode_google.py
reads data/shows.json venues); we only resolve the English city for dedup/geocode.

Output: data/utiki.json    Run: python scrapers/utiki.py
"""

import json
import re
import sys
import io
import html
import urllib.request
import urllib.parse
from datetime import datetime, timezone, timedelta
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
DATA = Path(__file__).resolve().parent.parent / "data"
TW_TZ = timezone(timedelta(hours=8))
UA = {"User-Agent": "Mozilla/5.0 (MusicalMap)"}

# non-musicals that can ride the 音樂劇 category/search (user-flagged philosophy:
# choirs, concerts and workshops are not staged musicals). Substring match on title.
EXCLUDE = ["老闆", "陽春麵", "演唱會", "合唱", "工作坊", "交響音樂會"]

# Chinese city/county -> English, to align with curated tw_venues + opentix cities.
CITY_MAP = {
    "臺北": "Taipei", "台北": "Taipei", "新北": "New Taipei", "基隆": "Keelung",
    "桃園": "Taoyuan", "新竹": "Hsinchu", "苗栗": "Miaoli", "臺中": "Taichung", "台中": "Taichung",
    "彰化": "Changhua", "南投": "Nantou", "雲林": "Yunlin", "嘉義": "Chiayi",
    "臺南": "Tainan", "台南": "Tainan", "高雄": "Kaohsiung", "屏東": "Pingtung",
    "宜蘭": "Yilan", "花蓮": "Hualien", "臺東": "Taitung", "台東": "Taitung",
    "澎湖": "Penghu", "金門": "Kinmen", "連江": "Lienchiang", "馬祖": "Lienchiang",
}

SITES = [
    {
        "name": "kham", "source": "kham.com.tw",
        "base": "https://kham.com.tw/application",
        "listing": "/UTK01/UTK0101_06.aspx?TYPE=1&CATEGORY=80",
        "detail": "https://kham.com.tw/application/UTK02/UTK0201_.aspx?PRODUCT_ID={pid}",
        "session": "/UTK02/UTK0201_00.aspx?PRODUCT_ID={pid}",
        "parse_list": "span_title", "parse_session": "kham_table",
    },
    {
        "name": "udn", "source": "tickets.udnfunlife.com",
        "base": "https://tickets.udnfunlife.com/application",
        "listing": "/UTK01/UTK0101_06.aspx?searchProductName=%E9%9F%B3%E6%A8%82%E5%8A%87",
        "detail": "https://tickets.udnfunlife.com/application/UTK02/UTK0201_.aspx?PRODUCT_ID={pid}",
        "session": None,                              # UDN cards already carry dates+venues
        "parse_list": "udn_cards", "parse_session": None,
    },
]


def get(url, referer=None):
    h = dict(UA)
    if referer:
        h["Referer"] = referer
    req = urllib.request.Request(url, headers=h)
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", "ignore")


def city_of(*texts):
    """Longest Chinese city/county name found in any of the texts -> English."""
    blob = " ".join(t or "" for t in texts)
    best, best_en = "", ""
    for zh, en in CITY_MAP.items():
        if zh in blob and len(zh) >= len(best):
            best, best_en = zh, en
    return best_en


def split_title(raw, en_hint=""):
    raw = html.unescape(raw or "").strip()
    m = re.search(r"[《＜<](.+?)[》＞>]", raw)
    if m:
        zh = m.group(1).strip()
    else:
        zh = re.sub(r"^(倫敦|經典法文|百老匯|影集式|全本|魔幻|外百老匯)+", "", raw)
        zh = re.sub(r"音樂劇.*$", "", zh).strip() or raw
    en = en_hint.strip()
    if not en:
        em = re.search(r"([A-Za-z][A-Za-z0-9 ,.&'\-:!?]{2,})\s*$", raw)
        en = em.group(1).strip() if em else ""
    return zh, en


# ---------- listing parsers -> [{pid, title, dates, venues, ended}] ----------
def list_span_title(h):
    """KHAM: cards only carry title; dates+venue come from the session page."""
    out = []
    for m in re.finditer(r'PRODUCT_ID=([A-Za-z0-9]+)"[^>]*>.*?<span class="title">(.*?)</span>', h, re.S):
        out.append({"pid": m.group(1), "title": m.group(2), "dates": [], "venues": [], "ended": False})
    return out


def list_udn_cards(h):
    """UDN: each card already holds title, date range, venue(s) and sale status."""
    out = []
    for m in re.finditer(r"PRODUCT_ID=([A-Za-z0-9]+).*?yd_card-body'>(.*?)</a>", h, re.S):
        pid, body = m.group(1), html.unescape(m.group(2))
        cells = [c.strip() for c in re.sub(r"<[^>]+>", "|", body).split("|") if c.strip()]
        if not cells:
            continue
        di = next((i for i, c in enumerate(cells)
                   if re.search(r"\d{4}/\d{1,2}/\d{1,2}\s*[~～至]", c)), None)
        dates, venues = [], []
        if di is not None:
            dates = re.findall(r"\d{4}/\d{1,2}/\d{1,2}", cells[di])
            if di + 1 < len(cells):
                venues = [v.strip() for v in cells[di + 1].split(",") if v.strip()]
        out.append({"pid": pid, "title": cells[0], "dates": dates,
                    "venues": venues, "ended": "結束銷售" in body})
    return out


# ---------- session parsers: -> list of {venue, city, dates:[YYYY-MM-DD], en} ----------
def sess_kham_table(h):
    m = re.search(r'class="eventTABLE".*?</table>', h, re.S)
    if not m:
        return []
    by_venue = {}
    for tr in re.findall(r"<tr.*?</tr>", m.group(0), re.S):
        tr = html.unescape(tr)                       # &amp;q= -> &q=
        d = re.search(r"(\d{4})/(\d{1,2})/(\d{1,2})", tr)
        v = re.search(r'id="PLACE_NAME">([^<]+)<', tr)
        if not d or not v:
            continue
        venue = v.group(1).strip()
        addr_m = re.search(r"[?&]q=([^&\"]+)", tr)
        addr = urllib.parse.unquote(addr_m.group(1)) if addr_m else ""
        ymd = f"{int(d.group(1)):04d}-{int(d.group(2)):02d}-{int(d.group(3)):02d}"
        rec = by_venue.setdefault(venue, {"venue": venue, "addr": "", "dates": []})
        rec["dates"].append(ymd)
        if addr and not rec["addr"]:
            rec["addr"] = addr
    res = []
    for rec in by_venue.values():
        res.append({"venue": rec["venue"], "city": city_of(rec["addr"], rec["venue"]),
                    "dates": sorted(rec["dates"]), "en": ""})
    return res


PARSERS_LIST = {"span_title": list_span_title, "udn_cards": list_udn_cards}
PARSERS_SESS = {"kham_table": sess_kham_table}


def resolve_venues(site, p):
    """Return [{venue, city, dates:[YYYY-MM-DD]}] for a product, fetching the
    session page only when the listing card didn't already carry venues (KHAM)."""
    if p["venues"]:                                  # UDN: listing card had it all
        rng = sorted({"{:04d}-{:02d}-{:02d}".format(*[int(x) for x in d.split("/")])
                      for d in p["dates"]})
        return [{"venue": v, "city": city_of(v), "dates": rng} for v in p["venues"]]
    if site["session"]:                              # KHAM: per-venue rows on session page
        try:
            sess = get(site["base"] + site["session"].format(pid=p["pid"]),
                       referer=site["detail"].format(pid=p["pid"]))
        except Exception:
            return []
        return PARSERS_SESS[site["parse_session"]](sess)
    return []


def main():
    today = datetime.now(TW_TZ).strftime("%Y-%m-%d")
    shows, dropped = [], []
    for site in SITES:
        try:
            listing = get(site["base"] + site["listing"])
        except Exception as e:
            print(f"  {site['name']}: listing failed ({e})", flush=True)
            continue
        products = PARSERS_LIST[site["parse_list"]](listing)
        print(f"  {site['name']}: {len(products)} 音樂劇 product(s)", flush=True)
        for p in products:
            raw_title = p["title"]
            if any(x in raw_title for x in EXCLUDE):
                dropped.append(raw_title + " (排除)"); continue
            zh, en = split_title(raw_title)
            for v in resolve_venues(site, p):
                dates = v.get("dates") or []
                if not dates:
                    dropped.append(zh + f" @ {v['venue']} (無日期)"); continue
                start, end = dates[0], dates[-1]
                if end < today or p.get("ended"):
                    dropped.append(zh + f" @ {v['venue']} (已結束)"); continue
                shows.append({
                    "id": f"{site['name']}-{p['pid']}-{abs(hash(v['venue'])) % 10000:04d}",
                    "title": zh, "title_en": en,
                    "venue": v["venue"], "city": v["city"], "country": "Taiwan",
                    "lat": None, "lng": None,        # filled by geocode_google.py
                    "start_date": start, "end_date": end,
                    "image": None,
                    "ticket_url": site["detail"].format(pid=p["pid"]),
                    "type": "tour", "verified": True, "source": site["source"],
                })
    out = {"meta": {"source": "utiki (kham+udn)", "count": len(shows)}, "shows": shows}
    (DATA / "utiki.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {len(shows)} -> data/utiki.json", flush=True)
    for s in shows:
        print(f"    keep: {s['title']} @ {s['venue']} ({s['city']}) {s['start_date']}~{s['end_date']}", flush=True)
    for d in dropped:
        print("    drop:", d, flush=True)


if __name__ == "__main__":
    main()
