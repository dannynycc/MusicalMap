# -*- coding: utf-8 -*-
"""產生「35 組官方沒給英文劇名」的人工複查頁(輸出到桌面資料夾)。

為什麼要有這一頁:我判定這 35 組「官方沒有英文劇名」的依據是【我逐張讀圖】,
而讀圖是這條鏈上最主觀、最沒有第二道把關的一步——2026-09-04 使用者一眼就發現
《当你心动时》海報上印著 Heart Shake(那組我判定為「有」,但收集完沒接進管線)。
所以「判定為沒有」的這 35 組更需要人親自看,而不是相信我的結論。

🚨 頁面設計上的兩個要求:
1. 縮圖一律【內聯成 base64】——桌面 HTML 若用 file:// 或外部路徑,常常整頁空白。
   內聯後不管怎麼開都看得到圖。
2. 每張縮圖同時連到【同資料夾裡的原圖】(相對路徑),要放大逐字看時一鍵就到。

用法: python scratchpad/cn82/mk_check_page.py
"""
import base64
import glob
import html
import io
import json
import os

from PIL import Image

sys_out = io.TextIOWrapper(__import__("sys").stdout.buffer, encoding="utf-8")
B = "scratchpad/cn82"
DEST = os.path.join(os.path.expanduser("~"), "Desktop",
                    "MusicalMap_33組無英文劇名_複查v2_2026-09-04")

# 🚨 v2 新增【主視覺】區。v1 只放詳情圖,而 2026-09-04 使用者抓到的 5 個錯【全部】在主視覺上
#    ——我的抓圖從來沒收過大麥商品頁的主視覺(全批 608 張裡 /bao/uploaded/ 型 0 張),
#    所以 v1 的複查頁根本沒把關鍵證據放進去。主視覺排在最前面、給最大版面。

# 主視覺給大一點(英文劇名多半印在這張),其餘只要看得出有沒有拉丁字就夠
# 一律同尺寸:實測 _0 不一定是主視覺(《0528》的 _0 是購票須知,主視覺在 _2),
# 猜哪張是主視覺會把大版面給錯圖。420px 對 1181 寬的原圖約 36%,
# 足以看出「有沒有拉丁字」而決定要不要點開原圖逐字看。
W_MAIN, Q_MAIN = 420, 68
W_REST, Q_REST = 420, 68
H_CAP = 2600          # 詳情長圖動輒上萬 px,縮圖再高也沒意義,超過就等比再縮


def thumb(path, width, quality):
    """回傳 (data_uri, 原圖尺寸字串)。失敗回 (None, 錯誤訊息)。"""
    try:
        im = Image.open(path)
        ow, oh = im.size
        if im.mode not in ("RGB", "L"):
            im = im.convert("RGB")
        w = min(width, ow)
        h = int(oh * w / ow)
        if h > H_CAP:                      # 太長的再等比縮一次
            h = H_CAP
            w = max(1, int(ow * h / oh))
        im = im.resize((w, h), Image.LANCZOS)
        buf = io.BytesIO()
        im.save(buf, "JPEG", quality=quality, optimize=True)
        b64 = base64.b64encode(buf.getvalue()).decode("ascii")
        return "data:image/jpeg;base64," + b64, "%d×%d" % (ow, oh)
    except Exception as ex:
        return None, str(ex)


def main():
    led = json.load(io.open(B + "/ledger.json", encoding="utf-8"))
    rep = json.load(io.open(B + "/_chk_links.json", encoding="utf-8"))
    groups = list(rep.keys())

    cards = []
    total_img = 0
    for idx, g in enumerate(groups, 1):
        e = led[g]
        safe = g.replace(" ", "_").replace("/", "_")
        files = sorted(glob.glob(os.path.join(DEST, "詳情圖", safe, "*")))
        total_img += len(files)

        # 我當初的判定原文——攤開來讓人對照,不是要人相信結論
        basis = html.escape(e.get("title_en_source") or "(帳本沒有記判定依據)")
        zh_title = html.escape(e.get("title") or g)

        # 平台標籤照【網域】判,不照來源檔判:china_poly.json 裡混有 damai 的搜尋頁,
        # 照檔案標會把它寫成「保利」。
        def plat_of(u):
            if "damai.cn" in u:
                return "大麥搜尋" if "/search" in u else "大麥"
            if "juooo" in u:
                return "聚橙"
            if "polyt" in u or "poly" in u:
                return "保利"
            return "官方"

        rows = rep[g]
        # 同一齣戲常有十幾個場次連結(《0528》13 個),看海報用不到那麼多:留 4 個,其餘摺疊
        head, rest = rows[:4], rows[4:]
        lk = "".join(
            '<a class="lk" href="%s" target="_blank" rel="noreferrer">%s ↗ <span>%s</span></a>'
            % (html.escape(u), plat_of(u), html.escape(u))
            for _p, u, _t in head)
        if rest:
            lk += ('<details class="more"><summary>另有 %d 個場次連結</summary>%s</details>'
                   % (len(rest), "".join(
                       '<a class="lk" href="%s" target="_blank" rel="noreferrer">%s ↗ <span>%s</span></a>'
                       % (html.escape(u), plat_of(u), html.escape(u))
                       for _p, u, _t in rest)))

        posters = sorted(glob.glob(os.path.join(DEST, "主視覺", safe, "*")))
        if posters:
            pshots = []
            for f in posters:
                uri, size = thumb(f, 560, 80)
                rel = "主視覺/%s/%s" % (safe, os.path.basename(f))
                name = html.escape(os.path.basename(f))
                if uri:
                    pshots.append('<figure class="poster"><a href="%s" target="_blank">'
                                  '<img src="%s" loading="lazy" alt="%s"></a>'
                                  '<figcaption>%s<br><span>%s</span></figcaption></figure>'
                                  % (html.escape(rel), uri, name, name, html.escape(size)))
            pblock = ('<h3 class="sec">主視覺海報 %d 張 <em>——使用者抓到的 5 個錯全部在這裡,'
                      'v1 複查頁沒放這一區</em></h3><div class="shots">%s</div>'
                      % (len(posters), "".join(pshots)))
        else:
            pblock = '<p class="warn">⚠ 這一組沒有主視覺海報(售票資料的 image 欄是空的)。</p>'

        if files:
            shots = []
            for i, f in enumerate(files):
                uri, size = thumb(f, W_MAIN if i == 0 else W_REST,
                                  Q_MAIN if i == 0 else Q_REST)
                rel = "詳情圖/%s/%s" % (safe, os.path.basename(f))
                name = html.escape(os.path.basename(f))
                if uri:
                    shots.append(
                        '<figure class="%s"><a href="%s" target="_blank">'
                        '<img src="%s" loading="lazy" alt="%s"></a>'
                        '<figcaption>%s<br><span>%s</span></figcaption></figure>'
                        % ("main" if i == 0 else "", html.escape(rel), uri, name, name,
                           html.escape(size)))
                else:
                    shots.append('<figure><div class="err">讀不到:%s</div></figure>' % name)
            imgs = (pblock + '<h3 class="sec">詳情圖 %d 張</h3><div class="shots">%s</div>'
                    % (len(files), "".join(shots)))
            warn = ""
        else:
            imgs = pblock
            warn = ('<p class="warn">⚠ <b>這一組沒有詳情圖存檔</b>——它不是大麥來源,'
                    '當初是讀該平台的<b>文字頁</b>做的判定,沒有逐張看過主視覺。'
                    '也就是說「官方沒給英文劇名」這個結論在這一組<b>證據較弱</b>,'
                    '請務必點開上面的連結親自看海報。</p>')

        cards.append(
            '<section id="g%d"><h2><span class="no">%02d</span> %s '
            '<code>%s</code> <span class="cnt">%d 張圖</span></h2>'
            '<div class="links">%s</div>%s'
            '<details open><summary>我當初的判定依據(逐字照錄帳本)</summary>'
            '<p class="basis">%s</p></details>%s</section>'
            % (idx, idx, zh_title, html.escape(g), len(files), lk, warn, basis, imgs))

    nav = " ".join('<a href="#g%d">%02d %s</a>' % (i, i, html.escape(g))
                   for i, g in enumerate(groups, 1))

    doc = """<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>33 組「官方沒給英文劇名」複查 v2</title>
<style>
:root{--bg:#faf8f3;--card:#fff;--ink:#23201b;--mut:#7a736a;--line:#e5ded1;--accent:#0f6b5c;--warn:#b3261e}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);
 font:15px/1.75 "Noto Sans TC","PingFang TC","Microsoft JhengHei",system-ui,sans-serif}
header{position:sticky;top:0;z-index:9;background:rgba(250,248,243,.97);
 border-bottom:1px solid var(--line);padding:14px 22px}
h1{margin:0 0 4px;font-size:19px;letter-spacing:.02em}
.sub{color:var(--mut);font-size:13px;margin:0}
.note{max-width:none;margin:14px 22px 0;padding:14px 16px;background:#fff8e6;
 border:1px solid #e8d9a8;border-radius:8px;font-size:13.5px;line-height:1.8}
.note b{color:#8a5a00}
nav{margin:12px 22px 0;font-size:12px;line-height:2.1}
nav a{color:var(--mut);text-decoration:none;margin-right:10px;white-space:nowrap}
nav a:hover{color:var(--accent);text-decoration:underline}
main{padding:8px 22px 60px}
section{background:var(--card);border:1px solid var(--line);border-radius:10px;
 margin:18px 0;padding:18px 20px}
h2{margin:0 0 10px;font-size:17px;display:flex;align-items:baseline;gap:10px;flex-wrap:wrap}
.no{color:var(--accent);font-variant-numeric:tabular-nums;font-size:14px}
h2 code{background:#f1ece1;padding:2px 7px;border-radius:4px;font-size:12px;color:var(--mut)}
.cnt{margin-left:auto;color:var(--mut);font-size:12px;font-weight:400}
.links{display:flex;flex-direction:column;gap:5px;margin-bottom:10px}
.lk{color:var(--accent);text-decoration:none;font-size:13px;word-break:break-all}
.lk span{color:var(--mut);font-size:11.5px}
.lk:hover{text-decoration:underline}
details{border-top:1px dashed var(--line);padding-top:9px;margin-top:4px}
summary{cursor:pointer;font-size:12.5px;color:var(--mut)}
.basis{margin:8px 0 0;font-size:13px;background:#f7f4ed;padding:11px 13px;
 border-radius:6px;border-left:3px solid var(--line);white-space:pre-wrap}
.warn{margin:10px 0;padding:11px 13px;background:#fdecea;border-left:3px solid var(--warn);
 border-radius:6px;font-size:13px}
.shots{display:flex;flex-wrap:wrap;gap:14px;margin-top:14px;align-items:flex-start}
figure{margin:0;max-width:420px}
figure.main{max-width:420px}
figure.poster{max-width:560px}
h3.sec{font-size:13px;color:var(--accent);margin:16px 0 2px;border-top:1px solid var(--line);padding-top:10px}
h3.sec em{color:var(--mut);font-style:normal;font-weight:400}
.more summary{margin:2px 0 4px}
figure img{width:100%;display:block;border:1px solid var(--line);border-radius:6px;background:#fff}
figcaption{font-size:11px;color:var(--mut);margin-top:4px;word-break:break-all}
figcaption span{opacity:.7}
.err{font-size:12px;color:var(--warn)}
@media (prefers-color-scheme:dark){
 :root{--bg:#17150f;--card:#201d16;--ink:#ece6da;--mut:#9a9184;--line:#372f22}
 header{background:rgba(23,21,15,.97)}
 .note{background:#2a2314;border-color:#4a3d20}.note b{color:#e0b45a}
 .basis{background:#191610}
 .warn{background:#2c1614}
 h2 code{background:#2a2419}
}
</style></head><body>
<header><h1>33 組「官方沒給英文劇名」複查 <span style="color:#b3261e">v2</span></h1>
<p class="sub">MusicalMap 中國原創批次 · 2026-09-04 · 共 __NG__ 組 / __NI__ 張圖</p></header>

<div class="note">
<b>v1 有嚴重缺陷,這是修正後的 v2。</b>使用者在 v1 之後指出四齣戲的海報上明明印著英文劇名。
查下去發現根因:<b>我的抓圖從來沒收過大麥商品頁的【主視覺海報】</b>——只收了詳情圖,
全批 82 組 608 張圖裡主視覺型<b>0 張</b>。而主視覺正是英文劇名最常印的地方,
URL 其實一直躺在我們自己的售票資料的 image 欄裡。<b>v1 這一頁因此根本沒放關鍵證據。</b><br>
重抓 35 組共 105 張主視覺逐張看完,<b>35 組裡我判錯 5 組</b>(錯誤率 14%):
喜欢你 <b>I like you</b>(9 張主視覺每一張都有)、玉良 <b>Pan Yu Lin</b>、
空中花园谋杀案 <b>THE MURDER OF HANGING GARDEN</b>、渡河 渡河 <b>The Other Shore</b>、
花木兰 <b>Mu Lan</b>。前四組已上線;花木兰不收(那個英文名屬於已結束的另一個製作)。<br>
<b>🚨 其中《玉良》最該檢討:</b>我帳本自己寫著「尚未逐張看主視覺 → 未確認」,
我卻把它歸進「官方【確實】沒給」——明知沒查完卻當成查過。<br>
<b>剩下這 33 組每一組都攤開四樣:</b>完整售票連結、我當初的判定依據逐字照錄、
<b>主視覺海報(v1 沒有的那一區,排在最前面)</b>、以及全部詳情圖。
縮圖點下去開同資料夾的原圖,可放大逐字看。<br>
⚠ 我判定「有英文字但不是劇名」的三組請特別看:<b>去你的夏天</b>(手寫花體單字 Back)、
<b>嗜血博士</b>(手寫小寫 doc/tor)、<b>邦尼帮你</b>(musical 標章與裝飾關鍵字邊框)——
這些是<b>我的判斷,不是官方陳述</b>,你可以推翻。
另外<b>觉醒年代</b>海報上的 LA JEUNESSE 是法文,且是劇中道具《新青年》雜誌的法文刊名,不是本劇英譯。
</div>

</div>

<nav>__NAV__</nav>
<main>__CARDS__</main>
</body></html>"""
    doc = (doc.replace("__NG__", str(len(groups)))
              .replace("__NI__", str(total_img))
              .replace("__NAV__", nav)
              .replace("__CARDS__", "".join(cards)))
    out = os.path.join(DEST, "檢查表.html")
    io.open(out, "w", encoding="utf-8").write(doc)
    sys_out.write("寫出 %s (%.1f MB)\n" % (out, os.path.getsize(out) / 1e6))
    sys_out.write("%d 組 / %d 張圖\n" % (len(groups), total_img))
    sys_out.flush()
    return 0


raise SystemExit(main())
