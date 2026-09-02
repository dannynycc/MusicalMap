# -*- coding: utf-8 -*-
"""波蘭三大音樂劇院【官網】直抓 —— 取代對 eBilet 單一來源的依賴。

為什麼有這支
------------
2026-09-02 之前,波蘭資料 100% 只靠 `poland.py`(eBilet)一個來源:
  · Ticketmaster 的國家清單雖然含 "PL",實測抓到 **0 筆**波蘭資料,幫不上忙。
  · eBilet 有 DataDome bot 牆,且是**速率/信譽制**:一輪完整抓取會過,
    緊接著的第二輪就被擋(2026-09-02 在同一個家用 IP 實測重現)。
    CI 的共用機房 IP 信譽更差,2026-09-01 起連三班排程被擋,資料卡在 08-30。
  · 單一來源 + 會擋人的來源 = 波蘭隨時可能整批停更。

實測結論(2026-09-02):**劇院官網沒有任何 bot 牆**,而且比 eBilet 給的還完整
—— 例如 Syrena 官網上有 Heathers / Matylda / Wszyscy mówią o Jamie'm 等
eBilet 那批沒出現的製作;Buffo 官網連 Metro 35 週年巡演的外地場次都列。

三個來源與各自的解析依據
------------------------
  Teatr Syrena   teatrsyrena.pl        純 HTTP。每個製作一頁,頁內有「Najbliższe
                                       spektakle」區塊與 dd.mm.yyyy 場次日期。
                                       ⚠️ 每頁頁尾都有一個無關的 18.07.2002,
                                       直接取 min/max 會把開演日算成 2002 年。
  Teatr ROMA     bilety.teatrroma.pl   純 HTTP。售票子網域是月曆:?m=<月>&y=<年>,
                                       每天一個 <td data-dzien_data="YYYY-MM-DD"
                                       data-title="...19:00 WICKED...">。
                                       主站 /repertuar/ 是 2024 年的舊頁,不可用。
  Studio Buffo   studiobuffo.com.pl    需 Playwright(日期是 JS 算繪)。/repertuar
                                       是每月一張 table.repertuar,前面有月份標頭
                                       (「Wrzesień 2026」);列為
                                       「DD wk. | HH:MM | 劇名 | KUP BILET」,
                                       日期欄留空代表沿用上一列的日子。

音樂劇判定用 `_pl_musical.keep_for_venue_site()`,與 `poland.py`(eBilet)共用同一份
DROP/KEEP 清單,不另外複製一套 —— 兩邊規則若分岔,之後一定會出現「這齣在 A 來源
算音樂劇、在 B 來源不算」的鬼打牆。

⚠️ 底層的 `is_musical()` 回傳的是 **(keep, reason) 三態**,不是 bool。
   第一版這裡寫成 `if not is_musical(title)` —— 非空 tuple 永遠為真,
   **過濾器整個靜默失效**,演唱會與禮券會被當成音樂劇收進來。
   所以一律走 `keep_for_venue_site()`,不要直接用 `is_musical()`。

守門(沿用 poland.py 的精神:寧可資料舊一天,也不要用殘缺資料蓋掉好資料)
------------------------------------------------------------------
  · 每個來源都有 `MIN_EXPECTED` 下限。任何一個來源低於下限 → **整輪中止、不寫檔**、
    非零退出碼。單一劇院改版或暫時掛掉,不該讓另外兩間的好資料被半套結果覆蓋。
  · 這裡守的是「每個來源各自的產出量」,不是全檔筆數 —— 全檔筆數守門會被
    「Syrena 抓到 20 筆、ROMA 掛掉 0 筆」這種情況騙過去。

Output: data/poland_teatry.json     Run: python scrapers/poland_teatry.py
"""

import json
import re
import sys
import time

import urllib.request
from datetime import date, timedelta
from hashlib import md5
from pathlib import Path
from typing import NoReturn

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _pl_musical import keep_for_venue_site  # noqa: E402  與 poland.py 共用同一份規則

DATA = Path(__file__).resolve().parent.parent / "data"
OUT = DATA / "poland_teatry.json"

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/126.0 Safari/537.36",
      "Accept-Language": "pl-PL,pl;q=0.9,en;q=0.8"}

# 場館資料。座標沿用 data/poland.json 裡已經驗過的值(eBilet 那批),
# 不重新地理編碼——同一個場館兩套座標是地圖上最難查的一種錯。
VENUES = {
    "syrena": {"venue": "Teatr Syrena w Warszawie", "city": "Warszawa",
               "lat": 52.2196, "lng": 21.019},
    "roma":   {"venue": "Teatr Muzyczny ROMA", "city": "Warszawa",
               "lat": 52.2247, "lng": 21.0156},
    "buffo":  {"venue": "Teatr Studio Buffo w Warszawie", "city": "Warszawa",
               "lat": 52.227, "lng": 21.026},
}

# 每個來源至少要產出幾齣,低於就視為該來源故障。
# 取值依據 2026-09-02 首次實測:Syrena 9 / ROMA 1 / Buffo 4。
# 下限刻意抓得比實測低一截,留給正常檔期波動(某月剛好只剩一檔在檔期內)。
MIN_EXPECTED = {"syrena": 3, "roma": 1, "buffo": 2}

MONTHS_PL = {"stycze": 1, "luty": 2, "marzec": 3, "kwiecie": 4, "maj": 5,
             "czerwiec": 6, "lipiec": 7, "sierpie": 8, "wrzesie": 9,
             "paździer": 10, "pazdzier": 10, "listopad": 11, "grudzie": 12}

MONTHS_AHEAD = 10          # ROMA 月曆往前看幾個月
TODAY = date.today()
FLOOR_DATE = TODAY - timedelta(days=1)   # 早於昨天的日期一律視為雜訊(如頁尾的 2002)


class SourceFailed(Exception):
    """某個劇院官網抓不到/解析不出來。跟「這齣不是音樂劇」的合法丟棄不同型:
    合法丟棄是資料判斷,來源失敗是**我們沒看到資料**,不可以當成「沒有這齣」。"""


def get(url, tries=3, timeout=30):
    last = None
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers=UA)
            return urllib.request.urlopen(req, timeout=timeout).read().decode("utf-8", "replace")
        except Exception as e:                      # noqa: BLE001
            last = e
            if i < tries - 1:
                time.sleep(2.0 * (i + 1))
    raise SourceFailed(f"{url} — {last}")


def flat(html):
    x = re.sub(r"<script.*?</script>|<style.*?</style>", " ", html, flags=re.S)
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", x))


def _row(key, title, dates, ticket_url, image=""):
    """把一齣戲的所有場次日期收斂成一筆 start/end 記錄。"""
    dates = sorted(set(dates))
    v = VENUES[key]
    ident = md5(f"{key}|{title}".encode("utf-8")).hexdigest()[:8]
    return {"id": f"plt-{ident}", "title": title, "title_en": "",
            "venue": v["venue"], "city": v["city"], "country": "Poland",
            "lat": v["lat"], "lng": v["lng"],
            "start_date": dates[0].isoformat(), "end_date": dates[-1].isoformat(),
            "image": image, "ticket_url": ticket_url,
            "type": "tour", "verified": True, "source": f"{key}.official"}


def _clean_title(t):
    """劇名正規化:去掉票務用語與『musical』前後綴,保留可辨識的本名。"""
    t = re.sub(r"\s*[-–—]\s*(musical\s*w\s*3D.*|trasa koncertowa.*)$", "", t, flags=re.I)
    t = re.sub(r"^\s*musical\s+", "", t, flags=re.I)
    t = re.sub(r"\s+W\s+BUFFO\s*$", "", t, flags=re.I)
    return re.sub(r"\s+", " ", t).strip(" -–—·|")


# --------------------------------------------------------------------------
# Teatr Syrena — 純 HTTP,一齣一頁
# --------------------------------------------------------------------------
def scrape_syrena():
    home = get("https://teatrsyrena.pl/")
    links = sorted({u.rstrip("/") + "/" for u in
                    re.findall(r'href="(https://teatrsyrena\.pl/[^"#?]+)"', home)})
    # 排除明顯不是製作頁的區塊(其餘靠「頁內是否有 Najbliższe spektakle」判定)
    skip = ("wp-content", "/bilety", "/edukacja", "/historia", "/oferty", "/warsztaty",
            "/aktualnosci", "/kontakt", "/faq", "/en/", "/polityka", "/regulamin",
            "/materialy", "/zamowienia", "/standardy", "/ostrzezenia", "/od-kulis",
            "/uczymy", "/urodziny", "/repertuar", "/spektakle", "/wznowilismy")
    cand = [u for u in links if not any(s in u for s in skip)]

    rows, failed = [], []
    for u in cand:
        try:
            html = get(u, tries=2, timeout=25)
        except SourceFailed:
            failed.append(u)
            continue
        finally:
            time.sleep(1.0)
        txt = flat(html)
        # 製作頁的判準:有「近期場次」預覽,或有訂票用的日期選單
        if "Najbliższe spektakle" not in txt and "godzina spektaklu" not in txt:
            continue
        mt = re.search(r"<title>(.*?)</title>", html, re.S)
        raw = mt.group(1) if mt else ""
        title = _clean_title(re.sub(r"\s*[-–|].*$", "", raw))   # 去掉「劇名 - 劇院名」的後半
        if not title or not keep_for_venue_site(title):
            continue
        # 日期來源用【訂票日期選單】(「Data i godzina spektaklu: Wybierz …」),
        # 那裡是完整的 dd.mm.yyyy 場次清單。
        # ⚠️ 不要用「Najbliższe spektakle」那一段:它只印 dd.mm(沒有年份),
        #    而且只列最近幾場 —— 第一版用它,結果一齣都抓不到。
        # ⚠️ 也不要對整頁取 min/max:頁尾有個無關的 18.07.2002。
        seg = txt.split("godzina spektaklu", 1)[1] if "godzina spektaklu" in txt else ""
        ds = []
        for d, m, y in re.findall(r"\b(\d{1,2})\.(\d{1,2})\.(20\d\d)\b", seg):
            try:
                dt = date(int(y), int(m), int(d))
            except ValueError:
                continue
            if dt >= FLOOR_DATE:
                ds.append(dt)
        if not ds:
            continue
        img = ""
        mi = re.search(r'<meta[^>]+property="og:image"[^>]+content="([^"]+)"', html)
        if mi:
            img = mi.group(1)
        rows.append(_row("syrena", title, ds, u, img))

    if failed and len(failed) > max(2, len(cand) // 4):
        raise SourceFailed(f"Syrena {len(failed)}/{len(cand)} 頁抓不到")
    return rows


# --------------------------------------------------------------------------
# Teatr Muzyczny ROMA — 純 HTTP,售票子網域的月曆
# --------------------------------------------------------------------------
def scrape_roma():
    by_title = {}
    seen_any = False
    for i in range(MONTHS_AHEAD):
        y = TODAY.year + (TODAY.month - 1 + i) // 12
        m = (TODAY.month - 1 + i) % 12 + 1
        try:
            html = get(f"https://bilety.teatrroma.pl/?m={m}&y={y}", tries=2, timeout=30)
        except SourceFailed:
            continue
        finally:
            time.sleep(1.0)
        # 每一天一個 td:data-dzien_data 是 ISO 日期,data-title 內含當天的節目
        for iso, tip in re.findall(r'data-dzien_data="(20\d\d-\d\d-\d\d)"[^>]*'
                                   r'data-title="(.*?)"', html, re.S):
            seen_any = True
            try:
                dt = date.fromisoformat(iso)
            except ValueError:
                continue
            if dt < FLOOR_DATE:
                continue
            for t in re.findall(r"\d{1,2}:\d{2}\s*([^<]{2,80})", tip.replace("&nbsp;", " ")):
                title = _clean_title(re.sub(r"&[a-z]+;", " ", t))
                if not title or not keep_for_venue_site(title):
                    continue
                by_title.setdefault(title, []).append(dt)
    if not seen_any:
        raise SourceFailed("ROMA 月曆沒有解析到任何 data-dzien_data 欄位(版面可能改了)")
    return [_row("roma", t, ds, "https://bilety.teatrroma.pl/")
            for t, ds in by_title.items()]


# --------------------------------------------------------------------------
# Studio Buffo — 需 Playwright(日期是 JS 算繪)
# --------------------------------------------------------------------------
def scrape_buffo():
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as e:
        raise SourceFailed(f"Buffo 需要 playwright:{e}") from e

    with sync_playwright() as pw:
        br = pw.chromium.launch(headless=True,
                                args=["--disable-blink-features=AutomationControlled"])
        pg = br.new_page(locale="pl-PL")
        try:
            pg.goto("https://www.studiobuffo.com.pl/repertuar",
                    wait_until="domcontentloaded", timeout=45000)
            pg.wait_for_timeout(2500)
            tables = pg.evaluate(r"""() => [...document.querySelectorAll('table.repertuar')]
              .map(tb => {
                let hdr='', n=tb;
                while (n && !hdr) { n = n.previousElementSibling || n.parentElement;
                  if (n && n.innerText && /20\d\d/.test(n.innerText.slice(0,40)))
                    hdr = n.innerText.split('\n')[0].trim(); }
                const rows = [...tb.querySelectorAll('tr')].map(tr =>
                  [...tr.querySelectorAll('td,th')].map(td =>
                    td.innerText.replace(/\s+/g,' ').trim()));
                return {hdr, rows};
              })""")
        finally:
            br.close()

    if not tables:
        raise SourceFailed("Buffo 沒有找到 table.repertuar(版面可能改了)")

    by_title, cur_day = {}, None
    for tb in tables:
        hdr = (tb.get("hdr") or "").lower()
        ym = re.search(r"20\d\d", hdr)
        mon = next((v for k, v in MONTHS_PL.items() if k in hdr), None)
        if not (ym and mon):
            continue
        year = int(ym.group(0))
        for cells in tb.get("rows") or []:
            if len(cells) < 3:
                continue
            dm = re.match(r"\s*(\d{1,2})\b", cells[0] or "")
            if dm:
                cur_day = int(dm.group(1))          # 空的日期欄沿用上一列
            if cur_day is None:
                continue
            raw = cells[2] if len(cells) > 2 else ""
            # ⚠️ Buffo 的節目表【連外地巡演場次也列】,例如
            #   「Musical METRO - trasa koncertowa na 35-lecie musicalu - Arena Jaskółka Tarnów」。
            # 這些不是在華沙 Buffo 演的。必須在 _clean_title 之前擋掉 —— 清理會把
            # 「- trasa koncertowa …」整段剝掉,剝完就變成「METRO」而被【併進華沙那一筆】,
            # 把塔爾努夫的場次標到華沙的座標上(首次實測 METRO 的結束日因此從
            # 2026-12-13 被拉長到 2027-06-05)。巡演場次由 eBilet 那條路徑各自建場館。
            if re.search(r"trasa koncertowa|tourn?ee", raw, re.I):
                continue
            title = _clean_title(raw)
            if not title or not keep_for_venue_site(title):
                continue
            try:
                dt = date(year, mon, cur_day)
            except ValueError:
                continue
            if dt >= FLOOR_DATE:
                by_title.setdefault(title, []).append(dt)
    return [_row("buffo", t, ds, "https://www.studiobuffo.com.pl/repertuar")
            for t, ds in by_title.items()]


def _abort(why) -> NoReturn:
    print(f"\n[poland_teatry] ABORT: {why}", flush=True)
    print("[poland_teatry] data/poland_teatry.json **維持原樣**"
          "(舊資料仍完整,build_shows 照常拿得到)。", flush=True)
    sys.exit(1)


def main():
    got, errs = {}, []
    for key, fn in (("syrena", scrape_syrena), ("roma", scrape_roma), ("buffo", scrape_buffo)):
        try:
            rows = fn()
        except SourceFailed as e:
            errs.append(f"{key}: {e}")
            got[key] = []
        else:
            got[key] = rows
        print(f"  {key:8s} {len(got[key]):2d} 齣", flush=True)

    thin = [f"{k}({len(v)} < {MIN_EXPECTED[k]})" for k, v in got.items()
            if len(v) < MIN_EXPECTED[k]]
    if thin:
        _abort("以下來源產出低於下限:" + ", ".join(thin) +
               ("  |  錯誤:" + "; ".join(errs) if errs else ""))

    rows = [r for v in got.values() for r in v]
    rows.sort(key=lambda r: (r["venue"], r["start_date"], r["title"]))
    OUT.write_text(json.dumps({"meta": {"source": "官方劇院網站(Syrena / ROMA / Buffo)",
                                        "count": len(rows)}, "shows": rows},
                              ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\nWrote {len(rows)} shows -> {OUT}", flush=True)
    for r in rows:
        print(f"  {r['title'][:40]:42s} {r['venue'][:30]:32s} "
              f"{r['start_date']} ~ {r['end_date']}", flush=True)


if __name__ == "__main__":
    main()
