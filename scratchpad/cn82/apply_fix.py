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
             "Where-Object { $_.CommandLine -like '*px_gen*' } | "
             "Select-Object -Expand CommandLine"],
            capture_output=True, text=True, timeout=60)
        # 🚨 2026-09-04 改精準:原本擋【任何】px_gen,但一個 px_gen 只寫它自己的輸出檔
        #    (檔名就在命令列裡)。簡中那支在跑的時候,繁中/英文的修正其實可以安全套用。
        #    改成【只擋正在被那支 px_gen 寫的檔】——這是把守門變準,不是變寬:
        #    比對不到命令列時仍然保守擋下(見 except)。
        lines = [x.strip() for x in (out.stdout or "").splitlines() if x.strip()]
        return lines
    except Exception as ex:                 # 查不到就當作【可能在跑】,寧可擋下來
        sys.stderr.write("::warning::查不到 px_gen 行程(%s),保守起見視為【全部都在跑】%s" % (ex, chr(10)))
        return ["<查詢失敗:保守視為全部在跑>"]


def main():
    fixes = json.load(io.open(sys.argv[1], encoding="utf-8"))
    targets = sorted({(f.get("suf") or SUF[f["lang"]]) for f in fixes if not f.get("_")})
    if "--dry" not in sys.argv:
        cmds = gen_running()
        # 只要有任何一支 px_gen 的命令列提到我要改的輸出檔,就擋下來
        clash = [suf for suf in targets
                 if any(("regen_%s.json" % suf) in c or "<查詢失敗" in c for c in cmds)]
        if clash:
            print("⛔ px_gen 正在寫 %s —— 不寫檔,否則修正會被續跑靜默覆蓋。" % clash)
            print("   命令列:%s" % [c[:110] for c in cmds])
            return 2
        if cmds:
            print("ℹ 有 %d 支 px_gen 在跑,但都不是寫 %s,可以安全套用。" % (len(cmds), targets))
    dry = "--dry" in sys.argv
    touched = {}
    for f in fixes:
        if f.get("_"):                       # 以 _ 開頭的欄位是註記,不是修正
            continue
        lang, g = f["lang"], f["group"]
        # 補充批寫的是 regen_zht_supp.json 之類的檔;讓 fix 條目可用 "suf" 指定,
        # 沒寫就沿用語言預設。🚨 不可讓它默默套到主批檔上——那會改錯篇。
        suf = f.get("suf") or SUF[lang]
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
