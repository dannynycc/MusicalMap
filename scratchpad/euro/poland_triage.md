# 歐陸原創 — 波蘭 7 部 triage(2026-08-31,逐部留證,不造假)
規則:①真波蘭原創音樂劇→寫三語簡介 ②外國名作在地版→重分類/合併 ③非book musical(gala/演唱會/選秀/致敬秀)→not_musical排除
裁判:波蘭語 wikipedia(pl.wikipedia)/劇院官方+媒體。每部記:判定+來源引文+URL。≥3獨立實讀源。

## 7部清單
1. metro — Metro (華沙 Studio Buffo) — 疑波經典(Józefowicz/Stokłosa 1991)
2. polita — POLITA (華沙 Studio Buffo) — 疑波原創(Pola Negri傳記)
3. bitwa o tron musicalowy talent show — Bitwa o tron. Musicalowy talent show (Teatr Syrena) — ⚠疑選秀talent show→排除
4. paris varsovie le cabaret musical ewunia — PARIS VARSOVIE LE CABARET MUSICAL Ewunia (Kozerki) — ⚠疑cabaret,查
5. serce ze szka musical zen — Serce ze szkła. Musical zen (STUDIO teatrgaleria) — ?
6. musical 1989 — Musical 1989 (Wrocław Hala Stulecia) — 疑波原創(團結工聯1989)
7. musical metro to juz 35 lat — Musical Metro! To już 35 lat! (Lublin) — ⚠疑Metro 35週年gala或=#1 Metro巡演,查(合併or排除)

---
## [1] Metro → ✅KEEP 真波蘭原創(波蘭第一部音樂劇,pl.wiki特色條目)
- 源:pl.wikipedia完整特色條目(Dobre Artykuły)「Metro – polski musical z muzyką Janusza Stokłosy, librettem Agaty Miklaszewskiej i Maryny Miklaszewskiej, wyreżyserowany przez Janusza Józefowicza. Prapremiera 30 stycznia 1991 w Teatrze Dramatycznym w Warszawie... od 1997 w Studio Buffo」+官方metro.studiobuffo.pl+Encyklopedia Teatru Polskiego。1992百老匯Minskoff Theatre、獲東尼獎提名(史上唯一波蘭劇);至2026-06逾2700場。
- 產地=波蘭原創(波蘭第一部音樂劇;音樂Janusz Stokłosa/劇本詞Agata & Maryna Miklaszewska/編導編舞Janusz Józefowicz)。
- ground truth(pl.wiki):一群年輕業餘藝術家在叛逆獨立的藝術家Jan帶領下(對他而言地鐵就是家),被導演Filip在職業音樂劇選角中刷掉;他們索性在劇院旁的地鐵站自辦演出。地下演出大獲成功,Filip回心轉意邀他們加入。年輕人陷入抉擇:追隨金錢與夢想,還是尊嚴?背景交織Jan與Anka的愛情線。結構近《歌舞線上A Chorus Line》《毛髮Hair》,群像+歌舞為主。分幕已足,生成前取核心。
- 相關:pl.wiki頁尾列Stokłosa舞台音樂劇含Metro/Piotruś Pan/Panna Tutli Putli/Romeo i Julia/Polita/Pola Negri→[2]POLITA確認為Stokłosa波蘭音樂劇(關於Pola Negri)。[7]「Musical Metro! To już 35 lat!」疑=Metro 35週年(1991+35=2026)巡演/gala→待查合併or排除。
## [2] POLITA → ✅KEEP 真波蘭原創(Pola Negri傳記音樂劇,pl.wiki)
- 3+源實讀:pl.wikipedia(「Polita – polski musical teatru Studio Buffo w reżyserii Janusza Józefowicza. Kompozytorem muzyki był Janusz Stokłosa. Libretto... Agata Miklaszewska, w oparciu o biografię postaci Poli Negri」)+官方polita-musical.pl+e-teatr.pl。Prapremiera 2011-12-04 Bydgoszcz;世界首部3D音樂劇(Platige Image技術);獲2017韓國大邱音樂劇節Grand Prix。原卡Pola Negri=Natasza Urbańska。
- 產地=波蘭原創(Studio Buffo/Józefowicz-Stokłosa-Miklaszewska同Metro班底;傳記音樂劇)。
- ground truth(概念):波蘭默片影星Pola Negri傳記——一個波蘭女孩如何從家鄉走向好萊塢與國際、成為1920年代默片時代的世界巨星;她傳奇的愛情(如與Rudolph Valentino、Charlie Chaplin)、璀璨與悲劇交織的一生。分幕生成前深讀官方補全。
## [3] Bitwa o tron. Musicalowy talent show → ❌EXCLUDE(talent show競賽format互動秀,非敘事book musical)
- 多源實讀:pl.wikipedia(「Bitwa o tron. Musicalowy talent show. Muzyka: Tomasz Filipczak. Słowa/Scenariusz: Jacek Mikołajczyk. Teatr Syrena. premiera 23 kwietnia 2021」)+IPA Polska PDF(「Pierwszy spektakl w Teatrze Syrena, w którym to widownia decyduje o jego zakończeniu. O głosy zabiega ośmiu królów」=觀眾投票決定結局、八王競逐選票)+Teatr Syrena官方+Kulturonieznawczyni樂評(「Musical? Koncert? Show!」自己都難歸類)+e-teatr。
- 判定:format=「musicalowy talent show」互動競賽revue——八位「國王」以歌競逐王位、觀眾投票決定結局(無固定敘事結局)。屬 flow 明列「選秀」類、非敘事book musical。
- 反面考量(留給使用者覆核):有原創波蘭音樂(Filipczak)+劇本(Mikołajczyk)、Teatr Syrena劇目、pl.wiki列為戲劇作品;但競賽/觀眾投票format不符敘事音樂劇。依使用者 flow「選秀→排除」判EXCLUDE。
- 處置:✅已加 not_musical.json titles「Bitwa o tron. Musicalowy talent show」→build_shows drop。
## [6] Musical 1989 → ✅KEEP 真波蘭原創(rap音樂劇「波蘭版漢密爾頓」,pl.wiki完整頁)
- 源:pl.wikipedia完整頁(「1989 – musical w reżyserii Katarzyny Szyngiery, premiera 2 grudnia 2022 na deskach Teatru im. Juliusza Słowackiego w Krakowie... Muzyka Andrzej Mikosz, Słowa Marcin Napiórkowski, Scenariusz Napiórkowski/Szyngiera/Wlekły」)+多篇press(Vogue Polska「Polski Hamilton」、Onet、Polityka五星、e-teatr)。世界首演2022-11-19 Gdański Teatr Szekspirowski;獲Paszport Polityki、Nagroda Wyspiańskiego;專輯2024獲Fryderyk。我方Wrocław Hala Stulecia=巡演場。
- 產地=波蘭原創(受百老匯《Hamilton》啟發的波蘭rap音樂劇;音樂Andrzej "Webber" Mikosz/劇本詞Marcin Napiórkowski等)。
- ground truth(pl.wiki):時間1980–1989(含1950年代回溯),描繪波蘭反共民主派的奮鬥——1980年八月大罷工、戒嚴、華勒沙(Lech Wałęsa)由妻子Danuta代領諾貝爾和平獎、Magdalenka密談、圓桌會議。主線為幾對夫妻:Frasyniuk夫婦、Kuroń夫婦、華勒沙夫婦、Alina Pienkowska與Bogdan Borusewicz。以rap/hip-hop頌團結工聯與波蘭和平轉型。分幕已足,生成前取核心。
## [7] Musical Metro! To już 35 lat! → 🔁合併進[1]Metro(同一部,35週年巡演)
- 多源實讀:eBilet(「Musical Metro ma już 35 lat - bilety na jubileuszową trasę... Legendarny musical 'Metro' to wizytówka repertuaru Studia Buffo」)+artbilet(巡演場次:29.11.2026 Lublin/23.01.2027 Tarnów/20.02.2027 Katowice/06.03.2027 Gdańsk/15.05.2027 Poznań)+KupBilecik+biletyna+Facebook Studio Buffo(前有「Metro ma już 30 lat」同型週年巡演)。
- 判定:=同一部 Studio Buffo《Metro》音樂劇的35週年紀念巡演(非另一作品、非gala concert;是完整劇目巡演)。
- 處置:✅已加 works.json canonical「Metro」+alias「Musical Metro! To już 35 lat!」(tradition=歐陸原創)→build_shows 併入[1]Metro同組。資料集僅此兩筆Metro皆波蘭Studio Buffo,無誤併風險。簡介沿用[1]Metro(canonical group=metro)。
## [4] PARIS VARSOVIE LE CABARET MUSICAL Ewunia → ❌EXCLUDE(雙語音樂卡巴萊/演唱會revue,非book musical)
- 多源實讀:PolskieGranie(「Dwujęzyczny spektakl muzyczny, który łączy piosenkę」)+eBilet(「Na jednej scenie spotykają się paryski wróbelek Edith Piaf oraz obłędna Kalina Jędrusik」)+Facebook Hotel Kozerki(「dwujęzyczny spektakl muzyczny, w którym francuski szyk spotyka polską duszę」)+cojestgrane/kapele.net(單場2026-08-30 Kozerki)。
- 判定:標題即「LE CABARET MUSICAL」;內容=把Edith Piaf(法語)與Kalina Jędrusik(波語)歌曲並陳的雙語歌曲revue/卡巴萊;場地Kozerki Sport&Business/網球學院(單場活動,非劇院常態劇目)。非敘事book musical→flow卡巴萊/演唱會/致敬秀類。
- 處置:✅已加 not_musical.json titles「PARIS VARSOVIE LE CABARET MUSICAL Ewunia」→build_shows drop。
## [5] Serce ze szkła. Musical zen → ✅KEEP 真波蘭原創(前衛實驗音樂劇)
- 5+源實讀:Teatr w Krakowie im. Słowackiego(「koprodukcja ze STUDIO teatrgalerii w Warszawie. Libretto: Klaudia Hartung-Wójciak, Maria Peszek; Reżyseria: Cezary Tomaszewski」)+e-teatr(「na podstawie 'Naku*wiam zen' Marii Peszek oraz 'Królowej Śniegu' Hansa Christiana Andersena」)+krytyczne-spojrzenie(「oparty na autobiograficznych wątkach z życia Marii Peszek i Jana Peszka」)+biletomat+Dzieje.pl+Teatr Studio官方。2024首演STUDIO teatrgaleria華沙。
- 產地=波蘭原創(前衛/實驗音樂劇「Musical zen」;libretto Klaudia Hartung-Wójciak & Maria Peszek、導演Cezary Tomaszewski;取材Maria Peszek書《Naku*wiam zen》+安徒生《冰雪女王》+Peszek家族自傳)。billed為Musical、有libretto/音樂/常態劇目→非gala/演唱會,屬正規音樂劇作品。
- ⚠劇情:前衛作品,非線性敘事——一場對空虛、身體、愛、「昔與今的波蘭」的不可預測、放縱又溫柔的冥想,以《冰雪女王》為母題交織Maria Peszek自傳。生成前深讀官方；勿硬編線性分幕,如實反映其實驗/冥想性質。

---
# ✅ 波蘭 7/7 triage 完成(2026-08-31)
- ✅真波蘭原創(4):Metro、POLITA、Musical 1989、Serce ze szkła. Musical zen
- 🔁合併(1):Musical Metro! To już 35 lat! → 併入Metro(works.json canonical「Metro」+alias)
- ❌排除(2):Bitwa o tron(選秀競賽format)、PARIS VARSOVIE LE CABARET MUSICAL Ewunia(雙語卡巴萊/演唱會)
- 待寫三語簡介:4部真波原創(Serce ze szkła前衛,生成前深讀勿硬編)。
