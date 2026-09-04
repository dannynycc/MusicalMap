# -*- coding: utf-8 -*-
"""關掉 Comet 裡殘留的 Perplexity 分頁,只留最後 N 個。

🚨 為什麼會殘留:px_gen 的 ask_once 有 try/finally p.close(),正常結束不會漏;
   但我用 Stop-Process 強制殺掉整個 python 行程時,finally 來不及跑,分頁就留在那裡。
   本輪為了修 prompt 停過六七次,累積到 19 個分頁 —— 使用者看到並提醒了記憶體。
   教訓:要停 px_gen 之前先想清楚,不要為了改一個字就殺;真的要殺,殺完立刻跑這支。

用法: python scratchpad/cn82/close_tabs.py [要保留幾個=2]
⚠ 跑之前【務必先確認沒有 px_gen 在跑】,否則會關掉它正在用的分頁。
"""
import json
import sys
import urllib.request

CDP = "http://127.0.0.1:9223"


def get(path):
    return json.load(urllib.request.urlopen(CDP + path, timeout=10))


def main():
    keep = int(sys.argv[1]) if len(sys.argv) > 1 else 2
    pages = [t for t in get("/json/list") if t.get("type") == "page"]
    # 保留 newtab 與 sidecar(那是使用者自己的),只關 perplexity 的搜尋/首頁分頁
    mine = [t for t in pages
            if "perplexity.ai" in (t.get("url") or "") and "sidecar" not in (t.get("url") or "")]
    others = [t for t in pages if t not in mine]
    closed = 0
    for t in mine[:-keep] if keep else mine:
        try:
            urllib.request.urlopen(CDP + "/json/close/" + t["id"], timeout=10).read()
            closed += 1
        except Exception as e:
            sys.stderr.write("關不掉 %s: %s\n" % (t["id"][:12], str(e)[:60]))
    left = [t for t in get("/json/list") if t.get("type") == "page"]
    sys.stderr.write("關閉 %d 個;分頁 %d → %d(其中非 perplexity 的 %d 個未動)\n"
                     % (closed, len(pages), len(left), len(others)))
    return 0


raise SystemExit(main())
