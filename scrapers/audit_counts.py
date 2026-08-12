"""資料量回歸守門(2026-08-12,Ticketmaster 429 事件後補)。

事件經過:排程 run 跑完約一小時後又手動觸發一次完整重建,把 Ticketmaster 當日 API
配額用光。TM 對**每一個國家**都回 HTTP 429,scraper 把它當可容忍的錯誤、寫出手上僅有的
資料、正常結束(exit 0)—— 於是 `gate "ticketmaster"` 通過、所有稽核通過、CI 全綠,
而 shows.json 從 2130 掉到 1552(-27%),殘缺資料被提交並部署上線。

既有的守門全部看不到這件事:
  · gate 只看 scraper 的退出碼 —— 429 被吞掉了,退出碼是 0
  · audit_sentinels 看「常設劇目在不在、來源有沒有低於低標」—— TM 還剩 178 筆,過關
  · audit_dates / audit_official / audit_geo 檢查的是「留下來的資料對不對」,
    不是「有沒有整批不見」
少掉的資料不會讓任何一項檢查變紅,因為它們檢查的都是**存在的東西**。
這支專門看「跟上一版比,是不是整批消失了」。

門檻取自實測(git 歷史 24 次資料提交):
  · 總筆數日常變化落在 -4.4% ~ +4.3%;事件當次是 -27.1% → 門檻設 -10%,**硬擋**
    (退出碼 1 → 工作流程停在這一步,殘缺資料不會被 commit,線上維持前一版良好資料)
  · 單一來源:中位跌幅 -2.1%,但 atrapalo.com 一週內合法地掉過兩次 -72%
    (Playwright 來源本來就會抖)→ 只警告不擋,免得天天狼來了

Run: python scrapers/audit_counts.py
"""

import collections
import io
import json
import subprocess
import sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

TOTAL_DROP_PCT = 10.0      # 總筆數跌幅超過這個 → 硬擋
SOURCE_DROP_PCT = 40.0     # 單一來源跌幅超過這個 → 只警告
SOURCE_MIN = 50            # 太小的來源不看(±幾筆就是大百分比)


def previous_shows():
    """上一版(HEAD)的 shows.json。取不到就回 None = 跳過檢查。"""
    try:
        out = subprocess.run(["git", "show", "HEAD:data/shows.json"],
                             cwd=ROOT, capture_output=True, timeout=120)
        if out.returncode != 0 or not out.stdout:
            return None
        return json.loads(out.stdout.decode("utf-8"))["shows"]
    except Exception:
        return None


def main():
    now = json.loads((DATA / "shows.json").read_text(encoding="utf-8"))["shows"]
    before = previous_shows()
    if before is None:
        print("count audit: 取不到上一版 shows.json(首次建置或不在 git 工作區)→ 跳過")
        return 0

    n_now, n_before = len(now), len(before)
    delta = n_now - n_before
    pct = (100.0 * delta / n_before) if n_before else 0.0

    src_now = collections.Counter(s.get("source") for s in now)
    src_before = collections.Counter(s.get("source") for s in before)
    warned = 0
    for s, c in sorted(src_before.items(), key=lambda kv: -kv[1]):
        if c < SOURCE_MIN:
            continue
        d = 100.0 * (src_now.get(s, 0) - c) / c
        if d <= -SOURCE_DROP_PCT:
            warned += 1
            print(f"::warning::count source-drop: {s} {c} → {src_now.get(s, 0)} 筆({d:+.0f}%)"
                  f" — 該來源可能整批抓失敗(被限流/版面改版/憑證過期)")

    gone = [s for s, c in src_before.items() if c >= SOURCE_MIN and src_now.get(s, 0) == 0]
    for s in gone:
        print(f"::warning::count source-gone: {s} 從 {src_before[s]} 筆變成 0 筆 — 整個來源消失")

    print(f"count audit: {n_before} → {n_now} 筆({pct:+.1f}%),"
          f"來源暴跌警告 {warned} 項")

    if pct <= -TOTAL_DROP_PCT:
        print(f"::error::資料量暴跌 {pct:.1f}%({n_before} → {n_now} 筆),超過 -{TOTAL_DROP_PCT}% 門檻。"
              f"多半是某個來源被限流或整批抓失敗;本次不提交資料,線上維持前一版。"
              f"日常變化區間約 -4.4% ~ +4.3%,請看上面的 source-drop 警告找出是哪個來源。")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
