# -*- coding: utf-8 -*-
"""
audit_visitor.py — 公開分享頁「登出訪客」路徑稽核（上線前跑）。

為什麼要有這支：
  分享頁 /<handle> 對「登入的擁有者」走 me.html、對「登出訪客」走 u-view.js，
  是兩條不同的 render 路徑。用登入狀態測會看到滿的、以為沒事，但訪客可能整頁掛
  （2026-07-16 就踩過：CITYZH TDZ crash、#pub-empty 永遠顯示、自訂海報代理 504）。
  本機用乾淨匿名 Chrome 載 u.html?u=<handle>（localhost 不轉址、無登入無快取）＝
  就是真正的訪客路徑，抓 console error / 未捕捉例外 / 破圖 / 失敗資源。

用法：
  python scripts/audit_visitor.py                 # 對 danny 跑真資料 + 邊緣資料
  python scripts/audit_visitor.py --handle alice   # 換一個公開 handle
  python scripts/audit_visitor.py --port 8901
  離開碼 0 = 乾淨；1 = 有 page error / console error（可接進 CI/pre-push）。

需求：pip install playwright ; python -m playwright install chromium
"""
import sys, io, json, argparse, subprocess, time, threading, functools, http.server, socketserver, os

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOISE = ('cloudflareinsights', 'google-analytics', 'ERR_FAILED', 'ERR_ABORTED', 'CORS', 'preflight')  # localhost 打不到分析端點，非 bug


class _QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a, **k):  # 別把每個 GET 都印出來
        pass


def serve(port):
    handler = functools.partial(_QuietHandler, directory=REPO)
    httpd = socketserver.TCPServer(("127.0.0.1", port), handler)
    t = threading.Thread(target=httpd.serve_forever, daemon=True); t.start()
    return httpd


def real_data_audit(pw, base, handle):
    """真 handle：三語 + 互動 + 查無帳號。回傳問題數。"""
    langs = [("繁中", ""), ("英文", "&hl=en"), ("簡中", "&hl=zh-hans")]
    issues = 0
    b = pw.chromium.launch(headless=True)
    for label, q in langs:
        ctx = b.new_context(); pg = ctx.new_page()
        ce, pe = [], []
        pg.on("console", lambda m: ce.append(m.text) if m.type == 'error' and not any(k in m.text for k in NOISE) else None)
        pg.on("pageerror", lambda e: pe.append(str(e)))
        pg.goto("%s/u.html?u=%s%s" % (base, handle, q), wait_until="load", timeout=45000)
        pg.wait_for_timeout(6000)
        # 互動：切分頁、開海報詳情
        for t in ["護照", "清單", "Passport", "List", "海報牆"]:
            try:
                el = pg.query_selector("text=%s" % t)
                if el: el.click(timeout=2500); pg.wait_for_timeout(900)
            except Exception: pass
        try:
            c = pg.query_selector("#wall-poster .card, #wall-poster button")
            if c: c.click(timeout=2500); pg.wait_for_timeout(1200); pg.keyboard.press("Escape")
        except Exception: pass
        pg.wait_for_timeout(800)
        dom = pg.evaluate("()=>({shows:(window.MM&&MM.shows)?MM.shows.length:'?', pubEmpty:(function(){var e=document.getElementById('pub-empty');return e?getComputedStyle(e).display!=='none':'no';})(), realBroken:[...document.querySelectorAll('#wall-poster img')].filter(i=>i.complete&&i.naturalWidth===0).length})")
        bad = len(pe) + len(ce)
        issues += bad
        print("  [%s] shows=%s pubEmpty=%s wallBroken=%d  → %s" % (label, dom['shows'], dom['pubEmpty'], dom['realBroken'], "OK" if bad == 0 else "❌%d" % bad))
        for e in pe[:6]: print("       !! PAGE ERROR:", e[:180])
        for e in ce[:6]: print("       -- CONSOLE:", e[:180])
        ctx.close()
    # 查無帳號
    ctx = b.new_context(); pg = ctx.new_page(); ce, pe = [], []
    pg.on("console", lambda m: ce.append(m.text) if m.type == 'error' and not any(k in m.text for k in NOISE) else None)
    pg.on("pageerror", lambda e: pe.append(str(e)))
    pg.goto("%s/u.html?u=zzz_nonexistent_handle" % base, wait_until="load", timeout=45000); pg.wait_for_timeout(5000)
    d = pg.evaluate("()=>({pubEmpty:(function(){var e=document.getElementById('pub-empty');return e?getComputedStyle(e).display!=='none':'no';})()})")
    ok = d['pubEmpty'] is True and not pe and not ce
    issues += (0 if ok else 1) + len(pe) + len(ce)
    print("  [查無帳號] 顯示空狀態=%s errors=%d → %s" % (d['pubEmpty'], len(pe) + len(ce), "OK" if ok else "❌"))
    ctx.close(); b.close()
    return issues


def edge_audit(pw, base):
    """攔截 Supabase，灌合成極端資料，測 u-view render 不炸。回傳問題數。"""
    def row(**kw):
        base_r = dict(id=1, title="Test", venue="Theatre", city="Taipei", country="Taiwan", lat=25.0, lng=121.5,
                      seen_date="2015-04-18", precision="day", seat=None, price=None, currency=None, url=None,
                      links=None, poster_override=None, production_key=None, rating=0, fav=False)
        base_r.update(kw); return base_r
    cases = {
        "0場": [], "1場": [row(id=1)],
        "2場(persona<3)": [row(id=1), row(id=2, seen_date="2016-01-01")],
        "全未來": [row(id=i, seen_date="2099-0%d-01" % i) for i in range(1, 4)],
        "欄位全空null": [row(id=i, venue=None, city=None, country=None, lat=None, lng=None, seen_date=None, precision="none") for i in range(1, 5)],
        "空字串標題": [row(id=i, title="", city="", venue="") for i in range(1, 5)],
        "怪符號/emoji/超長": [row(id=1, title='A"B<script>\''), row(id=2, title="🎭" * 30, city="長" * 60), row(id=3, title="O'B & \"S\"")],
        "重看5次": [row(id=i, title="Phantom") for i in range(1, 6)],
        "評分最愛極端": [row(id=1, rating=5, fav=True), row(id=2, rating=None, fav=None), row(id=3, rating=0)],
    }

    def mk(rows):
        def h(route):
            u = route.request.url
            if "/rest/v1/profiles" in u:
                route.fulfill(status=200, content_type="application/json", body=json.dumps([{"id": "edge", "display_name": "EdgeTest", "is_public": True}]))
            elif "public_sightings" in u:
                route.fulfill(status=200, content_type="application/json", body=json.dumps(rows))
            else:
                route.continue_()
        return h

    issues = 0
    b = pw.chromium.launch(headless=True)
    for name, rows in cases.items():
        ctx = b.new_context(); pg = ctx.new_page(); ce, pe = [], []
        pg.on("console", lambda m: ce.append(m.text) if m.type == 'error' and not any(k in m.text for k in NOISE) else None)
        pg.on("pageerror", lambda e: pe.append(str(e)))
        pg.route("**/rest/v1/**", mk(rows))
        try:
            pg.goto("%s/u.html?u=edgetest" % base, wait_until="load", timeout=45000); pg.wait_for_timeout(3500)
        except Exception as e:
            pe.append("goto:" + str(e)[:120])
        bad = len(pe) + len(ce)
        issues += bad
        print("  [%-18s] → %s" % (name, "OK" if bad == 0 else "❌%d" % bad))
        for e in pe[:5]: print("       !! PAGE ERROR:", e[:180])
        for e in ce[:5]: print("       -- CONSOLE:", e[:180])
        ctx.close()
    b.close()
    return issues


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--handle", default="danny")
    ap.add_argument("--port", type=int, default=8899)
    ap.add_argument("--base", default=None, help="不自架 server，直接對此 base 測")
    a = ap.parse_args()
    from playwright.sync_api import sync_playwright
    httpd = None
    base = a.base
    if not base:
        httpd = serve(a.port); base = "http://127.0.0.1:%d" % a.port; time.sleep(1)
    print("=== 訪客路徑稽核  base=%s  handle=%s ===" % (base, a.handle))
    total = 0
    with sync_playwright() as pw:
        print("\n[1] 真資料 · 三語 + 互動 + 查無帳號")
        total += real_data_audit(pw, base, a.handle)
        print("\n[2] 合成極端資料 · 10 案")
        total += edge_audit(pw, base)
    if httpd: httpd.shutdown()
    print("\n================ 結果 ================")
    print("問題總數 =", total, "→", "✅ 訪客路徑乾淨" if total == 0 else "❌ 有問題，別上線")
    sys.exit(0 if total == 0 else 1)


if __name__ == "__main__":
    main()
