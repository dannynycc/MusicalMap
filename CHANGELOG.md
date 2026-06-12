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
