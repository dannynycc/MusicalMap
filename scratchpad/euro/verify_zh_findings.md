# 三語查證:繁中 / 簡中 逐部發現

方法:英文 51 部已在 §3 逐部對官方原文查證完畢(見 verify_chrome_evidence.md / _hu.md)。
中文兩版是**獨立生成**,錯誤與英文不重疊,故逐部全讀 + 對照同一批官方原文;
凡中文出現英文版沒有的新主張(人名、數字、情節、專名),一律另開 Chrome 查該製作官方來源。

判定分級:
- **A 局部事實錯** → 用 apply_fixes.py 精確替換(不動語感)
- **B 劇情大面積偏離** → 局部替換無法救,列入**重新生成**清單(不由我手寫:依專案規則 Perplexity 生成是主體,我只做事實關卡)

---

## [2] Aggiungi un posto a tavola

**官方來源**:it.wikipedia.org/wiki/Aggiungi_un_posto_a_tavola(逐場 Trama + 角色說明 + 八版卡司表)

官方關鍵原文:
> don Silvestro riceve una sorprendente **telefonata: è Dio** che gli annuncia… un **secondo diluvio universale**… lo incarica di **costruire un'arca**
> **Toto**: il ragazzo sciocco del paese… grazie a un miracolo, si innamorerà e **farà innamorare di sé Consolazione**… portandola con sé sull'arca
> **Clementina, figlia del Sindaco e perdutamente innamorata di don Silvestro**
> **Cardinale**: l'Eminenza inviata dal Vaticano per mettere a tacere don Silvestro, accusato di follia visionaria
> Grazie all'intervento di don Silvestro per salvare i suoi amici, il Signore decide di **far cessare la pioggia**… tutti siedono a tavola a brindare… nel quale arriva in volo una **colomba bianca**

### 繁中 → A(已修 3 處)
| 原文 | 問題 | 已改為 |
|---|---|---|
| 克蕾曼蒂娜仍執著…**神父只能克制情感、守住信仰與職責** | 官方相反:神父最後**吻了她**,上帝也「contrario al celibato」,洪水後兩人能在一起 | 表白→以獨身戒律推辭→仍吻了她,上帝表明不贊成獨身 |
| 停止洪水,**讓彩虹重現** | 官方無彩虹,是**白鴿**飛落 | 讓大雨停歇 |
| 村民圍坐在長桌旁共享盛宴 | (承上,補回官方的白鴿意象) | 舉杯;那多留的位子上飛落一隻白鴿 |

繁中其餘全部命中官方:上帝**打電話**、第二次大洪水、造方舟、Silvestro/Toto/Crispino/Clementina/Consolazione 五個角色定位、Clementina 藉**告解**掩飾、梵蒂岡派來的樞機指他**瘋了**並說服村民不信、神父放棄方舟去救人、多留一個位子的題旨。

### 簡中 → **B(需重新生成)**
| 簡中原文 | 官方事實 |
|---|---|
| 一位自称奉上帝旨意而来的**神秘使者忽然降临** | 沒有使者,是**上帝親自打電話**給神父 |
| 村中青年托托**深爱克莱门蒂娜** | **兩條感情線搞混**:Toto 愛的是 **Consolazione** 並娶她;Clementina 是市長女兒、愛的是**神父** |
| 却因**家庭阻挠**和灾难将至,难以决定是否勇敢追随爱情 | 查無據 |
| 还得为方舟上的**座位作出艰难选择** | 查無據 |
| 危机最终…让原本狭小的**方舟成为人人能够共同前行的家园** | 官方結局是**洪水停止**、大家坐下舉杯,不是住進方舟 |
| (完全未出現) | Consolazione、樞機主教、洪水真的降臨、神父棄舟救人、上帝停雨、白鴿 |

→ 錯誤遍及每一段且含主線人物關係倒錯,非局部替換可救。

---

## [16] VY NEJSTE ŽENA, PANE! — 簡中 **B(需重新生成)**

**官方來源**:divadlorb.cz/repertoar/vy-nejste-zena-pane/(§3 已查)
> Dva cizí lidé, co se potřebovali jen přitulit, si domluvili vášnivé rande na anonymní seznamce.
> **Kdyby jen tušili, že jsou oba muži**… veselou cestu od bláznivého nedorozumění až k **neobyčejně korektní totalitě**
> co se může stát, když se z tak intimních věcí, jako je sexualita a láska, **stane nástroj moci**

**繁中**:匿名交友網站互傳訊息 → 見面才發現兩人都是男的 → 其中一人拒絕 → 不得志的律師兼政治人物把它包裝成歧視案件、上法庭與媒體 → 諷刺把親密關係全面政治化。**與官方完全相符,0 處修改。**

**簡中**:寫成了**另一齣戲**——「膽小男子為逃避追債躲進布拉格小劇院後台,穿上女演員禮服、假髮、高跟鞋,化名『薇拉』混入巡演劇團,成為觀眾追捧的新星;劇團經理要他繼續冒充,女主演嫉妒,樂隊指揮被『神秘女人』吸引,追債人循線而來……」
→ 這是 Sugar / Charley's Aunt 型的變裝喜劇,**與本劇沒有任何一處交集**:沒有交友網站、沒有兩個男人的約會、沒有律師、沒有法庭、沒有「寬容」的政治操作。整篇無一句可用。

---

## [17] Zlatovláska(繁中 4 處 / 簡中 1 處,皆已修)

**官方來源**:hdk.cz 官方角色表(展開 Obsazení)、cs.wiki《Zlatovláska (film, 1973)》Děj —— 本製作官方自述為 1973 電影音樂童話的新製作。

| 版本 | 原文 | 問題 | 已改為 |
|---|---|---|---|
| 繁 | 國王**卡齊斯維特** / 父王**莫伊米爾** | 官方角色表只有 Otec Zlatovlásky、Zlý král,**兩位國王都沒有名字**(英文版當時已刪) | 移除兩個編造的國王名(3 處) |
| 繁 | 尋回**海中**的戒指、辨認細小的珍珠 | 官方:珍珠在**草叢**中找回、金戒指從**湖底**撈起、第三題是**生死水** | 在草叢裡找回失落的珍珠、從湖底撈起金戒指,並取來生死之水 |
| 簡 | 从**灰烬中分拣散落的种子**、寻回遗失**海中**的戒指 | 「從灰燼中分揀種子」是**灰姑娘**的考驗,不是本劇;戒指在湖底 | 在草丛里找回失落的珍珠、从湖底捞起金戒指 |

繁簡其餘(蛇肉、聽懂獸語、國王震怒、救螞蟻/烏鴉/金魚、蒼蠅相伴、動物報恩、國王想奪走公主、生死水復活)皆與官方相符。

---

## [20] Rebelové — 簡中 1 處(已修)

官方(cs.wiki《Rebelové》Děj + 卡司表):
> Film vypráví příběh **tří maturantek – Terezy, Bugyny, Julči**, a **tří vojáků, uprchlíků z armády, chystajících se emigrovat – Šimona, Boba a Emana**. Vojáci chtějí odjet do **San Franciska**… Tereza, její otec a jeho přítelkyně emigrují. **Šimon skončí ve vězení.**

| 版本 | 劇情 | 事實 | 語意 |
|---|---|---|---|
| 英 | ✓ three soldiers—Šimon, Bob and Eman;木材列車偷渡西德、前往 San Francisco;Alžběta / Farář / Průvodčí Douša 皆為角色 | ✓ | ✓ |
| 繁 | ✓ 三名逃兵、Olda 是本地追求者(與官方不衝突)、牧師親戚的教堂(英文版列有 Farář 角色佐證) | ✓ | ✓ |
| 簡 | ✗→✓ 「他与鲍勃、埃曼、**奥尔达**三名逃离军营的年轻士兵同行」=**四個逃兵**且誤把 Olda 列入 → 已改為「他和鲍勃、埃曼一样,是逃离军营的年轻士兵,三人正设法搭车前往西方」 | 修 1 處 | ✓ |

---

## [21] Anděl Páně — 簡中 **B(需重新生成)**

官方(hdk.cz):
> V něm **Anděl Petronel – popleta a nebeský outsider** putuje v doprovodu **škodolibého čerta Uriáše** po Zemi, aby **dokázal Pánu Bohu, jak lehké je napravovat hříšníky** a tím se zároveň **sám nedostat do pekla**.
官方卡司(多來源一致):**Dorotka**: Kateřina Marie Fialová / Kristýna Daňhelová / Ines Ben Ahmed;另有 Klíčnice、Hrabě、Panna Marie。

| 版本 | 判定 |
|---|---|
| 英 | ✓ Petronel / Uriáš / Správce / Klíčnice / Dorotka / Hrabě 全部是官方角色 |
| 繁 | ✓ 「笨手笨腳的天使彼得羅內爾」對應 popleta;「愛捉弄人的惡魔烏里亞什」對應 škodolibý čert;墮地獄的威脅、感化罪人的任務、多蘿特卡、聖母皆有據。**0 處** |
| 簡 | ✗ **整篇人物都不存在**:天使叫「彼得」(官方 Petronel)、主角是「樂師卡雷爾」與「姑娘安娜」(查無據)、惡魔寫成「惡魔代理人」(官方 Uriáš)。無一句可用 |

---

## [22] Močál Story — 繁中 2 處(已修)

官方劇評(ocima7.cz,HDK 製作):
> **Spolužačky Dáša Nováková a Stáňa Poláková** již delší dobu **postrádají svoji kamarádku Bláža Procházkovou**. **V lese najdou některé její věci**… za pomoci dvou svérázných policistů po ztracené kamarádce pátrají… narážejí na… **upíry, Jožinem z bažin či zvědavými medvědy**.
(MUNI 報導標題亦作「hledání **Bláži**」)

| 版本 | 判定 |
|---|---|
| 英 | ✓ 「When a classmate disappears… Stáňa Poláková and Dáša Nováková set out」——兩人是尋人者,失蹤者未指名 |
| 繁 | ✗→✓ 把**尋人者達莎寫成失蹤者**,通篇沒有 Blažena → 已改回「達莎與史塔妮亞在林中撿到布拉熱娜掉落的物品」(2 處) |
| 簡 | ✓ 逐字對應官方,連「在林中发现遗落的物品」都命中。**0 處** |

---

## [23] Kapka medu pro Verunku — 簡中 2 處(已修)

官方(pixapro.cz 角色列 + musical.cz):
> **Princ Honza / Princ Mirek / Myslivec Jirka**
> Na cestu se vydali **tři hrdinové – myslivec Jirka a princové Honza a Mirek**
> se odehrává na pohádkovém ostrově, kde vedle sebe žijí **tři království…: Zlatovláskov, Popelkov a Honzovsko**

| 版本 | 判定 |
|---|---|
| 英 | ✓ both **Princ Mirek** of Popelkov and **Princ Honza** of Honzovsko;Kapeska 為自然力量女王 |
| 繁 | ✓ 兩位王子 + **獵人吉爾卡**、三個王國、女王卡佩絲卡、蜜蜂螫致沉睡百年,全對。**0 處** |
| 簡 | ✗→✓ 「**三位王子**」「**三名性格各异的王子**」把獵人 Jirka 也算成王子 → 已改為兩位王子 + 獵人伊日卡 |

---

## [18] Edudant a Francimor / [19] Čarodějnice Bordelína — 三語皆 0 處

- [18] 原著 Děj 逐字證實**兩版都對**:簡中「進城修魔法自行車→被學區督學發現沒上學」=「vyslala do města, aby nechali opravit její **kolo**… zahlédl **okresní školní inspektor**」;繁中「強盜、仙女、水妖、狗像人一樣生活的城市」=「mezi **loupežníky, víly**, nebo třeba k **vodníkovi**」+「**město, kde se psi chovali jako lidé**」。
- [19] 官方角色表 Bordelína / Sova **Mudrlice** / Čarodějnice **Řachatice** / Veverka **Drzečka** / Čaroděj **Puchonosor** / Zajíc **Cyril** —— 簡中五個角色名全中;劇評逐字證實「její **bratr** Puchonosor…**sestřenka** Řachatice」「musí za každou cenu **zůstat zlá a hlavně nikomu nepomáhat**」「už kují pikle, jak ji připravit o její **čarovnou moc, aby oni sami byli silnější**」。

---

## [24] Snowboarďáci — 繁中 1 處 / 簡中 2 處(已修)

官方角色表(divadlorb.cz):Rendy / Jáchym / **Lucka** / Marta / Panter / Nymfomanka / Milan / Pes / Sněhulák / Kluk / Dívka / Dívka 2
官方簡介:「Rendy a Jáchym… bojují o své místo na slunci, na svahu a **v srdci krásné Lucky**.」
電影 Děj(cs.wiki):「**Jáchym s sebou musí vzít svou otravnou sestru**」;卡司:Ester Geislerová **Marta**、Barbora Seidlová **Tereza**、Lucie Vondráčková **Klára**、Martina Klírová **Lucie**;「skupina místních frajerů, kteří si říkají **Snow Panthers**」;「ztratí bratrancova psa, nabourají mu auto, **naštvou sestru**, spadnou do řeky… jízdou po lavinovém svahu s Pantery… skončí v nemocnici. Těsně před půlnocí z nemocnice utečou」

| 版本 | 劇情 | 事實 | 語意 |
|---|---|---|---|
| 英 | ✓ 只提 Lucka、Panter、Nymfomanka、Milan——全是舞台版角色 | ✓ | ✓ |
| 繁 | 妹妹瑪塔 ✓(電影 sestra = Marta);✗→✓ 「露西、克拉拉與泰瑞莎三名女孩」是**電影**設定,舞台版把三人併為 **Lucka** 一角 → 已改為「漂亮的露茜卡」 | 修 1 處 | ✓ |
| 簡 | ✗→✓ 把女主角 **Lucka 寫成「姐姐」**(她是兩人爭取的對象,跟班是妹妹 Marta);「惹怒露茜卡」官方是「naštvou **sestru**」 → 已改 2 處。其餘(遊戲廳贏季票、表哥小屋變勞動營、雪豹團、弄丟狗/撞車/落水、雪坡較量進醫院、午夜前逃出醫院)全部逐字命中 | 修 2 處 | ✓ |

---

## [25] A dzsungel könyve — 簡中 2 處(已修):**被迪士尼版汙染**

官方(hu.wikipedia 該劇兩幕劇情全文,§3 已逐句比對過):
> 猴子擄走 Maugli 並推他為首領、之後反過來對付他;**Ká 催眠猴群、差點吃掉 Maugli,被 Balu 與 Bagira 阻止**
> 年老的 **Akela** 在 Sir Kán 設下的試煉中失敗、Sir Kán 自立為首領;**Bagira 派 Maugli 去人類村子取紅花(火)**;Maugli 帶火把回來救下 Akela、趕走 Sir Kán
> 第二幕:村裡只有女人在家,**Túna(村長 Buldeó 的女人)開始教他說話**

| 版本 | 判定 |
|---|---|
| 英 | ✓ §3 已判為「全篇逐句對得上,品質最高的一篇」 |
| 繁 | ✓ 阿克拉 / 巴希拉 / 巴魯 / 希爾汗 / 卡 / **圖娜** / **獵人布爾迪歐** 全部命中官方。**0 處** |
| 簡 | ✗→✓ ①「猴群首领**路易**」——**King Louie 是迪士尼 1967 動畫的原創角色**,吉卜林原著與本劇皆無;②「路易渴望掌握人类的红花」——官方是 Bagira 派 Maugli 去取紅花救 Akela;③「少女**梅苏亚**」——官方是 **Túna**(Messua 是原著小說的名字)。已改回官方版本 |

---

## [26] A Padlás — 簡中 **B(需重新生成)**

官方(hu.wikipedia 全文,§3 已逐句比對):Rádiós / 超級電腦 **Robinson** / **Süni** / **Mamóka** / 四個幽靈 **Herceg・Kölyök・Lámpás・沉默的 Meglökő** / **Révész**(擺渡人)/ **Barrabás** / **Témüller** / Detektív / Üteg / Süni 上屋頂接天線 / Rádiós 用機器召來暴風雪逼退直升機

| 版本 | 判定 |
|---|---|
| 英 | ✓ 全部角色與情節命中 |
| 繁 | ✓ 拉迪歐斯 / 羅賓森 / 蘇妮 / 瑪莫卡 / 王子・小子・燈籠・巨人推手 / 擺渡人 / 巴拉巴斯 / 偵探警察 / 蘇妮引開警方 / 暴風雪 —— **逐一對應,0 處** |
| 簡 | ✗ **整篇人物與設定都不存在**:「修理工雷茲」「巴蘭卡斯飛船」「少年梅尼哈爾特」「少女克勒姆普莉」「照看一群無家可歸的孩子」——官方沒有任何一個。無一句可用 |

---

## [27] Macskafogó — 三語皆 0 處

官方(jozsefattilaszinhaz.hu 角色表 + 官方簡介):M. M. u. 80 年 / X 星球 / 貓幫 Mr. Fritz Teufel / **Intermouse** 退休王牌特工 **Nick Grabowski** / 到 **Pokió** 取回 **Fushimishi 教授**的「**Macskafogó**」/「hogy a Macskafogó életre kel-e, az kiderül a darabból」
繁簡兩版的格拉博夫斯基、福希米希教授、波基歐、國際鼠聯、四名鼠族殺手、捕貓器扭轉貓鼠關係——全部有據。

---

## [28] Légy jó mindhalálig — 簡中 1 處(已修)

官方(hu.wiki 原著 Történet):Nyilas Misi 在德布勒森 Kollégium /「szobatársai felbontják az **otthonról kapott** pakk-ját」/ 為盲眼 **Pósalaky** 讀報並受託代填 **lutri**(彩券)/ **Doroghy Sanyika** 的家教 / **Bella** / 中四個號碼 / 被控 csalás・lopás、tanári konferencia / 洗清但「lelkileg összetörték, **nem akar többé debreceni diák lenni**」

| 版本 | 判定 |
|---|---|
| 英 | ✓ §3 逐條通過 |
| 繁 | ✓ 尼拉什．米西 / 鞋油被搶食 / **多羅吉家的小桑尼** / 失明的**波沙拉基**先生 / 讀報 / 彩券 / 洗清但只想回母親身邊 —— 全部命中官方。**0 處** |
| 簡 | ✗→✓ 把 Misi 寫成「**孤儿**」(官方是從家裡收到包裹、結局要回家) → 已改為「离开父母,被送来求学」。其餘缺少官方人名但無杜撰 |

---

## [29] MADE IN HUNGÁRIA — 繁中 6 處 / 簡中 6 處(已修):**兩版都用了電影的主角名**

官方(jozsefattilaszinhaz.hu 舞台版角色表):主角 **Ricky**(「Amerika magyarhangja」)/ Rudi / Csipu / Tripolisz / Kis Nyírő / Marina / Duci Juci / Sampon / Bigali elvtárs / **Vera** / **Röné(csókkirály)**
§3 記錄:「🎯 主角名 **Ricky** 是對的:ground truth 來自 2009 電影(主角叫 **Miki**),差點照電影去『修正』。」

| 版本 | 判定 |
|---|---|
| 英 | ✓ Ricky / Vera / Röné / Rudi / Csipu / Tripolisz / Kis Nyírő / Angyalföld 全對 |
| 繁 | ✗→✓ 主角寫成「米基」(=電影的 Miki)×6 → 已全部改為「瑞奇」。薇拉 ✓、羅內 ✓ 本來就對 |
| 簡 | ✗→✓ 主角「米基」×5 → 瑞奇;女主角「**埃迪特**」查無據 → 改為官方的**薇拉** |

---

## [30] A meseautó — 三語皆 0 處,但**撤回我先前對英文版的 1 處誤修**

官方角色表(veres1szinhaz.hu,完整):
> **SZŰCS JÁNOS, a Központi bank vezérigazgatója** / ANNA kisasszony, a titkárnője / HALMOS ALADÁR / PÉTERFFY TAMÁS, autószalon-tulajdonos / KOVÁCS SÁNDOR, budai kis cukorkaüzlet tulajdonosa / ETEL, a felesége / **VERA, a lányuk** / PITYU, Vera öccse / **SÁRI, Vera barátnője** / STUX / J.B.

- 🚨 **誤修撤回**:我先前判定生成寫的銀行名「Központi Bank」查無據,把英文版改成「a Budapest bank」。**官方角色表第一行就寫著 Központi bank** —— 生成本來就對。已改回。這是「把對的改成錯的」第 8 條,原因同前:官方資訊當時沒讀到角色表那一行。
- 繁中「薇拉」/ 簡中「维拉」✓ 官方 VERA;簡中「**中央银行**总经理」正是 Központi bank 的意譯 ✓;繁中「和朋友假裝有錢人逛高級商店」對應官方角色 **SÁRI, Vera barátnője** ✓;霍希(Horch 780)✓。

---

## [31] Nikola Tesla – Végtelen energia — 三語皆 0 處

官方(jegy.hu 文案 + Főbb szereplők):「**Smiljantól, Prágán, Budapesten, Párizson, New Yorkon és a Chicagói Világkiállításon át egészen a Niagara vízeséséig**」;角色表 Nikola Tesla / Szigeti Antal / **Szigeti Adél** / Thomas Alva Edison / Duka Tesla・Sarah Bernhardt / George Westinghause
- 繁中:斯米良 / 布達佩斯 / 巴黎 / 紐約 / 愛迪生 / **喬治・威斯汀豪斯** / 芝加哥世博 / 尼加拉瀑布 ✓
- 簡中:多了官方場景序列中的**布拉格** ✓;「**阿黛尔**的感情真挚而克制」正是官方角色 **Szigeti Adél** ✓

---

## [33] Mindig itt leszünk... Mohács 500 — 簡中 **B(需重新生成)**

官方(Budapesti Operettszínház + jegy.hu + PORT + Fidelio + Színház.online 五源一致):
> **Egy fiatal király, aki tudta, hogy hatalmas túlerő közeleg, mégsem fordított hátat országának.**
> Szomor György által írt rockmusical **II. Lajos, Habsburg Mária és kortársaik sorsán át** idézi meg a **szerelem, a helytállás és a remény** történetét.
官方卡司:II. Lajos — Tassonyi Balázs;Ulászló — Szomor György;Anna királyné — Lipics Franciska;Tomori Pál — Sándor Péter

| 版本 | 判定 |
|---|---|
| 繁 | ✓ 路易二世「明知敵我懸殊,仍不願背棄土地與臣民」**逐句對應官方第一句**;王后哈布斯堡的瑪麗亞 ✓;摩哈赤決戰、記憶延續 ✓。**0 處** |
| 簡 | ✗ 主角換成**查無據的虛構平民**「伊什特万」與戀人「安娜」,**II. Lajos 與 Habsburg Mária 一次都沒出現**——官方指名的兩位主角全部缺席,敘事框架與官方相反 |

---

## [34] Hogyan tudnék élni nélküled? — 繁中 2 處 / 簡中 2 處(已修):**與英文版同樣的兩個錯**

官方(jegy.hu 文案 + 角色表 + port.hu 電影劇情;官方明載劇本依據「Goda Krisztina és Kormos Anett által írt forgatókönyv alapján」):
> **Lili korunk tipikus lánya: magányos**, és igyekszik bebeszélni magának, hogy így jó neki
> a **kilencvenes évek elejének** egy felejthetetlen nyara, amikor három jó barátnő a **Balatonnál** vakációzik
> csak **Eszter akar hűséges maradni az otthon hagyott, karót nyelt pasijához**

| 版本 | 判定 |
|---|---|
| 英 | §3 已修同樣 2 處(「未婚夫的死」→ 孤獨;刪 Szigliget) |
| 繁 | ✗→✓ ①「四年前痛失未婚夫」官方是 **magányos**(孤獨);②「1994年」官方只寫 90 年代初;③「西格利蓋特海灘」三源查無 → 已修 |
| 簡 | ✗→✓ ①「未婚夫去世四年后」同上;②「锡格利盖特海滩」同上 → 已修。「20世纪90年代初」✓、樂團「离合器」(Kuplung)✓ 本來就對 |

---

## [32] A TRÓN / [35] Zrínyi 1566 — 三語皆 0 處

- [32]:繁中「南多爾費黑爾堡」與簡中「贝尔格莱德」是同一地(Nándorfehérvár)的不同譯法;Mátyás/马加什、匈雅提・亞諾什、拉斯洛、采列伊・烏爾里克、塞拉吉・伊莉莎白、布拉格囚禁、選王議會——皆為史實且與官方主線一致。
- [35]:繁中的侍從**切倫科**(Ferenc Črnko,圍城倖存者、日後寫下記述)、妻子伊娃、大維齊爾**索科利・梅赫梅德**皆有據;簡中的「苏莱曼在战局未定时去世」亦為史實(蘇萊曼死於圍城期間)。兩版互補,無衝突。

---

## [40] Musical 1989 — 簡中 **B(需重新生成)**;繁中 0 處

官方(§3 已查 teatrwkrakowie.pl 官方卡司表):LECHU(Lech Wałęsa)/ DANUSIA / KRYSIA(Frasyniuk)/ WŁADEK / GAJA(Kuroń)/ JACEK / BOGDAN(Borusewicz)/ ALINA(Pienkowska)/ HENRYKA(Krzywonos)/ ANNA(Walentynowicz)/ ZOFIA / GENERAŁ

| 版本 | 判定 |
|---|---|
| 英 | ✓ Lechu 爬上 Stocznia Gdańska 大門、三對夫妻、八月協議與 Solidarność、GENERAŁ 頒戒嚴 —— 全中 |
| 繁 | ✓ 1980 格但斯克造船廠罷工、華勒沙、**安娜．瓦倫蒂諾維奇**、**阿麗娜．皮恩科夫斯卡**、團結工聯、戒嚴、**弗拉西紐克**、**庫龍**、圓桌談判、部分自由選舉 —— 逐一對上官方卡司。**0 處** |
| 簡 | ✗ 寫成「1989 年華沙街頭少年**马切克**與伙伴踩着嘻哈节拍…市场经济涌入」的**虛構嘻哈少年故事**。官方十二個角色一個都沒有,團結工聯、罷工、戒嚴全部缺席 |

---

## [41] Serce ze szkła. Musical zen — 繁中 **B** / 簡中 **B**(兩版都需重新生成)

官方(Teatr Studio + Plebiscyt Musicalowy + Maria Peszek 本人 + krytyczne-spojrzenie 四源一致):
> **inspirowany baśnią „Królowa Śniegu" Hansa Christiana Andersena** oraz tekstami z książki…
> (Maria Peszek 本人)to **baśniowy musical biograficzny** na motywach „**Królowej Śniegu**" Andersena **i mojej książki „Naku*wiam zen"**
> oparty jest na **autobiograficznych wątkach z życia Marii Peszek i Jana Peszka**
> nieobliczalna, rozwiązła i czuła **medytacja pustki, ciała, miłości, polski kiedyś i dziś**

| 版本 | 判定 |
|---|---|
| 英 | ✓ **Kaj / Gerda 的多重化身(Maryjka, Ren, Mania, Maryśka)/ Królowa Śniegu / Wrona / Kruk / Gołębica / Finka / Matka Kaja / Lapończyk / Zbójniczka / Specjalistka Od Andersena / Dejmek**、「zima stulecia」、**Maria 與 Jan Peszek**、Jan 心臟病後能否再愛 —— 全部命中官方 |
| 繁 | ✗ 寫成「戰後華沙公寓、女子**潔西卡**照顧精神病母親、父親家暴」——**與本劇無一交集**:沒有《雪后》框架、沒有 Kaj/Gerda、沒有 Maria 與 Jan Peszek |
| 簡 | ✗ 寫成「臨海小城療養院、**阿妮娅**抱著裝滿碎玻璃的箱子等母親」——同樣與本劇無一交集 |

→ **這是繁中唯一一部需要重新生成的。**

---

## [42] Europavisjonar — 簡中 **B(需重新生成)**;繁中 0 處

官方形式:以歐洲歌唱大賽為框架,各國領袖化身參賽者。

| 版本 | 判定 |
|---|---|
| 英 | ✓ 柏林圍牆倒下起、Boris Jeltsin / Tony Blair / NATO / EU / Angela Merkel / Jens Stoltenberg / Erdoğan / Le Pen / Johnson / Putin 全部以參賽者登場 |
| 繁 | ✓ 同上,並補了難民危機、金融危機、民粹崛起、俄烏戰爭與以巴衝突使歡騰失去輕盈。**0 處** |
| 簡 | ✗ 寫成「奧斯陸辦公室裡年輕政治顧問**拉尔斯**為挪威大選策劃政治秀」——**歐洲歌唱大賽的框架、所有政治人物全部消失**,變成一齣挪威國內選舉戲 |

---

## [43] Änglagård — 繁中 1 處(已修);簡中 0 處

官方(§3 已查 Det Norske Teatret + sv.wikipedia 音樂劇條目 + Oscarsteatern 角色表):
> Ho er det **ukjente barnebarnet til den avdøde einstøingen Erik**, og arvingen til herregarden Änglagård
> **Kvifor drog mora til Fanny så brått frå byen og kven er eigentleg faren hennar?**
> 角色表:**Fanny Zander** / Rut Flogfält / Axel Flogfält / Zac Paulin / Gottfrid・Ivar Pettersson / Mårten Flogfält / Präst Henning Collmer

| 版本 | 判定 |
|---|---|
| 繁 | ✗→✓ ①姓氏寫成「芬妮．**桑德**」(官方 **Zander**);②「**父親**猝逝後前來繼承」官方是**祖父 Erik Zander** → 已一併改正,並補回官方的身世懸念(查清生父是誰) |
| 簡 | ✓ 1971 年露特拆信、五歲私生女、愛麗絲去柏林、**埃里克·赞德**、**孙女**范妮、马尔滕、伊瓦尔与戈特弗里德、**牧师亨宁** —— 全部命中。**0 處** |

---

## [44] Pippi på sirkus — 繁中 2 處(已修);簡中 0 處

官方(detnorsketeatret.no 全文):
> Bli med Pippi, **Tommy og Annika** på sirkus! Her møter dei mellom andre **sirkusprinsessa Miss Carmencita**, **linedansaren Elvira** og **ein illsint sirkusdirektør**. Pippi har aldri vore på sirkus, og **vil heller vere med, enn å sjå på**… Til slutt tek ho utfordringa om å **slåst med verdas sterkaste mann; Sterke Adolf**.
全頁搜尋 **Kling / Klang / politi / hest / ridning → 0 命中**

| 版本 | 判定 |
|---|---|
| 英 | ✓ Carmencita / Elvira / Adolf 皆在,無 Kling、Klang、馬 |
| 繁 | ✗→✓ ①「誤闖**馴馬表演**、以**騎術**贏得滿堂彩」官方無;②「**警察克林與克朗**」是原著角色,本製作沒有 → 已改為官方確有的卡門西塔、艾薇拉、強壯阿道夫 |
| 簡 | ✓ 卡门西塔 / 埃尔维拉 / 强壮阿道夫 / 团长 全部命中官方。**0 處** |

---

## [45] Emil i Lönneberga — 簡中 1 處(已修);繁中 0 處

| 版本 | 判定 |
|---|---|
| 繁 | ✓ 卡特胡特農莊、爸爸安東、媽媽阿爾瑪、妹妹伊達、**長工**阿爾弗雷德、**女傭**莉娜、湯盆卡頭、伊達升旗桿、木工小屋削木頭小人 —— 全對 |
| 簡 | ✗→✓ 「农庄里的**女佣**阿尔弗雷德和林娜」——官方 sv.wiki 明寫「**drängen Alfred** och **pigan Lina**」,Alfred 是男性長工 → 已改 |

---

## [46] Ronja Rövardotter — 簡中 1 處(已修);繁中 0 處

官方:「utmanar de varandra genom att hoppa över Helvetesgapet tills **Birk ramlar och Ronja räddar honom**」;「Birk räddar senare Ronja till livet **två gånger**」

| 版本 | 判定 |
|---|---|
| 繁 | ✓ 洛薇絲、隆妮、畢爾克、波爾卡、**狼嚎谷(Vargklämman)**、灰侏儒與野哈比鳥、熊洞、以自己交換畢爾克、不認父 —— 全對 |
| 簡 | ✗→✓ 「第一次遇见比克…**比克救下**困在地洞边的**罗妮娅**」把首次相遇的救援方向寫反 → 已改為「比克失足坠落,是罗妮娅救下了他;后来她的脚卡进屁股精的洞口时,比克也两度救她」 |

---

## [47] Så som i himmelen — 三語皆 0 處

兩版都寫對了**舞台版**的關鍵:繁中「決賽當天他再度心臟病發,無法站上指揮台;合唱團卻憑彼此聆聽完成演出,觀眾也受感染而加入和聲」;簡中「丹尼尔童年时的霸凌阴影,也因**康尼**的出现再次被唤起」——正是舞台版開場 Conny 霸凌七歲 Daniel 的設計(電影無此開場)。

---

## [48] The Julekalender — 繁中 **B(需重新生成)**;簡中 0 處

官方(da.wikipedia Handling + Wikiquote + Tivoli 官方英文頁):Gammel Nok 的 **spilledåse/livsmelodi** / 三個 nisser **Frits(Fritz)、Hansi、Günther** / **Den Store Bog** / **nåsåer** / 馬鈴薯農夫 **Oluf Sand** 與妻子 **Gertrud** / 假冒推銷員借宿的 **Benny** / **Gertrud ved en fejl har givet bogen væk til spejdernes indsamling**

| 版本 | 判定 |
|---|---|
| 繁 | ✗ 寫成「甘梅爾比村的三名地方青年**班尼、奧爾夫與艾爾文**對抗森林惡魔**費格斯**,北極聖誕老人派精靈協助」——把**反派 Benny** 和**農夫 Oluf** 寫成主角青年,加了查無據的惡魔與聖誕老人;音樂盒、鑰匙、Den Store Bog、nåsåer 全部缺席 |
| 簡 | ✓ 弗里茨/汉西/京特、老精灵「**老够了**」(Gammel Nok 意譯)、生命八音盒、《大书》、那索人、奥卢夫与格特鲁德、本尼以汽车抛锚借宿、弄弯螺旋桨、遗失地图、**格特鲁德误把书捐给童子军募捐** —— 逐項命中官方,**比英文版還完整。0 處** |

---

## [49] Ternet Ninja Live — 三語皆 0 處
兩版的史都華/斯图尔特、約恩/约恩、蘇內/苏内、潔西卡/杰西卡、葛倫/格伦,全部對上製作方官方新聞稿的角色名單。

---

## [50] De Spiekpietjes — 繁中 2 處 / 簡中 2 處(已修)
兩版的「乖孩子計量表 / 乖孩子仪」都正確對應官方的 **brave-kindjes-meter**(反而是英文版原本寫成 flinke-,已修);但兩版同樣有「**聖誕老人做最後巡視並發現**」「聖誕老人把希望寄託在小精靈身上」的問題——官方是「Er ontstaat paniek wanneer **ze**(小精靈們)merken dat de brave-kindjes-meter op hol slaat」,已一併修正。

---

# 中文 51/51 逐部查證完成

---

# 總結:三語 51/51 逐部深查

## 修正統計

| | 精確替換規則 | 專名全篇替換 | 需重新生成 |
|---|---|---|---|
| 英文 | 19 條(含**撤回我自己 1 處誤修**) | — | 0 |
| 繁中 | 26 條 | 6 處(MADE IN HUNGÁRIA 的 Ricky) | **2 部** |
| 簡中 | 28 條 | 6 處(Ricky、薇拉) | **8 部** |

## 需重新生成清單(局部替換救不回來)

**繁中 2 部**
1. `Serce ze szkła. Musical zen` — 官方是 Maria Peszek 的自傳式音樂劇(以安徒生《雪后》為框架、講她與父親 Jan Peszek);繁中寫成「潔西卡照顧精神病母親」
2. `The Julekalender` — 把反派 Benny 與農夫 Oluf 寫成「三名地方青年主角」,虛構了森林惡魔「費格斯」與北極聖誕老人

**簡中 8 部**
`Aggiungi un posto a tavola`(兩條感情線對調)、`VY NEJSTE ŽENA, PANE!`(整篇是變裝喜劇)、`Anděl Páně`(人物全不存在)、`A Padlás`(人物全不存在)、`Mohács 500`(主角換成虛構平民)、`Musical 1989`(換成虛構嘻哈少年)、`Serce ze szkła`(整篇無交集)、`Europavisjonar`(歌唱大賽框架全消失)

→ 重生成走 `px_gen.py`(Perplexity 為生成主體);prompt **只釘身份**(製作方／劇院／創作者／依據哪部作品),**不餵劇情**——劇情正確性留給生成後我自己再驗一次。

## 這一輪最重要的方法論結論

錯的方向**兩邊都有**,不能只往一個方向修:

**A. 生成寫對了舞台版,而我差點照原作改錯**(§3 已累積 8 條誤修並全部撤回)
- `MADE IN HUNGÁRIA`:舞台版主角是 **Ricky**,Miki 是 2009 電影 → 中文兩版反而用了電影名,已改正
- `Så som i himmelen`:舞台版 Daniel **死於心臟**,電影是廁所滑倒撞頭
- `Änglagård`:舞台版**一開場就讓觀眾看見 Rut 拆信**,電影把生父留作懸念
- `The Julekalender`:舞台版官方拼 **Frits**,電視劇是 Fritz
- `A meseautó`:銀行名 **Központi bank** 是官方寫的,我卻當成查無據刪掉了(第 8 條,已撤回)

**B. 生成被原作／他作汙染**
- `A dzsungel könyve` 簡中混入**迪士尼原創的「路易王」**(吉卜林原著與本劇皆無)
- `De Spiekpietjes` 三語都把官方的 **brave-kindjes-meter** 寫成原著書的 flinke-kinderen-machine 混合體
- `Snowboarďáci` 繁中用**電影**的三個女孩名(舞台版併為 Lucka 一人)
- `Pippi på sirkus` 繁中寫進**原著**的警察 Kling och Klang 與馴馬橋段(本製作沒有)
- `Zlatovláska` 簡中把考驗寫成**灰姑娘**的「從灰燼中分揀種子」

**唯一可靠的判準:這個製作自己的官方怎麼寫。** 原著、電影、其他語言版本都只能當對照,不能當標準。

## 另外修好的回歸地雷
`gen/apply_fixes.py` 裡原本留著 7 條**已被推翻**的舊修法,任何人重跑就會把已修正的內容再次改壞。已全部刪除並留下「切勿復原」註記與根因;同時讓腳本能區分「先前已套用」與「真的匹配不到」,現在 `--check` 為 **匹配不到 0**。
另加了 13 個哨兵回歸檢查(那些「我曾改錯、後來復原」的字串必須still在),已全部通過。

---

# 重新生成後的複驗(重生成不等於就對)

## 繁中 2 部(已完成並回填)

### Serce ze szkła. Musical zen — 框架已正確,但仍不完整
新版寫的是**葛爾達追尋被冰雪女王帶走的凱**——與官方的《雪后》基底相符(原本寫成「潔西卡照顧精神病母親」,完全無關)。
⚠ **仍缺本劇最關鍵的自傳層次**:官方明載「oparty jest na **autobiograficznych wątkach z życia Marii Peszek i Jana Peszka**」,Maria Peszek 本人也說是「baśniowy **musical biograficzny**… i **mojej książki**」;英文版有寫到 Maria 與 Jan Peszek 同在台上、以及 Gerda 的多重化身(Maryjka / Ren / Mania / Maryśka)。
→ 判定:**接受**(框架正確、無杜撰、無事實錯誤),但據實記錄「未涵蓋自傳層次」。這部是冷門的波蘭實驗劇,Perplexity 可用資料本就有限;再逼它補反而容易生出杜撰。

### The Julekalender — 修 1 處
新版逐條命中官方:弗里茨/漢西/京特、日德蘭洞穴、老精靈「**夠老**」的音樂盒與鑰匙、音樂盒停擺即life終、《**大書**》幾乎無所不答、**諾索人**、農夫**歐魯夫與葛楚德・桑德**、班尼是偽裝成人類的諾索人。
✗→✓ 唯一一處:「自稱**推銷鞋襪**的陌生人班尼,先以**車子沒油、爆胎**等藉口」——官方只寫「den københavnske **handelsrejsende** Benny, som **påstår at hans bil er brudt sammen** og spørger, **om han kan overnatte**」,沒有鞋襪、沒有沒油/爆胎。已改為官方寫法。
(同一處的公司名「Koch Sokker og Sko」先前也在英文版被查無據刪掉——**Perplexity 對這一點會反覆生成同類細節,下次重生成要特別盯**。)

## 簡中重生成 — 第 1 部複驗:`Aggiungi un posto a tavola` **仍未通過**

新版與官方(it.wikipedia Trama + 角色說明)比對:
| 新版簡中 | 官方 |
|---|---|
| 在教堂钟声中接到**上天的旨意** | 官方是**上帝親自打電話**(「riceve una sorprendente **telefonata: è Dio**」)——本劇最標誌性的設定,漏了 |
| **四天后**将有洪水 | 官方未寫天數 |
| 富有的**地主康索利尼**觊觎镇长之女 | ✗ 官方無此角色。**Consolazione 是「donna di facili costumi」的女性**,被誤寫成男性地主 |
| 克莱门蒂娜**爱着年轻的托托** | ✗✗ 官方:**Clementina 愛的是神父 Silvestro**;**Toto 愛的是 Consolazione 並娶她**(又一次把兩條線搞錯,只是錯法不同) |
| 洪水**没有**像众人想象的那样席卷而来 | ✗ 官方:**scoppia il diluvio**(洪水真的爆發),是神父放棄方舟去救朋友後上帝才 far cessare la pioggia |
| (缺席) | 梵蒂岡樞機主教指他 follia、市長逃跑並假冒聖人聲音、神父吻 Clementina、結尾飛落的**白鴿** |

→ **重生成沒有解決問題**:Perplexity 對這部的可用資料不足,換個 prompt 只是換一組錯。
→ 這說明「重生成」不是萬靈丹,**跑完必須逐部複驗**;若多數仍不通過,策略要改(見下方決策)。

## 【WATCH 結案】VY NEJSTE ŽENA, PANE! 的「Liga tolerance / 寬容聯盟」

§3 當時查 divadlorb.cz 官方頁時**該頁沒有角色表**,只能標記「⚠ 待補一個含角色表的 source 再定案」。
這次重生成的簡中又寫出「宽容联盟」,於是回頭把角色表抓出來:
> **Hrají: Milan Kokeš : Jakub Slach, Libor Náramný: Ernesto Čekan, Žalobce: Lukáš Burian, Obhájkyně: Anna Kulovaná / Charlotte Doubravová, Soudkyně: Romana Goščíková, Přísedící: Jan Fanta, Novinářka: Alžběta Fišerová**

全是兩位當事人加法庭角色(檢察官／辯護律師／法官／陪審／記者),**沒有任何名為 Liga tolerance 的組織**;全頁 `Liga`、`toleranc` 皆 0 命中。
→ 結論:①英文版刪掉它是**正確的**(不是第 9 條誤修);②角色名 **Milan**、**Žalobce** 生成本來就對;③**繁中的「寬容聯盟」是我先前漏抓**,已改;④新版簡中同一處待回填後一併處理。

## 簡中重生成複驗(逐部)

| # | 劇目 | 結果 | 說明 |
|---|---|---|---|
| 1 | Aggiungi un posto a tavola | ✗ **不通過** | 換 prompt 只是換一組錯:Consolazione(女)→「富有的地主康索利尼」、Clementina 愛的人再次寫錯、結局寫成「洪水沒有到來」(官方 scoppia il diluvio) |
| 2 | VY NEJSTE ŽENA, PANE! | ✓ **通過** | 交友網站→發現都是男的→律師包裝成歧視案→「宽容联盟」勝選→「絕對正確」反噬,全部對應官方「od bláznivého nedorozumění až k neobyčejně korektní totalitě」。僅「宽容联盟」一詞待改(與繁中同一處,已證實查無據) |
| 3 | Anděl Páně | △ **可局部修** | 主角名全部改對:**彼得罗内尔**(Petronel)、**乌里亚什**(Uriáš)、**多萝塔**(Dorotka);結局「他最终改造的罪人正是自己」✓。但混入「繼母和姐姐們」(灰姑娘設定)與官方角色表沒有的「國王」「大臣」(官方為 Hrabě / Správce / Klíčnice)→ 修掉這 2 處即可通過 |
| 4 | A Padlás | ✗ **不通過** | ①**Barrabás 是闖入的通緝犯,被寫成「房東」**;②四個幽靈(Herceg/Kölyök/Lámpás/Meglökő,漂泊數百年)被寫成「四個孩子」;③接引他們的 **Révész(擺渡人)** 被寫成「星船」;④Süni、Mamóka、超級電腦 Robinson、暴風雪全部缺席 |
| 5 | Mindig itt leszünk... Mohács 500 | ✓ **通過** | **拉约什二世**(II. Lajos)與**哈布斯堡的玛丽亚**都回來了;「明知胜算渺茫,仍不愿背弃王冠所代表的国家与臣民」逐句對應官方「Egy fiatal király, aki tudta, hogy hatalmas túlerő közeleg, **mégsem fordított hátat országának**」;官方三個主題詞 **szerelem / helytállás / remény**(愛情/堅守/希望)全部到位;國王殞命亦為史實 |
| 6 | Musical 1989 | ✓ **通過** | 瓦文萨/达努塔/弗拉西纽克夫妇/库龙夫妇/博鲁塞维奇/皮恩科夫斯卡/团结工会/戒严/圆桌会议/1989选举 —— 官方十二個角色與主線全中 |
| 7 | Serce ze szkła | ✓ **通過** | 凯、**多個「格尔达」般的女性身影**(對應官方 Gerda 的多重化身 Maryjka/Ren/Mania/Maryśka)、空教堂/沼澤/盜賊城堡(對應 Zbójniczka)、**父女關係**(繁中新版缺的自傳層次,簡中這版有了)、危機中的冰雪女王(對應 Królowa Śniegu W Kryzysie) |
| 8 | Europavisjonar | ✓ **通過** | 歌唱大賽框架、英國/俄羅斯/歐盟/北約、普京/默克爾/布萊爾/斯托爾滕貝格/埃爾多安/勒龐、金融與難民危機、俄烏與以巴 —— 全中(唯字數 527 超出 400–450,已單獨重跑一次) |

### 簡中重生成最終結果:**5 通過 + 1 局部修後通過 + 2 不通過**

**上架 49 部**;**暫緩 2 部**(另存 `gen/out_zhs_HELD.json`,含未通過理由,保留日後重試):
- `Aggiungi un posto a tavola`
- `A Padlás`

理由與處置原則:每個語言在 `build_served_synopses.py` 是**獨立過濾**的,某語言缺某部只是該語言沒有簡介;
**寧可該語言缺一部,也不放錯的內容上線**(誠實優先於好看)。

### 這一輪關於「重新生成」的結論
重生成**不是萬靈丹**。通過的都是官方有清楚文案的劇;不通過的兩部正是 Perplexity 可用資料不足者——
換一個 prompt 只是換一組錯(Aggiungi 第一次把 Toto 的戀人寫錯,第二次把 Consolazione 變成男地主)。
**所以每一部重生成後都必須逐部複驗**,這一輪就靠複驗攔下了 2 部,並在通過的 6 部裡再抓出 4 處錯
(VY NEJSTE 的「宽容联盟」×2、Anděl Páně 的「國王/大臣/繼母姐姐」、繁中 Julekalender 的「推銷鞋襪/沒油爆胎」)。

### Europavisjonar 字數重跑:**放棄新版,保留原版**
單獨重跑一次得到 475 字(原版 527,目標區間 400–450),但複驗發現新版**內容更差**:
- 多出查無據的「**戈尔巴乔夫与里根**」開場合唱(英文版與繁中版的官方人物名單皆無)
- 把 **glasnost(開放政策)誤譯成「去玻璃化」**,語意不通
- 掉了原版有的 **斯托尔滕贝格、勒庞**(皆為官方名單人物)

→ 決策:**保留 527 字的原版**。字數超出 400–450 是格式問題,內容錯誤才是實質問題;
依「誠實優先於好看」,寧可一部字數偏長,不要放內容有誤的版本。已在檔案中據實記錄,不掩蓋這個取捨。
