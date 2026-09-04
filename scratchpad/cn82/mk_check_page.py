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
                    "MusicalMap_35組無英文劇名_2026-09-04")

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
        files = sorted(glob.glob(os.path.join(DEST, "圖", safe, "*")))
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

        if files:
            shots = []
            for i, f in enumerate(files):
                uri, size = thumb(f, W_MAIN if i == 0 else W_REST,
                                  Q_MAIN if i == 0 else Q_REST)
                rel = "圖/%s/%s" % (safe, os.path.basename(f))
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
            imgs = '<div class="shots">%s</div>' % "".join(shots)
            warn = ""
        else:
            imgs = ""
            warn = ('<p class="warn">🚨 <b>這一組我手上沒有存圖</b>——它不是大麥來源,'
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
<title>35 組「官方沒給英文劇名」複查</title>
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
<header><h1>35 組「官方沒給英文劇名」複查</h1>
<p class="sub">MusicalMap 中國原創批次 · 2026-09-04 · 共 __NG__ 組 / __NI__ 張圖</p></header>

<div class="note">
<b>這一頁在確認什麼。</b>中國原創批次我逐張讀圖收集官方英文劇名,結論是 41 組有、
<b>這 35 組官方確實沒給</b>,所以一律不收(絕不自創:《花木兰》不可拿迪士尼 Mulan、
《黑旗令》不可自造 Black Flag Order)。<br>
<b>但「讀圖」是整條鏈上最主觀、最沒有第二道把關的一步。</b>同一批裡《当你心动时》
海報上明明印著 Heart Shake,我判定為「有」卻收集完沒接進管線,是你一眼看出來的。
所以「判定為沒有」的這 35 組更需要你親自看,而不是相信我的結論。<br>
<b>每一組都攤開三樣東西:</b>完整售票連結(可直接開官方頁)、我當初的判定依據逐字照錄、
以及我手上全部的存圖。縮圖點下去會開<b>同資料夾裡的原圖</b>(可放大逐字看)。<br>
<b>🚨 有 4 組我手上沒有存圖</b>(我那长乐塬、羊角尖、花木兰、貂蝉 你在想什么)——
它們不是大麥來源,當初是讀文字頁做的判定,<b>證據較弱</b>,那幾組請務必點連結親自看海報。
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
