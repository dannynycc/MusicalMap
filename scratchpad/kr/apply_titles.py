# -*- coding: utf-8 -*-
"""把韓國 61 組裡【查得到官方依據】的中文劇名寫進 i18n_maps.json。

政策(同 i18n_maps._show_titles_note):只收有官方依據的名字。
下面每一筆的依據與來源記在 scratchpad/kr/titles_ledger.json,查無依據的一律不收
—— 那些組會照舊顯示原文,這是合格結果不是缺漏。

⚠ 繁簡【不是】自動轉換就好,以下這些兩邊確實不同,必須分開寫:
   브람스      繁 布拉姆斯      / 簡 勃拉姆斯
   생텍쥐페리   繁 聖修伯里      / 簡 圣埃克苏佩里
   연의 편지    繁 淵的信件      / 簡 渊之信      (兩邊官方網漫站各自的正式名)
   김종욱 찾기  繁 尋找完美先生   / 簡 寻找金钟旭   (台灣電影片名 / 大陸片名)
   목마와 숙녀  繁 木馬與淑女    / 簡 木马和淑女   (台港用「與」、大陸百度用「和」)
   크리스마스 캐럴 繁 聖誕頌歌   / 簡 圣诞欢歌
   블랙메리포핀스 繁 (不收)      / 簡 水曜日      (大陸官方授權中文版【更名】,非直譯,繁中不可套用)
   종의 기원   繁 物種起源      / 簡 (不收)     (只有繁體譯本;簡體「物種起源」被達爾文原著佔用)
   드림하이    繁 夢想起飛 Dream High / 簡 (不收)
"""
import io
import json

P = "data/i18n_maps.json"

# group_key: (繁, 簡)  —— None 表示該語言查無官方依據,不收
ADOPT = {
    "7080 뮤지컬 목마와 숙녀": ("木馬與淑女", "木马和淑女"),
    "back to 1931": ("BACK TO 1931：是無言 李龍道", "BACK TO 1931：是无言 李龙道"),
    "brahms": ("布拉姆斯", "勃拉姆斯"),
    "gwanghwamun love song": ("光化門戀歌", "光化门恋歌"),
    "black mary poppins": (None, "水曜日"),
    "m butterfly": ("蝴蝶君", "蝴蝶君"),
    "park yeol": ("朴烈", "朴烈"),
    "origin of species": ("物種起源", None),
    "welcome to the hyunam dong bookshop": ("歡迎光臨休南洞書店", "欢迎光临休南洞书店"),
    "your letter": ("淵的信件", "渊之信"),
    "그날들": ("那些日子", "那些日子"),
    "김종욱 찾기": ("尋找完美先生", "寻找金钟旭"),
    "미디어아트 뮤지컬 파랑새": ("青鳥", "青鸟"),
    "벚꽃동산 하얀 집": ("櫻桃園", "樱桃园"),
    "생텍쥐페리": ("聖修伯里", "圣埃克苏佩里"),
    "쇼뮤지컬 드림하이": ("夢想起飛 Dream High", None),
    "빨래": ("洗衣", "洗衣"),
    "오셀로와 이아고": ("奧賽羅與伊阿古", "奥赛罗与伊阿古"),
    "음악극 소요유": ("逍遙遊", "逍遥游"),
    "베어만 마지막잎새": ("貝爾曼：最後一片葉子", "贝尔曼：最后一片叶子"),
    "크리스마스 캐럴": ("聖誕頌歌", "圣诞欢歌"),
    "푸른 꽃": ("藍花", "蓝花"),
}


def main():
    m = json.load(io.open(P, encoding="utf-8"))
    tw, cn = m["show_titles_tw"], m["show_titles"]
    sh = json.load(io.open("data/shows.json", encoding="utf-8"))["shows"]
    live = set(r["group"] for r in sh)

    # 護欄 1:group 必須真的在目錄裡,否則是我打錯鍵(寫進去也不會生效,而且會靜默)
    missing = [g for g in ADOPT if g not in live]
    if missing:
        print("❌ 這些 group 不在目錄裡,中止:")
        for g in missing:
            print("   ", g)
        return 1

    # 護欄 2:不覆蓋既有譯名(既有的是先前批次查證過的,不該被這批蓋掉)
    clash = [g for g in ADOPT if g in tw or g in cn]
    if clash:
        print("⚠ 這些 group 已有譯名,略過不覆蓋:", clash)

    n_tw = n_cn = 0
    for g, (t, c) in ADOPT.items():
        if t and g not in tw:
            tw[g] = t
            n_tw += 1
        if c and g not in cn:
            cn[g] = c
            n_cn += 1

    m["show_titles_tw"] = dict(sorted(tw.items()))
    m["show_titles"] = dict(sorted(cn.items()))
    m["_show_titles_note"] += (
        " | 2026-09-02 韓國 61 組(v2.107.0 一次進來、當時零查證的那批)逐組查劇名譯名,"
        "22 組有官方依據採用、39 組查無依據保留原文。逐組的來源/信心度/捨棄候選記在 "
        "scratchpad/kr/titles_ledger.json。⚠ 繁簡確實不同的:布拉姆斯/勃拉姆斯、"
        "聖修伯里/圣埃克苏佩里、淵的信件/渊之信、尋找完美先生/寻找金钟旭、木馬與淑女/木马和淑女、"
        "聖誕頌歌/圣诞欢歌。⚠ 只收單邊的:블랙메리포핀스 只收簡體《水曜日》"
        "(大陸官方授權中文版【更名】不是直譯,繁中不可套用);종의 기원 只收繁體《物種起源》"
        "(簡體無譯本,且該詞已被達爾文原著佔用);드림하이 只收繁體《夢想起飛 Dream High》。"
        "🚨 同輪修掉一個系統性缺陷:interpark 的 clean_title 沒剝巡演城市後綴,"
        "「그날들 - 용인」與「그날들 - 이천」被拆成兩組,「팬레터 - 울산」也對不上已登記的 "
        "Fan Letter —— 已加 strip_tour_city() 並補齊 KO_CITY 缺的 20 個城市韓文對照。"
    )
    json.dump(m, io.open(P, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("寫入 繁 %d 筆、簡 %d 筆" % (n_tw, n_cn))
    print("show_titles_tw %d 筆、show_titles %d 筆" % (len(tw), len(cn)))
    return 0


raise SystemExit(main())
