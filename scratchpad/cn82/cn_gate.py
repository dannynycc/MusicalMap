# -*- coding: utf-8 -*-
"""第一層機械把關:拿生成稿對帳本的【官方角色表】比對。

🚨 這【不取代】逐篇人工通讀(SOP:自動掃描會一再誤放),只是先把最容易犯的錯撈出來。
冒煙測試(2 齣)就抓到兩種,兩種都在這裡設檢查:

 A. 官方角色名【一個都沒出現】= 很可能寫的是別齣戲
    (《Borderline》第一次生成寫成同名的美國劇,官方的 July/June/February 一個都沒有)
 B. 官方角色名是【英文/拉丁字母】的,生成稿卻整篇找不到那個英文字串 = 被中譯了
    (《#0528》官方只給 Eggy/Brandon/Doris,生成稿寫成艾吉/朵莉絲/布蘭登;
     《Borderline》官方要求保留英文月份,生成稿寫成茱萊/六月/二月)
 C. 帳本 🚨 註記裡明寫「不可寫成 X」的詞,生成稿若出現就報

用法: python scratchpad/cn82/cn_gate.py <out_zht.json|out_en.json|out_zhs.json>
"""
import io
import json
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
BASE = "scratchpad/cn82"

# 🚨 2026-09-04:帳本的官方角色名是【簡體】(抄自大陸官方物料),繁中稿當然寫【繁體】——
#    不折疊簡繁就會整批誤報「官方角色名一個都沒出現 → 可能寫成別齣戲」。
#    實例:《savior》生成稿寫「范·米格倫」,帳本是「范·米格伦」,一個字之差就判成寫錯戲。
try:
    from opencc import OpenCC
    _t2s = OpenCC("t2s").convert
except Exception:                      # 沒裝 opencc 就退回原字串,但要出聲,不可靜默
    sys.stderr.write("::warning::opencc 不可用,簡繁不折疊,繁中稿會大量誤報\n")
    def _t2s(x):
        return x


# 🚨 英文稿會把中文角色名【羅馬拼音化】,拿中文名比對必然落空。
#    原本只能標「無法機械比對→人工看」,幾乎每組都亮燈,等於沒有鑑別力。
#    裝了 pypinyin 之後可以真的比:陈启耀 → chenqiyao,再去英文稿裡找(去掉空白與大小寫)。
#    ⚠ 只當【線索】:同音字、姓名分寫、官方自訂拼法(Hihara Ryūsen 是日文羅馬字不是漢語拼音)
#      都可能對不上,對不上不代表錯,仍要人工看。
try:
    from pypinyin import lazy_pinyin
    def to_pinyin(x):
        return "".join(lazy_pinyin(x or "")).lower()
except Exception:
    def to_pinyin(x):
        return ""


def fold(x):
    """比對前一律折成簡體 + 去掉間隔號/空白,避免『范·米格伦』vs『范米格倫』對不上。"""
    return _t2s(x or "").replace("·", "").replace("・", "").replace(" ", "")

# 帳本 characters 欄的【】不只標角色名,也用來強調說明詞。沿用 leak_check 的過濾。
# 帳本 characters 欄的【】既標角色名,也用來強調說明詞(「【狗头人身】」「【英文月份】」
# 「【身份欺瞞/懸念】」)。名字裡不會出現這些字,拿來當否定條件。
SKIP = re.compile(r"[《》「」:：;;、/]|民歌|題材|题材|版本|卡司|官方|角色|演員|演员|飾|饰"
                  r"|沒有|没有|不可|絕不|绝不|的|身|稱|称|懸念|悬念|組織|组织|名字|月份"
                  r"|人物|主角|配角|泛稱|泛称|設定|设定")


def official_names(e):
    """只留【看起來像名字】的:去掉說明詞、去掉純描述,長度 1~12。
    ⚠ 名字可能是『中文 ENGLISH』的並列寫法(維塔 VITA),那種要保留整串。"""
    out = set()
    # 🚨 帳本常把拉丁拼法寫在【】【外面】的括號裡:「【斯特里夫】(原著 Dirk Stroeve)」
    #    「【布兰琪】(Blanche)」「【路西法】(Lucifer,惡魔;卡司 王瑞、唐子晗)」。
    #    只抓【】內容的話,英文稿就完全比對不到這些名字 —— 實例:《月亮与六便士》英文稿
    #    把 William/Stroeve/Blanche/Amy 當成劇情人物寫進去,守門卻只回報「無法機械比對」。
    #    所以把緊接在【】後面那組括號裡的【大寫開頭拉丁詞】也收進來,配成「中文 Latin」。
    txt_c = e.get("characters") or ""
    for m in re.finditer(r"【([^】]{1,40})】\s*[(（]([^)）]{1,80})[)）]", txt_c):
        cn = m.group(1).strip()
        for la in re.findall(r"\b[A-Z][A-Za-zÀ-ÿ]{2,}(?:\s+[A-Z][A-Za-zÀ-ÿ]{2,})?", m.group(2)):
            if la.lower() not in ("the", "and", "musical"):
                out.add("%s %s" % (cn, la))
    for blk in re.findall(r"【([^】]{1,300})】", txt_c):
        # 有些組把整份名單塞在同一個【】裡(《风声》的「李宁玉 Li Ningyu、顾小梦 Gu Xiaomeng、…」),
        # 先用頓號拆開,否則整串太長會被長度限制濾掉,等於整組沒有角色表。
        for n in re.split(r"[、]", blk):
            n = n.strip()
            if not n or len(n) > 24 or SKIP.search(n):
                continue
            out.add(n)
    return out


def forbidden(e):
    """帳本裡『不可寫成 X』『不要寫成 X』後面括號內的詞。"""
    out = []
    txt = (e.get("characters") or "") + (e.get("note") or "")
    # 只認【緊接在「不可/不要寫成」後面】的括號,中間不准夾字 —— 夾了就會抓到卡司名
    # (「【路西法】(Lucifer,惡魔;卡司 王瑞、唐子晗)」曾被誤抓成禁忌詞)。
    # 允許「譯成中文(...)」這種中間夾 0~4 字的寫法,但仍要求括號緊跟其後
    for m in re.finditer(r"(?:不可|不要|絕不可|绝不可)(?:寫成|写成|譯成|译成)[^(（]{0,4}[(（]([^)）]{1,40})[)）]", txt):
        out += [w.strip() for w in re.split(r"[、/,,]", m.group(1)) if 2 <= len(w.strip()) <= 8]
    # 另一種寫法:「不可譯成中文(七月/六月/二月)」已被上式涵蓋;
    # 「不要寫成強尼/雪莉」這種沒括號的,取到句末標點為止。
    for m in re.finditer(r"(?:不可|不要)(?:寫成|写成|譯成|译成)([^,。;;()（）]{2,30})", txt):
        out += [w.strip() for w in re.split(r"[、/]", m.group(1))
                if 2 <= len(w.strip()) <= 8 and w.strip() not in ("中文", "英文", "拼音")]
    return sorted(set(out))


def main():
    path = sys.argv[1]
    # 🚨 語言決定比對方式。英文稿會把中文角色名【羅馬拼音化】(范·米格伦 → Van Meegeren),
    #    拿中文名去比對必然全部落空,會誤報「寫成別齣戲」。所以:
    #      中文稿 → 中文名與拉丁名都可比
    #      英文稿 → 只比【官方本來就有拉丁寫法】的名字;純中文名標成「無法機械比對」交人工
    is_en = "_en" in path
    rows = json.load(io.open(path, encoding="utf-8"))
    # regen 檔的順序是 regen_*_order.json(69 組),不是 order.json(78 組)
    import os
    suf = "en" if is_en else "zht"
    ro = "%s/regen_%s_order.json" % (BASE, suf)
    order = json.load(io.open(ro if ("regen" in path and os.path.exists(ro))
                              else "%s/order.json" % BASE, encoding="utf-8"))
    led = json.load(io.open("%s/ledger.json" % BASE, encoding="utf-8"))
    bad = 0
    print("稿 %d 筆 / 清單 %d 齣\n" % (len(rows), len(order)))
    for i, g in enumerate(order):
        if i >= len(rows):
            break
        txt = (rows[i].get("synopsis") or "").strip()
        e = led[g]
        note = []
        if not txt:
            print("❌ %-22s 空稿" % g[:22])
            bad += 1
            continue
        names = official_names(e)
        # 🚨 2026-09-04:原本拿【整份卡司表】比對,誤報一堆。官方劇情本身多半【不點名角色】
        #    (《0528》《六个说谎的大学生》官方梗概一個名字都沒有),簡介照著寫當然也沒有名字,
        #    卻被報成「可能寫成別齣戲」。更糟的是《亡灵之旅》——帳本明令【不可寫出阿努比斯】
        #    (那是官方刻意保留的身份懸念),稿子正確地沒寫,守門卻把它當缺漏。
        #    正確基準是【官方劇情裡真的出現過的名字】:那些才是「應該出現」;
        #    只在卡司表上的名字算 optional,不出現不是錯。
        plot_txt = fold((e.get("official_plot") or "")
                        + ((e.get("external_plot") or {}).get("text") or ""))
        if names:
            def _in_plot(n):
                cn = "".join(re.findall(r"[一-鿿A-Za-z0-9#]+",
                                        re.sub(r"[A-Za-z][A-Za-z .'Ā-ɏ-]*", " ", n))).strip()
                m2 = re.search(r"[A-Za-z][A-Za-z .'Ā-ɏ-]*", n)
                la = m2.group(0).strip() if m2 else ""
                return (cn and fold(cn) in plot_txt) or (la and la.lower() in plot_txt.lower())
            optional = {n for n in names if not _in_plot(n)}
            names = names - optional
            # 🚨 2026-09-04 補上【反向】檢查。上面那段把「只在卡司表、官方劇情沒提到」的名字
            #    當成 optional 放行 —— 但真正危險的方向是【它們跑進稿子裡】:
            #    《月亮与六便士》英文稿寫成「His path brings him into contact with
            #    William, Stroeve, Blanche, Amy, and Ata」,把官方【一人分飾多角的演員分飾表】
            #    當成他一路遇到的人;《命运之上》繁中稿也把四個卡司名寫成額外登場者。
            #    官方劇情沒提到的人,寫進簡介就等於宣稱「這個人在劇裡做了這些事」。
            #    ⚠ 只報不判錯:有時是【可靠的消去法】(官方說天使與惡魔,角色卡標明
            #      路西法=惡魔、拉斐爾=天使),那種是對的,交給人工看。
            extra = []
            for n in sorted(optional):
                cn2 = "".join(re.findall(r"[一-鿿A-Za-z0-9#]+",
                                         re.sub(r"[A-Za-z][A-Za-z .'Ā-ɏ-]*", " ", n))).strip()
                m3 = re.search(r"[A-Za-z][A-Za-z .'Ā-ɏ-]*", n)
                la2 = m3.group(0).strip() if m3 else ""
                hit_cn = (not is_en) and cn2 and len(cn2) >= 2 and fold(cn2) in fold(txt)
                hit_la = la2 and len(la2) >= 3 and la2.lower() in txt.lower()
                if hit_cn or hit_la:
                    extra.append(n)
            if extra:
                note.append("⚠卡司表上的名字寫進稿子了,但【官方劇情沒提到這個人】:%s → 人工確認是可靠消去法還是把分飾表當劇情人物"
                            % extra[:6])
        if names:
            # 🚨 拉丁名一律【轉小寫比對】:官方常寫全大寫(维塔 VITA / 荷鲁斯 HORUS),
            #    英文稿會寫成 Vita / Horus,大小寫敏感的比對會整批誤報「一個都沒出現」。
            # 🚨 帳本常寫成「中文 English」並列(「维塔 VITA」「李宁玉 Li Ningyu」),
            #    簡介裡只會出現其中一半 —— 整串比對必然落空,要拆開比。
            def parts(n):
                cn = "".join(re.findall(r"[一-鿿A-Za-z0-9#]+", re.sub(r"[A-Za-z][A-Za-z .'Ā-ɏ-]*", " ", n))).strip()
                m2 = re.search(r"[A-Za-z][A-Za-z .'Ā-ɏ-]*", n)
                return cn, (m2.group(0).strip() if m2 else "")
            hit, unchk = set(), set()
            ftxt = fold(txt)
            for n in names:
                cn, la = parts(n)
                if is_en and not la:
                    py = to_pinyin(cn)
                    flat = re.sub(r"[^a-z]", "", txt.lower())
                    if py and len(py) >= 4 and py in flat:
                        hit.add(n)        # 拼音對得上就算命中
                    else:
                        unchk.add(n)      # 對不上只能標「要人工看」,不能斷定是錯
                    continue
                if (la and la.lower() in txt.lower()) or ((not is_en) and cn and fold(cn) in ftxt):
                    hit.add(n)
            names = names - unchk
            # B:名字有拉丁寫法、且【中文部分在稿裡、拉丁部分不在】→ 官方英文名被中譯/被拿掉
            # B 只對【中文稿】有意義:官方給了英文名,中文稿卻整篇找不到 → 被中譯了
            # 🚨 只有【官方純英文名】(Eggy / July / Doris)才適用:那種名字中文稿也必須保留英文。
            #    官方寫成「中文 English」並列的(维塔 VITA、李宁玉 Li Ningyu),中文稿只寫中文是【正確的】
            #    —— 那個英文是官方給的對照拼寫,不是中文正文該出現的東西。原本沒分,誤報《亡灵之旅》。
            latmiss = []
            if not is_en:
                for n in names:
                    cn, la = parts(n)
                    if la and not cn and la.lower() not in txt.lower():
                        latmiss.append(n)
            # 🚨 反過來的錯:官方【中英並列】給了名字(「Queen of Spades 黑桃女王」、
            #    「Edward 爱德华」),中文稿卻挑英文那半來寫。官方劇情本文用的是中文,
            #    中文稿也該用中文。2026-09-04 連續兩組中招(《嗜血博士》寫 Jonathan/Edward、
            #    《爱丽丝奇境之旅》寫 Queen of Spades/Clark Hare),所以設成常設檢查。
            zhname_en = []
            if not is_en:
                for n in official_names(e):
                    cn, la = parts(n)
                    if cn and la and len(la) >= 3 and la.lower() in txt.lower():
                        zhname_en.append("%s→應寫「%s」" % (la, cn))
            if zhname_en:
                note.append("🚨中文稿用了英文寫法,但官方有中文名:%s" % zhname_en[:5])
            if unchk:
                note.append("⚠英文稿:%d 個官方角色名只有中文寫法(%s),機械比對不了→必須人工看"
                            % (len(unchk), sorted(unchk)[:5]))
            if names and not hit:
                note.append("🚨官方角色名【一個都沒出現】(%d 個:%s)→ 可能寫成別齣戲"
                            % (len(names), sorted(names)[:5]))
            elif len(hit) < len(names):
                note.append("缺 %d/%d 個官方角色名:%s" % (len(names) - len(hit), len(names),
                                                sorted(names - hit)[:6]))
            if latmiss:
                note.append("🚨官方英文名疑被中譯(整篇找不到):%s" % latmiss[:5])
        else:
            note.append("⚠ 帳本沒有官方角色表 → 這組只能靠人工外部查證")
        # 🚨 2026-09-04:我在帳本裡用【】標記角色名,《心安东坡》的繁中稿把
        #    「與【小靈】共同尋找」整個括號照抄進正文了 —— 官方文案沒有這種括號,
        #    讀者會看到莫名其妙的方括號。順便擋掉其他後設語言外洩(🚨/⚠/「根據官方」)。
        # 🚨 2026-09-04 二度中招,而且更嚴重:《狐说臣与仙》把我帳本的【編輯指示本身】
        #    整句寫進正文——「但這屬於典故背景上的推斷,並非劇中明說」。
        #    帳本裡對我自己講的話(「可點出但要標明是推斷」「不可自行設定」)會被當成
        #    要寫進簡介的內容,所以關鍵詞要一併擋。
        meta = sorted(set(re.findall(
            r"[【】]|🚨|⚠|根據官方|根据官方|以下是|Markdown"
            r"|並非劇中|并非剧中|官方沒有明說|官方没有明说|屬於[^,。]{0,8}推斷|属于[^,。]{0,8}推断"
            r"|可令人聯想|據此推測|据此推测|不可自行|需注意|請注意", txt)))
        if meta:
            note.append("🚨正文出現【標記/後設語言】外洩:%s" % meta)

        fb = [w for w in forbidden(e) if fold(w) in fold(txt)]
        if fb:
            note.append("🚨帳本明令不可寫的詞出現了:%s" % fb)
        if not (e.get("official_plot") or "").strip():
            note.append("⚠ 官方無劇情,無事實關卡,查證要最嚴")
        if note:
            bad += 1
            print("❌ %-22s %s" % (g[:22], " | ".join(note)))
        else:
            print("○  %-22s 機械檢查無異常(仍須人工通讀)" % g[:22])
    print("\n需要人工處理:%d / %d" % (bad, min(len(rows), len(order))))
    return 0


raise SystemExit(main())
