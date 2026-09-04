# -*- coding: utf-8 -*-
"""輪詢正式站,等本次建置的 DATA_VER 上線。

🚨 標記必須【本次獨有】:先確認正式站現在【沒有】這個值(0 匹配),
   否則會拿舊部署當成功交卷。
用法: python scratchpad/cn82/poll_deploy.py <DATA_VER> [最多幾分鐘=15]
"""
import re
import sys
import time

from curl_cffi import requests as rq

URL = "https://themusicalmap.com/"


def cur():
    r = rq.get(URL, impersonate="chrome", timeout=30,
               headers={"Cache-Control": "no-cache", "Pragma": "no-cache"})
    m = re.search(r'DATA_VER="([a-f0-9]+)"', r.text)
    return (m.group(1) if m else None), r.status_code


def main():
    want = sys.argv[1]
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else 15
    got, st = cur()
    if got == want:
        print("🚨 正式站【已經】是 %s —— 這個標記不是本次獨有,不能用來判斷部署" % want)
        return 2
    print("開始輪詢:want=%s,正式站現在=%s(確認 0 匹配 ✅)" % (want, got))
    deadline = time.time() + limit * 60
    n = 0
    while time.time() < deadline:
        time.sleep(20)
        n += 1
        got, st = cur()
        print("  第 %2d 次(%3ds) status=%s DATA_VER=%s" % (n, n * 20, st, got), flush=True)
        if got == want:
            print("✅ 部署完成:正式站 DATA_VER = %s" % got)
            return 0
    print("⏱ 逾時 %d 分鐘仍未更新(最後看到 %s)" % (limit, got))
    return 1


raise SystemExit(main())
