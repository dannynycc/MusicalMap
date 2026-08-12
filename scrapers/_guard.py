"""抓取結果暴跌守門(2026-08-12)。

問題長這樣:scraper 的主迴圈用 `except Exception: print(...); continue` 吞掉個別失敗,
然後**照樣把手上僅有的資料覆蓋上去**。個別失敗容忍是對的(某一頁挑戰驗證、某一國沒資料),
但當失敗是整批的(API 配額用盡、bot 牆升級、版面改版),結果就是「悄悄少一大塊」——
退出碼 0、CI 全綠、線上資料默默縮水。

實際案例(都在 2026-08-12 查證):
  · ticketmaster:當日 API 配額用盡,每個國家都回 429 → shows.json 2130 → 1552(-27%)
  · atrapalo.com:11 天內掉了 4 次,116 → 32 筆,約 82 齣西班牙演出消失半天再自己回來

守門邏輯:**寧可不更新,也不要用殘缺資料覆蓋上一份好資料。**
舊檔留在原地 → build_shows 仍拿得到完整資料 → 線上不受影響;同時以非零退出碼讓 CI 變紅。
下一次抓取正常就會自己恢復(這類故障多半是暫時的)。

用法(放在 write_text 之前):

    from _guard import guard_shrink
    guard_shrink(path, len(shows), label="atrapalo")

尚未採用的 scraper(2026-08-12 掃描結果,都有同樣的吞錯寫法):
austria, booking_horizon, china_damai, easteurope, eu_discover, gb_discover, italy,
japan, middleeast, na_discover, norway, poland, stage_de, sweden, utiki
"""

import json
import sys
from pathlib import Path

FLOOR = 50          # 少於這個筆數的來源不看(±幾筆就是大百分比,沒有意義)
MAX_DROP = 0.40     # 跌幅超過這個比例就擋下


def previous_count(path):
    """讀既有輸出檔的筆數;檔案不在或壞掉回 None(= 不做判斷)。"""
    p = Path(path)
    if not p.exists():
        return None
    try:
        d = json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None
    if isinstance(d, dict):
        for k in ("shows", "events", "items", "runs"):
            if isinstance(d.get(k), list):
                return len(d[k])
        return None
    return len(d) if isinstance(d, list) else None


def guard_shrink(path, new_count, label=None, floor=FLOOR, max_drop=MAX_DROP):
    """新結果比舊檔少太多就印 ::error:: 並 sys.exit(1),**不覆蓋舊檔**。

    正常情況直接返回,呼叫端照舊寫檔。
    """
    label = label or Path(path).stem
    prev = previous_count(path)
    if prev is None or prev < floor:
        return
    if new_count >= prev * (1 - max_drop):
        return
    drop = 100.0 * (prev - new_count) / prev
    print(f"\n::error::[{label}] 抓到的資料暴跌 {drop:.0f}%({prev} → {new_count} 筆),"
          f"超過 {int(max_drop * 100)}% 門檻 — 多半是整批抓失敗(限流/bot 牆/版面改版),"
          f"不是真的少了這麼多演出。不覆蓋 {Path(path).name},保留上一份完整資料;"
          f"下次抓取正常就會自己恢復。")
    sys.exit(1)
