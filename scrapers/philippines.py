# -*- coding: utf-8 -*-
"""Philippines (Metro Manila) — TicketWorld all-shows listing.

premier.ticketworld.com.ph 是馬尼拉主要票務(Ticketek 系),Broadway/West End 亞洲巡演
的馬尼拉站(Charlie and the Chocolate Factory、On Your Feet!、The Notebook…)都在這裡賣
(2026-07-14 使用者發現整個菲律賓缺口)。頁面是 server-rendered 但有 bot 牆:urllib 403、
curl_cffi 拿到 2.6KB 殼——真瀏覽器(Playwright Chromium)可過,同 atrapalo.py 先例。

只收「西方音樂劇」:標題比對 works.json registry(canonical+aliases 折 group key)。
菲律賓原創(OPM musical)/演唱會/兒童秀/頒獎禮一律不收——使用者規格:只要 Broadway/WestEnd。

日期:「Wed 8 Jul 2026 to Sun 26 Jul 2026」「Fri 17 Jul to Sat 18 Jul 2026」(首段年份省略,
補尾段的年)「Tue 28 Jul 2026」單日。解析不了的(如「Premieres: September 18」)整筆跳過,
寧缺勿假。

場館座標:Nominatim/OSM 查證(2026-07-14);表裡沒有的場館跳過並列印(先驗座標再收)。
"""
import io
import json
import re
import sys
from datetime import datetime
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
DATA = Path(__file__).resolve().parent.parent / "data"
URL = "https://premier.ticketworld.com.ph/shows/show.aspx?sh=PHEVENTS22"

# OSM/Nominatim 查證(2026-07-14)。Proscenium=Rockwell Center 建築群級(±200m)。
VENUES = {
    "the theatre at solaire":              (14.5224533, 120.9822613, "Parañaque"),
    "the proscenium theater":              (14.5657290, 121.0387500, "Makati"),
    "samsung performing arts theater":     (14.5723250, 121.0187760, "Makati"),
    "newport performing arts theater":     (14.5192780, 121.0195760, "Pasay"),
    "globe auditorium, maybank performing arts theater": (14.5477200, 121.0497670, "Taguig"),
    "aliw theater":                        (14.5569670, 120.9858530, "Pasay"),
    "music museum":                        (14.6025050, 121.0510900, "San Juan"),
}

MONTHS = {m: i + 1 for i, m in enumerate(
    ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"])}

DATE_RE = re.compile(
    r"(?:Mon|Tue|Wed|Thu|Fri|Sat|Sun)\s+(\d{1,2})\s+([A-Z][a-z]{2})\w*\s*(\d{4})?"
    r"(?:\s*(?:to|-|–)\s*(?:Mon|Tue|Wed|Thu|Fri|Sat|Sun)\s+(\d{1,2})\s+([A-Z][a-z]{2})\w*\s+(\d{4}))?")


def parse_dates(text):
    m = DATE_RE.search(text)
    if not m:
        return None, None
    d1, mo1, y1, d2, mo2, y2 = m.groups()
    if d2:                                   # range;首段缺年 → 用尾段年
        y1 = y1 or y2
        try:
            start = f"{int(y1):04d}-{MONTHS[mo1]:02d}-{int(d1):02d}"
            end = f"{int(y2):04d}-{MONTHS[mo2]:02d}-{int(d2):02d}"
            return start, end
        except (KeyError, ValueError):
            return None, None
    if y1:                                   # 單日
        try:
            d = f"{int(y1):04d}-{MONTHS[mo1]:02d}-{int(d1):02d}"
            return d, d
        except (KeyError, ValueError):
            return None, None
    return None, None


def gkey(t):
    """works registry 比對用的寬鬆 key(與 build_shows group_key 同精神:小寫去標點,
    去 the musical/the story of… 尾綴)。"""
    t = (t or "").lower()
    t = re.sub(r"[!:,.'’&]|the musical|a new musical", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t


def known_works():
    """works.json 的 canonical+aliases 全部折成寬鬆 key 集(=「西方音樂劇」白名單)。"""
    works = json.loads((DATA / "works.json").read_text(encoding="utf-8"))
    keys = set()
    rows = works if isinstance(works, list) else works.get("works", [])
    for w in rows:
        if not isinstance(w, dict):
            continue
        for name in [w.get("canonical") or w.get("title")] + (w.get("aliases") or []):
            if name:
                keys.add(gkey(name))
    return keys


def fetch_text():
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        # bot 牆對 bundled Chromium 回 HTTP2_PROTOCOL_ERROR;真 Chrome(channel)可過。
        # CI 沒有 Chrome 時回退 chromium+新版 headless(較不易被指紋)。
        try:
            b = p.chromium.launch(channel="chrome", headless=True)
        except Exception:  # noqa: BLE001
            b = p.chromium.launch(headless=True,
                                  args=["--headless=new", "--disable-blink-features=AutomationControlled"])
        page = b.new_page(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")
        page.goto(URL, wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(6000)          # SPA shell → 內容補水
        cards = page.evaluate("""() =>
          [...document.querySelectorAll("a[href*='show.aspx']")].map(a => {
            let el = a; for (let i = 0; i < 4 && el; i++) {
              if (el.innerText && el.innerText.length > 40) break;
              el = el.parentElement;
            }
            return { href: a.href, text: (el && el.innerText) || "" };
          })""")
        b.close()
    return cards


def main():
    keys = known_works()
    print(f"works registry keys: {len(keys)}")
    try:
        cards = fetch_text()
    except Exception as e:  # noqa: BLE001
        print(f"✗ fetch failed: {e} — keeping previous philippines.json")
        return 0
    shows, seen, skipped = [], set(), []
    for c in cards:
        lines = [x.strip() for x in (c.get("text") or "").split("\n") if x.strip()]
        if len(lines) < 3:
            continue
        title = lines[0]
        if gkey(title) not in keys:
            skipped.append(title)
            continue
        start = end = venue = None
        for ln in lines[1:5]:
            if start is None:
                s, e = parse_dates(ln)
                if s:
                    start, end = s, e
                    continue
            vkey = next((k for k in VENUES if k in ln.lower()), None)
            if vkey:
                venue = (ln.strip(), *VENUES[vkey])
        if not (start and venue):
            skipped.append(f"{title} (無日期/場館未驗)")
            continue
        vname, lat, lng, district = venue
        sid = "ph-" + re.sub(r"[^a-z0-9]+", "-", f"{title}-{vname}".lower()).strip("-")
        if sid in seen:
            continue
        seen.add(sid)
        shows.append({
            "id": sid, "title": title, "type": "tour",
            "venue": vname, "city": "Manila", "country": "Philippines",
            "lat": lat, "lng": lng,
            "start_date": start, "end_date": end,
            "ticket_url": c.get("href") or URL,
            "image": None,                    # TicketWorld 圖不穩定;交 build 的同組真海報繼承
            "tour_name": None, "verified": True,
            "source": "ticketworld.com.ph",
        })
        print(f"  ✓ {title[:40]:42} @ {vname[:34]:36} {start}~{end}")
    from datetime import timezone
    out = {"meta": {"source": "ticketworld.com.ph", "count": len(shows),
                    "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d")},
           "shows": shows}
    (DATA / "philippines.json").write_text(json.dumps(out, ensure_ascii=False, indent=2),
                                           encoding="utf-8")
    print(f"kept {len(shows)}, skipped {len(skipped)} (非西方音樂劇/資料不齊)")
    for s in skipped[:20]:
        print("   skip:", s[:60])
    print(f"Wrote {len(shows)} -> data/philippines.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
