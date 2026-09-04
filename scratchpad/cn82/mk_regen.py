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


# 🚨 OpenCC 簡→繁在【專名】上會挑錯字。實測本批中招的:
#    范·米格伦→範(范是姓氏)、马丁·布雷德乌斯→佈(音譯用布)、周会珍→週(姓周)、
#    余永泽→餘(姓余)、于贝→於(姓于)、游亦→遊(姓游)、祝英台→祝英臺。
#    這些在【一般文句】裡多半是對的(之後/發生/這裡),所以不能全域改;
#    只能【在專名範圍內】把它們改回來。
NAME_FIX = {"範": "范", "佈": "布", "週": "周", "餘": "余", "於": "于", "遊": "游", "臺": "台",
            "嶽": "岳"}
# 🚨 2026-09-04 補:這張表只保護【角色名】,【地名沒有保護到】。
#    《流星之绊》官方寫「岳州府平江县」,s2tw 轉成「嶽州府」(嶽只有山的意思才對),
#    prompt 帶著錯字,生成稿就照抄。地名種類太多列不完,所以真正的把關放在產出端:
#    scripts/zht_glyph_norm.py 會把 嶽州/嶽陽/嶽父/嶽飛 改回岳,並且【不動】五嶽/山嶽/嶽麓。
SKIP_NAME = re.compile(r"[《》「」:：;;、/]|民歌|題材|题材|版本|卡司|官方|角色|演員|演员|飾|饰"
                       r"|沒有|没有|不可|絕不|绝不|的|身|稱|称|懸念|悬念|組織|组织|名字|月份"
                       r"|人物|主角|配角|泛稱|泛称|設定|设定")


def official_names(e):
    out = set()
    for blk in re.findall(r"【([^】]{1,300})】", e.get("characters") or ""):
        for x in re.split(r"[、]", blk):
            x = x.strip()
            if x and 1 < len(x) <= 24 and not SKIP_NAME.search(x):
                out.add(x)
    return out


def fix_name(converted):
    for a, b in NAME_FIX.items():
        converted = converted.replace(a, b)
    return converted


def s2tw_safe(text, names):
    """轉繁體,但【專名先抽出來單獨處理】,避免 OpenCC 把姓氏/音譯字挑錯。

    做法:長名字先換成佔位符 → 整段轉繁 → 佔位符換回「轉繁後再修正過的名字」。
    先處理長名字,避免短名字是長名字的子字串時先被吃掉。
    """
    names = sorted((n for n in names if len(n) >= 2), key=len, reverse=True)
    holder = {}
    for i, n in enumerate(names):
        if n in text:
            key = "\x00%d\x00" % i
            holder[key] = fix_name(_s2t(n))
            text = text.replace(n, key)
    text = _s2t(text)
    for k, v in holder.items():
        text = text.replace(k, v)
    return text


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
        names = official_names(e)
        plot = s2tw_safe(plot, names)
        ext = s2tw_safe(ext, names)
        chars = s2tw_safe(chars, names)
    # 🚨 2026-09-04 實測:把官方資料排成【標題+換行】的長 prompt,會讓 Perplexity 切換成
    #    「研究報告」模式 —— 產出 Markdown 表格、分節標題、巡演場次清單,完全不是簡介
    #    (《#0528》實測回了 1100~1400 字的報告)。改法:
    #    (a) 壓成【單行】,不用標題也不用換行;(b) 把「改寫成一段簡介」的任務講在最前面;
    #    (c) 角色欄只取我標了 🚨 / 不可 的關鍵限制句,不要整段搬進去。
    ident = idt.split("。⚠ 请只描述")[0].strip()
    facts = (plot or ext).replace("\n", " ")
    warn = " ".join(x.strip() for x in re.split(r"[。\n]", chars)
                    if ("🚨" in x or "不可" in x or "絕不" in x or "绝不" in x))
    # 🚨 「人名一字不改照抄」這句對中文稿是對的,對【英文稿】卻會把漢字原封不動留在英文正文裡
    #    ——實測《三风一树》英文稿寫成「武耀 ekes out a living…德厚 and 子敬」,英語讀者讀不了。
    #    它甚至蓋掉了 px_gen 英文 TAIL 本來就有的「非拉丁字系一律羅馬拼音」規則。
    #    所以這句要跟著語言換:英文=羅馬拼音,中文=照抄。
    if lang == "en":
        name_rule = ("專有名詞若是漢字,請一律轉成【漢語拼音】並首字母大寫(例如 武耀 → Wu Yao、"
                     "德厚 → De Hou),不要把漢字留在英文正文裡;但若資料裡本來就給了英文名或"
                     "外文原名(例如 July、Van Meegeren、Göring),就直接用那個英文/原文寫法。"
                     "普通名詞(不是人名的稱謂,如「老師」「爺爺」「當代畫家」)請意譯成英文,不要拼音。")
    else:
        # 🚨 2026-09-04:「一字不改照抄」對【中英並列】的名字會出事。官方常寫成
        #    「Queen of Spades 黑桃女王」「Edward 爱德华」「维塔 VITA」,模型會挑英文那半來寫,
        #    產出「不喜陽光的 Queen of Spades 以黑魔法遮蔽光源劍」這種中英混雜的中文稿。
        #    實測連續兩組中招(《嗜血博士》《爱丽丝奇境之旅》)。官方【劇情本文】用的是中文,
        #    中文稿就該用中文;只有官方【從頭到尾只給英文名】(July、Eggy、Stevie)才保留英文。
        name_rule = ("人名與專有名詞一字不改照抄。若資料把同一個角色寫成中英並列"
                     "(例如「Queen of Spades 黑桃女王」「Edward 爱德华」),中文稿一律"
                     "只用【中文名】,不要寫英文;只有資料【從頭到尾都只給英文名】的角色"
                     "(例如 July、Eggy、Stevie)才保留英文原樣。")
    body = ("請把下面這段【已知資料】改寫成一段給觀眾看的劇情簡介,寫成通順的文章。"
            "只能用這段資料裡有的內容,不要補寫任何它沒說的情節、地點、人物關係或結局;"
            + name_rule + "資料:" + facts)
    if warn:
        # 補上句號:限制句常以「…的卡司區」這種沒有標點的片段結尾,直接接下一段指示會黏成一句
        body += " 另外這些限制務必遵守:" + warn.replace("\n", " ").rstrip("。 ") + "。"
    # 🚨 2026-09-04 設計衝突:px_gen 的 has_summary() 要求最後獨立一段做【主題性收束】
    #    (要出現「意義/主題/不只是/明白…」這類詞),但我上面說「不要補寫資料沒說的」——
    #    兩者互斥,實測第一次嘗試就 sum=N,再不處理會讓每一篇都跑滿 7 次重試。
    #    解法:明確允許結尾寫一段【只從既有素材收束】的短總結,不得引入新事實。
    # 🚨 has_summary() 是【關鍵字比對】,不是語意判斷:結尾段寫得再好,只要沒出現
    #    「全劇/主題/意義/叩問/道出/探討/不只是…」這類詞就會判 False,然後跑滿 7 次重試。
    #    實測《亡灵之旅》結尾寫「究竟意味著永生、重逢,還是更艱難的考驗?」——文意完全正確卻沒過。
    #    所以要直接告訴它可用的收尾詞,而不是讓它猜。
    # ⚠ 收尾詞【必須跟著輸出語言】:英文稿的 has_summary() 檢查的是
    #   ultimately / at its heart / the show / explores / is not only… 這些英文線索,
    #   叫它用「全劇/主題/叩問」是中文詞,英文稿根本用不上 —— 實測英文第一篇就 sum=N。
    if lang == "en":
        body += ("最後請【用英文】獨立成段收束全劇,兩到三句,只能從上面資料已有的內容去點出主題,"
                 "【不可帶入任何新的人物、情節或結局】;這一段請用 \"The show\" 或 \"Ultimately\" 開頭,"
                 "或在句中用到 \"at its heart\"、\"explores\"、\"is not only ... but also\"、"
                 "\"a story of\" 其中一個說法。")
    else:
        body += ("最後請獨立成段收束全劇,兩到三句,只能從上面資料已有的內容去點出主題,"
                 "【不可帶入任何新的人物、情節或結局】;這一段請用「全劇」開頭,"
                 "或在句中用到「主題」「意義」「叩問」「道出」「探討」「不只是」其中一個詞。")
    body += " (不要提到這段資料本身,不要寫『根據官方』,不要用表格或小標題。)"
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
