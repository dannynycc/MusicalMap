# -*- coding: utf-8 -*-
"""§3 查證判定 fix 的【定點修正】套用器。

為什麼不重生成:鐵則 6 說「每次重生成後整篇重讀」,而且『修 A 引入 B』已經發生四次。
一句話的事實錯誤,重跑整篇的風險遠大於收益。定點改完我仍然整篇重讀一次。

為什麼不直接手改 JSON:手改改不到會【無聲通過】——字串多一個空格、稿子後來被續跑覆蓋,
都會讓 replace() 什麼也沒做而 exit 0。所以每一條都斷言 old 在該篇【恰好出現一次】。

用法: python scratchpad/cn82/apply_fix.py <fixes.json> [--dry]
"""
import io
import json
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
B = "scratchpad/cn82"
SUF = {"zh-hant": "zht", "zh-hans": "zhs", "en": "en"}


def gen_running():
    """🚨 px_gen 還在跑的時候【絕不可】寫 regen_*.json。

    那支程式把整份 results 留在記憶體裡,每收一篇就整檔覆寫 —— 我在中途寫進去的修正,
    下一次覆寫就沒了,而且是【靜默】消失(exit 0、檔案還在、內容被換掉)。
    這與 2026-09-04 那次 17 篇被覆蓋是同一個機制,差別只在觸發者是我而不是續跑判準。
    正確做法:修正留在 fixes.json(源頭),等生成全部收工再套用。
    """
    import subprocess
    try:
        out = subprocess.run(
            ["powershell", "-NoProfile", "-Command",
             "Get-CimInstance Win32_Process -Filter \"Name like 'python%'\" | "
             "Where-Object { $_.CommandLine -like '*px_gen*' } | Measure-Object | "
             "Select-Object -Expand Count"],
            capture_output=True, text=True, timeout=60)
        return int((out.stdout or "0").strip() or 0)
    except Exception as ex:                 # 查不到就當作【可能在跑】,寧可擋下來
        sys.stderr.write("::warning::查不到 px_gen 行程(%s),保守起見視為仍在跑%s" % (ex, chr(10)))
        return -1


def main():
    fixes = json.load(io.open(sys.argv[1], encoding="utf-8"))
    if "--dry" not in sys.argv:
        n = gen_running()
        if n != 0:
            print("⛔ 偵測到 px_gen 仍在執行(%s 個),不寫檔 —— 寫了會被續跑覆蓋。" % n)
            print("   請等生成收工後再跑一次(現在可以先用 --dry 檢查修正是否仍然命中)。")
            return 2
    dry = "--dry" in sys.argv
    touched = {}
    for f in fixes:
        if f.get("_"):                       # 以 _ 開頭的欄位是註記,不是修正
            continue
        lang, g = f["lang"], f["group"]
        suf = SUF[lang]
        if suf not in touched:
            rows = json.load(io.open("%s/regen_%s.json" % (B, suf), encoding="utf-8"))
            order = json.load(io.open("%s/regen_%s_order.json" % (B, suf), encoding="utf-8"))
            touched[suf] = [rows, order]
        rows, order = touched[suf]
        i = order.index(g)
        assert i < len(rows), "%s/%s 這篇還沒生成出來(order 第 %d 筆,現有 %d 筆)" % (g, lang, i, len(rows))
        txt = rows[i]["synopsis"]
        # 預設只准改【剛好一處】。譯名統一這種本來就要全篇替換,必須把預期次數 n 寫死在
        # fixes.json 裡 —— 這樣稿子若被續跑改動、次數對不上,就會當場失敗而不是默默改錯篇幅。
        want = f.get("n", 1)
        n = txt.count(f["old"])
        assert n == want, ("❌ %s/%s:要改的字串出現 %d 次,預期 %d 次 → %r"
                           % (g, lang, n, want, f["old"][:60]))
        rows[i]["synopsis"] = txt.replace(f["old"], f["new"])
        rows[i].setdefault("_fixed", []).append({"why": f["why"], "old": f["old"], "new": f["new"]})
        print("✓ %-12s %-8s %s" % (g[:12], lang, f["why"][:64]))
    if dry:
        print("\n--dry:沒有寫檔")
        return 0
    for suf, (rows, _o) in touched.items():
        p = "%s/regen_%s.json" % (B, suf)
        json.dump(rows, io.open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print("寫回 %s(%d 篇)" % (p, len(rows)))
    return 0


raise SystemExit(main())
