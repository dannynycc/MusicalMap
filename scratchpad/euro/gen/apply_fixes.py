# -*- coding: utf-8 -*-
"""把 §3 查證抓到的事實錯誤套回生成結果(out_*.json)。

原則(SOP §3.4):**只改事實錯的那一處,不動語感、不整段重寫**。
每條規則都是精確字串替換;**匹配不到就報錯**(規則寫錯或原文變了要立刻知道,
不能默默跳過——默默跳過等於「以為修好了其實沒修」)。

用法:
    python scratchpad/euro/gen/apply_fixes.py --check   # 只檢查規則找不找得到(不寫檔)
    python scratchpad/euro/gen/apply_fixes.py           # 套用並寫回

⚠ 一定要等該語言的 px_gen 完全結束再跑:px_gen 每完成一部就把記憶體裡的
整個 results 陣列 dump 回檔案,中途改會被蓋掉。
"""
import json, io, os, sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))

# {檔案: [(show 前綴, 原文, 新文, 為什麼改), ...]}
RULES = {
    "out_en.json": [
        ('A meseautó',
         'the impeccably self-assured managing director of a Budapest bank',
         'the impeccably self-assured managing director of the Központi bank',
         '🚨 撤回我先前的誤修。Veres 1 Színház 官方角色表第一行為「**SZŰCS JÁNOS, a Központi bank vezérigazgatója**」——銀行名 **Központi bank 是官方寫的**,生成本來就對;我當時判定「查無據」而改成「a Budapest bank」是錯的(§3 誤修清單第 8 條)。此規則把它改回官方寫法。'),
        # ⚠ 以下 6 條規則已在 §3(真 Chrome 逐部深查)被推翻並刪除,切勿復原:
        #   A Christmas Carol「Rose」  — 官方卡司有「Isabella Tabarini — Rose Cratchit」
        #   Saturnin「Jirotka」×3      — hybernia.eu 卡司框有「Jirotka — Radek Melša」
        #   Belle e la Bestia 公主記憶 — 官方 SINOSSI 有「il ricordo del volto della principessa
        #                                che il potente sortilegio aveva cancellato per sempre」
        #   Zlatovláska 四姊妹         — Černovláska/Rudovláska/Hnědovláska/Plavovláska 是官方角色
        #   (連同先前刪除的 Macskafogó 一條,共 7 條「把對的改成錯的」修法已全部撤除)
        #   根因:拿原著/電影當標準去「訂正」舞台製作,且用 proxy 工具讀不到摺疊的卡司表。

        # ── 幻覺的人名 ────────────────────────────────────────────────


        # ── 查無據的組織名 ──────────────────────────────────────────
        ("VY NEJSTE",
         "who spots an opportunity to turn Milan’s refusal into a public cause for Liga tolerance.",
         "who spots an opportunity to turn Milan’s refusal into a public cause campaigned in the name of tolerance.",
         "「Liga tolerance」在官方頁、劇院頁與各售票頁都查不到"),
        ("VY NEJSTE",
         "while Žalobce uses the proceedings to promote Liga tolerance.",
         "while Žalobce uses the proceedings to promote his own cause.",
         "同上"),
        ("VY NEJSTE",
         "The story then widens when Liga tolerance wins the election.",
         "The story then widens when that movement wins the election.",
         "同上"),

        # ── Belle e la Bestia:官方沒有的身世與身世懸念 ──────────────
        ("Belle e la Bestia",
         "Meanwhile, Belle, the kind-hearted daughter of a widowed merchant, is drawn by chance into the Beast’s isolated world.",
         "Meanwhile, Belle, a young woman of pure heart and free spirit, is drawn by chance into the Beast’s isolated world.",
         "官方 sinossi 只說她是「dal cuore puro e dallo spirito libero」的年輕女子,沒有喪偶商人父親的設定"),
        ("Belle e la Bestia",
         "As buried memories begin to surface, the central mystery becomes urgent: is Belle truly connected to the lost Princess, and can their renewed love overturn the curse before Miguel’s designs destroy them both?",
         "As buried memories begin to surface, the question becomes urgent: can what grows between them overturn the curse before Miguel’s designs destroy them both?",
         "同上,刪掉無據的「Belle 就是失落的公主」懸念"),

        # ── 角色定位寫反 ────────────────────────────────────────────
        ("Michelangelo da Caravaggio",
         "Don Fernando embodies the forces that seek to restrain or exploit the artist, while",
         "Don Fernando, the Seville art dealer who recounts the painter’s story, frames the telling, while",
         "外部來源:Don Fernando 是塞維亞的藝術商人,把卡拉瓦喬的故事講給年輕畫家學徒聽——他是敘事者,不是壓迫者"),

        # ── 查無據的地名 ────────────────────────────────────────────
        ("Rebelové",
         "spend their days in the provincial town of Kostelec, impatient for romance",
         "spend their days in a small town near the border, impatient for romance",
         "hdk.cz 官方描述未提地點,2001 電影只說捷克邊境地區;Kostelec 查無據"),

        # ── Zlatovláska:四處編造(繁中版才是對的,以它的事實為準) ──
        ("Zlatovláska",
         "Kuchař Jiřík serves at the court of the vain and domineering Král Kazisvět.",
         "Kuchař Jiřík serves at the court of a vain and domineering king.",
         "hdk.cz 官方角色表只有「Otec Zlatovlásky」與「Zlý král」,兩位國王都沒有名字"),
        ("Zlatovláska",
         "When a mysterious fish arrives in the royal kitchen, the king tastes it and gains the ability to understand animals, then strictly forbids Jiřík to do the same.",
         "When a mysterious snake is brought to the royal kitchen, the king orders Jiřík to cook it and strictly forbids him to taste it.",
         "原著與官方都是蛇(had),不是魚;而且是國王命廚師煮蛇並禁止他嘗,國王沒有先吃"),
        ("Zlatovláska",
         "As punishment, Král Kazisvět orders him to travel to the distant realm of Král Mojmír and bring back the beautiful Zlatovláska",
         "As punishment, the king orders him to travel to a distant realm and bring back the beautiful Zlatovláska",
         "兩個國王名都是編的"),
        ("Zlatovláska",
         "the mission set by Král Kazisvět becomes a conflict between obedience and genuine love",
         "the mission becomes a conflict between obedience and genuine love",
         "同上"),
        ("Zlatovláska",
         "Jiřík returns with Zlatovláska, but Král Kazisvět refuses to accept that her heart belongs to the cook rather than to him.",
         "Jiřík returns with Zlatovláska, but the king refuses to accept that her heart belongs to the cook rather than to him.",
         "同上"),
        ("Zlatovláska",
         "Jiřík and Zlatovláska are united, while Král Kazisvět too is drawn toward reconciliation, ending in a second marriage with Babka.",
         "The king’s greed turns deadly, but the water of life undoes what his cruelty destroys, and Jiřík and Zlatovláska are united at last.",
         "「國王二婚」是編的;原著/1973 電影是國王誤用魔法水而死、Jiřík 成為國王娶了金髮公主,繁中版寫的「國王殘酷處置伊日克、金髮姑娘以神奇之水救回他」才對"),

        # ── 拼寫對齊原片/史實 ──────────────────────────────────────
        # ⚠ 原本這裡有一條 Macskafogó 規則(改拼寫 Poljakoff/Schwartz/Maxipocak、刪 Cicus)。
        #   §3 用真 Chrome 讀 1986 動畫官方角色表後確認:Poliakoff / Nero von Schwarz /
        #   Maxipotzac / Cicus 全部都是官方寫法,生成本來就是對的。該規則已刪除,
        #   避免任何人重跑 apply_fixes 又把正確內容改壞(回歸防護)。

        ("Nikola Tesla",
         "Nikola’s ideas find a more sympathetic champion in George Westinghause",
         "Nikola’s ideas find a more sympathetic champion in George Westinghouse",
         "拼寫:Westinghouse"),

        # ── De Spiekpietjes:官方專名寫法 + 誰發現儀表失控 ──────────
        ("De Spiekpietjes",
         "Sint makes one last inspection of his speelgoedfabriek before the Sinterklaasfeest, expecting the usual orderly flow of toys, packages and sweets. Instead, he discovers that the flinke-kindjes-meter is racing wildly upward.",
         "Inside Sint’s speelgoedfabriek the usual orderly flow of toys, packages and sweets is about to be thrown off course: the brave-kindjes-meter is racing wildly upward.",
         "官方寫的是「brave-kindjes-meter」（非 flinke-）；且官方是「Er ontstaat paniek wanneer **ze**（小精靈們）merken dat de brave-kindjes-meter op hol slaat」，沒有 Sint 巳巡工廠並發現這件事"),
        ("De Spiekpietjes",
         "Sint knows exactly whom to call: the Spiekpietjes. The small Sinterklaashulpjes",
         "It is the Spiekpietjes who walk straight into it. The small Sinterklaashulpjes",
         "同上：官方並無「Sint 召來小精靈」這條線，是他們第一次參觀工廠時正好撞上"),

        # ── 查無據的公司名 ──────────────────────────────────────────
        ("The Julekalender",
         "comes Benny, a stranger who knocks at Oluf and Gertrud’s door claiming to be a travelling salesman for Koch Sokker og Sko.",
         "comes Benny, a travelling salesman from Copenhagen who knocks at Oluf and Gertrud’s door, claiming his car has broken down and asking to stay the night.",
         "「Koch Sokker og Sko」找不到可靠來源（唯一提及的網頁留言自己也不確定拼 Cock 還是 Koch）；丹麥維基官方劇情寫 Benny 是「den københavnske handelsrejsende」，說詞是「hans bil er brudt sammen og spørger, om han kan overnatte」"),

        # ── 官方劇情沒有的情節 ──────────────────────────────────────
        ("Pippi på sirkus",
         " Behind the circus chaos, the Sirkusdirektøren’s poor ticket sales and hunger for money lead to a plan to take Pippi’s fortune, but the attempted escape is stopped before it can succeed.",
         "",
         "Det Norske Teatret 官方劇情沒有「團長貪圖 Pippi 金幣、企圖搶奪」這條線(那是原著裡小偷的情節)"),
    ],
    "out_zht.json": [
        ('VY NEJSTE',
         '企圖藉此替自己的「寬容聯盟」搏取聲量',
         '企圖藉此替自己以寬容為名的政治主張搏取聲量',
         '【WATCH 結案】divadlorb.cz 官方角色表(展開後取得,這正是先前缺的那份 source):**Milan Kokeš / Libor Náramný / Žalobce / Obhájkyně / Soudkyně / Přísedící / Novinářka** —— 全是當事人與法庭角色,**沒有任何名為「Liga tolerance / 寬容聯盟」的組織**;全頁搜尋 Liga、toleranc 皆 0 命中。英文版當時據此刪除該組織名是正確的(不是誤修);繁中版的「寬容聯盟」是我先前漏抓,一併改掉。'),
        ('The Julekalender',
         '某日，自稱推銷鞋襪的陌生人班尼上門，先以車子沒油、爆胎等藉口博取同情，後來竟賴在農場不走。',
         '某日，哥本哈根來的旅行推銷員班尼上門，說自己車子拋錨、想借宿一晚，後來竟一天拖過一天賴在農場不走。',
         '重生成後的查證:官方(da.wikipedia Handling)寫「den københavnske **handelsrejsende** Benny, som **påstår at hans bil er brudt sammen** og spørger, **om han kan overnatte**」——只說他是哥本哈根來的旅行推銷員、藉口車子拋錨要借宿;**沒有說他賣鞋襪**,也沒有「沒油/爆胎」。(英文版先前同一處寫的公司名「Koch Sokker og Sko」也是查無據而刪掉的。)'),
        ('De Spiekpietjes',
         '聖誕老人走進玩具與糖果工廠，準備在節日前做最後巡視，卻發現「乖孩子計量表」瘋狂震動、一路飆升。',
         '聖誕老人的玩具與糖果工廠裡，「乖孩子計量表」正瘋狂震動、一路飆升。',
         '與英文版同一處:官方(capitole-gent.be)寫「De spiekpietjes krijgen hun eerste rondleiding… Er ontstaat paniek wanneer **ze**(小精靈們)**merken dat de brave-kindjes-meter van Sinterklaas op hol slaat**」——是**小精靈們參觀時發現**儀表失控,官方並無「Sint 做最後巡視並發現」「Sint 召來小精靈」這條線。英文版 §3 已修同樣兩處。'),
        ('De Spiekpietjes',
         '聖誕老人知道，只有這群最懂得觀察孩子、也最會想鬼點子的助手，或許能找出讓計量表冷靜下來的辦法。',
         '而能想出辦法讓計量表冷靜下來的，正是這群最懂得觀察孩子、也最會想鬼點子的助手。',
         '與英文版同一處:官方(capitole-gent.be)寫「De spiekpietjes krijgen hun eerste rondleiding… Er ontstaat paniek wanneer **ze**(小精靈們)**merken dat de brave-kindjes-meter van Sinterklaas op hol slaat**」——是**小精靈們參觀時發現**儀表失控,官方並無「Sint 做最後巡視並發現」「Sint 召來小精靈」這條線。英文版 §3 已修同樣兩處。'),
        ('Pippi på sirkus',
         '她先誤闖馴馬表演，以怪異卻俐落的騎術贏得滿堂彩；接著又自告奮勇與大力士較量。',
         '她先闖進馬戲公主卡門西塔的表演，又盯著走鋼索的艾薇拉在高處翻飛；接著自告奮勇，要和號稱世界最強壯的男人強壯阿道夫較量。',
         'Det Norske Teatret 官方全文只列出:Pippi、**Tommy og Annika**、**sirkusprinsessa Miss Carmencita**、**linedansaren Elvira**、**ein illsint sirkusdirektør**、**Sterke Adolf**。全頁搜尋 **Kling / Klang / politi / hest / ridning 皆 0 命中** —— 警察 Kling och Klang 是《長襪皮皮》原著/其他劇目的角色,本製作沒有;馴馬與騎術橋段官方亦無。英文版與簡中版都沒寫這兩項,只有繁中寫了。(先前我也曾在這一部刪掉官方沒有的「團長貪圖皮皮金幣」情節。)'),
        ('Pippi på sirkus',
         '脾氣不佳的團長眼看演出節奏被打亂，既憤怒又無可奈何；警察克林與克朗也想把皮皮拉回秩序裡，卻總被她天真直接的邏輯弄得手忙腳亂。',
         '脾氣不佳的團長眼看演出節奏被打亂，既憤怒又無可奈何，想把皮皮拉回秩序裡，卻總被她天真直接的邏輯弄得手忙腳亂。',
         'Det Norske Teatret 官方全文只列出:Pippi、**Tommy og Annika**、**sirkusprinsessa Miss Carmencita**、**linedansaren Elvira**、**ein illsint sirkusdirektør**、**Sterke Adolf**。全頁搜尋 **Kling / Klang / politi / hest / ridning 皆 0 命中** —— 警察 Kling och Klang 是《長襪皮皮》原著/其他劇目的角色,本製作沒有;馴馬與騎術橋段官方亦無。英文版與簡中版都沒寫這兩項,只有繁中寫了。(先前我也曾在這一部刪掉官方沒有的「團長貪圖皮皮金幣」情節。)'),
        ('Änglagård',
         '芬妮．桑德與她風采張揚的摯友札克，從柏林夜生活回到西約塔蘭森林深處的伊克薩雷德村。父親猝逝後，芬妮前來繼承名為「天使莊園」的農地，也想尋找自己從未真正認識的家族根源；',
         '芬妮．贊德與她風采張揚的摯友札克，從柏林夜生活回到西約塔蘭森林深處的伊克薩雷德村。獨居的祖父艾瑞克．贊德猝逝後，芬妮以唯一繼承人的身分前來接手名為「天使莊園」的農地，也想查清自己從未見過的生父究竟是誰；',
         '§3 已查:Det Norske Teatret 官方寫「Ho er det **ukjente barnebarnet til den avdøde einstøingen Erik**, og arvingen til herregarden Änglagård」(她是已故獨居者 **Erik** 不為人知的**孫女**、莊園繼承人)、「Kvifor drog mora til Fanny så brått frå byen og **kven er eigentleg faren hennar**?」;sv.wikipedia 音樂劇條目與 Oscarsteatern 角色表皆作 **Fanny Zander**、**Erik Zander**。繁中把姓氏寫成「桑德」(Sand 是另一部戲 The Julekalender 的姓),又把**祖父**寫成父親;簡中版兩處都寫對。'),
        ('Elvált nők klubja',
         '安妮長年在婚姻中壓抑自己，面對丈夫比爾的冷漠與新戀情，幾乎失去說出心聲的勇氣',
         '安妮長年在婚姻中壓抑自己，面對丈夫亞倫的冷漠與新戀情，幾乎失去說出心聲的勇氣',
         'jegy.hu 官方角色表逐行寫明:「**AARON (Annie férje)**」「**MORTY (Brenda férje)**」「**BILL (Elise férje)**」——**Bill 是 Elise 的丈夫**,Annie 的丈夫是 **Aaron**。繁中把 Bill 安給了 Annie。(另有 CASSANDRA-SHELLY-PSZICHOLÓGUS、DWAYNE 兩個角色。)'),
        ('Hogyan tudnék élni nélküled',
         '四年前痛失未婚夫的她始終無法走出悲傷，於是和手足循著字跡，讀進一段發生在1994年巴拉頓湖畔的夏日往事。',
         '獨自生活的她總告訴自己這樣也好，於是和手足循著字跡，讀進一段發生在九○年代初、巴拉頓湖畔的夏日往事。',
         '與英文版同一處錯:官方/電影寫 Lili 是「**magányos**(孤獨),igyekszik bebeszélni magának, hogy így jó neki」,沒有「未婚夫過世」這件事;英文版 §3 已據此修正,中文兩版沿用了同一個杜撰設定。官方時間寫「**90-es évek**」/「**kilencvenes évek elejének** egy felejthetetlen nyara」,並無 1994 這個年份。'),
        ('Hogyan tudnék élni nélküled',
         '葛爾戈和鼓手加博、鍵盤手查比組成樂團，在西格利蓋特海灘演出；',
         '葛爾戈和鼓手加博、鍵盤手查比組成樂團，在湖畔的沙灘上演出；',
         '與英文版同一處錯:**Szigliget** 這個演出地點在 jegy.hu 官方文案、erkelszinhaz.hu、port.hu 三個來源皆查無,英文版 §3 已刪除地名,中文兩版同樣要刪。(樂團名 Kuplung 有據,保留。)'),
        ('Snowboar',
         '旅館裡還住著露西、克拉拉與泰瑞莎三名女孩，立刻讓兩個菜鳥把「練會滑雪」與「贏得芳心」列為同等重要的目標。',
         '旅館裡還住著漂亮的露茜卡，立刻讓兩個菜鳥把「練會滑雪」與「贏得芳心」列為同等重要的目標。',
         '本舞台製作(Divadlo Radka Brzobohatého)官方角色表為:Rendy / Jáchym / **Lucka** / Marta / Panter / Nymfomanka / Milan / Pes / Sněhulák / Kluk / Dívka / Dívka 2 —— **沒有 Klára、Tereza**;官方簡介也只寫「bojují o své místo na slunci, na svahu a **v srdci krásné Lucky**」。電影版才有 Tereza(Barbora Seidlová)、Klára(Lucie Vondráčková)、Lucie(Martina Klírová)三個女孩,舞台版把她們併成 Lucka 一人。'),
        ('Močál Story',
         '森林步道上，一群同學結伴出遊，卻發現同伴達莎．諾瓦可娃突然失去蹤影；原本尋常的郊遊，轉眼成了通往沼澤的荒唐搜索。慌亂的史塔妮亞一面擔心朋友安危，一面與眾人設法回想達莎最後出現的地方，警方也派出警探雅羅斯拉夫．班布拉與菜鳥警員維納「藍波」多皮爾前來辦案。',
         '同學達莎．諾瓦可娃與史塔妮亞．波拉可娃已經好一陣子聯絡不上好友布拉熱娜．普羅哈茲科娃；她們在林子裡撿到她掉落的隨身物品，認定她有危險，原本尋常的林間路程轉眼成了通往沼澤的荒唐搜索。警方派出警探雅羅斯拉夫．班布拉與菜鳥警員維納「藍波」多皮爾前來辦案。',
         '劇評(ocima7.cz,Hudební divadlo Karlín 製作)原文:「Spolužačky **Dáša Nováková a Stáňa Poláková** již delší dobu **postrádají svoji kamarádku Bláža Procházkovou**. **V lese najdou některé její věci** a usoudí proto, že je Bláža v nebezpečí a za pomoci dvou svérázných policistů po ztracené kamarádce pátrají.」——失蹤的是 **Blažena Procházková**;Dáša 與 Stáňa 是尋人的兩個同學。繁中把尋人者寫成了失蹤者(簡中版寫對了)。MUNI 的報導標題也直接寫「hledání Bláži」。'),
        ('Močál Story',
         '達莎的失蹤讓所有角色被迫跨出原有生活範圍',
         '布拉熱娜的失蹤讓所有角色被迫跨出原有生活範圍',
         '劇評(ocima7.cz,Hudební divadlo Karlín 製作)原文:「Spolužačky **Dáša Nováková a Stáňa Poláková** již delší dobu **postrádají svoji kamarádku Bláža Procházkovou**. **V lese najdou některé její věci** a usoudí proto, že je Bláža v nebezpečí a za pomoci dvou svérázných policistů po ztracené kamarádce pátrají.」——失蹤的是 **Blažena Procházková**;Dáša 與 Stáňa 是尋人的兩個同學。繁中把尋人者寫成了失蹤者(簡中版寫對了)。MUNI 的報導標題也直接寫「hledání Bláži」。'),
        ('Zlatovláska',
         '城堡廚師伊日克違抗國王卡齊斯維特的禁令',
         '城堡廚師伊日克違抗國王的禁令',
         'hdk.cz 官方角色表只有「Otec Zlatovlásky」與「Zlý král」——**兩位國王都沒有名字**;「Kazisvět」「Mojmír」是編造的,英文版當時已據此刪除,繁中同樣要刪。'),
        ('Zlatovláska',
         '來到金髮公主父王莫伊米爾的宮廷後',
         '來到金髮公主父王的宮廷後',
         'hdk.cz 官方角色表只有「Otec Zlatovlásky」與「Zlý král」——**兩位國王都沒有名字**;「Kazisvět」「Mojmír」是編造的,英文版當時已據此刪除,繁中同樣要刪。'),
        ('Zlatovláska',
         '尋回海中的戒指、辨認細小的珍珠，並完成國王提出的難題。',
         '在草叢裡找回失落的珍珠、從湖底撈起金戒指，並取來生死之水。',
         'cs.wiki《Zlatovláska (film, 1973)》Děj 原文(本製作官方自述為該片音樂童話的新製作):「Nejprve musí **v trávě najít ztracené perly**」(先在**草叢**中找回失落的珍珠)、「Za druhé musí **ze dna jezera vylovit zlatý prsten**」(再從**湖底**撈出金戒指)、「Nakonec musí přinést **živou a mrtvou vodu**」(最後取來生死水),另有「moucha mu pomůže vybrat tu pravou dívku」(蒼蠅幫他認出正確的姑娘)。戒指在湖底不在海中;珍珠是在草叢裡找回,不是「從灰燼中分揀種子」(那是灰姑娘的考驗)。'),
        ('Zlatovláska',
         '然而，卡齊斯維特真正想得到的是公主本人',
         '然而，國王真正想得到的是公主本人',
         'hdk.cz 官方角色表只有「Otec Zlatovlásky」與「Zlý král」——**兩位國王都沒有名字**;「Kazisvět」「Mojmír」是編造的,英文版當時已據此刪除,繁中同樣要刪。'),
        ('Il ragazzo dai pantaloni rosa',
         '安德烈亞在校園裡穿上自己喜歡的粉紅色長褲，原想用一點勇氣展現真實的模樣，卻立刻成為同學注目的焦點。',
         '安德烈亞收到一條紅色長褲，洗過之後褪成了粉紅；他仍決定穿去學校，原想用一點勇氣坦然保留自己的顏色，卻立刻成為同學注目的焦點。',
         '這是本案的核心細節:那條褲子不是他挑的粉紅褲,而是**紅褲子洗過之後褪成粉色**,他仍決定穿去學校。Teatro Sistina 官方明載舞台版取材自 Andrea Spezzacatena 真實事件與其母 Teresa Manes 的書,劇評並載「trama in linea con il film」;英文版與簡中版都寫對(red trousers that turn pink in the wash / 红裤子,洗涤后褪成粉色),只有繁中寫成「穿上自己喜歡的粉紅色長褲」,把被迫承受的標記寫成了自主選擇。'),
        ('Michelangelo da Caravaggio',
         '年邁畫家唐．費南多翻開記憶，將眾人帶回1599年的羅馬。',
         '藝術商人唐．費南多翻開記憶，將眾人帶回十七世紀的羅馬。',
         "goldenticketcompany.it 官方與 lavocediasti 報導:「Fabrizio Rizzolo interpreta don Fernando, **mercante d'arte di Siviglia** che apre e chiude il racconto」——他是塞維亞的藝術商人兼敘事者,不是畫家,也未提年邁。官方簡介另寫「sfida la Roma Papalina **del '600**」(十七世紀),中文的「1599年」查無據且與官方所寫的世紀不符。"),
        ('Aggiungi un posto',
         '另一方面，克蕾曼蒂娜仍執著於西爾維斯特，但神父只能克制情感、守住信仰與職責。',
         '另一方面，克蕾曼蒂娜終於向西爾維斯特表白；神父先以神職的獨身戒律推辭，最後仍吻了她——連上帝也表明不贊成獨身，說洪水過後兩人便能在一起。',
         '官方劇情相反:Clementina 終於表白後,don Silvestro 先以神職獨身制推辭,最後仍吻了她(「Silvestro bacia Clementina」);他再去面對上帝時「scopre che anche Lui è contrario al celibato」,並得知「Dopo il diluvio le cose cambieranno e don Silvestro potrà stare con Clementina」。原句「只能克制情感、守住信仰與職責」把結論寫反了。'),
        ('Aggiungi un posto',
         '上帝因此看見他不願獨自得救的愛，停止洪水，讓彩虹重現。',
         '上帝因此看見他不願獨自得救的愛，讓大雨停歇。',
         '官方結局沒有彩虹:「il Signore decide di far cessare la pioggia… tutti siedono a tavola a brindare. È per lui che è stato aggiunto un posto a tavola nel quale arriva in volo una colomba bianca」——是一隻白鴿飛落在那多留的位子上。彩虹是諾亞方舟的聖經聯想,非本劇。'),
        ('Aggiungi un posto',
         '最後，村民圍坐在長桌旁共享盛宴。',
         '最後，村民圍坐在長桌旁舉杯；那多留出來的一個位子上，飛落一隻白鴿。',
         '官方結局沒有彩虹:「il Signore decide di far cessare la pioggia… tutti siedono a tavola a brindare. È per lui che è stato aggiunto un posto a tavola nel quale arriva in volo una colomba bianca」——是一隻白鴿飛落在那多留的位子上。彩虹是諾亞方舟的聖經聯想,非本劇。'),
        ('Forza Venite Gente',
         '但貝爾納多、吉拉多等人逐漸被他的坦率與熱情感動',
         '但仍有人逐漸被他的坦率與熱情感動',
         '義大利維基與 Cathopedia 兩份角色表、以及完整 23 場歌單(Forza venite gente→Laudato sii)都沒有「貝爾納多」「吉拉多」這兩個角色;劇中同伴一律以 nuovi confratelli / primi compagni 泛稱,唯一有名字的弟兄是 Frate Leone。「Bernardo」在資料中只出現在父親全名 Pietro di Bernardone 裡。'),
        ('Forza Venite Gente',
         '他赤腳行走於鄉野與城鎮，照料痲瘋病人，親近窮人，',
         '他赤腳行走於鄉野與城鎮，親近窮人，',
         '本劇 23 場逐場歌單中沒有痲瘋病人場景(lebbrosi 在兩份資料全頁皆不出現);官方對這段只寫「servizio dei più poveri」(服事最窮的人),繁中原句已有「親近窮人」,「照料痲瘋病人」是本劇沒有的具體化。'),
        ("C'era una volta",
         '人稱「俄羅斯人」——',
         "人稱「'o russo」(那不勒斯話的「紅髮」)——",
         "官方角色表寫「Raffaele 'o russo」;那不勒斯方言 russo = 義大利語 rosso(紅髮),不是「俄羅斯人」(義語 russo 的字面義)。角色是那不勒斯人 Raffaele Capasso,譯「俄羅斯人」是把方言按標準義大利語誤讀。改為保留官方原文並註明方言含義。"),
        ("C'era una volta",
         '「俄羅斯人」則成了黑手黨頭目',
         "「'o russo」則成了卡莫拉黑幫的頭目",
         "官方角色表寫「Raffaele 'o russo」;那不勒斯方言 russo = 義大利語 rosso(紅髮),不是「俄羅斯人」(義語 russo 的字面義)。角色是那不勒斯人 Raffaele Capasso,譯「俄羅斯人」是把方言按標準義大利語誤讀。改為保留官方原文並註明方言含義。 / 官方寫「boss camorrista」/「ribellarsi alla camorra」:卡莫拉是那不勒斯的犯罪組織,與西西里的 Mafia(黑手黨)是不同組織,不可混稱。"),
        ("C'era una volta",
         '「俄羅斯人」的怒火與嫉妒',
         "「'o russo」的怒火與嫉妒",
         "官方角色表寫「Raffaele 'o russo」;那不勒斯方言 russo = 義大利語 rosso(紅髮),不是「俄羅斯人」(義語 russo 的字面義)。角色是那不勒斯人 Raffaele Capasso,譯「俄羅斯人」是把方言按標準義大利語誤讀。改為保留官方原文並註明方言含義。"),
        ("C'era una volta",
         '呼喊反抗黑手黨，',
         '呼喊反抗卡莫拉，',
         '官方寫「boss camorrista」/「ribellarsi alla camorra」:卡莫拉是那不勒斯的犯罪組織,與西西里的 Mafia(黑手黨)是不同組織,不可混稱。'),
    ],
    "out_zhs.json": [
        ('Anděl Páně',
         '也使宫廷阴谋愈发失控',
         '也使府邸里的算计愈发失控',
         '同一部第二處(回歸掃描抓到我漏改的):官方角色表 Petronel / Uriáš / Dorotka / Hrabě / Správce / Klíčnice / Panna Marie / Ježíšek —— **沒有國王,也沒有宮廷**,場景是伯爵的府邸。'),
        ('Anděl Páně',
         '多萝塔对亲情与真爱的坚持，国王在危难中的良知',
         '多萝塔对亲情与真爱的坚持，众人在危难中重新浮现的良知',
         '同一部第二處(回歸掃描抓到我漏改的):官方角色表 Petronel / Uriáš / Dorotka / Hrabě / Správce / Klíčnice / Panna Marie / Ježíšek —— **沒有國王,也沒有宮廷**,場景是伯爵的府邸。'),
        ('VY NEJSTE',
         '律师借机为“宽容联盟”造势',
         '律师借机为自己以宽容为名的政治主张造势',
         '【WATCH 已結案】divadlorb.cz 官方角色表:Milan Kokeš / Libor Náramný / Žalobce / Obhájkyně / Soudkyně / Přísedící / Novinářka —— 全是當事人與法庭角色,**沒有名為「Liga tolerance / 寬容聯盟」的組織**;全頁 Liga、toleranc 皆 0 命中。英文版與繁中版同一處已改,簡中重生成後又出現,一併改掉。'),
        ('VY NEJSTE',
         '后来，“宽容联盟”甚至赢得选举',
         '后来，这股打着宽容旗号的势力甚至赢得选举',
         '【WATCH 已結案】divadlorb.cz 官方角色表:Milan Kokeš / Libor Náramný / Žalobce / Obhájkyně / Soudkyně / Přísedící / Novinářka —— 全是當事人與法庭角色,**沒有名為「Liga tolerance / 寬容聯盟」的組織**;全頁 Liga、toleranc 皆 0 命中。英文版與繁中版同一處已改,簡中重生成後又出現,一併改掉。'),
        ('Anděl Páně',
         '两人来到尘世的王国，卷入王宫与民间的纷乱。年轻伯爵娘多萝塔善良勇敢，却遭继母和姐姐们轻视；虚荣的国王沉迷奢华，又被野心勃勃的大臣玩弄。',
         '两人来到人间，卷入伯爵府邸里的纷乱：彼得罗内尔遇见善良勇敢的多萝塔，也遇上精于算计的管家与女管家。',
         '官方角色表為 Petronel / Uriáš / Dorotka / **Hrabě**(伯爵)/ **Správce**(管家)/ **Klíčnice**(女管家)/ Panna Marie / Ježíšek —— **沒有國王、沒有大臣**,Dorotka 也不是伯爵夫人;「繼母和姐姐們」是灰姑娘的設定,本劇沒有。改為只用官方角色表確有的角色,且不斷言彼此關係。'),
        ('De Spiekpietjes',
         '圣诞老人走进玩具和糖果工厂作最后巡查时，负责统计乖孩子数量的“乖孩子仪”忽然疯狂飙升。',
         '圣诞老人的玩具和糖果工厂里，负责统计乖孩子数量的“乖孩子仪”忽然疯狂飙升。',
         '與英文版同一處:官方(capitole-gent.be)寫「De spiekpietjes krijgen hun eerste rondleiding… Er ontstaat paniek wanneer **ze**(小精靈們)**merken dat de brave-kindjes-meter van Sinterklaas op hol slaat**」——是**小精靈們參觀時發現**儀表失控,官方並無「Sint 做最後巡視並發現」「Sint 召來小精靈」這條線。英文版 §3 已修同樣兩處。'),
        ('De Spiekpietjes',
         '圣诞老人把希望寄托在这些善于观察孩子、收集愿望清单的小帮手身上：必须在机器彻底失控前，找出让数字降下来的办法。',
         '必须在机器彻底失控前找出让数字降下来的办法的，正是这些善于观察孩子、收集愿望清单的小帮手。',
         '與英文版同一處:官方(capitole-gent.be)寫「De spiekpietjes krijgen hun eerste rondleiding… Er ontstaat paniek wanneer **ze**(小精靈們)**merken dat de brave-kindjes-meter van Sinterklaas op hol slaat**」——是**小精靈們參觀時發現**儀表失控,官方並無「Sint 做最後巡視並發現」「Sint 召來小精靈」這條線。英文版 §3 已修同樣兩處。'),
        ('Emil i Lönneberga',
         '农庄里的女佣阿尔弗雷德和林娜，则在忙碌生活中见证这家人的争吵、欢笑与温情。',
         '农庄里的长工阿尔弗雷德和女佣林娜，则在忙碌生活中见证这家人的争吵、欢笑与温情。',
         '§3 已查:官方售票頁「Du får møte Emil, Ida, **Alfred**, Lina…」;sv.wikipedia:「**drängen Alfred** och **pigan Lina**」——**Alfred 是男性長工(dräng)**,Lina 才是女僕(piga);維基並明寫「Pappa Anton… **är inte Emils manlige förebild, utan det är drängen Alfred**」。簡中把 Alfred 寫成「女佣」。繁中版寫「長工阿爾弗雷德和女傭莉娜」是對的。'),
        ('Ronja Rövardotter',
         '可在冒险中，比克救下困在地洞边的罗妮娅，罗妮娅也在危急时刻回报了他。',
         '两人隔着地狱谷比赛跳跃，比克失足坠落，是罗妮娅救下了他；后来她的脚卡进屁股精的洞口时，比克也两度救她于危难。',
         'sv.wikipedia《Ronja rövardotter》:「När Birk och Ronja möts första gången utmanar de varandra genom att hoppa över Helvetesgapet tills **Birk ramlar och Ronja räddar honom**」——**第一次相遇是 Birk 失足、Ronja 救他**;「Birk räddar senare Ronja till livet **två gånger**」(Birk 是後來才兩度救她,其中一次正是她腳卡進 rumpnissehåla 時)。簡中把首次相遇的救援方向寫反了。'),
        ('Metro',
         '在华沙熙攘的街头，一群年轻人结束白天的奔波，走入地铁隧道深处的废弃站台，把那里当作属于自己的舞台。来自小城的雅努什怀抱歌手梦想，偶然加入这支地下表演团体；他结识了率性、敏感的安卡，并迅速被她吸引。',
         '一群怀抱明星梦的年轻人走进剧院试镜，却被主持试镜的导演菲利普拒于门外。他们没有就此散去，而是转到剧院附近的地铁站台，把那里当作属于自己的舞台。带头的是把地铁当作第二个家的扬；他结识了率性、敏感的安卡，并迅速被她吸引。',
         'Studio Buffo(製作方)官方角色表為 **Anka / Jan / Filip / Max**;pl.wikipedia 劇情:「grupy nastoletnich aktorów amatorów, **pod wodzą Jana** – zbuntowanego, niezależnego artysty, **dla którego metro jest drugim domem**. Młodzi aktorzy **zostają odrzuceni przez Filipa, reżysera prowadzącego casting**… Postanawiają więc rozpocząć występy na **położonej nieopodal teatru stacji metra**.」——主角是 **Jan**(揚),他是**帶頭人**、地鐵是他的第二個家;「Janusz」是作曲家 Janusz Stokłosa 與導演 Janusz Józefowicz 的名字,不是角色。起點是**被試鏡導演 Filip 拒絕**,演出地是**劇院附近的地鐵站**,不是廢棄站台。繁中版全部寫對。'),
        ('Metro',
         '雅努什逐渐成为团体中最受瞩目的声音',
         '扬逐渐成为团体中最受瞩目的声音',
         'Studio Buffo(製作方)官方角色表為 **Anka / Jan / Filip / Max**;pl.wikipedia 劇情:「grupy nastoletnich aktorów amatorów, **pod wodzą Jana** – zbuntowanego, niezależnego artysty, **dla którego metro jest drugim domem**. Młodzi aktorzy **zostają odrzuceni przez Filipa, reżysera prowadzącego casting**… Postanawiają więc rozpocząć występy na **położonej nieopodal teatru stacji metra**.」——主角是 **Jan**(揚),他是**帶頭人**、地鐵是他的第二個家;「Janusz」是作曲家 Janusz Stokłosa 與導演 Janusz Józefowicz 的名字,不是角色。起點是**被試鏡導演 Filip 拒絕**,演出地是**劇院附近的地鐵站**,不是廢棄站台。繁中版全部寫對。'),
        ('Metro',
         '雅努什在成功机会与安卡、伙伴之间摇摆',
         '扬在成功机会与安卡、伙伴之间摇摆',
         'Studio Buffo(製作方)官方角色表為 **Anka / Jan / Filip / Max**;pl.wikipedia 劇情:「grupy nastoletnich aktorów amatorów, **pod wodzą Jana** – zbuntowanego, niezależnego artysty, **dla którego metro jest drugim domem**. Młodzi aktorzy **zostają odrzuceni przez Filipa, reżysera prowadzącego casting**… Postanawiają więc rozpocząć występy na **położonej nieopodal teatru stacji metra**.」——主角是 **Jan**(揚),他是**帶頭人**、地鐵是他的第二個家;「Janusz」是作曲家 Janusz Stokłosa 與導演 Janusz Józefowicz 的名字,不是角色。起點是**被試鏡導演 Filip 拒絕**,演出地是**劇院附近的地鐵站**,不是廢棄站台。繁中版全部寫對。'),
        ('Hogyan tudnék élni nélküled',
         '未婚夫去世四年后，她始终困在悲伤里，歌唱事业也难以起步；',
         '独自生活的她总告诉自己这样也好，歌唱事业也难以起步；',
         '與英文版同一處錯:官方/電影寫 Lili 是「**magányos**(孤獨),igyekszik bebeszélni magának, hogy így jó neki」,沒有「未婚夫過世」這件事;英文版 §3 已據此修正,中文兩版沿用了同一個杜撰設定。官方時間寫「**90-es évek**」/「**kilencvenes évek elejének** egy felejthetetlen nyara」,並無 1994 這個年份。'),
        ('Hogyan tudnék élni nélküled',
         '夜晚在锡格利盖特海滩演出。',
         '夜晚在湖畔的沙滩上演出。',
         '與英文版同一處錯:**Szigliget** 這個演出地點在 jegy.hu 官方文案、erkelszinhaz.hu、port.hu 三個來源皆查無,英文版 §3 已刪除地名,中文兩版同樣要刪。(樂團名 Kuplung 有據,保留。)'),
        ('Légy jó mindhalálig',
         '善良敏感的孤儿尼拉伊·米希被送来求学。他出身贫寒，却珍惜来之不易的机会',
         '善良敏感的尼拉伊·米希离开父母，被送来求学。他出身贫寒，却珍惜来之不易的机会',
         'Misi **不是孤兒**:官方(hu.wikipedia 原著 Történet)寫「a szobatársai felbontják az **otthonról kapott** pakk-ját」(同學拆了他**從家裡**收到的包裹),結局「**nem akar többé debreceni diák lenni**」是要回家;英文版與繁中版都寫他離開父母來寄宿,只有簡中把他寫成孤兒。'),
        ('Snowboar',
         '雅希姆还被迫带上令他头疼的姐姐露茜卡',
         '雅希姆还被迫带上令他头疼的妹妹玛尔塔',
         'cs.wikipedia《Snowboarďáci》Děj:「**Jáchym s sebou musí vzít svou otravnou sestru**」,卡司表為 Ester Geislerová **Marta** —— 被迫帶上的是**妹妹 Marta**;**Lucka 是兩人爭取的女孩**(官方:「v srdci krásné Lucky」),不是姐姐。同段的「naštvou **sestru**」(惹怒妹妹)簡中也誤植成惹怒 Lucka。繁中版寫「妹妹瑪塔」是對的。'),
        ('Snowboar',
         '弄丢表哥的狗、损坏汽车、惹怒露茜卡，甚至跌入冰冷河水',
         '弄丢表哥的狗、损坏汽车、惹怒妹妹，甚至跌入冰冷河水',
         'cs.wikipedia《Snowboarďáci》Děj:「**Jáchym s sebou musí vzít svou otravnou sestru**」,卡司表為 Ester Geislerová **Marta** —— 被迫帶上的是**妹妹 Marta**;**Lucka 是兩人爭取的女孩**(官方:「v srdci krásné Lucky」),不是姐姐。同段的「naštvou **sestru**」(惹怒妹妹)簡中也誤植成惹怒 Lucka。繁中版寫「妹妹瑪塔」是對的。'),
        ('A dzsungel könyve',
         '也遭到猴群首领路易的掳走。路易渴望掌握人类的“红花”——火，企图借此获得绝对力量；毛克利则在危机中逐渐明白',
         '也被猴群掳走、被它们推举为首领，随即又遭反噬；卡阿催眠了猴群，几乎连他一起吞下，幸有巴鲁与巴希拉赶到。年迈的阿克拉在谢尔·汗设下的试炼中失利后，巴希拉派他去人类村落取来“红花”——火，他举着火把回来救下阿克拉、赶走谢尔·汗。毛克利则在危机中逐渐明白',
         '本劇(Dés–Geszti–Békés 匈牙利版)官方 hu.wikipedia 兩幕劇情**沒有名叫「路易」的猴王**——「路易王(King Louie)」是**迪士尼 1967 動畫的原創角色**,吉卜林原著與本劇皆無。官方寫的是:猴子擄走 Maugli 並推他為首領、之後反過來對付他;Ká 催眠猴群、差點吃掉他,被 Balu 與 Bagira 阻止。「紅花(火)」也不是猴王的野心,官方是**年老的 Akela 在 Sir Kán 設下的試煉中失敗後,Bagira 派 Maugli 去人類村子取紅花**,Maugli 帶火把回來救下 Akela、趕走 Sir Kán。'),
        ('A dzsungel könyve',
         '少女梅苏亚让他第一次感受到另一种亲近与归属',
         '村长布尔迪奥的女人图娜开始教他说话，让他第一次感受到另一种亲近与归属',
         '官方劇情中,人類村落裡教 Maugli 說話的是**村長 Buldeó 的女人 Túna**(第二幕:村裡只有女人在家,Túna 開始教他說話);結局 Maugli 用 Sir Kán 的皮把 Túna 從 Buldeó 手中贖回來,Túna 向他發誓忠誠。「Messua(梅蘇亞)」是吉卜林**原著小說**裡的名字,不是本劇角色。繁中版寫「圖娜」是對的。'),
        ('Kapka medu pro Verunku',
         '三位王子都到了成婚的年纪，偏偏美丽善良的维鲁娜公主只有一位',
         '两位王子都到了成婚的年纪，偏偏美丽善良的维鲁娜公主只有一位',
         '製作方官方頁 pixapro.cz 的角色列為「**Princ Honza / Princ Mirek / Myslivec Jirka**」,musical.cz 亦寫「Na cestu se vydali **tři hrdinové – myslivec Jirka a princové Honza a Mirek**」——出發的三人是**兩位王子(Honza、Mirek)加一位獵人 Jirka**,不是三位王子。(三個王國為 Zlatovláskov / Popelkov / Honzovsko,繁中版寫對了。)'),
        ('Kapka medu pro Verunku',
         '三名性格各异的王子被迫踏上充满障碍、诱惑与任务的旅程',
         '两位王子与猎人伊日卡被迫踏上充满障碍、诱惑与任务的旅程',
         '製作方官方頁 pixapro.cz 的角色列為「**Princ Honza / Princ Mirek / Myslivec Jirka**」,musical.cz 亦寫「Na cestu se vydali **tři hrdinové – myslivec Jirka a princové Honza a Mirek**」——出發的三人是**兩位王子(Honza、Mirek)加一位獵人 Jirka**,不是三位王子。(三個王國為 Zlatovláskov / Popelkov / Honzovsko,繁中版寫對了。)'),
        ('Rebelové',
         '他与鲍勃、埃曼、奥尔达三名逃离军营的年轻士兵同行，正设法搭车前往西方',
         '他和鲍勃、埃曼一样，是逃离军营的年轻士兵，三人正设法搭车前往西方',
         'cs.wikipedia《Rebelové》Děj 原文:「Film vypráví příběh **tří maturantek – Terezy, Bugyny, Julči**, a **tří vojáků, uprchlíků z armády, chystajících se emigrovat – Šimona, Boba a Emana**.」——逃離軍隊的三人是 **Šimon、Bob、Eman**;簡中把 Olda 也算成逃兵,且寫成「他與鮑勃、埃曼、奧爾達三名」=四個人,與官方的三人相矛盾。繁中把 Olda 寫成本地的追求者,與此不衝突。'),
        ('Zlatovláska',
         '从灰烬中分拣散落的种子、寻回遗失海中的戒指、辨认容貌相近的姐妹。',
         '在草丛里找回失落的珍珠、从湖底捞起金戒指、辨认容貌相近的姐妹。',
         'cs.wiki《Zlatovláska (film, 1973)》Děj 原文(本製作官方自述為該片音樂童話的新製作):「Nejprve musí **v trávě najít ztracené perly**」(先在**草叢**中找回失落的珍珠)、「Za druhé musí **ze dna jezera vylovit zlatý prsten**」(再從**湖底**撈出金戒指)、「Nakonec musí přinést **živou a mrtvou vodu**」(最後取來生死水),另有「moucha mu pomůže vybrat tu pravou dívku」(蒼蠅幫他認出正確的姑娘)。戒指在湖底不在海中;珍珠是在草叢裡找回,不是「從灰燼中分揀種子」(那是灰姑娘的考驗)。'),
        ('Saturnin',
         '萨图宁陪着年轻主人尤拉伊特登上',
         '萨图宁陪着年轻主人伊罗特卡登上',
         'Divadlo Hybernia 官方角色表(展開 TVŮRCI A OBSAZENÍ 後)為:Jirotka / Saturnin / Barbora / Tetička Kateřina / Dědeček / Doktor Vlach / Milouš。主人的角色名是 **Jirotka**,音譯應作「伊罗特卡」;「尤拉伊特」對不上任何官方角色名(繁中版寫「吉羅特卡」是對的)。'),
        ('Saturnin',
         '还一心想把害羞的侄女芭芭拉嫁给尤拉伊特；虚荣懒惰的米洛什则把这桩婚事视作攀附富亲戚的机会。',
         '一心要替儿子谋得好处；虚荣懒惰的米洛什也把开朗时髦的芭芭拉当成可以争取的对象。',
         '多來源(cs.wikipedia「Saturnin (román)」、postavy.cz、edufix、studentino)一致:**Slečna Barbora Terebová** 是獨立人物,「milá, **energická, moderní** žena, která umí dobře hrát tenis」,**不是 Kateřina 的侄女**,也沒有「姨媽要把她嫁給主人」這條線;「**Milouš – syn Kateřiny**」是姨媽的兒子,姨媽的算計是替兒子謀好處。此外 Barbora 官方形容是有活力、時髦,不是「害羞」。'),
        ('Saturnin',
         '同一阵线；尤拉伊特虽然屡屡措手不及',
         '同一阵线；伊罗特卡虽然屡屡措手不及',
         'Divadlo Hybernia 官方角色表(展開 TVŮRCI A OBSAZENÍ 後)為:Jirotka / Saturnin / Barbora / Tetička Kateřina / Dědeček / Doktor Vlach / Milouš。主人的角色名是 **Jirotka**,音譯應作「伊罗特卡」;「尤拉伊特」對不上任何官方角色名(繁中版寫「吉羅特卡」是對的)。'),
        ('Saturnin',
         '在萨图宁的推波助澜下，尤拉伊特和芭芭拉',
         '在萨图宁的推波助澜下，伊罗特卡和芭芭拉',
         'Divadlo Hybernia 官方角色表(展開 TVŮRCI A OBSAZENÍ 後)為:Jirotka / Saturnin / Barbora / Tetička Kateřina / Dědeček / Doktor Vlach / Milouš。主人的角色名是 **Jirotka**,音譯應作「伊罗特卡」;「尤拉伊特」對不上任何官方角色名(繁中版寫「吉羅特卡」是對的)。'),
        ('Peter Pan il Musical',
         '叮当及时阻止彼得饮下毒药，彼得与迷失男孩登上海盗船，展开决战，救回伙伴。',
         '叮当替彼得喝下那杯毒药，生命随之黯淡；彼得唤起众人相信仙子，才让她重新亮起。随后他与迷失男孩登上海盗船，展开决战，救回伙伴。',
         '官方兩幕 Trama(it.wikipedia.org/wiki/Peter_Pan,_il_musical)寫:虎克「sostituire la medicina per Peter… con un forte veleno」,而「**Trilli, che, per salvarlo beve la pozione fatale al posto suo**」——叮噹是**替他喝下**那杯致命藥水,不是阻止他喝;繁中與英文版都寫對,只有簡中寫成「及时阻止」,連帶漏掉全劇最著名的「我相信仙子」復活場面。'),
        ('Raffaella il Musical',
         '1951年的罗马，来自贝拉里亚的拉斐拉·佩洛尼',
         '罗马，来自贝拉里亚的拉斐拉·佩洛尼',
         '§3 已查:raffaellailmusical.com 官方站、teatrobrancaccio.it、完整 CASTING LIST 與導演專訪皆無「1951 年」這個年份,英文版當時已據此刪除;簡中同樣要刪(其餘專名 Pelloni/Bellaria/Iris/Nadia/Giovanni Salvi/Gianni Boncompagni/Alessandro 都與官方 CASTING LIST 相符,不動)。'),
        ('Michelangelo da Caravaggio',
         '年迈画家唐·费尔南多开启尘封往事，将人们带回1599年的罗马：',
         '艺术商人唐·费尔南多开启尘封往事，将人们带回十七世纪的罗马：',
         "goldenticketcompany.it 官方與 lavocediasti 報導:「Fabrizio Rizzolo interpreta don Fernando, **mercante d'arte di Siviglia** che apre e chiude il racconto」——他是塞維亞的藝術商人兼敘事者,不是畫家,也未提年邁。官方簡介另寫「sfida la Roma Papalina **del '600**」(十七世紀),中文的「1599年」查無據且與官方所寫的世紀不符。"),
        ("C'era una volta",
         '人称“俄罗斯人”——',
         "人称“'o russo”（那不勒斯话的“红发”）——",
         "官方角色表寫「Raffaele 'o russo」;那不勒斯方言 russo = 義大利語 rosso(紅髮),不是「俄羅斯人」(義語 russo 的字面義)。角色是那不勒斯人 Raffaele Capasso,譯「俄羅斯人」是把方言按標準義大利語誤讀。改為保留官方原文並註明方言含義。"),
        ("C'era una volta",
         '拉斐尔已成为黑手党头目',
         '拉斐尔已成为卡莫拉黑帮的头目',
         '官方寫「boss camorrista」/「ribellarsi alla camorra」:卡莫拉是那不勒斯的犯罪組織,與西西里的 Mafia(黑手黨)是不同組織,不可混稱。'),
        ("C'era una volta",
         '以歌声与呐喊反抗黑手党；',
         '以歌声与呐喊反抗卡莫拉；',
         '官方寫「boss camorrista」/「ribellarsi alla camorra」:卡莫拉是那不勒斯的犯罪組織,與西西里的 Mafia(黑手黨)是不同組織,不可混稱。'),
    ],
}


def main():
    check_only = "--check" in sys.argv
    rc = 0
    for fname, rules in RULES.items():
        path = os.path.join(HERE, fname)
        if not os.path.exists(path):
            print(f"[skip] {fname} 不存在")
            continue
        data = json.load(open(path, encoding="utf-8"))
        applied = missing = already = 0
        for prefix, old, new, why in rules:
            hits = [r for r in data if r["show"].startswith(prefix)]
            if not hits:
                print(f"  [!] {fname}: 找不到 show 前綴 {prefix!r}")
                missing += 1
                continue
            for r in hits:
                if old not in r["synopsis"]:
                    if (new and new in r["synopsis"]) or not new:
                        already += 1          # 先前已套用,不是錯誤
                        continue
                    print(f"  [!] {fname} / {prefix[:32]}: 原文匹配不到 → {old[:70]!r}")
                    missing += 1
                    continue
                if not check_only:
                    r["synopsis"] = r["synopsis"].replace(old, new)
                applied += 1
                print(f"  [ok] {prefix[:32]} — {why}")
        if not check_only and applied:
            json.dump(data, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        print(f"{fname}: 套用 {applied} / 先前已套用 {already} / 匹配不到 {missing}"
              + ("(--check,未寫檔)" if check_only else ""))
        if missing:
            rc = 1
    return rc


if __name__ == "__main__":
    sys.exit(main())
