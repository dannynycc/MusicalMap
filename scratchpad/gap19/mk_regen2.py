# -*- coding: utf-8 -*-
"""第二輪重生成:通讀【中文稿】時才抓到的錯誤。

⚠ 不要覆蓋 regen_list.json —— 第一輪的 px_gen 可能還在跑,而且那是它的輸入檔。
   這一輪另外寫 regen2_list.json。

這三齣為什麼要重做:
  starzynski           繁中開頭寫「1941年萬靈節前夕」,同段後面又寫 1939-10-26 → 自相矛盾,官方是 1939
  naruto               繁中整篇是漫畫劇情(水木/伊魯卡/封印之書/搶鈴鐺/達茲納/波之國/再不斬與白/中忍考試),
                       官方只說「演少年篇、鳴人與夥伴一同成長」,且本作是【無台詞動作秀】;
                       英文稿則在結尾出現「The official production identifies its story as…」的元敘述
  charlie brown        兩語都寫成「【學校】的耶誕劇」,官方通稿是 neighborhood(鄰里)的;
                       繁中還漏掉 Linus 的演說(全劇最著名的轉折),並寫出【派伯敏特・佩蒂】——
                       該角色 1966 年才登場,1965 年原作沒有她

用法: python scratchpad/gap19/mk_regen2.py
"""
import io
import json
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
BASE = "scratchpad/gap19"

JOBS = {
    "starzynski": [
        "🚨 The action takes place on the evening, night and morning of 26 and 27 OCTOBER 1939 "
        "— never 1941. These are Starzyński's last hours in Warsaw's city hall under German "
        "occupation.",
        "Official facts: battered Warsaw, boundless helplessness, remorse, sadness and moral "
        "dilemmas; outside there are ruins, autumn, the approaching Zaduszki (All Souls') and "
        "darkness; ghosts crawl out of memories and dream mixes with waking.",
        "Official cast: Stefan Starzyński, Stefania Witkowska/Syrena/Reklamiara, Adam Brodziński, "
        "Stanisław Lorentz, Władysław Studnicki, Matka, Ojciec/Józef Piłsudski, Józia, "
        "Sylwester Wojewódzki/Lech Niemojewski, Paulina/Ludwika Nitschowa, Żołnierz Gestapo.",
        "The production uses fragments of Adam Mickiewicz's 'Dziady', quotations from "
        "Starzyński's own speeches, and Ludwika Nitschowa's words from Polish Radio reportage. "
        "It is inspired by Grzegorz Piątek's biography 'Starzyński. Prezydent z pomnika'.",
    ],
    "naruto": [
        "🚨 This production is a NON-VERBAL ninja live show ('ノンバーバル忍者ライブショー'): no "
        "dialogue and no songs. It uses actors' action, acrobatics and aerial work fused with "
        "projection mapping and illusion, plus all the stage machinery of the kabuki theatre "
        "Minamiza.",
        "🚨 The only plot statement the producers make is that it depicts the story of the "
        "NARUTO boyhood arc (少年篇), in which Naruto Uzumaki grows up together with his "
        "companions in the Hidden Leaf Village. Do NOT retell specific manga arcs — no source "
        "says this show stages the Land of Waves, Zabuza and Haku, the Chūnin Exams, Mizuki, "
        "Iruka or the Scroll of Sealing.",
        "Official characters announced: Naruto Uzumaki, Sasuke Uchiha, Sakura Haruno, "
        "Kakashi Hatake. Do not introduce others by name.",
        "🚨 Never write a sentence about what 'the official production identifies' or about "
        "sources, adaptations or versions. Describe only what happens.",
        "It is acceptable for this synopsis to be shorter than usual, because very little plot "
        "detail has been published.",
    ],
    "charlie brown christmas": [
        "🚨 Charlie Brown is asked to direct the NEIGHBORHOOD Christmas play — not a school play. "
        "The official touring copy says the Peanuts gang 'produce their own Christmas play and "
        "ultimately learn the true meaning of the season'.",
        "🚨 Linus's speech is the turning point of the work and must appear: when Charlie Brown "
        "asks whether anyone knows what Christmas is all about, Linus steps into the spotlight "
        "and answers.",
        "Officially named characters: Charlie Brown, Snoopy, Lucy, Linus, and 'the whole Peanuts "
        "gang'. Lucy runs her own five-cent psychiatric booth — Charlie Brown pays her for "
        "advice; she does not set it up for him.",
        "🚨 Do NOT include Peppermint Patty: she first appeared in 1966, after the 1965 work this "
        "show adapts. Sally, Schroeder, Violet, Frieda and Patty are safer, but the official copy "
        "names only Charlie Brown, Snoopy, Lucy and Linus — keep other names to a minimum.",
        "Other canonical beats: Snoopy decorates his doghouse for the lights-and-display contest; "
        "Charlie Brown chooses a small bare tree instead of a shiny aluminium one; the others "
        "mock it, then restore it together. Music by Vince Guaraldi.",
    ],
}


def main():
    order = json.load(io.open("%s/order.json" % BASE, encoding="utf-8"))
    ident = json.load(io.open("%s/list.json" % BASE, encoding="utf-8"))
    idx = {g: i for i, g in enumerate(order)}
    prompts, groups = [], []
    for g, rules in JOBS.items():
        block = " ".join("(%d) %s" % (i + 1, r) for i, r in enumerate(rules))
        prompts.append("%s. VERIFIED FACTS about this production — the synopsis must not "
                       "contradict any of them: %s" % (ident[idx[g]], block))
        groups.append(g)
    json.dump(prompts, io.open("%s/regen2_list.json" % BASE, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    json.dump(groups, io.open("%s/regen2_order.json" % BASE, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print("第二輪重生成 %d 齣:" % len(groups))
    for g in groups:
        print("   -", g, "(%d 條硬性事實)" % len(JOBS[g]))
    return 0


raise SystemExit(main())
