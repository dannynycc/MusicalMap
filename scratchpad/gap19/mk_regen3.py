# -*- coding: utf-8 -*-
"""第三輪:修第一輪重生成【自己帶進來的】問題。

為什麼會有第三輪:第二輪把官方角色表餵進提示以擋住捏造,結果產生副作用 ——
模型開始【列名單】,把「Carole/Konferansjerka/Brenda」這種連斜線的角色欄位
原樣抄進正文,讀起來像節目冊。另外 天堂邊緣 的英文稿直接夾了中文字。

這一輪的提示因此要同時給【事實】與【行文限制】。

用法: python scratchpad/gap19/mk_regen3.py
"""
import io
import json
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
BASE = "scratchpad/gap19"

NO_ROSTER = ("Write flowing prose, NOT a cast list. Name only the few characters the story "
             "actually needs, and never copy a cast-sheet entry with slashes in it "
             "(never write things like 'Carole/Konferansjerka/Brenda' or "
             "'Dennis Stone/dr van Hoff/dr Berkeley/Bob'). Do not enumerate the company.")

JOBS = {
    "na prochach": [
        "The family on stage is called BARKER (Robert, Rosa, Adam, Archibald, Rupert Barker). "
        "NEVER write Sackler, Purdue or OxyContin.",
        "Królowa Opioidów (the Opioid Queen) is a central figure, danced largely without words; "
        "keep her in the story.",
        "A Konferansjerka (compère) frames the show. Do not call it a television show.",
        "Do NOT give any character a profession — the official cast list gives none.",
        "Keep these official facts: the painkiller proved to be opium in pills; patients moved on "
        "to street heroin; more than 500,000 Americans have died; the makers' settlement cost "
        "less than their profit and bought them impunity.",
        NO_ROSTER,
    ],
    "wypior": [
        "Marta and Łukasz are a couple in the middle of a relationship crisis; the closing "
        "question is whether the great figure of Polish Romanticism still has the power TO SAVE "
        "their relationship.",
        "Adam Mickiewicz lives as a vampire in a flat in the fashionable pl. Zbawiciela area of "
        "present-day Warsaw; by day he hides in the wardrobe from the deadly sun, by night he "
        "steals blood from a hospital bin.",
        "Do NOT name a specific hospital or park and do NOT say whose flat it is.",
        "Based on Grzegorz Uzdański's novel, largely written in thirteen-syllable verse; played "
        "in the Bistro Syrena space; a mixture of theatre, musical and literary cabaret.",
        NO_ROSTER,
    ],
    "天堂邊緣": [
        "🚨 Romanise every Chinese name — the English text must contain NO Chinese characters. "
        "Use Xiuyan (秀燕), Hezhi (何智), Feifei (菲菲) and Zhenyu (震宇); render 天使 simply as "
        "'an Angel'.",
        "The three souls have watched over Zhenyu for TWENTY-NINE years, since his birth.",
        "An Angel appears and tells them that each must complete their own last regret within "
        "twenty-four hours before they can travel on to heaven; a search across family love, "
        "friendship and romantic love follows.",
        "Do NOT decide which regret belongs to which soul — the official text does not say.",
        "Official theme: true fulfilment is not a life without regret, but learning to let go and "
        "to cherish the people still around you.",
    ],
    "caperucita roja": [
        "In Chinese this show must be called 小紅帽 / 小红帽 — the standard Chinese name for "
        "Little Red Riding Hood. Do NOT transliterate 'Caperucita' phonetically "
        "(never 卡佩露西塔). The wolf is 大野狼 / 大灰狼 and the grandmother 外婆.",
        "Official plot: she is curious and brave and takes a basket of food through the forest to "
        "her grandmother; the cunning wolf plots to reach the grandmother's house first and eat "
        "them both; WITH HER FRIENDS AND AN UNEXPECTED HERO she learns to listen to her elders "
        "and to be careful. Never write that a huntsman rescues her.",
        "Do not characterise the grandmother as madder than the wolf.",
    ],
    "precure colorful runway": [
        "🚨 The Japanese names are written in kanji and must be reproduced exactly — do not "
        "re-invent them. They are 神白彩人 (Kamishiro Ayato), 蜂針衣月 (Hachibari Itsuki), "
        "御厨王子 (Mikuriya Oji) and 百瀬昭彦 (Momose Akihiko). Never write 神代彩人, 蜂張樹 "
        "or 百瀬明彦.",
        "Write a straightforward, positive description from the published facts below. "
        "This is a brand-new original stage story for the male Precure, opening December 2026.",
        "The theme is FASHION. The show portrays the heroes' life-size everyday lives together "
        "with their duty as Precure, told through staging, song and action that only the theatre "
        "can give, shining like a colourful runway.",
        "The four heroes are Kamishiro Ayato / Cure Silhouette, Hachibari Itsuki / Cure Collage, "
        "Mikuriya Oji / Cure Flash, and Envy / Cure Trad. Momose Akihiko also appears. "
        "The announced adversaries are Bogart, Banshee and Gothic.",
        "The producers have not published any further plot, so describe the premise, the world "
        "and the announced figures rather than inventing events, motives or battles.",
    ],
}


# 🚨 各語言要重做的【不一樣】,全語言重跑會把已經正確的稿蓋掉:
#    英文  na prochach / wypior 列名單、天堂邊緣 夾中文字、precure 產出空白
#    中文  na prochach / wypior / 天堂邊緣 的繁中都【已經正確】,不可重跑;
#          只有 caperucita(被音譯成卡佩露西塔)與 precure(日文漢字名被改寫)要修
PER_LANG = {
    "en": ["na prochach", "wypior", "天堂邊緣", "precure colorful runway"],
    "zht": ["caperucita roja", "precure colorful runway"],
    "zhs": ["caperucita roja", "precure colorful runway"],
}


def main():
    order = json.load(io.open("%s/order.json" % BASE, encoding="utf-8"))
    ident = json.load(io.open("%s/list.json" % BASE, encoding="utf-8"))
    idx = {g: i for i, g in enumerate(order)}
    for short, want in PER_LANG.items():
        prompts, groups = [], []
        for g in want:
            block = " ".join("(%d) %s" % (i + 1, r) for i, r in enumerate(JOBS[g]))
            prompts.append("%s. VERIFIED FACTS about this production — the synopsis must not "
                           "contradict any of them: %s" % (ident[idx[g]], block))
            groups.append(g)
        json.dump(prompts, io.open("%s/regen3_list_%s.json" % (BASE, short), "w",
                                   encoding="utf-8"), ensure_ascii=False, indent=1)
        json.dump(groups, io.open("%s/regen3_order_%s.json" % (BASE, short), "w",
                                  encoding="utf-8"), ensure_ascii=False, indent=1)
        print("%-4s %d 齣: %s" % (short, len(groups), ", ".join(groups)))
    return 0


raise SystemExit(main())
