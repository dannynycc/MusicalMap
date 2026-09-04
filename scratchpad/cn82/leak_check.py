# -*- coding: utf-8 -*-
"""生成前守門:確認 identity.json 的 prompt【沒有洩漏劇情或角色名】。

🚨 SOP §1:prompt 只釘身份,絕不餵劇情。餵了之後 Perplexity 只是把我的字吐回來,
   我再拿它去「查證」就是球員兼裁判,§3 整個失效(Pinocchio 犯過)。

檢查三件:
 1. identity 是否含官方【角色表】裡的名字 —— 但【劇名本身含有的名字不算】
    (《阿Q与吴妈》《宝玉》《亡灵之旅:冥犬与少年》的角色名就是劇名,無法也不需迴避)。
 2. identity 是否與 official_plot 有過長的共同子字串(逐字抄劇情)。
 3. identity 是否為空(還沒人工填寫就不准拿去生成)。

用法: python scratchpad/cn82/leak_check.py
"""
import io
import json
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
BASE = "scratchpad/cn82"
MIN_COMMON = 12          # 與官方劇情連續相同 ≥12 字 = 抄劇情


def longest_common(a, b):
    """最長共同連續子字串長度(短字串用,O(n*m) 可接受)。"""
    if not a or not b:
        return 0, ""
    best, bs = 0, ""
    prev = [0] * (len(b) + 1)
    for i in range(1, len(a) + 1):
        cur = [0] * (len(b) + 1)
        for j in range(1, len(b) + 1):
            if a[i - 1] == b[j - 1]:
                cur[j] = prev[j - 1] + 1
                if cur[j] > best:
                    best, bs = cur[j], a[i - cur[j]:i]
        prev = cur
    return best, bs


def strip_title(txt, title):
    """把劇名、書名號內容與『(原创)音乐剧』這類通用前綴從字串裡拿掉。"""
    out = txt or ""
    for t in re.findall(r"《([^》]+)》", title or ""):
        out = out.replace(t, " ")
    for t in re.findall(r"《([^》]+)》", out):
        out = out.replace(t, " ")
    for w in ("原创音乐剧", "中文原创音乐剧", "大型音乐剧", "音乐剧", "音樂劇", "《", "》"):
        out = out.replace(w, " ")
    return re.sub(r"\s+", " ", out).strip()


def main():
    ident = json.load(io.open(BASE + "/identity.json", encoding="utf-8"))
    led = json.load(io.open(BASE + "/ledger.json", encoding="utf-8"))
    bad = 0
    empty = [g for g, v in ident.items() if not (v.get("identity") or "").strip()]
    if empty:
        print("⚠ identity 還沒填的 %d 組(不可生成):" % len(empty))
        for g in empty:
            print("   ", g)
    for g, v in ident.items():
        idt = (v.get("identity") or "").strip()
        if not idt:
            continue
        e = led.get(g, {})
        title = (e.get("title") or "") + (v.get("title") or "") + g
        # 🚨 characters 欄裡的【】不只標角色名,也用來強調一般詞(「【北魏民歌《木兰词》】」
        #    「【卡司 徐沛】」)。只收【看起來像人名】的:不含書名號/引號、長度 2~8、非說明詞。
        names = {n for n in re.findall(r"【([^】]{2,8})】", e.get("characters") or "")
                 if not re.search(r"[《》「」:：]", n)
                 and not re.search(r"民歌|題材|题材|版本|卡司|官方|角色|演員|演员|飾|饰", n)}
        allow = set(v.get("leak_ok") or [])
        leak = [n for n in names if n in idt and n not in title and n not in allow]
        if leak:
            bad += 1
            print("🚨 %-24s identity 含官方角色名(且不在劇名裡):%s" % (g[:24], leak))
        # 🚨 比對前先把【劇名與通用前綴】剝掉。官方劇情常以「音乐剧《X》…」開頭,
        #    不剝的話每一組都會報「共同 12 字」= 狼來了,守門就沒人看了。
        a = strip_title(idt, title)
        b = strip_title(e.get("official_plot") or "", title)
        for w in allow:          # 已寫明理由的來源署名(原著作者/授權方)先剝掉
            a = a.replace(w, " ")
        n, sub = longest_common(a, b)
        if n >= MIN_COMMON:
            bad += 1
            print("🚨 %-24s identity 與官方劇情連續相同 %d 字:%r" % (g[:24], n, sub))
    okd = {g: v["leak_ok"] for g, v in ident.items() if v.get("leak_ok")}
    if okd:
        print("\n⚠ 已寫明理由的例外(不是忽略,是【判定為身份而非劇情】):")
        for g, w in okd.items():
            print("   %-20s %s\n      理由:%s" % (g[:20], w,
                  (ident[g].get("leak_ok_why") or "🚨 沒寫理由,不可放行!")[:110]))
    print("\n已填 %d / %d 組" % (len(ident) - len(empty), len(ident)))
    print("%s" % ("✅ 沒有劇情/角色名洩漏" if bad == 0 else "🚨 %d 組有洩漏,必須改掉再生成" % bad))
    return 1 if (bad or empty) else 0


raise SystemExit(main())
