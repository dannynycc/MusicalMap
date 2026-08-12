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
    guard_shrink(path, len(shows), label="atrapalo")            # 全自動來源:暴跌就擋
    guard_shrink(OUT, len(shows), label="x", block=False)       # 跑一半合法的來源:只警告

已採用(2026-08-12):ticketmaster、tm_tours、atrapalo、broadway_tours、atg、italy、
japan、china_poly、easteurope、opentix、westend、na_discover、gb_discover 皆為硬擋;
china_damai 為 block=False(人工逐頁解驗證碼,刻意只跑部分頁面是合法操作)。

門檻校準(git 歷史 26 次資料提交的實測單日最大跌幅):
    broadway.org -3% / atgtickets -1% / teatro.it -1% / opentix -2% /
    londontheatre -2% / polyt.cn -3% / jegy.hu -3% / damai -9%
全部離 -40% 很遠 → 這些來源不會誤報。歷史上唯二超過 -40% 的是 atrapalo(-72%)
與 ticketmaster(-77%),而那兩次正是本模組要抓的真故障,不是誤報。

**沒有加守門的地方,以及為什麼:**
· `build_shows.py` → shows.json:已由 `audit_counts.py` 在管線的正確位置用更嚴的
  -10% 門檻硬擋(門檻同樣取自歷史實測:日常 -4.4% ~ +4.3%)。再塞一個 -40% 的
  重複守門只會多一個失敗點,不會多擋到任何東西。
· 輸出少於 FLOOR(50)筆的小來源(austria 2、poland 4、middleeast 4、sweden 7、
  norway 8、utiki 8、stage_de 12…):守門在這個量級只會空轉,±幾筆就是大百分比。
  這些來源將來長大到 50 筆以上時再加即可。
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


def guard_shrink(path, new_count, label=None, floor=FLOOR, max_drop=MAX_DROP, block=True):
    """新結果比舊檔少太多就示警。正常情況直接返回,呼叫端照舊寫檔。

    block=True(預設):印 ::error:: 並 sys.exit(1),**不覆蓋舊檔**。用於全自動來源——
        跑一半沒有正當理由,少一大塊一定是故障。
    block=False:只印 ::warning:: 就返回,照樣寫檔。用於「跑一半是合法的」來源,
        例如 china_damai 要人工逐頁解驗證碼,刻意只跑前幾頁是正常操作;
        這種硬擋會把使用者一小時的工作丟掉,比病本身還糟。
    """
    label = label or Path(path).stem
    prev = previous_count(path)
    if prev is None or prev < floor:
        return
    if new_count >= prev * (1 - max_drop):
        return
    drop = 100.0 * (prev - new_count) / prev
    if block:
        print(f"\n::error::[{label}] 抓到的資料暴跌 {drop:.0f}%({prev} → {new_count} 筆),"
              f"超過 {int(max_drop * 100)}% 門檻 — 多半是整批抓失敗(限流/bot 牆/版面改版),"
              f"不是真的少了這麼多演出。不覆蓋 {Path(path).name},保留上一份完整資料;"
              f"下次抓取正常就會自己恢復。")
        sys.exit(1)
    print(f"\n::warning::[{label}] 抓到的資料比上一份少 {drop:.0f}%({prev} → {new_count} 筆)。"
          f"若這次是刻意只跑部分頁面就沒問題;否則多半是整批抓失敗,"
          f"請確認後再決定要不要保留這份輸出。")
