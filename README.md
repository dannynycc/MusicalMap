# MusicalMap

一張地圖，呈現**此刻全球正在上演的音樂劇** —— 常駐型（Broadway / West End）與巡演型（tour，顯示目前在哪座城市）。

頂部 header bar（品牌 + 醒目「⭐ 我的音樂劇足跡」入口）、淺色地圖鋪滿畫面、海報縮圖當 marker + cluster、hover 預覽卡、點擊跳 popup、側欄一劇一列（同劇自動合併、可展開看各地點）+ 搜尋 + **類型篩選**（依血統 tag：Broadway/West End（百老匯/西區）、德奧、法語、西語、葡語、中／台／日／韓、歐陸其他；點 pill 多選，勾「Broadway/West End」連在澳洲巡演的 Wicked 也一起出現）+ **時間軸**（**月份**滑桿＋月份選擇器同步，選哪個月就顯示「演出期間跨過該月」的劇；▶ 播放每月推進可看巡演在城市間移動；**可往回拖到過去月份看歷史檔期**，資料來自每日累積的歷史檔）。

> **日期語意**：完整檔期顯示「start – end」；長壽劇顯示「自 X 上演」（end 只是滾動售票線非閉幕日）；Ticketmaster 來源（`onsale_only`）為可購票窗，顯示「售票中至 X」。**官網做成「劇名標題」的超連結**（官網不分潤，不單獨給圖卡免得稀釋售票平台點擊）；「購票」圖卡區只放**售票平台**（多平台並列，圖卡寬度依數量自適應、單一來源也填滿不留白）。

線上版：https://dannynycc.github.io/MusicalMap/

**My Musicals（個人音樂劇足跡）**：登入(Google)後記錄看過的音樂劇(可編輯/刪除),自動生成 Top 劇目/國家/城市/劇院、年度/每月/每週**折線圖**與**海報圖卡個人地圖**(FlightRadar「My Flights」風格、全英文 UI)。新增表單自動帶入劇院/城市/幣別、**劇名中英雙搜**(輸入「西貢」或「Miss」皆命中 Miss Saigon · 西貢小姐)。後端 Supabase(Postgres+Auth,RLS),前端仍純靜態。設定見 `docs/SETUP_ACCOUNTS.md`。

---

## 架構：資料層與呈現層分離

```
scrapers/  ──產出──>  data/*.json  ──merge──>  data/shows.json  ──讀取──>  前端 (index.html)
```

- **呈現層**（`index.html` / `css` / `js`）只讀 `data/shows.json`（現在/未來）+ `data/archive/`（拖時間軸到過去時 lazy-load），不在乎資料怎麼來。換來源不用動地圖。
- **資料層**（`scrapers/`）每個來源各寫一支 scraper、各產一個 source 檔；`build_shows.py` 合併、套用人工修正、做同劇合併與海報繼承。re-scrape 單一來源不會蓋掉其他來源。
- **歷史層**（`scrapers/archive.py`）獨立於純函式 build 之外:每天把當前快照**累積**進不可變歷史檔（`archive = 舊 ∪ 今天`）。**事實（劇名/劇院/日期）閉幕後凍結永不改;tag/group 每次重算**（改分類規則,歷史顯示自動更新,日期不動）。自動累積與人工策展（`curated_history.json`）同 schema,用 `provenance` 區分。**這層有狀態,刻意與「可重跑的純 build」隔開**。

### 檔案

| 路徑 | 作用 |
|---|---|
| `index.html` | **根目錄語言路由頁**(依 localStorage/瀏覽器轉址到 `/zh-hant//zh-hans//en/`,附 x-default 連結;由 `build/gen_site.mjs` 產生) |
| `build/gen_variants.mjs` → `data/variants/shows.{en,zh-hans,zh-hant}.json` | **三語資料變體**(OpenCC 簡⇄繁 + `data/i18n_maps.json` 的 CN/TW/JP/KR 地名 + 平台英文名)。需 Node + `opencc-js` |
| `build/gen_site.mjs` → `/en//zh-hans//zh-hant/index.html` + `sitemap.xml` + `robots.txt` | **三語獨立網址 + 預渲染**(劇目清單 + JSON-LD 寫進靜態 HTML → Google 與不跑 JS 的 AI 爬蟲都讀得到)+ hreflang。每日 CI 重生成 |
| `js/app.js` | 地圖、海報 marker、側欄、搜尋/篩選、popup、同劇合併與多地點 overview;變體頁載 `data/variants/`,中文判斷用 `isZh()`(繁簡皆是);含 `overlapsMonth` 與 XSS 跳脫 |
| `me.html` / `css/me.css` / `js/me.js` | My Musicals 個人頁(FlightRadar 風)、表單/自動帶入/折線圖/海報地圖/編輯刪除 |
| `theatres.html` / `js/theatres.js` | 所有劇院地圖(全 catalog ~5,000 場館,綠色群聚圈 + 多語搜尋) |
| `u.html` / `js/u.js` | 公開唯讀 profile 分享頁(`?u=<handle>`,免登入,推廣用) |
| `scrapers/gen_catalog.py` → `data/venues_catalog.json` | 自動帶入字典(場館去重 / 中英劇名 / 幣別 / 海報) |
| `css/style.css` | 淺色 UI（白底＋teal 主色） |
| `data/shows.json` | **前端唯一讀的檔**，由 build 產生 |
| `data/broadway.json` | Broadway scraper 輸出（broadway-show-tickets.com） |
| `data/westend.json` | West End scraper 輸出（londontheatre.co.uk） |
| `data/tours.json` | 北美巡演彙總 scraper 輸出（broadway.org，28 劇 297 站） |
| `data/intl.json` | 國際製作 scraper 輸出（broadway.org/international，全球駐演） |
| `data/ticketmaster.json` | Ticketmaster Discovery API 輸出（全球補洞，需 API key） |
| `data/shiki.json` | 劇団四季輸出（shiki.jp JSON API，日本 9 劇場，精確檔期） |
| `data/takarazuka.json` | 宝塚歌劇団輸出（kageki.hankyu.co.jp，宝塚/東京兩館接力檔期） |
| `data/interpark.json` | 韓國 Interpark 輸出（world.nol.com 開放 API，真實開演日） |
| `data/opentix.json` | 台灣 OPENTIX 兩廳院售票輸出（search.opentix.life JSON API，戲劇-音樂劇，自帶座標+海報） |
| `data/utiki.json` | 台灣 utiki 售票引擎輸出（寬宏 KHAM 分類 80 + udn售票 搜尋音樂劇 + MNA 分類 77；同套 UTK 引擎，座標交 Google geocode） |
| `data/manual.json` | **人工策展**：自有售票系統的劇（上海大劇院、Live Nation FR、捷克 NDM…），隨發現隨補 |
| `data/works.json` | **正典作品主檔**（單一真相來源，158 筆）：每齣作品一筆，記 `tradition`（血統 tag）+ 跨語言 `aliases` + 選填 `poster`／`productions`（版本層，見 `docs/DESIGN_productions.md`）。build 時供①血統分類②跨語言去重③雙語顯示三用——任何別名（`Macskák`/`キャッツ`/`Cats`）都收斂到同一作品。`build_shows.py --discover` 會把「疑似未對照的進口劇」寫到 `data/_works_discover.json` 供審核 |
| `data/not_musical.json` | **非音樂劇排除清單**：來源平台把話劇/演唱會/致敬樂團/魔術秀/2.5次元舞台劇/餐飲體驗等標成 musical，title pattern（`NOT_MUSICAL_RE`）抓不到的逐筆列此（web 查證）。build 時依正規化標題剔除 |
| `data/overrides.json` | 人工座標/欄位修正（依 show id；修來源錯誤，build 時套用） |
| `data/booking_horizon.json` | 開放式長壽劇的**最後售票日**（依 show id；`booking_horizon.py` 用 Ticketmaster `sort=date,desc` 抓，build 時填入無 end_date 的劇，避免時間軸把它們一路顯示到數年後） |
| `data/venue_coords.json` | **場館級權威座標**（`venue\|city`→[lat,lng]，建築級 ≤~30m，由 Google 產生；build 時套用到該場館所有場次） |
| `data/venues.json` | venue→座標 geocode 快取（手動可編） |
| `scrapers/geocode_google.py` | **Google Places (New) 權威 geocode**（建築級 ≤30m，增量回填 venue_coords.json；金鑰走 .gitignore 不入庫） |
| `scrapers/audit_geo.py` | 離線國家邊界框健全檢查（抓標到別國/null-island） |
| `scrapers/{tw,jp,kr,cn}_venues.py` → `data/*_venues.json` | 台/日/韓/中**完整在地音樂劇場館清單**（雙語名+Google 座標；供 My Musicals autocomplete，無當前檔期不上世界地圖） |
| `scrapers/venue_names.py` → `data/venue_names.json` | 亞洲場館英文+原文雙名（Google `languageCode`） |
| `data/venues_catalog.json` 的 `search` 欄位 | 英文+原文+簡體+繁體+臺/台 折疊（OpenCC），中英任一寫法皆可搜 |
| `scrapers/geocode.py` | Nominatim geocoding + 永久快取 |
| `scrapers/broadway.py` | Broadway scraper（解析 `__NEXT_DATA__`，含 NYC 座標檢查） |
| `scrapers/westend.py` | West End scraper（解析 `__NEXT_DATA__` + geocode） |
| `scrapers/broadway_tours.py` | **全美巡演彙總** scraper（broadway.org/tours，一次抓所有巡演劇） |
| `scrapers/intl.py` | **國際製作** scraper（broadway.org/international，含著名劇院手動座標表） |
| `scrapers/shiki.py` | **劇団四季** scraper（api_stage_list；日文劇名→英文正名以便全球合併） |
| `scrapers/takarazuka.py` | **宝塚歌劇団** scraper（各製作頁公演期間，按位置切段解析） |
| `scrapers/interpark.py` | **韓國 Interpark** scraper（NOL 開放 API；韓國場館座標表） |
| `scrapers/audit_images.py` | 海報畫質稽核（實測像素，小於顯示尺寸即報告） |
| `scrapers/ticketmaster.py` | **Ticketmaster** Discovery API（18 國掃描，需 `TICKETMASTER_API_KEY`） |
| `scrapers/build_shows.py` | 合併所有 source、TM 補洞去重、套 overrides、同劇合併、海報繼承、**血統 tag 分類**（依 `works.json`）→ `shows.json`（純函式、可重跑） |
| `scrapers/archive.py` → `data/archive/<year>.json` | **歷史累積層**（每日 CI 在 build 後跑）：`archive = 舊 ∪ 今天 shows`。閉幕場次凍結（事實不可變）、tag/group 每次重算；按 start 年分檔 + `index.json`。前端拖時間軸到過去才 lazy-load 對應年檔 |
| `scrapers/bootstrap_archive.py` | 一次性：挖 **git 歷史**裡每天 commit 的舊 `shows.json`，回溯灌入 archive（git 本身就是不可變每日快照）。`python scrapers/bootstrap_archive.py` |
| `data/curated_history.json` | **人工策展深歷史**：archive 開始前就閉幕的重要檔期（Hamilton 2015-、Phantom NY 1988-2023…），售票 API 抓不到過去,改由 Wikipedia/Wikidata 查證。只記事實,tag 自動套 |

---

## 資料模型（每筆 show / tour stop）

```json
{
  "id": "westend-wicked-tickets",
  "title": "Wicked",
  "type": "resident",          // "resident" 常駐 | "tour" 巡演
  "venue": "Apollo Victoria Theatre",
  "city": "London", "country": "UK",
  "lat": 51.4956, "lng": -0.1426,
  "start_date": "2006-09-27",  // ISO 日期或 null
  "end_date": null,            // null = 無限期/常駐中
  "ticket_url": "https://…",
  "image": "https://…",        // 海報；巡演沿用該劇海報
  "tour_name": null,           // 巡演才有，例 "Wicked — North American Tour"
  "group": "wicked",           // build 產生的正規化合併鍵（同劇同 key）
  "verified": true,
  "source": "londontheatre.co.uk"
}
```

- 巡演的每一「站」是一筆獨立紀錄，用 `[start_date, end_date]` 表示在該城市的檔期。
  **「目前在哪座城市」** = 今天落在哪一站的日期區間（見 `app.js` 的 `isPlayingNow`）。
- `group` 由 `build_shows.py` 的標題正規化產生，讓不同來源命名（`SIX` / `SIX: The Musical`）歸為同一齣。

---

## 怎麼跑

```bash
# 1) 起本機 server（前端用 fetch 讀 JSON，必須走 http，不能直接開檔）
cd D:/ClaudeCode/MusicalMap
python -m http.server 8753            # 瀏覽器開 http://localhost:8753/

# 2) 重新抓資料
python scrapers/westend.py            # West End（首次 geocode ~50s，之後走快取）
python scrapers/broadway.py           # Broadway（進 28 個細節頁拿 venue+座標）
python scrapers/broadway_tours.py     # 全美巡演（broadway.org，28 劇 297 站）
python scrapers/intl.py               # 國際製作（broadway.org/international）
python scrapers/shiki.py              # 劇団四季（日本）
python scrapers/takarazuka.py         # 宝塚歌劇団（日本）
python scrapers/interpark.py          # 韓國 Interpark（world.nol.com API）
python scrapers/atg.py                # ATG 英國地方圈
python scrapers/stage_de.py           # Stage Entertainment 德國
TICKETMASTER_API_KEY=xxx python scrapers/ticketmaster.py  # 全球補洞（需免費 key）
python scrapers/build_shows.py        # 合併成 data/shows.json
```

提交流程（CHANGELOG / 版號 / tag）見 **`docs/WORKFLOW.md`**；自動更新與部署見 `.github/workflows/update.yml`（**一日兩次**：台北 06:00 & 18:00）。

---

## 現況 / 待辦

- ✅ **共 ~1,600 筆、約 31 國**（隨每日 CI 變動），含座標與海報。自動 scraper：Broadway、West End、北美巡演（broadway.org 297 站）、國際製作、劇団四季、宝塚、東宝/2.5次元/東急（`japan.py`）、韓國 Interpark、ATG 英國巡演、Stage DE、Madrid、台灣 OPENTIX/utiki、東歐（jegy.hu）、義/瑞/荷/波/挪/奧/中東、**中國**（Poly/上海文廣/ypiao/中演/聚橙 juooo，逆向官方 API；**大麥 247 場次/52 城，人工協助批次解 x5sec、非 CI**）、Portugal（BOL）、Ticketmaster 全球補洞。
- ✅ **人工策展（`manual.json`，反爬市場）**：巴西（6）、阿根廷（2）、南非（4）、新加坡（4，到 2027）、葡萄牙、上海、各劇巡演段（Les Mis Arena/Miss Saigon/Beetlejuice/Chicago/SIX/Heathers/Roméo et Juliette…）。反爬來源（Sympla/Plateanet/MBS Akamai/SISTIC 需授權）無法自動抓，逐齣查證後手填。
- 🆕 **`scrapers/audit_manual.py`**（CI 每次跑）：抓 manual.json 中已落幕（end_date 過期）或逾期未查證（_checked >120 天）的手填劇，避免硬填資料默默過期。
- 🆕 **反爬 CDN 海報** rehost 到 `posters/`（同源，避開防盜連 403；如 Diana 的 Sympla 圖）。
- 🔄 自動更新：**一日兩次**（台北 06:00 & 18:00），見 `.github/workflows/update.yml`。
- 📒 **來源登記表：`docs/SOURCES.md`**（用戶提供的網址一律登記在此，含狀態）。
- ✅ **Production／版本層（v0.57.0，見 `docs/DESIGN_productions.md`）**：足跡記錄可選「版本／製作」（如歌劇魅影：倫敦/北美/日本四季…各國 live 版本 + 台灣巡演/25 週年 RAH 等 archival 版本），各帶正確海報；未收錄的版本可貼「自訂海報網址」。沒在演的劇（如 Love Never Dies／愛無止盡）也進自動完成並有縮圖。海報解析序 `自訂→版本→作品→♪`。`gen_catalog.py` 自動依國家分群產生 live 版本；`scrapers/audit_productions.py`（CI）守海報。
- ✅ 座標修正機制：NYC 範圍檢查、lat/lng 對調偵測、城市中心點 fallback、著名劇院手動座標表、`overrides.json`、geocode 快取。
- ✅ 同劇合併（標題正規化）、正式劇名覆蓋、巡演各自海報、cluster 依數量 √n 縮放、地圖／衛星切換、多地點 overview、popup 完整海報、多地區售票連結(「**購票**」標頭下各平台以**方形 logo tile**並排、含右箭頭;logo 用 favicon 自動取得,中國站如大麥/聚橙放官方 logo)。
- ✅ **多平台分潤框架（`MM_CONFIG.AFFILIATE` + `affiliateUrl()`，見 `docs/DESIGN_affiliate.md`）**：render 時把外連售票 URL 依 host 包成分潤連結（資料層只存乾淨 URL，換 ID = 改 config 一行）。支援 Impact／Partnerize／Awin／tmpl(Sovrn 等)多網絡;每個程式 dormant，填碼即生效。**直接計畫**:**Ticketmaster**（Impact,~600 齣,較高佣金,獨立於 Sovrn)。**Sovrn Commerce / VigLink catch-all**(一把 key 變現所有 in-network 售票站):涵蓋 **TodayTix(101)+ londontheatre(45)+ broadway-show-tickets(27)+ ATG(219)** ≈ 390 條外連,1-2% CPA+CPC。⚠️ **Sovrn 端需人工審網站(~3-5 天,Settings→Pending)後才開始計佣**。ATG/Broadway Direct 之後可升級為**直接計畫**(Partnerize/Awin,較高)取代 Sovrn。各平台 2026-06-23 逐一查證,詳見 `docs/DESIGN_affiliate.md`;TodayTix 改導用 `scrapers/todaytix.py`。
- 🟡 West End 少數冷門場館 geocode 為近似位置（可編 `data/venues.json` 校正）。
