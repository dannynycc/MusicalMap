# 變更紀錄 CHANGELOG

> 時間一律為**台北時間 (UTC+8)**。每次 commit 前先跑 `Get-Date -Format "yyyy-MM-dd HH:mm"` 取真實時間再寫。
>
> **版號規則 (語意化版號 vMAJOR.MINOR.PATCH)**
> - **PATCH** `+0.0.1`：bug 修正、資料/scraper 修正、文案、小調整
> - **MINOR** `+0.1.0`：新功能、新資料來源、UI 大改
> - **MAJOR** `+1.0.0`：架構大改版或不相容變更
>
> 每次 push 到 main 都要打對應的 git tag（與本檔版號一致）。

---

## [v0.38.0] - 2026-06-14 17:38
### 變更(個人頁 u.html UI 精緻化)
- 公開個人頁「精緻淺色」polish(純 CSS,沿用既有 FlightRadar 橘色調性、不動 JS/結構):霜面 sticky header、左錨大標題 hero(漸層字 + 強調線)、pill 分頁、數據條/彩色圖卡圓角加深 + hover 上浮、地圖圓角 16px、log 卡片 hover 上浮 + 海報縮圖陰影、層次柔陰影與平滑過場、行動版置中。

## [v0.37.5] - 2026-06-14 17:32
### 修正(個人頁海報縮圖對不上)
- **Roméo et Juliette(及一整類)在 u.html/me 個人頁看不到海報縮圖**。根因:catalog 的 `en` 取 group 第一個 show 的 title,而 bilingual 會把 canonical 串在原文前(「Roméo et Juliette Again, Romeo & Jeliet」「Gutenberg! The Musical! Gutenberg, el mejor…」),u.js 用 `en.toLowerCase()` 當海報 key,使用者記的標準劇名就對不上 → 無縮圖。
- **修法**:gen_catalog 改為 **registered 作品的 `en` 直接用 works.json 的 canonical**(乾淨、可比中);原標題仍進 `search` 維持可搜。Roméo→livenation 海報、Jeliet→自己的 interpark 海報、title 也拆開。
- (附帶)`Again, Romeo & Jeliet` 拆出後 catalog 一直沒重生,故此前殘留串接——本次一併修正並重生。

## [v0.37.4] - 2026-06-14 17:16
### 修正(大邱 DREAM HALL 城市/座標 + 根因)
- `Again, Romeo & Jeliet` 場館修正:NOL/interpark 把**未知場館一律預設 Seoul**(interpark.py line ~130),導致大邱的 DREAM HALL 被擺到首爾。查證:DREAM HALL = 478 Apsansunhwan-ro, Nam-gu, Daegu(대덕문화전당)。
  - **現有資料**:overrides.json 加 `ip-26007357` → city=Daegu、lat/lng=35.8331/128.5835。
  - **根因**:interpark.py VENUES 表新增 `dream hall` → Daegu,未來自動掃也正確(非首爾場館需列入此表才不會被預設 Seoul)。
- archive 重置(1296 runs)。

## [v0.37.3] - 2026-06-14 17:06
### 修正
- **`Again, Romeo & Jeliet` 改回韓國原創**(原誤判為法式)。用戶查證:這是大邱本土原創中小型音樂劇(90 分、₩50,000、刻意拼「Jeliet」做區隔),非法語引進的大型《Roméo et Juliette》。移除 works.json 中的錯誤別名。
- **更正 `londontheatre.co.uk` 分潤歸屬**(查證後):它屬 **TodayTix Group**(非 ATG、非 London Theatre Direct),抽成要走 **TodayTix via Impact(~1-2%)**,不是 Awin。更新 `docs/AFFILIATE_SETUP.md` 第 3 節與 app.js `AFFILIATE` 註解;策略上西區高報酬仍是 ATG(已有 238 連結)。
- archive 重置保持乾淨(1296 runs)。

## [v0.37.2] - 2026-06-14 16:58
### 文件
- `docs/AFFILIATE_SETUP.md`:ATG(Partnerize)與 LondonTheatre(Awin)補上逐步申請步驟(註冊→填料→收款/稅表→驗證→申請計畫→核准後拿 camref / awinmid+awinaffid)。註明 Awin 需約 US$5 可退押金、以及先確認 londontheatre.co.uk 是否其實導到 ATG(避免重複申請)。

## [v0.37.1] - 2026-06-14 16:37
### 新增
- index.html `<head>` 加入 Impact(impact.com)網站擁有權驗證 meta 標籤(公開驗證碼,非密鑰),供 Ticketmaster 聯盟申請驗證 dannynycc.github.io/MusicalMap。

## [v0.37.0] - 2026-06-14 16:24
### 新增(隱私權政策 + 使用條款頁)
- `privacy.html` / `terms.html`:聯盟計畫(Impact 等)審核要求的公開頁面。內容據實:靜態地圖無廣告追蹤/無第三方分析;My Musicals 用 Google 登入、資料存 Supabase(RLS,僅本人可存取);售票外連可能含分潤(Impact/Partnerize/Awin,使用者不多付);準據法台灣;聯絡 dannynycc@gmail.com。
- 首頁頁尾 + 兩頁導覽互連,公開可達(`.legal`/`.foot-links` 樣式)。

## [v0.36.4] - 2026-06-14 16:20
### 新增(文件)
- `docs/AFFILIATE_SETUP.md`:分潤帳號申請逐步清單(Ticketmaster/Impact、ATG/Partnerize、LondonTheatre/Impact·Awin),含共用前提(隱私權/條款頁、W-8BEN 稅表、收款)、每家在哪拿哪些 ID、拿到後給我哪些欄位即可填入 `AFFILIATE` 上線。

## [v0.36.3] - 2026-06-14 16:13
### 新增(分潤連結範本 — 研究各平台聯盟計畫)
- 研究確認各售票平台 2026 聯盟方案,把**正確連結格式**寫成 `AFFILIATE` 範本(app.js),申請後填 ID 即生效:
  - **Ticketmaster**(我們最大宗 ~915 連結)→ Impact(impact.com),redirect 包裝 `https://imp.pxf.io/c/{帳號}/{ad}/{campaign}?u={目的URL}`;30 天 last-click;**佣金低(約 $0.30/單),且開賣前/開賣首 24 小時不計佣**。
  - **ATG Tickets**(238 連結)→ Partnerize `https://prf.hn/click/camref:{CAMREF}/destination:{URL}`,階梯佣金。
  - **LondonTheatre.co.uk**(82 連結)→ Impact/Awin,**約 10%(西區最佳率)**。
  - Stage Entertainment DE 有德國聯盟(~4-7%);Broadway.org/Interpark/jegy/OPENTIX/四季 等**無公開聯盟**→ 維持純連出。
- 全平台皆支援 deep-link,**連主頁帶追蹤碼即可抽成**(印證既有設計:資料存乾淨主頁、前端 render 時包裝)。

## [v0.36.2] - 2026-06-14 15:58
### 修正 / 新增(售票連結 + 分潤掛勾)
- **Ticketmaster 連結一律連到穩定主頁**:確認 915 條中 895 條已是 `/artist/` attraction 主頁(如 `funny-girl-touring-tickets/artist/3007772`);剩 25 條會過期的 `/event/` 單場連結改成同國域名的**搜尋頁** fallback(ticketmaster.py/tm_tours.py 改 code + 既有資料就地修),現存 `/event/` 連結歸零。
- **分潤/commission 連結掛勾**(app.js `affiliateUrl()` + `AFFILIATE` 設定):資料維持乾淨主頁 URL,分潤包裝集中在前端 render 時套用——拿到 Impact/Partnerize 等分潤 ID 後填一行即生效,**不必重抓、不污染資料**;支援按網域分別設定(Ticketmaster/ATG…)。預設 passthrough(尚未啟用)。
- **archive 身分穩定性修正**:run_key 依賴 group,session 中途改正規化會讓 git-backfill 的舊狀態與現狀對不上(且復活已移除的非音樂劇)。改以**乾淨當前狀態重置 archive**(1296 runs),`bootstrap_archive.py` 加註腳:正規化變動後應走「重置 + 前向累積」而非 backfill。

## [v0.36.1] - 2026-06-14 15:36
### 變更
- **前端暫不顯示歷史資料**:時間軸往回瀏覽功能用 `SHOW_HISTORY=false` 旗標關閉(滑桿維持只到本月、不載入 archive)。歷史層 `archive.py` 仍每日 CI 累積,資料持續存著,日後一行翻 `true` 即開啟。

## [v0.36.0] - 2026-06-14 14:31
### 新增(歷史檔案系統 — 時間軸可往回看過去)
- **歷史累積層 `scrapers/archive.py`**(獨立於純函式 build):每天把當前快照**累積**進不可變歷史檔 `data/archive/<year>.json`(`archive = 舊 ∪ 今天`)。原本 build 每天**覆蓋**、閉幕劇永久消失;現在改成只增不刪。
  - **架構原則**:事實(劇名/劇院/日期)閉幕後**凍結永不改**;tag/group **每次重算**(我改分類規則,歷史顯示自動更新,日期不動)。身分用穩定自然鍵(group|城市|劇院|起始年)。**刻意把有狀態的累積與「可重跑的純 build」隔開**,避免每次 build 回頭竄改歷史。
- **git 歷史回溯 `scrapers/bootstrap_archive.py`**:CI 本來就每天 commit `shows.json`,git 即不可變每日快照;一次性挖出來灌入 archive → 免費拿到專案開始至今的回溯資料。已 bootstrap:1355 runs / 跨 1988–2028。
- **人工策展深歷史 `data/curated_history.json`**:archive 開始前就閉幕的重要檔期(Hamilton 2015-、Phantom NY 1988–2023),售票 API 抓不到過去,改 Wikipedia/Wikidata 查證;只記事實,tag 自動套。與自動累積同 schema,用 `provenance` 區分,策展事實不被 scrape 覆蓋。
- **前端時間軸往「過去」延伸**(app.js):滑桿 min 依 archive index 延到最早年份;拖到過去月份時 lazy-load 對應年檔(現在/未來仍讀 live `shows.json`);`overlapsMonth` 不變。
- **CI**:build 後加跑 `archive.py`,commit `data/archive/`。
### 誠實限制
- 回溯只到「CI 開始 commit shows.json」那天(本專案約 4 天前);更早(含 2025/12 多數)挖不到,需靠 `curated_history.json` 人工補。**愈早開 archive 愈值錢**(每天不存就丟)。
- 深歷史策展是持續工作(下一步:用 Wikidata/Wikipedia 拉主要劇歷年檔期填 curated)。

## [v0.35.0] - 2026-06-14 13:55
### 新增(西語類別 + tag fallback 重設計)
- **新增「西語音樂劇」類別**(西/墨/拉美),前端第 8 個 filter pill。
- **重寫 `classify_tag` fallback**:Broadway/West End 不再是萬用預設(原本把 `Hola Raffaella` 等西語原創誤掃進百老匯),只給①已註冊英美作品②真正英美來源(broadway/atg/londontheatre)③英語市場(US/UK/CA/AU/NZ/IE…)。其餘按國家落地:西/墨→西語、德奧區→德奧、法→法式、其他歐陸(比/荷/丹/義/北歐…)→歐陸原創(語意擴為「全歐陸在地原創」)。

### 修正(完整通盤查證 — 4 桶 web 稽核)
- 派研究 agent **web 查證西語/韓國/歐陸/日本四桶共約 200 齣**,逐筆判定「是不是真音樂劇」+「血統/是否進口」。
- **非音樂劇大清除(共剔 139 筆)**:新增 `data/not_musical.json` 排除清單 + 多語 pattern。揪出被當音樂劇的:話劇(La cena de los idiotas=Le Dîner de Cons、Drácula una comedia)、致敬演唱會(Hola Raffaella=Raffaella Carrà 致敬、tributo a ABBA/Tina、Oh What a Night、Nino Bravo)、a cappella/朗誦(Dimensión vocal、Los diarios de Manhattan)、魔術/默劇/喜劇變奏(PaGAGnini、Les Virtuoses、Slapstick、Limbo)、餐飲體驗(Mamma Mia! The Party)、**2.5次元舞台劇 19 齣**(ブルーロック/チェンソーマン/ダンダダン/龍が如く/あんステ/おそ松 on STAGE/刀剣乱舞 ICE SHOW…;2.5次元有「ミュージカル」也有「舞台」,只留前者)、兒童偶戲(Bluey's Big Play)、Jr./Junior 校園刪減版。
- **翻譯/在地語標題的進口劇歸位**(模糊比對抓不到、靠查證):西語 `El Rey León`=Lion King、`El Fantasma de la Ópera`=Phantom、`La Familia Addams`、`Querido Evan Hansen`、`La Novicia Rebelde`=Sound of Music、`Matilda`、`Papá por siempre`=Mrs. Doubtfire、`Treintonas`=WaistWatchers、`Sunday in the park…`、`Los últimos 5 años`=Last Five Years、`Asesinato para dos`=Murder for Two、`Gutenberg`;歐陸 `DONAHA`=Full Monty、`Divotvorný hrnec`=Finian's Rainbow、`Menopauza`=Menopause、`Pět let zpět`=Last Five Years、`Sopranistky`=Our Ladies、`Oltári srácok`=Altar Boyz、`Monte-Cristo`、`Oliver!`;德奧誤判 `& Juliet`/`Tarzan`/`The Devil Wears Prada` → Broadway/West End;韓國 `Lempicka`/`Midnight`/`Barbershopera` → 英美、`Again Romeo & Jeliet` → 法式、`Ghost & Lady` → 日本(四季);日本 `BOOP!`/`NINE` → 英美。
- **Death Note 韓國場(Daejeon)** → 日本原創。**I Love You, You're Perfect, Now Change** → Broadway/West End(1996 Off-Broadway 長壽劇)。
- **根因修 `_norm` 撇號不一致**:直引號 `'` 被當詞界變空格("you're"→"you re")、彎引號 `'` 被 ascii-ignore 丟掉("youre"),同劇不同引號對不上、dedup 失效;改一開始統一刪所有撇號變體,連帶修 disney 前綴。
- **過濾 Jr./Junior 校園版**;**discover 報告擴及西語/所有在地桶**。
- 最終分布(1295 齣,8 類):Broadway/West End 1091 · 日本 50 · 歐陸 42 · 台灣 38 · 西語 27 · 韓國 21 · 德奧 17 · 法式 9。非音樂劇剔除累計 139。
### 誠實限制
- 四個高汙染桶(西/韓/歐陸/日)已 web 查證;Broadway/West End 桶(1091,多來自英美策展源)以 pattern 掃過,未逐筆 web 查證,殘留少量可能漏網。`build --discover` 每次列疑似未對照進口供持續修。

## [v0.34.0] - 2026-06-14 13:10
### 新增(類型/血統 tag 分類 + 篩選)
- **每齣劇自動標血統 tag**(`build_shows.py` classify_tag):Broadway/West End、德奧音樂劇、法式音樂劇、台灣原創、日本原創、韓國原創、歐陸原創。判定看**作品血統不看演出地**——勾「Broadway/West End」連在澳洲/匈牙利巡演的 Wicked、布達佩斯的 `Macskák`(Cats)都一起出現;Les Misérables 歸 Broadway/West End。
- **前端類型篩選 pill**(index.html / app.js / style.css):側欄搜尋下方一排可多選 pill(各帶血統色 + 數量),空選=全部;popup 卡加血統色 badge。
- **正典作品註冊表 `data/works.json`(單一真相來源)**:把原本散落的 `INTL_IP`(雙語顯示)/`GROUP_ALIASES`(去重)/in-code tag 清單**三套併成一套**。一齣作品一筆記 `tradition` + 跨語言 `aliases`,任何別名(`Macskák`/`キャッツ`/`貓`/`Cats`)收斂到同一 group → 同時供分類、跨語言去重、雙語顯示三用,加新語言/來源只需補 alias。
- **discovery 報告**(`build_shows.py --discover` → `data/_works_discover.json`):用模糊比對揪出「被標成在地原創、但高度近似某正典」的疑似未對照進口劇(已抓到韓國場的 Death Note 變體)。
- 修正東歐授權劇誤判:`Az Operaház Fantomja`=Phantom、`Jégvarázs`/`Ledové království`=Frozen、`APÁCA SHOW`=Sister Act、`VÁMPÍROK BÁLJA`=Tanz der Vampire(德奧)等十餘齣,從「歐陸原創」歸位到正確血統;Kiki's/Death Note 從台灣原創修正回日本原創。歐陸原創淨剩 39 齣**真**匈牙利/捷克原創。

### 修正(Ticketmaster 殭屍/非音樂劇)
- **跳過 cancelled/postponed 場次**(ticketmaster.py + tm_tours.py 讀 `dates.status.code`),並改用穩定的 **attraction 頁** URL 當售票連結(原 per-performance event URL 過期即 404)。全球掃 405→398。
- **強化非音樂劇全域過濾**:TM 把致敬樂團/演唱會/songbook/drag/medley 標成 Musical(如 Hotel California - Eagles Tribute、Bee Gees Celebration、Disney Princess - The Concert、Fuel Injected Magic Concert),新增 `tribute|concert|soundtrack|gala|celebration|symphony|orchestra|songs of|drag|nonstop|koncert` 等規則,實測剔除 70 筆假音樂劇、0 誤殺真劇。

## [v0.33.0] - 2026-06-14 12:05
### 新增(東歐 — 第二階段:捷克)
- **捷克音樂劇接入**(easteurope.py scrape_czech,來源 prazskemuzikaly.cz)。只收**職業大劇院**(Karlín / Hybernia / Broadway / Kalich / Radka Brzobohatého / NDM Ostrava 等 allowlist,排除地方/業餘),城市由場館判定(非頁面文字,頁尾恆有 Praha)。日期取 JSON-LD `startDate`(避開 `validFrom`=今天的陷阱)→ 真實檔期。帶入 31 檔:Dracula / SIX / Mamma Mia / The Bodyguard / Ledové království(Frozen)/ ELISABETH / Beetlejuice / Jesus Christ Superstar / Anděl páně / Rebelové 等(Prague 27 + Ostrava 4),0 無座標、皆在捷克境內。掛每日 CI。
- 東歐累計:匈牙利 36 + 捷克 31。**WIP:波蘭(Teatr Roma)下一步。**

## [v0.32.0] - 2026-06-14 03:09
### 新增(東歐 — 第一階段:匈牙利)
- **匈牙利音樂劇接入**(新 `scrapers/easteurope.py`,jegy.hu musical 分類;結構可加捷克/波蘭)。平台已做類型過濾,全為音樂劇;category 取劇名+海報+場館(schema.org Place)+地址城市,detail 取所有場次日期(首末=檔期)。帶入 36 檔:Az Operaház Fantomja(魅影)/WICKED/Macskák(貓)/REBECCA/ELISABETH/Jekyll és Hyde/VÁMPÍROK BÁLJA(吸血鬼之舞)/Mamma Mia/Evita/Jégvarázs(冰雪奇緣)等,涵蓋 Budapest(21)+Szeged/Győr/Debrecen/Veszprém 等,Google 建築級座標、0 無座標、地理檢查皆在匈牙利境內。掛每日 CI。
- 東歐先前僅 1 檔(Ostrava Elisabeth 手動)→ 大幅補強。**WIP:捷克(colosseumticket.cz)/波蘭(Teatr Roma)下次續做。**

## [v0.31.1] - 2026-06-14 02:52
### 修正
- **坎培拉漏抓**:坎培拉劇院中心音樂劇賣在 Canberra Ticketing(自家系統)不在 TM。補上 Heathers The Musical 坎培拉站(8/14–23,與雪梨站同巡演),Google 建築級座標。揭露通則:澳洲二線城市(坎培拉/Newcastle 等)音樂劇多在地方售票系統(無 API),目前靠發現/手動補。

## [v0.31.0] - 2026-06-14 02:45
### 新增 / 修正(澳洲嚴格驗證)
- **補上漏掉的大型音樂劇 SIX**(在 **Ticketek** 不在 Ticketmaster,故 TM scrape 漏):手動加 Melbourne Comedy Theatre(7/24)、Theatre Royal Sydney(10/9)、QPAC Playhouse Brisbane(2027/1/2)三站,Google 建築級座標。
- **城市正規化**:TM 用郊區名(Pyrmont/Haymarket→Sydney、Burswood/Northbridge→Perth、Torrensville→Adelaide),改顯示都市。
- **剔除非音樂劇/非職業**:Scotch College-Hadestown(學校製作)、A Very Musical Theatre Christmas(聖誕 revue)加入全域過濾。
- **修 Beetlejuice Brisbane 無開演日**(manual 補 2026-06-07,官方 QPAC 季);verify 後 Hamilton/Phantom(Handa)非缺漏(已結束/未巡演),& Juliet Queanbeyan/Newcastle 疑社區製作未加。
### 誠實限制
- 澳洲 TM 部分每日 CI 自動更新;SIX/Beetlejuice 為手動(Ticketek/QPAC 無公開 API)。Ticketek 是澳洲另一大票務盲區。

## [v0.30.0] - 2026-06-14 02:28
### 修正
- **韓國剔除非音樂劇**(world.nol.com/Interpark 把觀光向無歌曲表演標成 MUSICAL):NANTA(난타 打擊喜劇)、PAINTERS(繪畫秀)、JUMP/Comic Martial Arts(武術喜劇)、Sleep No More(沉浸式劇場,無歌曲)全域過濾。韓國 36→31 真音樂劇。Beethoven/PAGANINI/Diaghilev(韓國原創音樂劇)保留。

## [v0.29.5] - 2026-06-14 02:19
### 修正
- **Harry Potter and the Cursed Child 是話劇非音樂劇**(broadway.org 誤分類),全域 NOT_MUSICAL_RE 加「cursed child」剔除(全球各地共 7 站,含東京 TBS赤坂ACT)。
- 系統性查證:99 檔日本 show 座標與城市地理一致性 0 異常(每筆都在其都府縣範圍);城市讀自網頁「【XX公演】」語義非 Tokyo fallback;シアター1010=Tokyo(足立区)、京都劇場=Kyoto 等建築級準確。

## [v0.29.4] - 2026-06-14 02:15
### 修正
- **東急シアターオーブ海報抓到通用卡圖**(og:image=cardimage.png)。改抓頁面內 `/data/files/.../mainvisual.jpg` 真海報。BOOP!/Sunset Boulevard/Chicago/Miss Saigon/NINE/BLAST 6 檔全到(實測 200)。

## [v0.29.3] - 2026-06-14 02:12
### 修正
- **2.5次元海報抓到協會 logo 而非劇目海報**(og:image 是 j25musical 通用 logo)。改抓頁面內 `showCtsImage.php?cid=…&no=1` 真海報。70 檔全部取到(忍たま乱太郎/ヒプノシスマイク… 實測 200)。

## [v0.29.2] - 2026-06-14 02:06
### 新增 / 修正
- **東急シアターオーブ(音樂劇專用劇場)接入**(japan.py scrape_orb):補上非東宝製作的大型音樂劇 **BOOP! / Sunset Boulevard / Chicago / NINE / BLAST**(Miss Saigon 與東宝去重)。lineup 各檔 detail 取 og:title +「公演日程」。
- **日文大 IP 中英並列+去重**:INTL_IP 加 シカゴ→Chicago、ミス・サイゴン→Miss Saigon、サンセット大通り→Sunset Boulevard、レベッカ→Rebecca 等 → orb「シカゴ」併入既有 Chicago、避免同劇重複。
- 日本總數→99 檔、0 無座標。全部掛在每日 CI(toho/j25/orb 都在 japan.py)自動更新。

## [v0.29.1] - 2026-06-14 01:50
### 修正
- **剔除 Ticketmaster 誤分類為音樂劇的非音樂劇活動**:全域標題過濾(movie tour / screening / film concert / comedy tour / documentary / book tour / stand-up / in conversation)。例:「John Cameron Mitchell: Hedwig 25th Anniversary Movie Tour」(電影巡迴放映,9 站)剔除,真音樂劇「Hedwig and the Angry Inch」保留。

## [v0.29.0] - 2026-06-14 01:46
### 新增 / 修正
- **日本擴充(二):2.5次元ミュージカル**(japan.py scrape_j25,來源 日本2.5次元ミュージカル協会 j25musical.jp)。逐檔解析「【城市公演】日期 場館」多城巡演區塊,過濾未來場、抓官方海報。帶入テニスの王子様/ヒプノシスマイク/ブルーロック/あんさんぶるスターズ/忍たま乱太郎等;城市正規化(東京凱旋→Tokyo 等),海外/未對應城市略過。日本場館 geocode 補齊(含 name_ok 擋下的 4 個手動補)。日本總數→95 檔、0 無座標。
- **宝塚雙部劇名**:抓題名全部『』(前半芝居+後半ショー)→ 黒蜥蜴／Diamond IMPULSE、RYOFU／水晶宮殿、天穹のアルテミス／Belle Époque、London Way／Ivresse Vague;HTML entity 解碼(É)。
- **再修同劇重複**:`clean_title` 也剝「(New York, NY)」「(Cleveland, OH)」城市州別後綴(The Lion King 不再重複);`group_key` 先剝 Disney's 再剝 the(「Disney's The Lion King」併入「The Lion King」)。

## [v0.28.4] - 2026-06-14 01:34
### 修正
- 宝塚海報抓取改鎖定「主視覺欄位」(`article01`/`div.img` 500px 那格)的圖,不再看副檔名:黒蜥蜴=xyd93.jpg(真海報)、尚未出圖的(Elisabeth/天穹/London Way)=官方 revuetop_comingsoon.jpg。修正 v0.28.3 誤抓到頁首 logo(.png)的問題。

## [v0.28.3] - 2026-06-14 01:28
### 修正
- 宝塚海報再修:真海報常是 `.png`(comingsoon 才是 .jpg),原 regex 只抓 .jpg 導致 Elisabeth/天穹/London Way 誤用 coming-soon 圖。改抓 jpg+png 且排除 comingsoon → 7 檔全部真海報(實測 200)。

## [v0.28.2] - 2026-06-14 01:25
### 修正
- 東宝(japan.py)補上海報:從 card-lineup__image 依 alt(=劇名)對應抓圖,8 檔皆有官方主視覺(實測 200)。日本三來源(四季/宝塚/東宝)海報齊全。

## [v0.28.1] - 2026-06-14 01:23
### 修正
- **宝塚海報抓到的是組別通用 logo 不是劇目海報**(黒蜥蜴顯示宙組 og_cosmos.png 佔位)。改為優先抓劇目頁內文主視覺 `/revue/<年>/<slug>/<hash>-img/<hash>.jpg`,og:image 只當最後備援。黒蜥蜴/ポーの一族/RRR/RYOFU 取到真海報;尚未公布主視覺的(Elisabeth/天穹/London Way)用官網 coming-soon 預告圖。

## [v0.28.0] - 2026-06-14 01:19
### 新增
- **日本擴充(第一階段):東宝音樂劇**。新 `scrapers/japan.py`(與既有 shiki/takarazuka 並存,不取代)。從 toho.co.jp/stage/lineup 取『』劇名+日期+場館,只留「ミュージカル」前綴(剔除舞台劇/演唱會);JP 日期解析(2026年5月6日～6月30日)。帶入 8 檔:レベッカ/町田くんの世界/ゴースト/民王/ファニー・ガール/RENT/ミス・サイゴン/ラ・カージュ・オ・フォール(シアタークリエ/日生劇場/東急シアターオーブ,Google 建築級座標)。掛進每日 CI。
  - 日期模糊(2027秋上演/全国ツアー中)或多場館未定者暫跳過;梅田芸術劇場、2.5次元(j25musical)為下一階段。

## [v0.27.5] - 2026-06-14 00:32
### 修正
- `core_title` 也支援「」『』角括號取劇名:「唱進心靈的眼眸：『青瞑猴，出外讀冊拼出頭』音樂劇」→「青瞑猴，出外讀冊拼出頭」(《》仍優先)。

## [v0.27.4] - 2026-06-14 00:29
### 修正
- **OPENTIX 多場館巡演只抓到第一個場館**:`eventVenues[0]` 寫死,像躍演《勸世三姊妹》3 城巡演(國家戲劇院/臺中國家歌劇院大劇院/衛武營歌劇院)只顯示台北。改為**每個 eventVenue 各出一筆**,各自帶該站的座標與場次日期(OPENTIX 每館自帶 location + times)。OPENTIX 收錄 30 → 40 檔。

## [v0.27.3] - 2026-06-14 00:25
### 修正
- OPENTIX 排除清單微調:加入「天堂客棧」(確認非音樂劇);移除「大家都怎麼做音樂劇」(用戶確認屬音樂劇,改回收錄)。OPENTIX 收錄 30 檔。

## [v0.27.2] - 2026-06-14 00:22
### 修正
- 續清 OPENTIX 分類混入的非音樂劇:新增排除「漫才」(類型詞)+ 點名項(大家都怎麼做音樂劇/怪美妖仙傳/一個彥達/最後五秒/築夢之橋);天堂客棧保留。OPENTIX 收錄 35 → 29 檔。

## [v0.27.1] - 2026-06-14 00:12
### 修正
- **utiki 來源沒有海報**(KHAM/UDN/MNA 的劇在地圖上只顯示音符佔位圖)。`utiki.py` 加 `find_image()`:從 listing 抓 imgs2.utiki.com.tw 的產品海報(優先 UTK2401 產品圖,避開 404 的縮圖變體)。萬世巨星/史瑞克/魔女宅急便 皆補上海報(實測 4 張皆 HTTP 200)。
- **MNA 場館沒帶廳別**(臺中國家歌劇院有大/中/小三廳)。`mna_venue()` 改為場次列取基本館名後,再從描述補上具體廳別 → 魔女宅急便(台中)= **臺中國家歌劇院大劇院**(與 OPENTIX 命名一致,套到既有座標)。

## [v0.27.0] - 2026-06-14 00:02
### 修正
- **OPENTIX 只抓到第一頁(漏掉大量音樂劇)**:search API 每頁只回 15 筆(`hitsCount`=44 才是總數)+ `nextOffset` 游標,我之前只取第一頁 → 9 月的《囍宴》等被漏掉(拉到 9 月地圖空白)。`fetch()` 改為用 offset 分頁抓完全部。OPENTIX 收錄 12 → **35 檔**(涵蓋到 11 月)。
- **無《》標題清理**:像「國際共製大型音樂劇 囍宴」沒有書名號,`core_title` 改為再嘗試取「…音樂劇/舞台劇 之後的名稱」→「囍宴」。
- **排除主辦混入「戲劇-音樂劇」分類的非音樂劇**:依標題類型詞(舞台劇/擊樂秀/演唱會/音樂會/工作坊)+ 點名項(H&G2、一粒萬倍)過濾;搶救魔幻飛船(花露露舞台劇)、咻咻擊樂秀、讀演音樂會等已剔除。如蝶翩翩(韓國音樂劇)等正常收錄。

## [v0.26.2] - 2026-06-13 23:54
### 修正
- **INTL_IP 對照表查核清理**:逐條檢視我先前憑記憶加的條目。移除 **金牌特務→Kinky Boots(查證為錯:金牌特務=Kingsman 間諜片,非音樂劇;Kinky Boots 正確是長靴妖姬)**、非標準變體「劇院魅影」、重複的「羅密歐與茱麗葉」;補上繁中「漢彌爾頓→Hamilton」。其餘為標準通用譯名;目前實際使用中的僅 3 筆(萬世巨星/史瑞克/魔女宅急便)皆來源確認。

## [v0.26.1] - 2026-06-13 23:48
### 修正
- 移除 INTL_IP 誤加的「獅子王王國→The Lion King」(不是真實劇名,且獅子王已在表中)。

## [v0.26.0] - 2026-06-13 23:46
### 新增
- **MNA 售票來源(ticket.mna.com.tw)**:同屬 utiki UTK 引擎,整合進 `utiki.py`(共用 cookie session)。分類 77(音樂)混雜演唱會/交響音樂會,只留標題含「音樂劇」;日期取自 listing 卡片、場館取自詳情頁場次表(取最常出現場館)。
  - 帶入:**Kiki's Delivery Service 魔女宅急便**(臺北國家戲劇院 7/10–19、臺中國家歌劇院 7/24–8/2 兩城巡演),Google 建築級座標。
- INTL_IP 對照新增 魔女宅急便 → Kiki's Delivery Service,中英並列顯示。

## [v0.25.2] - 2026-06-13 02:13
### 變更
- onsale_only 日期文案語意調整:「售票中 · 約演至 X」→「**售票中至 X**」(X 是售票截止日,非演出結束推估)。

## [v0.25.1] - 2026-06-13 02:11
### 修正
- **Ticketmaster 來源「約演至」日期錯誤(太早)**:CATS: The Jellicle Ball 顯示「約演至 2026-07-02」實際售票到 2027-01-17。根因是我寫的 ticketmaster.py 用 `sort=date,asc` 掃城市、撞到 1000 筆深分頁上限,熱門城市(紐約)把劇目後段場次截掉。改由 booking_horizon.py 用 TM 正確的 `sort=date,desc` 取每齣劇**真正最後一場**,並擴及所有 onsale_only 的劇(本次修正 32 筆 end)。
- **同劇重複(去重漏掉)**:Ticketmaster 的「Wicked (NY)」因「(NY)」後綴 group_key 不同,沒跟百老匯駐演 Wicked(同場館)合併而重複出現。`clean_title` 改為剝除結尾的地點/巡演限定詞(NY/Broadway/UK Tour…),正當括號(如 Two Strangers (Carry a Cake…))保留。
- **側欄展開場館清單排版參差**:長場館名換行時城市被擠成兩行(Milwaukee,/WI)。`.sub-item` 改為場館名 `flex:1` 自然換行、城市 `nowrap` 靠右、整列頂端對齊。

## [v0.25.0] - 2026-06-13 01:46
### 修正
- **開放式長壽劇拖到數年後仍顯示**(Buena Vista Social Club 售票只到 2027/1,時間軸拖到 2029/6 還在地圖上)。根因:`overlapsMonth` 把「無 end_date」當成「永遠在演」。
  - 新 `scrapers/booking_horizon.py`:對所有無 end_date 的劇用 **Ticketmaster `sort=date,desc`** 抓「最後一場售票日」當 end(TM 就是售票系統,最準)。實測 22/27 取到真實日期(Buena Vista→2027-01-17、Phantom→2027-03-13、Wicked→2027-01-03…);TM 無資料的(ABBA Voyage、馬德里西語劇)退回啟發式。
  - `overlapsMonth` 對仍無 end 的劇加「售票視野上限」(今天 +12 個月)fallback,不再無限延伸。
  - 這類 end 標記 `end_rolling`,顯示「自 X 上演 · 售票至 Y」而非像閉幕公告的日期區間。
  - 接入 build_shows 與每日 CI(build → booking_horizon → build)。
- **時間軸滑桿範圍改為依資料動態**:原固定 3 年(拖到 2029 全空),改成只到「最晚一檔開演月份 +1」(目前 2028-04),不再有一堆空白月份。

## [v0.24.0] - 2026-06-13 01:19
### 新增 / 變更
- **OPENTIX 劇名自動 parse**:主辦把真名包在《》裡加一堆前後綴(果陀劇場《生命中最美好的5分鐘》2026音樂奇蹟重現),改成取《》內真名 →「生命中最美好的5分鐘」。
- **國際大 IP 中英並列**:萬世巨星→「Jesus Christ Superstar 萬世巨星」、史瑞克→「Shrek 史瑞克」。本土原創維持中文(光看英文字串無法分辨國際 IP 與本土翻譯,故以 build_shows `INTL_IP` 對照表辨識,持續擴充)。
- **地圖同場館多筆改為 zoom 感知動態展開**(個人足跡 me / u):環半徑 = max(18px, 38m)——低 zoom 用 18px floor 就稍微錯開(不再 100% 疊),越 zoom 分越開,高 zoom 回到真實 38m 位置完全分離;每次 zoom 重算。
### 修正
- **恆春文化中心座標**:確認線上現為 Google 建築級 22.00261,120.748859(=恆春鎮文化中心劇場館,2025/11 新啟用,0m 吻合);先前舊部署殘留 OPENTIX 原始 22.00657(差 447m)。全部 12 個台灣 OPENTIX/utiki 場館已逐一對 Google Places 重查,皆 ≤30m。

## [v0.23.1] - 2026-06-13 00:54
### 修正
- **utiki show id 不穩定**:原用 Python 內建 `hash()`(每 process 隨機化),本地/CI/每日之間 id 都不同會造成資料無謂 churn。改用 `hashlib.md5` 取穩定 id。

## [v0.23.0] - 2026-06-13 00:51
### 新增
- **台灣 utiki 售票來源(寬宏 KHAM + udn售票)**:新 scraper `scrapers/utiki.py`,兩家共用同一套 UTK 引擎。
  - KHAM:分類 80(音樂劇)listing → 場次頁 eventTABLE 逐場取日期/場館(`PLACE_NAME`)/地址。
  - UDN:搜尋「音樂劇」listing 卡片直接帶日期範圍+場館(可多場館巡演)+銷售狀態,免打場次頁。
  - 排除合唱/演唱會/工作坊/交響音樂會;已結束(end < today 或標「結束銷售」)自動濾掉;座標交 `geocode_google.py` 取建築級。
  - 目前帶入:萬世巨星 @ 國家戲劇院(6/18–21)、史瑞克 @ 臺北表演藝術中心 大劇院(11/20–29)。
- 接入 `build_shows.py` SOURCE_FILES 與每日 CI。
### 修正
- **`group_key` 純中文標題全 collide 成空字串**:ASCII-strip 後中文劇名變 `""`,導致同城市所有中文劇被 merge 成一筆(萬世巨星/史瑞克皆 `""`)。fallback 改用保留 CJK 的 Unicode word 字元 → 各劇有穩定且不同的 key。順帶救回 6 筆先前被錯誤合併的中文劇(1284→1290)。

## [v0.22.5] - 2026-06-13 00:31
### 修正
- **地圖同場館多筆永遠疊在一起 / 要 zoom 到很深才展開且每 zoom 重收合**(臺中國家歌劇院同座標 3 筆 = Phantom/Miss Saigon/Roméo)。
  - 個人足跡地圖 (me / u) **改為不做數字群集**:一載入就把每筆都畫出來,低 zoom 互疊沒關係,zoom in 自己分開。
  - 同一座標的多筆改用**環狀微位移**(~38m,popup 仍存真實場館座標)展開,zoom 越深分越開,**最終一定分離**,不再永遠疊著、也不需手動點開。
  - 主地圖 (index) 仍保留數字群集(全球密度需要),但同套位移讓同場館多場在高 zoom 自然脫離群集分開。
  - me.html / u.html 移除已不再使用的 markercluster 載入。

## [v0.22.4] - 2026-06-13 00:03
### 修正/新增
- **台灣場館重複**(臺中歌劇院中/大/小劇場各出現兩次):OPENTIX 用中文城市(臺中)、curated 用英文(Taichung),分桶配不到。opentix.py 加 CITY_MAP 正規化城市為英文 + gen_catalog 比對忽略空格、合併後採雙語名。
- **連結可拖曳排序**:多個連結時可用把手 ⠿ 拖曳調整上下順序。

## [v0.22.3] - 2026-06-12 23:57
### 變更
- 國家兩廳院場館中文名簡化:「國家戲劇院（國家兩廳院）」→「國家戲劇院」(顯示為 National Theater and Concert Hall 國家戲劇院)。

## [v0.22.2] - 2026-06-12 23:54
### 修正
- **OPENTIX 台灣場館改用 Google 建築級座標**:原本用 OPENTIX 自帶 location,實測 16 個偏 >30m。改為 build 後跑 geocode_google 取精準座標寫入 venue_coords.json(至德堂/恆春文化中心等已校正;CI 沿用)。
- **排除「服裝造型工作坊」**:工作坊非音樂劇,opentix.py EXCLUDE 加「工作坊」。

## [v0.22.1] - 2026-06-12 23:46
### 新增
- **一筆紀錄可加多個連結**:新增表單把單一 Link 改成可動態增減的多連結(「＋ add link」/「×」);log 與公開表格顯示全部 🔗。(後端 `supabase/add_url.sql` 同時加 `links jsonb`;缺欄時自動略過不報錯)
### 修正
- **同名場館存錯座標**(用戶:Miss Saigon 圖示跑到芝加哥):「Orpheum Theatre」多城市同名,onSave 只用名字配到第一個(Minneapolis)。改為選自動帶入時記住該場館座標(隱藏 lat/lng),手填則用名字+城市配。重新編輯重選該城市即修正。
- **場館名存檔後被改回**(用戶:選大劇院變中劇院):`upgradeVenueNames` 用座標把同座標子廳(大/中/小劇場、戲劇院/實驗劇場)覆蓋成任意一個,還會在 Edit→Save 時把錯名寫回 DB。改為:已是現有 catalog 名稱就尊重不動,僅當舊名且該座標唯一場館時才升級。

## [v0.22.0] - 2026-06-12 23:35
### 新增(台灣當期音樂劇 — OPENTIX)
- **`opentix.py` scraper**:接兩廳院售票系統 API(`POST search.opentix.life/search`,分類 戲劇-音樂劇),取真實場館+座標(WGS-84)+檔期+海報。納入主地圖「演出地圖」(SOURCE_FILES + 每日 CI)。
- 自動排除非音樂劇:合唱(音樂-合唱 tag,如竹科媽媽)、演唱會、用戶點名的《老闆～來碗陽春麵》。當期收錄 12 部(I Love You You're Perfect / 生命中最美好的5分鐘 / 幸福三姐妹 / 潘朵拉的音樂盒 / COMPANY / 重拾時間的山語 等)。
- title 用中文(台灣觀眾慣用名),主地圖可用中文搜尋。
### 修正
- **Link 欄位缺後端時不再跳錯**:若 Supabase 尚未加 `url` 欄,存檔自動略過 url(其餘照存),不再 Save failed。

## [v0.21.0] - 2026-06-12 23:12
### 新增
- **新增表單加「Link」欄位**:可選填官網/售票連結;log 卡與公開表格顯示 🔗。(後端需跑 `supabase/add_url.sql` 加 `url` 欄)
- **公開頁 Overview / Log 分頁**:`u.html` 上方分頁切換;**Log 改成大表格、依日期排序、每欄可點擊排序**(日期/劇目/劇院/城市/國家/座位/票價/連結)。
- **同場館多場自動展開**:縮放到位時自動 spiderfy 散開(臺中歌劇院 3 場不需點擊自動分開);改用 markercluster `animationend` 觸發。
- **舊場館名自動升級**:顯示時依座標對照 catalog 用最新名稱(National Theater→National Theater and Concert Hall),不必手改舊紀錄。
### 修正
- **Per Year 折線連續**:從最早年到最新年每年都顯示(沒資料補 0),不再跳年。
- **移除自製 clampWorld/maxBounds**:那套造成個人/公開地圖縮放時 `_zoom` 崩錯、marker 渲染失敗;改回與 index.html 相同的乾淨地圖設定。

## [v0.20.1] - 2026-06-12 22:31
### 修正
- **同場館多場無法展開**:個人/公開地圖上,同一劇院的多場紀錄座標完全重疊(如臺中國家歌劇院 3 場),MarkerCluster 縮放無法分開。改為點擊 cluster 時若子點座標相同就直接 spiderfy 展開(me.js / u.js,實測點一下展開成 3 個海報)。
- **國家兩廳院英文名**:Google 回「National Theater」→ 硬改為 **National Theater and Concert Hall**(實驗劇場標為 …(Experimental Theater));`tw_venues.py` 加 `EN_OVERRIDE` 保證 re-run 不被蓋回。

## [v0.20.0] - 2026-06-12 22:19
### 新增(公開分享 profile — 推廣用)
- **`u.html?u=<使用者名稱>` 公開唯讀頁**:免登入即可看別人的音樂劇足跡(地圖+統計圖+清單,FlightRadar 風),類似 my.flightradar24 的分享頁。
- **me 頁加「公開分享」列**:設使用者名稱(handle)+ 勾「公開」→ 產生可分享連結 `…/u.html?u=名稱`(複製鈕)。
- 後端**無需改 schema**——既有 RLS 已允許匿名讀「is_public 的 profile + 其紀錄」(handle/is_public 欄位本就保留)。使用者名稱唯一,重複會提示換一個。

## [v0.19.2] - 2026-06-12 21:40
### 變更
- **所有劇院頁加「衛星」圖層切換**(Esri World Imagery,右上角地圖/衛星);衛星與 OSM 同為 WGS-84,方便直接驗證中國等地落點。

## [v0.19.1] - 2026-06-12 21:37
### 修正
- **中國場館位置全部偏移(~數百公尺)**:Google 對中國大陸回的是加密過的 **GCJ-02** 座標,但底圖是 WGS-84 → 全偏。`cn_venues.py` 加 GCJ-02→WGS-84 轉換(只作用於大陸經緯範圍,港澳台/海外不變),重抓 89 個中國場館 + 修正 shows 的上海大劇院。實測上海大劇院 121.4718→121.4673,落點正確。

## [v0.19.0] - 2026-06-12 21:26
### 新增(所有劇院地圖頁)
- **`theatres.html` 新頁面**:把全部 **4,919 個劇院**用與主頁相同的綠色群聚圈(cluster,√n 大小)呈現在地圖上;點擊圈圈逐層放大、單一劇院顯示小圓點 + popup(名稱/城市/國家)。
- **多語搜尋**:浮動搜尋框比對 catalog `search` 欄位(英/原文/簡繁/無重音),如「台中」「madach」即時過濾,顯示符合數/總數。
- 主頁 topbar 加「🎭 所有劇院」入口;新頁可回「🗺 演出地圖」與「⭐ 我的音樂劇足跡」。

## [v0.18.0] - 2026-06-12 21:19
### 新增(英國深掃 + 其他區域重點場館)
- **英國深掃** `gb_discover.py`:掃 91 個英國城市(theatre/opera house/concert hall/playhouse),Google Places 類型+評論數過濾,**UK 119 → 476**(West End → 全英各城 PAC/touring)。
- **其他薄弱區域重點場館** `row_venues.py`:拉美(巴西7/阿根廷5/智利3/哥倫比亞/秘魯)、中東(以色列4/UAE4)、印度5、東南亞(印尼/越南)、非洲(南非6/埃及)、土耳其7、墨西哥旗艦——含**本地語名**(希伯來/葡/西/阿拉伯/越南文),英文或本地語皆可搜。
- **catalog 場館 4,505 → 4,907、46 → 57 國**。

## [v0.17.3] - 2026-06-12 20:14
### 修正
- **拖時間軸 slider 會連底圖一起拖動**:timebar 浮在地圖上,Leaflet 攔截了其上的拖曳事件。加 `L.DomEvent.disableClickPropagation/disableScrollPropagation` + 阻擋 pointer/touch move 傳播,拖 slider 不再平移地圖(實測地圖中心不動、月份正常變)。

## [v0.17.2] - 2026-06-12 20:01
### 變更
- **時間軸拉寬**:原本置中只用約 1/3 寬;改為左右各留 10%(寬度 ~80%,手機 ~92%),月份 slider 隨之變長好拖曳。

## [v0.17.1] - 2026-06-12 19:59
### 新增(美洲 + 大洋洲深度覆蓋)
- **`na_discover.py`**:同 EU 方法,Google Places Text Search 掃 **170 個美/加/澳/紐城市**(performing arts center / theatre / concert hall / opera house),類型 + 評論數 ≥150 過濾,**淨增 1,619 個**真實場所。
- **各國暴增**:美 257→**1,561**、加 16→**199**、澳 14→**112**、紐 7→**41**。**catalog 場館 2,886 → 4,505**。
- 用戶先前點名缺的 **Hill Auditorium**(密大)現已收錄。
- gen_catalog 探勘去重 pass 通用化(eu + na 兩檔)。

## [v0.17.0] - 2026-06-12 19:08
### 新增(歐洲 + 俄羅斯深度覆蓋 + 無重音搜尋)
- **歐洲在地音樂劇場館**:`eu_venues.py` 精選核心(德/法/義/西-Barcelona/荷/比/北歐/波蘭/捷克/匈牙利/奧地利/斯洛伐克/斯洛維尼亞/克羅埃西亞/希臘/俄羅斯,~82 個,英文+本地語名)。
- **`eu_discover.py` 深度探勘**:用 Google Places Text Search 掃 100 個歐洲城市(theatre/concert hall/opera house),以場館類型 + 評論數(≥150)過濾,**Google 當資料源不杜撰**,清掉演出名/公司名雜訊;**淨增 1951 個**真實表演場所。希臘/俄羅斯另抓原文(英文或原文皆可搜)。
- **catalog 場館 859 → 2,886、涵蓋 46 國**。
- **無重音(diacritic-insensitive)搜尋**:`madach`=Madách、`munchen`=München、`lodz`=Łódź、`zurich`=Zürich;只折疊拉丁字母重音,**不碰** CJK 假名 / 西里爾 / 諺文(避免 ガ→カ)。`me.js` 與 `gen_catalog._clean()` 同步。
### CI/工具
- `geocode_google.py` 增量;EU 檔走獨立座標去重 pass(探勘是單點 POI,可安全用座標 ≤55m 去重,不影響亞洲子廳)。

## [v0.16.2] - 2026-06-12 18:53
### 修正
- **場館重複合併(用戶確認的 9 組)**:同場館不同寫法用明確別名清單 `ALIAS_MERGES` 合併為一(Fox Cities PAC、KeyBank State、Robinson、Hollywood Pantages、Hard Rock NYC、Dr. Phillips、Academy of Music、Straz Center、Hanover Theatre),兩種寫法仍可搜。**不同廳/不同劇院**(Tokyo Forum Hall A/C、Cool Japan TT/WW、Sydney 的 Joan Sutherland 廳、Madrid 三間、Nottingham 兩間…)**一律不動**。場館 866 → 857。

## [v0.16.1] - 2026-06-12 18:41
### 修正(用戶逐項回報)
- **cluster 圓圈大小不成比例**:原本線性 `26+n*1.7` cap 96 → n≥41 全撞頂(39/83/109 一樣大)。改 **半徑 ∝ √n**(面積≈正比數量)、上限拉到 112,大群明顯更大。
- **搜「藝術」找不到日文「梅田芸術劇場」**:OpenCC 無 jp2t config(我誤用害簡繁也一度失效);改各別 try 初始化 + 手動日文新字體→繁中字表(芸→藝、国→國…),日文場館中文也搜得到。
- **同場館不同寫法重複(San Jose…)**:`norm_venue` 把城市 token 移光後變空 → 原本用完整名當 key 害變體不合;改為空時**保留城市 token 再正規化**(「San Jose Center for the Performing Arts」變體合併為一)。
- **幣別不完整**:補 **NZD** 及全部涵蓋國別(14 → 34:THB/MYR/PHP/IDR/VND/INR/SEK/NOK/DKK/PLN/BRL/ZAR/AED…)。
- 座標去重偵測:純座標 80m 會誤合鄰近不同劇院(紐約一條街 5 間百老匯)與不同廳(大/中/小劇場),故**不做自動座標合併**;改名稱相似度過濾出 ~14 組真重複,待別名清單處理。

## [v0.16.0] - 2026-06-12 18:15
### 新增(覆蓋率大擴張 + 雙語/繁簡場館搜尋)
- **Ticketmaster 全球深掃**:國家清單從 18 國擴成全球所有市場;修掉 US/GB 深分頁 400(改按城市子查詢突破 TM 1000 筆上限)+ 5xx 重試。淨增 ~42 場館、77 場次,並為 174 筆既有附 TM 購票連結(1200 場次 / 589 場館 from shows)。
- **亞洲完整場館清單(用戶提供,Google 建築級座標+雙語)**:
  - 台灣 61、日本 81、韓國 51、中國 89 → `data/{tw,jp,kr,cn}_venues.json`(各自 scraper `*_venues.py`)。
  - 東南亞 Google 座標入 CURATED:菲律賓 8、新加坡 7、泰國 8、馬來西亞 12。
  - 這些是「My Musicals」個人紀錄 autocomplete 的在地場館(無當前檔期 → 不上世界地圖)。**catalog 場館 534 → 859、國家 31。**
- **雙語 + 繁簡 + 異體字 + 括號搜尋**:catalog 每個場館/劇名加隱藏 `search` 欄位,收錄 **英文 + 原文 + 簡體 + 繁體**(OpenCC,build 時產生),折疊 **臺↔台**,並把**所有半形/全形括號引號**(`() [] （）［］「」『』 ＂＇ "" ''` 等)正規化為空白(build 與前端 `me.js` 一致)。實測「上海大劇院 / 上海大剧院 / Shanghai Grand Theatre」「台中 / 臺中」「金沙 / Sands」「電通四季劇場 / 電通四季劇場（海） / [海]」「「國家戲劇院」」皆互通。場館顯示改「English 原文」。
- **修正純中日韓名場館被丟棄**:`norm_venue` 對無拉丁 token 的名字回空 → `add_venue` 原本直接跳過,害大阪/有明/電通四季劇場等整批不進 catalog;改為以去括號名當 key 保留(catalog 多救回 ~41 個)。
- **場館英文名**:亞洲場館用 Google Places `languageCode` 取英文 + 原文(`venue_names.py` / 各 `*_venues.py`)。
### 修正
- **個人地圖右側空乏區**:Leaflet 縮太遠時世界 < 容器寬 → 依容器寬設最小縮放(世界填滿)+ `maxBounds` 擋虛空(`me.js`)。
### 工具/CI
- `scrapers/geocode_google.py` 改增量(只補新場館,`--all` 重跑);TM 金鑰亦支援 `.tm_key`(gitignore)。
- CI workflow 加 `pip install opencc-python-reimplemented`(gen_catalog 繁簡需要);`data/_*` 與金鑰檔全 gitignore。

## [v0.15.2] - 2026-06-12 17:19
### 修正(用戶:劇院座標亂標、誤差要 ≤30m;以及時間亂填)
- **全場館座標重做到建築級(目標 ≤30m)**:用戶抓到 Diamond Head Theatre 偏 3km(geocode 誤抓火山地標)。全面 audit 發現**原始資料 300 個場館座標偏 >30m**,最誇張 Showcenter Complex(Monterrey)偏 **2,319 km**、McKelligon Canyon 911 km、Capital Theatre(London)47 km。
- **解法**:用 **Google Places API (New)** 對全部 547 場館取建築級座標,名稱比對驗證;28 筆「正名/原文名/母體館名」(如 Murat Centre→Old National Centre、Hayes Hall→Artis-Naples)經城市地址比對確認後併入。**1134 場次座標更新**,bbox 複查全清、主地圖無海上落點。
- **新增場館級座標修正機制** `data/venue_coords.json`(`build_shows.py` 套用,一筆修好該場館所有場次,亦餵入 catalog)。
- **新工具**:`scrapers/geocode_google.py`(Google 權威 geocode,金鑰走 `.gitignore` **絕不入庫/不上線**)、`scrapers/audit_geo.py`(離線國家邊界框健全檢查)。
- **時間戳更正**:先前 v0.15.0 / v0.15.1 的 CHANGELOG 時間誤用 bash `date`(此環境慢 8 小時)而寫錯,已依 git commit 真實時間更正為 16:17 / 16:31。

## [v0.15.1] - 2026-06-12 16:31
### 變更(My Musicals 配色重做 — 真正 follow FlightRadar24)
- **每張統計卡整片實色**(用戶:之前全白底+橘 bar「像小學生做的」):Top 劇目=綠、國家=琥珀、城市=紅、劇院=紫;Per Year=藍綠、Per Month=藍、Per Weekday=靛——皆為漸層實色卡。
- **卡內元素全白**:橫條改白色填充 + 半透明白軌、標籤/數值白字;**摺線圖改白線 + 半透明白填充 + 半透明白格線/刻度**(對應 FlightRadar Flights per year/month/weekday)。
- **頂部改深色 hero stat strip**:深灰底白大數字 + 底部七色彩虹分隔線(對應 FlightRadar 個人頁頂欄)。
- 移除未使用的 `FR_ORANGE` 常數。

## [v0.15.0] - 2026-06-12 16:17
### 變更(My Musicals 11 項改版 + 主頁 header / 時間軸)
- **`me.html` 全面 FlightRadar24 風改版**:全英文 UI、Roboto 字體、橘色 `#f89800` 主色;**地圖移到頂部放大(460px)**、海報**圖卡 marker**(非地標釘,重用 `.poster-pin`,以劇名→group→`posters` 查表)、總計格大寫標籤、My Log 改**雙欄海報縮圖卡**。
- **每年/每月/每週幾改折線圖**(Chart.js `line`,橘色填充);Top 劇目/國家/城市/劇院維持橫條。
- **紀錄可編輯**:每筆 Log 有 Edit/Delete;表單以隱藏 `id` 區分 insert / `update().eq("id",…)`,共用同一 dialog。
- **自動帶入擴充**:幣別(`currencies` 字典,選後存幣別代碼)、**劇名中英雙搜**(`titles` 為 `{en,zh,group}`,輸入「西貢」或「miss」皆命中「Miss Saigon · 西貢小姐」);選劇院自動帶城市/國家。
- **「新增一場音樂劇」**(原「記錄一場」)、地圖標題改「My Musicals Map」。
### 主頁(index.html)
- **頂部 header bar(stayplot 風)**:左 `MusicalMap` 品牌、右側醒目膠囊鈕 **「⭐ 我的音樂劇足跡」**(原文案「我的觀劇足跡」用詞怪、且只是側欄小連結太不醒目)。
- **時間軸改月份粒度**:`type=month` 選擇器 + 月份 slider(本月→+36 月);判定改「**演出期間只要跨過該月份就顯示**」(`overlapsMonth`:run 與該月任一天重疊即入)、播放改每月一格、「今天」鈕改「本月」。
### 資料
- USA/UK 國家名正規化(`United States Of America`→`USA`);入場須知雜訊括號從劇名清除(`clean_title` 同時套用 source 與 TM)。
- 共 1123 筆;字典 497 場館(去重)/ 332 劇名(30 含中文)/ 329 海報;稽核全過(海報 406 清晰、連結 DEAD=0)。

## [v0.14.1] - 2026-06-12 15:06
### 變更
- 接上 Supabase 專案(`js/config.js`:Project URL + publishable key,皆公開值、RLS 保護)。資料庫 schema 已套用、三表(profiles/sightings/venues)經 REST 驗證就緒。剩使用者端 Google OAuth 啟用即全線上。

## [v0.14.0] - 2026-06-12 14:44
### 新增(進階功能:My Musicals 個人觀劇足跡 — 第一階段)
- **帳號系統(Google 登入)**:架構選 **Supabase(Postgres + Auth)**,理由是面向未來上萬用戶——分析(Top/per-year-month-weekday)是 SQL 聚合、可擴跨用戶/公開 profile、劇院字典可群眾外包成長;仍部署在 GitHub Pages 純靜態(supabase-js client SDK 直連)。
- **`me.html` 個人頁**:登入後可記錄看過的音樂劇(日期/時間/國家/城市/劇院/劇名/座位/票價/幣別/備註),自動生成 5 個總計格 + Top 劇目/國家/城市/劇院 + 每年/每月/每週幾長條圖(Chart.js)+ 個人觀劇地圖(Leaflet)。
- **智慧自動帶入**:輸入「國家」即浮現國家戲劇院/國家音樂廳/臺中國家歌劇院/衛武營… (字典 `data/venues_catalog.json` 由現有 1125 筆 + 台灣/亞洲主要表演廳種子,`gen_catalog.py` 產出、納入每日 CI);選劇院自動帶入城市/國家/座標。
- **資料安全**:`supabase/schema.sql` 用 Row Level Security——每人只能讀寫自己的紀錄;profiles 預留 `is_public` 供未來公開分享 profile。
- **`docs/SETUP_ACCOUNTS.md`**:Supabase 專案 + Google OAuth 逐步設定清單(此步需用戶自己的 Google 帳號;`js/config.js` 占位,貼上 Project URL + anon key 即啟用)。
### 現況
- 前端全部完成並可部署(未登入頁正常顯示);**待用戶建 Supabase 專案並貼 2 個值後**登入/記錄/統計即上線。anon key 為公開金鑰(RLS 保護),不入任何私密金鑰。

## [v0.13.1] - 2026-06-12 13:39
### 修正(用戶:雪梨/奧克蘭怎麼又消失了)
- **嚴重去重 bug**:TM 合併用「國家」當涵蓋單位——我手動加了 2 筆澳洲 Beetlejuice,就讓整個 Australia 被判為「已涵蓋」,**TM 抓到的所有澳洲站(Anastasia/Lion King/My Fair Lady…雪梨)整批被跳過**;同理影響任何「有零星 manual/intl 紀錄」的國家。
- **修法**:徹底移除國家層級判定,改為**純 (劇, 城市) 去重**(城市鍵已正規化大小寫/州別後綴);TM 兩檔之間也互相去重。雪梨區恢復 12 部、AU 21、NZ 13(Auckland 7)。
### 資料
- 共 1125 筆;稽核全過(海報 406 清晰、連結 DEAD=0)。

## [v0.13.0] - 2026-06-12 13:09
### 新增(雙軸查證體系 — 用戶定義的方法論落地)
- **`docs/TOUR_SWEEP.md` 雙軸查證總表**:軸①從劇出發(每劇查在哪演)＋軸②從城市出發(每城查演什麼),逐項記錄查證狀態與日期,「查證為無」也算完成,未查證一律標「待查」。
- **軸① `tm_tours.py`**:對全部 221 部已列劇目逐一做 TM attraction 嚴格比對(名稱正規化全等才收),109 部命中、420 個場館站;Beetlejuice NA tour 等 broadway.org 沒有的巡演由此補齊。
- **軸② `madrid.py`(teatromadrid.com)**:馬德里 55 部,**西語標題正名映射**(El Rey León→The Lion King、Sonrisas y lágrimas→The Sound of Music、Cenicienta→Cinderella、Los miserables→Les Misérables…用戶點名 6 例全數驗證正確);場館未定/geocode 失敗一律剔除不堆假點。
- **ATG tour hub(phase 2 完成)**:33 條 UK 巡演 **201 站**(站點 JSON 嵌在 hub RSC)。
- **官網對照表 `official_sites.json`**:分區官網(UK 卡只放 UK 官網)置於售票連結上方;Beetlejuice us/uk/au 三區、Chicago、HSM(disneytickets)等 17 組。
- **web 查證入庫**:Beetlejuice 澳洲(Brisbane QPAC qtix/Adelaide,用戶抓到的 TM 外盲區)、Les Misérables Arena Spectacular(Birmingham 現在/RAH/Radio City)、Chicago 國際(東京/大阪/杜拜,官網 /international)。
- 查證為「無進行中巡演」:Aladdin UK(2025/1 止)、Lion King UK、Wicked UK(2023-25 止);Hamilton 墨爾本因官方日期未確認**不入庫**(Ticketek 盲區已登記)。
### 修正
- **group_key 過度剝除**(High School Musical→"high" 真實 bug)→ 尾部剝除必須含 "the"。
- **城市鍵正規化**("Boston, MA"≠"Boston" 導致同站重複)→ 合併 17 筆重複。
- Interpark 把「字幕眼鏡租借」等服務商品當劇(用戶抓到假 Billy Elliot)→ JUNK 過濾。
- ATG 海報抓到 srcSet 最小檔(375px 模糊)→ Cloudinary 參數改寫 w_1280;URL HTML entity 未解碼修正。
- TM US 由「純連結豐富」升級為「NYC 以外可補 marker」(broadway.org 巡演清單證實不完整)。
### 資料
- **共 1084 筆**(去重後);海報稽核 375 張全清晰;連結稽核 DEAD=0。

## [v0.12.0] - 2026-06-12 11:54
### 修正（用戶連續指出的卡片/連結問題，全面處理）
- **「常駐演出中」全移除；「售票至 X」廢除**：起始日其實大多在資料裡，是顯示邏輯吞掉。新格式——有完整檔期顯示「start – end」；長壽劇（檔期>2.5 年者，end 只是滾動售票線非閉幕日）顯示「自 start 上演」；僅知結束顯示「演至 end」。
- **londontheatre 死連結 153 個**（Pride／Dark of the Moon 等，用戶抓到）：正式連結格式是 `/show/{數字id}-{slug}`，我只用 slug 拼。改用產品數字 id 重建 → **連結稽核 DEAD 歸零**。
- 新增 `scrapers/audit_links.py`：全量 GET 每個購票連結。Ticketmaster 對 bot 回 401 但真瀏覽器完整渲染（playwright 驗證）→ 歸類 bot-block 非死連。
- **Elisabeth 海報**換用用戶指定的官方劇目海報（NDM A1 1st cast）。
### 新增（用戶要求）
- **官網 vs 售票平台分流**：連結標記 `kind`（official＝劇團/製作方/劇院自營：四季、宝塚、Stage、上海大劇院、NDM；ticketing＝第三方票務），大卡分「官網：」「售票平台：」兩列；單連結按鈕文案也跟著區分。
- **大型售票平台並列**：TM 掃描加回 US 作純連結豐富（不加重複 marker）——已被 curated 涵蓋的劇，TM 的 show 頁（artist 連結）自動掛入售票平台列。例 Ragtime 紐約＝Broadway票務＋Ticketmaster。共 47 筆獲 TM 連結、全站 52 筆有多購票來源。

## [v0.11.0] - 2026-06-12 11:08
### 新增
- **ATG Tickets scraper**（`atg.py`，英國地方圈）：**無公開 API**（實測 GraphQL 僅會員服務）→ 解析 SSR 卡片＋分頁。含日期的單場館紀錄收錄；無日期者剔除（細節頁日期 JS-only，不讓未開演的誤顯為上演中）；33 個「Tour (N Venues)」卡需逐 hub 爬＝phase 2（已登記）。
- **Stage Entertainment scraper**（`stage_de.py`，德國）：**無公開 API** → SSR 解析。漢堡/柏林/斯圖加特 13 部駐演（TINA、Tanz der Vampire、Frozen、獅子王、MJ、回到未來、&Juliet…），自有劇場座標表；劇場判定用「頁面提及 ≥2 次」（nav 會提到所有劇場，首次匹配會錯）。
- **跨來源同劇同城合併＋多購票連結**（用戶要求）：同一齣在同城市被多個售票源列出時，保留最權威紀錄、**所有來源的購票連結並列在大卡**（「購票來源：LondonTheatre →｜ATG →」）。本次合併 9 筆（Wicked/獅子王/Paddington 倫敦＝LondonTheatre+ATG；獅子王/MJ 漢堡＝Stage+Disney…）。
### 資料
- 共 604 筆。

## [v0.10.1] - 2026-06-12 10:44
### 修正（用戶質問 Miss Saigon 為何缺漏 — 結構性盲區）
- **根因（誠實承認）**：londontheatre.co.uk 只涵蓋倫敦西區，而我接 Ticketmaster 時以「英國已被涵蓋」為由把 GB 整國剔除——「倫敦 ≠ 英國」，整個英國地方巡演圈成為盲區。Miss Saigon UK & Ireland Tour 正在進行（6/12 當天在 Glasgow King's Theatre）卻不在地圖上。
- **修法**：(1) TM 加回 GB，build 改為「GB 僅排除倫敦市，其他城市保留」＋(劇,城市) 級去重防重複；(2) Miss Saigon 已驗證的 4 個現在/接下來巡演站入庫（Glasgow 6/9–6/20、Blackpool、Canterbury、Bristol，官方 1920×1080 主視覺）；(3) TM GB 另帶入 8 筆英國地方巡演。
- 畫質稽核：265 張全清晰。
### 資料
- 共 595 筆。

## [v0.10.0] - 2026-06-12 10:31
### 新增
- **韓國 Interpark scraper**（`interpark.py`，world.nol.com 開放 JSON API）：59 部音樂劇、39 筆含座標（首爾 32／大邱 6／大田 1，含 Billy Elliot @ BLUE SQUARE、Lempicka、Sleep No More Seoul @ 舊大韓劇場）。**真實開演/結束日**（非可購票窗）。韓國主要場館座標表（首爾＋大邱 DIMF 場館）；查無座標的一律剔除並列報告，絕不亂放。
### 變更（用戶要求）
- **全面恢復原圖**：移除所有 CDN 縮圖/壓縮參數與本地壓縮副本（Elisabeth 還原 NDM 原圖），一律載入官方原始大圖——畫質優先於載入速度。
### 修正（圖片畫質全面體檢）
- 新增 `scrapers/audit_images.py`：實際下載量測每張海報像素，小於 popup 顯示尺寸（高 340px）即列為模糊。**全 259 張通過、0 模糊 0 失效**。
- **劇団四季海報 200×132 縮圖**（用戶截圖指出 Mamma Mia/A Chorus Line 模糊的根因）→ 改用 `/shared/images/ogp/{enmoku_id}.jpg`（1200×630）。
- **宝塚**改用各製作真實主視覺（revue 總覽縮圖；官方未發佈者 fallback 劇團 og 圖）。
- **Interpark 海報**：`goodsLargeImageUrl` 大量 404 → 改用 `posterImageUrl`（`_p.gif`）。
- Interpark API 分頁陷阱：size 參數被靜默 cap（要求 50 仍回 ~15）、totalPages 按要求 size 計算不可信 → 改逐頁抓到空頁／滿 totalElements。
### 資料
- 共 584 筆（新增南韓 39）。

## [v0.9.0] - 2026-06-12 09:45
### 新增
- **劇団四季 scraper**（`shiki.py`，shiki.jp 的 `api_stage_list` JSON API）：日本 9 劇場 10 製作含精確檔期（東京 Frozen/BTTF/阿拉丁/獅子王/A Chorus Line、橫濱 Mamma Mia!、舞濱小美人魚、名古屋歌劇魅影、大阪鐘樓怪人）。日文劇名映射為英文正名以便全球同劇合併。全国ツアー無固定城市，誠實未收（記於 SOURCES）。
- **宝塚歌劇団 scraper**（`takarazuka.py`，kageki.hankyu.co.jp）：6 製作 12 檔（宝塚大劇場→東京宝塚劇場接力），含寶塚版 Elisabeth（花組，宝塚 10/17–11/22、東京 12/19–2027/2/7）— 與捷克 Ostrava 版自動合併為同一齣三地。
- **`docs/SOURCES.md` 來源登記表**（用戶要求）：用戶提供的每個網址登記日期與狀態，新來源先查表。
### 修正
- broadway.org 的日本資料過時（獅子王還列舊 HARU 劇場）→ build 改以 shiki.jp 為日本權威來源，自動剔除被取代的過時紀錄（3 筆）。
- Takarazuka 解析：劇場區塊改按位置切段，第二劇場的檔期不會誤掛到第一劇場；id 含起演日避免同館兩檔互覆。
### 資料
- 共 545 筆。

## [v0.8.1] - 2026-06-12 02:13
### 修正
- **Elisabeth 海報載入極慢**（用戶回報）：NDM 為無 CDN 的劇院自家伺服器且不支援縮圖參數，marker 每次都抓 1200×540 原圖（393KB 跨洲）。改為下載壓縮後自家託管（`assets/posters/`，640 寬 20KB，走 GitHub Pages CDN）。日後 manual 來源遇到慢速圖源一律比照辦理（已記入 manual.json 規範）。

## [v0.8.0] - 2026-06-12 02:03
### 變更（用戶決定）
- **移除「常駐／巡演」分類功能**（checkbox、色點、卡片標籤、marker 色框全拿掉；分類難以準確定義）。marker 統一白框。
### 修正
- **Mamma Mia 合併失敗**（用戶指正）：(1) 通用化副標剝除——破折號/冒號後含 "musical" 的行銷副標一律去除，任何語言（Das Hit-Musical auf Schweizerdeutsch / The Broadway Musical…）；(2) en/em-dash（–/—）先轉成 `-` 再做 ASCII 轉換（原本直接被丟掉導致規則失效）。Mamma Mia 現為一組 22 地（倫敦＋北美巡演＋維也納＋布雷根茨＋蘇黎世）。
- **Elisabeth 海報**：NDM 官方劇照（已驗證載入）；NDM 官網連結修正為 `/inscenation/` 路徑（原 `/titul/` 404，用戶指正）。
- **Roméo et Juliette 海報**：Live Nation 官方主視覺，8 站全套用；新增 Live Nation CDN 縮圖參數支援與 URL query 安全拼接。
- manual.json 三個官方連結全數驗證 200。
### 資料
- 共 526 筆。

## [v0.7.0] - 2026-06-12 01:46
### 修正（自我迭代掃漏 + 模擬全部用戶動作，8 項情境測試全過）
- **小卡/大卡交互**：大卡開啟時小卡立即關閉且不再彈出（原本兩卡重疊）；低 zoom 點 marker 改為「先單一動畫飛入 → 到位才開大卡」（原本大卡先開再飛、雙動畫；另修 zoomToShowLayer 對未聚合 marker 不縮放的問題）。
- **側欄 hover**：marker 被聚合在圈圈內時不再彈出懸空小卡（檢查 `_icon` 可見性）。
- **側欄展開狀態**：拖滑桿/搜尋造成重繪時，已展開的劇保持展開（原本每次重繪全部收合）。
- **滑桿效能**：input 事件以 rAF 節流（原本拖動時每 tick 全量重建 marker）。
- **手機**：大卡寬度以視窗寬度夾住，不再超出螢幕。
- **巡演分類**（用戶指正）：Ticketmaster 限期檔期改歸「巡演」（原誤標常駐，導致勾巡演只看得到美國）；東京四季、漢堡等經年駐演維持「常駐」。
- **同劇合併漏洞**：group key 先去重音（Misérables 的 é 原被當斷詞）；別名表合併 MJ（紐約/漢堡/伯斯三地現為一組）、Spamalot、Les Mis。
### 新增
- **`data/manual.json` 人工策展來源**：收錄各地自有售票系統的劇（隨發現隨補）：《劇院魅影》40 週年上海告別季（上海大劇院 9/29–11/29，經官方 API 查證）、Roméo et Juliette 2027-28 法國巡演（巴黎駐演＋7 個 arena 站，Live Nation FR）、Elisabeth（捷克 Ostrava NDM repertory，2024/12 首演–2027/6）。
- 滑桿範圍延長至 **+730 天**（原 365 天拖不到 2027/12 起的 Roméo et Juliette）。
### 資料
- 共 526 筆。

## [v0.6.1] - 2026-06-12 01:23
### 修正
- **真實開演日補齊（上網查證 + hardcode）**：API 證實無法提供開演日（13 個日期參數全為「未來場次池的過濾器」，過去窗口實測回 0 筆；onsale 系列是開賣日非開演日）。改以官網/媒體逐筆查證 11 個被截斷的製作，寫入 `overrides.json`（含來源註記）：Anastasia 雪梨 4/7–7/19、Lion King 雪梨 4/18–、HAIR 雪梨 6/6–7/11、MJ 伯斯 6/6–7/19、Spamalot 伯斯 5/20–、Tootsie 雪梨 5/26–、Priscilla 都柏林 6/8–6/13、Are Ya Dancin' 都柏林 6/9–6/13、Heathers 奧克蘭 6/10–6/14、Tērā te Auahi 羅托魯瓦 6/10–、MAMMA MIA! 蘇黎世 5/6–6/14。查證後清除 `onsale_only` 旗標，卡片顯示真實檔期。

## [v0.6.0] - 2026-06-12 01:15
### 新增
- **時間軸**：地圖下方時間列＝日期滑桿＋日曆（雙向同步）＋「今天」鍵＋「▶ 播放」（每秒推進一週，可看巡演在城市間移動）。範圍今天～+365 天。拖到哪天就顯示那天上演中的劇；側欄計數同步顯示所選日期。
### 修正（Ticketmaster 日期語意，用戶指正）
- **認知修正**：TM 的最早場次＝「目前最早可購票日」（過期場次會從 API 消失），**不是真正開演日**；end 為最後排定場次。已查證 Anastasia 雪梨站：API 僅 6/12–7/18 共 36 場，4/7 開演日不存在於 API、7/19 查無場次。
- 不造假日期：撤回「start 改成今天」的 grace hack（會造成巡演換城 10 天內同劇兩地同時顯示）。改為保留真實可購票窗 + `onsale_only` 旗標，卡片誠實顯示「售票中 · 約演至 X」。
- TM 只掃 curated 未涵蓋國家（澳/紐/愛/加/比/丹/義/瑞典等 16 國）並抓滿所有分頁 → end_date 為真實最後場次；亦省 API 額度。
- 標題正規化補強：`(Australia)` 等區域括號、無障礙場次（Auslan/Audio Described/Relaxed/Captioned）、`- Opening Night`、測試 event 過濾 → 同劇正確合併。
### 資料
- 共 516 筆（80 常駐 ＋ 297 北美巡演 ＋ 13 國際 ＋ 126 TM 補洞）。

## [v0.5.0] - 2026-06-12 00:36
### 新增
- **Ticketmaster Discovery API 全球來源**（`scrapers/ticketmaster.py`）：掃 18 國票務站，分類過濾（只留 musical subGenre）、同劇同場館跨國去重、每地區售票連結收進卡片、髒標題清理。以「未涵蓋國家補洞」策略併入（只加澳/紐/愛/加/比利時/北歐等 curated 沒有的國家，避免與美/英重複）→ 新增 125 個製作。
- **衛星地圖**：右上角可切換「地圖／衛星」（Esri World Imagery，免 key）。
- popup 多地區售票連結（同劇跨國時各地連結並列）。
### 修正
- **cluster 圈圈縮放**：原本 33 以上全頂到上限變一樣大（35/38 同尺寸），改為實際範圍內遞增，數量大圈圈確實較大。
- **hover 卡片字體超框**：Leaflet tooltip 預設不換行，長劇名溢出 → 改為自動換行。
### 資料
- 共 515 筆（80 常駐 ＋ 297 北美巡演 ＋ 13 國際 ＋ 125 Ticketmaster 補洞，涵蓋約 20 國）。
- CI 加 `TICKETMASTER_API_KEY` secret 支援（未設則保留既有資料）。

## [v0.4.1] - 2026-06-12 00:10
### 變更
- popup 海報改為**撐滿卡片高度**（上下到滿、寬度依比例自動變寬），消除海報下方留白；卡片寬度自適應。

## [v0.4.0] - 2026-06-12 00:00
### 新增
- **國際製作來源**：新增 `scrapers/intl.py`，抓 broadway.org/broadway-shows-international，納入非英美的全球駐演（巴黎、漢堡、科隆、東京、墨西哥城、烏特勒支、馬德里等 13 個）。含各劇海報。
- 著名劇院手動座標表（東京 4 個 Shiki 劇院、漢堡 Stage 劇院等），解決同城多劇院全疊在市中心的問題。
### 變更
- **popup 海報改完整呈現**：改用 `<img>` 依原始比例顯示完整海報（不裁切、不黑邊），未裁切 CDN 原圖，popup 加寬。
- **cluster 圈圈改線性縮放**（30px–88px，字級隨之），數量差距更明顯。
- **訂票按鈕**文案明確化為「前往官方售票頁 →」。
### 修正
- **正式劇名覆蓋**：`Phantom of the Opera`（官方名不帶 The），套用於 popup／側欄／hover 標題與巡演名。
### 資料
- 共 390 筆（80 常駐 ＋ 297 北美巡演 ＋ 13 國際）。

## [v0.3.0] - 2026-06-11 23:43
### 新增
- **全美巡演彙總**：新增 `scrapers/broadway_tours.py`，從 broadway.org/tours（The Broadway League 官方）**一支 scraper 抓全部 28 個正在巡演的劇、共 297 個城市站**（取代原本逐劇的 wicked_tour）。含年份推算（排程無年份，依時間順序遞推）與城市中心點 fallback。
- 每個巡演劇抓取**自己的海報** key-art（broadway.org `/assets/shows/`），純巡演劇（Spamalot、Back to the Future 等）也有正確海報。
- **cluster 圈圈大小隨數量縮放**（數字大圈圈大，最小不小於 32px、最大 64px）。
- 低 zoom 點 marker 會**先放大再顯示卡片**（worldwide 不再跳出怪卡片）。
### 變更
- 字卡與海報全面放大（marker 海報 52×72、側欄縮圖 56×80、hover 卡 96px 海報、popup 寬 340 + 海報 140）。
- `build_shows.py` 來源改為 `tours.json`（彙總巡演）；移除 `wicked_tour.py`。
### 修正
- **CI 失敗修正**：push 觸發時不再 scrape/commit（避免與本機 push 競爭 `git push`），只部署；排程觸發才 commit，且 commit 前 `pull --rebase` 並重試；checkout 改 full depth。
### 資料
- 目前 377 筆（80 常駐 ＋ 297 巡演站）；**正在上演的 marker 76 個**（含 19 個正在巡演的劇橫跨北美），全部含座標與海報。

## [v0.2.0] - 2026-06-11 23:05
### 新增
- **海報視覺**：地圖 marker 改為各劇海報縮圖（依「常駐／巡演」加藍／紅色框），一眼辨識。
- **hover 資訊卡**：滑鼠移到 marker 顯示海報＋劇名＋劇院＋檔期。
- **popup 改版**：左側大海報＋訂票 CTA 按鈕。
- **同劇合併（標題正規化）**：同一齣戲在不同來源命名不同（如 `SIX` ↔ `SIX: The Musical`、`Mamma Mia!` ↔ `Mamma Mia`）會自動歸為同一組；側欄一劇一列。
- **多地點 overview**：點擊同時在多地上演的劇（如 Wicked：紐約＋倫敦＋巡演），地圖自動縮放到該劇全球所有地點，並展開卡片可再鑽進單一地點。
- **巡演資料**：新增 Wicked 北美巡演 scraper（`tour.wickedthemusical.com`，17 站，含當前城市判斷）。
- **巡演海報繼承**：巡演紀錄自動沿用該劇海報（不再顯示音符占位）。
- scraper 補抓海報圖（West End：Contentful `productMedia.posterImage`；Broadway：`verticalImage`）。
- **體驗細節**：載入時自動縮放到所有 marker、側欄↔地圖 hover 雙向連動、搜尋無結果空狀態、圖片載入失敗以音符（♪）替代、CDN 參數即時縮圖加速。
- **提交防呆機制**：`.githooks/pre-commit`（改 code 沒更新 CHANGELOG 會擋）、`docs/WORKFLOW.md` 提交流程、本 CHANGELOG。
### 變更
- **整體改為淺色主題**（白底面板＋slate 灰字＋teal 主色＋圓角），地圖底圖改用淺色 CARTO Voyager（原 dark 底圖在 dark mode 下幾乎看不見）。
- 移除先前的假巡演示範資料（`tours.json`），改用真實 Wicked 巡演。
### 資料
- 目前涵蓋 97 筆（Broadway 28 ＋ West End 52 ＋ Wicked 巡演 17），全部含座標與海報。

## [v0.1.1] - 2026-06-11 22:36
### 修正
- **Masquerade - Phantom of the Opera Reimagined**：修正 `detail_url`（該劇歸在 `/plays/` 非 `/musicals/`，原本抓不到）；補正實際地址 218 W 57th St（五層樓沉浸式場館，無正式劇院名）。
- **The Lost Boys**：來源誤連曼徹斯特 Palace Theatre，以 `overrides.json` 修正為紐約 Palace Theatre。
- **Two Strangers**：來源 lat/lng 顛倒，自動偵測對調修正。
- 新增 NYC 座標範圍檢查（超出範圍且對調無效則丟棄，避免標錯位置）。
- 補齊 West End 先前 9 間 geocode 失敗的場館座標。
- Broadway scraper 加完整瀏覽器 headers，解決雲端 (GitHub Actions) HTTP 403。
- 結果：82/82 部音樂劇全部有座標。

## [v0.1.0] - 2026-06-11 22:26
### 新增
- Broadway scraper（broadway-show-tickets.com，解析 `__NEXT_DATA__`，含精確座標）。
- West End scraper（londontheatre.co.uk，解析 `__NEXT_DATA__` + OSM Nominatim geocode 快取）。
- Leaflet 地圖 + MarkerCluster + 側欄列表 + 搜尋 + 常駐／巡演篩選。
- 資料層／呈現層分離架構（scrapers → 各來源 JSON → `build_shows.py` 合併 → 前端讀 `shows.json`）。
- GitHub Actions 每日自動重抓 + 合併 + 提交 + 部署 GitHub Pages。
- 安全處理：所有爬取文字 HTML 跳脫、URL 協定白名單。
