# MusicalMap

一張地圖，呈現**此刻全球正在上演的音樂劇** —— 常駐型（Broadway / West End）與巡演型（tour，顯示目前在哪座城市）。

頂部 header bar（品牌 + 醒目「⭐ 我的音樂劇足跡」入口）、淺色地圖鋪滿畫面、海報縮圖當 marker + cluster、hover 預覽卡、點擊跳 popup、側欄一劇一列（同劇自動合併、可展開看各地點）+ 搜尋 + **類型篩選**（依血統 tag：Broadway/West End、德奧、法式、西語、台／日／韓原創、歐陸原創；點 pill 多選，勾「Broadway/West End」連在澳洲巡演的 Wicked 也一起出現）+ **時間軸**（**月份**滑桿＋月份選擇器同步，選哪個月就顯示「演出期間跨過該月」的劇；▶ 播放每月推進可看巡演在城市間移動）。

> **日期語意**：完整檔期顯示「start – end」；長壽劇顯示「自 X 上演」（end 只是滾動售票線非閉幕日）；Ticketmaster 來源（`onsale_only`）為可購票窗，顯示「售票中至 X」。連結分「官網」與「售票平台」（多平台並列）。

線上版：https://dannynycc.github.io/MusicalMap/

**My Musicals（個人音樂劇足跡）**：登入(Google)後記錄看過的音樂劇(可編輯/刪除),自動生成 Top 劇目/國家/城市/劇院、年度/每月/每週**折線圖**與**海報圖卡個人地圖**(FlightRadar「My Flights」風格、全英文 UI)。新增表單自動帶入劇院/城市/幣別、**劇名中英雙搜**(輸入「西貢」或「Miss」皆命中 Miss Saigon · 西貢小姐)。後端 Supabase(Postgres+Auth,RLS),前端仍純靜態。設定見 `docs/SETUP_ACCOUNTS.md`。

---

## 架構：資料層與呈現層分離

```
scrapers/  ──產出──>  data/*.json  ──merge──>  data/shows.json  ──讀取──>  前端 (index.html)
```

- **呈現層**（`index.html` / `css` / `js`）只讀 `data/shows.json`，不在乎資料怎麼來。換來源不用動地圖。
- **資料層**（`scrapers/`）每個來源各寫一支 scraper、各產一個 source 檔；`build_shows.py` 合併、套用人工修正、做同劇合併與海報繼承。re-scrape 單一來源不會蓋掉其他來源。

### 檔案

| 路徑 | 作用 |
|---|---|
| `index.html` | 頁面骨架，CDN 載入 Leaflet + MarkerCluster |
| `js/app.js` | 地圖、海報 marker、側欄、搜尋/篩選、popup、同劇合併與多地點 overview；含「演出是否跨過所選月份」判斷(`overlapsMonth`)與 XSS 跳脫 |
| `me.html` / `css/me.css` / `js/me.js` | My Musicals 個人頁(FlightRadar 風)、表單/自動帶入/折線圖/海報地圖/編輯刪除 |
| `theatres.html` / `js/theatres.js` | 所有劇院地圖(全 catalog ~4,900 場館,綠色群聚圈 + 多語搜尋) |
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
| `data/works.json` | **正典作品註冊表**（單一真相來源，143 筆）：每齣作品一筆，記 `tradition`（血統 tag）+ 跨語言 `aliases`。build 時供①血統分類②跨語言去重③雙語顯示三用——任何別名（`Macskák`/`キャッツ`/`Cats`）都收斂到同一作品。`build_shows.py --discover` 會把「疑似未對照的進口劇」寫到 `data/_works_discover.json` 供審核 |
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
| `scrapers/build_shows.py` | 合併所有 source、TM 補洞去重、套 overrides、同劇合併、海報繼承、**血統 tag 分類**（依 `works.json`）→ `shows.json` |

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

提交流程（CHANGELOG / 版號 / tag）見 **`docs/WORKFLOW.md`**；自動每日更新與部署見 `.github/workflows/update.yml`。

---

## 現況 / 待辦

- ✅ Broadway（28）、West End（52）、北美巡演（broadway.org，297 站）、國際製作、劇団四季（10）、宝塚歌劇団（12）、韓國 Interpark（39）、ATG 英國地方圈（5）、Stage Entertainment 德國（13）、Ticketmaster 全球補洞、人工策展：共 604 筆，約 25 國，含座標與海報。
- 📒 **來源登記表：`docs/SOURCES.md`**（用戶提供的網址一律登記在此，含狀態）。
- ✅ 座標修正機制：NYC 範圍檢查、lat/lng 對調偵測、城市中心點 fallback、著名劇院手動座標表、`overrides.json`、geocode 快取。
- ✅ 同劇合併（標題正規化）、正式劇名覆蓋、巡演各自海報、cluster 線性縮放、地圖／衛星切換、多地點 overview、popup 完整海報、多地區售票連結。
- 🟡 Ticketmaster 分潤需另加入 affiliate 聯盟（需審核），通過後可把追蹤碼包進售票連結。
- 🟡 West End 少數冷門場館 geocode 為近似位置（可編 `data/venues.json` 校正）。
