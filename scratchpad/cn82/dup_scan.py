# -*- coding: utf-8 -*-
"""同一篇內的【用詞重複】掃描器。

為什麼要有:這一批我親自讀出的問題裡,有一整類是守門完全看不到的——
同一篇裡同一個詞組反覆出現(牡丹亭「傳奇」同句兩次、日出渤海「渤海軍區教導旅」相鄰兩句、
ne zha 三個情節座標列兩次、金童子 馬丁·布斯/Martin Booth 並存)。
🚨 順序很重要:是【先親自讀出這一類問題,才把它寫成檢查】,不是先寫檢查再照它改。
   所以這支只【報告】不判定——人名、關鍵詞本來就該重複,要不要改由人看。

用法: python scratchpad/cn82/dup_scan.py <regen_*.json> [最短詞長,預設4]
"""
import io
import json
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
PUNC = "，。；：、？！「」『』“”‘’《》()（）——…\n "


def dups(t, n=4):
    """回傳 [(詞, 次數)],只留【極大】的重複片段(被更長重複片段包含的不重複報)。"""
    out = []
    for size in range(12, n - 1, -1):
        for i in range(len(t) - size + 1):
            w = t[i:i + size]
            if any(c in PUNC for c in w):
                continue
            c = t.count(w)
            if c > 1 and not any(w in prev for prev, _ in out):
                out.append((w, c))
    return out


def main():
    path = sys.argv[1]
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 4
    rows = json.load(io.open(path, encoding="utf-8"))
    op = path.replace(".json", "_order.json")
    order = json.load(io.open(op, encoding="utf-8"))
    is_en = "_en" in path
    hits = 0
    for i, r in enumerate(rows):
        t = r.get("synopsis") or ""
        if is_en:
            # 英文按【詞】切,4 個詞以上的重複才報(中文按字,標準不同)
            ws = re.findall(r"[A-Za-z'’-]+", t.lower())
            found = []
            for size in range(8, 3, -1):
                for j in range(len(ws) - size + 1):
                    g = " ".join(ws[j:j + size])
                    c = " ".join(ws).count(g)
                    if c > 1 and not any(g in p for p, _ in found):
                        found.append((g, c))
            d = found
        else:
            d = dups(t, n)
        if d:
            hits += 1
            print("── %s" % order[i])
            for w, c in d[:6]:
                print("     ×%d  %s" % (c, w))
    print("\n%d/%d 篇有重複片段(僅供人工判斷,人名與關鍵詞本來就會重複)" % (hits, len(rows)))
    return 0


raise SystemExit(main())
