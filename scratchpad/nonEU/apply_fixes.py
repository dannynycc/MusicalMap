# -*- coding: utf-8 -*-
"""非歐陸範圍修正的唯一入口(使用者 2026-09-01 授權第 2、3 類)。
每條附來源與理由;匹配不到就大聲失敗,不靜默跳過。"""
import io, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

LIB = 'data/synopses_library/%s.json'
SUB = {'en': 'en', 'zh-hant': 'zh', 'zh-hans': 'zh-hans'}

RULES = {
'en': [
  ('grand hotel', 'steal jewels from the fading Russian ballerina',
   'steal the necklace of the fading Russian ballerina',
   'MTI 官方 full synopsis 全文只寫 "a necklace / her precious necklace",從不指明材質;'
   '原句 "jewels" 雖不算錯,但改用 necklace 與官方一致'),
  ('screwtape letters', 'With the seasoned demon Lilith as part of the operation',
   'With the seasoned demon Black Angel as part of the operation',
   '角色名錯。此為韓國原創音樂劇(PLAYDB:창작뮤지컬),官方角色是 블랙엔젤(Black Angel)。'
   '6 個獨立來源一致:Naver Blog「경험 많은 악마 블랙엔젤」、나무위키 卡司、'
   'Instagram×2/Facebook/Threads 謝幕紀錄「블랙엔젤 役 서하임」'),
  ('screwtape letters', 'placing Wormwood and Lilith under increasing pressure',
   'placing Wormwood and Black Angel under increasing pressure', '同上'),
],
'zh-hant': [
  ('grand hotel', '費利克斯潛入她房內欲偷走鑽石項鍊',
   '費利克斯潛入她房內欲偷走項鍊',
   'MTI 官方 full synopsis 不指明材質(只說 a necklace);「鑽石」僅見於 en.wikipedia 且無註腳,'
   '而原著與 1932 電影是珍珠 → 拿掉材質,兩邊都不超出官方'),
  ('grand hotel', '紡織廠老闆普萊辛', '紡織廠總經理普萊辛',
   'MTI 逐字「Preysing, a general manager of a textile mill」;中文「老闆」指 owner,'
   '但他是受雇的總經理(劇中要向 shareholders 交代)'),
  ('screwtape letters', '與經驗豐富的女惡魔莉莉絲納入特訓',
   '與經驗豐富的惡魔黑天使納入特訓',
   '角色名錯,官方是 블랙엔젤(Black Angel);「經驗豐富」對應官方「경험 많은 악마」正確。'
   '「女」字拿掉:官方文案未言明性別,該角由 서하임、김태영 輪演'),
  ('rebelove karlin', '剛高中畢業的泰蕾莎在捷克邊境小鎮幫父親打理新開的咖啡館，和好友茱莉卡、布吉娜',
   '剛高中畢業的泰蕾莎在捷克邊境小鎮，和好友茱莉卡、布吉娜',
   '「幫父親打理新開的咖啡館」查 6 個管道皆無(cs.wiki / ČSFD 官方 Obsah / 音樂劇角色表 / '
   'Google 捷克語多輪 / Novinky 劇評被 cookie 牆擋 / TipTicket)→ 依 SOP「官方查不到的細節不放行」移除。'
   '父親這條線在後文「與父親的憂慮之間」已有,且音樂劇角色表確有 Terezin otec'),
  ('rebelove karlin', '直到三名自稱修理工的陌生青年出現',
   '直到三名陌生青年出現',
   '「自稱修理工」同樣 6 管道查無;後文本來就會揭曉他們是逃兵(ČSFD:kluk, který utekl z vojny)'),
],
'zh-hans': [
  ('grand hotel', '男爵原想偷走她的珍珠项链', '男爵原想偷走她的项链',
   '同繁中:MTI 官方不指明材質。「珍珠」是原著與 1932 電影的設定,不是這齣音樂劇官方所寫'),
  ('grand hotel', '他与野心勃勃的企业家普赖辛格相识',
   '他与纺织厂总经理普赖辛格相识',
   'MTI 逐字「a general manager of a textile mill」;「企业家」過於模糊'),
  ('screwtape letters', '地狱资深引诱者斯克鲁泰普奉命指导年轻恶魔伍木，',
   '地狱资深引诱者斯克鲁泰普奉命指导年轻恶魔伍木，并让经验丰富的恶魔黑天使一同参与，',
   '補上官方三大主要角色之一 블랙엔젤(Black Angel);簡中原本完全沒有這個角色'),
  ('moon sorbet', '躲进冷气房贪凉', '躲进空调房贪凉',
   '「冷氣房」是台灣用語,大陸說「空调房」。這篇簡中是繁中的純字轉換,沒做用語在地化'),
  ('moon sorbet', '热心的主委奶奶', '热心的管委会主委奶奶',
   '「主委」是台灣公寓大廈管理委員會主任委員的簡稱,大陸讀者難懂。'
   '⚠ 刻意「不」改成「楼长/居委会主任」——那是大陸的社區制度,會把這齣台灣的戲寫成大陸社區='
   '改變事實;改為補全職稱,既保留台灣脈絡又讓人看懂'),
  ('moon sorbet', '悄悄藏着全球暖化与环境的提醒', '悄悄藏着全球变暖与环境的提醒',
   '「全球暖化」台灣用語 /「全球变暖」大陸標準術語,經 zh.wikipedia 地區詞轉換確認'),
  ('月亮雪酪', '躲进冷气房贪凉', '躲进空调房贪凉', '同 moon sorbet(同一齣劇的另一個 group)'),
  ('月亮雪酪', '热心的主委奶奶', '热心的管委会主委奶奶', '同上'),
  ('月亮雪酪', '悄悄藏着全球暖化与环境的提醒', '悄悄藏着全球变暖与环境的提醒', '同上'),
],
}

def main():
    tot_ok = tot_already = tot_miss = 0
    for lang, rules in RULES.items():
        path = LIB % lang
        d = json.load(io.open(path, encoding='utf-8'))
        syn = d.get('syn', d)
        k = SUB[lang]
        ok = already = miss = 0
        for g, old, new, why in rules:
            rec = syn.get(g)
            if not isinstance(rec, dict) or k not in rec:
                print('  [!] %s / %s: 找不到該組或該語言' % (lang, g)); miss += 1; continue
            t = rec[k]
            # 🚨 冪等判斷:不能只看 old 在不在。當 new 「包含」old 時(例如在原句後面
            #    插入一段),套用後 old 仍然在文中,若只憑 old 就會**重複插入**。
            #    2026-09-01 實際踩到:screwtape 簡中被插入兩次「并让经验丰富的恶魔黑天使一同参与，」。
            if new in t and (old not in t or new.find(old) >= 0):
                already += 1; continue
            if old not in t:
                print('  [!] %s / %s: 原文匹配不到 -> %r' % (lang, g, old[:44])); miss += 1; continue
            rec[k] = t.replace(old, new, 1)
            ok += 1
        json.dump(d, io.open(path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        print('%-8s 套用 %d / 已套用 %d / 匹配不到 %d' % (lang, ok, already, miss))
        tot_ok += ok; tot_already += already; tot_miss += miss
    print('-' * 44)
    print('合計 套用 %d / 已套用 %d / 匹配不到 %d' % (tot_ok, tot_already, tot_miss))
    return 1 if tot_miss else 0

if __name__ == '__main__':
    sys.exit(main())

