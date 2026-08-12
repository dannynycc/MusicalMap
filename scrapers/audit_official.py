"""官方網站(official_sites.json)體檢 — build 後對照 shows.json。

動機(2026-07-09 星光快車事件):波鴻星光快車的條目只有 uk 鍵,de 區駐演對不到就整個
不顯示,而且沒有任何機制會發現。使用者警告:「有些劇針對不同城市有不同官網,要非常小心」。

2026-08-12 追加存活檢查(--check-live):原本只驗結構(key 對不對、地區有沒有漏),
從不驗「這個網址是不是還活著」。實際掃過一輪,363 條裡有 9 條爛掉 ——
hairspraythemusical.co.uk 已轉手成足球俱樂部、waitressthemusical.com.au 變健身房、
fiddlermusical.com 與 ghostthemusical.com 是 GoDaddy 停放頁、
rockofagesmusical.co.uk 與 beetlejuicethemusical.com.au 直接 NXDOMAIN。
劇目的官網域名會隨製作結束而過期被別人買走,這是會持續復發的一類,所以要常態掃。

判準只收**高信心**訊號(這輪 15 個可疑裡有 6 個是誤報,教訓寫死在這):
  · 403 / 逾時 **不算死** —— Cloudflare 機器人牆對 curl 與真 headless Chrome 都回 403,
    charlie/don juan/thelma&louise/tina/ride the cyclone 五個都是這型,網站其實活得好好的。
  · 轉到別的網域也**不一定**是壞 —— jesuschristsuperstar.com→andrewlloydwebber.com、
    lion king es→stage.es、mj au→michaelcassel.com 都是製作方/場館營運商的正常整併。
  只認:DNS 查不到、解析到 127.0.0.1/0.0.0.0、以及頁面出現停放商的招牌字樣。

四項檢查(都只 ::warning 不擋 build):
1. region-miss:resident 劇有條目、但該地區既無地區鍵也無 global → 該卡完全沒官網
   (星光快車型漏洞;tour 不查,巡演station多為一次性)。
2. 授權目錄頁污染:Concord/MTI/劇本授權商的頁面不是「官方製作網站」,任何鍵掛這類
   網域都算髒資料(2026-07-09 清過 14 條,防再犯)。
3. 大市場 resident 無條目統計:非中國(中國經抽查證實無獨立官網生態,見 official_sites
   _note_cn)的 resident 劇完全沒條目的數量,異常升高=新來源進來沒補官網。
4. 連結存活(僅 --check-live):域名消失 / 指向 localhost / 域名停放頁。

Run: python scrapers/audit_official.py            # 結構檢查,不連網
     python scrapers/audit_official.py --check-live  # 額外做連線檢查(CI 每日跑)
"""

import json
import socket
import sys
import io
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
DATA = Path(__file__).resolve().parent.parent / "data"

LICENSING_DOMAINS = ("concordtheatricals", "mtishows.com", "broadwaylicensing",
                     "theatricalrights", "rnh.com")

# 完全沒條目的可容忍上限(2026-07-09 補完後基線=3 組:Diana São Paulo、
# Jack and the Beanstalk London、サンレッドショー東京——都查證過真的沒官網)。超過=有新缺口。
NO_ENTRY_CEILING = 15


def region(country):
    c = (country or "").strip().lower()
    c = {"usa": "us", "united states": "us", "uk": "gb", "united kingdom": "gb"}.get(c, c)
    if c in ("us", "canada"):
        return "us"
    if c in ("gb", "ireland"):
        return "uk"
    return {"australia": "au", "germany": "de", "japan": "jp", "france": "fr",
            "spain": "es", "netherlands": "nl", "mexico": "mx", "austria": "at",
            "switzerland": "ch", "china": "cn", "south korea": "kr"}.get(c, c)


# 域名停放商的招牌字樣。只有這些才算「死」——一般的 403/逾時是機器人牆,不算。
# GoDaddy 的停放頁對 curl 只回 114 bytes 的 JS 跳板(真正的 "parked free, courtesy of
# GoDaddy" 字樣要執行 JS 才看得到),所以跳板本身才是可靠特徵。
PARKED_MARKERS = ("is parked free, courtesy of godaddy", "hugedomains.com",
                  "sedoparking.com", "buy this domain", "this domain may be for sale",
                  "domain is for sale", "afternic.com", 'location.href="/lander"',
                  "location.href='/lander'")
DEAD_IPS = {"127.0.0.1", "0.0.0.0", "::1"}
# 劇場詞彙(多語)。官網理應至少出現一個;一個都沒有=這個域名已經不是劇場的了。
THEATRE_WORDS = ("musical", "theatre", "theater", "tickets", "box office", "cast",
                 "performance", "on stage", "broadway", "west end", "teatro", "théâtre",
                 "musicals", "spektakel", "espectáculo", "ミュージカル", "劇場", "音乐剧",
                 "뮤지컬", "voorstelling", "föreställning")
STOP = {"the", "and", "a", "an", "of", "on", "in", "le", "la", "les", "el", "der", "die", "das"}


def _host(u):
    """原始主機名。DNS 查詢一定要用這個 —— 裸網域常常沒有 A 記錄,只有 www. 子網域有
    (www.umegei.com 活著、umegei.com 無 A 記錄;若拿剝掉 www. 的裸網域去查會誤判成死站)。"""
    try:
        return u.split("//", 1)[1].split("/", 1)[0].split(":")[0].lower()
    except IndexError:
        return ""


def _site(u):
    """比對用的網域(去掉 www. 前綴,讓 www.a.com 與 a.com 視為同一站)。不可拿去查 DNS。"""
    h = _host(u)
    return h[4:] if h.startswith("www.") else h


def liveness(item):
    """回傳 (key, url, 死因) —— 活著或無法斷定時死因為 None。

    寧可漏抓也不誤報:403、逾時、連不上一律不下判斷(那是機器人牆或一時的網路問題,
    2026-08-12 那輪 15 個可疑裡有 5 個是這型的假警報)。
    """
    key, url = item
    host = _host(url)
    if not host:
        return key, url, "網址格式不對"
    try:
        ips = {ai[4][0] for ai in socket.getaddrinfo(host, None)}
    except socket.gaierror:
        return key, url, "DNS 查不到這個域名(NXDOMAIN / 無 A 記錄)"
    except Exception:
        return key, url, None
    if ips and ips <= DEAD_IPS:
        return key, url, f"域名解析到 {sorted(ips)}(等於沒指向任何主機)"
    try:
        from curl_cffi import requests as creq
        r = creq.get(url, impersonate="chrome124", timeout=30)
        body = (r.text or "")[:8000].lower()
        final = _site(str(r.url))
        size = len(r.content)
    except Exception:
        return key, url, None          # 連不上不下判斷

    for m in PARKED_MARKERS:
        if m in body:
            return key, url, "域名停放頁(已過期被停放商接管)"
    if r.status_code == 200 and size < 400 and final == _site(url):
        return key, url, f"回應只有 {size} bytes 的空殼(疑似停放/廢棄)"

    # 域名被別人買走:跨網域 + 整頁找不到本劇名 + 整頁沒有任何劇場詞彙,三個同時成立才算。
    # (只有跨網域會誤殺 jesuschristsuperstar→andrewlloydwebber、lion king es→stage.es
    #  這類製作方/場館營運商的正常整併,所以三重條件缺一不可。)
    if final and final != _site(url):
        show = key.split("[")[0].strip().lower()
        toks = [w for w in show.replace("-", " ").split() if len(w) >= 4 and w not in STOP]
        hay = body + " " + final
        if toks and not any(t in hay for t in toks) and not any(w in body for w in THEATRE_WORDS):
            return key, url, f"域名疑似已轉手 → {final}(整頁既無本劇名也無任何劇場詞彙)"
    return key, url, None


def check_live(OFF):
    items = [(f"{g}[{reg}]", url) for g, sites in OFF.items()
             if isinstance(sites, dict)
             for reg, url in sites.items()
             if isinstance(url, str) and url.startswith("http")]
    with ThreadPoolExecutor(max_workers=12) as ex:
        res = list(ex.map(liveness, items))
    dead = [r for r in res if r[2]]
    for key, url, why in dead:
        print(f"::warning::official dead-link: {key} = {url} — {why}")
    print(f"  存活檢查:{len(items)} 條,{'全過 ✓' if not dead else f'{len(dead)} 條已失效'}")
    return len(dead)


def main():
    shows = json.loads((DATA / "shows.json").read_text(encoding="utf-8"))["shows"]
    OFF = {k: v for k, v in
           json.loads((DATA / "official_sites.json").read_text(encoding="utf-8")).items()
           if not k.startswith("_")}
    warn = 0

    # 0. key 有效性:official_sites 以 group 為 key,key 對不上任何現有 group=官網掛不上
    #    (2026-07-14 使用者抓到 & Juliet:官網三條齊全,key 卻寫成舊制「juliet」,對不上
    #    group「and juliet」——與 local_titles 同型。有「近似 group」的失效 key 最可疑=
    #    多半是 group_key 演進後沒跟上;完全無近似的=下檔劇殘鍵,合法保留不吵)
    groups = {s.get("group") for s in shows}
    for k in OFF:
        if k in groups:
            continue
        close = [g for g in groups if g and (k in g or g in k)]
        if close:
            warn += 1
            print(f"::warning::official dead-key: {k!r} 對不上任何 group,近似 {close[:3]} — 官網掛不上,疑 key 過時")

    # 1. region-miss(resident 有條目但對不到 URL)
    seen = set()
    for s in shows:
        if s.get("type") == "tour":
            continue
        g = s.get("group")
        sites = OFF.get(g)
        if not sites:
            continue
        reg = region(s.get("country"))
        if not (sites.get(reg) or sites.get("global")) and (g, reg) not in seen:
            seen.add((g, reg))
            warn += 1
            print(f"::warning::official region-miss: {g} [{reg}] 有條目但該地區對不到官網"
                  f"(現有鍵 {list(sites)})— 該地區駐演卡片將沒有官網連結")

    # 2. 授權目錄頁污染
    for g, sites in OFF.items():
        for reg, url in sites.items():
            if isinstance(url, str) and any(dom in url for dom in LICENSING_DOMAINS):
                warn += 1
                print(f"::warning::official licensing-page: {g}[{reg}] = {url} 是授權商目錄頁,不是官方製作網站")

    # 3. 非中國 resident 無條目數量
    no_entry = {s.get("group") for s in shows
                if s.get("type") != "tour" and s.get("country") != "China"
                and s.get("group") not in OFF}
    if len(no_entry) > NO_ENTRY_CEILING:
        warn += 1
        sample = ", ".join(sorted(no_entry)[:8])
        print(f"::warning::official no-entry: 非中國 resident 無官網條目 {len(no_entry)} 組"
              f"(基線上限 {NO_ENTRY_CEILING})— 可能有新來源沒補官網。例: {sample}")

    # 4. 連結存活(要連網,只在明確要求時做)
    if "--check-live" in sys.argv:
        warn += check_live(OFF)

    print(f"official audit: {len(OFF)} 條目,{'全過 ✓' if warn == 0 else f'{warn} 項告警'}"
          f"(非中國 resident 無條目 {len(no_entry)} 組)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
