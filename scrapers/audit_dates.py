"""日期結構體檢(2026-08-12)。

動機:日期正確性是本站最高優先(演出日期錯 = 使用者白跑一趟),但先前**沒有任何
跨全庫的結構性日期檢查**——只有 audit_sample_truth 每天隨機抽 ~15 筆 TM 卡打 API 對照,
覆蓋率極低且只涵蓋 Ticketmaster 來源。這支補上不連網、瞬間跑完的全庫不變式檢查。

檢查的都是「不需要外部真相就能斷定不對」的結構問題:
1. 日期格式不是 YYYY-MM-DD —— 前端 localDate() 會解析失敗,卡片直接壞掉。
2. 閉幕日早於開演日 —— 一定是解析錯。
3. 已閉幕卻還在檔,且超過寬限期 —— build_shows 只留 3 天防時區邊界;超過=丟棄規則壞了。
4. 完全沒有開演日 —— 無法誠實放上時間軸(2026-08-12:4 筆在 13 個月全部出現、日期欄
   空白;前端已改成只在當月出現並顯示「檔期未公布」,但資料層仍該追回真實檔期)。
5. 開演日在 3 年後 —— 幾乎必然是解析錯(年份抓錯位)。
6. 檔期超過 400 天卻沒標 end_rolling —— 多半是把「訂票視野最後一天」當成閉幕日
   (booking horizon ≠ 閉幕日)。有既有積欠,設上限只擋惡化。

Run: python scrapers/audit_dates.py
"""

import io
import json
import re
import sys
from datetime import date, timedelta
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
DATA = Path(__file__).resolve().parent.parent / "data"

ISO = re.compile(r"^\d{4}-\d{2}-\d{2}$")
GRACE_DAYS = 3          # 與 build_shows.py 的丟棄寬限一致
LONGRUN_DAYS = 400
# 既有積欠上限(2026-08-12 基線 12,含 Interpark/維也納那批訂票視野型)。只擋惡化。
LONGRUN_CEILING = 15
NOSTART_CEILING = 6     # 基線 4


def d(s):
    try:
        return date.fromisoformat(str(s))
    except Exception:
        return None


def main():
    shows = json.loads((DATA / "shows.json").read_text(encoding="utf-8"))["shows"]
    today = date.today()
    warn = 0

    bad_fmt = [s for s in shows
               if (s.get("start_date") and not ISO.match(str(s["start_date"])))
               or (s.get("end_date") and not ISO.match(str(s["end_date"])))]
    for s in bad_fmt:
        warn += 1
        print(f"::warning::date format: {s.get('title')!r} @ {s.get('venue')} "
              f"start={s.get('start_date')!r} end={s.get('end_date')!r} — 前端會解析失敗")

    for s in shows:
        a, b = d(s.get("start_date")), d(s.get("end_date"))
        if a and b and b < a:
            warn += 1
            print(f"::warning::date inverted: {s.get('title')!r} @ {s.get('venue')} "
                  f"{s['start_date']} ~ {s['end_date']}(閉幕早於開演)source={s.get('source')}")

    cutoff = today - timedelta(days=GRACE_DAYS)
    for s in shows:
        b = d(s.get("end_date"))
        if b and not s.get("end_rolling") and b < cutoff:
            warn += 1
            print(f"::warning::date ended-still-listed: {s.get('title')!r} @ {s.get('venue')} "
                  f"結束於 {s['end_date']}({(today - b).days} 天前,寬限 {GRACE_DAYS} 天)"
                  f" — build_shows 的丟棄規則可能壞了 source={s.get('source')}")

    nostart = [s for s in shows if not s.get("start_date")]
    if len(nostart) > NOSTART_CEILING:
        warn += 1
        print(f"::warning::date no-start: {len(nostart)} 筆沒有開演日(基線上限 {NOSTART_CEILING})"
              f" — 例:{', '.join(repr(s.get('title')) for s in nostart[:5])}")

    horizon = today + timedelta(days=365 * 3)
    for s in shows:
        a = d(s.get("start_date"))
        if a and a > horizon:
            warn += 1
            print(f"::warning::date far-future: {s.get('title')!r} @ {s.get('venue')} "
                  f"開演 {s['start_date']}(3 年後,疑年份解析錯)source={s.get('source')}")

    longrun = [s for s in shows
               if d(s.get("start_date")) and d(s.get("end_date")) and not s.get("end_rolling")
               and (d(s["end_date"]) - d(s["start_date"])).days > LONGRUN_DAYS]
    if len(longrun) > LONGRUN_CEILING:
        warn += 1
        for s in longrun[:8]:
            span = (d(s["end_date"]) - d(s["start_date"])).days
            print(f"::warning::date long-span: {s.get('title')!r} {s['start_date']} ~ "
                  f"{s['end_date']}({span} 天)未標 end_rolling — 疑把訂票視野當閉幕日 "
                  f"source={s.get('source')}")
        print(f"::warning::date long-span 共 {len(longrun)} 筆(基線上限 {LONGRUN_CEILING})")

    print(f"date audit: {len(shows)} 筆,{'全過 ✓' if warn == 0 else f'{warn} 項告警'}"
          f"(無開演日 {len(nostart)},超長檔期未標 rolling {len(longrun)})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
