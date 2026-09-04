# -*- coding: utf-8 -*-
"""三語覆蓋率稽核:每一組作品的【標題】與【劇情簡介】在 en / zh-hant / zh-hans 的覆蓋狀況。

覆蓋是什麼意思(定義寫死在這裡,避免每次口徑不同)
------------------------------------------------
「覆蓋」= 該語言的使用者看到的是【自己看得懂的文字】,不是「欄位有值」。
每一筆在三個 variant 裡都一定有 title,所以數欄位有值等於恆真、零資訊
(同 feedback_vacuous_negative_test)。

標題:
  build/gen_variants.mjs 的 cjk() **只做繁簡轉換,不翻譯**。所以:
    • en 覆蓋   = en variant 顯示的題名不含 CJK/假名/諺文
                  (來源:題名本來就是拉丁字母,或 OPENTIX 等來源給了 title_en)
    • 繁/簡覆蓋 = 有 cn_annot(來自 i18n_maps.show_titles_tw / show_titles 的官方譯名)
                  或 顯示的題名本身就是中文

  ⚠「題名是中文」不能只看有沒有漢字 —— 只有漢字、沒有假名的【日文】劇名
    (民王、青春-AOHARU-鉄道)也會通過漢字檢查,把日文題名當成中文覆蓋。
    判準改用【有沒有在中文市場上演】:在中國/台灣/香港/澳門/新加坡有場次的,
    漢字題名才算中文在地題名。2026-09-02 雙向驗證過這條規則:
      • 反向:中國/台灣原創卻沒有中文市場場次的組 = 0(不會誤殺)
      • 正向:恰好抓出 4 組只在日本上演的日文漢字題名
        (diamond impulse / 民王 / spyfamily 2 / aoharu)
    ⚠ 反例參照:刀剣乱舞、薄桜鬼 真改雖只在日本演,但有官方中文譯名(刀劍亂舞 /
      薄櫻鬼 真改)寫在譯名表裡,走 cn_annot 那條,仍算覆蓋 —— 兩條路要分開判。

劇情:
  data/synopses/<lang>.json 的 syn[group][sub] 有非空字串才算(sub: en→en / 繁→zh / 簡→zh-hans)。
  這是【前端實際吃的檔】,不是後台知識庫(library 527 組 > served,差額是目前不在檔期的作品)。

分母:
  data/variants/shows.en.json 裡出現過的 group(= 目前在檔期的作品組),不是場次數。
  一組多場只算一次 —— 使用者看到的是「一齣戲」。

用法:
  python scripts/qa/coverage_report.py            # 摘要
  python scripts/qa/coverage_report.py --csv out.csv   # 逐組明細
  python scripts/qa/coverage_report.py --json out.json
"""
import io
import json
import re
import sys
from collections import Counter, OrderedDict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

VAR = "data/variants/shows.%s.json"
SYN = "data/synopses/%s.json"
LANGS = [("en", "en"), ("zh-hant", "zh"), ("zh-hans", "zh-hans")]

HAN = re.compile(r"[一-鿿㐀-䶿]")
KANA = re.compile(r"[぀-ヿ]")           # 平假名/片假名 → 日文
HANGUL = re.compile(r"[가-힯ᄀ-ᇿ]")  # 諺文 → 韓文
CYRIL = re.compile(r"[Ѐ-ӿ]")
# 中文市場:漢字題名要在這些地方有場次,才算「中文在地題名」而非日文漢字題名。
ZH_MARKET = {"中國", "臺灣", "台灣", "香港", "澳門", "新加坡",
             "China", "Taiwan", "Hong Kong", "Macau", "Singapore"}


def zh_local_title(t, countries):
    """這個題名算不算「中文使用者看得懂的在地題名」。

    🚨 不能直接用 script_of(t) == "han":script_of 只要看到【一個】假名就整串判成日文,
    於是把中文圈常見的【の 當「的」用】的寫法一起誤殺。2026-09-05 使用者要求核對產生器
    時抓到:台灣製作《無聲の海腳間仔》(漢字 6、假名 1,在臺灣演出)被判成「中文未覆蓋」,
    害繁中/簡中標題覆蓋率各少算 1 組(389→390 / 388→389)。

    判準:漢字【多於】假名,且在中文市場有場次。
      • 全庫 18 組題名含假名,其中 17 組是日本的(不在中文市場)→ 市場檢查本來就擋掉了;
        只有《無聲の海腳間仔》這一組是中文市場的,正是被假名短路誤殺的那筆。
      • 保留「漢字 > 假名」這道比例護欄,是為了擋日後【日文題名巡演到中文市場】的情況
        (テニスの王子様 漢3假名4 → 仍不算中文在地題名,走官方譯名表那條路)。
    """
    han = len(HAN.findall(t or ""))
    kana = len(KANA.findall(t or ""))
    return bool(han and han > kana and (countries & ZH_MARKET))


def script_of(t):
    """題名的書寫系統。回傳 latin / han / kana / hangul / cyrillic。

    ⚠ 這支只用來描述「這串字長什麼樣」(統計/顯示用),【不要】拿它直接判中文覆蓋
      —— 判覆蓋請用 zh_local_title(),原因見該函式。
    """
    t = t or ""
    if KANA.search(t):
        return "kana"
    if HANGUL.search(t):
        return "hangul"
    if HAN.search(t):
        return "han"
    if CYRIL.search(t):
        return "cyrillic"
    return "latin"


def load():
    var = {}
    for lang, _ in LANGS:
        rows = json.load(io.open(VAR % lang, encoding="utf-8"))["shows"]
        var[lang] = rows
    syn = {}
    for lang, sub in LANGS:
        d = json.load(io.open(SYN % lang, encoding="utf-8"))
        d = d.get("syn", d)
        syn[lang] = {g: v for g, v in d.items() if (v or {}).get(sub)}
    return var, syn


def main():
    var, syn = load()

    # 逐組收題名。同一組可能有多場;先確認同組同語言的題名一致,不一致要講出來。
    per = OrderedDict()
    inconsistent = []
    for lang, _ in LANGS:
        for r in var[lang]:
            g = r.get("group") or ""
            if not g:
                continue
            e = per.setdefault(g, {"group": g, "tag": r.get("tag"), "n_shows": 0,
                                   "title": {}, "annot": {}, "countries": set()})
            e["countries"].add(r.get("country") or "")
            t = r.get("title") or ""
            a = r.get("cn_annot") or ""
            if lang in e["title"] and e["title"][lang] != t:
                inconsistent.append((g, lang, e["title"][lang], t))
            e["title"][lang] = t
            e["annot"][lang] = a
    for r in var["en"]:
        g = r.get("group") or ""
        if g in per:
            per[g]["n_shows"] += 1

    # 判定覆蓋
    for g, e in per.items():
        e["script"] = script_of(e["title"]["en"])
        # 標題
        en_t = e["title"]["en"]
        e["title_cov"] = {}
        e["title_src"] = {}
        e["title_cov"]["en"] = script_of(en_t) in ("latin", "cyrillic")
        e["title_src"]["en"] = "原生拉丁" if e["title_cov"]["en"] else "—"
        for lang in ("zh-hant", "zh-hans"):
            if e["annot"][lang]:
                e["title_cov"][lang] = True
                e["title_src"][lang] = "官方譯名表"
            elif zh_local_title(e["title"][lang], e["countries"]):
                e["title_cov"][lang] = True
                e["title_src"][lang] = "原生中文"
            else:
                e["title_cov"][lang] = False
                # 漢字題名但不在中文市場 = 日文漢字,講明白別混進「沒有題名」
                e["title_src"][lang] = ("日文漢字題名"
                                        if script_of(e["title"][lang]) == "han" else "—")
        # 劇情
        e["syn_cov"] = {lang: (g in syn[lang]) for lang, _ in LANGS}

    total = len(per)
    print("=" * 78)
    print("MusicalMap 三語覆蓋率稽核 —— 分母 = 目前在檔期的 %d 組作品(非場次)" % total)
    print("=" * 78)
    if inconsistent:
        print("⚠ 同組同語言題名不一致 %d 筆(下列前 5 筆),覆蓋率取最後一筆:" % len(inconsistent))
        for x in inconsistent[:5]:
            print("   ", x)
        print()

    print("【標題】該語言使用者看到的是自己看得懂的文字嗎")
    for lang, _ in LANGS:
        n = sum(1 for e in per.values() if e["title_cov"][lang])
        srcs = Counter(e["title_src"][lang] for e in per.values() if e["title_cov"][lang])
        detail = "、".join("%s %d" % (k, v) for k, v in srcs.most_common())
        print("  %-8s %4d / %d = %5.1f%%   (%s)" % (lang, n, total, 100.0 * n / total, detail))

    print()
    print("【劇情簡介】data/synopses/<lang>.json 有非空內容")
    for lang, _ in LANGS:
        n = sum(1 for e in per.values() if e["syn_cov"][lang])
        print("  %-8s %4d / %d = %5.1f%%" % (lang, n, total, 100.0 * n / total))

    print()
    print("【交叉】標題與劇情都覆蓋(三語各自)")
    for lang, _ in LANGS:
        n = sum(1 for e in per.values() if e["title_cov"][lang] and e["syn_cov"][lang])
        print("  %-8s %4d / %d = %5.1f%%" % (lang, n, total, 100.0 * n / total))

    print()
    print("【三語全滿】標題與劇情在 en+繁+簡 全部覆蓋:%d / %d = %.1f%%"
          % (sum(1 for e in per.values()
                 if all(e["title_cov"][l] and e["syn_cov"][l] for l, _ in LANGS)),
             total, 100.0 * sum(1 for e in per.values()
                                if all(e["title_cov"][l] and e["syn_cov"][l] for l, _ in LANGS)) / total))

    print()
    print("【已排除的高估】漢字題名但不在中文市場上演 = 日文漢字,不計入中文覆蓋:")
    sus = [e for e in per.values() if e["title_src"]["zh-hant"] == "日文漢字題名"]
    if sus:
        for e in sus:
            print("   %-24s %-10s %-30s %s"
                  % (e["group"][:24], e["tag"], e["title"]["zh-hant"][:30],
                     sorted(e["countries"])))
    else:
        print("   (無)")

    print()
    print("【題名書寫系統分布】(en variant 顯示值)")
    for k, v in Counter(e["script"] for e in per.values()).most_common():
        print("   %-10s %d" % (k, v))

    if "--csv" in sys.argv:
        p = sys.argv[sys.argv.index("--csv") + 1]
        import csv
        with io.open(p, "w", encoding="utf-8-sig", newline="") as f:
            w = csv.writer(f)
            w.writerow(["group", "tag", "shows", "title_en", "title_zh_hant", "cn_annot_hant",
                        "title_zh_hans", "cn_annot_hans",
                        "title_en_ok", "title_hant_ok", "title_hans_ok",
                        "title_hant_src", "title_hans_src",
                        "syn_en", "syn_hant", "syn_hans"])
            for e in sorted(per.values(), key=lambda x: x["group"]):
                w.writerow([e["group"], e["tag"], e["n_shows"],
                            e["title"]["en"], e["title"]["zh-hant"], e["annot"]["zh-hant"],
                            e["title"]["zh-hans"], e["annot"]["zh-hans"],
                            int(e["title_cov"]["en"]), int(e["title_cov"]["zh-hant"]),
                            int(e["title_cov"]["zh-hans"]),
                            e["title_src"]["zh-hant"], e["title_src"]["zh-hans"],
                            int(e["syn_cov"]["en"]), int(e["syn_cov"]["zh-hant"]),
                            int(e["syn_cov"]["zh-hans"])])
        print("\n逐組明細 → %s" % p)

    if "--json" in sys.argv:
        p = sys.argv[sys.argv.index("--json") + 1]
        json.dump(list(per.values()), io.open(p, "w", encoding="utf-8"),
                  ensure_ascii=False, indent=1, default=list)
        print("逐組明細 → %s" % p)
    return 0


raise SystemExit(main())
