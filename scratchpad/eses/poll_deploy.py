# -*- coding: utf-8 -*-
"""輪詢正式站直到本次部署的 DATA_VER 出現。標記已先對舊版檔驗過 0 匹配。"""
import io, sys, time, urllib.request
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
MARK = "7d87425356"
URL = "https://themusicalmap.com/"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) MusicalMap-deploy-check"}
for i in range(40):
    try:
        req = urllib.request.Request(URL, headers=UA)
        with urllib.request.urlopen(req, timeout=25) as r:
            html = r.read().decode("utf-8", "replace")
        if MARK in html:
            print("OK 第 %d 次:正式站已是本次部署(DATA_VER=%s)" % (i + 1, MARK))
            sys.exit(0)
        import re
        cur = re.search(r'MM_DATA_VER="([a-f0-9]+)"', html)
        print("  第 %d 次:線上仍是 %s" % (i + 1, cur.group(1) if cur else "?"))
    except Exception as e:
        print("  第 %d 次:%s" % (i + 1, e))
    time.sleep(20)
print("逾時:13 分鐘內未看到本次部署")
sys.exit(1)
