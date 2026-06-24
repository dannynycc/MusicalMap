# -*- coding: utf-8 -*-
"""
大麥 Damai 人工協助抓取工具 (manual-assisted harvest)

大麥有阿里 BaXia x5sec 風控 (滑塊驗證)，無人值守 CI 繞不過。
本工具走「人過驗證、機器接手 session」路線：

  1) python china_damai.py launch   # 開真 Chrome (遠端除錯埠) 導到大麥音樂劇搜尋頁
  2) 你手動把滑塊解掉、看到搜尋結果
  3) python china_damai.py probe     # 連上同一 session，打一次 searchajax 確認沒被擋
  4) python china_damai.py harvest   # 控速逐頁抓，一偵測 x5sec 立即停

抓 searchajax 是「在頁面 context 內 fetch」→ 自動帶你過關後的 cookie + 同源 + 真指紋。
這是一次性/偶爾的手動批次，不是自動來源。
"""
import sys, io, os, re, json, time, subprocess, argparse, collections

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

CHROME = r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
DEBUG_PORT = 9222
PROFILE_DIR = os.path.join(os.environ.get("TEMP", r"C:\Temp"), "damai_cdp_profile")
SEARCH_URL = "https://search.damai.cn/search.htm?keyword=%E9%9F%B3%E4%B9%90%E5%89%A7"
OUT_RAW = os.path.join(os.path.dirname(__file__), "..", "data", "china_damai_raw.json")


def launch():
    os.makedirs(PROFILE_DIR, exist_ok=True)
    args = [
        CHROME,
        f"--remote-debugging-port={DEBUG_PORT}",
        f"--user-data-dir={PROFILE_DIR}",
        "--no-first-run", "--no-default-browser-check",
        SEARCH_URL,
    ]
    # detached：Chrome 自成一個 process，解完滑塊後留著給 probe/harvest 連
    subprocess.Popen(args, creationflags=getattr(subprocess, "DETACHED_PROCESS", 0))
    print(f"[launch] Chrome 已開 (debug port {DEBUG_PORT})，導到大麥音樂劇搜尋頁。")
    print("[launch] 請手動解滑塊、確認看到搜尋結果列表後，告訴我跑 probe。")


def _connect():
    from playwright.sync_api import sync_playwright
    pw = sync_playwright().start()
    browser = pw.chromium.connect_over_cdp(f"http://127.0.0.1:{DEBUG_PORT}")
    ctx = browser.contexts[0]
    page = ctx.pages[0] if ctx.pages else ctx.new_page()
    return pw, browser, page


def _fetch_searchajax(page, keyword, cty, curr_page, page_size=100):
    """在頁面 context 內 fetch searchajax，帶 session cookie + 同源。"""
    url = (
        "https://search.damai.cn/searchajax.html"
        f"?keyword={keyword}&cty={cty}&ctl=&order=1"
        f"&pageSize={page_size}&currPage={curr_page}&tabType=&categoryId="
    )
    js = """
    async (u) => {
        const r = await fetch(u, {credentials:'include', headers:{'Referer':'https://search.damai.cn/search.htm'}});
        const t = await r.text();
        return {status:r.status, text:t};
    }
    """
    return page.evaluate(js, url)


def _looks_blocked(text):
    return ("x5secdata" in text) or ("captcha" in text) or ("_____tmd_____" in text) or ("punish" in text)


def probe():
    pw, browser, page = _connect()
    try:
        from urllib.parse import quote
        res = _fetch_searchajax(page, quote("音乐剧"), "", 1)
        text = res["text"]
        print(f"[probe] HTTP {res['status']}, {len(text)} bytes")
        if _looks_blocked(text):
            print("[probe] ❌ 仍是 x5sec 擋頁 — session 還沒過關或又被挑戰。請重解滑塊再試。")
            print("[probe] body 前 300:", text[:300])
            return
        print("[probe] ✅ 看起來是真資料，不是擋頁。結構預覽：")
        try:
            data = json.loads(text)
            print("[probe] top keys:", list(data.keys()))
            print(json.dumps(data, ensure_ascii=False)[:1200])
        except Exception:
            print("[probe] 非 JSON，前 1200 字：")
            print(text[:1200])
    finally:
        browser.close(); pw.stop()


def _row_key(r):
    return r.get("projectid") or r.get("itemId") or r.get("id") or r.get("nameNoHtml") or r.get("name")


def _load_existing():
    """讀既有 raw 檔 → (dict by key, set)；支援 --start-page 續抓累積。"""
    if os.path.exists(OUT_RAW):
        try:
            with open(OUT_RAW, encoding="utf-8") as f:
                rows = json.load(f)
            return {_row_key(r): r for r in rows}
        except Exception:
            pass
    return {}


def _save(by_key):
    os.makedirs(os.path.dirname(OUT_RAW), exist_ok=True)
    with open(OUT_RAW, "w", encoding="utf-8") as f:
        json.dump(list(by_key.values()), f, ensure_ascii=False, indent=2)


def harvest(max_pages=10, start_page=1, delay_min=15.0, delay_max=25.0):
    """控速、每頁即時寫檔、可 --start-page 續抓。一遇 x5sec 立即停並告知續抓頁。

    pageSize=100 → 711 部約 8 頁；間隔 15~25s 隨機抖動裝人。
    被擋時：你在視窗補解滑塊，再 `harvest --start-page <被擋的那頁>` 接著抓。
    """
    import random
    from urllib.parse import quote
    pw, browser, page = _connect()
    by_key = _load_existing()
    print(f"[harvest] 既有 {len(by_key)} 筆；從第 {start_page} 頁開始", flush=True)
    try:
        cp = start_page
        last_page = start_page + max_pages - 1
        while cp <= last_page:
            res = _fetch_searchajax(page, quote("音乐剧"), "", cp)
            text = res["text"]
            if _looks_blocked(text):
                _save(by_key)
                print(f"[harvest] ⚠ 第 {cp} 頁撞 x5sec — 已停。目前 {len(by_key)} 筆已存檔。", flush=True)
                print(f"[harvest] 👉 請在視窗補解滑塊，再跑：python scrapers/china_damai.py harvest --start-page {cp}", flush=True)
                break
            try:
                data = json.loads(text)
            except Exception:
                _save(by_key)
                print(f"[harvest] 第 {cp} 頁非 JSON，停（已存 {len(by_key)} 筆）。前 200：{text[:200]}", flush=True)
                break
            pd = data.get("pageData", {}) or {}
            rows = pd.get("resultData") or data.get("resultData") or []
            total_page = pd.get("totalPage")
            if not rows:
                _save(by_key)
                print(f"[harvest] 第 {cp} 頁無 resultData，停（已存 {len(by_key)} 筆）。keys={list(data.keys())}", flush=True)
                break
            new = 0
            for r in rows:
                k = _row_key(r)
                if k not in by_key:
                    new += 1
                by_key[k] = r
            _save(by_key)  # 每頁即時寫，被砍也不丟
            print(f"[harvest] 第 {cp}/{total_page} 頁 抓 {len(rows)} 筆(+{new} 新)；累計 {len(by_key)}", flush=True)
            if total_page and cp >= total_page:
                print(f"[harvest] ✅ 已到最後一頁 ({total_page})，全部抓完。", flush=True)
                break
            cp += 1
            if cp <= last_page:
                d = random.uniform(delay_min, delay_max)
                # 約 1/4 機率「停下來看一齣」：多停 10~30s，模擬真人讀內容
                if random.random() < 0.25:
                    extra = random.uniform(10, 30)
                    d += extra
                    print(f"[harvest] 睡 {d:.1f}s（含 {extra:.0f}s 讀內容停頓）", flush=True)
                else:
                    print(f"[harvest] 睡 {d:.1f}s（裝人）", flush=True)
                time.sleep(d)
        print(f"[harvest] 本輪結束，raw 共 {len(by_key)} 筆 → {OUT_RAW}", flush=True)
    finally:
        browser.close(); pw.stop()


# ---------------------------------------------------------------------------
# build：raw → 濾音樂劇 → 劇名+城市去重 → 標準 schema (同 china_juooo.json)
# ---------------------------------------------------------------------------
OUT_SHOWS = os.path.join(os.path.dirname(__file__), "..", "data", "china_damai.json")

# 城市中→英（juooo CITY_EN + 大麥多出來的 20 城）
CITY_EN = {
    "北京": "Beijing", "上海": "Shanghai", "广州": "Guangzhou", "深圳": "Shenzhen",
    "天津": "Tianjin", "重庆": "Chongqing", "武汉": "Wuhan", "南京": "Nanjing",
    "杭州": "Hangzhou", "苏州": "Suzhou", "成都": "Chengdu", "西安": "Xi'an",
    "沈阳": "Shenyang", "哈尔滨": "Harbin", "青岛": "Qingdao", "济南": "Jinan",
    "郑州": "Zhengzhou", "长沙": "Changsha", "南昌": "Nanchang", "合肥": "Hefei",
    "福州": "Fuzhou", "厦门": "Xiamen", "太原": "Taiyuan", "海口": "Haikou",
    "南宁": "Nanning", "银川": "Yinchuan", "无锡": "Wuxi", "宁波": "Ningbo",
    "常州": "Changzhou", "东莞": "Dongguan", "珠海": "Zhuhai", "佛山": "Foshan",
    "昆明": "Kunming", "贵阳": "Guiyang", "大连": "Dalian", "长春": "Changchun",
    # 大麥多出來的
    "南通": "Nantong", "嘉兴": "Jiaxing", "衢州": "Quzhou", "廊坊": "Langfang",
    "绍兴": "Shaoxing", "中国澳门": "Macau", "温州": "Wenzhou", "衡阳": "Hengyang",
    "潍坊": "Weifang", "昆山": "Kunshan", "淄博": "Zibo", "烟台": "Yantai",
    "徐州": "Xuzhou", "西宁": "Xining", "鄂尔多斯": "Ordos", "中山": "Zhongshan",
    "延边": "Yanbian", "桂林": "Guilin", "淮安": "Huai'an", "周口": "Zhoukou",
}

# 名字含這些 = 確定音樂劇
_POS = ["音乐剧", "音乐喜剧", "音乐戏剧", "音乐舞台", "musical", "Musical", "MUSICAL"]
# 即便有 _POS，含這些 = 借名舞劇/誤標/純音樂會 → 仍剔除
_NEG = ["舞蹈诗剧", "舞蹈剧场", "舞蹈秀", "现代舞", "街舞", "歌舞晚会", "歌舞秀",
        "芭蕾", "舞剧", "明星音乐会", "演唱会",
        "券包", "套票", "通票", "年卡", "月卡", "次卡", "惠民卡", "9.9元"]  # 非單一場次的票券商品


def _is_musical(name):
    return any(p in name for p in _POS) and not any(g in name for g in _NEG)


def _canon_title(name):
    """取《》內為正規劇名(去重 key+顯示);無《》則清掉促銷前綴/站別。"""
    m = re.search(r"《([^》]+)》", name)
    if m:
        return m.group(1).strip()
    n = re.sub(r"^\s*[\[【（(][^\]】）)]*[\]】）)]\s*", "", name)  # 去開頭一組括號
    n = re.sub(r"[—\-·•].*?站\s*$", "", n)                       # 去尾「…站」
    return n.strip()


def _parse_dates(showtime):
    """'2026.07.02-07.05'→('2026-07-02','2026-07-05')。處理跨月/單日/帶星期時間
    (如 '2026.06.28 周日 15:00')/跨年。只取日期數字,丟掉星期與時刻。"""
    if not showtime:
        return None, None
    parts = showtime.replace("．", ".").strip().split("-", 1)
    a = re.findall(r"\d+", parts[0])          # 起始端只取數字組
    if len(a) < 3 or len(a[0]) != 4:
        return None, None
    y, m, d = a[0], a[1].zfill(2), a[2].zfill(2)
    start = f"{y}-{m}-{d}"
    end = start
    if len(parts) > 1:
        b = re.findall(r"\d+", parts[1])
        if len(b) >= 3 and len(b[0]) == 4:    # 完整 Y.M.D(可能跨年)
            end = f"{b[0]}-{b[1].zfill(2)}-{b[2].zfill(2)}"
        elif len(b) >= 2:                     # M.D，年沿用起始
            end = f"{y}-{b[0].zfill(2)}-{b[1].zfill(2)}"
        elif len(b) >= 1:                     # 只有 D
            end = f"{y}-{m}-{b[0].zfill(2)}"
    return start, end


def build():
    rows = json.load(open(OUT_RAW, encoding="utf-8"))
    mus = [r for r in rows if r.get("subcategoryname") == "音乐剧"]
    keep_raw = [r for r in mus if _is_musical(r.get("nameNoHtml", ""))
                and (r.get("venue") or "") not in ("大麦网", "大麥網", "")]
    dropped = len(mus) - len(keep_raw)

    # 劇名+城市去重，取最早 start_date 的場次代表
    groups = {}
    for r in keep_raw:
        title = _canon_title(r.get("nameNoHtml", ""))
        city_cn = r.get("venuecity") or ""
        start, end = _parse_dates(r.get("showtime"))
        key = (title, city_cn)
        prev = groups.get(key)
        if prev is None or (start and (prev["_start"] is None or start < prev["_start"])):
            groups[key] = {"r": r, "title": title, "city_cn": city_cn,
                           "_start": start, "_end": end}

    shows = []
    for (title, city_cn), g in groups.items():
        r = g["r"]
        pid = str(r.get("projectid") or "").strip()
        ticket = f"https://detail.damai.cn/item.htm?id={pid}"
        shows.append({
            "id": f"damai-{pid}",
            "title": title,
            "type": "limited",
            "venue": r.get("venue") or "",
            "city": CITY_EN.get(city_cn, city_cn),
            "city_cn": city_cn,
            "country": "China",
            "lat": None, "lng": None,           # geocode_google.py 依 venue|city 補
            "start_date": g["_start"], "end_date": g["_end"],
            "ticket_url": ticket,
            "ticket_links": [{"label": "大麥", "url": ticket, "kind": "ticketing"}],
            "image": r.get("verticalPic") or None,
            "tour_name": None,
            "source": "damai",
        })
    shows.sort(key=lambda s: (s["city"], s["title"]))
    out = {"meta": {"source": "damai.cn", "count": len(shows),
                    "note": "人工協助抓取(x5sec 需真人解);劇名+城市去重;含精準 detail 連結"},
           "shows": shows}
    json.dump(out, open(OUT_SHOWS, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"[build] 音乐剧 raw {len(mus)} → 濾真音樂劇 {len(keep_raw)} (剔除非音樂劇 {dropped}) "
          f"→ 劇名+城市去重 {len(shows)} 場次 → {OUT_SHOWS}", flush=True)
    cities = collections.Counter(s["city"] for s in shows)
    print(f"[build] 涵蓋 {len(cities)} 城;top: {cities.most_common(8)}", flush=True)
    untrans = sorted(set(s["city_cn"] for s in shows if s["city"] == s["city_cn"]))
    if untrans:
        print(f"[build] ⚠ 未翻譯城市(沿用中文): {untrans}", flush=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["launch", "probe", "harvest", "build"])
    ap.add_argument("--max-pages", type=int, default=10)
    ap.add_argument("--start-page", type=int, default=1)
    ap.add_argument("--delay-min", type=float, default=15.0)
    ap.add_argument("--delay-max", type=float, default=25.0)
    a = ap.parse_args()
    if a.cmd == "launch":
        launch()
    elif a.cmd == "probe":
        probe()
    elif a.cmd == "build":
        build()
    else:
        harvest(a.max_pages, a.start_page, a.delay_min, a.delay_max)
