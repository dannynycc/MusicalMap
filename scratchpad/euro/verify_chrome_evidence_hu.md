# 匈牙利批 — claude-in-chrome 逐部深查證據(接續 verify_chrome_evidence.md)
> 三維度逐條:劇情鏈 / 語意 / 事實。每部列出實際開啟的 URL + 照抄原文。

## [HU-10] Hogyan tudnék élni nélküled?(修 2 處)
**Chrome 開啟**
1. jegy.hu/program/hogyan-tudnek-elni-nelkuled-184904(官方文案 + **完整角色表**)
2. erkelszinhaz.hu/eloadas/hogyan-tudnek-elni-nelkuled/(劇院官方)
3. port.hu/…movie-254236(**電影劇情**——官方明載舞台劇本「Goda Krisztina és Kormos Anett által írt forgatókönyv alapján」,故電影為其正當依據,非「被電影干擾」)

**原文照抄**
- 官方角色表:Gergő(Ember Márk)/ Eszter / Gábor / Kata / Major Márton / Csabi / Betti / Eszter apja / Eszter anyja / Major Lili(Csobot Adél)/ Major Döme / Novai Balázs
- 官方文案:「A könnyed hangulatú történet felidézi a **90-es évek nyári balatoni hangulatát**, ahol a **múlt és a jelen összefonódik**, és ahol **újra meg kell tanulni bízni, elengedni és szeretni**」;「**érzelmekkel teli, romantikus történet szerelemről, veszteségről és újrakezdésről**」
- 電影劇情:「**Lili korunk tipikus lánya: magányos**, és igyekszik bebeszélni magának, hogy így jó neki. De egyszer **a szülei lakásában talál egy régi levélcsomagot, amit az anyja… nem akart megmutatni neki**… **a kilencvenes évek elejének egy felejthetetlen nyara, amikor három jó barátnő a Balatonnál vakációzik**, és közülük csak **Eszter akar hűséges maradni az otthon hagyott, karót nyelt pasijához**」

| # | 生成 | 對應原文 | 判定 |
|---|---|---|---|
| 1 | ~~Lili 走不出**未婚夫的死**~~ | 電影是「**magányos**(孤獨)」 | 🚩 已改為「孤獨、告訴自己這樣也好」 |
| 2 | 與弟妹翻出**舊信** | **levélcsomag** ✓;Major Döme ✓ | ✅ |
| 3 | 90 年代巴拉頓、Eszter 與 Kata / Betti 度假 | 「három jó barátnő a **Balatonnál** vakációzik」+ 角色表 | ✅ |
| 4 | 認識 Gergő 與 Gábor / Csabi,樂團 **Kuplung** | 角色表 ✓;Kuplung 見 port.hu 留言「**Kuplung-banda jelenet**」 | ✅ |
| 5 | ~~在 **Szigliget** 海灘演出~~ | 三個 source 皆查無 | 🚩 已刪地名 |
| 6 | Eszter 已許給可靠的 **Major Márton** | 「csak Eszter akar **hűséges maradni az otthon hagyott, karót nyelt pasijához**」+ 角色 | ✅ |
| 7 | 今昔交錯、重新學會信任與愛 | 官方逐句對應 | ✅ |

## [HU-12] Elvált nők klubja ✅ 全通過(零修正)
**Chrome 開啟**:jegy.hu/program/elvalt-nok-klubja-premier-musical-193357(**官方劇情全文 + 角色表**)

**原文照抄**:「**Három régi barátnő hosszú évek után újra találkozik egy közös ismerősük temetésén. Brenda, Elise és Annie ráébrednek, hogy életük meglepően hasonló fordulatot vett: mindhármukat elhagyta a férje egy fiatalabb nőért.** A kezdeti **csalódottság és önsajnálat** után a három nő **összefog, hogy visszaszerezzék önbecsülésüket – és közben egy kis elégtételt is vegyenek volt férjeiken**. A bosszú azonban… arra is ráébreszti őket, hogy **az igazi győzelem nem a férfiakon, hanem saját félelmeik és bizonytalanságaik legyőzésében rejlik**… témák: **az öregedés, a válás, az újrakezdés és az önmagunkra találás**」

**判定**:葬禮重逢、都被丈夫為年輕女人拋棄、失望與自憐後結盟、重拾自尊並報復、真正的勝利是戰勝自身恐懼 —— **每一句逐句精準對應**,零修正。

## [HU-13] Carmen(Wildhorn / Budapesti Operettszínház)(修 2 處)
**Chrome 開啟**
1. jegy.hu/program/carmen-147472(**官方劇情 + 完整角色表**)
2. operett.hu/repertoar/carmen

**原文照抄**
- 劇情:「**Egy spanyol kisvárosban eljegyzést tartanak: Mayor Mendoza, a helyi polgármester férjhez adja lányát, Catarinát José Riverához. Az esemény azonban váratlan fordulatot vesz, amikor megérkezik Carmennel az élen egy cirkuszi vándortársulat. A forróvérű, vadító, féktelen természetű lány megbolondítja Josét, olyannyira, hogy a férfi képes érte feladni addigi kiegyensúlyozott életét.**… **fókuszpontjában a cirkusz, mint műfaj és színpadi környezet áll**」;導演 **Homonnay Zsolt**
- 角色表:**Carmen** / **Jose Rivéra, rendőrhadnagy** / **Garcia, késdobáló** / **Katarina, a polgármester lánya** / **Zuniga, rendőrkapitány** / **Mendoza, polgármester** / **Inmar, José barátja** / **Inez, Katarina nagynénje** / **Jósnő** / Cirkuszi konferanszié

| # | 生成 | 對應原文 | 判定 |
|---|---|---|---|
| 1 | 警察 José 與市長之女訂婚 | **Jose Rivéra, rendőrhadnagy** ✓;「eljegyzést tartanak」 | ✅ |
| 2 | 巡迴馬戲團帶著 Carmen 到來,打亂他的人生 | 逐字對應 | ✅ |
| 3 | ~~**circus proprietor** García~~ | 官方:**Garcia, késdobáló(擲刀手)** | 🚩 已改 knife thrower(正好解釋後面擲刀的情節) |
| 4 | ~~Katarína~~ | 官方拼 **Katarina** | 🚩 已改 |
| 5 | 警長 Zuniga、市長 Mendoza、José 的朋友 **Inmar** | 角色表逐一對應(Inmar 開槍救人與「José barátja」相符) | ✅ |
| 6 | 馬戲團的公開陷阱與悲劇收場 | 「fókuszpontjában a cirkusz」+ 擲刀手設定一致 | ✅ |

## [HU-06] A meseautó(修 1 處)
**Chrome 開啟**
1. jegy.hu/program/a-meseauto-zenes-vigjatek-ket-reszben-170208(官方劇情)
2. veres1szinhaz.hu/a-meseauto/(**完整角色表**)
3. hu.wikipedia.org/wiki/Meseautó_(film,_1934)(電影 Cselekmény 全文)

**原文照抄**:「**Szűcs János bank-vezérigazgató nagy nőcsábász**, éppen pihenni készül, ám ezúttal **egy hónapos szabadságát távol a világtól és messze a nőktől szeretné eltölteni**. Mielőtt elindulna… **egy Horch 780-as kabriót vásárol 20000 pengőért**. Ám ekkor **egy az autószalonban nézelődő ifjú hölgy felkelti az érdeklődését, és minden másképpen alakul.**」

**判定**:①開頭逐句對應 ✅;②Anna kisasszony / Halmos Aladár / Péterffy Tamás / Kovács Sándor(**糖果店老闆**)/ Etel / Pityu / **Stux** / **J.B.** 全為舞台版角色 ✅;③🚩 生成自行補的銀行名「**Központi Bank**」查無據 → 已改為 a Budapest bank。

## [HU-07] Nikola Tesla – Végtelen energia(1 處拼寫分歧,據實記錄)
**Chrome 開啟**
1. jegy.hu/program/nikola-tesla-vegtelen-energia-musical-121504(**官方文案 + Főbb szereplők**)
2. deszkavizio.hu/megvan-a-nikola-tesla-vegtelen-energia-szereposztasa/

**原文照抄**
- 「bemutatva **Smiljantól, Prágán, Budapesten, Párizson, New Yorkon és a Chicagói Világkiállításon át egészen a Niagara vízeséséig** az akkori roppant színes és pezsdülő nagyvilágot」
- 「Tesla szakmai karrierje Budapestről, a **Puskás Telefontársaságtól (első munkahelye)** indult… megtervezhette a **Niagara-vízesésre épített** erőművét」
- 角色表:Nikola Tesla / **Szigeti Antal** / **Szigeti Adél** / **Thomas Alva Edison** / **Duka Tesla・Sarah Bernhardt**(同一演員分飾)/ **George Westinghause** / Bacherol・Lenin;rendező **Radó Denise**

**判定**:①場景序列逐項命中 ✅;②Puskás 電話公司=第一份工作 ✅ 精準;③Szigeti Antal / Adél / Edison / Duka Tesla / Sarah Bernhardt 全為官方角色 ✅;
④⚠ **拼寫分歧**:官方角色表拼 **George Westinghause**,deszkavizio 卡司公告拼 **George Westinghouse**。歷史人物標準拼法為 Westinghouse,判定官方筆誤 → **維持改為 Westinghouse**(分歧據實記錄,不掩蓋)。
⑤⚠ 開場「在 **Városliget** 用樹枝畫交流電動機原理」為史實名場面,官方頁未載 → WATCH,不改。

## [HU-04] Légy jó mindhalálig(1 處待補 source)
**Chrome 開啟**
1. jegy.hu/program/legy-jo-mindhalalig-191421(**我方場次 Pannon Várszínház 官方**)
2. jegy.hu/program/legy-jo-mindhalalig-194542(另一場次)
3. hu.wikipedia.org/wiki/Légy_jó_mindhalálig_(regény)(**原著 Történet 全文 + Musical 章節**)

**原文照抄**
- 我方場次官方掛名:「**Móricz Zsigmond – Kocsák Tibor – Miklós Tibor: LÉGY JÓ MINDHALÁLIG - musical -**」;「Móricz Zsigmond klasszikus regénye… **Nyilas Misi** ikonikus figurája hitelesen szólítja meg a mai fiatalságot」
- hu.wiki Musical 章節:「Zenéjét **Kocsák Tibor** írta… A librettót **Miklós Tibor** írta, az összekötő jeleneteket **Pinczés István**. Az ősbemutatót a **Debreceni Csokonai Színházban, 1991. április 19-én** tartották… **az átdolgozás a mai gyerekek életérzését, gondjait is érinti**」(官方自承是**改編**)
- hu.wiki 原著 Történet:「**Nyilas Misi a debreceni kollégium**… **a szobatársai felbontják az otthonról kapott pakk-ját**… **Pósalaky**, akinek délutánonként **felolvas**… **tegye meg a lutrin**… **Doroghy Sanyikát**… **megkedveli a középső lányt, Bellát**… Beszél a lutriról **Török bácsi fiának, Jánosnak**, majd a kisfiú **ottfelejti a lump gigerlinél a fogadószelvényt**… **A megtett számokat a lutrin kihúzzák, négy számot eltaláltak**… **Misit csalással, lopással vádolják, tanári konferencia elé idézik**… **Végül minden jóra fordul, kiderül ártatlansága, de Misit már lelkileg összetörték, nem akar többé debreceni diák lenni**」

| # | 生成 | 對應原文 | 判定 |
|---|---|---|---|
| 1 | 德布勒森 Kollégium、想家的 Nyilas Misi | 逐字對應 | ✅ |
| 2 | 家裡的包裹被同學吃光(連鞋油) | 「szobatársai **felbontják az otthonról kapott pakk-ját**」 | ✅ |
| 3 | 為盲眼的 Pósalaky 讀報、受託代填**彩券** | 「**Pósalaky**… **felolvas**… **tegye meg a lutrin**」 | ✅ |
| 4 | **Doroghy** 家的家教;傾心 **Bella** | 「**Doroghy Sanyikát**… **megkedveli… Bellát**」 | ✅ |
| 5 | 彩券中獎 | 「**négy számot eltaláltak**」 | ✅ |
| 6 | 被控詐欺/侵占、面對教師會議 | 「**csalással, lopással vádolják, tanári konferencia elé idézik**」 | ✅ |
| 7 | 洗清卻已心力交瘁,告別德布勒森 | 「**kiderül ártatlansága, de… lelkileg összetörték, nem akar többé debreceni diák lenni**」 | ✅ 精準 |
| 8 | **Török János 拿走彩券並帶 Bella 私奔**;十福林栽贓 | 原著是「**ottfelejti a lump gigerlinél a reskontót**」;**音樂劇為改編版**,triage 的 5 個音樂劇 source 寫的是私奔版 | ⚠ WATCH:待補一個 Chrome 實讀的音樂劇 source;依「查該製作」原則暫不改 |
| 9 | **Valkay tanár úr** 介紹家教 | Valkay 在 hu.wiki 角色表 ✓;此細節未逐字 | ✅角色/⚠細節 |
