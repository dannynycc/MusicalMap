# -*- coding: utf-8 -*-
"""產生 kb_merge 用的 keymap:[[group, show字串], ...]

🚨 為什麼一定要有:kb_merge 對每一筆結果做 `key = keymap.get(title) or group_key(title)`,
   而我們 results.json 裡的 `show` 欄【是整段重生成 prompt】(幾百字,含官方劇情),
   沒有 keymap 就會被 group_key() 算成一個垃圾鍵,簡介會掛在一個不存在的 group 上
   —— 而且不會報錯,前端只是永遠不顯示。

用法: python scratchpad/cn82/mk_keymap.py <zht|en|zhs>
輸出: scratchpad/cn82/keymap_<suf>.json
"""
import io
import json
import os
import sys

BASE = "scratchpad/cn82"


def main():
    suf = sys.argv[1]
    order = json.load(io.open("%s/regen_%s_order.json" % (BASE, suf), encoding="utf-8"))
    # 🚨 2026-09-04:keymap 的 show 字串【必須取自 kb_merge 實際會讀的那個檔】(regen_<suf>.json
    #    的 show 欄),不可取自 regen_<suf>_list.json。兩者會漂移:我為了做反向測試重跑了
    #    mk_regen.py en,把 list 檔覆蓋成【新版 prompt】,而 results 裡存的是【生成當時的舊 prompt】
    #    —— keymap 因此對不到任何一筆(實測英文 0/69),而 kb_merge 對不到只會靜默改用
    #    group_key(整段 prompt) 算出垃圾鍵,不會報錯,前端永遠不顯示。
    rp = "%s/regen_%s.json" % (BASE, suf)
    if os.path.exists(rp):
        rows = json.load(io.open(rp, encoding="utf-8"))
        assert len(rows) <= len(order), "results 比 order 還長,順序對不上"
        km = [[order[i], r["show"]] for i, r in enumerate(rows) if r.get("show")]
        src = "results(%d 筆)" % len(rows)
    else:
        shows = json.load(io.open("%s/regen_%s_list.json" % (BASE, suf), encoding="utf-8"))
        assert len(order) == len(shows), "order 與 list 筆數不符"
        km = [[g, s] for g, s in zip(order, shows)]
        src = "list(尚未生成)"
    out = "%s/keymap_%s.json" % (BASE, suf)
    json.dump(km, io.open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    sys.stderr.write("keymap %s: %d 筆 -> %s\n" % (suf, len(km), out))
    return 0


raise SystemExit(main())
