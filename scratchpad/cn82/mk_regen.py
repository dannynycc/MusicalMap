# -*- coding: utf-8 -*-
"""第二輪:用【官方事實】約束重生成。

SOP §1 說第一輪 prompt 只釘身份不餵劇情 —— 那是為了讓查證獨立。
查證做完之後(§3),就可以也【應該】把官方事實寫進 prompt 重生成:此時官方原文
已經是我親自從官方物料讀來的 ground truth,拿它約束產出不是球員兼裁判,
而是把 Perplexity 的語感套在正確的事實上(Perplexity=主體、我=事實校對)。

🚨 第一輪實測(中國批)為什麼幾乎每組都要重生成:
   《东南望》主角名寫成「陳啟正」(官方 陈启耀),還編出「同鄉會之託攜回抗戰資金交給地下組織」;
   《亡灵之旅》寫成「登上冥河之舟」(冥河是希臘神話),並直接點破官方刻意保留的身份懸念。
   這些劇太冷門,Perplexity 沒有資料時會拿題材相近的通用想像頂替。

用法: python scratchpad/cn82/mk_regen.py <lang> <只要這些組的清單.json|all>
輸出: scratchpad/cn82/regen_<lang>_list.json + regen_<lang>_order.json
"""
import io
import json
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
BASE = "scratchpad/cn82"
SUF = {"zh-hant": "zht", "zh-hans": "zhs", "en": "en"}


try:
    from opencc import OpenCC
    # s2tw = 台灣字形(為/裡),s2t 會給異體字(爲/裏);
    # 不用 s2twp —— 那會連詞彙一起換(網絡→網路、軟件→軟體),會改掉官方用語。
    _s2t = OpenCC("s2tw").convert
except Exception:
    sys.stderr.write("::warning::opencc 不可用,繁中 prompt 不會轉繁體,專有名詞會混簡體\n")

    def _s2t(x):
        return x


def build(g, e, idt, lang):
    """身份 + 官方事實。官方原文【原樣附上】,不改寫 —— 我改寫就等於我在編。

    🚨 但【字形要跟著目標語言】:官方原文是簡體,直接餵給繁中生成,模型會照抄簡體專有名詞,
       產出「维塔在稱量法庭交出心臟」這種簡繁混雜的稿(實測《亡灵之旅》就是這樣)。
       所以做 zh-hant 時,把餵進 prompt 的事實先 s2t 轉成繁體字形 ——
       只轉【字形】不轉詞彙(用 s2t 不用 s2twp),避免把官方用語改掉。
       ⚠ 只轉 prompt 裡的副本,ledger 裡的官方原文一律保持原樣不動。
    """
    plot = (e.get("official_plot") or "").strip()
    ext = (e.get("external_plot") or {}).get("text", "").strip()
    chars = (e.get("characters") or "").strip()
    if lang == "zh-hant":
        plot, ext, chars = _s2t(plot), _s2t(ext), _s2t(chars)
    # 🚨 2026-09-04 實測:把官方資料排成【標題+換行】的長 prompt,會讓 Perplexity 切換成
    #    「研究報告」模式 —— 產出 Markdown 表格、分節標題、巡演場次清單,完全不是簡介
    #    (《#0528》實測回了 1100~1400 字的報告)。改法:
    #    (a) 壓成【單行】,不用標題也不用換行;(b) 把「改寫成一段簡介」的任務講在最前面;
    #    (c) 角色欄只取我標了 🚨 / 不可 的關鍵限制句,不要整段搬進去。
    ident = idt.split("。⚠ 请只描述")[0].strip()
    facts = (plot or ext).replace("\n", " ")
    warn = " ".join(x.strip() for x in re.split(r"[。\n]", chars)
                    if ("🚨" in x or "不可" in x or "絕不" in x or "绝不" in x))
    body = ("請把下面這段【已知資料】改寫成一段給觀眾看的劇情簡介,寫成通順的文章。"
            "只能用這段資料裡有的內容,不要補寫任何它沒說的情節、地點、人物關係或結局;"
            "人名與專有名詞一字不改照抄。資料:" + facts)
    if warn:
        body += " 另外這些限制務必遵守:" + warn.replace("\n", " ")
    # 🚨 2026-09-04 設計衝突:px_gen 的 has_summary() 要求最後獨立一段做【主題性收束】
    #    (要出現「意義/主題/不只是/明白…」這類詞),但我上面說「不要補寫資料沒說的」——
    #    兩者互斥,實測第一次嘗試就 sum=N,再不處理會讓每一篇都跑滿 7 次重試。
    #    解法:明確允許結尾寫一段【只從既有素材收束】的短總結,不得引入新事實。
    # 🚨 has_summary() 是【關鍵字比對】,不是語意判斷:結尾段寫得再好,只要沒出現
    #    「全劇/主題/意義/叩問/道出/探討/不只是…」這類詞就會判 False,然後跑滿 7 次重試。
    #    實測《亡灵之旅》結尾寫「究竟意味著永生、重逢,還是更艱難的考驗?」——文意完全正確卻沒過。
    #    所以要直接告訴它可用的收尾詞,而不是讓它猜。
    body += ("最後請獨立成段收束全劇,兩到三句,只能從上面資料已有的內容去點出主題,"
             "【不可帶入任何新的人物、情節或結局】;這一段請用「全劇」開頭,"
             "或在句中用到「主題」「意義」「叩問」「道出」「探討」「不只是」其中一個詞。"
             " (不要提到這段資料本身,不要寫『根據官方』,不要用表格或小標題。)")
    return ident + " —— " + body


def main():
    lang = sys.argv[1]
    only = sys.argv[2] if len(sys.argv) > 2 else "all"
    led = json.load(io.open(BASE + "/ledger.json", encoding="utf-8"))
    ident = json.load(io.open(BASE + "/identity.json", encoding="utf-8"))
    order = json.load(io.open(BASE + "/order.json", encoding="utf-8"))
    pick = order if only == "all" else json.load(io.open(only, encoding="utf-8"))
    out_order, out_list, skipped = [], [], []
    for g in pick:
        e = led[g]
        if not ((e.get("official_plot") or "").strip()
                or (e.get("external_plot") or {}).get("text")):
            skipped.append(g)          # 沒有事實可約束就別重生成,交給人工外部查證
            continue
        out_order.append(g)
        out_list.append(build(g, e, ident[g]["identity"], lang))
    suf = SUF[lang]
    json.dump(out_order, io.open("%s/regen_%s_order.json" % (BASE, suf), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    json.dump(out_list, io.open("%s/regen_%s_list.json" % (BASE, suf), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print("重生成清單 %s:%d 組" % (lang, len(out_order)))
    if skipped:
        print("⚠ 沒有官方/外部劇情可約束,【不重生成】的 %d 組:%s" % (len(skipped), skipped))
    return 0


raise SystemExit(main())
