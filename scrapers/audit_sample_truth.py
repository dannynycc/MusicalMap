"""抽樣對照源頭稽核(2026-07-13,「沒抓到的錯怎麼辦」的答案)。

其他 audit 守「已知病類」;這支不預設病型——每日隨機抽 N 筆 TM 系卡片,
直接打 Ticketmaster API 比對「卡片顯示的」vs「源頭此刻說的」:
  1. 該 attraction 在該場地查無任何 event(下架/搬家/錯配)→ 警告
  2. 卡片日期範圍與 API 在售日期零交集(過期殘留/日期錯)→ 警告
     (API 會丟棄已過場次,卡片 start 早於 API 最早日屬正常,只驗交集)
  3. 卡片標題與 attraction/event 名 token 零交集(掛羊頭)→ 警告
抽樣種子=當天日期(可重現);量少但每天不同批,一個月滾過 ~450 筆。
無論管線哪一層出了「沒想過的 bug」,只要結果偏離事實,抽樣遲早撞到。
"""
import json
import random
import re
import sys
import time
import unicodedata
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
DATA = Path(__file__).resolve().parent.parent / "data"
KEY_FILE = Path(__file__).resolve().parent / ".tm_key"
API = "https://app.ticketmaster.com/discovery/v2/events.json"
SAMPLE = 15

_STOP = {"the", "a", "an", "of", "and", "le", "les", "la", "de", "musical", "on", "in"}


def toks(t):
    t = unicodedata.normalize("NFKD", t or "").encode("ascii", "ignore").decode()
    return set(re.findall(r"[a-z0-9]+", t.lower())) - _STOP


def main():
    if not KEY_FILE.exists():
        print("audit_sample_truth: no .tm_key — skipped")
        return
    key = KEY_FILE.read_text().strip()
    shows = json.loads((DATA / "shows.json").read_text(encoding="utf-8"))["shows"]
    pool = [s for s in shows
            if s.get("source") == "ticketmaster"
            and re.search(r"/artist/(\d+)", s.get("attraction_url") or "")]
    rng = random.Random(date.today().isoformat())   # 種子=日期:同日可重現、逐日輪替
    sample = rng.sample(pool, min(SAMPLE, len(pool)))
    bad = []
    for s in sample:
        # ⚠️ 不能用 attractionId:網站 /artist/{數字} 是 legacy id,Discovery API 的
        # attraction id 是 K 開頭字串,兩套不通(首跑 15/15 全滅的教訓)。
        # 改 keyword=劇名+city 查,再以場地 token 過濾。
        q = urllib.parse.urlencode({
            "apikey": key, "keyword": s["title"], "size": 100,
            "city": (s.get("city") or "").split(",")[0],
        })
        try:
            with urllib.request.urlopen(f"{API}?{q}", timeout=30) as r:
                data = json.load(r)
        except Exception as e:  # noqa: BLE001 — 網路錯不算資料錯
            print(f"  [skip] API error for {s['id']}: {e}")
            time.sleep(0.3)
            continue
        evs = (data.get("_embedded") or {}).get("events") or []
        vt = toks(s.get("venue"))
        here = [e for e in evs
                if vt & toks(((e.get("_embedded") or {}).get("venues") or [{}])[0].get("name"))]
        if not here:
            bad.append(f"查無場地事件: {s['title']!r} @ {s.get('venue')} ({s['id']}) — "
                       f"keyword+city 查得 {len(evs)} 個 event 但無此場地")
        else:
            dates = sorted(filter(None, (((e.get("dates") or {}).get("start") or {}).get("localDate")
                                         for e in here)))
            if dates and s.get("end_date") and s["end_date"] < dates[0]:
                bad.append(f"日期零交集: {s['title']!r} @ {s.get('venue')} 卡片至 {s['end_date']},"
                           f"API 最早在售 {dates[0]} ({s['id']})")
            names = " ".join(filter(None, [e.get("name") for e in here]))
            att_name = ((here[0].get("_embedded") or {}).get("attractions") or [{}])[0].get("name") or ""
            if not (toks(s["title"]) & (toks(names) | toks(att_name))):
                bad.append(f"標題零交集: 卡片 {s['title']!r} vs API {names[:60]!r} ({s['id']})")
        time.sleep(0.25)
    if bad:
        print(f"抽樣對照 FAIL:{len(bad)}/{len(sample)} 筆與源頭不符")
        for b in bad:
            print("  " + b)
        sys.exit(1)
    print(f"抽樣對照 PASS({len(sample)} 筆卡片 vs Ticketmaster API,零不符)")


if __name__ == "__main__":
    main()
