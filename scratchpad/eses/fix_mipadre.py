# -*- coding: utf-8 -*-
"""mi padre sabina y yo —— 移除查無來源的細節、校正 Sabina 的角色定位。

五個來源(製作方兼場館 plotpoint.es / teatromadrid / tea3.eu / madridesteatro /
revistateatros)逐一比對後:

【對得上的,不動】海梅是單純天真的年輕歌手、華金是米其林三星主廚兼花花公子、
  12 月 28 日派對中被敲門、25 歲、住到親子關係被承認或 DNA 結果出爐、
  兩人在確認血緣前就先成了父子、閃回結構、Sabina 歌詞烘托情緒。

【改 1】「海梅剛與女友分手 / 刚结束一段感情 / still bruised by the end of a
  relationship」—— 五個來源全都沒有這件事。角色的具體身世不能沒有來源就寫。

【改 2】英文原寫 Sabina 是「Joaquín's idol, muse and imaginary guide」——
  把 Sabina 掛到父親這個角色身上。TEA3 的說法是對整個故事而言:
  「un tercer protagonista de la historia, al que no se ve nunca, pero que
   siempre está presente: Joaquín Sabina」。改成貼合來源的講法。

【補】繁中刪字後會掉出 400 字下限,補上這條已查證的事實(而不是隨便湊字)。
"""
import io
import json

KEY = "mi padre sabina y yo"

EN = (
    "This is not a musical in the usual sense but a play carried by songs, presided over by a "
    "third figure who never appears on stage and yet is present throughout: Joaquín Sabina "
    "himself. On 28 December the doorbell cuts through one of Joaquín’s habitual parties: amid "
    "the women, drink, noise and rock-and-roll excess, a 25-year-old stranger named Jaime stands "
    "outside claiming to be his son. Jaime, a young singer, ingenuous and unsure of where his "
    "life is heading, has tracked down the man he believes to be his father. Joaquín is a "
    "celebrated three-Michelin-star chef, but he is also an irrepressible womanizer: charming, "
    "reckless, determined to remain young, and used to arranging his life around pleasure rather "
    "than responsibility. Jaime refuses to leave until Joaquín acknowledges him—or until the "
    "results of an ADN test settle the question—and the unexpected visitor moves into Joaquín’s "
    "home.\n\n"
    "The forced arrangement immediately unsettles them both. Jaime’s innocence, caution and "
    "comparatively orderly habits clash with Joaquín’s unruly existence, while Joaquín’s bravado "
    "and appetite for risk challenge the young man’s idealized notions of adulthood and "
    "fatherhood. Their arguments expose mutual vulnerabilities: Jaime’s need to belong and to "
    "find direction, and Joaquín’s fear of age, commitment and the consequences of the life he "
    "has chosen. As their days together unfold, flashbacks illuminate the emotional routes that "
    "brought them to this confrontation, while songs shape the shifts between comic chaos, "
    "confrontation and moments of unexpected tenderness.\n\n"
    "Waiting for the ADN results becomes more than a practical delay. Jaime and Joaquín trade "
    "advice, irritate one another, test boundaries and gradually discover forms of trust neither "
    "expected. By the time certainty about their biological connection can arrive, their shared "
    "experiences have already begun to create a relationship that feels recognizably like that "
    "of father and son.\n\n"
    "The musical considers whether family is determined by blood, choice, or the care people "
    "learn to give one another. It also weighs youthful uncertainty against the loneliness "
    "beneath perpetual freedom, finding warmth and humour in two flawed people learning to face "
    "reality together."
)

ZH_HANT = (
    "12月28日，米其林三星主廚華金正與一群女子狂歡，"
    "25歲的年輕歌手海梅卻突然敲開他的門，"
    "自稱是他失散多年的兒子。"
    "風流不羈、把派對和情場當成日常的華金，"
    "面對這個拘謹單純、凡事循規蹈矩的陌生青年，"
    "只想盡快擺脫麻煩；"
    "海梅則堅信眼前人就是父親，"
    "決定在親子鑑定結果出爐前住進公寓，"
    "逼他正視這段可能存在的血緣關係。\n\n"
    "兩個原本毫無交集的男人被迫共處。"
    "華金習慣以玩笑、酒精與情人逃避歲月和責任；"
    "海梅則帶著對父親的想像、對人生的迷惘，"
    "以及過分規矩而不懂變通的生活態度。"
    "生活習慣與價值觀的衝突接連爆發，"
    "父子身分尚未獲得證實，"
    "彼此卻已在爭吵、試探與互相拆臺之中，"
    "看見對方不願示人的脆弱。"
    "故事穿插回憶片段，"
    "並以華金・薩維納的歌曲串起角色的情緒與人生選擇；"
    "薩維納本人從未現身，卻像第三位主角般始終在場。\n\n"
    "鑑定報告究竟會如何判定，並不是唯一的答案。"
    "在等待真相的日子裡，"
    "華金與海梅已逐漸學會接納彼此，"
    "也在一段意外展開的關係中，"
    "重新理解父親、兒子與成長的意義。"
)

ZH_HANS = (
    "12月28日，米其林三星主厨华金正与一群女子狂欢，"
    "一名25岁的年轻歌手海梅突然敲开了他的家门。"
    "海梅坚称华金是自己从未谋面的父亲，并带着行李住下："
    "在华金承认亲子关系、或DNA检测结果出来之前，他绝不离开。"
    "突如其来的儿子打破了华金以派对、艳遇和放纵维系的生活秩序，"
    "也迫使这个自认永远年轻的男人面对被搁置多年的责任。\n\n"
    "海梅则怀着对父亲的想象而来。"
    "他性格单纯、拘谨，"
    "渴望从这位陌生父亲身上找到归属；"
    "可眼前的华金既不符合他的期待，"
    "也不愿被家庭身份束缚。"
    "等待鉴定期间，"
    "两个人生观截然相反的男人不得不共处一室："
    "华金嫌海梅过分规矩，"
    "海梅也难以接受父亲的玩世不恭。"
    "争吵与试探接连发生，"
    "让两人各自的脆弱、孤独和恐惧逐渐暴露。\n\n"
    "剧情以闪回穿插现实，"
    "华金·萨维纳的歌曲贯穿父子相处的起伏，"
    "为他们说不出口的失落、欲望与温情补足情绪；"
    "萨维纳本人从未登台，却像第三位主角般始终在场。\n\n"
    "亲子鉴定尚未揭晓，"
    "父亲与儿子的关系却已在琐碎碰撞中悄然生成。"
    "血缘或许需要证明，"
    "但理解、陪伴与互相改变，"
    "先让两个陌生人成为了彼此生命中不可替代的人。"
)

PLAN = [("en", "en", EN), ("zh-hant", "zh", ZH_HANT), ("zh-hans", "zh-hans", ZH_HANS)]
WINDOW = {"en": (220, 340), "zh-hant": (400, 450), "zh-hans": (400, 450)}

# 查無來源的字串必須真的不在新文本裡。空的檢查等於沒檢查 —— 這裡的每一條
# 在【舊】文本裡都確實存在(所以它抓得到東西),不是恆真的檢查。
BANNED = {
    "en": ["bruised by the end of a relationship", "idol, muse and imaginary guide"],
    "zh-hant": [u"剛與女友分手"],
    "zh-hans": [u"刚结束一段感情"],
}


def size(lang, text):
    return len(text.split()) if lang == "en" else len(text.replace("\n", ""))


def main():
    old = {}
    for lang, sub, _ in PLAN:
        d = json.load(io.open("data/synopses_library/%s.json" % lang, encoding="utf-8"))
        old[lang] = d["syn"][KEY][sub]

    bad = []
    for lang, _sub, text in PLAN:
        lo, hi = WINDOW[lang]
        n = size(lang, text)
        print("%s%-8s %d  (%d~%d)" % ("OK " if lo <= n <= hi else "!! ", lang, n, lo, hi))
        if not (lo <= n <= hi):
            bad.append(lang)
        for b in BANNED[lang]:
            if b not in old[lang]:
                print("!! 檢查無效:%s 的舊文本本來就沒有 %r,這條檢查抓不到東西" % (lang, b))
                bad.append(lang)
            elif b in text:
                print("!! %s 新文本仍含 %r" % (lang, b))
                bad.append(lang)
    if bad:
        print("中止,未寫檔")
        return 1

    for lang, sub, text in PLAN:
        p = "data/synopses_library/%s.json" % lang
        d = json.load(io.open(p, encoding="utf-8"))
        d["syn"][KEY][sub] = text
        with io.open(p, "w", encoding="utf-8") as f:
            json.dump(d, f, ensure_ascii=False, indent=2)
        print("寫入 %s" % p)
    return 0


raise SystemExit(main())
