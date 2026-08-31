# 歐陸原創 — 北歐+比利時+土耳其+中國 剩餘 triage(2026-08-31,逐部留證,不造假)
規則:①真歐陸原創音樂劇→寫三語簡介 ②外國名作在地版→重分類/合併 ③非book musical(gala/演唱會/選秀/致敬秀)→not_musical排除
裁判:當地語 wikipedia(no/sv/nl/da/tr)/劇院官方+媒體。≥3獨立實讀源。

## 清單(跨國group「Night of Famous Musicals」挪威+芬蘭同一筆)
挪威:1.Europavisjonar 2.Änglagård 3.Pippi på sirkus 4.Prosjekt Prøysen 5.Night of Famous Musicals(=芬蘭同筆)
瑞典:1.Emil i Lönneberga 2.Ronja Rövardotter 3.Så som i himmelen
比利時:1.Oliver Twist 2.De Spiekpietjes 3.The Count of Monte Cristo
丹麥:1.Et Juleeventyr 2.The Julekalender 3.Ternet Ninja
土耳其:1.Efkan Şeşen 2.Paris! The Show
中國:1.玩偶(上海;⚠tag歐陸原創疑誤植,查)

---
## [挪威5 / 芬蘭1] Night of Famous Musicals → ❌EXCLUDE(名劇金曲gala巡演音樂會,跨國同一group)
- 多源實讀:Instagram negar.zarassi(「Night of Famous Musicals is returning with its biggest Swedish tour so far, bringing hits from Les Misérables, The Phantom of the Opera...」)+Instagram shimi_goodman(「Musical Director for Night of Famous Musicals (Scandinavian Tour)... London Concert Orchestra」)+NORDIC CURTAIN CALL(北歐巡演,含Wicked等)。
- 判定:串唱Les Mis/Phantom/Wicked等名劇金曲的巡演音樂會/gala,非敘事book musical→flow gala/演唱會/致敬秀類。同一group橫跨挪威(Lillehammer/Oslo)+芬蘭(Lahti)——排除title即涵蓋兩國(此即72 vs 73計數差來源)。
- 處置:✅已加 not_musical.json titles「Night of Famous Musicals」→build_shows drop。
## [土耳其1] Efkan Şeşen → ❌EXCLUDE(土耳其歌手個人演唱會,非音樂劇)
- 3+源實讀:Biletix(「MÜZİK · Alternatif · Efkan Şeşen. 16 Eki 2026, Kadıköy Sahne, İstanbul」)+Instagram kadikoy.sahne(「Efkan Şeşen, 1963 İstanbul doğumlu... Türk besteci, müzisyen ve eski Grup Yorum solistidir」)+Facebook/Instagram官方(「Efkan Şeşen Konseri」多場)。
- 判定:Efkan Şeşen=土耳其創作歌手/音樂家(前Grup Yorum主唱),資料條目=其個人演唱會(標題即歌手本名)。非音樂劇,tag歐陸原創誤植。
- 處置:✅已加 not_musical.json titles「Efkan Şeşen」→build_shows drop。
## [挪威1] Europavisjonar → ✅KEEP 真挪威原創(政治諷刺音樂劇,Det Norske Teatret)
- 5+源實讀:Det Norske Teatret官方(「Ein Eurovision-musikal! Premiere 1. mars 2025... av Simen Formo Hay, Johan Hveem Maurud og Oda Radoor. Regissør Simen Formo Hay, Musikkansvarleg Benjamin Giørtz」)+Aftenposten(「7 og stående applaus」)+NRK(「Ein genistrek... Douze points」)+Dagsavisen(「musikalsk, satirisk og politisk genistrek」)+Heddaprisen 2025(最佳舞台與服裝設計)。
- 產地=挪威原創(挪威語原創音樂劇;創作/導演Simen Formo Hay等,國家級Det Norske Teatret,獲挪威劇場獎Heddapris)。約3小時。
- 判定要點(對比波蘭Bitwa o tron排除):Europavisjonar雖有觀眾投票橋段,但為完整劇本音樂劇——貫穿1989柏林圍牆倒塌至今的歐洲政治史敘事、大量真實政治人物角色、原創音樂、獲主流劇評與Heddapris肯定為「政治音樂劇場」→屬正規book musical KEEP;波蘭那部為純競賽talent-show format故排除。
- ground truth(官方):以「歐洲歌唱大賽」為框架的政治諷刺音樂劇——從柏林圍牆倒塌至今的歐洲各國元首(Merkel、Blair、Jeltsin、Erdoğan、Le Pen、Putin、Trump、Macron、Zelensky、Stoltenberg等)以歌舞、亮片與華服競演各自的「歐洲願景」,串起glasnost、90年代市場自由化、金融危機、難民危機、戰爭與和平;由觀眾投票選出勝利願景。對民主的華麗諷刺與致敬。分幕生成前取核心。
## [挪威4] Prosjekt Prøysen → ❌EXCLUDE(teaterkonsert劇場音樂會/致敬,非book musical)
- 5+源實讀,一致billed「teaterkonsert」無一稱musikal:Facebook Øyvind Risvik(「Prosjekt Prøysen er en varm, sterk, til tider rocka... teaterkonsert med kjente Prøysen-karakterer og sanger」)+全名「PROSJEKT PRØYSEN RAK SOM ET LYS UNDER STORGRANA - en teaterkonsert basert på stubber og viser av Alf Prøysen」+Teater Ibsen/egalteater(「EIN TEATERKONSERT MED STUBBAR OG VISER AV ALF PRØYSEN」)+Visit Sjusjøen+Teater Innlandet。
- 判定:format=teaterkonsert(劇場音樂會)——串演挪威創作歌手Alf Prøysen歌曲與小品(viser og stubber)的致敬音樂會;有劇場框架但非敘事book musical。屬flow演唱會/致敬秀類。
- 處置:✅已加 not_musical.json titles「Prosjekt Prøysen」→build_shows drop。
## [挪威2] Änglagård → ✅KEEP 歐陸原創(瑞典原創音樂劇;Oslo為巡演場,作品產地=瑞典)
- 3+源實讀:Instagram bobbiloproduktion(「Änglagård – The Musical (the hit stage adaptation of the classic 1992 film)」巡演)+Instagram amka_nordic(「the hit Swedish musical Änglagård—based on the classic 1992 Colin Nutley [film]」)+Det Ny Teater/Malmö Opera提及(「musicalen Änglagård på Oscarsteatern」)。
- 產地=瑞典(改編自1992瑞典經典電影《Änglagård》[導演Colin Nutley],瑞典音樂劇,斯德哥爾摩Oscarsteatern首演;巡演至Oslo→我方country標挪威是巡演場地,作品本體=瑞典原創)。tradition tag 歐陸原創正確。
- ⚠註:country顯示挪威(Oslo venue),但簡介應寫明瑞典原創/瑞典電影源;作曲/改編團隊生成前確認。
- ground truth(1992電影概念):都會來的年輕女子Fanny(歌舞演員)與她張揚的同志好友Zac,繼承了瑞典鄉間保守小村的一棟農舍;兩人不羈的生活方式震撼了心胸狹隘的村民,由衝突到理解,叩問寬容與偏見。分幕生成前深讀補全。
## [挪威3] Pippi på sirkus → ✅KEEP 歐陸原創(瑞典原創馬戲音樂劇,Björn Ulvaeus音樂;Oslo挪威語版)
- 5+源實讀:Det Norske Teatret官方(「Sirkusregissør Tilde Björfors... Pippi på sirkus」)+NRK樂評(2026-04-22)+Aftenposten樂評(「sprudlende teaterfest der musikk, akrobatikk og sceneglede」)+ABBA Intermezzo(「The Norwegian version of 'Pippi at the Circus'... premiere 18 April 2026 at Det Norske Teatret in Oslo」+Björn Ulvaeus參與)+Filmkunst Musikverlag(「World premiere of the musical 'Pippi på cirkus'... Astrid Lindgren Company... in Stockholm」)。
- 產地=瑞典(音樂Björn Ulvaeus[ABBA]、與Astrid Lindgren Company合作、改編Astrid Lindgren《長襪皮皮》、瑞典斯德哥爾摩世界首演;挪威語版於Oslo Det Norske Teatret→我方country標挪威是該語製作場)。tradition tag 歐陸原創正確。
- ⚠註:country顯示挪威(Oslo),簡介應寫明瑞典原創(Lindgren源+Björn Ulvaeus音樂)。
- ground truth(Lindgren原著馬戲篇):力大無窮、特立獨行的紅髮女孩Pippi(獨自住在亂糟糟別墅、養著一匹馬和猴子Nilsson先生)帶朋友Tommy與Annika去看馬戲團;她輕鬆擊敗馬戲團大力士、以頑皮與歡樂攪亂演出,張揚自由與力量。Björn Ulvaeus譜曲的馬戲音樂劇。分幕生成前深讀補全。

---
# 挪威 5/5 完成:✅KEEP 3(Europavisjonar挪原創、Änglagård瑞典原創、Pippi på sirkus瑞典原創) ❌EXCLUDE 2(Prosjekt Prøysen teaterkonsert、Night of Famous Musicals gala[跨芬蘭])
## [瑞典1] Emil i Lönneberga → ✅KEEP 真瑞典原創(家庭音樂劇,Astrid Lindgren)
- 3+源實讀:2Entertain(「Denna musikal baserad på Emil i Lönneberga blandar nostalgi och värme med fartfylld show」)+Showtic(「Höstens familjemusikal... Intiman, Stockholm 19 sep.-29 nov.」)+Teater Bristol(「originalmanus av Astrid Lindgren」)+Via TT(2026-04「Astrid Lindgrens älskade berättelser blir en fartfylld familjemusikal」)+Intiman。
- 產地=瑞典原創(瑞典家庭音樂劇;改編Astrid Lindgren經典《Emil i Lönneberga》;2Entertain製作於Intiman斯德哥爾摩)。音樂多沿用Georg Riedel經典Emil曲(生成前確認)。
- ground truth(Lindgren原著):20世紀初瑞典Småland的Katthult農莊,調皮卻善良的小男孩Emil成天闖禍(hyss)——把頭卡進湯盆、把妹妹Ida升上旗桿……每次都被父親罰去木工房刻小木人;儘管淘氣,Emil心地善良(著名的救濟窮人院橋段)。角色有妹妹Ida、母親Alma、長工Alfred、女僕Lina。溫暖懷舊的瑞典閤家歡。分幕生成前深讀補全。
## [瑞典3] Så som i himmelen → ✅KEEP 真瑞典原創(音樂劇,改編Kay Pollak 2004電影)
- 5+源實讀:Via TT(「Musikalen 'Så som i himmelen' är skapad av Kay Pollak, Carin Pollak och Fredrik Kempe, och är baserad på Kay Pollaks succéfilm från 2004」)+Lorensbergsteatern官方/Facebook(「Musikalversionen baserad på Kay Pollak ikoniska film」)+Showtic(「En hjärtevärmande musikal... Lorensbergsteatern, Göteborg」)+Instagram christopherwollter(Teater Satelliten「MUSIKALEN SÅ SOM I HIMMELEN av KAY POLLAK, CARIN POLLAK och FREDRIK KEMPE」)+2Entertain+Malmö Opera。
- 產地=瑞典原創(音樂劇;創作Kay Pollak/Carin Pollak/Fredrik Kempe;改編Kay Pollak 2004奧斯卡提名瑞典電影《Så som i himmelen》)。哥德堡Lorensbergsteatern。
- ground truth(2004電影概念):世界知名的國際指揮家Daniel Daréus心臟病發後,返回瑞典北方童年小村休養;他成為當地教會唱詩班的領唱,以音樂逐漸改變村民的生命——喚醒他們的愛、勇氣與自我價值(含受虐妻子Gabriella藉〈Gabriellas sång〉找回自己的聲音),卻也面對僵固牧師與小鎮壓抑的張力。關於音樂療癒與解放力量的動人故事。名曲〈Gabriellas sång〉。分幕生成前深讀補全。
## [瑞典2] Ronja Rövardotter → ✅KEEP 真瑞典原創(家庭音樂劇,Astrid Lindgren/Björn Isfält)
- 3+源實讀:Showtic(「Ronja Rövardotter är baserad på Astrid Lindgrens bok med samma namn. Musik: Björn Isfält, Dramatisering och regi: Kålle Gunnarsson」)+Instagram Lorensbergsteatern(「ASTRID LINDGRENS Ronja Rövardotter, REGI: Kålle Gunnarsson, PREMIÄR 19 DEC」)+2Entertain/Facebook(「I jul väcks Astrid Lindgrens älskade klassiker till liv på Lorensbergsteatern. Följ Ronja på hennes modiga resa genom Mattisskogen」)+Göteborgs Stadsteater。
- 產地=瑞典原創(瑞典家庭音樂劇;改編Astrid Lindgren《Ronja Rövardotter大盜的女兒羅妮亞》,音樂Björn Isfält[經典1984電影配樂者]、改編導演Kålle Gunnarsson)。哥德堡Lorensbergsteatern 2026-12-19首演。
- ground truth(Lindgren原著):強盜首領Mattis之女Ronja在雷電將城堡劈成兩半的暴風夜出生,自由地在充滿危險(rumphobbar、vildvittror等)的Mattis森林長大;她與宿敵強盜幫Borka之子Birk結為好友,兩人的友誼違逆世仇父輩,最終離家自居森林、化解兩幫世仇。關於友情、自由與自然超越世襲仇恨的成長故事。分幕生成前深讀補全。

---
# 瑞典 3/3 完成:✅KEEP 全3(Emil i Lönneberga、Ronja Rövardotter、Så som i himmelen,皆瑞典原創)
## [比利時1] Oliver Twist → ✅KEEP 真比利時(法蘭德斯)原創(Deep Bridge自製,公版Dickens)
- 5+源實讀:Deep Bridge官方(「In het najaar van 2026 brengen we een gloednieuwe Vlaamse musicalversie van de tijdloze klassieker van Charles Dickens」)+Musicalnieuws.nl(「Deep Bridge presenteert een gloednieuwe, eigen Vlaamse musicalversie van... 'Oliver Twist'」)+Chez Bartizze(「'Oliver Twist, de Musical' speelt vanaf 6 november 2026 in Capitole Gent (try-outs), Stadsschouwburg Antwerpen (première 13 december 2026)」)+toneelschrijver.be(「volledig nieuwe Vlaamse musicalversie van Charles Dickens' 'Oliver Twist'」)+Cultuurmania。
- 產地=比利時原創(法蘭德斯Deep Bridge全新自製音樂劇「eigen Vlaamse musicalversie」;改編公版Charles Dickens《孤雛淚》)。同義大利[6]Christmas Carol型:在地自製+公版文學源→KEEP。作曲/創作團隊生成前確認。
- ground truth(Dickens原著):維多利亞時代的孤兒Oliver Twist逃離濟貧院與殘酷學徒生活,流落倫敦誤入Fagin的少年扒手幫(機靈鬼Dodger等);夾在犯罪地下世界(Bill Sikes、Nancy)與更好人生的盼望之間,最終憑真實身世與善心恩人獲救。法蘭德斯原創音樂劇treatment,分幕生成前深讀補全。
- 線索:Deep Bridge亦製作其他法蘭德斯音樂劇(De Tovenaar van Oz/Peter Pan/Roodkapje);[比利時3]Count of Monte Cristo可能亦Deep Bridge/法蘭德斯自製,後續查。
## [比利時2] De Spiekpietjes → ✅KEEP 歐陸原創(荷語兒童音樂劇;⚠來源薄,生成前須驗或標無法查證)
- 源實讀(較薄):Instagram kattendans/hetpaashuis(「De spiekpietjes hebben nu een musical. Ze nemen ons mee naar het fabriek want daar werken ze. Maar ohjee alle kindjes zijn te braaf geweest...」)+entracte.kcb(「Spiekpietjes Academy」)+Bloggen.be。我方venue=Hasselt(比利時)。
- 產地=歐陸原創(荷語/法蘭德斯兒童音樂劇;基於Spiekpietjes=聖尼可拉斯的「偷看小精靈」helper角色concept;有工廠設定敘事+歌曲,billed musical)。Spiekpietjes concept在荷蘭與法蘭德斯皆有,我方Hasselt→歸比利時合理。
- ⚠劇情細節薄+來源多為小型兒童劇場IG:非gala/演唱會(是有故事的兒童音樂劇故KEEP不排除),但生成前**必找≥3可靠源**確認劇情+創作團隊;查不到=標「無法查證·不寫」,絕不硬編。可能是低知名度兒童品牌劇。
- ground truth(概念,暫):Spiekpietjes在工廠工作(製作/準備聖尼可拉斯禮物?),因孩子們都太乖而引發的閤家歡兒童冒險——待生成前查證補全,不確定不寫。
## [比利時3] The Count of Monte Cristo → 🔁重分類=法式音樂劇(La Légende de Monte-Cristo,法國原創;Forest National為巡演場)
- 多源實讀:Forest National官方(「Monte-Cristo, Le Spectacle Musical... Show in French... 10.10.2026」)+官方站montecristolespectacle.fr(「Monte-Cristo, le spectacle musical | Aux Folies Bergère et en tournée」)+BroadwayWorld(「« La Légende de Monte-Cristo, le Musical » est une adaptation」)+Ticketmaster BE+Facebook官方(3.5萬追蹤,Forest National Bruxelles場次)。
- 判定:=法國音樂劇《La Légende de Monte-Cristo, le spectacle musical》(法語演出、巴黎Folies Bergère、改編大仲馬《基督山恩仇記》),巡演至布魯塞爾Forest National;我方country比利時是巡演場,作品產地=法國。
- 處置:✅已把 works.json 既有 canonical「The Count of Monte Cristo」(原aliases含「LA LEGENDE DE MONTE-CRISTO, Le Musical」「基督山伯爵 中文版」等)tradition 由「歐陸原創」改為「法式音樂劇」→build_shows 會把本Belgium entry及綁定的中文版一併重標法式。簡介沿用既有Monte Cristo group。
## [丹麥2] The Julekalender → ✅KEEP 真丹麥原創(聖誕音樂劇,De Nattergale)
- 4+源實讀:da.wikipedia(「The Julekalender er en dansk julekalender fra 1991, skrevet og instrueret af Hans-Erik Saks og komikergruppen De Nattergale」)+tvSyd(「Musikteater for unge og voksne... 120 min med pause. Lion Entertainment ApS」)+Teateravisen(丹麥各劇院聖誕檔)+KOP kultur(「THE JULEKALENDER... juleforestilling」)+Aalborg Teater/Tivoli。
- 產地=丹麥原創(丹麥聖誕音樂劇/musikteater;基於1991丹麥經典聖誕影集,喜劇團體De Nattergale創作;含招牌歌Støvle Dance)。
- ground truth(1991影集概念):三個「nisser(聖誕精靈/地精)」Hansi、Günther、Fritz是碩果僅存的好精靈,必須從美國返回丹麥尋回古老的聖誕之書、拯救聖誕與自身存續,因為邪惡的Krybbenisser(如Benny/Gammel Nok與Kartoffelwoman)威脅他們滅絕;以丹麥語與蹩腳英語混雜的招牌喜劇風。分幕生成前深讀補全。

## [丹麥1] Et Juleeventyr(Det Ny Teater, Balletsalen)→ ❌EXCLUDE(獨角戲 monolog,非音樂劇)
- 3+源實讀:Det Ny Teater官方頁(全名「Et Juleeventyr – En magisk monolog」;Jan Hertz導演/概念、Lars Kaaber改編Dickens文本、Kim Hammelsvang一人飾20+角、Troels Kaaber僅「lyddesign og komponist」音景設計、60分鐘無中場、7歲以上闔家)+Ungt Teaterblod劇評(「har nu omsat historien til en monolog」「Der er 20 karakterer i fortællingen, og Kim Hammelsvang spiller dem alle」,通篇無歌曲/musical字樣)+HAVE Kommunikation新聞稿(售罄加演,billed為juleforestilling非musical)+scenen.dk/teaterbilletter.dk條目同名「En magisk monolog」。
- 判定:形式=單人說書式獨角戲(monolog),音樂僅為氛圍音景設計,無歌唱敘事→符合flow③非book musical(獨角秀)排除。與義大利[6]A Christmas Carol(真音樂劇)不同,勿混淆。
- 處置:✅已加 not_musical.json titles「Et Juleeventyr」→build_shows drop。

## [丹麥3] Ternet Ninja(Ternet Ninja Live)→ ✅KEEP 真丹麥原創音樂劇
- 4+源實讀:Iscene(2026-03-31,「En helt ny og unik dansk musical, der sprænger rammerne for, hvad man kan forvente af genren」;創作團隊Clemens Telling[概念/共同製作/改編劇本]、Sargun Oshana[導演]、Steen Koerner[編舞]、Benjamin La Cour[舞台設計]、Jeppe Lawaetz[燈光];Thomas Volmer與Clemens Telling合作創作原創音樂,與既有名曲並用)+Nordjyske(「Anders Matthesens ternede ninja bliver til musical」;原著2016小說→2018動畫電影[25年來丹麥戲院最多人看的丹麥電影,逾90萬張票]→舞台)+migogkbh(同團隊曾製作「Terkel – The Motherfårking Musical」;2027-05-06 Tivoli Koncertsalen首演,巡演Odense/Holstebro/Esbjerg/Randers/Aalborg/Vejle/Viborg後回Tivoli演至2027-07-25)+Tinghallen/Musikteatret Holstebro巡演頁+nyheder.dk。
- 產地=丹麥原創(丹麥語原創音樂劇;改編Anders Matthesen丹麥國民IP《Ternet Ninja》;原創音樂Thomas Volmer+Matthesen名曲Pesto/Jessicas sang/Verdens bedste)。我方場次=Aalborghallen 2027-06-16~20 巡演站,tradition 歐陸原創(country Denmark fallback)正確,不需註冊works.json。
- ground truth(原著/電影):被霸凌的少年Aske收到叔叔從泰國帶回的格紋忍者玩偶,玩偶竟然活了——裡頭住著慘死泰國血汗工廠男孩的靈魂,一心復仇;一人一偶展開暴力又爆笑的復仇之旅,同時Aske得面對校園霸凌者、暗戀的Jessica與自己的懦弱。角色:Aske、Jessica、Glenn、Sune、Stewart Stardust等。分幕生成前深讀補全。

## [土耳其2] Paris! The Show(Zorlu PSM)→ ❌EXCLUDE(法式香頌卡巴萊致敬秀,非book musical)
- 3+源實讀:Anadolu Ajansı法文版(「porte la signature du célèbre metteur en scène Gil Marsalla」;卡巴萊形式、現場樂團、唱Édith Piaf/Charles Aznavour/Jacques Brel/Joséphine Baker等既有名曲;三位演唱者Josephine Cocolletto、Stephanie Impoco、Jules Grison;「plus de 600 représentations et attiré plus d'un million de spectateurs dans le monde entier」)+Yabangee(「vibrant stage production celebrates the culture, art, music, and style of Paris」,live music+dance+theatrical storytelling)+Zorlu PSM月報導/Eventmag節目表(歸類音樂演出)。
- 判定:Gil Marsalla(亦製作「Piaf! The Show」——本清單既有排除項)出品的法國巡演香頌致敬秀:無原創曲、無book劇本,以名曲串接+卡巴萊敘事框架→符合flow③排除(致敬秀/卡巴萊)。旁證:not_musical.json 既有「Piaf! The Show」同製作方同格式。
- 處置:✅已加 not_musical.json titles「Paris! The Show」→build_shows drop。

---
# 丹麥 3/3 完成:✅KEEP 2(The Julekalender、Ternet Ninja) ❌EXCLUDE 1(Et Juleeventyr 獨角戲)
# 土耳其 2/2 完成:❌EXCLUDE 2(Efkan Şeşen 演唱會、Paris! The Show 卡巴萊致敬秀)
