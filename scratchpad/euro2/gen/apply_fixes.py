# -*- coding: utf-8 -*-
"""euro2(4 部新進匈牙利劇)三語修正的唯一入口。

原則(同 2026-08-31 夜訂立的流程):
  * 判準 = 「這個製作自己怎麼寫」(官方角色表 / 官方劇情 / 專業樂評);
    原著、電影、其他語言版本只能當對照。
  * 每條規則都寫明理由與來源;匹配不到就大聲失敗,不靜默跳過。
  * 已套用過(new 已在文中)= already,不算錯。
"""
import io, json, os, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)))

RULES = {
"out_en.json": [
  # ---- 1. Szeretve mind a vérpadig ----
  ("Szeretve mind a v", "Szunyoghy Ozmanda’s presence", "Szunyoghy Ozmonda’s presence",
   "官方角色表逐字作「SZUNYOGHY OZMONDA, grófnő」(jegy.hu / port.hu / atempo.sk / Magyar Nemzet 一致);生成拼成 Ozmanda"),

  # ---- 2. Egri csillagok ----
  ("Egri csillagok", "Bornemissza Gergely and the young Vicuska are seized by the one-eyed Jumurdzsák",
   "Bornemissza Gergely and Cecey Éva are seized as children by the one-eyed Jumurdzsák",
   "本製作官方劇情逐字:「Bornemissza Gergely és Cecey Éva gyermekként esik a félszemű Jumurdzsák fogságába」——官方一律用 Cecey Éva,Vicuska 是原著中的小名"),
  ("Egri csillagok", "between Gergely and Vicuska, later known as Cecey Éva, while",
   "between Gergely and Éva, while",
   "同上;且「later known as Cecey Éva」把本名說成後來才有的稱呼,與官方相反"),

  # ---- 3. Valahol Európában ----
  ("Valahol Eur", "Kuksi’s song rises over a Europe torn apart by war, where hungry",
   "Somewhere in a Europe torn apart by war, hungry",
   "本劇 Kuksi 的曲子是「Nem szabad félni!(Kuksi halála)」= 他的臨終之歌,放在開場會誤導"),
  ("Valahol Eur", "That fragile refuge is tested when hostile villagers, stirred against the children, close in on the castle.",
   "That fragile refuge is tested when the children are found out and adults from the surrounding country set out to seize them, closing in on the castle.",
   "hu.wiki 劇情逐字:「A gyerekek azonban lebuknak, és elfogatásukra több felnőtt is megindul.」——是四鄰的成年人出動,不是「被煽動的村民」"),
  ("Valahol Eur", "They defend their home together, and when some of the children are captured, the others fight for their release. As the war finally ends, Simon turns the old castle into an official home for the children, giving permanence to the belonging they have created together.",
   "They defend their home together, and in the shooting one of the youngest, Kuksi, is fatally wounded — to save him the band must carry him down into the village, knowing that capture is certain. Kuksi does not survive, but Simon returns from the town with an order clearing the children of the thefts hunger had forced on them and handing the castle over into their own possession, giving permanence to the belonging they had created together.",
   "「有人被抓、其他人去營救」查無來源。hu.wiki 逐字:「egy puskalövéstől az egyik gyerek, Kuksi halálos sebesülést szerez. Kénytelenek bevinni őt a faluba, holott tudják, így elfogják őket. Kuksi meghal, ám Simon a városból olyan rendelkezést hoz, amely a gyermekeket felmenti a … büntetések alól, és a várat is az ő birtokukba adja.」"),

  # ---- 4. Ezeregy éjszaka ----
  ("Ezeregy", "Seherezádé is led before Sahriár király, a ruler",
   "Seherezádé is led before King Sahriár, a ruler",
   "「király」是匈牙利語的「國王」,直接搬進英文句子等於寫成 King Sahriár king"),
  ("Ezeregy", "Sahriár király gradually moves from listening",
   "King Sahriár gradually moves from listening", "同上"),
  ("Ezeregy", "Sahriár király’s path back to empathy",
   "King Sahriár’s path back to empathy", "同上"),
  ("Ezeregy", "Harún, a naive young prince, is swept into dangers beyond the safety of court life.",
   "Harún, a young ruler stripped of his throne and of his sight, is swept into dangers far beyond anything the court had prepared him for.",
   "Spirituszonline 樂評(László Ferenc)逐字:「Alida … a trónjától és látásától megfosztott ifjú uralkodó talpraesett támasza」——哈倫是被奪走王位與視力的年輕君主,不是安居宮中的王子"),
  ("Ezeregy", "The talkative Dzsinn offers marvels and wishes",
   "The talkative Dzsinn, freed from his bottle, offers marvels and wishes",
   "同一篇樂評:「a palackból szabadult Dzsinn és Bek-Bek, a főeunuch」——本劇的精靈出自瓶子"),
  ("Ezeregy", "encounters with Maszrúr, Ifrit, a Jósnő, and even the Emberfejeket termő fa test the travellers",
   "encounters with Maszrúr, an ifrit, a fortune-teller and even a tree that grows human heads test the travellers",
   "官方角色表的匈牙利文標籤直接搬進英文散文(Jósnő=女預言家、Emberfejeket termő fa=長人頭的樹),英文讀者無法理解"),
],

"out_zht.json": [
  ("Ezeregy", "能言善道、力量驚人的神燈精靈則掀起",
   "能言善道、力量驚人的精靈被放出瓶外，掀起",
   "「神燈精靈」是迪士尼版。本劇官方角色為 DZSINN,樂評明載「a palackból szabadult Dzsinn」(從瓶中放出);該樂評整篇正是在說本劇是 Disney 版的替代品"),
  ("Ezeregy", "機靈的盜賊阿里周旋",
   "機靈的盜賊阿里達周旋",
   "官方角色表寫 ALI(DA),樂評全篇一律 Alida;只譯「阿里」會與簡中「阿里达」對不上"),
  ("Ezeregy", "天真卻心懷善意的王子哈倫，愛上美麗堅毅的茉莉公主",
   "遭篡位而失去王位的年輕君主哈倫，愛上蘇丹的女兒茉莉公主",
   "樂評:哈倫是「trónjától és látásától megfosztott ifjú uralkodó」(被奪王位與視力的年輕君主),非安居宮中的王子;官方角色表有「ÖREG SZULTÁN, JÁZMIN APJA」佐證茉莉是蘇丹之女。另「堅毅」與樂評所述她一度投向 Dzsáfár/黑暗面不符,改用有據的身分描述"),
],

"out_zhs.json": [
  ("Valahol Eur", "煽动者和村民把孩子们当作威胁，围攻城堡、抓走伙伴。",
   "孩子们的行踪败露，四邻的大人纷纷出动前来抓捕，围住了城堡。",
   "「煽动者」與「抓走伙伴」查無來源。hu.wiki 逐字:「A gyerekek azonban lebuknak, és elfogatásukra több felnőtt is megindul.」"),
  ("Valahol Eur", "而是与西蒙并肩守护家园，冒险营救同伴。战争的结束带来新的希望，西蒙也努力让城堡成为孩子们真正的归宿。",
   "而是与西蒙并肩守护家园；混乱的枪声中，最小的库克西身受致命枪伤，大家明知会被抓也只能把他送进村子。库克西没能活下来，西蒙则从城里带回一纸命令，免除孩子们因饥饿而偷窃的罪责，并把城堡判归他们所有。",
   "「冒险营救同伴」查無來源。hu.wiki 逐字:Kuksi 中槍致命→被迫送進村子明知會被捕→Kuksi 死→Simon 帶回命令免罪並把城堡判歸孩子所有"),
  ("Ezeregy", "也让他在乞丐装束中无人相信其身份",
   "也夺走了他的视力，流落市井后再无人相信他的身份",
   "「乞丐装束」查無來源;樂評明載他是「trónjától és látásától megfosztott」(被奪走王位「與視力」),以有據細節取代未證實細節"),
  ("Ezeregy", "满身狼狈的精灵胡克",
   "满身狼狈的精灵",
   "官方角色表只有「DZSINN ÉS BEK-BEK, A FŐEUNUCH」,無「胡克」這個角色;精靈在本劇無專名"),
],
}


def main():
    total_ok = total_already = total_missing = 0
    for fname, rules in RULES.items():
        path = os.path.join(BASE, fname)
        rows = json.load(open(path, encoding='utf-8'))
        ok = already = missing = 0
        for prefix, old, new, reason in rules:
            hit = [r for r in rows if r['show'].startswith(prefix)]
            if len(hit) != 1:
                print("  [!] %s / %s: prefix 命中 %d 筆" % (fname, prefix, len(hit)))
                missing += 1
                continue
            r = hit[0]
            if old not in r['synopsis']:
                if new and new in r['synopsis']:
                    already += 1
                    continue
                print("  [!] %s / %s: 原文匹配不到 -> %r" % (fname, prefix, old[:70]))
                missing += 1
                continue
            r['synopsis'] = r['synopsis'].replace(old, new)
            ok += 1
        json.dump(rows, open(path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        print("%-14s 套用 %d / 已套用 %d / 匹配不到 %d" % (fname, ok, already, missing))
        total_ok += ok; total_already += already; total_missing += missing
    print("-" * 46)
    print("合計 套用 %d / 已套用 %d / 匹配不到 %d" % (total_ok, total_already, total_missing))
    return 1 if total_missing else 0


if __name__ == '__main__':
    sys.exit(main())
