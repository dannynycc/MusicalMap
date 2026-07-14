"""官方網站(official_sites.json)體檢 — build 後對照 shows.json。

動機(2026-07-09 星光快車事件):波鴻星光快車的條目只有 uk 鍵,de 區駐演對不到就整個
不顯示,而且沒有任何機制會發現。使用者警告:「有些劇針對不同城市有不同官網,要非常小心」。

三項檢查(都只 ::warning 不擋 build):
1. region-miss:resident 劇有條目、但該地區既無地區鍵也無 global → 該卡完全沒官網
   (星光快車型漏洞;tour 不查,巡演station多為一次性)。
2. 授權目錄頁污染:Concord/MTI/劇本授權商的頁面不是「官方製作網站」,任何鍵掛這類
   網域都算髒資料(2026-07-09 清過 14 條,防再犯)。
3. 大市場 resident 無條目統計:非中國(中國經抽查證實無獨立官網生態,見 official_sites
   _note_cn)的 resident 劇完全沒條目的數量,異常升高=新來源進來沒補官網。

Run: python scrapers/audit_official.py
"""

import json
import sys
import io
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

    print(f"official audit: {len(OFF)} 條目,{'全過 ✓' if warn == 0 else f'{warn} 項告警'}"
          f"(非中國 resident 無條目 {len(no_entry)} 組)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
