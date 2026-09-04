# -*- coding: utf-8 -*-
"""從帳本抽出【身份識別】欄位,組成生成用的 prompt 前綴。

🚨 SOP §1 鐵則:prompt【只釘身份,絕不餵劇情】。
   餵了劇情,Perplexity 只會把我的字吐回來,我再拿它「查證」= 球員兼裁判,查證整個失效。
   所以這支【只碰】title / 出品製作 / 主創 / 場館 / 城市 / 年份,
   絕不從 official_plot、characters 取任何東西。

抽取來源:note / tag_error / tag_check_needed(我自己寫的,格式相對一致)。
輸出草稿到 identity.json,【必須由本人逐條校對】後才拿去生成 —— 正則抽的名字會錯。

用法: python scratchpad/cn82/mk_identity.py
"""
import io
import json
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
BASE = "scratchpad/cn82"

# 🚨 只取這些欄位。official_plot / characters / official_extra 一律不碰(會洩劇情)。
SRC_FIELDS = ["note", "tag_error", "tag_check_needed"]
ROLES = ["出品", "聯合出品", "联合出品", "製作", "制作", "出品人", "製作人", "制作人",
         "導演", "导演", "總導演", "总导演", "編劇", "编剧", "作曲", "作詞", "作词",
         "音樂總監", "音乐总监", "演出單位", "演出团体", "演出劇團", "剧团", "劇團"]


def fields(e):
    return " ".join(e.get(k) for k in SRC_FIELDS if isinstance(e.get(k), str))


def pick(txt, role):
    """抓『<role>【名字】』或『<role> 名字、名字』;只取到標點為止。"""
    out = []
    for m in re.finditer(re.escape(role) + r"\s*[:：]?\s*【([^】]{1,40})】", txt):
        out.append(m.group(1))
    if not out:
        m = re.search(re.escape(role) + r"\s*[:：]\s*([^,。;;、()()\n]{2,30})", txt)
        if m:
            out.append(m.group(1).strip())
    return out


def main():
    led = json.load(io.open(BASE + "/ledger.json", encoding="utf-8"))
    shows = json.load(io.open("data/shows.json", encoding="utf-8"))
    shows = shows.get("shows") or shows
    venue = {}
    for s in shows:
        venue.setdefault(s["group"], []).append((s.get("city_cn") or s.get("city"), s.get("venue")))

    out = {}
    for g, e in led.items():
        if g.startswith("_"):
            continue
        if (e.get("catalog_status") or "").startswith("⛔"):
            continue
        txt = fields(e)
        roles = {}
        for r in ROLES:
            v = pick(txt, r)
            if v:
                roles[r] = v
        places = sorted({("%s %s" % p).strip() for p in venue.get(g, []) if p[1]})
        out[g] = {
            "title": e.get("title"),
            "title_en": e.get("title_en"),
            "venues": places[:3],
            "roles_auto": roles,
            "identity": "",          # ← 由本人填寫/校對後才可使用
            "_note_excerpt": txt[:300],
        }
    json.dump(out, io.open(BASE + "/identity.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    have = len([1 for v in out.values() if v["roles_auto"]])
    print("寫出 identity.json:%d 組,其中 %d 組抽到主創欄位" % (len(out), have))
    print("🚨 identity 欄目前全空 —— 必須本人逐條校對後填寫,不可直接拿 roles_auto 去生成")
    return 0


raise SystemExit(main())
