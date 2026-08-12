# -*- coding: utf-8 -*-
"""手動劇目(data/manual.json)新鮮度守門。

hardcode 進 manual.json 的劇(反爬市場:巴西/阿根廷/東南亞 Akamai 等無法自動抓)
不會像 scraper 來源那樣自動更新,容易過期或填錯。此腳本抓三類問題:

  1. STALE  — end_date 已過(劇已落幕,應移除或更新檔期)→ 擋 CI
  2. URGENT — 現正上演或 SOON_DAYS 天內開演,且 _checked 逾期 → 最可能出錯又最傷
  3. UNCHECKED — 其餘 _checked 逾期者(遠期檔期,風險較低)

第 2 類是 2026-08-12 補的。起因:上海《劇院魅影》檔期被延長(11-29 → 12-13),
但條目仍在檔期內、`_checked` 只有 61 天 —— 舊門檻 120 天完全抓不到,錯誤日期就這樣
掛在站上。「已落幕」只抓得到演完的,抓不到「還在演但日期已經變了」這一型。

用法:
  python scrapers/audit_manual.py            # 用系統時鐘當今天
  python scrapers/audit_manual.py 2026-06-15 # 指定今天(避免時鐘問題)

CI 可掛此腳本;發現 STALE 時回傳非零 exit code。
"""
import sys, io, json
from datetime import date, datetime
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

# _checked 超過這天數就提醒重新查證。2026-08-12 由 120 收緊到 45:上海魅影的檔期
# 在第 61 天被發現已經改過,120 天的門檻等於放行了兩個月的錯誤日期。
STALE_DAYS = 45
# 「現正上演 / 這麼多天內開演」= 使用者最可能照著這個日期出門的區間
SOON_DAYS = 90

DATA = Path(__file__).resolve().parent.parent / "data"


def parse_d(s):
    try:
        return datetime.strptime(s, "%Y-%m-%d").date()
    except (TypeError, ValueError):
        return None


def main():
    today = (parse_d(sys.argv[1]) if len(sys.argv) > 1 else None) or date.today()
    m = json.loads((DATA / "manual.json").read_text(encoding="utf-8"))
    shows = m["shows"] if isinstance(m, dict) else m

    stale, urgent, unchecked = [], [], []
    for s in shows:
        end = parse_d(s.get("end_date"))
        if end and end < today:
            stale.append((s.get("id"), s.get("title"), s.get("end_date")))
            continue                       # 已落幕就不必再談查證新鮮度
        chk = parse_d(s.get("_checked"))
        # _checked 缺漏視為從未查證(不是「不用查」)
        age = (today - chk).days if chk else None
        overdue = (age is None) or (age > STALE_DAYS)
        if not overdue:
            continue
        start = parse_d(s.get("start_date"))
        # 現正上演(已開演且未落幕)或即將開演 → 使用者可能正照著這個日期出門
        playing_or_soon = (start is None) or ((start - today).days <= SOON_DAYS)
        row = (s.get("id"), s.get("title"), s.get("_checked"), age,
               s.get("start_date"), s.get("end_date"))
        (urgent if playing_or_soon else unchecked).append(row)

    print(f"audit_manual: {len(shows)} manual shows | today={today}")
    if stale:
        print(f"\n  ⚠ {len(stale)} STALE (end_date 已過 → 移除或更新檔期):")
        for i, t, e in stale:
            print(f"      {e}  {t}  [{i}]")
    if urgent:
        print(f"\n  ‼ {len(urgent)} URGENT — 現正上演或 {SOON_DAYS} 天內開演,"
              f"但 _checked 逾期(>{STALE_DAYS}d)。這一型最可能已被延長/改期/取消:")
        for i, t, c, a, sd, ed in urgent:
            print(f"      _checked {c} ({'從未' if a is None else str(a) + 'd'})  "
                  f"{sd}~{ed}  {t}  [{i}]")
    if unchecked:
        print(f"\n  · {len(unchecked)} 遠期檔期需重新查證 (_checked > {STALE_DAYS} 天):")
        for i, t, c, a, sd, ed in unchecked:
            print(f"      _checked {c} ({'從未' if a is None else str(a) + 'd'})  "
                  f"{sd}~{ed}  {t}  [{i}]")
    if not stale and not urgent and not unchecked:
        print("  OK: 無過期、無逾期未查證項目")

    # CI: 只有 stale(資料已確定錯了)擋 CI;URGENT/UNCHECKED 是「該去查」的提醒,
    # 不代表資料一定錯,擋下來會讓 CI 長期紅燈而失去意義。
    return 1 if stale else 0


if __name__ == "__main__":
    sys.exit(main())
