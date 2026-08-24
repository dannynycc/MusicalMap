"""Poland musicals — source: eBilet.pl (the dominant PL ticketing platform).

eBilet pages are server-rendered static HTML (no headless browser needed), but the
server rate-limits aggressive crawling (HTTP 429), so every request goes through a
polite throttle + exponential backoff.

How we read each show:
  - The "musicale" category page + per-city pages give us the set of event slugs:
      https://www.ebilet.pl/teatr/musicale
      https://www.ebilet.pl/teatr/musicale/miasto/{city}
  - Each event page (https://www.ebilet.pl/teatr/musicale/{slug}) carries:
      * a schema.org Event JSON-LD block (id="json-ld-event-data-...") with the clean
        title (name), venue (location.name), city (location.address.addressLocality)
        and a poster image. NOTE: the LD "image" URLs are corrupted by a doubled
        "https://www.ebilet.pl/media" prefix on eBilet's side, so we prefer og:image.
      * a JS data blob with "eventsDateFrom"/"eventsDateTo" = the authoritative run
        range, plus a list of "date":"YYYY-MM-DDT.." performance datetimes. We take
        the run from eventsDateFrom/To, falling back to min/max of future perf dates.

Non-musicals leak into the "musicale" bucket (concerts, recitals, galas, talent
shows, stand-up, solo-artist tours), so titles are filtered (see DROP/KEEP below).

2026-08-24 — bot 牆與守門(這支曾經悄悄弄丟 8 檔波蘭音樂劇):
  排程那班 19 個 slug 全數找到,但其中 **11 個事件頁 fetch failed**(six / wicked /
  my-fair-lady / next-to-normal / 1989 / high-heels …),只解析出 4 筆。當時本檔
  **沒有任何守門**,4 筆殘缺資料直接覆蓋掉前一天的 12 筆、退出碼還是 0 → CI 只發了
  一則 warning,線上就這樣少了 8 檔(SIX / Wicked / Beetlejuice / My Fair Lady /
  Next to Normal / Musical 1989 / Serce ze szkła / Metro 35 lat)。
  查下去發現 429 的 body 是 **DataDome 的 JS 挑戰頁**(`dd_referrer` +「Please enable
  JS」),封鎖是 IP 級:urllib / curl_cffi(chrome124) / headless Playwright / 真 Chrome
  當天全都拿到同一頁。逐頁重試不會過,只會加深封鎖(那班為此空轉 43 分鐘)。
  因此:
    · 偵測到挑戰頁 → `Blocked` → **中止整輪、不寫檔**(見 `_abort`)
    · 事件頁抓取失敗率 > `MAX_FETCH_FAIL` → 同樣不寫檔、非零退出
    · 重試次數由 6 收到 3(挑戰頁重試無用,單純節流 2 次退避夠了)
  守的是「抓取失敗率」而非 `_guard.py` 的筆數跌幅——這來源只有十幾筆,FLOOR=50 的
  筆數守門對它永遠空轉(`_guard.py` 檔頭已載明),失敗率才是對症的軸。
  ⚠️ 未來若 DataDome 常態化,下一步是 atrapalo.py 那套(Playwright 取 clearance
  cookie → 灌進 curl_cffi 快車道);已知 headless 當下也被擋,需要時再實測。

Output: data/poland.json     Run: python scrapers/poland.py
"""

import json
import re
import sys
import io
import html
import time
import hashlib
import urllib.request
import urllib.error
from datetime import datetime, timezone, timedelta
from typing import NoReturn
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
DATA = Path(__file__).resolve().parent.parent / "data"
CET = timezone(timedelta(hours=2))  # Poland is CEST in summer; date-only comparisons
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0",
      "Accept-Language": "pl"}
BASE = "https://www.ebilet.pl"

# Cities eBilet exposes a musicale sub-page for. The category page is the real
# superset; the city pages just help surface any slug the category lazy-loads off.
CITIES = ["warszawa", "gdynia", "lodz", "wroclaw", "chorzow", "gliwice",
          "poznan", "krakow", "katowice", "gdansk", "bydgoszcz", "szczecin"]

# Building-level coordinates for the major Polish musical houses. Matched by
# case-insensitive substring against the venue name from the event page.
# (key substring) -> (lat, lng)
VENUES = {
    "roma":            (52.2247, 21.0156),  # Teatr Muzyczny ROMA, Nowogrodzka 49, Warszawa
    "syrena":          (52.2196, 21.0190),  # Teatr Syrena, Litewska 3, Warszawa
    "buffo":           (52.2270, 21.0260),  # Studio Buffo, Konopnickiej 6, Warszawa
    "gdyni":           (54.5167, 18.5360),  # Teatr Muzyczny w Gdyni, pl. Grunwaldzki 1
    "w łodzi":         (51.7800, 19.4690),  # Teatr Muzyczny w Łodzi, Północna 47/51
    "w lodzi":         (51.7800, 19.4690),
    "capitol":         (51.1015, 17.0265),  # Teatr Muzyczny Capitol, Piłsudskiego 67, Wrocław
    "rozrywki":        (50.2960, 18.9540),  # Teatr Rozrywki, Konopnickiej 1, Chorzów
    "gliwicki":        (50.2945, 18.6610),  # Gliwicki Teatr Muzyczny, Nowy Świat 55/57
    "w poznaniu":      (52.4030, 16.9230),  # Teatr Muzyczny w Poznaniu, Niezłomnych 1e
}

# --- Non-musical filter ----------------------------------------------------
# Drop if any of these substrings appear in the (lower-cased) title. Covers the
# concert / recital / gala / talent-show / stand-up / solo-artist-tour leakage.
DROP_WORDS = [
    "koncert", "recital", "jazz", "kolęd", "koled", "kabaret", "stand-up",
    "stand up", "komediowy", "komediowa", "gala", "talent show", " tour",
    "tribute", "symfonicz", "improwizowany", "improwizacja",
]
# Known solo artists whose "musicale"-bucket entries are live shows, not musicals.
DROP_ARTISTS = [
    "michał bajor", "michal bajor", "edyta geppert", "igor herbut",
    "grzegorz turnau", "kayah", "andrzej piaseczny",
]
# Strong KEEP signals — overrides the drop list (e.g. a title that contains both
# "musical" and a borderline word). Known musical/operetka titles + genre words.
KEEP_WORDS = [
    "musical", "musicalow", "operetka", "wicked", "six", "mamma mia",
    "skrzypek na dachu", "dracula", "beetlejuice", "madagaskar",
    "next to normal", "metro", "dzień świstaka", "dzien swistaka",
    "chłopi", "chlopi", "wiedźmin", "wiedzmin", "producenci", "high heels",
    "my fair lady", "polita",
]


class FetchFailed(Exception):
    """單頁抓不到(逾時/連線錯/非挑戰頁的 429)。跟「這齣不是音樂劇」的合法丟棄
    不同型:合法丟棄是資料判斷,抓取失敗是**我們沒看到資料**,不可以當成「沒有這齣」。"""


class Blocked(Exception):
    """eBilet 的 bot 牆(DataDome)擋下了整個 IP,不是單頁失敗。

    2026-08-24 觀察到的樣子:HTTP 429,body 是 ~2.3KB 的 JS 挑戰頁(含 `dd_referrer`
    與「Please enable JS and disable any ad blocker」)。封鎖是 **IP 級**的——urllib、
    curl_cffi(chrome124 指紋)、headless Playwright、真 Chrome 全都拿到同一頁。
    這種狀態下逐頁重試只會加深封鎖(那天 CI 為此空轉 43 分鐘),所以一偵測到就中止整輪。"""


def _is_challenge(body):
    return "dd_referrer" in body or "disable any ad blocker" in body


# JSON-LD 缺 location 時的場館兜底(僅限場館固定的駐演製作,鍵為小寫劇名)。
#   Wicked — Teatr Muzyczny ROMA(Nowogrodzka 49, Warszawa)波蘭非複製版駐演。
#   查證(2026-08-24):teatrroma.pl/spektakl/wicked/ 官方場次表 2026-09-26~2026-11-29
#   與 eBilet 抓到的檔期完全一致;cojestgrane.pl 亦列同一場館與 9/26 首場。
VENUE_FALLBACK = {
    "wicked": ("Teatr Muzyczny ROMA", "Warszawa"),
}


def get(url, tries=3):
    """Fetch a URL as UTF-8 text, retrying with exponential backoff on 429/5xx.

    eBilet rate-limits bursts hard. 429 有兩種:單純節流(重試會過)與 bot 牆挑戰頁
    (重試永遠不會過,見 `Blocked`)。後者直接拋 `Blocked` 中止整輪。"""
    for k in range(tries):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=30) as r:
                body = r.read().decode("utf-8", "ignore")
            # DataDome 不一定用 429 送挑戰頁,200 也會——內容才是判準
            if _is_challenge(body):
                raise Blocked(url)
            return body
        except urllib.error.HTTPError as e:
            body = ""
            try:
                body = e.read().decode("utf-8", "ignore")
            except Exception:
                pass
            if e.code == 429 and _is_challenge(body):
                raise Blocked(url)
            if e.code in (429, 500, 502, 503) and k < tries - 1:
                time.sleep(15 * (k + 1))   # 15s, 30s
                continue
            return ""
        except Blocked:
            raise
        except Exception:
            if k < tries - 1:
                time.sleep(10 * (k + 1))
                continue
            return ""
    return ""


def collect_slugs():
    """Union of event slugs from the musicale category page + per-city pages."""
    slugs = {}
    pages = [f"{BASE}/teatr/musicale"] + \
            [f"{BASE}/teatr/musicale/miasto/{c}" for c in CITIES]
    for p in pages:
        d = get(p)
        for s in re.findall(r'href="/teatr/musicale/([^"/?#]+)"', d):
            slugs.setdefault(s, None)
        time.sleep(3.0)   # be polite between listing requests
    return list(slugs)


def is_musical(title):
    """Return (keep: bool, reason: str). KEEP words win over DROP words."""
    t = title.lower()
    if any(k in t for k in KEEP_WORDS):
        return True, "keep-signal"
    for a in DROP_ARTISTS:
        if a in t:
            return False, f"solo-artist ({a})"
    for w in DROP_WORDS:
        if w in t:
            return False, f"non-musical word ({w.strip()})"
    return None, "unsure"   # None = no strong signal either way


def parse_event(slug):
    """Fetch one event page → dict, or (None, reason) when it must be dropped."""
    url = f"{BASE}/teatr/musicale/{slug}"
    d = get(url)
    if not d:
        raise FetchFailed(slug)

    # Clean title from og:title, fall back to the LD name.
    og_t = re.search(r'<meta property="og:title" content="([^"]+)"', d)
    title = html.unescape(og_t.group(1)).strip() if og_t else slug

    keep, reason = is_musical(title)
    if keep is False:
        return None, f"{title} ({reason})"

    # schema.org Event JSON-LD: venue + city (most reliable).
    venue = city = None
    m = re.search(r'<script type="application/ld\+json" id="json-ld-event-data[^"]*">(.*?)</script>',
                  d, re.S)
    if m:
        try:
            o = json.loads(m.group(1))
            if not title or title == slug:
                title = (o.get("name") or title).strip()
            loc = o.get("location") or {}
            venue = (loc.get("name") or "").strip() or None
            addr = loc.get("address") or {}
            city = (addr.get("addressLocality") or "").strip() or None
        except Exception:
            pass

    # eBilet 的 JSON-LD 偶爾整塊少掉 location(2026-08-24 實例:Wicked 那頁),結果是
    # 一張沒有劇院、沒有城市、沒有座標的卡——地圖上根本不會出現。這裡只補**駐演製作**
    # (sit-down,場館固定),不碰巡演(巡演換場館,硬填就是造假)。
    # 每筆都要有一手依據,並在下面註明。
    if not venue:
        fb = VENUE_FALLBACK.get(title.strip().lower())
        if fb:
            venue, city = fb

    # If we still have no strong musical signal AND it's an unsure title, drop it
    # (instruction: "when unsure, exclude and log").
    if keep is None:
        return None, f"{title} (unsure — no musical signal)"

    # Run range: prefer the authoritative eventsDateFrom/To, else min/max of the
    # future performance dates ("date":"YYYY-MM-DD...").
    today = datetime.now(CET).strftime("%Y-%m-%d")
    ef = re.findall(r'"eventsDateFrom":"(20\d{2}-\d{2}-\d{2})', d)
    et = re.findall(r'"eventsDateTo":"(20\d{2}-\d{2}-\d{2})', d)
    perf = sorted(set(re.findall(r'"date":"(20\d{2}-\d{2}-\d{2})T', d)))
    future = [x for x in perf if x >= today]
    start = ef[0] if ef else (future[0] if future else None)
    end = et[0] if et else (future[-1] if future else None)
    if not start or not end:
        return None, f"{title} (no dates found)"
    # FUTURE/CURRENT only.
    if end < today:
        return None, f"{title} (ended {end})"

    # Poster: og:image is the clean URL (the LD image[] is corrupted by a doubled
    # /media prefix on eBilet's side).
    og_i = re.search(r'<meta property="og:image" content="([^"]+)"', d)
    image = og_i.group(1).strip() if og_i else None

    return {
        "title": title, "venue": venue, "city": city,
        "start": start, "end": end, "image": image, "url": url,
    }, "kept"


def venue_coords(venue):
    """Substring-match the venue name against VENUES → (lat, lng) or (None, None)."""
    if not venue:
        return None, None
    v = venue.lower()
    for key, (lat, lng) in VENUES.items():
        if key in v:
            return lat, lng
    return None, None


# 事件頁抓取失敗率超過這個比例就視為來源故障:不覆蓋舊檔、以非零退出碼讓 CI 變紅。
# 門檻取 0.25:合法的個別失敗(某頁暫時 500)不該擋,整批失敗一定要擋。
MAX_FETCH_FAIL = 0.25


def _abort(why, kept_n, slugs_n, failed=None) -> NoReturn:
    """不覆蓋舊檔就結束——寧可資料舊一天,也不要用殘缺資料蓋掉好資料。"""
    print(f"\n[poland] ABORT: {why}", flush=True)
    print(f"[poland] 只解析到 {kept_n}/{slugs_n} 筆,"
          f"data/poland.json **維持原樣**(舊資料仍完整,build_shows 照常拿得到)。",
          flush=True)
    if failed:
        print("[poland] 抓不到的 slug:", ", ".join(failed), flush=True)
    sys.exit(1)


def main():
    try:
        slugs = collect_slugs()
    except Blocked as b:
        _abort(f"eBilet bot 牆(DataDome)在列表頁就擋下整個 IP — {b}",
               kept_n=0, slugs_n=0)
    print(f"Found {len(slugs)} candidate slugs", flush=True)

    kept, dropped, failed = [], [], []
    for slug in slugs:
        try:
            row, reason = parse_event(slug)
        except FetchFailed:
            failed.append(slug)
            continue
        except Blocked as b:
            _abort(f"eBilet bot 牆(DataDome)擋下整個 IP — 於 {b} 中止",
                   kept_n=len(kept), slugs_n=len(slugs))
        finally:
            time.sleep(4.0)   # polite gap between event pages (avoids 429)
        if row is None:
            dropped.append(reason)
        else:
            kept.append(row)

    # 抓取失敗率守門。2026-08-24:19 個 slug 有 11 個 fetch failed,poland.py 沒有
    # 任何守門,4 筆殘缺資料就這樣覆蓋掉 12 筆好資料、退出碼還是 0(線上少了 SIX /
    # Wicked / Beetlejuice / My Fair Lady / Next to Normal 等 8 檔)。
    # 守的是「抓取失敗率」而不是 `_guard.py` 的筆數跌幅:這個來源只有十幾筆,
    # FLOOR=50 的筆數守門對它永遠空轉(見 _guard.py 檔頭),失敗率才是對症的軸。
    if slugs and len(failed) / len(slugs) > MAX_FETCH_FAIL:
        _abort(f"{len(failed)}/{len(slugs)} 個事件頁抓不到"
               f"(>{MAX_FETCH_FAIL:.0%}) — 視為來源故障",
               kept_n=len(kept), slugs_n=len(slugs), failed=failed)

    shows = []
    coords_n = null_n = 0
    for s in kept:
        lat, lng = venue_coords(s["venue"])
        if lat is None:
            null_n += 1
        else:
            coords_n += 1
        sid = "pl-" + hashlib.md5(
            f"ebilet.pl|{s['title']}|{s['venue']}".encode()).hexdigest()[:8]
        shows.append({
            "id": sid, "title": s["title"], "title_en": "",
            "venue": s["venue"], "city": s["city"], "country": "Poland",
            "lat": lat, "lng": lng,
            "start_date": s["start"], "end_date": s["end"],
            "image": s["image"], "ticket_url": s["url"],
            "type": "tour", "verified": True, "source": "ebilet.pl",
        })

    out = {"meta": {"source": "ebilet.pl", "count": len(shows)}, "shows": shows}
    (DATA / "poland.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"\nWrote {len(shows)} -> data/poland.json", flush=True)
    print(f"  coords: {coords_n}   null-coords: {null_n}", flush=True)
    for s in shows:
        c = f"{s['lat']},{s['lng']}" if s["lat"] is not None else "no-coords"
        print(f"  keep: {s['title']} @ {s['venue']} ({s['city']}) "
              f"{s['start_date']}~{s['end_date']} [{c}]", flush=True)
    print(f"\nDropped {len(dropped)}:", flush=True)
    for d in dropped:
        print("  drop:", d, flush=True)


if __name__ == "__main__":
    main()
