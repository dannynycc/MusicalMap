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

## [v0.69.5] - 2026-06-25 11:38
### 修正 — 城市譯名人工校對(使用者回饋）
- 新增：Wimbledon（溫布頓／温布尔登）、Grand Rapids（大急流城）。
- 台灣譯名修正：Fort Lauderdale 羅德岱堡、Louisville 路易斯維爾、Memphis 曼菲斯。
- 改回英文（台灣不慣用）：Durham、Aalborg、Hartford。

## [v0.69.4] - 2026-06-25 11:16
### 修正 — 低信心台灣城市譯名改回英文（招供 #3）
- agent 標「台灣媒體少見／無標準」的 8 城（Des Moines／Ostrava／Brescia／Hasselt／Trier／Brno／Knoxville／Greensboro）從 `cities`／`cities_tw` 移除 → 中文版顯示英文（不硬塞不確定的譯名）。其餘高信心台灣譯名（雪梨／杜拜／休士頓／聖荷西…）保留。

## [v0.69.3] - 2026-06-25 11:01
### 修正 — 預渲染 SEO 頁日期格式跟 app 一致（招供 #4）
- `build/gen_site.mjs` 給爬蟲/AI 看的預渲染清單,日期原本是舊的 `start – end` ISO 全格式,現改成跟互動版一致的 `至 M/D`／`長期上演`／`M/D 起`（城市/國家在地化早已因 gen_site 讀變體檔而自動套用）。

## [v0.69.2] - 2026-06-25 10:57
### 修正 — 補完城市州 ＋ 清城市錯字 ＋ 國家在地化（主動 audit 自己漏掉的）
- **英文版補完所有美/加城市的州**：上版只補主要城市，自我 audit 發現還有 **67 個缺州**（Honolulu／Atlantic City／Winnipeg／Lexington…）。用**座標精準定州**（Aurora→IL 非 CO、Columbia→MD、Concord→NH）全部補進 `us_ca_state` → EN 缺州城市歸零。
- **清城市錯字**：`San Deigo`→San Diego、`Ft Lauderdale`→Fort Lauderdale、`GATINEAU`→Gatineau（`build_shows` 正規化，連帶修掉地圖重複 marker）。
- **國家在地化**（原本只翻 CN/TW/JP/KR，西方國家在中文版顯示英文如「倫敦, UK」）：補全部國家中文 ＋ **兩岸差異** `countries_tw`（義大利／意大利、澳洲／澳大利亚、紐西蘭／新西兰）。

## [v0.69.1] - 2026-06-25 10:44
### 新增 — 城市名稱在地化（分語言 ＋ 兩岸譯名 ＋ 英文補州）
- 原本西方城市一律英文（London／New York…）。現在分語言處理：
  - **中文版（繁／簡）**：主要世界城市翻中文（~150 城），小鎮（East Lansing…）留英文。
  - **英文版**：統一「City, ST」（美/加州碼）。缺州的城市從**權威對照表回填**（Phoenix→AZ、San Jose→CA、Montreal→QC…），不再因「資料沒有就留空」。
- **兩岸譯名分流**：OpenCC 簡→繁**只轉字、不轉譯名慣例**，故另建 `cities_tw` 台灣譯名覆寫表（**42 城，web 查證**）：雪梨（非悉尼）、杜拜（非迪拜）、休士頓（非休斯顿）、紐奧良、聖荷西、蒙特婁、威靈頓、水牛城、克里夫蘭…；zh-hant 優先用它、否則退回 OpenCC。
- **修城市格式不一致**：同一城市「Boston」與「Boston, MA」兩種寫法並存（不同來源），現統一（EN 一律帶州、中文一律不帶州）。機制 `build/gen_variants.mjs` ＋ `data/i18n_maps.json`。

## [v0.69.0] - 2026-06-25 10:13
### 改進 — 列表日期顯示大改 ＋「長期上演」精準判定 ＋ West End 去重修正
- **列表副標題統一「城市 · 日期」**：原本巡演／駐演／限定三種格式混用、日期更有 8 種講法（很亂）。改為 3 態：有結束日→「**至 M/D**」、開放式長演→「**長期上演**」、本月才首演→「**M/D 起**」、缺日期留白；緊湊格式（跨年才補年份）。
- **「長期上演」改成精準判定**：原本盲信 `type=resident`，把 `j25musical` 的日本 2.5 次元（《網球王子》等 1–8 天短檔）也標長期。改為**只認開放式 sit-down 劇院**（百老匯／西區／Stage Entertainment），且 Broadway 的 end＝滾動售票期、West End／德國認「**無閉幕日且已開演**」。最終 **48 齣**（Broadway 27＋West End 18＋德國 3），逐一查證；West End 有閉幕日的限定檔（Sinatra／The Producers／Kinky Boots 等）正確改顯示「至 X」。
- **修 West End 去重**：Wicked／Lion King 西區原本被 **ATG 爛資料**（`type=tour`＋滾動售票期當閉幕日）蓋過 londontheatre 的正確 `resident` 版。`build_shows` 跨來源去重改成「**來源優先序優先**」（londontheatre＞ATG），不再「有 end 就贏」。
- **Stage Entertainment 德/荷 14 齣補真實日期到 `overrides.json`**（該來源完全不給日期 → 全被誤判長期）：3 開放式（漢堡獅子王 2001-／MJ 2024-／柏林 WIR SIND AM LEBEN 2026-）、6 限定（**Frozen 至 2027/1**＋Back to the Future／Tarzan／We Will Rock You／DIE AMME／Bibi und Tina）、5 未上演（Salon Rosie／Devil Wears Prada／& Juliet ×2／Tanz der Vampire）。**每齣經兩輪獨立 web 查證**：漢堡獅子王自 2001（逾 9,400 場、無接班）；Frozen 雖無確切閉幕日,但接班 Tanz der Vampire 2027/3 進同劇院 → 實質演到 2027/1,故列「至 X」非長期。
- i18n 三語（`至`／`長期上演`／`起`）；`README` 日期語意同步。

## [v0.68.13] - 2026-06-25 00:35
### 改進 — OPENTIX 售票圖示換成官方高清 logo
- OPENTIX 的 favicon 太糊，改 rehost 使用者提供的 **512×512 官方 logo** 到 `logos/opentix.png`，加進 `js/app.js` LOGO_MAP（host `opentix.life` 匹配）。
- 重建 HTML 刷 cache-bust；README 的 LOGO_MAP 說明同步。

## [v0.68.12] - 2026-06-24 23:26
### 修正 — 東歐/南歐當地語言「進口劇」誤標歐陸、沒併入正典（& Juliet 同病根的系統性盤點）
- 延續 & Juliet：當地語言標題的**進口劇**（同曲同本的授權版）沒被登記為別名 → 自成一群＋誤標當地 tradition。
- 9 個 agent 並行分類 **103 個歐陸候選**，嚴格區分「進口授權版」vs「當地原創」——**同源故事各自獨立創作的算原創、不亂併**（如匈牙利《叢林奇譚》是 Dés László 原創、非迪士尼；義大利《小飛俠》是 Bennato 原創）。**94 個確認當地原創，維持不動。**
- 揪出 **9 個進口劇**補進 `works.json`（166→170 筆），全部歸位英文 group ＋統一 Broadway/West End：Muzikál CHICAGO→Chicago、Producenti→The Producers、A muzsika hangja→The Sound of Music、GREASE O MUSICAL→Grease、Annie julen→Annie、Anyatigrisek→Motherhood the Musical、Rocky Il Musical→Rocky、Il Principe d’Egitto→The Prince of Egypt、Brokeback Mountain（瑞典）。
- `README`／`DESIGN_productions` works 數 166→170。本機完整重建直接 commit（push deploy，無 CI race）。

## [v0.68.11] - 2026-06-24 22:33
### 修正 — & Juliet 荷蘭製作沒併入（別名拼錯，被當成另一齣＋誤標歐陸原創）
- 使用者抓到搜「& Juliet」出現兩筆：主 & Juliet（百老匯＋北美巡演＋斯圖加特）和「**& Juliet de powerpopmusical**」（Beatrix Theater Utrecht，荷蘭 Stage Entertainment 製作）。後者其實是**同一齣的荷蘭製作**，卻自成一群、誤標「歐陸原創」。
- 根因：`works.json` 的 & Juliet 別名寫成「& Juliet de **pop**musical」（少了 power），與實際標題「de **powerpop**musical」對不上 → 沒收斂。
- 修法：別名補上「& Juliet de powerpopmusical」。重建後 Utrecht 併入 & Juliet（group `juliet`、tag Broadway/West End），側欄合為一齣 19 個地點。
- 本機完整重建直接 commit（push deploy，無 CI race）。

## [v0.68.10] - 2026-06-24 22:14
### 文件 — MD freshness（補 v0.68.6–v0.68.9 漏掉的文件同步）
- `README.md`：`works.json` 158→**166 筆**；檔案表**新增 `data/official_sites.json`**（184 筆、作品官網主檔、分區 map ＋「掛 `kind:official`→劇名標題超連結」機制）；現況「同劇合併」補上**同座標去重**。
- `docs/DESIGN_productions.md`：works.json 158→166。

## [v0.68.9] - 2026-06-24 22:03
### 修正 — 同一場館被兩來源標不同 city → 地圖上兩個重複的點（座標去重）
- 使用者抓到 Jersey Boys 在 New Wimbledon Theatre 出現**兩個點**：同座標，但一來源（londontheatre）標 city「London」、另一來源（ATG）標「Wimbledon」（Wimbledon 是倫敦一區）。既有的 `(group, city, venue)` 去重因 city 不同而抓不到。
- `build_shows` 新增「**同 group + 同座標**」去重（在座標校正之後）：同座標＝同一個實體場館，合併雙方售票連結（含尚未陣列化的 `ticket_url`）＋取最寬日期範圍，最完整者存活。
- 全站合併 5 組（Jersey Boys／SIX／Lion King／Les Misérables／Trainspotting）。嚴格驗證：1608→**1603 ＝ 不重複的 (group,座標) 數**，**0 場次誤刪**。Jersey Boys 現 1 點、5 個連結全保留（官網＋TodayTix＋LondonTheatre＋ATG＋Ticketmaster）。
- 本機完整重建直接 commit（push deploy，無 CI race）。

## [v0.68.8] - 2026-06-24 21:43
### 修正 — CI race 把帶 git 衝突標記的壞變體部署上線（官網沒顯示的真因）
- 症狀：手動觸發 CI 後 Avenue Q 等官網標題連結**還是沒出現**。根因有二：
  1. **CI race**：一個較早的 run 用**舊的 16 部** `official_sites.json` 建出 270 筆官網，其資料 commit 經 `git pull --rebase` 乾淨疊到 v0.68.7 之上（`943f7be`）；我的手動 run 建出**正確的 1022 筆**，但 commit step 的 rebase 撞上它 → `shows.json` 衝突 → working tree 留下 `<<<<<<<` 標記 → 被「Upload Pages artifact」**原樣部署** → 線上變體 JSON 損毀。
  2. 結果：git HEAD 乾淨但資料舊（270 筆），**線上實際是帶衝突標記的壞檔**。
- **修法**：本機完整重建（`build_shows` + `gen_variants` + `gen_site`）→ `shows.json`／三語變體 **1022 筆官網、0 衝突標記、Avenue Q→`avenueqmusical.co.uk`**，直接 commit；由 **push 觸發**的 deploy 跳過 scrape／data-commit、直接服務 committed 檔（無 race）。
- **硬化 workflow**：commit step 的 rebase 衝突時 `git rebase --abort`，**絕不讓衝突標記進到 Pages artifact**，防止再次部署壞檔。

## [v0.68.7] - 2026-06-24 20:40
### 新增 — 補齊百老匯/西區缺漏官網（official_sites.json 108→184）
- 使用者抓到 Avenue Q 等純英文百老匯/西區劇**沒有官網標題連結**。根因：`works.json` 註冊表只收非英語劇種／有外語別名的劇，純英文 Anglo 劇被省略 → **從沒被研究到**。
- 對地圖上 **549 個作品**做覆蓋盤點（之前只有 84 個有官網）。抓出 **157 部缺官網的百老匯/西區**，10 個 agent 並行研究（過濾無障礙場次／地方劇團／演唱會／翻譯版／junk）。
- 新增 **76 部**官網（81 部確認無單一官網→null：Cinderella／Guys and Dolls／Into the Woods 等授權經典＋雜訊條目）。`official_sites.json` **108→184**。
- 實測 `build_shows`：官網掛載 678→**1006 筆**（**1026/1607 shows** 有官網連結，43%→64%）；**Avenue Q→`avenueqmusical.co.uk` 已修**；分區續用（Titanique／Operation Mincemeat 等 US/UK 分流）。
- 下次 CI scrape 重建 `shows.json` 後上線。

## [v0.68.6] - 2026-06-24 20:15
### 整併 — 官網資料合併進 `official_sites.json`（單一來源、全面 wire）
- 背景：兩個 session 平行做官網——`official_sites.json`（16 部、已 wire 進 build_shows）與 `works.json` 的 `official`（107 部研究、未 wire）分歧，只有 16 部生效。
- 把 works.json 的 **107 部研究合併進 `official_sites.json`**：`canonical`→`group_key`、`default/USA/UK/Australia`→`global/us/uk/au`；既有資料優先、僅補缺（保留對方更準的 UK 變體如 Beetlejuice `beetlejuicemusical.co.uk`）。現 **108 部**。移除 `works.json` 重複的 `official` → 單一來源、避免分歧。
- 實測 `build_shows`：掛上 **678 筆** region-appropriate 官網（**699 shows** 有官網連結）；Wicked 美版→`.com`、英版(倫敦)→`.co.uk` 正確分流。
- 顯示沿用既有新 rule（官網＝**標題**超連結、非售票圖卡，不搶 affiliate 點擊）。`shows.json` 由下次 CI scrape 重建後上線。

## [v0.68.5] - 2026-06-24 19:00
### 修正 — popup 文字＋圖卡溢出白框（我 v0.68.2 用 fit-content 引入的 regression）
- 根因(實測):`.pop-body { width: fit-content }` 讓 **Leaflet 量錯** popup 寬度——量成 574px 設定白框,實際 render 718px → 整個右半塊(**標題/場館/日期文字 + 售票圖卡**)超出白框右緣約 127px。
- 修法:(1) `.pop-body` 改**確定寬度**(由 `popupHtml` 依圖卡數 inline:3+ 卡 380px、否則 280px) + `box-sizing: border-box`,Leaflet 才量得準;(2) `.pop-poster` 加 `max-width:340px; object-fit:cover` 防超寬海報把 poster+body 推爆 maxWidth。poster(≤340)+body(≤380)=720 剛好在 maxWidth 內。
- 驗證:headless 真 Leaflet popup 量 4 種(Mamma Mia 3卡/OPENTIX 1卡/SIX 4卡/Paddington)文字與圖卡右緣**全 ≤ 白框右緣**,並截圖目視確認在框內。單一來源面板較窄(280)、圖卡維持 110px。

## [v0.68.4] - 2026-06-24 18:37
### 修正 — 售票圖卡標籤空白(OPENTIX 等沒帶 label 的來源)
- 部分 scraper(如 opentix)的 `ticket_links` 不帶 `label` 欄位 → 圖卡只有 icon+箭頭、**標籤一片空白**。原本 `l.label || l.country` 兩者皆無就空。
- 新增 `PLATFORM_NAME` host→平台名對照表(opentix→OPENTIX、todaytix→TodayTix、ticketmaster、atg、londontheatre、大麥、聚橙、寬宏、interpark、sistic、jegy…),`lab = l.label || platformName(host, …)`。**任何來源的圖卡都有正確平台名**;查無對照時退回裸網域而非空白。
- 自我校稿:headless render 4 種情況(長標題單卡/短標題單卡/3卡/官網標題連結)逐一檢查標籤與版面。

## [v0.68.3] - 2026-06-24 18:29
### 修正 — jegy.hu(東歐)海報模糊:popup 改用高清 -original- 版
- jegy.hu 來源存的是 `{slug}-{W}-{H}-{id}.jpg` **小縮圖**(如 222×131,9KB),放到 340px 大 popup 被放大成糊。`posterFull` 偵測 jegy.hu URL → 改寫成 `-original-` 高清版(實測 1080×636,131KB);marker 小縮圖維持小圖不變(140px 夠用、省頻寬)。布達佩斯 Mamma Mia 等東歐場次海報轉清晰(headless 驗證 naturalWidth 222→1080)。

## [v0.68.2] - 2026-06-24 18:25
### 修正 — popup 面板縮寬(非撐寬圖卡) + 移除標題 ↗(不招攬點官網)
- 上一版方向做反:把圖卡撐寬填滿固定 380px 面板。**正解**:圖卡**還原固定 110px 原狀**,改讓 `.pop-body` 用 `width:fit-content`(min 232 / max 380)→ 只有一個售票來源(如大麥/中國劇)時**整個右側面板縮窄貼合內容**,右邊大片留白消失;3 個來源仍維持原寬。
- **移除標題旁的 ↗ 箭頭 + hover 變色/底線**:官網雖掛在標題(可點),但加 ↗ 等於招手叫人去點**不分潤的官網**,與「把官網從顯眼圖卡拿掉」初衷矛盾。改成標題**外觀與純文字完全一致**(無箭頭/底線/變色)——能點但不宣傳,點擊自然流向有分潤的售票平台圖卡。

## [v0.68.1] - 2026-06-24 18:18
### 變更 — 大麥精準連結升級擴大到所有中國來源 + CI 持久化設計
- 原本只有「跟大麥場次合併過」的記錄能拿到精準 detail 連結。改成用 `china_damai.json` 建 **(group, 城市) 查找表**，**任何**中國來源（保利/聚橙/ypiao/上海文廣…）的大麥**搜尋頁**連結（`search.damai.cn`，點進去一堆場次），只要大麥已抓到該（劇名+城市）就換成**精準 detail 連結**。本次 **51 個**升級，剩 15 個是大麥沒抓到的劇/城市（誠實保留搜尋頁）→ **289/304 = 95% 大麥連結已精準**。
- **此升級在 `build_shows.py` 每次 CI build 都跑**：大麥 `china_damai.json` 已 commit、`build_shows` 每天 merge 它，故大麥的點天天在圖上**不需重抓**；隔天新抓的保利/聚橙也會自動比對升級。⚠️ 大麥本身是**手動批次**（需真人解 x5sec），是凍結快照，要手動重抓才更新（新劇不會自動出現、下檔的隨 end_date 自然淡出）。

## [v0.68.0] - 2026-06-24 18:10
### 變更 — popup 圖卡優化（官網移到標題、圖卡動態寬、大麥 label 統一、叢集半徑）
- **官網改成劇名標題的超連結**（`js/app.js`/`css`）：官網不分潤，原本在「購票」區做成顯眼圖卡會把點擊從**有分潤的售票平台**吸走。改成把官網連結掛在 popup 標題（劇名後加 ↗、hover 變色底線），購票圖卡區**只放售票平台**。
- **購票圖卡動態寬度**：原本固定 110px + flex-wrap，只有一個來源（如大麥/中國劇）時右邊一整排留白。改 `flex:1 1 0`→圖卡均分整行填滿；**單一來源**改橫向排版（logo+標籤並排）讀起來像刻意的寬鈕，不再是小圖示孤零零。3 個來源維持原本每格 ~110px 的觀感。
- **中國售票連結 label 按 host 統一**（`build_shows.py`）：同一齣劇不同城市來自不同來源（保利把大麥連結標「售票連結」、大麥 scraper 標「大麥」），標籤不一致。改成依目的地 host 正規化（damai→大麥、juooo→聚橙…），94 個連結統一;ticket_url-only 的補成 ticket_links 免得顯示泛用字。
- **叢集半徑 70→90**（`js/app.js`）：大叢集泡泡（如中國「95」）半徑大過鄰近小叢集的合併距離，視覺上蓋住卻不合併。調大半徑讓「視覺重疊」的鄰近叢集真的併進去（headless 截圖驗證 36+2→39、鄰居有間距）。

## [v0.67.1] - 2026-06-24 17:49
### 修正 — 大麥場次誤掛「未驗證（示範資料）」badge
- `china_damai.py build()` 漏設 `verified` 欄位 → 162 個大麥場次全被當未驗證，圖卡/popup 掛「⚠ 未驗證（示範資料）」。但大麥是真實官方 API 抓取（真場館/檔期/連結），同 juooo 應標 `verified: True`。補上後重建：`shows.json` **1607 verified / 0 unverified**，badge 消失（headless 截圖驗證）。

## [v0.67.0] - 2026-06-24 17:42
### 新增 — 大麥 Damai 中國音樂劇來源（人工協助批次、247 場次/52 城、精準售票連結）
- **新 scraper `scrapers/china_damai.py`**：大麥有阿里 BaXia x5sec 滑塊風控，無人值守 CI 繞不過 → 走「人過驗證、機器接手 session」路線。`launch`(真 Chrome 開遠端除錯埠導到搜尋頁) → 人解滑塊 → `probe`(確認 session 乾淨) → `harvest`(CDP 連同一 session,在頁面 context 內 fetch `searchajax`,pageSize 鎖 30、每頁 15~25s 隨機抖動+1/4 機率讀內容停頓、每頁即時寫檔、`--start-page` 可續抓、撞 x5sec 即停)。**誠實記錄：慢速仍會頻繁 re-challenge,需真人全程顧著解(~15 次/全量)**。
- **`build` 清洗**：raw 711 筆「音乐剧」分類其實 64% 是雜質 → 剔除舞劇 222/芭蕾 68/歌劇 22/文旅秀/券包共 464 → 劇名+城市去重 → **`china_damai.json` 247 場次/52 城**,含真實檔期、海報、**精準 `detail.damai.cn/item.htm?id={projectid}` 連結**。
- **`build_shows.py` 接線**：(1) 加 `china_damai.json` 來源;(2) **線 B 連結升級**——同一場若有大麥精準 detail 連結,移除舊「硬導向搜尋頁」連結(`search.damai.cn`),47 個升級、對不到的 4 個保留舊搜尋。
- **分類 tag 正確化**：大麥那批混了非中國原創的進口劇。靠 `works.json` 登錄機制 + 血統前綴證據 + web 查證,重標 9 齣——Moulin Rouge(梦断花都)/Daddy Long Legs/NYMT 青少年劇/MJ 致敬秀→Broadway/West End、紅舞鞋→法式、**Brothers Karamazov→韓國原創**(web 查證糾正我誤判的「俄」)。
- **座標**：大麥只給場館名,走 Google 國際 API geocode(實測對中國回 **WGS-84** 非 GCJ-02);3 個 agent 並行查上海星空间/十二楼等微劇場地址。**154/162 場次上圖**,8 個微劇場未定位 → `docs/DAMAI_未定位場館待查.md` 待補。
- ⚠️ **此來源非 CI 自動**(需真人解 x5sec),手動跑;`china_damai_raw.json` 保留 raw 以便重 `build` 不必重抓。

## [v0.66.1] - 2026-06-24 17:31
### 新增 — 分區官網（works.json `official` 升級為可分區物件）
- 從 `shows.json` 篩出 **26 部「同時在美(百老匯)+英(西區)上演」**的作品，3 個 agent 定向查各自 US/UK/AU 官網。
- 其中 **10 部有真正不同的分區官網**，`official` 由字串升級成物件 `{default, USA?, UK?, Australia?}`：Wicked、The Book of Mormon、Hadestown、SIX、Beetlejuice、Heathers、Mrs. Doubtfire、The Lion King、Kinky Boots、Waitress。其餘 16 部是「單一全球站＋subpath 分區」，維持字串。
- **schema 向後相容**：`build_shows` 接線時，字串→全場次共用；物件→依**該場次的 `country`** 挑（fallback `default`）→ 每張圖卡顯示**該地區的官網**（含巡演：tour 在哪國就挑哪國）。仍未接 `build_shows`（等 Damai）。

## [v0.66.0] - 2026-06-24 17:14
### 新增 — 作品官網資料(works.json) + Ticketmaster 高清 logo + 修 logo 路徑
- **官網研究**：10 個 agent 並行逐部搜尋+驗證 166 部作品官網，**107 部找到**（89 high + 18 medium；59 部確認無官網標 null），寫進 `data/works.json` 的 `official` 欄位。**僅資料準備、尚未接 `build_shows`**（避開進行中的 Damai 改動衝突），故暫不顯示於地圖；接線後一次補上一大片缺官網的劇（每部作品官網會繼承到其所有場次）。
- **Ticketmaster logo**：官方只發 32px favicon，改 rehost **426px 高清** `logos/ticketmaster.png`（LOGO_MAP）。
- **修既有 bug**：`platformIcon` 的 LOGO_MAP 相對路徑在變體頁 `/MusicalMap/zh-hant/` 會 404（damai/juooo logo 一直壞、被 `onerror` 藏掉）；補 `MM_BASE` 前綴後正確解析。
- 重建三語頁刷 cache-bust。

## [v0.65.9] - 2026-06-24 17:01
### 改善 — 售票平台圖示畫質（favicon sz 64→128）
- `platformIcon` 取 favicon 由 `sz=64` 改 `sz=128`：高 DPI 螢幕放到 52px 不再顆粒（todaytix/LondonTheatre/ATG 等大多數明顯變清晰，實測對照確認）。
- 例外：**Ticketmaster 官方只發布 32px favicon**（Google/DuckDuckGo/apple-touch/favicon.ico 全卡 32px），畫質受限；要清晰需另 rehost 重繪 logo（待議）。
- 重建三語頁刷 cache-bust。

## [v0.65.8] - 2026-06-24 16:48
### 改善 — popup 售票 tile 放大、標籤一行、版面加寬
- 標籤不再換行：`.pop-tile-label` 改**單行**（`white-space: nowrap` + ellipsis），消除「London Thea／tre」「Ticketmaste／r」這種醜換行。
- tile 加寬 76→110px、圖示放大 40→52px、圓角 14px；`.pop-body` 280→380px、popup `maxWidth` 620→720 容下更大、更好看的版面。
- 重建三語頁刷 cache-bust。

## [v0.65.7] - 2026-06-24 16:34
### 修正 — popup 售票平台 tile 名稱被裁切
- 症狀：popup「購票」區每個平台 tile 的名稱（官方網站／TodayTix／Ticketmaster 等）**底部被切掉**。
- 根因：`.pop-tile` 固定 `height: 92px`，容不下「圖示 40px + 標籤(最多 2 行) + 箭頭」，標籤被擠到溢出裁切。
- 修法：`css/style.css` 改 `min-height: 104px`（容得下 2 行標籤、會換行的 Ticketmaster 也不再切），微調 gap/padding。重建三語頁刷 cache-bust。

## [v0.65.6] - 2026-06-24 14:11
### 新增 — 品牌 logo + header/sidebar 改用 logo 米白底色
- 加入品牌 logo（金色高音譜號徽章）到 header 品牌區（`logo.png`，原圖縮放至 122×200）。
- 取樣原 logo 背景真實色 = **`#fefefc`**（米白，極淡暖白），新增 CSS 變數 `--cream`；`#topbar`（上方 banner）與 `#sidebar`（左側欄）背景由純白 `var(--panel)` 改為 `var(--cream)` → logo 米白底融進去、無白框感。
- `#brand` 改 `align-items: center` ＋ `.brand-logo`（高 40px）。
- 手寫頁 `theatres`/`privacy`/`terms` 的 header 同步加 logo；地圖頁由 `gen_site.mjs` 產生。
- 重建三語頁刷 cache-bust；MD freshness 掃過、無因此過時項。

## [v0.65.5] - 2026-06-24 14:01
### 新增 — 地圖即時 zoom level 顯示
- `js/app.js`：在 +/- 按鈕下方加一個 Leaflet 控制項（`.mm-zoom-level`），即時顯示目前縮放級別（`z N`），隨縮放更新（`zoom`/`zoomend` 事件）→ 一眼看到現在第幾級（判斷叢集在哪級散開等很方便）。
- `css/style.css`：`.mm-zoom-level` 白底圓角小牌，與淺色 UI 一致。
- 重建三語預渲染頁刷 cache-bust；MD freshness 掃過、無因此過時項。

## [v0.65.4] - 2026-06-24 13:40
### 調整 — 叢集合併距離 45→70（減少海報蓋住圓圈的醜重疊）
- `js/app.js` `maxClusterRadius` 45→70（≈ 一張海報高度 72px）：地理上相鄰到「海報會嚴重蓋住圓圈」的點，會合併成一顆圓圈，避免「海報板子幾乎蓋滿圓圈」的醜畫面；放大即散開、露出個別海報。
- 重建三語預渲染頁刷新 cache-bust 雜湊。
### 文件 freshness
- `README.md`：修正過時敘述「cluster 線性縮放」→「cluster 依數量 √n 縮放」（程式 `iconCreateFunction` 早已改為 `Math.sqrt(n)`）。

## [v0.65.3] - 2026-06-24 13:28
### 新增 — 所有外部 API 呼叫的用量記錄（評估能否提高掃描頻率）
- 新增 `scrapers/usage.py`：import 時 monkey-patch `urllib.request.urlopen`（**所有 scraper 都用這個呼叫形式**），自動**按 host 計數 API 呼叫** ＋ 擷取 `Rate-Limit*` header（如 Ticketmaster 每日 5,000 額度/剩餘）。process 結束時 merge 進 `logs/api_usage.json`（按 CI run 分組，bounded ring buffer）。
- 新增 `scrapers/_run.py` 包裝器：CI 改用 `python scrapers/_run.py scrapers/X.py` 跑每支 scraper（先 import usage 再 runpy 執行目標、保留 `__main__`/`__file__`/argv）→ **28 支 scraper 一行都不用改**就全涵蓋。
- `update.yml`：所有 scraper 改走 `_run.py`；`logs/api_usage.json` 納入每日 commit。
- 用途：跑幾天後看 `logs/api_usage.json` 各 host 的 `total_calls` 與 TM 的 `available`，判斷加頻率撐不撐得住（現況 TM 單班約用 ~1,400/5,000、有餘裕）。**純 ops，無網站變更、不需重建。**
- 實測：探針 + 真實 scraper（shiki）驗證 host 計數與 TM 額度擷取正確。

## [v0.65.2] - 2026-06-24 12:46
### 新增 — 叢集圓圈 hover 時浮起 + 放大（解決重疊被擋）
- 重疊的叢集泡泡（66/25/10 那種圓圈）互相遮住時，hover 看不清被擋的那顆。Leaflet 的 `riseOnHover` 只作用於單一 marker，**不含 markercluster 的叢集泡泡**。
- `js/app.js`：掛 `clustermouseover`/`clustermouseout`，hover 時 `setZIndexOffset(10000)` 把該圓圈拉到最上層、移開還原。
- `css/style.css`：`.mm-cluster` 加 `transition`＋`.leaflet-marker-icon:hover .mm-cluster { transform: scale(1.25) }`，hover 時略放大（呼應海報圖卡的放大手感）。海報 marker 本就有 `riseOnHover`，維持不變。

## [v0.65.1] - 2026-06-24 12:27
### 修正 — Mapbox 受限 token + `no-referrer` 不相容導致地圖空白
- 症狀：v0.65.0 上線後三語頁地圖**整片空白**。根因：受限 Mapbox token 靠 HTTP `Referer` 判斷來源網域，但頁面 `<meta name="referrer" content="no-referrer">` 讓瀏覽器**完全不送 Referer** → Mapbox 回 `403` 擋掉所有圖磚。curl 實測：無 Referer=403、帶 origin Referer=200、錯誤網域 Referer=403。
- 修法：`build/gen_site.mjs` 把 referrer policy 由 `no-referrer` 改為 `strict-origin-when-cross-origin`（瀏覽器預設值）→ 跨來源只送 origin（如 `https://dannynycc.github.io/`，不洩漏完整路徑/query），Mapbox 即可比對白名單放行。重建三語頁。
- 影響：外連售票連結現在會帶 origin-only referer（sovrn/Impact 等聯盟靠 URL 參數歸因、不受影響）。

## [v0.65.0] - 2026-06-24 11:46
### 變更 — 地圖底圖改用 Mapbox Streets（綠地藍海，取代 CARTO Voyager）
- **底圖供應商換成 Mapbox**：`js/app.js` 街道底圖由 CARTO Voyager（米黃陸地、偏濁）改為 **Mapbox Streets v12**（清新綠地＋明亮藍海），海報 marker / 叢集圈在乾淨背景上更跳出；版權標示同步改為 Mapbox + OpenStreetMap。@2x/512 tiles + `zoomOffset:-1` 高清渲染。衛星圖切換鈕不變。
- **Mapbox public token 放 `js/config.js`**（`MM_CONFIG.MAPBOX_TOKEN`，公開金鑰，性質同 Supabase anon key；免費額度每月 5 萬次載入）。用**受限 token `musicalmap-web`**，URL 白名單：`dannynycc.github.io`、`localhost`、`themusicalmap.com`（Mapbox 不支援 `*`，但裸網域自動涵蓋 `my.`/`www.` 等子網域＋ http/https＋子路徑），故搬網域時 Mapbox 端不需再改。
- 重建三語預渲染頁刷新 cache-bust 雜湊至 `abd4398d3a`，回訪者自動載到新 `app.js`/`config.js`（避免 v0.64.2 那種舊快取空地圖）。
- headless 截圖驗證真實 zh-hant 地圖底圖已是 Mapbox 綠藍。

## [v0.64.3] - 2026-06-24 01:23
### 修正 — 地圖填滿視窗高度(消除上下灰底)+ cache-bust 改用內容雜湊
- **地圖上下灰底**:Leaflet 在低 zoom 時世界高度 < 容器高度會露出灰色背景。`js/app.js`:(1) 動態 `minZoom = ceil(log2(視窗高/256))` → 世界永遠蓋滿高度、zoom out 不會露灰;(2) `maxBounds` 緯度夾在 ±85、經度留 ±Infinity → 拖曳也不露灰,但**水平無限捲動保留**;(3) `maxBoundsViscosity:1`。headless 驗證 zoom 到底無灰底、marker 正常、水平仍 wrap。
- **cache-bust token 改用 js/css 內容 MD5 雜湊**(取代資料時間戳):只改 app.js 時時間戳不變會讓回訪者吃舊檔;改雜湊後**任何 js/css 變動都換新 token**,回訪者必拿到新版。

## [v0.64.2] - 2026-06-24 01:15
### 修正 — js/css cache-busting(回訪者看到空地圖的 bug)
- 症狀:回訪者進 `/zh-hant/` 等變體頁「所有 marker 消失」。原因:瀏覽器**快取了舊版 `js/app.js`**(抓相對 `data/shows.json`,在子目錄下變 404)→ 無資料。全新快取的 headless 載入線上頁則正常,確認是快取問題非線上 bug。
- 修法:`build/gen_site.mjs` 為 `css/style.css` 與所有 `js/*.js` 加 `?v={token}`(token 取自 `shows.json` 的 `generated_at`,每次重建即更新)→ 回訪者自動載到新檔。
- 使用者即時解:該頁 Ctrl+Shift+R 強制重新整理。

## [v0.64.1] - 2026-06-24 01:08
### 變更 — 合併「西語+葡語」為「西葡音樂劇」+ 百老匯標籤加「音樂劇」
- **西語音樂劇 + 葡語音樂劇 → 西葡音樂劇**(單一分類):`build_shows.py` `classify_tag` 把 Spanish/Portuguese 國家都歸 `西葡音樂劇`;`works.json` 1 筆 tradition 改名;`app.js` `TAG_DEFS` 兩列併一;`build_shows.py` REGIONAL set 更新。三語標籤:繁「西葡音樂劇」/ 簡「西葡音乐剧」(OpenCC)/ 英「Spanish/Portuguese」。
- **百老匯/西區 → 百老匯/西區音樂劇**(中文補後綴,與其他分類一致):繁「百老匯/西區音樂劇」/ 簡「百老汇/西区音乐剧」;英維持「Broadway/West End」(英文標籤本就無 musicals 後綴)。
- 重建 shows.json/變體/三語頁;headless 驗證:繁體「百老匯/西區音樂劇 196・西葡音樂劇 18」、英文「Broadway/West End・Spanish/Portuguese 18」正常,無殘留舊分類。

## [v0.64.0] - 2026-06-24 01:01
### 新增(階段2/2)— 繁/簡/英「三語獨立網址」+ 預渲染 + SEO/AI-search
- **三套網址**:`/zh-hant/`、`/zh-hans/`、`/en/`,各為 **build 時預渲染的靜態 HTML**(劇目清單 + JSON-LD Event 寫進原始 HTML)→ Google **與不跑 JS 的 AI 爬蟲(GPTBot/ClaudeBot/Perplexity)都讀得到內容**。
- `build/gen_site.mjs`:產三套 `index.html`(正確 `<html lang>`、title/description、canonical、**hreflang(zh-Hant/zh-Hans/en/x-default)**、JSON-LD WebApplication+ItemList、預渲染 `#show-list`、絕對 `/MusicalMap/` 資源路徑、語言切換 `<a>` 導向對應網址)+ **根目錄語言路由**(依 localStorage/瀏覽器轉址,附 x-default 連結)+ `sitemap.xml`(7 URL,xhtml:link hreflang)+ `robots.txt`(放行 12 個搜尋/AI bot)。
- `js/i18n.js`:支援三語(en / zh=繁 / zh-hans=簡)。變體頁由 `window.MM_VARIANT` 固定語言;**簡體 UI 由 OpenCC(t2cn ~65KB)即時轉**(劇→剧、樂→乐…);舊頁(theatres/me)維持 `?lang` 相容。
- `js/app.js`:變體頁載入 `data/variants/shows.{variant}.json`,資源走 `MM_BASE` 絕對路徑;中文判斷改 `isZh()`(繁簡皆是)。
- `.github/workflows/update.yml`:加 Node + `npm install` + 跑 `gen_variants.mjs`/`gen_site.mjs`,把變體與預渲染頁納入每日提交;node_modules 不進 Pages artifact。
- 本地 headless 三變體全驗證:繁(全繁)、簡(OpenCC 轉簡)、英(全英)UI + 地圖 + 側欄正常;原始 HTML 含預渲染劇目+JSON-LD。
- 根 `index.html` 由「應用頁」改為「語言路由頁」(舊 `/MusicalMap/` 訪客轉址到對應語言)。

## [v0.63.0] - 2026-06-24 00:45
### 新增(階段1/2)— 繁/簡/英三語「資料變體」地基(OpenCC build-time 轉換)
- 目標:繁體中文 / 簡體中文 / English 三語,選了「全站文字」(含劇名、地名、平台名)跟著變;且要 **SEO + AI-search friendly**。研究結論(已查證):AI 爬蟲(GPTBot/ClaudeBot/Perplexity)**不跑 JS** → 內容須 build 時就寫進靜態 HTML;Google 要求**每語言不同網址**(`/zh-hant//zh-hans//en/`);轉換用 **OpenCC**(`opencc-js`)。
- **本次(階段1,純新增、不動線上)**:
  - `build/gen_variants.mjs`(Node + opencc-js):由 `data/shows.json` 產生 `data/variants/shows.{en,zh-hans,zh-hant}.json`。劇名/場館/巡演名用 OpenCC 雙向轉(cn⇄tw,處理一對多如 发→發/髮);平台名 en 用英文(聚橙→AC Orange、大麦→Damai),繁簡用 OpenCC。
  - `data/i18n_maps.json`:CN/TW/JP/KR 共 65 城 + 4 國的地名對應(英→簡,繁體由 OpenCC 自動轉);西方地名(New York/London)維持英文。
  - 驗證:怨种闺蜜→en/簡保留、繁體「怨種閨蜜」;Shenzhen→深圳/中国·中國;Lion King 三版不變。
  - `package.json` 宣告 opencc-js 依賴;`.gitignore` 擋 node_modules。
- **下一步(階段2)**:產 `/en//zh-hans//zh-hant/` 三套預渲染 HTML(內容入 HTML + JSON-LD)、hreflang/sitemap/robots、語言切換改成換網址、接進 CI。

## [v0.62.3] - 2026-06-23 22:01
### UI/修正 — 售票區:修 get_tickets 漏譯、logo 放大、箭頭移到名稱下方、標頭去底線
- **修 bug**:`get_tickets` 在英文 locale 漏加 → 直接顯示原始 key「get_tickets」。已補 en「Get Tickets」(標頭用 title case)。
- **logo 放大、更大氣**:售票區方塊 58×66 → 76×92、logo 27→**40px**;`.pop-body` 232→**280px** 讓大方塊仍三排(3×76+2×6=240)。
- **箭頭移到名稱下方**置中(原本右上角)。
- **標頭去掉底線**(border-bottom),字級 12→13,乾淨。

## [v0.62.2] - 2026-06-23 21:27
### UI — 售票區改版:加「購票」標頭 + 名稱加粗 + 每塊右箭頭(參考 JustWatch/Songkick)
- 回饋:logo 方塊的平台名稱**灰字太淡**、看不出「點進去是售票」。參考 JustWatch(where to watch)+ Songkick/Bandsintown(buy tickets)歸納:**需明確區塊標頭 + 名稱要清楚可讀**。
- `js/app.js` + `css/style.css`:售票方塊上方加 **「購票」標頭**(粗體 + 底線,**不用 emoji**——使用者明示 emoji 難看);平台名稱從淡灰 `--muted` 改 **深色 `--text` + 700 粗體**、字級 9→10;方塊改成**按鈕感**(淡底 `#f8fafc`、hover 轉白+浮起);**每塊右上角加 `→` 箭頭**(文字符號非 emoji,hover 變強調色並右移)。
- `js/i18n.js`:新增 `get_tickets`(購票 / Get tickets)。
- 仍維持使用者要的「方形 logo、三個一排」(58×66 在 232px body 內剛好 3 排)。headless Chrome 截圖驗證:Lion King 的 TodayTix/Broadway.org/Ticketmaster 三塊含標頭、粗名稱、箭頭正常。

## [v0.62.1] - 2026-06-23 21:04
### 新增 — 大麥彩虹 logo + 聚橙的劇加上大麥購票連結
- **指定 logo 覆蓋**(`js/app.js` `LOGO_MAP` + `platformIcon()`):Google favicon 服務對中國站只回通用地球圖,故為大麥放上**官方彩虹 logo**(`logos/damai.png`,取自 App Store 官方 App icon、親眼驗證)。所有大麥連結(保利巡演 + 聚橙)都顯示彩虹,辨識度高;其餘平台仍用 favicon。
- **`scrapers/china_juooo.py`**:聚橙的劇除了 `m.juooo.com/ticket/{schedular_id}`,**另加一條大麥搜尋連結**(`聚橙` + `大麥` 兩個 tile),中國買家多用大麥。
- **修 bug**:china_juooo 的 showSearch 對「無音樂劇的城市」會回 `result:[]`(list 非 dict),導致 `res.get(...)` 崩潰(掃到該城市才觸發)。加 `isinstance` 守衛。
- headless Chrome 截圖驗證:怨种闺蜜 popup 顯示 聚橙 + 大麥(彩虹)兩 tile 正常。

## [v0.62.0] - 2026-06-23 20:02
### UI — 售票連結改成「各平台 logo 方形 tile 並排」
- popup 的售票連結從「全寬綠色文字按鈕」改為**方形 logo tile 一排**(`js/app.js` popupHtml + `css/style.css` `.pop-tiles`/`.pop-tile`):每個售票站顯示**自己的 favicon + 名稱**,比一排同色按鈕清楚。官網優先、其餘票務接續,affiliate 包裝不變。
- icon 用 **Google favicon 服務即時取得**(`s2/favicons?domain={host}`)—— 任何售票站(含各劇官網、任何網域)自動有 icon,零維護、零 rehost;載入失敗則只留名稱(onerror 隱藏圖)。
- tile 尺寸 58×66 調校成在 232px 寬的 `.pop-body` 內**剛好 3 個一排**(3×58+2×7=188)。headless Chrome 截圖驗證:Lion King 的 TodayTix／Broadway.org／Ticketmaster 三個 logo 並排正常。
- 只影響主地圖(app.js);me/u 個人足跡頁不受影響(它們無售票按鈕)。

## [v0.61.3] - 2026-06-23 18:04
### 變更 — Sovrn 一把 key 擴成「售票站 catch-all」(深入查文件後)
- 研究 agent 讀透 Sovrn KB + Developer Center,確認:**Redirect API 是自建連結網站的正解**(JS 版是給部落格自動改連結用,我們不需要那段 `vglnk.js`);**一把 site key 可變現任何 in-network merchant**(out-of-network 原樣通過,無害);CPA+CPC 都計;`sovrn.co` 是 `redirect.viglink.com` 的新等價網域。
- `js/config.js`:用同一把 Sovrn key 把 **todaytix.com / londontheatre.co.uk / broadway-show-tickets.com / atgtickets.** 全部包成 Sovrn 分潤連結(≈ 390 條外連)。`SOVRN` 模板抽成常數。Ticketmaster 仍走較高的直接 Impact(不進 Sovrn)。
- ATG/Broadway Direct 之後拿到直接計畫(Partnerize camref / Awin affid)可升級取代 Sovrn 條目(註解已標)。
- ⚠️ 文件記明:Sovrn 端**網站需人工審 ~3-5 天(Settings→Pending,首次點擊後)才開始計佣** —— 目前 Pending 屬正常。
- node 實測:TM→Impact、四個售票站→Sovrn、非聯盟 passthrough。README / config 註解更新。

## [v0.61.2] - 2026-06-23 17:48
### 上線 — TodayTix 分潤實際生效(經 Sovrn Commerce / VigLink)
- 使用者完成 Sovrn Commerce(Publisher → Commerce)申請,TodayTix merchant 122507「Open」。取得 VigLink **API key**(Site Settings 🔑,公開值)。
- 填入 `js/config.js`:`todaytix.com` 的 `tmpl` = `https://redirect.viglink.com?key=…&u={url}`。**實測驗證**:`redirect.viglink.com?key=…&u=<TodayTix劇目>` → 302 正確導到該劇頁(網域活、key 有效)。
- 效果:`scrapers/todaytix.py` 對到的 **101 條 TodayTix 連結現在 render 時自動包成 Sovrn 分潤連結**(排票務最前)。**TodayTix 成為繼 Ticketmaster 後第 2 個實際變現的來源**。
- `js/app.js`:`AFF_TRACKING` 防呆加入 `viglink.com`/`sovrn.co`(不重複包)。
- node 實測:TodayTix→viglink、TM 仍 Impact 無回歸、非聯盟 passthrough。README / DESIGN_affiliate 對應更新為「LIVE」。

## [v0.61.1] - 2026-06-23 17:26
### 變更 — 分潤平台逐一查證 + 框架加 `tmpl` 型(支援 Sovrn)
- **逐一實測每個分潤平台**(回應「每樣都要驗」),結果寫進 `docs/DESIGN_affiliate.md` §5/§7:
  - **ATG / LOVEtheatre = Partnerize**,✅ 驗證可申請(`signup.partnerize.com/signup/en/ambassadortheatregroup`,5 天 cookie)。
  - **Broadway Direct = Awin** merchant **28987**(✅ 驗證存在,Nederlander 9 院)。
  - **London Box Office = 自有**(email 申請,48h 回 Unique ID)。
  - **TodayTix 直接計畫已關**(FlexOffers 標 "not currently offering";`hello.todaytix.com` 已死 NXDOMAIN)——更正先前「Impact 1-2%」的錯誤。**唯一變現路 = Sovrn Commerce**(Merchant Explorer merchant 122507 標「Open」)。
- **`js/config.js` + `js/app.js`**:`affiliateUrl` 新增 **`tmpl` 網絡型**(設定放含 `{url}` 佔位的連結模板)—— 給「過審後才知格式」的網絡(如 Sovrn)用。TodayTix/londontheatre 改成 `tmpl`(Sovrn,dormant);ATG=partnerize、Broadway Direct=awin 註解標為已驗證。node + 既有測試:TM 照常、dormant passthrough、填模板即生效。
- 教訓記入文件:別憑搜尋/AI 背書,affiliate 狀態要逐一實測(DNS+內容+網絡)。README 對應更新。

## [v0.61.0] - 2026-06-23 15:39
### 新增 — TodayTix 改導 matcher(分潤 Phase 2,自動化)
- 新增 **`scrapers/todaytix.py`**:逆向 TodayTix 開放 API(`api.todaytix.com/api/v2/shows`,無 auth、無反爬),掃**全 13 城**(NYC/London/Chicago/SF/LA/DC/Boston/雪梨…)的 **Musicals**,**保守對應**到我們的劇(正規化標題 group_key + **精確城市**比對,清掉「on Broadway/the musical」字尾;slug 缺用 id-only URL,會 301 轉)。輸出 `data/todaytix.json`(103 連結 / 76 作品)。
- **`build_shows.py`**:讀 todaytix.json,給對到的劇(group+city 相符)掛 TodayTix `ticket_link`,**插在票務連結最前**(官方網站 → TodayTix → 其他)——因 TodayTix 抽 ~1-2% 遠高於 TM 固定 $0.30。實測掛上 **101 筆**(Wicked/Hamilton/SIX… 紐約/倫敦/DC 各對到正確城市 URL)。
- **CI**:`todaytix.py` 排在第一次 build_shows 之後、第二次之前(自動每日跑;matcher 需 shows.json,build_shows 需 todaytix.json)。
- 連結仍是**乾淨 URL**,分潤碼 render 時才包(TodayTix Impact 過審填碼即自動抽成,零後續開發)。
- 文件:`docs/DESIGN_affiliate.md` Layer B/C 標為已實作;README 對應更新。

## [v0.60.0] - 2026-06-23 15:13
### 新增 — 多平台分潤框架(Phase 1)+ 架構定案
- `affiliateUrl()` 從「只 Ticketmaster」重構為**多網絡、config 化**:`MM_CONFIG.AFFILIATE`(key=外連 host,value=`{net,…creds}`)支援 **Impact / Partnerize / Awin** 三種網絡;每個程式 **dormant**(creds 沒填齊→passthrough,連結照常不抽成),**填碼即生效**。
  - 已登記:`ticketmaster.`(Impact,live)、`atgtickets.`(Partnerize,219 齣待 camref)、`londontheatre.co.uk`(Impact/TodayTix,45 齣待 domain+ids)、`todaytix.com`(Impact,Phase 2)、`broadwaydirect.com`(Awin mid 28987,待 affid)。
  - 防呆:已是追蹤網域(evyy.net/pxf.io/sjv.io/prf.hn/awin1.com)不重複包;`AFFILIATE_PRIORITY` 預留優先序(Phase 2 用)。
- **鐵則**:資料層只存乾淨原始 URL,分潤碼一律 render 時才包 → 換/加 ID = 改 config 一行,**永不重建資料**。node + headless Chrome 實測:TM 照常包、dormant 平台 passthrough、填碼後 Partnerize/Awin 格式正確、不重複包、index.html 無 JS error。
- 新增 **`docs/DESIGN_affiliate.md`**:兩種接法(wrap 現有 / re-point 新平台)、三層架構、**自動化程度表**(唯一無法自動=申請帳號)、各平台狀態、Phase 2(TodayTix matcher 走 CI + 信心門檻自動取捨)計畫、品牌端申請須知。
- 文件:README 分潤條目改多平台框架;AFFILIATE_SETUP 更新 `MM_CONFIG.IMPACT`→`MM_CONFIG.AFFILIATE`。

## [v0.59.0] - 2026-06-23 14:38
### 新增資料來源 — 聚橙 juooo(中國第 5 個官方 API)
- 新增 **`scrapers/china_juooo.py`**:逆向聚橙官方 H5 API(**不需簽章、無 BaXia 牆**)。
  - 城市清單 `api.juooo.com/city/city/getCityList`;節目 `gw.juooo.com/gw/show/showSearch`(POST form,`cate_parent_id=79`=音樂劇 `+city_id+page`);座標 `gw/show/showDetail` → `venue.coordinate`(GCJ-02 **自轉 WGS-84**,不依賴 cn_venues.json);售票連結 `m.juooo.com/ticket/{schedular_id}`。
  - **遍歷全 253 城**(showSearch 分城市),任何城市日後有音樂劇都抓得到。目前 3 齣(全深圳安托山公共文化中心 —— 聚橙自營庫存集中深圳,北京/上海在 juooo 上 0 場)。
- 接入 `build_shows.py`(合併清單 + `juooo`→中國原創 tag)與 `.github/workflows/update.yml`(每日兩次自動跑)。地圖總數 1432→**1435**。
- **`docs/SOURCES.md`**:juooo 上線詳述 + 誠實記錄「**大麥/猫眼評估後不採用**」(BaXia x-sign/x-mini-wua 為 server/SDK 端簽章,對無人值守 CI 太重+脆弱+中國零分潤;維持售票連結導大麥搜尋頁)。
- 過程修正:一度誤判 juooo「geo 鎖深圳」—— 實為打錯端點(showSearch 分城市 vs getShowList 需 server 端 sign);切城市用 city_id 遍歷即可,從任何 IP 都能全國抓。

## [v0.58.1] - 2026-06-23 11:59
### 文件 — 全 md freshness 全面對照(使用者要求逐份掃)
- 逐一掃過全部 9 份文件對照真實資料,修正過時數字(改用「約/隨 CI 變動」避免每日刷新又過時):
  - **README**:作品主檔 157→**158 筆**(並補 `poster`/`productions` 說明);資料「~1,437/30 國」→**~1,430/31 國**;TM 分潤「612 齣」→**約 600 齣**。
  - **docs/AFFILIATE_SETUP**:TM 連結數 612→**約 600**(隨每日 CI 變動)。
  - **docs/DESIGN_productions §3**:標明「157 筆/無 poster」是**改版前**狀態,現為 158 筆帶版本層。
  - **docs/WORKFLOW**:稽核清單補 `audit_productions.py`。
  - **llms.txt**:playing across「40+ countries」→**30+**(與實際 31 國、README 一致)。
- 其餘(SOURCES/TOUR_SWEEP/SETUP_ACCOUNTS)本 session 無波及,確認無過時。

## [v0.58.0] - 2026-06-23 11:51
### 新增 — Ticketmaster 分潤(Impact)上線
- Impact 分潤計畫核准 + 帳務(美國銀行 EFT)+ 稅表(W-8BEN,非美國人 0% 預扣)全部完成 → **把追蹤碼接進地圖售票連結**。
- **`js/config.js`**:新增 `MM_CONFIG.IMPACT`(Ticketmaster 追蹤 ID:`ticketmaster.evyy.net` / account 7408739 / campaign 264167 / ad 4272 / subId1 `musicalmap`)。ID 放 config**不寫死**在邏輯;這些是公開值(出現在每條外連)。
- **`js/app.js`**:`affiliateUrl()` 改由 config 建表。任何 `ticketmaster.*` 售票連結自動包成 deep-link `…/c/7408739/264167/4272?u={URL-encoded 該劇TM頁}&subId1=musicalmap` —— 使用者**仍導向該劇頁面**,只是帶上分潤追蹤;非 TM 連結原樣;已是追蹤網域(evyy.net/pxf.io/prf.hn)的不重複包。
- **`index.html`**:補載 `js/config.js`(原本只有 me/u 頁載,主地圖沒載 → 否則讀不到 IMPACT 設定)。
- 覆蓋:612 齣有 TM 連結的劇(美 385 / 英 86 / 加 21 / 墨 18…),其餘 ~830 齣售票為別家(passthrough 不變)。
- 驗證:node 邏輯測試 + headless Chrome 在 index.html 實測(config 載入順序、deep-link 目的地保留、subId 標籤、非 TM passthrough、不重複包)全綠。
- 待後台驗證:美站 ticketmaster.com 有把握歸佣;各國 TM 網域是否同計畫,待有點擊後看 dashboard 的 `subId1=musicalmap` 數據確認。
- 文件:`docs/AFFILIATE_SETUP.md` §1 標為已上線、§0 勾掉收款/W-8BEN;README 對應條目改 ✅。

## [v0.57.2] - 2026-06-23 01:22
### 文件 — 記錄「系統性抓過去版本」的決策(換 session 前)
- `docs/DESIGN_productions.md` 加 §11 決策紀錄:評估後**否決 Wikidata / Theatricalia** 作為 archival 版本來源(實測 Theatricalia 嚴重偏 UK、整庫無 Wicked、非英語劇歸零、無海報、ODbL share-alike);記錄目前已 scale 的部分(live 自動分群、個人 `poster_override`)與未解的「共享層 scale」=自助 UGC 貢獻迴路(已暫緩,明天續)。
- 純文件;明天從 §11 接續研究 UGC 迴路。

## [v0.57.1] - 2026-06-23 01:08
### 新增 — Roméo et Juliette 台灣巡演 2023 版本(使用者提供海報)
- 使用者回報其 2023 在臺中國家歌劇院看的 **Roméo et Juliette**(羅密歐與茱麗葉,Gérard Presgurvic 法文音樂劇 20 週年紀念巡演)應有專屬海報 → 新增 archival 版本 **`rj-taiwan-2023`**(海報 `posters/romeo_juliette_tw2023.jpg`,使用者提供 + 親眼驗證:臺中/台北流行音樂中心/高雄衛武營,2/11–2/28)。
- R&J 現有 2 版本:**台灣巡演 2023**(archival)+ **France**(live,即系統原本顯示的「2027–28 法國特殊封面」)。使用者那筆 2023 紀錄重新編輯時選「台灣巡演 2023」即帶對海報;法國特殊封面被正確歸到 France 版本,不再誤當通用圖。
- headless Chrome 截圖驗證版本下拉 + 海報預覽正常;audit_productions 0 broken。

## [v0.57.0] - 2026-06-22 23:25
### 新增 — Production(製作/版本)層上線:足跡可選版本 + 沒在演的劇也查得到
- **足跡表單(me.js / me.html)新增「版本／製作」下拉 + 「海報網址(選填)」**:選了劇名若該作品有多版本(如歌劇魅影),會跳出版本下拉(附即時海報預覽),選哪版就帶哪版的海報;未收錄的版本可貼自訂海報網址。海報解析序 **自訂 → 版本 → 作品 → ♪**(存版本 key 不存死圖 → 日後修圖自動傳播;使用者自訂覆蓋永遠優先)。
- **沒在演的劇現在也進自動完成且有縮圖**(解決 Love Never Dies 查不到):`gen_catalog.py` 的 titles 改為「現役場次 ∪ 已登錄作品」聯集,works.json 升級為作品主檔(加 `poster` / `productions`)。
  - 新增 **Love Never Dies**(中文「愛無止盡」,別名「真愛不死」),海報用使用者提供的 San Jose 巡演版主視覺。
  - **歌劇魅影 10 個版本**:8 個 live(英/美/日四季/匈/奧/中/墨/挪,海報自動取各國現役場次圖)+ 2 個 archival(**台灣巡演 2026**、**25 週年 RAH 演唱會**,海報皆使用者提供 + 親眼驗證 rehost)。
- **live 版本自動產生**:`gen_catalog.py` 依國家把每作品的現役場次分群成版本(海報取代表圖),不必手寫規則;**app.js(live 地圖)無需改動**——它本來就用每場自己的海報。
- **公開分享頁(u.js)** 套用同一套版本海報解析,別人看你的足跡也是正確版本。
- **新增 `scrapers/audit_productions.py`**(掛 CI):檢查作品/版本海報「檔案存在且為圖檔」、列出缺海報的版本與無縮圖的劇。
- **Supabase**:新增 `supabase/add_production.sql`(`production_key` / `poster_override`,`add column if not exists`);App 在欄位未建時優雅降級不報錯。
- 文件:`docs/DESIGN_productions.md` 加實作後修訂(app.js 不用動、live 自動分群)、`docs/SETUP_ACCOUNTS.md` 補 migration 說明、README 改「版本層已上線」。
- 驗證:headless Chrome 截圖確認版本下拉 + 海報預覽(Phantom)與 LND 縮圖正常;修掉一個 CSS specificity bug(`#add-form label{display:flex}` 蓋過 `[hidden]` 導致空版本下拉沒被隱藏)。

## [v0.56.3] - 2026-06-22 22:53
### 新增 — Production(製作/版本)三層資料模型「設計定案」
- 新增 **`docs/DESIGN_productions.md`**:把資料模型從現行兩層(作品 work / 場次 run)補上中間的 **製作/版本 production** 層。解決使用者回報的兩個現象 —— (1) 沒在演的劇(如 Love Never Dies)查不到、無縮圖;(2) 同一齣劇所有版本共用同一張海報(歌劇魅影 27 場原始資料其實有 8 種海報卻被收斂成一張)。
- 定案要點:production 分 `live`(有現役場次,規則自動配對,live 地圖也跟著拆海報)與 `archival`(已落幕/歷史錄影,只供足跡手動選版本);海報解析順序 `poster_override → production → work → ♪`(存 key 不存死圖,修圖自動傳播、使用者覆蓋優先);Supabase 加 `production_key`/`poster_override`;新增稽核 `audit_productions.py`。
- 本次僅落定文件;功能實作分階段進行(資料模型 → 後端配對 → 前端足跡 → live 地圖/公開頁 → migration),功能性改動屆時以 MINOR 進版。
- **README.md**:docs 區塊補列 `DESIGN_productions.md` 指標。

## [v0.56.2] - 2026-06-15 17:13
### 文件 freshness 全面更新(換 session 前)
- **README.md**:現況從「604 筆/約 25 國」更新為 **~1,437 筆/約 30 國**;補列全部自動 scraper(中國×4、Portugal、義/瑞/荷/波/挪/奧/中東、Madrid、東歐、japan、tm_tours…)與人工策展市場(巴西/阿根廷/南非/新加坡);tag 清單改新顯示名(百老匯/西區、法語、葡語、歐陸其他…);works.json 143→**157**;場館 ~4,900→**~5,000**;CI 改「一日兩次」;新增 audit_manual.py 與 posters/ rehost 說明。
- **docs/SOURCES.md**:自動 scraper 表補齊中國/葡萄牙/各歐洲國/tm_tours;人工策展表補巴西/阿根廷/南非/新加坡/葡萄牙/巡演段;盲區更新(南美/新加坡已涵蓋、SISTIC API 需授權、曼谷/港/馬來待查)。
- **docs/TOUR_SWEEP.md**:Les Mis 各站狀態(Birmingham 已落幕移除、新加坡/馬尼拉已落幕)、Cats/Moulin Rouge 補新加坡站;城市表新加坡/南非/南美由「待查」改「✅ 已涵蓋」。
- CHANGELOG 歷史條目保留原樣(不竄改既往紀錄)。

## [v0.56.1] - 2026-06-15 16:41
### CI 自動更新改為一日兩次
- `.github/workflows/update.yml` 排程從每日一次(09:00 UTC)改為**一日兩次**:
  - `0 22 * * *`(22:00 UTC = 台北隔日 **06:00**)
  - `0 10 * * *`(10:00 UTC = 台北 **18:00**)
- 註:GitHub Actions 排程在尖峰時段可能延遲數分鐘,非精準準點。

## [v0.56.0] - 2026-06-15 16:25
### 新加坡擴充至 2027 + 分類 label 微調 + 手動劇目新鮮度守門
- **新加坡完整檔期**(使用者指出 MBS 還有更多場次到明年):
  - 修正 **Cats** 日期 → **2026-10-29～11-15**(先前誤植 8/19–9/6,那其實是 JCS 的檔期 —— 被搜尋引擎混淆,使用者協助發現)。
  - 加 **Jesus Christ Superstar**(Sands Theatre,8/19–9/6,SISTIC)、**Legally Blonde**(Esplanade Theatre,7/29–8/9,SRT)、**Moulin Rouge! The Musical**(Sands Theatre,2027-02-16～04-04,SISTIC,東南亞首站世界巡演)。
  - JCS / Moulin Rouge 售票連結改用使用者提供的 SISTIC 直連。新加坡現 5 齣(到 2027/4)。
- **分類 label 微調**:英文 Spanish-language→**Spanish**、Portuguese-language→**Portuguese**;中文 Broadway/West End→**百老匯/西區**(僅顯示,內部值不動)。
- **新增 `scrapers/audit_manual.py`**(回應「都在 hardcode」疑慮):掃 manual.json 抓「已落幕(end_date 過期)」與「逾期未查證(_checked>120 天)」。已掛進 CI(non-blocking)。首跑即抓到並移除過期的 **Les Misérables 阿瑞納 Birmingham 站**(6/14 結束;RAH 6/18、Radio City 7/23 保留)。

## [v0.55.0] - 2026-06-15 16:05
### 東南亞 — 新加坡上線(Cats @ Marina Bay Sands)
- 查證泰國/新加坡/菲律賓國際巡演。確認多為已落幕,唯一未來且有確切日期的:
  - **Cats** @ Sands Theatre, Marina Bay Sands(新加坡),2026-08-19～09-06,SISTIC 售票,Broadway/West End,海報借資料庫現有 Cats。場館 geocode 驗證(Marina Bay Sands Theatre POI)。
- 已落幕不收:新加坡 Les Misérables Arena Spectacular(3/24–5/10)、馬尼拉 Les Misérables World Tour @ The Theatre at Solaire(1/20–2/15)。
- 待補(查到但無確切日期/售票):新加坡 **Jesus Christ Superstar**(8 月)、**Charlie and the Chocolate Factory**(東南亞首站,日期未定)。
- 曼谷目前查到多為泰國本土製作(Scenario 歷年引進國際巡演,但 2026 無確認國際 Broadway/West End 檔期)→ 暫不收。Solaire(馬尼拉)座標已備,有未來檔期即可加。

## [v0.54.5] - 2026-06-15 15:58
### 歐陸分類改名為「歐陸其他 / Other European」
- 將「歐陸音樂劇」改為 **「歐陸其他」**(en: **Other European**)。此類本質是兜底桶(德奧/法語/西語/葡語等具名強流派之外的歐陸原創),用「其他」更誠實,避免讓人誤以為存在一個統一的「歐陸」風格流派。
- 僅改 js/i18n.js 顯示 label(zh+en),內部 tag 值不動;已截圖確認 chip 顯示「歐陸其他 9」。

## [v0.54.4] - 2026-06-15 15:44
### 分類顯示改名 + 補齊最後兩張巴西原創海報(100%)
- **分類顯示改名**(使用者要求,只改顯示 label,內部 tag 值與資料管線不動):法式音樂劇→**法語音樂劇**、中國原創→**中國音樂劇**、台灣原創→**台灣音樂劇**、日本原創→**日本音樂劇**、韓國原創→**韓國音樂劇**、歐陸原創→**歐陸音樂劇**。改 js/i18n.js 的 zh label 即生效(顯示全走 `tagLabel`,無他處顯示原始值);已截圖確認 filter chips 正確顯示。
- **補齊 Rita Lee + Minha Estrela Dalva 海報**:使用者提供 URL → 下載 rehost 到 posters/(Rita Lee Sympla WAF 重試後取得 jpg;Estrela Dalva Azure blob 取得 png),Read 確認是本劇真圖。手動劇目海報 **36/36 = 100%**。
- Rita Lee 海報上「TEMPORADA ESTENDIDA ATÉ AGOSTO」證實延檔至 8 月,先前 end_date 2026-08-30 正確。

## [v0.54.3] - 2026-06-15 15:34
### 修正 Diana 分類錯誤 + 手動劇目海報大批回填
- **Diana 分類修正(使用者抓到)**:原誤標「葡語音樂劇」。海報上明寫「**um musical da Broadway**」、創作者 Joe DiPietro(劇本/詞)+ David Bryan(曲)正是百老匯 *Diana: The Musical* 原班,Tadeu Aguiar 巴西版。已加入 works.json registry → **Broadway/West End**(依原作出身,與 Wicked/TINA 同規則)。
- **Diana 海報(使用者指出有圖卻沒顯示)**:Sympla CDN 有 WAF/防盜連 —— 實測 headless 瀏覽器渲染失敗、HTTP 200/403 不穩定(URL 拿得到≠顯示得出)。故**下載一次後 rehost 到 `posters/diana-saopaulo-2026.jpg`(同源)**,並以 `<img>` + CSS background 兩種(與 app.js 一致)實際截圖驗證可顯示。
- **批次回填 20 齣手動劇目缺圖**:用資料庫中**同劇其他製作的現有海報**(ctfassets / headout / ticketm / cloudinary / utiki 等已在站上正常顯示的 host)回填——含 Wicked、Annie、Anastasia、TINA、Shrek、Oliver!、Chicago、SIX、Les Misérables、Beetlejuice、Heathers、Phantom(上海)。手動劇目海報覆蓋 14/36 → **34/36**。
- 加 `<meta name="referrer" content="no-referrer">`(隱私/相容預設;不影響既有 CDN)。
- **仍缺(誠實標註)**:Rita Lee、Minha Estrela Dalva 兩齣巴西**原創**,無同名可借,海報鎖在反爬 SPA;唯一抓得到的 og:image 是劇院全站通用 banner(非本劇)→ 拒用錯圖,維持 ♪ 佔位。若提供海報 URL(如 Diana 那樣)即可比照 rehost 補上。

## [v0.54.2] - 2026-06-15 15:20
### 南非加碼 — Oliver!(Joburg Theatre / Pieter Toerien / Artscape 全年掃描)
- 掃描南非各大場館 2026 下半年檔期,加 **Oliver!**(Cameron Mackintosh / Pieter Toerien & Cape Town Opera 製作):
  - **Oliver!** @ Artscape Opera House(開普敦),2026-12-11～2027-01-17,Webtickets。
  - **Oliver!** @ Teatro at Montecasino(約堡),2027-01-29～03-07,Webtickets。
  - registry → Broadway/West End。Webtickets 已開賣。
- 在 venue_coords.json **pin** 了 Artscape Opera House + Teatro at Montecasino 的權威座標,讓同場館的 Mamma Mia 與 Oliver! 共用同一點(marker 正確聚合)。
- 南非現有 4 齣:Mamma Mia!(開普敦/約堡)+ Oliver!(開普敦/約堡)。
- 掃描到但**未收**(附原因):**Taxi Wars: Umzila the Musical**(南非原創,registry 無對應,目前分類體系沒有「非洲原創」類,會誤標 → 待決定是否新增分類)、**Pretty Woman**(主檔期 4–5 月已過;另有來源稱 9 月 Market Theatre 場,來源可疑未證實)、**Peter Pan Jr / Alice in Wonderland**(Peoples Theatre 兒童 Jr 簡化版,非完整職業製作)。

## [v0.54.1] - 2026-06-15 15:14
### 非洲 — 南非確認有(資料清理,非新增)
- 查證:非洲音樂劇主場是南非。Ticketmaster.co.za scraper **早就抓到** Mamma Mia! 兩場,本版只做清理與驗證:
  - **Mamma Mia!** @ Artscape Opera House(開普敦),2026-09-03～10-10
  - **Mamma Mia!** @ Teatro at Montecasino(約翰尼斯堡),2026-10-16～11-22
  - 兩場日期一律以 TM(實際售票來源)為準,座標經 reverse/forward 驗證正確(Artscape、Montecasino 複合體內),registry → Broadway/West End。
- 我一度手動加了 Mamma Mia,但 TM 版日期更準(我猜的 10/11、11/30 < TM 的 10/10、11/22)→ **撤掉手動筆,避免用較差日期蓋掉 TM**。
- 過濾掉誤入的 **Ndlovu Youth Choir**(南非青年合唱團演唱會,非音樂劇,卻被 TM 歸在 musicals 分類 + 誤標 Broadway/West End)→ 加進 not_musical.json。
- 已過檔不收:Pretty Woman(~4/19、5/24)、CATS(Montecasino 2/22 結束)、Rocky Horror(5/31)。

## [v0.54.0] - 2026-06-15 15:02
### 阿根廷上線 — 布宜諾斯艾利斯(Corrientes 大道劇場區)
- 之前阿根廷卡在 PlateaNet 403 + 清單無連結。改從可讀新聞稿查到兩齣**現演**百老匯原作的西語製作,逐齣查證日期+售票連結+Nominatim geocode:
  - **Annie** @ Teatro Broadway(Corrientes 1155),2026-03-19 起演(open run),Plateanet obra 33501。
  - **Anastasia** @ Teatro Astral(Corrientes 1639),2026-05-05 起演(open run),Atrápalo 售票。
- 兩齣 registry 均為 Broadway/West End → 依「原作出身」歸類(與巴西 Wicked/TINA 同規則,不因西語製作改判)。結束日未公布 → end_date=null,前端以 12 個月票期視窗自動封頂。
- 待補(尚未查到確切場館/檔期/售票):**Company**(Fer Dente)、**Chicago**(Flor Peña/Laurita Fernández)。

## [v0.53.2] - 2026-06-15 14:56
### 修正:Shrek 沒結束(我判斷錯誤)+ 加入
- 上一版我說 Shrek「6/7 已結束」是**錯的** —— 我只引用編輯文章的原定檔期,沒查官方頁。官方站 shrekomusicalbrasil.com 寫「EM CARTAZ ATÉ 05 DE JULHO」,**已延檔到 2026-07-05**。
- 加 **Shrek the Musical(聖保羅 Teatro Renault,2026-04-15～07-05)**,Broadway/West End,附 Tickets for Fun 售票連結。
- 連帶複查 **Flashdance**:官方原定 4/9～5/31,售票頁最後場次 5/30,無延檔,多來源一致 → 確實已結束,維持不收。
- 巴西現有 6 齣:Broadway 巡演 TINA、Wicked、Shrek + 葡語原創 3 齣。

## [v0.53.1] - 2026-06-15 14:42
### 巴西 +《Wicked》里約(百老匯官方授權複刻版)
- 使用者指出巴西重點是國際 Broadway/西區大製作。查證後加 **Wicked(里約 Cidade das Artes,2026-07-15～08-09)**——百老匯官方授權葡語複刻版,已在 Sympla 開賣(24h 售出萬張)。Broadway/West End,附 Sympla 售票連結 + 場館座標(Nominatim)。
- 巴西現有 5 齣:Broadway 巡演 TINA(聖保羅)、Wicked(里約)+ 葡語原創 3 齣。
- 未加(查證後不符「有確切日期+售票連結」門檻):**Hadestown** @ Renault(僅「2026 下半年」、無確切日期/售票)、**Flashdance/Shrek**(可讀來源顯示 5/31、6/7 已結束,與「熱演中」說法衝突,待確認新檔期)。有確切資訊我再補。

## [v0.53.0] - 2026-06-15 14:36
### 巴西聖保羅(手動精選)+ 新增「葡語音樂劇」分類
- 巴西主流票務全反爬牆(Sympla=Cloudflare、Ingresso=SPA、場館站 Santander=Akamai「Access Denied」),無法自動抓。改從可讀的編輯型清單(WebFetch)取**真實現演資料**,手動加進 `manual.json`(逐齣查證日期+售票連結+Nominatim geocode 場館,不亂填):
  - **TINA - The Tina Turner Musical** @ Teatro Santander(→Broadway/West End)
  - **Rita Lee, uma autobiografia musical** @ Teatro Porto Seguro
  - **Minha Estrela Dalva** @ Teatro do SESI(FIESP)
  - **Diana, a Princesa do Povo** @ Teatro Liberdade
  四齣**都附 Sympla/SESI 售票連結**。
- **新增分類「葡語音樂劇」**(Portuguese-language):`build_shows.py` country Brazil/Portugal + bol.pt 來源 → 葡語(註冊表仍優先,故巴西的 TINA 仍歸 Broadway/West End);加進 TAG_DEFS(色 #65a30d)+ i18n 中英;Portugal 從 CONTINENTAL_C 移到葡語。
- 阿根廷:PlateaNet 硬 403,可讀清單只有過期(Jan–Mar)且無售票連結,**暫不加**(不上沒驗證的資料)。

## [v0.52.0] - 2026-06-15 13:07
### 新增葡萄牙(BOL)—— 南美/葡萄牙缺口第一步
- 查證:Ticketmaster 在南美/葡萄牙這區**只有墨西哥有音樂劇**(274 筆已收),巴西/阿根廷/智利/哥倫比亞/秘魯/葡萄牙 TM 全 0,得做本土平台 scraper。
- **`portugal.py`**(BOL / bol.pt):每個事件頁有乾淨 JSON-LD Event(名稱/演期/海報/場館 + **內建 geo 座標 WGS84 + 城市**,免 geocode)。抓首頁事件、篩 `catTeatro` + 音樂劇(標題含 musical 或對上 works.json 註冊劇)→ **Evita @ 里斯本 Capitólio** 上線(Broadway/West End)。
- 註:BOL 類別枚舉(全列)頁面是 JS 載入,目前用首頁精選,葡萄牙當前音樂劇本就少。巴西(Ingresso 混淆 SPA)、阿根廷(PlateaNet SSL)較難,待續。

## [v0.51.0] - 2026-06-15 12:49
### me.html / u.html 雙語化 → 全站中英一致
- me.html(個人足跡)+ u.html(公開分享頁)套用共用 i18n:nav、hero、分享列、儀表板卡片標題、紀錄表、新增/編輯表單、按鈕、提示、alert、空狀態全部中英對照;同款 🌐 中文|English 切換器 + 每頁標題;切語言即時重繪(`mm-langchange`)。
- u.html 表格欄位(Date/Musical/Theatre…)、分頁(總覽/紀錄)、「找不到此檔案」、profile 標題與「看過 N 場(全球)」皆雙語。
- 處理 `t` 區域變數遮蔽(u.js 用 `TL()` 模組別名避開 renderTable 內的 `t`),結果清單用 DOM/esc 不注入。
- Playwright 驗證:me/u 的 EN↔ZH 切換、title、空狀態皆正確,無 JS error。
- **至此 index / theatres / me / u 四頁全部雙語**,切換器一致,預設依瀏覽器語言。

## [v0.50.2] - 2026-06-15 12:33
### theatres.html 雙語化
- theatres.html 套用共用 i18n:tagline、nav、搜尋 placeholder、結果計數(「5,003 theatres」/「1 theatres (of 5,003)」↔「個劇院（共）」)全部隨語言切換;同款 🌐 中文|English 切換器 + 每頁標題;加 description/canonical/hreflang。`theatres.js` 動態字串走 `t()` 並於 `mm-langchange` 重繪。Playwright 驗證通過。
- 註:me.html / u.html 本就以英文為主(nav/按鈕/標籤皆英),美國訪客已可讀;後續再補其切換器與中文化。

## [v0.50.1] - 2026-06-15 12:15
### AI-search / SEO 探索層
- **`llms.txt`**(llmstxt.org 標準):給 AI 答題引擎的網站 markdown 摘要(用途、主要頁面、資料來源、血統標籤語意說明)。
- **`robots.txt`**:明確歡迎 AI 爬蟲(GPTBot/OAI-SearchBot/ClaudeBot/PerplexityBot/Google-Extended/Applebot-Extended…)+ 指向 sitemap。
- **`sitemap.xml`**:主要頁面 + 首頁 hreflang(en/zh-Hant/x-default)。
- **JSON-LD 結構化資料**(schema.org WebApplication,雙語 inLanguage、免費)寫進 index.html。
- **視覺隱藏 `<h1>`**(雙語關鍵字)供無障礙 + 非 JS 爬蟲。
- 驗證:JSON-LD/sitemap 格式有效,robots/sitemap/llms 皆 200,頁面無 JS error。

## [v0.50.0] - 2026-06-15 12:11
### 雙語化 index.html(中/English)+ 最佳實踐語言切換 + SEO 基建
- **i18n 系統**(`js/i18n.js`):全部 UI 字串中英對照(tagline/nav/搜尋/分類/日期/售票/footer/計數…),`t()` + `data-i18n` 標記;動態字串改走 `t()`,切換語言即時重繪(`mm-langchange`)。預設依瀏覽器語言(zh* → 中文,否則 English)。
- **語言切換器(查 i18n UX 最佳實踐後做)**:右上 **🌐 地球 + 「中文 | English」分段**,當前高亮、母語名稱、**不用國旗**(國家≠語言)、圖示+文字。選擇存 localStorage。
- **SEO**:雙語 `<title>`+`<meta description>`;`?lang=en|zh` 可索引 URL + `hreflang`(en/zh-Hant/x-default)+ canonical + Open Graph;切換語言會更新網址與 canonical(可分享、語言一致)。
- Playwright 驗證:EN/ZH 全字串切換、URL 更新、切換器高亮皆正確。
- (待續:theatres/me/u 其他頁雙語化 + AI-search 檔案 JSON-LD/llms.txt/robots/sitemap。)

## [v0.49.0] - 2026-06-15 11:57
### 分類數字改為「當月」+ 時間 bar 縮短
- **分類 pill 數字現在對應選取月份**(`app.js`):原本永遠顯示總數,改成隨月份滑桿+搜尋即時更新該分類當月上演數(`updateTagCounts()` 每次 render 算)。pill 集合維持穩定(不會跳出跳進),當月為 0 的淡化顯示(`.tag-zero`)。驗證:本月 Broadway 258/韓國 25 → +6 月 Broadway 160/韓國 1/中國 0。
- **時間 bar 縮為約 2/3 長**(`style.css`):`left/right` 10% → 23.5%(地圖區寬 80%→53%)。

## [v0.48.0] - 2026-06-15 11:48
### theatres.html 搜尋加可點結果清單(點一下飛到該劇院)
- 使用者反映:搜尋「上海大劇院」只顯示「1 個劇院」數量,卻沒有可點的東西。原本搜尋只過濾地圖標記+顯示數量,標記還在群集裡、看不到也點不到。
- 新增**搜尋結果下拉清單**(`theatres.html` / `theatres.js` / `style.css`):打字即列出符合的劇院(名稱+城市/國家,最多 60 筆),**點一下飛到該劇院並彈出資訊框**(`flyTo` + 飛行結束後開 popup)。清單用 DOM textContent 建構(非 innerHTML),scraped 名稱不會注入。
- Playwright 互動截圖驗證:搜「上海大劇院」→ 清單顯示 Shanghai Grand Theatre → 點擊飛到人民廣場 + popup 正確。

## [v0.47.1] - 2026-06-15 11:35
### 中國場館精準驗證(Google 逐館比對)→ 修 5 筆 + 移除 1 個虛構場館
- 高德/百度/騰訊申請 key 都要中國身分證實名認證(無法),改用既有 Google key 對 118 個中國場館逐一 POI 比對(GCJ→WGS84),揪出座標偏 >200m 的。
- **修正座標**:廣州…(見下)、张家港保利大剧院(偏南 14km → 31.8714,120.5711 張家港市區)、北京艺术中心歌剧院(誤放市中心 → 39.9021,116.6429 通州城市綠心)、延边工人文化艺术中心(偏 30km → 42.8905,129.5029 延吉)、海口演艺新空间(→ 20.0301,110.3051 海口灣)。有劇的 3 場(Sherlock/Matilda)經 venue_coords.json 同步。
- **移除虛構場館**:`廣州保利大劇院` 座標竟是南京的(複製錯),且 web 查證**廣州根本沒有這家**(只有廣州大劇院)——刪除。
- Google 對「X保利大剧院」會誤配成上海,經查證我原存的(苏州狮山/深圳滨海等)反而是對的,未動。catalog 5004→5003。

## [v0.47.0] - 2026-06-15 11:11
### 全球場館國家標籤總驗證(reverse-geocode)→ 修 43 筆貼錯,theatres.html 同步
- 用 `verify_geo.py` 對全球(扣中國)**4843 個場館**逐一 reverse-geocode(新帳號 Google 額度,約 $24),反查每個座標的真實國家。
- 抓出 **43 筆國家標籤貼錯**(座標對、標籤錯),全部修正:
  - discover 把鄰國/同名城市場館抓錯國(雪梨歌劇院→標 Reading/UK、Lviv 國家歌劇院→標 Poland 實烏克蘭、維也納國家歌劇院→標捷克、紐卡索 UK 多館→標 Australia、Lancaster PA→標 UK…)→ 改 `*_discovered.json` 真實國家+城市(49 筆)。
  - broadway.org 巡演把加拿大/墨西哥巡演站標 USA(National Arts Centre/Place Des Arts/Queen Elizabeth Theatre/Showcenter Monterrey…)→ 新增 `data/venue_country.json` 國家覆蓋,`build_shows.py` 套用(18 筆 show)。
- 重生 venues_catalog.json:**重新驗證後 0 筆國家不符**;13 個重複場館自動合併(5017→5004)→ push 後 **theatres.html 同步**。
- Türkiye=Turkey 同國別名加進 verify_geo,不再假警報。

## [v0.46.0] - 2026-06-15 10:06
### 時間滑桿固定 1 年範圍(自動滾動)+ 場館座標總檢 + 全球驗證工具
- **時間滑桿改成「最遠 +12 個月」硬上限,自動滾動**(`app.js`):現在 2026-06 → 拉到 2027-06;到 2026-07-01 → 自動變 2027-07。原本是拉到資料最遠那筆(上限 48 個月)。與開放式駐演的 12 個月顯示上限一致。
- 全 1424 齣座標健檢:**0 落在 (0,0)、0 跑出國界、僅 1 齣缺座標**。補上義大利 Valenza 的 Teatro Sociale(Nominatim/OSM,45.0131,8.6443)。
- 新增 `scrapers/verify_geo.py`:全球(扣中國)場館 reverse-geocode 驗證工具,反查每個座標的真實國家、揪出標籤貼錯(如雪梨歌劇院被標 Reading/UK)的場館。
- 「新場館預設座標可疑」原則:有劇場館中非中國純靠 scraper 座標的 ~10 個已用 Nominatim 比對全數 ≤1.4km;台灣場館 0 個未驗證(全已收錄)。

## [v0.45.4] - 2026-06-15 02:22
### 全面改用真實場次 showTime(全 91 齣保利劇日期)+ 修正 v0.45.3 抓錯
- 對全部 91 齣保利劇跑了 stored vs 真實場次比對。過程中發現 v0.45.3 的 real_run **抓太貪**(grep 整個 JSON blob 的所有日期),把 `saleBeginTimeStr`(開售日)誤當演出日 —— 所以 Ash亚斯 被算成 05-23 起,其實 05-23 是開售日,**真正首演是 06-19**。
- 正解:只讀 `data.showInfoDetailList[].showTime`(真實場次時間),不碰開售日。**全部 91 齣改用真實場次取 min/max**(productShowTime 只當 fallback),`china_poly.py` 每齣多抓一次 `/good/shows/{id}`。
- **Ash亚斯 = 2026-06-19 ~ 2026-06-27**(4 場,與大麥完全一致)。SIX/Phantom 等抽驗皆與場次相符。0 筆 null。

## [v0.45.3] - 2026-06-15 02:12
### 確認並修正:Ash亚斯 根本不到 2027(用實際場次 API 查證)
- 接續 v0.45.2:不該猜「開放式駐演」就 end=null。去查保利**實際場次 API**(`/good/shows/{id}`)——《Ash亚斯》真實排期只有 `2026.05.23、06.19、06.20、06.26、06.27`,**沒有任何 2027 場次**。`2027.06.27` 純粹是 productShowTime 給沉浸式駐演空間的假開售窗口。
- 改法:`china_poly.py` 對窗口 >120 天的劇,改抓 `/good/shows/{id}` 的真實場次取 min/max → **Ash亚斯 = 2026-05-23 ~ 2026-06-27**(與大麥 6 月批次一致)。

## [v0.45.2] - 2026-06-15 02:08
### 修正:沉浸式駐演超長檔期(Ash亚斯 顯示到 2027)
- 使用者抓到《Ash亚斯》(深圳保利剧聚空间)顯示 2026.06.05–**2027.06.27**,但大麥只顯示 2026.06.19–06.27。原因:保利的 `productShowTime` 對沉浸式駐演空間給的是**整個開售窗口**(到 2027),但票只分批開賣,大麥顯示的是當前批次。硬寫 2027 閉幕日會誤導成確定的一年檔期。
- 修法(已被 v0.45.3 取代):把 >120 天檔期當開放式駐演 end=null。

## [v0.45.1] - 2026-06-15 02:01
### 修正:大麥搜尋連結用錯路由(會轉 404)
- v0.45.0 用的 `search.damai.cn/search?keyword=` 其實會 **302 轉址到 `www.damai.cn/404/`**(使用者抓到)。正確的是 `search.damai.cn/search.htm?keyword=`(大麥沿用多年的搜尋頁,200 不轉址)。91 筆保利售票連結全部改正,逐一驗證。

## [v0.45.0] - 2026-06-15 01:52
### 修正:福尔摩斯血統 + 保利連結 + 接中演院线
- **福尔摩斯的音乐探险 → 法式音樂劇**(原誤標中國原創):查證為法國音樂劇 **Sherlock Holmes: L'Aventure Musicale**(Samuel Safa,2022 巴黎 Le 13e Art 首演)。works.json 登記,15 個巡演城市 + 變體「夏洛克福尔摩斯音乐探险之旅」全部統一歸位。
- **保利售票連結修正**(使用者抓到連進去都是首頁):`weixin.polyt.cn` 是微信內專用 SPA,瀏覽器只會渲染空殼。改成**大麥搜尋連結**(`search.damai.cn/search?keyword=劇名`)——大麥是大陸主要票務,搜尋頁真人瀏覽器可正常開(反爬只擋自動化非真人點擊),使用者能實際找到並購票。
- **接中演院线**(`china_chinaticket.py`,中票在线 chinaticket.com):全國院線、SSR 無反爬、詳情頁帶街道地址可 geocode。目前音乐剧庫存薄(此刻僅《红莲》),但廣州大劇院/廈門閩南大戲院等中演獨家館上劇時會自動補進。`build_shows.py` 跨來源去重(group+city+venue)避免與保利重複。
- 中國維持 100 齣 / 42 城市,全站 1424 齣,audit 0 misses。

## [v0.44.1] - 2026-06-15 00:55
### 修正:小城保利場館不該跳過 —— 用官方街道地址全部 geocode 對
- 上一版把南昌/启东/张家港/衡阳/衢州 5 個保利大剧院「跳過」其實也是認輸。**保利 API 的劇院清單(`/good/shops/city`)本身有 `detailAddress` 精確街道地址**——用街道地址 geocode 比場館名可靠太多。全部 geocode 對:启东=江海南路钱塘江路口、张家港=杨舍镇人民东路605号、南昌=红谷滩南龙蟠街、衡阳=石鼓区文化中心、衢州=柯城区三江东路(衡阳/衢州地址另經 web 查證石鼓区/柯城区)。
- **連帶修正**:苏州保利大剧院原 geocode 也錯(被配到 31.66),用官方地址「吴中区东苑路1号」修正到 31.269,120.627。
- 7 個原本跳過的演出全部回歸:china_poly 84 → **91 齣**,中國 93 → **100 齣 / 42 城市**,99 有海報。全站 **1424 齣**,audit 0 misses。

## [v0.44.0] - 2026-06-15 00:48
### 新增:破解保利票务官方 API → 中國 93 齣 / 37 城市
- 不該那麼快認輸。大麥/貓眼有反爬牆,但**保利院線(全國 ~80 家劇院)的微信 H5 票務後端是開放 JSON API**(讀取不擋驗證碼)。逆向 H5 bundle 得到:`https://weixin.polyt.cn/platform-backend`(header `Channel: theatre_wx`),`POST /good/search-products-data {keyword,page,size}` 分頁產品(MyBatis-Plus,真正分頁參數是 `page`),`/dictionary/product/categories` 給音乐剧 categoryId。
- `scrapers/china_poly.py`:翻頁 keyword=音乐剧、留 categoryName=音乐剧、每齣一筆 → **84 齣官方資料(標題/演期/城市/場館/真海報)**,遠勝聚合站。座標**只認** cn_venues.json,配不到跳過(7 個小城保利館 Google 索引不到而略過)。
- **座標補強**:批次 geocode 22 個保利場館寫進 cn_venues.json(Google Places + GCJ→WGS84 + 「距城市中心 <0.4°」sanity check,擋掉 Google 一直把各地保利大剧院誤配成上海/苏州那家的錯誤)。
- **跨來源去重**(`build_shows.py`):同 group+城市+場館的記錄(如武漢 Phantom 同時出現在 polyt 與 ypiao)合併,留有海報那筆。
- **血統修正**:works.json +Hedwig and the Angry Inch(搖滾芭比)、Lizzie、The Curious Case of Benjamin Button、Murder Ballad(謀殺歌謠)——皆英美原創,原本誤落 中國原創;排除致敬MJ秀、明星音樂會(非音樂劇)。
- **結果:中國 15 → 93 齣 / 6 → 37 城市**(深圳/瀋陽/重慶/濟南/鄭州/東莞/煙台/太原/福州/海口…),92 齣有海報。全站 1339 → **1417 齣**,audit 0 misses。CI 加 china_poly.py。

## [v0.43.1] - 2026-06-15 00:16
### 修正:蘇州《瑪蒂爾達》補回(不該因 geocode 失敗就略過真實場館)
- 上一版把蘇州《瑪蒂爾達》略過的處理很怪 —— 苏州狮山大剧院是**真實存在的場館**(2024-08-31 啟用,上海大劇院參與營運,位於高新区狮山文化广场、天狮湖与狮子山之间),不該因 Google 配錯就放棄整齣。
- 之前配錯的原因:query 帶了「文化艺术中心」被拉到工業園區(金鸡湖畔)那個不同的館。改用精確 query `狮山大剧院 苏州高新区狮山文化广场` → 高新區正確落點 **31.29723, 120.56538**(GCJ→WGS84,城市範圍 sanity check 通過),寫入 `cn_venues.json`。
- 《瑪蒂爾達》補回:works.json Matilda 補大陸譯名 alias「玛蒂尔达/瑪蒂爾達」(原本只有「瑪蒂達」,OpenCC 折不到大陸譯法)→ 蘇州場正確歸 **Broadway/West End 並繼承 Matilda 海報**。
- 中國 14 → **15 齣 / 6 城市**(+蘇州),全站 1339 齣,audit 0 misses。

## [v0.43.0] - 2026-06-14 23:17
### 新增:中國其他城市(北京/武漢/杭州/南京)+ Fan Letter 台譯
- **中國從「只有上海」擴到 5 城市**(`scrapers/china_ypiao.py`):大麥/貓眼/保利/天橋官網全是 SPA+反爬牆,改用有票网(ypiao.com)聚合站的伺服器渲染列表做多城市發掘。只當**發掘來源**:僅留 `音乐剧《…》`(濾掉演唱會/音樂會)、座標**只認** `cn_venues.json`(Google geocode+GCJ→WGS84)、**配不到已驗證座標的劇直接跳過**(蘇州《瑪蒂爾達》因狮山大剧院座標 Google 連兩次配錯——配到杭州大劇院/工業園區文化中心——寧缺勿放錯而略過)。新增 6 齣:
  - 北京:道林格雷的画像(韓國原創)、人间失格(中國原創)
  - 武漢:剧院魅影 → **The Phantom of the Opera / Broadway/West End**(繼承 Phantom 海報)
  - 上海:危险游戏 → **Thrill Me / Broadway/West End**(外百老匯)
  - 南京:她的海(中國原創)、杭州:蝶变(中國原創)
- **座標補強**:`cn_venues.json` +上海共舞台、杭州东坡大剧院(Google geocode+GCJ→WGS84,均做城市範圍 sanity check)。
- **血統登記**:works.json +The Picture of Dorian Gray(韓)、Thrill Me(Off-Broadway);Phantom 補簡體 alias「剧院魅影/歌剧魅影」(原本只認繁體導致武漢場誤判中國原創)。
- **Fan Letter** 補台灣譯名《光的來信》alias(你提供:台譯光的來信、陸譯粉絲來信、韓原팬레터)。
- 上海文化廣場座標對齊 cn_venues 的 Google 值(31.2127,121.4581)。
- 全站 1332 → **1338 齣**,中國 1 → **14 齣 / 5 城市**,audit 0 misses。

## [v0.42.0] - 2026-06-14 22:48
### 新增:中國音樂劇(上海文化廣場)
- **中國資料來源上線**(`scrapers/china.py`):大麥/貓眼有反爬牆(x5secdata 滑塊),改從**場館層級**抓——上海文化廣場(上汽·上海文化廣場)是大陸音樂劇旗艦館,且 ASP.NET 前端後面有乾淨 JSON API:
  - `POST /webapi.ashx?op=GetTBLEVENTListForCalendar`(year/month)→ 當月所有檔期
  - `POST /webapi.ashx?op=GettblprogramCache`(id)→ 權威 genre / 演期 / 海報 / 場地 / 語言
  掃未來 13 個月,只留 genre = **音乐剧** 的節目,每齣輸出完整演期。共 **7 齣**(全有海報,逐一 HTTP 200 image/jpeg 驗證)。
- **按血統正確分類**(非按演出地)——這正是你要的「上海的 Phantom 屬於百老匯」原則:
  - 太阳王 → **法式音樂劇**(Le Roi Soleil,場館自標「法语原版」)
  - 我的遗愿清单 / 粉丝来信 → **韓國原創**(My Bucket List / Fan Letter)
  - 基督山伯爵 中文版 → **歐陸原創**(俄羅斯莫斯科輕歌劇院 2008 原版授權;**修正**舊 works.json 把它誤標 Broadway/West End)
  - 快乐即逝 → **西語音樂劇**(場館自標「巴塞罗那当代音乐剧」)
  - 大状王(粵語)/ 锦衣卫之刀与花(新國風)→ **中國原創**
- works.json +6 entries、Le Roi Soleil 補中文 alias;`build_shows.py` SOURCE_FILES +china.json、tag 來源 `shculturesquare`(域名已失效被印尼站接管)→ `shcstheatre`;CI 加 china.py。
- 全站 1325 → **1332 齣**,audit 0 misses。

## [v0.41.1] - 2026-06-14 22:20
### 修正(海報圖片 + Stage 德國海報全面修正 + Frost→Frozen + 去重)
- **小圖空白 bug**(使用者抓到 Everybody's Talking About Jamie「有大圖卻沒有小圖」):圖片 URL 含撇號(`'`),原本 marker / 側欄 / 地圖 pin 的 `background-image:url()` 用 `esc()` 做 HTML 轉義(`'`→`&#39;`),但 CSS **不會** decode HTML entity → url 壞掉,只有彈窗 `<img>` 正常。新增 `cssUrl()`(`js/app.js`、`me.js`、`u.js`)對 `' " ( ) 空白 反斜線` 做 percent-encoding,所有 `background-image` 改用它。
- **Stage 德國海報全面修正**(使用者抓到 Frozen 沒小圖):前一版號稱「13 檔 0 缺漏」其實是假完成 —— 7 檔抓到的是首頁通用 banner(`SEN-Web-Startbanner-ComposingNavi`,全部變成 Prada 的圖)、2 檔是 `.tif`(瀏覽器**根本不能顯示**)。改寫 `pick_image()`:優先抓該劇專屬的 `ShowOnly-{劇碼}-900x1459px` 直幅海報(每頁只有當齣劇有 ShowOnly,其他劇用 Keyvisual/Header),次選可顯示的 og:image(排除 .tif),再次用劇碼比對 → 13 檔**全部對應到各自正確海報**(WWRY/BTTF 還從 logo 升級為直幅海報),逐一 HTTP 200 + `image/webp` 驗證。
- **Frost → Frozen**:Frozen 在挪威/丹麥叫「Frost」(works.json 已登記為 alias),但 `build_shows.py` 的 Ticketmaster 合併路徑漏套 `canonical_title()` → 群組標題顯示「Frost」。補上後 frozen 群組 14 筆標題全部統一為 **Frozen**(辨識度優先,有正式英文劇名就用)。
- **Bibi & Tina 誤判**:Stage `canon()` 用裸字 `"tina"` 把兒童耶誕劇「Weihnachten mit Bibi und Tina」誤判成「TINA - The Tina Turner Musical」→ 改為 `"tina turner"` 精確比對。
- **Paddington 去重**:行銷尾綴「- Relaxed Performance」等表演型態字串導致同劇分裂,`build_shows.py` 加 `PERF_TYPE_RE` 剝除,`audit_dups.py` 強化偵測。

## [v0.41.0] - 2026-06-14 21:54
### 新增 / 修正(奧地利 + 中東去重 + 波蘭)
- **奧地利**(`austria.py`,維也納 VBW musicalvienna.at):補上 Das Phantom der Oper(Raimund Theater)——原本全奧地利只有 TM 的 Mamma Mia。
- **中東標題清乾淨 + 去重**:Platinumlist 行銷標題(「Chicago Musical Event Live in Dubai」「… in Abu Dhabi」「… Musical Event Live」)改 `middleeast.py` 清理 + build 端 `strip_city_qualifier` 加剝「in 城市」尾綴 → 杜拜 Chicago 與既有 manual 那筆**合併成 1 筆**(含 Coca-Cola Arena 演出頁 + 官網 + Platinumlist 三連結);Charlie/Cats 標題乾淨歸位。
- **杜拜 Chicago 官方售票連結**改指定演出頁 `coca-cola-arena.com/theater/1894/chicago-the-musical`(原為首頁)。
- 波蘭:eBilet 限流解除可抓 listing,但逐場 detail 頁仍被限流(待改 listing-only)。

## [v0.40.3] - 2026-06-14 20:59
### 新增(陸/台/港中文譯名一次查齊)
- agent web 查證 112 部英美作品的中文譯名,合併進 works.json(加 90 個,跳過 0 跨作品衝突):每部收齊**大陸/台灣/香港**多種譯名 + 音譯/意譯。例:Legally Blonde=律政俏佳人(陸)/金髮尤物(台)/律政可人兒(港);Oliver!=孤雛淚/霧都孤兒/苦海孤雛;Mean Girls=賤女孩/辣妹過招;Jersey Boys=澤西男孩/紐澤西男孩;Hadestown=冥界/黑帝斯城/哈迪斯城/冥府。搭配既有 OpenCC 簡繁互通,陸台港用詞 × 簡繁字形全可搜。
- 13 部確認無通用中文名(Fifty Shades!/Murder for Two/Gutenberg/Ride the Cyclone/Finian's Rainbow/Menopause/Our Ladies/Altar Boyz/Midnight/Barbershopera/Lempicka/We Will Rock You/Me and My Girl)。

## [v0.40.2] - 2026-06-14 20:24
### 修正
- 修中文譯名錯字 + 補各地變體:Legally Blonde→律政俏佳人(陸)/金髮尤物(台,原誤植「金法」)/律政可人兒(港);Hadestown→冥界/冥界：地下城/黑帝斯城/哈迪斯城(原誤植「哈帝」);Hamilton 加漢米爾頓。已派 agent 系統性查齊全部 112 部的陸/台/港譯名,回來統一合併。

## [v0.40.1] - 2026-06-14 20:19
### 變更
- 再補英美作品中文譯名(Funny Girl 妙女郎、Spamalot 火腿騎士、Gypsy 玫瑰舞后、Nine 華麗年代、Heathers 希德姊妹幫、La Cage 鳥籠、& Juliet 茱麗葉)。英美作品 94 部有中文名,剩 18 部為無通用中文名的冷門/新劇(Hair、Gutenberg、BOOP、Lempicka 等)。

## [v0.40.0] - 2026-06-14 19:44
### 新增(挪威 + 中東 + 中文搜尋強化)
- **挪威**(`norway.py`):7 齣——Folketeateret(Les Misérables、Annie、Phantom 2027)、Det Norske Teatret(Europavisjonar、Pippi、Cabaret)、Trøndelag(Matilda)。建築級座標。修正:TM Discovery API 不含挪威常駐音樂劇(誤判),改專屬 scraper。
- **中東**(`middleeast.py`,Platinumlist Gulf):4 齣——杜拜 Chicago、阿布達比 Charlie and the Chocolate Factory / Cats(波斯灣多為零星巡演,屬正常)。
- **中文搜尋:台/中用詞 + 簡繁字形互通**。build_shows `alt` 欄位用 OpenCC 展開**簡繁雙形**,works.json 補台灣+中國雙版譯名(Phantom 加中國「劇院魅影」、Wicked 加「女巫前傳/魔法壞女巫」、Madagascar「馬達加斯加」… 共 34 個)。實測:搜「劇院」「剧院」都→Phantom,「女巫前傳」「魔法坏女巫」→Wicked,「馬達加斯加」「马达加斯加」→Madagascar。
- **「中國原創」tag 基礎建好**(classify_tag + 前端 pill);全中國音樂劇 scraper agent 進行中(大麦/猫眼/上海文化广场 多源)。
### 修正
- 標題尾端**裸年份**剝除(「Phantom of the Opera 2027」→ 對到 Phantom、不再誤判歐陸)。
- medley gala 過濾加 `night at/of the musicals`(剔「A Night at the Musicals」)。
- middleeast.py `end` 為 None 時預設 start(避免比較崩潰)。
- 最終 1326 劇,去重稽核 0 漏合併。

## [v0.39.2] - 2026-06-14 19:26
### 變更
- **羅密歐與茱麗葉 2027-28 法國巡演**(8 站,manual.json)海報換成 jds.fr 指定圖(Cécilia Cara 版,已驗證 HTTP 200 webp)。

## [v0.39.1] - 2026-06-14 19:17
### 修正(去重根因 + 自動稽核)
- **`presents:` 冒號版 + `production of` 前綴**沒被 v0.39.0 蓋到(「Ford's Theatre presents: Come From Away」「NYT production of …Little Mermaid」「All-City Musical presents: Mean Girls」「Toby's…Presents: Mean Girls」)→ clean_title 前綴 regex 補上冒號與 production of。
- **結尾標點**讓「MAMMA MIA! The Musical!」(尾端 `!`)沒被剝成 mamma mia → 和「Mamma Mia!」分兩組;_norm 的 musical 尾綴 regex 改 `musical\W*$` 容許結尾標點。Mamma Mia 現為單一組。
- **新增 `scrapers/audit_dups.py`**:自動稽核去重漏合併 + promoter 前綴 + 套票垃圾殘留,接進每日 CI(build 後跑)。以後這類問題在 CI/我這邊先抓出,不再靠人工發現。修後稽核 0 問題(1316 劇 / 394 組)。

## [v0.39.0] - 2026-06-14 19:13
### 新增(歐洲擴張 — 平行 agent 建 4 國 scraper)
- **義大利**(`italy.py`,teatro.it JSON-LD):22 齣(Notre Dame de Paris、Moulin Rouge、Il Principe d'Egitto、Forza Venite Gente、Frida、Lupin…);主流是 TicketOne/teatro.it 非 Ticketmaster,補上漏掉的 7 成。
- **瑞典**(`sweden.py`,showtic.se JSON API):8 齣(Chicago、Grease、Emil i Lönneberga、Ronja…)。
- **荷蘭**(`netherlands.py`,stage-entertainment.nl SSR):2 齣(& Juliet、Moulin Rouge;NL 目前僅這些常駐)。
- **波蘭**(`poland.py`,eBilet.pl):scraper 已建,惟 eBilet 目前回 429 限流,待 CI/限流解除產出。
- 四者皆過濾非音樂劇 + 大場館建築級座標;Google geocode 補新場館座標。掛每日 CI。

### 變更 / 修正(標題與搜尋)
- **拿掉中文譯名前綴**:`Jesus Christ Superstar 萬世巨星` → `Jesus Christ Superstar`、`Cats Macskák` → `Cats`(顯示 canonical;中文/外語別名移到 `alt` 欄位**仍可搜尋**)。
- **搜尋去重音 + 去標點(全劇通用)**:`les mise`→Les Misérables、`notre dame`→Notre-Dame de Paris、`mamma mia`→Mamma Mia!、`悲慘世界`→Les Misérables 都命中(app.js `fold()`)。
- **標題清理**:`{Company} presents X`→`X`(Lyric Theatre of Oklahoma presents Annie → Annie)、剝場館尾綴(`Jesus Christ Superstar - The Palladium`→…)、外語 `Il/De Musical` 尾綴正規化(`Moulin Rouge! Il Musical`→對到 Moulin Rouge)。
- 修 `stage-entertainment` 字串誤把**荷蘭**站當德國(`& Juliet` 一度標德奧);改以國家判定。
- works.json 補進口劇別名(Amélie、& Juliet NL、A Christmas Carol 等)。

## [v0.38.3] - 2026-06-14 18:31
### 修正(去重 — 系統性掃全庫)
- loose-key 審計找出 **8 組「應合併卻分開」**,全是同類病根,根因一次修掉:
  - **TM 加自己城市的尾綴 `(Chicago)`**(Water for Elephants、Book of Mormon、& Juliet、Kinky Boots、Dirty Dancing、The Notebook、SUFFS)→ 新增 city-aware `strip_city_qualifier`,只在括號內容＝該筆城市時才剝(真標題如「(Carry a Cake Across New York)」不動)。
  - **年份尾綴 `(1993)`**(Mrs Doubtfire)→ clean_title 剝除 `(19xx/20xx)`。
  - **套票/訂房上賣垃圾**(「Official … Ticket+ Hotel Packages」「VIP/suite/parking packages」「meet & greet」)→ 全域剔除。
- 修後 loose-key 審計 **0 漏合併**;difflib 模糊掃描僅 1 對(網球王子 vs 新網球王子,本就是不同作品)。Water for Elephants 併成 1 組 12 城、Mrs Doubtfire 併成 1 組。

## [v0.38.2] - 2026-06-14 17:52
### 變更
- u.html / me.html 內容欄加寬 1200→**1600px**(header `.top-inner` 同步),寬螢幕左右空白大幅縮小、填滿更多;header 仍與內容對齊。1920px render 截圖驗證。

## [v0.38.1] - 2026-06-14 17:47
### 修正(header 與內容寬度不一致)
- u.html / me.html 的 header(#me-top)原本滿版(brand/nav 貼視窗邊),內容區(#me-main)卻是 1200px 置中 → 寬螢幕上 header 左右各比內容寬約 40px、對不齊。把 header 內容包進 `.top-inner`(max-width 1200 + 18px padding、置中),與下方內容同欄對齊。以 headless Chrome 本機 render 截圖驗證對齊無誤。

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
