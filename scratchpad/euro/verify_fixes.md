# §3 逐部查證紀錄 + 待修清單(Claude 本人親做;對照 verify_truth_*.md 的外部 ground truth)

## ✅ EN 批已收尾(51/51)
- **22 處事實修正已套用**(`gen/apply_fixes.py`,每條規則匹配不到就報錯,不會默默跳過):Cratchit 太太的假名 Rose、Saturnin 敘事者被冠上作者姓 Jirotka ×3、VY NEJSTE 查無據的「Liga tolerance」×3、Belle 的假身世與假身世懸念 ×3、Caravaggio 把敘事者 Don Fernando 寫成壓迫者、Rebelové 的假地名 Kostelec、**Zlatovláska 六處**(魚→蛇、兩個假國王名、四個假姊妹名、假的「國王二婚」結局)、Macskafogó 三個拼寫對齊原片、Nikola Tesla 的 Westinghouse、Pippi 官方沒有的「團長貪圖金幣」整句刪除。
- **2 部整篇重生成**(不是改幾句能救的):
  - **De Spiekpietjes** —— 原生成寫的是**系列裡的另一部**(Spiekpietje 333 失蹤 + kerstelf)。我方 2026-11-29 Trixxo Theater 那場官方明確是「**Paniek in de speelgoedfabriek**」。改用釘死劇名的 prompt 重生成後,內容完全對上官方(乖孩子計量器暴衝、工廠將爆炸、Spiekpietjes 用故意調皮的方式讓它平靜)。
  - **Il ragazzo dai pantaloni rosa** —— 原生成通篇是電影情節。prompt 釘死「2026 Teatro Sistina **舞台版**、Piparo/Proia 改編、不是 2024 電影」後重生成,新版帶出**成年 Andrea 回望**的框架與**音樂老師 Prof. Gioli**(兩者都是舞台版才有、且經兩篇獨立劇評證實),敏感段落措辭也審慎。
- **兩個「差點誤刪」的反例**(提醒:查不到 ≠ 不存在,要查得夠深):
  - **Raffaella 的 Giovanni Salvi 與 Alessandro Lo Cascio 是真的**——前者是 RAI 主管、第一個給 Raffaella 機會把她放進節目卡司的人;後者是 Carrà 的經紀人、導演 Cannito 的密友,劇中有以他為靈感的角色。原本已列入「待刪的無據人名」,查到 ilmattino/leggo/flaminioboni 的選角報導才確認要保留。
  - **MADE IN HUNGÁRIA 的 Ricky** 是舞台版的正確主角名(電影才叫 Miki)。
- **一處 ground truth 自我更正**:`nordic_etc_triage.md` 原本寫 The Julekalender 的 Gammel Nok 是「邪惡的 Krybbenisser」——**錯**。多源實讀後確認 Gammel Nok 是命在旦夕的長老精靈,三個 nisser 要找回音樂盒鑰匙救他;反派是假扮推銷員的 nåsåer **Benny**。生成寫的才是對的,已更正 `verify_truth_poland_nordic_be.md`。
- 最終檢查:51/51 全部達標(字數+總結)、**0 書評框架開頭、0 slug 殘留、0 空段**。
> 規則:語意對就**原文不動**(保留 Perplexity 語感);只改事實錯的那一處。
> 狀態:`OK`=三語皆通過、`FIX`=有事實錯待修、`WATCH`=需再查一個來源才能定。

---
## EN 批次(out_en.json)

### 1. A Christmas Carol(BIT)— **FIX(1 處)**
- 通過:Marley 鬼魂與鎖鏈、三靈順序與內容、Bob Cratchit、Tiny Tim、外甥 Fred、妹妹 **Fan**、第一任雇主 **Mr. Fezziwig**、結局送禮與轉變 — 均與 compagniabit.com / teatrocarcano / danzaeffebi 的 BIT 版官方描述與 Dickens 一致。
- 🚩 **「Bob, his wife Rose」**:任何來源(BIT 官方、劇院頁、Dickens 原著)都沒有「Rose」這個名字;原著為無名的 Mrs. Cratchit。→ 幻覺,**刪掉名字**(改為「his wife」)。

### 2. Alice nel Paese delle Meraviglie — **OK**
- 開頭「thirteen-year-old girl weary of being told it is time to grow up…longing to stop the clock」**精準命中此版(ItaliaShow / Nati da un Sogno,Roberta Bonino 編導)特有的設定**,不是通用 Carroll 敘事 → Perplexity 抓對了製作。
- 其餘(白兔、毛毛蟲、柴郡貓、三月兔、瘋帽匠茶會、紅心皇后、審判)為此劇公開描述涵蓋的仙境元素,無矛盾。

### 3. Aggiungi un posto a tavola — **OK**
- 通過:上帝來電要 Don Silvestro 造方舟 ✓;市長名 **Crispino** ✓(it.wiki 角色表);市長之女 **Clementina** 愛上神父 ✓;**Consolazione** ✓;純真的 **Totò** 愛上 Consolazione ✓;**樞機主教**從羅馬來抹黑神父 ✓;洪水因神父之舉而止、眾人同桌 ✓(it.wiki:「Nel finale, tutti siedono a tavola a brindare」)。
- 小註:「Consolazione, a glamorous woman sent to distract the village men from their labour」符合公認劇情脈絡(市長陣營的阻撓),it.wiki 摘要未逐字明載但不矛盾 → 不動。

### 4. Belle e la Bestia(Compagnia dell'ORA)— **FIX(2 處)**
- 通過:王子因傲慢被囚於獸身 ✓;唯有「愛他勝過自己性命」的人能解咒 ✓;Belle 偶然踏入城堡、喚醒野獸沉睡的情感與那位公主的容顏記憶 ✓;**Miguel** = 本版新增的反派、Belle 不領情的追求者、以欺瞞與嫉妒作梗 ✓(compagniadellora.it 官方)。
- 🚩 **「Belle, the kind-hearted daughter of a widowed merchant」**:官方 sinossi 只說她是「dal cuore puro e dallo spirito libero」的年輕女子,沒有喪偶商人父親的設定(那是原童話/迪士尼)。→ **刪掉身世**。
- 🚩 **「links Belle to the Princess erased from everyone's memory」/「is Belle truly connected to the lost Princess」**:官方明確**不把 Belle 認定為公主**(fetch 註:「La sinossi non identifica Belle come principessa」)。生成把「野獸想起公主的容顏」超譯成「Belle 可能就是失落的公主」的懸念 → **改回官方語意**(野獸在 Belle 身上重新感受到沉睡的情感與記憶),不編造身世謎團。

### 5. C'era una volta... Scugnizzi — **OK(1 小 WATCH)**
- 通過:兩人同為 **Nisida** 少年感化院出身、二十年後走上相反的路 ✓;Don Saverio 成為街頭神父、投身志工與音樂 ✓;**Raffaele「'o russo」成為 camorrista** ✓;**'o russo 殺死 Don Saverio**,而這場謀殺是他的失敗而非勝利——孩子們因此起而反抗 camorra、發出抗議之聲 ✓(it.wiki trama 逐句對上);**Rosa、Carmine** 確實在主要角色表中(scugnizza / scugnizzo)✓。
- ⚠ WATCH:「Rosa, a teenage mother raising her child alone」— it.wiki 角色表只標 Rosa 為 scugnizza,未載未成年母親設定。若找不到第二個來源支持 → 淡化為不指明的角色描述。

### 6. Forza Venite Gente — **OK**
- 通過(it.wiki 該劇條目逐項對上):**L'Angelo Biondo**(只有方濟各看得見聽得見的天使)✓;**La Cenciosa** 作為敘事/評論者 ✓;**Frate Leone**(團體的書記)✓;**Sorella Morte**(終場擬人角色)✓;馴服 **Gubbio 的狼** ✓;**第一座馬槽(presepe)** ✓;父親 **Pietro Bernardone** 的衝突 ✓;**Chiara** 放棄優渥生活 ✓;23 段歌唱場景涵蓋生平多個片段 ✓。
- 小註:「Pope Innocent III」與地名「Greccio」未在該 wiki 條目明載,但均為方濟各生平的標準史實(教宗批准會規、Greccio 馬槽),且與該劇涵蓋範圍相符 → 不動。

### 7. FRIDA Opera Musical — **OK**
- 通過(it.wiki「Frida Opera Musical」逐項對上):革命後的墨西哥 ✓;**La Catrina 作為貫穿全劇的敘事線索**(filo conduttore e narrante)✓;與 **Diego Rivera** 熾烈而反覆受考驗的關係 ✓;為身分與自我解放而戰 ✓;**Lev Trotsky、André Breton、Tina Modotti、Emiliano Zapata 以時代的象徵性人物出現在群像中** ✓;把個人經驗放進歷史群像的手法 ✓。

### 8. Gloria — **OK**
- 通過:Gloria = 一心想成功的年輕歌手 ✓;與家庭期待的衝突 ✓;愛情、友情、背叛與陰謀交錯 ✓;結尾走向「以自己的方式」成功 ✓(teatroarcimboldi / ilmessaggero / globalist 的官方劇情描述)。
- 重點:**沒有把它寫成 Umberto Tozzi 的傳記**(那會是大錯)→ 正確。
- ⚠ 版面:本篇正文只有一大段 + 總結段(其他部多為 3 段)。內容無誤,但入庫前確認前端呈現不致過於擁擠。

### 9. Il ragazzo dai pantaloni rosa — **FIX(版本問題)**
- 通過:真實事件、15 歲的 Andrea Spezzacatena、母親 **Teresa**、朋友 **Sara**、霸凌者 **Christian**、紅褲子誤洗成粉紅、校園與網路霸凌升級、Andrea 自殺、母親面對留下的紀錄 ✓。
- 🚩 **舞台版 ≠ 電影版**(ilsistina 官方 + mediaesipario 劇評):Piparo/Proia 的舞台版是**重新編排的 jukebox musical**,並**新增了兩個舞台版才有的元素**:①**「成年 Andrea」**(Christian Roberto 飾)作為回望自己少年時代的旁白;②**音樂老師 Prof. Gioli**(具療癒作用的角色),突顯音樂作為敘事主軸。
- 🚩 生成裡屬**電影專屬且無舞台版佐證**的細節:教宗合唱團試唱與「Andrea 獲選為教宗獻唱、Christian 落選」、姓氏「**Christian Todi**」、弟弟 **Daniele**、父親 **Tommaso**、**Sara 前往巴黎**、**十五歲生日的園遊會**。→ 最小修正:刪去這些未經舞台版佐證的專屬情節點,保留敘事骨幹,並讓文字符合舞台版(可帶出音樂作為救贖/回望視角),**不整段重寫**。
- ✅ **舞台版可以放心寫進去的**(zerkalospettacolo 劇評 + mediaesipario 劇評,兩篇獨立確認):舞台版新增了一個「**成年的 Andrea**」(Christian Roberto 飾),作為「舞台上的良心」在旁觀察、評論、陪伴,與過去和觀眾對話;**Sara 是他最好的朋友**;全劇以義大利流行金曲當「敘事關節」,把霸凌與網路霸凌的題材轉成共同經驗而非傳統情節推進。舞台版另有音樂老師 **Prof. Gioli** 這個電影沒有的角色(mediaesipario)。
- ⚠ 舞台版的細部情節在公開劇評中本來就寫得少(評論偏重導演與表演)→ **凡是只在電影裡才查得到的情節點,一律不寫**,寧可寫得概括。

### 10. LUPIN – Il Musical — **OK(1 小 WATCH)**
- 通過(lupinilmusical.it 官方 sinossi 逐句對上):開場即東方快車巴黎→伊斯坦堡 ✓;**Ahmed III 的鬱金香從保險箱消失**、看似 Lupin 的大手筆 ✓;竊案不是為竊案本身,而與 **Isabelle**——巴黎年輕孤女——有關 ✓;Lupin 對她「sentimento sincero, profondo」並**以一朵鬱金香日日相贈**贏得她 ✓;Isabelle 在**巧克力工廠**當女工 ✓;劇本 Salvatore Sito、原創音樂 Paola Magnanini ✓。
- ⚠ WATCH:生成把巧克力工廠寫成「bleak, oppressive, and full of unspoken threats…secrets, covert schemes」,官方只說那是「un luogo che evoca straordinarie suggestioni」(引人遐想之地)。屬氛圍加料而非事實錯 → 若要動,只把「陰森有陰謀」淡化,不重寫整段。

### 11. Maradona El Diego — **OK**
- 通過:貧困少年、把足球當成尊嚴與救贖的承諾 ✓;拿坡里與城市的共生關係 ✓;**聖 Gennaro(San Gennaro)作為反諷、慈悲而守望的存在** ✓——官方卡司確認 **Lello Arena 飾 San Gennaro**,定位是「遠離刻板印象、人性而反諷、深具象徵、連接神聖與世俗的橋樑」,生成描述完全對上;傳奇與凡人之間的距離、跌落與再起 ✓(取材《L'Avvocato del D10S》的人性辯護角度)。
- 補記(ground truth 追加):導演 **Jacopo Spirei**;製作 Patagonia Group;2027 年檔期。

### 12. Michelangelo da Caravaggio – A Rebel Rock Musical — **OK**
- 通過(官方卡司表逐名對上):**Lena Antognetti**(Maddalena)✓、**Annuccia Bianchini** ✓、**Cardinale Del Monte** ✓、**Costanza Colonna (Sforza)** ✓、**Giovanni Baglione**(敵對畫家)✓、**Ranuccio Tomassoni** ✓、**Don Fernando** ✓(由 Fabrizio Rizzolo 本人飾演);把窮人與妓女畫成聖人聖母、與教皇治下羅馬的衝突、殺人後逃亡與死亡陰影 ✓。
- 補記(ground truth 更正):**音樂 = Sandro Cuccuini + Fabrizio Rizzolo**;劇本/歌詞/導演 = Fulvio Crivello + Fabrizio Rizzolo(先前只記後者為全包,更正)。

### 13. Peter Pan il Musical(Bennato/Colombi)— **OK**
- 通過:Wendy、John、Michael、教他們飛、Tinker Bell、Neverland、迷失男孩、**Tiger Lily(Giglio Tigrato)**、美人魚、**Captain Hook** 與 **Smee(Spugna)**、吃掉虎克手的**滴答鱷魚**、毒藥與 Tink 捨身、最後劍鬥、Wendy 兄妹回倫敦 ✓(對上 marcheteatro / bennato.net / LAC 的官方元素清單與 Barrie 原著)。
- ✅ 開場的「說書人」框架**已證實為此製作的設計**:it.wikipedia「Peter Pan, il musical」角色表列有 **Cantastorie**(歷年皆有不同演員飾演),且劇情段落明載「La scena si apre in un parco di inizio XX secolo a Londra… Un cantastorie si presenta nei **Giardini di Kensington**, invitando i bambini ad ascoltare i suoi magici racconti」——與生成的第一句完全吻合。

### 14. Raffaella il Musical — **FIX(2 個無據人名)**
- 通過:出身 **Bellaria** 到羅馬 ✓(史實);古典舞訓練起家 ✓;先電影後電視 ✓;**Canzonissima** 的突破 ✓;**西班牙**的成功 ✓;聚焦生涯前段「一顆星如何誕生」✓;母親 **Iris** ✓(史實:Iris Dell'Acqua);**Nadia** ✓(官方徵選公告載明:「靈感來自 Raffaella 的表姊兼終生好友,風趣機敏、自嘲、話多」);**Gianni Boncompagni** ✓(史實上的創作與感情夥伴)。
- 🚩 **「television director Giovanni Salvi」與「friend Alessandro Lo Cascio」**:徵選公告的主要角色只有 RAFFAELLA 與 NADIA,兩個名字在任何官方或報導來源都查不到 → 無據,**刪掉這兩個人名**(該句對敘事不重要,刪去不傷語感)。

### 15. Win for life(Oblivion)— **OK**
- 通過(ticketone/musical.it/劇院頁的官方文案逐項對上,細節密度極高卻全部命中):陌生人按門鈴、**每天八千歐、永遠** ✓;保密條件 ✓;女主角**偷偷迷戀歷史學家 Alessandro Barbero 與他的 Robin Hood podcast** ✓;**懶散的丈夫**滿腦子宏大計畫(在烏克蘭上方造橋把摩爾多瓦接到海)✓;**只用兩個字加一句髒話表達的年邁殘障老人** ✓;**被瑜伽啟蒙卻更在意銀行帳戶的女兒** ✓;**放高利貸的毒販** ✓;**帶著成堆鈔票、看起來不像超級英雄的神祕蒙面人** ✓;**合唱隊與三名 mariachi 抱著吉他闖進來、動不動打斷敘事** ✓。
- 補記:全長 80 分鐘;製作 AGIDI。

> ⚠️ 捷克 10 部的 EN 版已用**修正後的 prompt 重新生成**(原本那句「用英語製作慣用的角色名」害它自己編英文名)。以下 16-19 的查證是**重生成後的新版**;舊版的問題記在最後面存查。

### 16. Saturnin(重生成版)— **FIX(1 處:敘事者被冠上作者的姓)**
- ✅ 角色名全部正名(重生成的效果):**Tetička Kateřina**(滿口莊嚴諺語)✓、**Milouš**(被寵壞、自命不凡)✓、**Dědeček** ✓、**Doktor Vlach**(冷眼旁觀的對照)✓、**Barbora** ✓ ——舊版的 Bertie / Doctor Witherspoon 消失了。
- 🚩 **「A young man named Jirotka」**:Jirotka 是**作者 Zdeněk Jirotka 的姓**,小説裡的敘事者(vypravěč)**沒有名字**。→ 刪掉這個名字(改回「a young Prague gentleman」之類)。
- 其餘通過:僕人以無懈可擊的禮節製造精心設計的混亂、把社交常規當笑料、讓人露出真面目;親戚被帶離城市進入越來越滑稽的處境;結尾戳破虛假的體面、鬆動僵化的家族期待、幫猶豫的戀人走近彼此 ✓。

### 17. VY NEJSTE ŽENA, PANE!(重生成版)— **FIX(1 個查無據的組織名)**
- ✅ 角色名全部對上官方角色表:**Milan Kokeš、Libor Náramný、Žalobce、Soudkyně、Přísedící、Obhájkyně**,連 **Novinářka**(女記者)都對(舊版英文版的「eager journalist」原來是真的)。
- ✅ 主題命中:官方說本劇批判「hyperkorektnost(過度政治正確)」、走向「neobyčejně korektní totalita(非比尋常的正確極權)」——生成寫「以寬容之名取得權力後反過來管制寬容」,正是這個意思;另一來源亦載「當性與愛這種私密之事變成權力工具會發生什麼」。
- 🚩 **「Liga tolerance」這個組織名查無據**(官方頁、劇院頁、多家售票頁都沒有)。→ 改成不指名的說法(某個以寬容為名的運動/團體),或找到來源再定。

### 18. Zlatovláska(重生成版)— 🚩🚩 **FIX(比舊版更糟,四處編造)**
- 🚩 **「a mysterious fish」→ 應為蛇(had)**:Erben 原著與 hdk.cz 官方都是「採藥婆送來一條蛇,吃了能懂獸語」。(舊版寫 snake 是對的,重生成反而錯。)
- 🚩 **「Král Kazisvět」與「Král Mojmír」仍是編的**,而且這一版還把兩人對調。hdk.cz 官方角色表只有「**Otec Zlatovlásky**」與「**Zlý král**」,兩位國王都沒有名字。
- 🚩 **姊妹名「Černovláska、Rudovláska、Hnědovláska、Plavovláska」是編的**:原著是十二個蒙面後一模一樣、無名字的姊妹。
- 🚩 **結局「Král Kazisvět 與 Babka 二婚」是編的**:原著/1973 電影是老國王誤用魔法水而死、Jiřík 成為國王娶了金髮公主。
- ✅ 對的部分:廚師 **Jiřík** 偷嚐後聽懂獸語、被派去為國王求娶金髮公主、路上救助 **mravenci(螞蟻)/ krkavci(烏鴉)/ zlatá rybka(金魚)** 並有 **Muška(蒼蠅)** 同行、動物朋友幫他完成難題、他與公主相愛使任務變成「服從 vs 真愛」的衝突 ✓(這四種動物正是 hdk.cz 官方寫的)。
- → 處理:骨幹留著,**把四類編造內容(魚、兩個國王名、四個姊妹名、二婚結局)全部拿掉**,國王改回官方的稱謂;若改完讀起來破碎,就針對這一部重新生成再驗。

### 19. Edudant a Francimor(重生成版)— **OK(1 處待證)**
- ✅ 幾乎逐名對上 prazskemuzikaly.cz 的完整卡司:**Halabába** ✓、**Fena Peggy**(狗城裡再現)✓、**Hospodský Brok** ✓、**Král Růženín** ✓、**Princezna Róza / Princezna Růža** ✓、**Loupežník**(家人不肯配合他做強盜)✓、**Ředitel školy** ✓;**Růžový patník** 城堡遺跡 ✓;收尾「世界不一定那麼粉紅」✓。
- ⚠ 待證:**校長發不出「p」音**這個特徵仍找不到來源(官方角色表不含此描述)。若補不到,刪掉這半句即可,其餘不動。
- 註:重生成版已無舊版的「hdk」slug 殘留。

### 20. Čarodějnice Bordelína — **OK(2 個小待證)**
- ✅ 角色名**逐一對上官方卡司**(divadlorb.cz / prazskemuzikaly.cz):**Sova Mudrlice**(貓頭鷹)、**Veverka Drzečka**(松鼠)、**Zajíc Cyril**(兔子)、**Čarodějnice Řachatice**、**Čaroděj Puchonosor** ✓ 全部存在。
- ✅ 骨幹對上官方劇情:Bordelína 搬進安靜的 **Bambručák** 森林、樣樣不滿意、飛快把一切照自己意思施法、動物與孩子束手無策、惡作劇一個接一個 ✓。
- ⚠ 待證(官方短文未載,屬合理但未證):魔法雨傘飛行、把苔蘚換成蕁麻、以及「Řachatice 與 Puchonosor 覬覦她的魔力」這條副線。若補不到第二個來源,保留骨幹、淡化這些細節。

### 21. Rebelové — **FIX(1 個地名)**
- ✅ 角色**全部對上 hdk.cz 官方角色表**:Tereza、Šimon、**Bugyna**、**Julča**、**Bob**、**Eman**、**Alžběta**、**Tatínek Terezy**(Tereza 的爸爸)、**Farář**(神父)、**Průvodčí Douša**(列車長)✓——連配角都對。1968 年夏天、逃兵躲藏、計畫越境、被發現、Šimon 入獄 ✓;八月華沙公約入侵終結一切 ✓。
- 🚩 **「the provincial town of Kostelec」**:hdk.cz 官方描述未提地點,2001 電影亦只說「捷克邊境地區」。→ 刪掉地名或改為泛稱的邊境小鎮。
- 小註:生成漏了 Olda(也追求 Tereza 的同學),不算錯,可不補。

### 22. Anděl Páně — **OK**
- ✅ 全部對上(cs.wikipedia 電影條目 + ceskatelevize 官方 + irozhlas):**Petronel** 是固執又笨手笨腳的天使,因為審判來者比上帝還嚴、甚至頂撞上帝而被罰下凡 ✓;**必須感化至少一個罪人,否則聖誕夜就墮入地獄** ✓;同行的是幸災樂禍的魔鬼 **Uriáš** ✓;人間遇到只顧玩樂的年輕**伯爵(hrabě)**、肆無忌憚偷竊主人的**správce(管家)**、貪圖財富的 **klíčnice(女管家)**、以及方圓內唯一的好心人——謙遜可愛的女僕 **Dorotka** ✓;結局:靠人的愛與希望把一切補回來,而 Petronel 最後感化的罪人是他自己,因此得以回天堂 ✓。

### 23. Močál Story — **OK(2 個小待證)**
- ✅ 角色**幾乎逐一對上 hdk.cz 官方角色表**:**Komisař Bambula** ✓、**Policista Véna「RAMBO」** ✓、**Stáňa Poláková** ✓、**Dáša Nováková** ✓、**Jožin**(同一演員兼演倉鼠與熊)✓、**Linda** ✓、**Jenda Benda**(兼演 houbař 採菇人、hasič 消防員)✓、**myslivec**(獵人)✓、**starosta**(市長)與 **upír**(吸血鬼)✓;官方劇情:「故事非常單純——一個失蹤的女同學,由兩名迷糊警察偵辦」,一路撞見 Ivan Mládek 歌裡的人物 ✓。
- ⚠ 待證:**listonoška**(女郵差)與 **ježibaba**(女巫)未在官方角色表;警官全名「Jaroslav Bambula」與「Véna Dopil」的名/姓也只在生成裡出現。→ 這些細節可淡化或刪,骨幹不動。

### 24. Kapka medu pro Verunku — **OK(2 個小 WATCH)**
- ✅ 對上 pixapro.cz 官方(這部先前被標「劇情薄」,現在補齊了):魔法島上三個王國 **Zlatovláskov(金髮公主國)/ Popelkov(灰姑娘國)/ Honzovsko(傻瓜洪扎國)** ✓ 名字完全正確;**Princezna Verunka 是唯一的新娘** ✓(解決了先前「Verunka 在劇中是誰」的疑問);**Princ Mirek 與 Princ Honza** ✓;**Kapeska** ✓;**獵人 Jirka(myslivec)** ✓;自然的力量因人們疏於照顧環境而發怒,對未來的統治者設下考驗勇氣、智慧與敬重自然的試煉 ✓。
- ⚠ WATCH ①:官方寫「**三位**王子同時求親」,生成只寫了兩位(Mirek、Honza)。②「一隻特別的蜜蜂螫了 Verunka、使她陷入百年沉睡」這個機關官方頁未載(雖與「蜂蜜」主題相合)。→ 兩點都再找一個來源;補不到就寫得含糊些,不寫死。

### 25. Snowboarďáci — **OK(2 個小 WATCH)**
- ✅ 舞台版核心對上 divadlorb.cz / aplausin.cz:**Rendy 與 Jáchym** 再度上山,為自己在陽光下、雪坡上與美麗的 **Lucka** 心裡的位置而戰 ✓(注意:**電影裡的女主角叫 Klára/Lucie,舞台版改叫 Lucka**,生成用 Lucka 是對的);**Špindlerův Mlýn** ✓、**Milan**(Jáchym 的表哥、山莊經理)✓、**Marta** ✓(電影由 Ester Geislerová 飾)。
- ⚠ WATCH:「**Panter**」與「**Nymfomanka**」兩個角色在電影卡司與舞台版公開資料都查不到 → 找不到第二來源就刪掉名字、保留情境描述。

### 26. A dzsungel könyve — **OK(全篇逐句對得上,品質最高的一篇)**
- 我把 hu.wikipedia 該劇條目的兩幕劇情**全文抓下來逐句比對**,生成的每個情節點都命中:
  - Sir Kán 攻擊 Maugli 一家、殺了父親、孩子逃進叢林 ✓;szioni 狼群首領 **Akela** 提議收留 ✓;**DzsTK(a dzsungel törvénykönyve,叢林法典)規定收養需要兩位保薦者** ✓;教導法律的熊 **Balu** 站到 Akela 這邊,黑豹 **Bagira** 用自己獵到的一頭牛說服其他狼 ✓。
  - 猴子擄走 Maugli 並推他為首領、之後反過來對付他;**Ká** 催眠猴群、差點吃掉 Maugli,被 Balu 與 Bagira 阻止 ✓。
  - 掉進 **Kobra** 的寶穴、出於憐憫收下 **ankus**、看見人類為它自相殘殺而懂得 Bagira 為何說人是「可怕的怪物」✓。
  - 年老的 Akela 在 Sir Kán 設下的試煉中失敗、Sir Kán 自立為首領;Bagira 派 Maugli 去人類村子取**紅花(火)**;Maugli 帶火把回來救下 Akela、趕走 Sir Kán,但狼群已散 ✓。
  - **「As Balu leaves to die」**——hu.wiki:「Balu, aki érzi halála közeledtét, elbúcsúzik Mauglitól... és elmegy meghalni」(Balu 感到死期將近,與 Maugli 告別後去赴死)✓ **正確**。
  - 第二幕:村裡只有女人在家,**Túna**(村長 **Buldeó** 的女人)開始教他說話、女人們接納他;男人們回來後不歡迎他 ✓;Maugli 在叢林殺了 Sir Kán 並剝下皮 ✓;Buldeó 以巫術指控他、煽動全村,**Túna 站在 Maugli 這邊** ✓;Maugli 折斷 Buldeó 的槍卻不報復,**用 Sir Kán 的皮把 Túna 從 Buldeó 手中贖回來** ✓(Buldeó 當初是花錢把 Túna 買來的);他絕望地明白自己到哪裡都是局外人,而 **Túna 向他發誓忠誠** ✓——生成寫「choosing a future with her even as he recognises that he belongs fully to neither world」完全正確。
- → **不需修改**。

### 27. A Padlás — **OK(逐句對得上)**
- 同樣抓 hu.wikipedia 全文比對:布達佩斯閣樓、控制論學家 **Rádiós** 與他敏感的超級電腦 **Robinson** ✓;隔壁學小提琴的 **Süni** 暗戀他 ✓;四個幽靈 **Herceg / Kölyök / Lámpás / 沉默的 Meglökő** 等 **Révész** 帶他們去「**örökre szépek**」的星球 ✓;**Mamóka** 看得見他們(「只有心像孩子一樣純潔無瑕的人才看得見」)✓;**Témüller** 看不見、只想找碴 ✓。
- **Barrabás** 從屋頂闖入、打昏 Rádiós、逃走時被射殺;回來的身體裡是**借用他形體來體驗人間的 Révész** ✓;**Detektív 與 Üteg** 上門搜捕 ✓;**szilvásgombóc(李子丸子)** ✓;**Varázskönyv** ✓。
- 第二幕:警方限時後要強攻;**Süni 冒險上屋頂接好 Robinson 的天線**、**Rádiós 用機器召來暴風雪逼退直升機** ✓——生成這兩句與 hu.wiki 完全一致;幽靈隨 Révész 離去、Rádiós 認清自己愛 Süni、定時炸彈、Témüller 被捕、Barrabás 向善的靈魂出現 ✓(與 `hungary_triage.md` 的 5 源 ground truth 相符)。
- → **不需修改**。

### 28. Macskafogó — **OK(1 個小抽驗待補)**
- 通過:**M. M. u. 80 年、X 星球、鼠族面臨滅族** ✓;貓幫首腦 **Mr. Fritz Teufel**、**Safranek**、**Lusta Dick** ✓(對上 jozsefattilaszinhaz.hu 官方角色表);**Intermouse** 退休王牌特工 **Nick Grabowski** 是唯一希望 ✓;必須到 **Pokió** 取回 **Fushimishi 教授**的發明「**Macskafogó**(捕貓器)」✓。
- ✅ 那一長串角色**全部查證屬實**(en.wikipedia「Cat City」原片角色表):Bob Poljakoff、Giovanni Gatto、Nero von Schwartz、Maxipocak、Billy、Buddy、Cookie、Pissy、Chino San、Edlington 皆為 1986 動畫的角色。
- ⚠ 只有三個**拼寫**要對齊原片:**Poliakoff → Poljakoff**、**Nero von Schwarz → Nero von Schwartz**、**Maxipotzac → Maxipocak**。(Cicus 未在該表,可留可刪。)

### 29. Légy jó mindhalálig — **OK**
- 通過(對上 `hungary_triage.md` 的 5+ 源與 Móricz 原著):德布勒森的 **Kollégium**、想家又用功的 **Nyilas Misi** ✓;家裡寄來的食物包裹被同學吃光、連鞋油都吃掉 ✓;**Valkay tanár úr** 幫他找到 **Doroghy** 家的家教工作 ✓;為盲眼的 **Pósalaky úr** 讀報 ✓;他傾心 **Bella kisasszony**,而她心繫魯莽的 **Török János** ✓;Pósalaky 託他保管 **lutriszelvény(彩券)**、Török János 拿走彩券並帶著 Bella 私奔 ✓;彩券中獎、嫌疑落到 Misi 身上;Török János 栽贓的十福林紙鈔在他口袋被搜出、被控侵占 ✓;最終真相大白卻已心力交瘁,他告別德布勒森 ✓。

### 30. MADE IN HUNGÁRIA — **OK(我原本以為錯的地方,查完發現生成是對的)**
- 🎯 **主角名 Ricky 是對的**:我手上的 ground truth 來自 2009 電影(主角叫 **Miki**),差點照電影去「修正」。查 jozsefattilaszinhaz.hu 舞台版角色表才確認:**舞台版主角就叫 Ricky**(「Amerika magyarhangja」)。
- 其餘也**逐名對上舞台版角色表**:**Rudi**(糖果師傅/鼓手)、**Csipu**(薩克斯風)、**Tripolisz**(貝斯)、**Kis Nyírő**(義務技師)、**Marina**、**Duci Juci**、**Sampon**(Figaro 樂團主唱)、**Bigali elvtárs**(多功能幹部)、**Vera**、**Röné(csókkirály)** ✓;安傑爾福德(Angyalföld)、從美國回來、樂團與競爭 ✓。
- 📌 教訓寫進 `verify_truth_hungary.md`:**ground truth 要取自「這個製作」**;拿原作/電影當標準去改,會把對的改成錯的。

### 31. A meseautó — **OK(同上,生成用的是舞台版角色)**
- 通過:**Szűcs János**(Központi Bank 總經理)、Horch 780、**Kovács Vera**、隱瞞身分假扮司機好讓她在不知他地位財富下愛上他 ✓(1934 電影 hu.wiki 全文核對)。
- 🎯 生成裡那些「電影查不到」的名字,**全部是 Veres 1 Színház 舞台版的角色**(官方角色表實讀):**Anna kisasszony**(秘書)、**Halmos Aladár**、**Péterffy Tamás**(車行老闆)、**Kovács Sándor**(**糖果店老闆**——生成寫 Vera 出身「modest budai confectioner's family」正確)、**Etel**、**Pityu**(弟弟)、**Stux**、**J.B.** ✓。
- ⚠ 唯一可考慮補的:電影裡的關鍵設定是他安排讓 Vera **以「第一萬名顧客」中獎得到那輛車**(標題「夢幻車」的由來),生成只寫她在車行看車。舞台版官方短文與生成一致,故**不強改**;若要更貼原作可補一句。

### 32. Nikola Tesla – Végtelen energia — **FIX(1 個拼寫)**
- ✅ 角色對上官方卡司公告(deszkavizio.hu / margitszigetiszinhaz.hu):**Szigeti Antal** ✓、**Szigeti Adél** ✓(確實是劇中角色,不是幻覺)、**Thomas Alva Edison** ✓、**George Westinghouse** ✓;場景 Smiljan→布拉格→布達佩斯→巴黎→紐約→芝加哥世博→尼加拉 ✓(官方文案完全一致);**Puskás Telefontársaság** ✓(史實:Tesla 在布達佩斯任職於 Puskás 兄弟的電話公司);母親 **Đuka(Duka)Tesla** ✓、Sarah Bernhardt、晚年的白鴿 ✓(皆為史實)。
- 🚩 **「George Westinghause」拼錯 → Westinghouse**。
- 補記:導演 **Radó Denise**。

### 33. A TRÓN — **OK(1 個拼寫可選)**
- ✅ 角色對上官方卡司(erkelszinhaz.hu / deszkavizio.hu / musicalinfo.hu):**Mátyás(Ember Márk)**、**László(Brasch Bence)**、**Szilágyi Erzsébet(Auksz Éva)**、**Garai(Feke Pál)**、**Garai Anna**、**Cillei Ulrik**、**Frigyes(III. Frigyes)**、**Kunigunda(Podjebrád Kunigunda)**、**Ladislaus / V. László**、Petrus、Zofia ✓;劇涵蓋 **1456-1458**(Hunyadi János 之死到 Mátyás 登基)——生成寫「from the victory at Nándorfehérvár to the election of a new king」正好對上 ✓;László 被處決、Mátyás 被帶往布拉格為質、最後在 **királyválasztó országgyűlés** 被選為國王 ✓。
- ⚠ 可選:劇中角色表拼作 **Jan Griska**,生成寫 Jan Giskra(史實 Jan Jiskra 的匈牙利慣用拼法)。兩者皆通,不強改。
- 補記(更精確的掛名):**編劇 Szente Vajk + Galambos Attila、音樂 Juhász Levente**。

### 34. Mindig itt leszünk... Mohács 500 — **OK**
- 通過:年輕的 **II. Lajos** 明知敵軍強大仍不背棄國家 ✓;與 **Habsburg Mária** 的愛在危局中受考驗 ✓;**II. Ulászló**(父王的遺產)、**Szapolyai János**(內部權力鬥爭)、**Tomori Pál**(軍事決心)✓——全部對上 operett.hu 官方角色與內容;結尾「莫哈奇敗了,但民族存續」✓ 正是官方那句「Bár Mohács elveszett, a magyar nemzet megmaradt」。

### 35. Hogyan tudnék élni nélküled? — **OK**
- ✅ 角色**逐名對上 erkelszinhaz.hu 官方角色表**:**Major Lili**(Csobot Adél)、**Major Döme**、**Major Luca**、**Eszter**(Törőcsik Franciska)、**Gergő**(Ember Márk)、**Kata**、**Betti**、**Gábor**(Marics Péter)、**Csabi**、**Major Márton**(Brasch Bence)✓ 全部存在。
- ✅ 結構對上官方:今昔交錯——現代線(Lili 走不出未婚夫的死、與弟妹清理老家時翻出母親 Eszter 的信與日記)接到 **1990 年代巴拉頓的夏天**;主題「愛、失去與重新開始」✓。
- ⚠ 小 WATCH:樂團名「**Kuplung**」與「**Szigliget 海灘**」不在角色表(場景/團名本來就不會列),沒有第二來源;若要保守可淡化成不指名的樂團與湖畔。

---
## 既有兩部歐陸原創的複查(不在 51 部生成名單內)
### oliver twist(比利時 Deep Bridge)— **維持原簡介,不需改**
- 疑慮:這個 group 的簡介是 2026-08-27「west」批入庫的,內容是 Dickens 原著骨幹(濟貧院出生、要更多食物、Bumble、Sowerberry、Noah Claypole、Artful Dodger、Fagin、Bill Sikes、Nancy),擔心是拿英國《Oliver!》的內容誤掛到比利時製作上。
- 查證(deepbridge.be 官方 show 頁實讀):Deep Bridge 版是**全新法蘭德斯自製音樂劇**(全新音樂),劇情即「19 世紀倫敦的孤兒尋找溫暖、愛與自己在世界上的位置」,官方點名的角色是**狡猾的 Fagin、Dodger、英勇的 Nancy** ✓ 與現有簡介一致,無版本衝突。2.5 小時、6 歲以上;2026-11-06~08 根特試演、2026-12-13 安特衛普首演,另有 Hasselt Trixxo Theater 場。
- → 現有簡介適用,**不動**。(另註:庫中英國/百老匯的《Oliver!》是不同 group `oliver`,兩者沒混。)
### pinocchio musical(義大利 Compagnia BIT)— **前一批已 method B 查證過,不重做**
- 帳本 `data/synopses_verification.json` 記載:2026-08-28,來源含 pinocchiomusicalitalia.it 官方、Teatrionline、Fondazione Teatro Coccia、Musical.it、CulturSocialArt 專訪;`external_multisource: true`。

---
### 【存查】舊 prompt 的捷克 EN 版問題(已重生成,不入庫)
1. Saturnin:Milouš→「Bertie」(《Jeeves》角色)、doktor Vlach→「Doctor Witherspoon」。
2. Edudant:正文夾一行「hdk」(來源 slug)。
成因與修法見上方 16 的說明,`px_gen.py` 的 en prompt 與 slug 規則都已改。

### 16-old. Saturnin(舊版,已作廢)— **FIX(2 個角色名被英文化成別的作品的名字)**
- 通過(cs.wikipedia 小説條目 + postavy.cz + 讀書筆記多源):**teta Kateřina**——守寡十年、為爭奪爺爺的錢無所不用其極、愛用諺語評論一切 ✓(生成「domineering widow who delivers pronouncements through proverbs」完全對);**slečna Barbora**——和善、有活力、現代的女性 ✓;**dědeček**——和善的有錢老先生,顯然樂在看親戚爭產 ✓;伏爾塔瓦河上的**船屋** ✓;移師鄉間別墅、被天候困住、親戚close quarters ✓。
- 🚩 **「her indulged, insufferable son Bertie」→ 應為 Milouš**(teta Kateřina 的兒子;Bertie 是 P.G. Wodehouse《Jeeves》的角色,顯然是被英語化時漂過去的)。
- 🚩 **「the sardonic Doctor Witherspoon」→ 應為 doktor Vlach**(五十歲醫生,愛諷刺與長篇大論、專門發明各種人類行為理論)。
- 成因:en 的 prompt 尾巴要求「using character and place names as used in English-language productions」——捷克/匈牙利這類**沒有英語製作**的劇,這句話會誘導 Perplexity 自行編英文名。往後同批要注意所有非英語劇的人名。

### 17. VY NEJSTE ŽENA, PANE! — **OK(輕微加料)**
- 通過(divadlorb.cz 官方頁角色表實讀):**Milan Kokeš**(Jakub Slach 飾)與 **Libor Náramný**(Ernesto Čekan 飾)✓ 名字完全正確;兩個只想找人相擁的陌生人在匿名交友網約會、發現彼此都是男的 ✓;**確有法庭線**:Žalobce(檢察官,Lukáš Burian)、Obhájkyně(女辯護律師)、Soudkyně(女法官)、Přísedící(陪席)✓;官方定位是「從誤會走向『非比尋常的正確極權(neobyčejně korektní totalita)』的荒謬旅程」,批判當代社會的過度政治正確 ✓——生成的「私人渴望被轉化成意識形態、法律論證與政治籌碼」正是這個意思。
- ⚠ 輕微加料:檢察官「政治生涯乏人問津」的動機、以及「eager journalist」角色未在官方角色表出現;不影響主旨,可留可淡化。

### 18. Zlatovláska — **FIX(2 個編造的國王名 + 1 個相反的結局)**
- 通過:廚師 **Jiřík** 偷嚐蛇肉後聽懂獸語 ✓;被派去為國王求娶金髮公主 ✓;路上救助**螞蟻、烏鴉(幼鳥)、金魚**,還有**蒼蠅(muška)**這位夥伴 ✓(hdk.cz 官方明列這四種動物朋友);公主有一群一模一樣的姊妹(原著十二姊妹)✓;動物朋友在每個難關出手 ✓。
- 🚩 **「King Mojmír」與「King Kazisvět」查無據**:hdk.cz 官方角色表只有「**Otec Zlatovlásky**(金髮公主的父親)」與「**Zlý král**(壞國王)」,兩位國王都沒有名字;cs.wikipedia 的 1973 電影條目同樣只稱「老國王」「金髮公主的父親」。→ **刪掉這兩個名字**,改回官方的稱謂。
- 🚩 **結局寫反**:生成說「Kazisvět, spared a cruel fate, finds a different path to happiness and love of his own」;而原著/1973 電影是**老國王誤用魔法水而死,Jiřík 成為國王並娶了金髮公主**。Karlín 版官方頁未載結局 → 兩種做法:①保守寫到「兩人結合、國王的主張瓦解」為止,不寫國王的下場;②找到 Karlín 版結局的來源再定。**不可保留現在這句無據的「國王另尋幸福」**。

### 19. Edudant a Francimor — **FIX(1 個 slug 殘留)+ 部分待證**
- 通過(hdk.cz 官方頁角色表實讀):兄弟倆是「兩個會魔法的青春期少年」、母親 **paní doktorka Halabába** 忘了送他們上學 ✓;**Matka Halabába / Fena Peggy 由同一位演員分飾**——生成寫「Halabába reappears as Peggy, the canine choirmistress」✓ 命中;**Princezna Róza** 與 **Princezna Růža** 兩位公主 ✓;校外教學去 **Růžový patník** 城堡遺跡 ✓;一路是滑稽場面與奇怪的相遇、最後懂得「世界不一定那麼粉紅(svět nemusí být tak růžový)」✓——生成的收尾「the world beyond their home is stranger… and less 'rosy' than it first seems」正是官方那句雙關。
- 🚩 **正文倒數第二行有一行孤立的「hdk」** = 來源 slug 殘留(hdk.cz)。**入庫前必刪**。已把 `scripts/px_gen.py` 與掃描器的 slug 規則從 3 字元放寬到 2 字元,往後這類三字母縮寫不會再漏。
- ⚠ 待證(官方角色表不完整,未涵蓋):**král Růženín**、發不出「p」音的老師、狗統治的城市、校園霸凌者、走投無路的強盜。若補不到第二個來源 → 保留骨幹、刪去無據的專有名詞。

---
## ZH-HANT 批次(out_zht.json)
> 已知風險:中文版準確度明顯低於英文(見 memory `feedback_zhhans_perplexity_less_accurate`),三語各自獨立查、錯誤不重疊。

### 1. A Christmas Carol(BIT)— **FIX(1 處格式)+ WATCH**
- 通過:平安夜、拒捐、苛待鮑伯・克拉特奇、外甥佛瑞德的邀請、**已逝七年**的馬利鬼魂與鐵鍊錢箱 ✓;三靈依序:**妹妹芬**、**費茲威格**的聖誕舞會、克拉特奇一家與**小提姆**、無人哀悼的死與遭瓜分的財物 ✓;清晨轉變 ✓。全部對得上 BIT 官方 trama 與 Dickens。
- 🚩 **正文中出現「全劇總結」這四個字當成標題單獨一行** → 正是 `project_musicalmap_kb_banking` 警告的殘留,**入庫前必刪**(這是系統性問題,三語全批都要掃)。
- ⚠ WATCH:開頭「**1843年**倫敦的平安夜」——1843 是 Dickens 小説出版年,BIT 官方未指明劇中年份。多數改編確實設在 1840 年代,不算錯,但若要保守可只留「倫敦的平安夜」。

### 2. Alice nel Paese delle Meraviglie — **OK**
- 通過:**十三歲**的愛麗絲、厭倦被催「該長大了」、希望**時鐘停下** ✓(此版特有設定,命中);白兔、毛毛蟲、柴郡貓、瘋帽客茶會、紅心皇后砍頭、審判、鼓起勇氣 ✓;總結「長大不是告別想像力」與官方訊息「永遠不嫌晚決定自己想成為誰」相符 ✓。

### 3. Aggiungi un posto a tavola — 🚩🚩 **FIX(人物關係整組錯,最嚴重一篇)**
- 對照 it.wikipedia 角色表 + 官方:
  - 🚩「酒館老闆**康索萊**」→ **Consolazione 是女性角色**(1974 原卡司 Bice Valori 飾),不是酒館老闆。
  - 🚩「村中青年托托深愛**康索萊的女兒克萊門蒂娜**」→ **雙重錯誤**:①**Clementina 是市長 Crispino 的女兒**,不是 Consolazione 的女兒;②**Clementina 愛的是 Don Silvestro(神父)**,這條「神父獨身 vs 愛情」的線是全劇主軸;③**Totò 愛的是 Consolazione 本人**。
  - 🚩 缺少結局關鍵:**羅馬來的樞機主教**試圖抹黑神父、村民棄他而去,神父仍下方舟與村民同在,洪水因此止息,終場眾人同桌舉杯。
- → 這篇不是「潤一句」能救,**人物關係必須整段改正**(改完仍盡量保留 Perplexity 的句法與語感;若改動後讀起來變成我的文風,重新生成這一部再驗)。
- ⚠ 另:中文劇名「《加多一把椅子》」需查台灣/華語圈是否有既有譯名;查無既有譯名時,依政策不硬翻(標題交由頁面卡片顯示原名)。

### 4. Belle e la Bestia — **OK(繁中比英文版準確)**
- 通過:王子因傲慢化為野獸 ✓;解咒需要「毫無保留、愛他勝過自身一切」的愛 ✓;貝兒偶然踏進城堡、喚醒野獸沉睡的情感、依稀想起公主的面容 ✓;**米格爾**單戀不成、以欺瞞與嫉妒介入 ✓。
- 註:繁中**沒有**犯英文版那兩個錯(沒把貝兒寫成喪偶商人的女兒,也沒編出「貝兒可能就是失落的公主」)——三語各自獨立查是對的。

### 5. C'era una volta... Scugnizzi — **OK(1 個文風問題)**
- 通過:尼西達感化院、二十年後分道揚鑣、街頭神父教孩子音樂、「俄國佬」成為黑幫並利用孩子運送違禁品、殺害薩維里奧、孩子們在悲痛中集結反抗 ✓。
- ⚠ 文風:開頭「**《從前有群街頭少年》以拿坡里為背景,描寫……**」= 書評框架 + 自創中文劇名,違反「直接入戲」策展政策(既有 418 部中 283 部首行不含《劇名》)。→ 改寫第一句直接進場景;華語圈查無既有譯名時不硬翻劇名。

### 6. Forza Venite Gente — **FIX(格式)**
- 通過:亞西西富商之子與父親**伯多祿(Pietro Bernardone)**的衝突 ✓;戰爭、囚禁與病痛後的轉向 ✓;修復破敗小教堂 ✓(史實 San Damiano);放下家產與華服、選擇赤貧 ✓;同伴追隨、**克拉拉(Chiara)**離開優渥家庭 ✓;與狼和解 ✓。
- 🚩「全劇總結」標題殘留。
- 註:比英文版概括(未寫出金髮天使、La Cenciosa、Frate Leone、Sorella Morte),但不算錯。

### 7. FRIDA Opera Musical — **FIX(2 處)**
- 通過:革命後的墨西哥 ✓;**卡翠娜(La Catrina)**穿梭引領 ✓;與**狄亞哥・里維拉**的核心關係與反覆碰撞 ✓;傷殘身體與繪畫 ✓;**沙巴達、托洛斯基、布勒東、蒂娜・莫多蒂**構成時代身影 ✓。
- 🚩 **「政治理想、人體藝術與人體藝術創作彼此激盪」——「人體藝術」重複**(生成瑕疵,語意也不通)。
- 🚩「全劇總結」標題殘留。

### 8. Gloria — **FIX(格式+文風)**
- 通過:懷抱歌手夢的葛洛莉亞、家人的疑慮、愛情、背叛與算計、最終走向屬於自己的成功 ✓;**沒有誤寫成 Tozzi 傳記** ✓。
- 🚩「全劇總結」標題殘留。
- ⚠ 文風:開頭「《Gloria－音樂劇》以懷抱歌手夢的年輕女孩葛洛莉亞為主角」= 書評框架 → 改直接入戲。

### 9. Il ragazzo dai pantaloni rosa — **FIX(結構+版本)**
- 🚩 **結構錯**:「全劇總結」標題殘留,且標題後面接的**不是總結,而是劇情結局**(生日、遊樂園、走下遊樂設施)——等於這篇**沒有總結段**。需重寫收尾或重新生成這一部。
- 🚩 版本問題同英文版:大量電影專屬情節(留級生補習、告白遭拒後失控、派對設局拍羞辱影片、遊樂設施),舞台版是 Piparo/Proia 重新編排的 jukebox musical(新增「成年 Andrea」旁白與音樂老師 Prof. Gioli)。⚠ 另注意:**繁中與英文兩版講的具體情節彼此不同**(英文說教宗合唱團落選,繁中說留級生補習)→ 至少一版是幻覺,兩版都要對舞台版重新校準。

### 10. LUPIN – Il Musical — **OK(同英文版的小加料)**
- 通過:1930 年代、東方快車巴黎→伊斯坦堡開場、艾哈邁德三世鬱金香從保險箱失竊、目的不只是寶石、巴黎孤女伊莎貝爾在巧克力工廠、每日一朵鬱金香 ✓。
- ⚠ 同英文版:把工廠寫成「內裡卻冷漠陰鬱,隱藏著不為人知的陰謀」屬加料(官方只說那是引人遐想之地)。

### 11. Maradona El Diego — **OK**
- 通過:貧困少年、足球是唯一出口、不逐場鋪陳球賽而聚焦「迭戈」這個人 ✓(正好對上官方「不是講足球生涯,而是人性辯護」的定位);拿坡里的宿命聯繫 ✓;**守護拿坡里的聖人聖雅納略以幽默與洞察的視角陪伴凝視** ✓(官方:Lello Arena 飾 San Gennaro,人性而反諷、連接神聖與世俗)。

### 12. Michelangelo da Caravaggio — **FIX(1 處職業)**
- ✅ 重要:繁中的**框架敘事是真的**——「從西班牙塞維亞……喚起往事,將觀眾帶回羅馬」對上外部來源:**Don Fernando 是塞維亞的藝術商人(mercante d'arte),他知道卡拉瓦喬的故事,決定講給自己的一位年輕畫家學徒聽**,由 Fabrizio Rizzolo 飾演。
- 🚩 **「年邁畫家唐・費爾南多」→ 他是藝術商人,不是畫家**(年輕畫家是聽故事的學徒)。
- 🚩 **反過來,英文版第 12 篇把 Don Fernando 寫成「embodies the forces that seek to restrain or exploit the artist」也錯**——他是敘事者。英文版該句一併修。
- 其餘通過:把窮人與妓女畫成聖徒聖母、與教廷權貴的衝突、決鬥後背上死刑判決而逃亡 ✓(史實:殺 Ranuccio Tomassoni)。

### 13. Peter Pan il Musical — **FIX(格式+譯名)**
- 通過:尋回影子、教溫蒂三兄妹飛、小叮噹仙粉、失落男孩要溫蒂當「媽媽」、虎克與斷手/滴答鱷魚、毒藥陷阱、海盜船決戰、虎克敗逃、孩子回家而彼得留下 ✓。
- 🚩「全劇總結」標題殘留。
- ⚠ 譯名:「印地安公主**莉莉公主**」——Tiger Lily 台灣通行譯名是「**虎蓮公主**」;且「印地安」宜改中性說法。
- ⚠ 缺英文版有的開場框架(Cantastorie 在肯辛頓花園),不算錯,可不動。

### 14. Raffaella il Musical — **FIX(同英文版的 2 個無據人名 + 文風)**
- 通過:貝拉里亞→羅馬 ✓;**原名拉斐拉・佩洛尼** ✓(史實 Raffaella Pelloni);古典芭蕾出身、初入藝界的挫折 ✓;母親**伊莉絲** ✓、表姊**娜迪雅** ✓(官方徵選公告確認 NADIA 靈感來自其表姊兼終生好友)、**賈尼・邦孔帕尼** ✓;**《Canzonissima》**的突破 ✓。
- 🚩 **「友人亞歷山德羅・洛・卡西奧」與「電視圈人士喬凡尼・薩爾維」**——與英文版同樣的兩個查無據人名,兩版一起刪。
- ⚠ 文風:開頭「《Raffaella》以……為軸,描繪……」= 書評框架 → 改直接入戲。

### 15. Win for life — **OK**
- 通過:門鈴開場 ✓(且是直接入戲,文風合格);東歐幫傭**蜜拉**、終身每天八千歐、不得透露否則全數歸還 ✓;遊手好閒滿腦子異想天開的丈夫 ✓;信奉瑜伽卻緊盯家中帳目的女兒 ✓;脾氣暴烈的老先生 ✓;放高利貸的毒販 ✓;戴面具行蹤難測的男子 ✓;**合唱團與三名墨西哥流浪樂手(mariachi)不時闖進情節、打斷並攪亂故事** ✓——官方文案全部命中。

### 16. Saturnin — **FIX(與英文版同一個錯:敘事者被冠上作者的姓)**
- 🚩 **「年輕主人吉羅特卡」**——Jirotka 是**作者 Zdeněk Jirotka**,小説的敘事者沒有名字。**英文版與繁中版犯同一個錯**(可見 Perplexity 的幻覺會跨語言重複,不能只靠「三語互比」查證)。
- 其餘通過且音譯正確:**芭芭拉(Barbora)** ✓、**凱瑟琳姨媽(teta Kateřina)**滿口陳腔濫調 ✓、被嬌養的兒子**米洛什(Milouš)** ✓、樂於看熱鬧的**祖父** ✓、言談犀利的**弗拉赫醫生(doktor Vlach)** ✓;擅自搬到**船屋** ✓;鄉間別墅、暴風雨困住親戚 ✓。

### 17. VY NEJSTE ŽENA, PANE! — **FIX(無據組織名 + 文風)**
- 通過:**米蘭・科凱什 / 利博爾・納拉姆尼** ✓;匿名交友網、以為對方是女性、見面才發現都是男的 ✓;急欲出頭的律師兼政治人物把「拒絕與男性約會」包裝成歧視 ✓;檢察/辯護/法官/陪審/記者輪番上陣 ✓;掌權後把言行感情納入規範、操弄者自己也受困 ✓(對上官方「neobyčejně korektní totalita」)。
- 🚩 **「寬容聯盟」= 英文版「Liga tolerance」的中譯,同樣查無據** → 兩版一起改成不指名的說法。
- ⚠ 文風:開頭「《您不是女人,先生!》是一齣以網路交友、性別認同與政治操作為核心的捷克音樂喜劇」= 最典型的書評框架 → 改直接入戲。

### 18. Zlatovláska — **OK(事實全對,只有開頭文風要改)**
- 🎯 **繁中版比英文版正確得多**(同一部劇、三語各查的價值):蛇肉(**不是英文版寫的魚**)✓;伊日克偷嚐後聽懂獸語 ✓;侍酒時聽見鳥兒談起金髮姑娘、國王因此命他去帶她回來 ✓;路上**救下受火威脅的螞蟻、餵飢餓的烏鴉幼鳥、買下金魚放回湖裡** ✓(與 Erben 原著一致);三道難題**草地尋回散落的珍珠、湖底取金戒指、取能決定生死的神奇泉水** ✓(原著三題完全正確);結局**國王貪戀美貌而殘酷處置伊日克,金髮姑娘以神奇之水救回他的性命**,兩人終於相守 ✓(原著:國王砍了 Jiřík 的頭,公主用死水生水救活他)。**沒有編造國王的名字。**
- 🚩 開頭「在卡林音樂劇院的《金髮姑娘》中,……」= 書評框架 + 把劇院名寫進正文 → 改直接入戲。
- 📌 英文版第 18 篇的修正應**以這一版的事實為準**。

### 19. Edudant a Francimor — **FIX(文風)**
- 通過:**圓胖矮小的艾杜丹與高瘦的法蘭奇莫**(原著設定)✓;母親**哈拉芭芭**忘了送他們上學、近成年才當一年級新生 ✓;**玫瑰石柱(Růžový patník)城堡遺址**校外教學 ✓;途中遇盜賊、古怪陌生人、**一座由狗掌權的城市** ✓;結尾「世界不那麼玫瑰色」✓(官方雙關)。
- 🚩 開頭「《艾杜丹與法蘭奇莫》描寫一對……」= 書評框架 → 改直接入戲。
- ⚠ 沒寫到 Král Růženín 與兩位公主(英文版有),不算錯。

### 20. Čarodějnice Bordelína — 🚩🚩 **FIX(人物性格寫反了)**
- 官方(divadlorb.cz):Bordelína 是**搬進 Bambručák 森林、樣樣不滿意、像個稱職的女巫那樣飛快把一切施法改造成自己喜歡的樣子、讓動物和孩子束手無策、惡作劇一個接一個的小叛逆**。
- 生成卻寫成「**有一顆柔軟善良的心,無法對受欺負的人和動物置之不理**」「決定用魔法幫助遇到困難的人」「證明自己並非眾人想像中的邪惡角色」——**把主角的性格與全劇的喜劇動力整個寫反**,主題也變成「接納差異」。
- 也沒提 **Bambručák 森林**與 **Sova Mudrlice / Veverka Drzečka / Zajíc Cyril** 等已證實的角色。
- → 這一部**繁中重新生成**(骨幹錯得太多,不是改幾句能救),再對官方重驗。

### 21. Rebelové — **FIX(文風)+ 1 個小 WATCH**
- 通過:1968 年夏天、捷克邊境小鎮 ✓(這裡沒犯英文版「Kostelec」的錯);**泰瑞莎、布吉娜、尤莉亞、歐達(Olda)** ✓;三名逃兵、**西蒙** ✓;蘇聯入侵終結一切 ✓。
- 🚩 開頭「《叛逆者》把故事放在 1968 年夏天的捷克邊境小鎮」= 書評框架 → 改直接入戲。
- ⚠ WATCH:「暫時**假扮維修工人**藏身」在官方與電影資料都查不到 → 刪掉或改成單純「藏身」。

---
(以下待生成完成後續填:EN 36-51、ZH-HANT 22-51、ZH-HANS 1-51)
