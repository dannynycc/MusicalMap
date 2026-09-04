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
    for blk in re.findall(r"【([^】]{1,300})】", e.get("characters") or ""):
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
    rows = json.load(io.open(path, encoding="utf-8"))
    order = json.load(io.open("%s/order.json" % BASE, encoding="utf-8"))
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
        if names:
            # 🚨 帳本常寫成「中文 English」並列(「维塔 VITA」「李宁玉 Li Ningyu」),
            #    簡介裡只會出現其中一半 —— 整串比對必然落空,要拆開比。
            def parts(n):
                cn = "".join(re.findall(r"[一-鿿A-Za-z0-9#]+", re.sub(r"[A-Za-z][A-Za-z .'Ā-ɏ-]*", " ", n))).strip()
                m2 = re.search(r"[A-Za-z][A-Za-z .'Ā-ɏ-]*", n)
                return cn, (m2.group(0).strip() if m2 else "")
            hit = set()
            for n in names:
                cn, la = parts(n)
                if (cn and cn in txt) or (la and la in txt):
                    hit.add(n)
            # B:名字有拉丁寫法、且【中文部分在稿裡、拉丁部分不在】→ 官方英文名被中譯/被拿掉
            latmiss = []
            for n in names:
                cn, la = parts(n)
                if la and la not in txt and (not cn or cn not in txt):
                    latmiss.append(n)
            if not hit:
                note.append("🚨官方角色名【一個都沒出現】(%d 個:%s)→ 可能寫成別齣戲"
                            % (len(names), sorted(names)[:5]))
            elif len(hit) < len(names):
                note.append("缺 %d/%d 個官方角色名:%s" % (len(names) - len(hit), len(names),
                                                sorted(names - hit)[:6]))
            if latmiss:
                note.append("🚨官方英文名疑被中譯(整篇找不到):%s" % latmiss[:5])
        else:
            note.append("⚠ 帳本沒有官方角色表 → 這組只能靠人工外部查證")
        fb = [w for w in forbidden(e) if w in txt]
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
