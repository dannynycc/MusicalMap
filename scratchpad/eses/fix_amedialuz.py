# -*- coding: utf-8 -*-
"""a media luz —— 用官方查證結果取代自創細節。

為什麼要改(逐項對官方):
  1. 繁中原寫「在酒吧般曖昧的夜晚裡」—— 官方三處(製作方 OnBeat / 場館 Espacio Alma /
     Cartelera Musicales)一致只說「una ciudad」,沒有任何酒吧。而劇組官方 IG
     @_a_media_luz_ 的角色貼文寫 JULIÁN 是「Un español en Buenos Aires」,
     城市其實是布宜諾斯艾利斯 —— 原文既錯又漏。
  2. 簡中原寫「其中一人渴望挣脱既有关系…另一人则害怕承认…第三人看似自由洒脱」——
     完全是推想。官方 IG 三則角色介紹給的是完全不同的設定:
       JULIÁN  Un español en Buenos Aires. Un hombre de certezas. O eso cree.
       CLARA   Brillante y difícil de sorprender. Observa. Entiende más de lo que dice.
       TOMÁS   Llega tarde. Siempre. Y nunca por casualidad.
  3. 英文只有泛稱「three people」,沒用上已查證的角色名。

保留不動的部分(已逐句對上官方,不重寫):
  「三具身體與一座城市」= Musical de tango para tres cuerpos y una ciudad
  「不是能否同時愛上兩個人…不背叛自己」= El conflicto no es amar a dos personas,
     sino no saber cómo hacerlo sin traicionarse
  LGBTIQ+ / 愛、自由、連結 = De temática LGTBIQ+ … el amor, la libertad y los vínculos
"""
import io
import json

KEY = "a media luz"

EN = (
    "A tango for three bodies and a city. In Buenos Aires, where every tango seems to hold a "
    "secret, three lives are about to intersect: Julián, a Spaniard abroad and a man of "
    "certainties — or so he believes; Clara, brilliant and difficult to surprise, who observes "
    "and understands more than she says; and Tomás, who arrives late, always, and never by "
    "chance. Theirs is an openly LGBTIQ+ story about love, freedom and the bonds between people, "
    "in which attraction becomes both an invitation and a threat: the closer the three come to "
    "one another, the harder it is to preserve the reassuring stories they tell themselves.\n\n"
    "As the connections among the three deepen, affection refuses to fit into a simple, exclusive "
    "shape. Each person must confront not merely whom they desire, but what honesty requires when "
    "that desire reaches beyond a conventional couple. Silence, evasion and fear of causing pain "
    "turn intimacy into a delicate negotiation. A glance, a dance and an unfinished confession "
    "acquire the weight of decisions, while the city surrounding them becomes a fourth "
    "presence—watching, sheltering and reflecting their changing emotional landscape.\n\n"
    "The tension does not arise from the existence of love for two people, but from the "
    "uncertainty of how to sustain it without deceit, possessiveness or self-erasure. The three "
    "are forced to ask whether freedom can be lived responsibly, whether vulnerability can "
    "replace control, and whether they can meet one another as they truly are. Tango gives form "
    "to what speech cannot easily resolve: desire, jealousy, tenderness, hesitation and the hope "
    "that honesty may lead not to abandonment, but to a more generous way of being together.\n\n"
    "At its heart, A Media Luz considers love as an act of truthfulness rather than a matter of "
    "labels or fixed rules. It explores freedom, queer intimacy and human bonds, asking how "
    "people can love openly without betraying either themselves or those closest to them."
)

ZH_HANT = (
    "布宜諾斯艾利斯的夜色裡，"
    "每一支探戈都藏著祕密，"
    "三個人的生命即將交錯。"
    "胡利安是身在異鄉的西班牙人，"
    "自認凡事都有答案；"
    "克拉拉聰慧敏銳、難以被驚動，"
    "總是看得比說出口的更多；"
    "托馬斯永遠遲到，而且從不是碰巧。\n\n"
    "探戈不只是伴奏，"
    "也成為他們互相靠近、周旋與拉開距離的語言。"
    "每一次對舞都像一次坦白："
    "有人渴望被完整選擇，"
    "有人害怕承諾會限制自由，"
    "也有人在愛上兩個人之後，"
    "發現最難的並非做出取捨，"
    "而是不以謊言傷害任何一方。"
    "當壓抑已久的情感浮上檯面，"
    "三人必須停止以沉默維持表面的和諧。\n\n"
    "傳統愛情敘事期待的專一與佔有，"
    "和三人各自對自由、誠實與親密的想像彼此碰撞；"
    "他們既想保護對方，"
    "也怕自己的真心成為傷人的理由。"
    "隨著祕密揭露，"
    "曾經看似能共存的情感開始要求每個人表態。\n\n"
    "最後，三人明白愛情不會因逃避而變得簡單，"
    "也沒有任何形式能保證所有人毫髮無傷。"
    "唯有直視欲望與恐懼，"
    "在坦誠中重新協商彼此的連結，"
    "他們才可能找到不背叛自己、"
    "也不欺騙所愛之人的方式。"
    "這是一齣以 LGBTIQ+ 為題的探戈音樂劇，"
    "寫的是三具身體與一座城市。"
)

ZH_HANS = (
    "布宜诺斯艾利斯的夜色渐深，"
    "三个人的生命即将在探戈的旋律"
    "与昏暗灯光中交错，"
    "各自带着未说出口的心事。"
    "在这座城市里，每一支探戈都藏着一个秘密。\n\n"
    "胡利安是身在异乡的西班牙人，"
    "自认凡事都有答案——或者只是这么以为；"
    "克拉拉聪慧敏锐、难以被惊动，"
    "她观察，也懂得比说出口的更多；"
    "托马斯永远迟到，而且从不是碰巧。"
    "三人的关系随着一次次相见而改变："
    "暧昧不再只是游戏，"
    "承诺也不再能够轻易说出口。"
    "传统探戈中关于欲望、失落与重逢的旋律，"
    "映照着他们的犹疑，"
    "让每一次拥抱都同时包含靠近与退缩。\n\n"
    "当感情不再符合单一、明确的答案，"
    "他们不得不面对真正的难题："
    "不是能否同时爱上两个人，"
    "而是如何在爱里坦诚、尊重彼此，"
    "并且不背叛自己。"
    "欲望、嫉妒、温柔与恐惧交织，"
    "让短暂的相遇成为对亲密关系的考验。\n\n"
    "三人未必找到完美的相处公式，"
    "却开始学会直视自己的需要，"
    "也承认他人的选择。"
    "这是一部以 LGBTIQ+ 情感为核心的作品，"
    "写的是三具身体与一座城市；"
    "故事以探戈般忽近忽远的节奏收束，"
    "把爱情呈现为一场需要勇气与诚实共同完成的舞蹈。"
)

PLAN = [("en", "en", EN), ("zh-hant", "zh", ZH_HANT), ("zh-hans", "zh-hans", ZH_HANS)]

# 護欄:長度窗口。超出就整支中止,不寫任何一個檔(避免只改一半)。
WINDOW = {"en": (220, 340), "zh-hant": (400, 450), "zh-hans": (400, 450)}


def size(lang, text):
    return len(text.split()) if lang == "en" else len(text.replace("\n", ""))


def main():
    bad = []
    for lang, _sub, text in PLAN:
        lo, hi = WINDOW[lang]
        n = size(lang, text)
        mark = "OK " if lo <= n <= hi else "!! "
        print("%s%-8s %d  (%d~%d)" % (mark, lang, n, lo, hi))
        if not (lo <= n <= hi):
            bad.append(lang)
    # 自創細節必須真的消失 —— 不是「我以為改掉了」
    for needle, lang in ((u"酒吧", "zh-hant"),               # 酒吧
                         (u"第三人看似", "zh-hans")):  # 第三人看似
        src = dict((l, t) for l, _s, t in PLAN)[lang]
        if needle in src:
            print("!! %s 仍含自創字串 %s" % (lang, needle))
            bad.append(lang)
    if bad:
        print("中止,未寫檔")
        return 1

    for lang, sub, text in PLAN:
        p = "data/synopses_library/%s.json" % lang
        d = json.load(io.open(p, encoding="utf-8"))
        assert KEY in d["syn"], "%s 找不到 %s" % (lang, KEY)
        d["syn"][KEY][sub] = text
        with io.open(p, "w", encoding="utf-8") as f:
            json.dump(d, f, ensure_ascii=False, indent=2)
        print("寫入 %s" % p)
    return 0


raise SystemExit(main())
