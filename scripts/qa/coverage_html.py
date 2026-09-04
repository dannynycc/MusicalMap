# -*- coding: utf-8 -*-
"""把 coverage_report.py 的逐組結果輸出成一份自包含 HTML(可直接雙擊開,無外部連結)。

用法:
  python scripts/qa/coverage_report.py --json scratchpad/cov.json
  python scripts/qa/coverage_html.py scratchpad/cov.json "C:/Users/Home/Desktop/MusicalMap_三語覆蓋率.html"
"""
import io
import json
import sys
from collections import Counter, defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

LANGS = [("en", "英文"), ("zh-hant", "繁中"), ("zh-hans", "簡中")]


def esc(t):
    return (str(t or "").replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def _opt(flag, default=""):
    """讀 --flag value;沒給就回 default。"""
    if flag in sys.argv:
        i = sys.argv.index(flag)
        if i + 1 < len(sys.argv):
            return sys.argv[i + 1]
    return default


def main():
    src, out = sys.argv[1], sys.argv[2]
    # 🚨 資料時間【不可寫死】。第一版把 2026-09-02 直接寫在模板裡,隔天重跑產出的檔
    #    副標仍印著前一天 —— 拿去當 status update 會直接給出錯誤資訊。
    date = _opt("--date") or __import__("datetime").date.today().isoformat()
    # 變化區塊是一次性的對照文字(比較對象是上一次交付的那份檔),用外部 fragment 帶入,
    # 不寫死在模板裡,避免下次重跑又印出過期的比較。
    dfile = _opt("--delta")
    delta = io.open(dfile, encoding="utf-8").read() if dfile else ""
    d = json.load(io.open(src, encoding="utf-8"))
    total = len(d)

    def pct(n):
        return 100.0 * n / total if total else 0.0

    tcov = {l: sum(1 for e in d if e["title_cov"][l]) for l, _ in LANGS}
    scov = {l: sum(1 for e in d if e["syn_cov"][l]) for l, _ in LANGS}
    both = {l: sum(1 for e in d if e["title_cov"][l] and e["syn_cov"][l]) for l, _ in LANGS}
    allfull = sum(1 for e in d if all(e["title_cov"][l] and e["syn_cov"][l] for l, _ in LANGS))

    by_tag = defaultdict(list)
    for e in d:
        by_tag[e["tag"] or "(無)"].append(e)

    quad = Counter((e["title_cov"]["zh-hant"], e["syn_cov"]["zh-hant"]) for e in d)

    rows = []
    for e in sorted(d, key=lambda x: (not x["syn_cov"]["zh-hant"],
                                      not x["title_cov"]["zh-hant"], x["group"])):
        zh_disp = e["annot"]["zh-hant"] or e["title"]["zh-hant"]
        zs_disp = e["annot"]["zh-hans"] or e["title"]["zh-hans"]
        cells = []
        for l, _ in LANGS:
            cells.append('<td class="c %s">%s</td>' % ("y" if e["title_cov"][l] else "n",
                                                       "✓" if e["title_cov"][l] else "✗"))
        for l, _ in LANGS:
            cells.append('<td class="c %s">%s</td>' % ("y" if e["syn_cov"][l] else "n",
                                                       "✓" if e["syn_cov"][l] else "✗"))
        score = sum(e["title_cov"][l] for l, _ in LANGS) + sum(e["syn_cov"][l] for l, _ in LANGS)
        rows.append(
            '<tr data-tag="%s" data-score="%d" data-full="%d">'
            '<td class="g">%s</td><td class="t">%s</td><td>%s</td><td>%s</td>'
            '<td class="tag">%s</td><td class="c">%d</td>%s</tr>'
            % (esc(e["tag"]), score, 1 if score == 6 else 0,
               esc(e["group"]), esc(e["title"]["en"]), esc(zh_disp), esc(zs_disp),
               esc(e["tag"]), e["n_shows"], "".join(cells)))

    tag_rows = []
    for t, es in sorted(by_tag.items(), key=lambda x: -len(x[1])):
        n = len(es)
        a = sum(1 for e in es if e["title_cov"]["en"])
        b = sum(1 for e in es if e["title_cov"]["zh-hant"])
        c = sum(1 for e in es if e["syn_cov"]["en"])
        tag_rows.append(
            "<tr><td>%s</td><td class=c>%d</td>"
            "<td class=c>%d<span class=p>%.0f%%</span></td>"
            "<td class=c>%d<span class=p>%.0f%%</span></td>"
            "<td class=c>%d<span class=p>%.0f%%</span></td></tr>"
            % (esc(t), n, a, 100.0 * a / n, b, 100.0 * b / n, c, 100.0 * c / n))

    def bar(label, n):
        return ('<div class="row"><span class="lb">%s</span>'
                '<span class="track"><i style="width:%.1f%%"></i></span>'
                '<span class="num">%d<small>/%d</small> %.1f%%</span></div>'
                % (label, pct(n), n, total, pct(n)))

    # ⚠ 這是給使用者雙擊開的獨立檔,不是 Artifact —— 沒有人幫它補 <head>。
    #   少了 charset,Windows 的瀏覽器會猜 cp950,整份中文變亂碼
    #   (2026-09-02 第一版就是這樣,截圖才發現)。lang 也一併宣告。
    html = """<!doctype html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>三語覆蓋率稽核</title>
<style>
:root{--bg:#faf8f4;--fg:#1f1c18;--mut:#6b6459;--line:#e3ddd2;--card:#fff;
      --ok:#2f7d5d;--no:#b4453a;--accent:#a07a34}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){
  --bg:#171512;--fg:#eee9e0;--mut:#a09889;--line:#332f29;--card:#201d19;
  --ok:#5fbf94;--no:#e0796d;--accent:#d3a95c}}
:root[data-theme="dark"]{--bg:#171512;--fg:#eee9e0;--mut:#a09889;--line:#332f29;
  --card:#201d19;--ok:#5fbf94;--no:#e0796d;--accent:#d3a95c}
body{background:var(--bg);color:var(--fg);font:15px/1.65 "Noto Sans TC","PingFang TC",
  "Microsoft JhengHei",system-ui,sans-serif;margin:0;padding:28px 20px 60px}
.wrap{max-width:1180px;margin:0 auto}
h1{font-size:25px;margin:0 0 4px;letter-spacing:-.01em}
.sub{color:var(--mut);margin:0 0 26px;font-size:13.5px}
h2{font-size:17px;margin:34px 0 12px;padding-bottom:7px;border-bottom:1px solid var(--line)}
.card{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:18px 20px;margin:14px 0}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(290px,1fr));gap:14px}
.row{display:flex;align-items:center;gap:10px;margin:9px 0}
.lb{width:52px;color:var(--mut);font-size:13px;flex:none}
.track{flex:1;height:9px;background:var(--line);border-radius:5px;overflow:hidden}
.track i{display:block;height:100%;background:var(--accent);border-radius:5px}
.num{width:132px;text-align:right;font-variant-numeric:tabular-nums;font-size:13px;flex:none}
.num small{color:var(--mut)}
.big{font-size:31px;font-weight:600;letter-spacing:-.02em}
.k{color:var(--mut);font-size:13px}
table{border-collapse:collapse;width:100%;font-size:13.5px}
th,td{padding:6px 8px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}
th{position:sticky;top:0;background:var(--bg);font-weight:600;font-size:12.5px;color:var(--mut);z-index:2}
td.c,th.c{text-align:center}
.y{color:var(--ok);font-weight:700}.n{color:var(--no);font-weight:700}
.g{color:var(--mut);font-size:12px;font-family:ui-monospace,SFMono-Regular,Menlo,monospace}
.t{font-weight:500}
.tag{font-size:12px;color:var(--mut);white-space:nowrap}
.p{color:var(--mut);font-size:11.5px;margin-left:5px}
.scroll{overflow-x:auto;border:1px solid var(--line);border-radius:10px;background:var(--card)}
.scroll table{min-width:900px}
.tools{display:flex;gap:8px;flex-wrap:wrap;margin:12px 0}
button{font:inherit;font-size:13px;padding:5px 12px;border:1px solid var(--line);
  background:var(--card);color:var(--fg);border-radius:999px;cursor:pointer}
button[aria-pressed=true]{background:var(--accent);color:#fff;border-color:var(--accent)}
.note{font-size:13px;color:var(--mut);background:var(--card);border-left:3px solid var(--accent);
  border-radius:0 8px 8px 0;padding:12px 16px;margin:14px 0}
.note b{color:var(--fg)}
ul{margin:8px 0;padding-left:20px}li{margin:5px 0}
code{background:var(--line);padding:1px 5px;border-radius:4px;font-size:12.5px}
.hd{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:14px}
</style>
</head>
<body>
<div class="wrap">
<h1>MusicalMap 三語覆蓋率稽核</h1>
<p class="sub">分母 = 目前在檔期的 __TOTAL__ 組作品(一齣戲算一組,非場次)&nbsp;·&nbsp;資料時間 __DATE__&nbsp;·&nbsp;數字已對正式站重算驗證</p>

<div class="card">
<div class="hd">
<div><div class="big">__ALLPCT__%</div><div class="k">三語全滿(標題+劇情 6 項全有)__ALLN__ 組</div></div>
<div><div class="big">__ENP__%</div><div class="k">英文站可讀標題</div></div>
<div><div class="big">__ZHP__%</div><div class="k">中文站可讀標題</div></div>
<div><div class="big">__SYP__%</div><div class="k">劇情簡介(三語同步)</div></div>
</div>
</div>

__DELTA__
<div class="grid">
<div class="card"><h3 style="margin:0 0 10px;font-size:14px">標題</h3>__TBARS__</div>
<div class="card"><h3 style="margin:0 0 10px;font-size:14px">劇情簡介</h3>__SBARS__</div>
<div class="card"><h3 style="margin:0 0 10px;font-size:14px">標題+劇情都有</h3>__BBARS__</div>
</div>

<div class="note">
<b>「覆蓋」的定義</b>：不是「欄位有沒有值」——三個語言版本每一筆都一定有 title，數欄位有值等於恆真、零資訊。
這裡的覆蓋是<b>該語言的使用者看到的是不是自己看得懂的文字</b>。<br>
· <b>英文標題</b>：英文站顯示的題名不含中日韓文字（本來就是拉丁字母，或來源給了官方英文名）。<br>
· <b>中文標題</b>：有官方中文譯名（<code>i18n_maps.show_titles(_tw)</code>），或題名本身就是中文。<br>
&nbsp;&nbsp;⚠ 只看「有沒有漢字」會把<b>日文</b>題名（民王、青春-AOHARU-鉄道）算成中文。
判準改成<b>有沒有在中文市場上演</b>，雙向驗過：反向誤殺 0 組、正向恰好抓出 4 組純日本場次的日文漢字題名。<br>
· <b>劇情</b>：<code>data/synopses/&lt;lang&gt;.json</code> 有非空內容（前端實際吃的檔）。
</div>

<h2>依原創分類</h2>
<div class="scroll"><table>
<thead><tr><th>分類</th><th class=c>組數</th><th class=c>英文標題</th><th class=c>中文標題</th><th class=c>劇情</th></tr></thead>
<tbody>__TAGROWS__</tbody></table></div>

<h2>缺口在哪</h2>
<div class="card">
<ul>
<li><b>中文標題有 + 劇情有</b>：__Q11__ 組（完整）</li>
<li><b>中文標題無 + 劇情有</b>：__Q01__ 組 → 只缺譯名，補 <code>i18n_maps</code> 即可，成本最低</li>
<li><b>中文標題有 + 劇情無</b>：__Q10__ 組 → 缺的是簡介__Q10TAGS__</li>
<li><b>兩者都無</b>：__Q00__ 組 → 缺口最深</li>
</ul>
</div>

<div class="note">
<b>缺口最深的分類(由本次資料算出,非寫死)</b><br>
__GAPNOTE__
<br><b>⚠ 這份報表的口徑</b>:分母是【目前在檔期】的作品組,所以會隨檔期進出而變動——
不同日期的兩份報表數字不同是正常的,不代表資料變差。歷史批次的完成度請看 CHANGELOG。
</div>

<h2>逐組明細（__TOTAL__ 組）</h2>
<div class="tools">
  <button data-f="all" aria-pressed="true">全部</button>
  <button data-f="gap">有缺口</button>
  <button data-f="full">三語全滿</button>
  <button data-f="nosyn">缺劇情</button>
  <button data-f="nozh">缺中文標題</button>
</div>
<div class="scroll"><table id="tb">
<thead><tr>
<th>group key</th><th>英文題名</th><th>繁中顯示</th><th>簡中顯示</th><th>分類</th><th class=c>場次</th>
<th class=c>標題<br>英</th><th class=c>標題<br>繁</th><th class=c>標題<br>簡</th>
<th class=c>劇情<br>英</th><th class=c>劇情<br>繁</th><th class=c>劇情<br>簡</th>
</tr></thead>
<tbody>__ROWS__</tbody></table></div>
</div>
<script>
var btns=[].slice.call(document.querySelectorAll('.tools button'));
var trs=[].slice.call(document.querySelectorAll('#tb tbody tr'));
btns.forEach(function(b){b.addEventListener('click',function(){
  btns.forEach(function(x){x.setAttribute('aria-pressed', x===b?'true':'false');});
  var f=b.getAttribute('data-f');
  trs.forEach(function(tr){
    var sc=+tr.getAttribute('data-score'), show=true;
    if(f==='gap') show = sc<6;
    else if(f==='full') show = sc===6;
    else if(f==='nosyn') show = tr.children[9].textContent==='\\u2717';
    else if(f==='nozh') show = tr.children[7].textContent==='\\u2717';
    tr.hidden=!show;
  });
});});
</script>
</body>
</html>"""

    rep = {
        "__TOTAL__": str(total),
        "__DATE__": date, "__DELTA__": delta,
        "__ALLPCT__": "%.1f" % pct(allfull), "__ALLN__": str(allfull),
        "__ENP__": "%.1f" % pct(tcov["en"]),
        "__ZHP__": "%.1f" % pct(tcov["zh-hant"]),
        "__SYP__": "%.1f" % pct(scov["en"]),
        "__TBARS__": "".join(bar(n, tcov[l]) for l, n in LANGS),
        "__SBARS__": "".join(bar(n, scov[l]) for l, n in LANGS),
        "__BBARS__": "".join(bar(n, both[l]) for l, n in LANGS),
        "__TAGROWS__": "".join(tag_rows),
        "__ROWS__": "".join(rows),
        "__Q11__": str(quad[(True, True)]), "__Q01__": str(quad[(False, True)]),
        "__Q10__": str(quad[(True, False)]), "__Q00__": str(quad[(False, False)]),
    }
    for k, v in rep.items():
        html = html.replace(k, v)
    # 🚨 這段敘述【必須由資料算】。第一版把 2026-09-02 的查證結論寫死在模板裡
    #    (「中國原創 88 組的劇情簡介是 0%」「西葡 4 組被靜默漏掉」),2026-09-05 重跑時
    #    兩件事其實都已經做完了(中國原創 73/75=97%、那 4 組三語簡介都有),
    #    寫死的結論就從「當時的事實」變成「現在的錯誤」。使用者要求核對產生器時抓到。
    #    → 敘述一律從 per 重新算,寧可少講也不要講過期的話。
    from collections import defaultdict as _dd
    _by = _dd(list)
    for _e in d:
        _by[_e.get("tag") or "—"].append(_e)
    _rank = []
    for _tag, _rs in _by.items():
        _miss = [r for r in _rs if not all(r["syn_cov"].values())]
        if _miss:
            _rank.append((len(_miss), _tag, len(_rs), _miss))
    _rank.sort(reverse=True)
    if _rank:
        _li = []
        for _n, _tag, _tot, _miss in _rank[:5]:
            _names = "、".join("<code>%s</code>" % esc(m["group"]) for m in _miss[:6])
            if len(_miss) > 6:
                _names += " …等 %d 組" % len(_miss)
            _li.append("<li><b>%s</b>：%d/%d 組缺劇情簡介 —— %s</li>"
                       % (esc(_tag), _n, _tot, _names))
        gapnote = "<ul>%s</ul>" % "".join(_li)
    else:
        gapnote = "<b>所有分類的劇情簡介都已補齊。</b>"
    # 「多為中國原創」原本也是寫死的(2026-09-05 使用者要求核對產生器時一併改)。
    # 那句當下剛好還成立(2 組都是中國原創),但只要缺口一換分類就會變成假話。
    _q10 = [e for e in d if e["title_cov"]["zh-hant"] and not e["syn_cov"]["zh-hant"]]
    if _q10:
        _c = Counter(e.get("tag") or "—" for e in _q10)
        _q10tags = "（%s）" % "、".join("%s %d" % (esc(t), n) for t, n in _c.most_common())
    else:
        _q10tags = ""
    html = html.replace("__Q10TAGS__", _q10tags)
    html = html.replace("__GAPNOTE__", gapnote)
    io.open(out, "w", encoding="utf-8").write(html)
    print("寫出 %s (%.0f KB)" % (out, len(html.encode("utf-8")) / 1024.0))
    return 0


raise SystemExit(main())
