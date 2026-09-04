# -*- coding: utf-8 -*-
"""簡中(zh-hans)引號正規化:「」→“”、『』→‘’。

為什麼需要:大陸官方物料【兩種引號都會用】,模型就照著抄,結果同一批稿子內部不一致——
2026-09-04 實測:《入傩》《去你的夏天》用“”,《亡灵之旅》《六个说谎的大学生》用「」,
而《博物馆奇遇记》【同一篇裡兩種都有】(2 個「 + 1 個 “)。

慣例從現有簡介庫數出來,不是我決定的:
    data/synopses*/zh-hans.json → “ 848 次 : 「 294 次(約 74%)

🚨 只動【簡中】。繁中(zh-hant)的慣例相反,是「」,絕不可套用這支。

用法:
    python scripts/zhs_quote_norm.py <檔.json> --check   # 只報告
    python scripts/zhs_quote_norm.py <檔.json>           # 實際寫回
    python scripts/zhs_quote_norm.py --stats             # 重新統計全站慣例
    python scripts/zhs_quote_norm.py --test              # 正反向測試
"""
import glob
import io
import json
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

# 外層「」→“”,內層『』→‘’。中文標點的巢狀順序:「…『…』…」 對應 “…‘…’…”
PAIRS = [("「", "“"), ("」", "”"), ("『", "‘"), ("』", "’")]


def norm(text):
    changes = 0
    for a, b in PAIRS:
        changes += text.count(a)
        text = text.replace(a, b)
    return text, changes


def stats():
    files = [p for p in glob.glob("data/synopses*/**/*.json", recursive=True)
             if p.endswith("zh-hans.json")]
    s = "".join(json.dumps(json.load(io.open(p, encoding="utf-8")), ensure_ascii=False)
                for p in files)
    print("來源:%s" % files)
    for a, b in PAIRS:
        print("  %s %5d  vs  %s %5d" % (a, s.count(a), b, s.count(b)))
    return 0


def test():
    cases = [
        ("在「称量法庭」交出心脏", "在“称量法庭”交出心脏", "該換的要換"),
        ("在“称量法庭”交出心脏", "在“称量法庭”交出心脏", "已經對的不可動"),
        ("他说「我看过『亡灵书』」", "他说“我看过‘亡灵书’”", "巢狀引號要對應換"),
        ("《亡灵书》与《女神录》", "《亡灵书》与《女神录》", "🚨 書名號不是引號,不可動"),
        ("暗杀组织Borderline", "暗杀组织Borderline", "沒有引號就不該有任何改動"),
    ]
    bad = 0
    for src, want, why in cases:
        got, _n = norm(src)
        ok = got == want
        bad += 0 if ok else 1
        print("%s %-26s → %-26s  %s" % ("○" if ok else "❌", src, got, why))
    print("\n%d/%d 通過" % (len(cases) - bad, len(cases)))
    return 1 if bad else 0


def main():
    if "--stats" in sys.argv:
        return stats()
    if "--test" in sys.argv:
        return test()
    path = sys.argv[1]
    # 🚨 防呆:這支只能跑簡中。跑到繁中檔上會把「」全部換掉,方向剛好相反。
    if "zht" in path or "hant" in path:
        print("⛔ %s 看起來是繁中檔。繁中慣例是「」,這支只能用在簡中。" % path)
        return 2
    rows = json.load(io.open(path, encoding="utf-8"))
    total = 0
    hit = []
    for i, r in enumerate(rows):
        t = r.get("synopsis") or ""
        if not t:
            continue
        new, n = norm(t)
        if n:
            total += n
            hit.append(i)
        rows[i]["synopsis"] = new
    print("有改動的篇:%s(共 %d 處)" % (hit, total))
    if "--check" in sys.argv:
        print("--check:沒有寫檔")
        return 0
    json.dump(rows, io.open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("已寫回 %s" % path)
    return 0


raise SystemExit(main())
