# -*- coding: utf-8 -*-
"""手動劇目(data/manual.json)新鮮度守門。

hardcode 進 manual.json 的劇(反爬市場:巴西/阿根廷/東南亞 Akamai 等無法自動抓)
不會像 scraper 來源那樣自動更新,容易過期或填錯。此腳本抓兩類問題:

  1. STALE  — end_date 已過(劇已落幕,應移除或更新檔期)
  2. UNCHECKED — _checked 距今超過 STALE_DAYS 天(該重新查證日期/售票連結)

用法:
  python scrapers/audit_manual.py            # 用系統時鐘當今天
  python scrapers/audit_manual.py 2026-06-15 # 指定今天(避免時鐘問題)

CI 可掛此腳本;發現 STALE 時回傳非零 exit code。
"""
import sys, io, json
from datetime import date, datetime
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

STALE_DAYS = 120  # _checked 超過這天數就提醒重新查證

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

    stale, unchecked = [], []
    for s in shows:
        end = parse_d(s.get("end_date"))
        if end and end < today:
            stale.append((s.get("id"), s.get("title"), s.get("end_date")))
        chk = parse_d(s.get("_checked"))
        if chk and (today - chk).days > STALE_DAYS:
            unchecked.append((s.get("id"), s.get("title"), s.get("_checked"), (today - chk).days))

    print(f"audit_manual: {len(shows)} manual shows | today={today}")
    if stale:
        print(f"\n  ⚠ {len(stale)} STALE (end_date 已過 → 移除或更新檔期):")
        for i, t, e in stale:
            print(f"      {e}  {t}  [{i}]")
    if unchecked:
        print(f"\n  · {len(unchecked)} 需重新查證 (_checked > {STALE_DAYS} 天):")
        for i, t, c, d in unchecked:
            print(f"      _checked {c} ({d}d)  {t}  [{i}]")
    if not stale and not unchecked:
        print("  OK: 無過期、無逾期未查證項目")

    # CI: 有 stale 視為失敗(逾期未查證僅提醒,不擋)
    return 1 if stale else 0


if __name__ == "__main__":
    sys.exit(main())
