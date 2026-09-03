# -*- coding: utf-8 -*-
"""為查出錯誤的劇目產生【事實受限】的重生成提示。

⚠ 為什麼這裡可以餵官方事實,第一輪卻不行:
   第一輪的提示只釘身份不給情節,目的是讓產出【獨立於帳本】,我才能拿帳本當裁判做查證。
   查證已經做完、錯誤已經逐項記在 verify_en.json 之後,再用官方事實去約束重生成,
   就不是球員兼裁判,而是「照判決結果修正」。

用法: python scratchpad/gap19/mk_regen.py
輸出: scratchpad/gap19/regen_list.json(給 px_gen 用的提示陣列)
      scratchpad/gap19/regen_order.json(對應的 group 順序)
"""
import io
import json
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
BASE = "scratchpad/gap19"

# 每齣要重生成的劇 + 這次一定要遵守的硬性事實(全部來自帳本與外部查證)
JOBS = {
    "na prochach": [
        "The family on stage is called BARKER (Robert, Rosa, Adam, Archibald, Rupert Barker). "
        "NEVER write Sackler, Purdue or OxyContin — the production fictionalises the name.",
        "The official cast also includes KRÓLOWA OPIOIDÓW (the Opioid Queen), a major figure "
        "played by the show's choreographer, with long wordless danced sequences. Include her.",
        "Other official characters: Megan Queen, Evelyn Morgan, Oliver Harris, "
        "Carole/Konferansjerka/Brenda, Becky/Nancy, Dennis Stone/dr van Hoff/dr Berkeley/Bob.",
        "Do NOT invent professions. The official cast list gives none — do not call Oliver Harris "
        "a journalist or Evelyn Morgan a prosecutor.",
        "A Konferansjerka (female compère) is an official role, so a show-like framing is correct, "
        "but do NOT say it is a television show — no source says that.",
        "Official facts to keep: the painkiller turned out to be opium in pills; patients moved on "
        "to street heroin; over 500,000 Americans have died; the makers' court settlement cost "
        "less than their profit and secured them impunity.",
    ],
    "romeo i julia": [
        "This is Studio Buffo's Polish musical (music Janusz Stokłosa, Polish text Agata "
        "Miklaszewska, directed and choreographed by Janusz Józefowicz) — NOT the French "
        "'Roméo et Juliette' and NOT a straight staging of Shakespeare.",
        "🚨 The official cast contains a character called DEALER (a drug dealer) who does not "
        "exist in Shakespeare. The official content warnings are: drugs, suicide, killing, "
        "profanity, murder, mourning. The drug thread must appear in the synopsis.",
        "Official cast: Julia, Romeo, Pani Capuletti, Pan Capuletti, Niania, Parys, Benvolio, "
        "Merkucjo, Tybalt, Ojciec Laurenty, Dealer, Rosalina. "
        "There are NO Montague parents in this production.",
        "Official framing: the love of two young people who cannot reach an understanding with "
        "the adult world; a drama of parents and children who cannot talk to, listen to or "
        "respect each other; uncompromising young love meeting the ruthlessness of the parents' "
        "commercial world.",
    ],
    "piotrus pan": [
        "🚨 The Darling brothers are called JAŚ and MIŚ in this production — never Janek or "
        "Michaś.",
        "Official cast: Piotruś Pan, Wendy, Dorosła Wendy (grown-up Wendy), Jane (Wendy's "
        "daughter), Jaś, Miś, Pan Darling, Pani Darling, Kapitan Hak, Tygrysica z Lilią w Zębach, "
        "Sznaps, Wódz Olbrzymia Pantera Mniejsza, Powtórka, Ciutek, Trąbal, Rybol, Szpic, Nana.",
        "Do NOT name the island: no source gives its name in this production. Never write "
        "'Nibywalencja' — that name appears in no source at all. Describe it generically.",
        "Do NOT name the fairy: 'Dzwoneczek' is not in the official cast list.",
        "The crocodile does appear. Libretto and lyrics by Jeremi Przybora, music Janusz "
        "Stokłosa; this Studio Buffo staging premiered on 12 December 2015.",
    ],
    "caperucita roja": [
        "🚨 The official synopsis says Caperucita is helped by HER FRIENDS (sus amigos) and by "
        "AN UNEXPECTED HERO (un inesperado héroe). Do NOT write that a huntsman/Cazador rescues "
        "her — a huntsman is the classic version's character and is not 'unexpected'.",
        "Official characters: Caperucita Roja, the Lobo Feroz, la abuelita. "
        "Do not invent others by name.",
        "Official plot: she is curious and brave and goes into the forest with a basket of food "
        "for her grandmother; the cunning wolf plots to reach the grandmother's house first and "
        "eat them both; with her friends and an unexpected hero she learns the value of listening "
        "to her elders and being careful. Comedy, action and music for the whole family.",
        "Do NOT characterise the grandmother as madder than the wolf — no source says that.",
    ],
    "precure colorful runway": [
        "🚨 The producers announced this show on 1 September 2026 and have published almost no "
        "plot. Write ONLY what is officially published; invent nothing.",
        "Official text: an all-new original stage story for the male Precure; this time the theme "
        "is FASHION; it portrays the boys' life-size everyday lives and their duty as Precure, "
        "with staging, song and action unique to the theatre, shining like a colourful runway.",
        "Official characters: Cure Silhouette / Kamishiro Ayato, Cure Collage / Hachibari Itsuki, "
        "Cure Flash / Mikuriya Oji, Cure Trad / Envy, Momose Akihiko, Bogart, Banshee, Gothic.",
        "Do NOT invent the villains' motives, the characters' personalities, or any battle "
        "description. Do not claim what the enemies want. Keep it short and factual; it is "
        "acceptable for this synopsis to be shorter than usual.",
    ],
    "edda musical a kor": [
        "🚨 At the start a soul in heaven chooses to be born as Elmó's son and discusses it with "
        "THE UNIVERSE (az Univerzum) — not with an 'Isteni Hang' / 'divine voice'.",
        "Official/verified characters: Elmó (the protagonist), Angóra (his girlfriend, who leaves "
        "him because she thinks the relationship beneath her), Fausztusz (Angóra's influential "
        "father, who runs for president), Szezár (leader of a motorcycle gang), Írisz (Szezár's "
        "sister), Frédi (who becomes Elmó's manager and makes him a successful singer).",
        "Ending as staged since 2024: Fausztusz wins the election, admits at a mass rally that "
        "his campaign was not wholly truthful and that austerity follows, an uprising breaks out, "
        "Frédi is shot; the stage darkens and the final scene jumps ten years ahead, where Elmó "
        "and Írisz have a son and Frédi's vision of that unborn child is recalled.",
        "This staging uses 24 EDDA songs and honours the band's 50th anniversary.",
    ],
    "天堂邊緣": [
        "🚨 The three souls have watched over 震宇 for TWENTY-NINE years (29年), since his birth "
        "— not twenty-eight.",
        "Official characters: 秀燕, 何智, 菲菲 (three souls wandering the human world), 震宇 "
        "(the man they have guarded since birth), and 天使 (the Angel).",
        "Official plot: the three souls cannot leave. An angel suddenly appears and tells them "
        "they must each complete their own last regret within 24 hours before they can travel on "
        "to heaven. A search across family love, friendship and romantic love then unfolds.",
        "Do NOT assign specific regrets to specific souls — the official text does not say which "
        "regret belongs to whom.",
        "Official theme: true fulfilment in life is not the absence of regret, but learning how "
        "to let go and to cherish everyone around you.",
    ],
    "wypior": [
        "Official framing (keep it): Marta and Łukasz are a couple going through a relationship "
        "crisis; the closing question is whether the leading figure of Polish Romanticism still "
        "has the power TO SAVE the relationship of two thirty-somethings in the big city. "
        "Do not write only that he makes their life impossible.",
        "Official facts: Adam Mickiewicz lives as a vampire in a flat in the fashionable area of "
        "pl. Zbawiciela in contemporary Warsaw; by day he hides in the wardrobe from the deadly "
        "sun; at night he steals blood from a hospital bin.",
        "Do NOT name a specific hospital or park, and do NOT say whose flat it is — no source "
        "gives those details.",
        "Official cast: Wypiór (Adam Mickiewicz), Marta, Łukasz, and two actors covering "
        "Syrenka/Pielęgniarka/Zofia Szymanowska/prof. Klicka/Matka and "
        "Detektyw/Stróż/Dyrektor muzeum/Kot Eks.",
        "Based on Grzegorz Uzdański's novel, most of it written in thirteen-syllable verse; "
        "played in the Bistro Syrena space; a mixture of theatre, musical and literary cabaret.",
    ],
}


def main():
    led = json.load(io.open("%s/ledger.json" % BASE, encoding="utf-8"))
    order = json.load(io.open("%s/order.json" % BASE, encoding="utf-8"))
    ident = json.load(io.open("%s/list.json" % BASE, encoding="utf-8"))
    idx = {g: i for i, g in enumerate(order)}
    prompts, groups = [], []
    for g, rules in JOBS.items():
        base = ident[idx[g]]
        block = " ".join("(%d) %s" % (i + 1, r) for i, r in enumerate(rules))
        prompts.append("%s. VERIFIED FACTS about this production — the synopsis must not "
                       "contradict any of them: %s" % (base, block))
        groups.append(g)
    json.dump(prompts, io.open("%s/regen_list.json" % BASE, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    json.dump(groups, io.open("%s/regen_order.json" % BASE, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print("重生成清單 %d 齣:" % len(groups))
    for g in groups:
        print("   -", g, "(%d 條硬性事實)" % len(JOBS[g]))
    return 0


raise SystemExit(main())
