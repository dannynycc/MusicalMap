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
import sys

BASE = "scratchpad/cn82"


def main():
    suf = sys.argv[1]
    order = json.load(io.open("%s/regen_%s_order.json" % (BASE, suf), encoding="utf-8"))
    shows = json.load(io.open("%s/regen_%s_list.json" % (BASE, suf), encoding="utf-8"))
    assert len(order) == len(shows), "order 與 list 筆數不符"
    km = [[g, s] for g, s in zip(order, shows)]
    out = "%s/keymap_%s.json" % (BASE, suf)
    json.dump(km, io.open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    sys.stderr.write("keymap %s: %d 筆 -> %s\n" % (suf, len(km), out))
    return 0


raise SystemExit(main())
