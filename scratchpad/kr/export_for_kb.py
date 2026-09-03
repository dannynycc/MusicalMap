# -*- coding: utf-8 -*-
"""把最終三語稿匯出成 kb_merge.py 吃得下的格式。

kb_merge 需要 [{"show": <劇名>, "synopsis": <內文>}],而且 show 要能對到
keymap_final.json 的 title(已驗證 title_en 與 keymap 是 55/55 完全對應)。
out_*.json 的 show 欄位是【生成用的長 prompt】,不能直接餵進去。

🚨 這裡【排除 4 齣 verdict=reject 的】:官方完全沒公開劇情、產出全是模型自行補的,
   不入庫(나의 첫사랑 레시피 / 물속의 달-오필리어 / 고백 / 조선셰프 한상궁)。

用法: python scratchpad/kr/export_for_kb.py
輸出: scratchpad/kr/final_en.json / final_zht.json / final_zhs.json
"""
import io
import json
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
BASE = "scratchpad/kr"
PAIRS = [("en", "out_en.json", "final_en.json"),
         ("zh-hant", "out_zht.json", "final_zht.json"),
         ("zh-hans", "out_zhs.json", "final_zhs.json")]


def load(p):
    return json.load(io.open("%s/%s" % (BASE, p), encoding="utf-8"))


def main():
    todo = load("syn_todo.json")
    log = load("verify_log.json")["shows"]
    km = {t: g for g, t in load("keymap_final.json")}
    rejected = {c for c, v in log.items() if v.get("verdict") == "reject"}
    skipped = []
    for lang, src, dst in PAIRS:
        rows = load(src)
        assert len(rows) == len(todo), (lang, len(rows), len(todo))
        out, skipped = [], []
        for i, t in enumerate(todo):
            if t["code"] in rejected:
                skipped.append(t.get("title_en")); continue
            title = t.get("title_en")
            assert title in km, ("title 不在 keymap", title)
            s = (rows[i].get("synopsis") or "").strip()
            assert s, ("空稿", lang, title)
            out.append({"show": title, "synopsis": s})
        json.dump(out, io.open("%s/%s" % (BASE, dst), "w", encoding="utf-8"),
                  ensure_ascii=False, indent=2)
        print("%-8s -> %s  %d 筆(排除 reject %d 齣)" % (lang, dst, len(out), len(skipped)))
    print("排除的:", ", ".join(skipped))
    return 0


raise SystemExit(main())
