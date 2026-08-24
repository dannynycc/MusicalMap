# MusicalMap

一張地圖，呈現**此刻全球正在上演的音樂劇** —— 常駐型（Broadway / West End）與巡演型（顯示目前巡到哪座城市）。

**線上版：https://themusicalmap.com/**

---

## 這個站有什麼

**世界地圖**：暖米白底圖鋪滿畫面，海報縮圖當 marker、相鄰的自動聚成群，hover 出預覽卡、點擊開詳情。

**側欄劇目列表**：一劇一列，同一齣在不同城市的場次自動合併，可展開看各地點。依血統分類排序。

**篩選列**：依作品血統分類（百老匯／西區、德奧、法語、西語、葡語、中／台／日／韓、歐陸其他），可多選。

**時間軸**：月份滑桿 + 月份選擇器。選哪個月就顯示「檔期跨過該月」的劇；按播放可看巡演在城市間移動。**可往回拖到過去月份**看歷史檔期，資料來自每日累積的歷史檔。

**三語**：繁體中文／简体中文／English，各有獨立網址（`/zh-hant/`、`/zh-hans/`、`/en/`）與預渲染 HTML。

### 日期怎麼顯示

| 情況 | 顯示 |
|---|---|
| 有結束日 | 至 M/D |
| 開放式長演 | 長期上演 |
| 本月才首演 | M/D 起 |
| 缺日期 | 留白 |

「長期上演」**只給開放式 sit-down 劇院**（百老匯／西區／Stage Entertainment 漢堡·斯圖加特），由 `build_shows.py` 標 `end_rolling`。其餘地區（日／韓／巡演／2.5 次元短檔）一律顯示真實的「至 X」。

作品官網做成**劇名標題的超連結**；「購票」區只放售票平台的方形 logo tile。官網不分潤，所以不單獨給圖卡，免得稀釋售票平台的點擊。

---

## My Musicals — 個人音樂劇足跡

登入後記錄自己看過的音樂劇。

**登入方式**：Google，或 Email 驗證碼（6 位數，給收不到 Google 的環境如中國網路）。同一個 email 兩種登入會自動合併成同一帳號。

**三種檢視**：海報牆／護照／清單，加上統計儀表板（場次數、最常看的劇／國家／城市／劇院榜、各年月週的觀劇分布）與點陣世界地圖。

**輸入**：搜尋劇名自動帶入劇院、城市、幣別（劇庫含近 5,500 座劇院的中英文名、歷史舊名、同名多城市消歧）。可填日期時間、評分、座位、票價、心得，每筆可自訂海報網址。

**可預先輸入未來場次** —— 海報牆標「即將上演」並加面紗，但**不計入任何「看過」的呈現**:統計數字、城市榜、護照蓋章、足跡地圖都只算已到場的場次。

**戰力圖與徽章**：六邊形戰力圖（劇院常客／嘗鮮作品／劇種涉獵／跨國足跡／狂粉劇迷／音樂劇齡），六軸皆為對數前載計分；17 族成就徽章，銀銅金三級。規則見 `docs/PERSONA_RULES.md`。

**公開分享頁**：每個帳號可設一個唯一 handle，產生公開頁 `my.themusicalmap.com/<handle>`。唯讀，資料走資料庫層的 `public_sightings()` 遮罩函式——**票價／座位由使用者決定是否公開（預設關），筆記永遠不出現在公開頁**。改名後舊網址自動轉到新網址。

後端 Supabase（Postgres + Auth + RLS），前端仍是純靜態。設定見 `docs/SETUP_ACCOUNTS.md`。

---

## 架構：資料層與呈現層分離

```
scrapers/  ──產出──>  data/*.json  ──merge──>  data/shows.json  ──讀取──>  前端
```

**呈現層**（`index.html` / `css` / `js`）只讀 `data/shows.json`（現在與未來）與 `data/archive/`（拖到過去月份時才 lazy-load），不管資料怎麼來。換來源不用動地圖。

**資料層**（`scrapers/`）每個來源各一支 scraper、各產一個 source 檔；`build_shows.py` 負責合併、套人工修正、同劇合併、海報繼承。重抓單一來源不會蓋掉其他來源。**這一層是純函式、可重複執行。**

**歷史層**（`scrapers/archive.py`）刻意獨立在純函式 build 之外，因為它**有狀態**：每天把當前快照累積進不可變的歷史檔（`archive = 舊 ∪ 今天`）。閉幕場次的事實（劇名／劇院／日期）永久凍結，但 tag 與 group 每次重算——所以改分類規則時，歷史顯示會自動跟著更新，日期不動。

---

## 資料模型

每一筆是一個「演出檔期」。巡演的每一站都是獨立一筆。

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
  "tour_name": null,           // 在地製作名，彈窗大標用；列表用乾淨的 title
  "group": "wicked",           // 正規化合併鍵，同劇同 key
  "verified": true,
  "source": "londontheatre.co.uk"
}
```

- 「**目前巡到哪座城市**」＝今天落在哪一站的日期區間（見 `js/app.js` 的 `isPlayingNow`）。
- `group` 由標題正規化產生，讓不同來源的命名（`SIX` / `SIX: The Musical`）歸為同一齣。

---

## 資料來源

**自動抓取（34 支 scraper，每日兩次 CI）**

| 地區 | 來源 |
|---|---|
| 英美 | Broadway、West End、北美巡演（broadway.org）、國際製作、ATG 英國巡演 |
| 日本 | 劇団四季、宝塚歌劇団、東宝／2.5 次元／東急 |
| 韓國 | Interpark（NOL 開放 API） |
| 中國 | 保利、上海文廣、ypiao、中演、聚橙 |
| 台灣 | OPENTIX 兩廳院、utiki（寬宏／udn／MNA／tixFun） |
| 歐洲 | Stage DE、Madrid、Barcelona、義／瑞典／荷／波蘭／挪威／奧地利／葡萄牙／東歐 |
| 其他 | 中東、菲律賓、Ticketmaster（全球補洞，18 國） |

**半自動**：大麥（damai.cn）需人工協助批次解反機器人驗證，不在 CI，約每月跑一次。

**人工策展**（`data/manual.json`）：反爬市場（巴西、阿根廷、南非、新加坡…）與自有售票系統的劇，逐齣查證後手填。

來源登記表在 **`docs/SOURCES.md`**，用戶提供的網址一律登記在此。

---

## 檔案結構

### 前端

| 路徑 | 作用 |
|---|---|
| `index.html` | 根目錄語言路由頁（依瀏覽器語言轉址到三語變體） |
| `js/app.js` | 地圖、marker、側欄、搜尋篩選、popup、同劇合併 |
| `css/style.css` | 暖米白 ivory 主題 |
| `me.html` + `me-input.html` | My Musicals 主頁與輸入端（iframe） |
| `u.html` + `js/u-view.js` | 公開唯讀分享頁 |
| `settings.html` | 帳號設定（改名／隱私開關／刪除帳號） |
| `css/me-v2.css` | me.html 與 u.html **共用**的護照風樣式（避免兩頁分岔） |
| `js/mm-strings.js` | me／u／settings 的三語字典 |
| `js/i18n.js` | 主地圖的三語字典 |
| `worker/` | Cloudflare Worker：`my.themusicalmap.com/<handle>` 乾淨網址、舊名 301、爬蟲 meta 注入 |

### 建置

| 路徑 | 作用 |
|---|---|
| `build/gen_variants.mjs` | 產三語資料變體（OpenCC 簡繁 + 地名／劇名字典） |
| `build/gen_site.mjs` | 產三語獨立網址 + 預渲染 HTML + JSON-LD + sitemap／robots |
| `build/gen_pages.mjs` + `build/pages/` | 內容頁（about／guide／privacy／terms）三語變體與 404 頁 |

> ⚠️ 改 about／guide／privacy／terms 要改 **`build/pages/`** 的 source，再跑 `node build/gen_site.mjs`。根目錄的同名檔是產物，會被 CI 覆蓋。

### 資料主檔

| 路徑 | 作用 |
|---|---|
| `data/shows.json` | **前端唯一讀的檔**，由 build 產生 |
| `data/works.json` | **正典作品主檔**（207 筆，單一真相來源）：每齣作品的血統 tag、跨語言別名、選填海報與版本層。任何別名（`Macskák`／`キャッツ`／`Cats`）都收斂到同一作品 |
| `data/official_sites.json` | 作品官網（224 部劇／478 條網址），依場次國家挑對應地區的官網 |
| `data/venues_catalog.json` | 自動帶入字典（5,486 場館去重、中英劇名、幣別、海報） |
| `data/venue_coords.json` | 場館級權威座標（建築級 ≤30m） |
| `data/archive/<year>.json` | 歷史累積層，按年分檔 + `index.json` |

### 人工修正檔

| 路徑 | 作用 |
|---|---|
| `data/manual.json` | 人工策展的演出（反爬市場、自有售票系統） |
| `data/overrides.json` | 依 show id 修正座標與欄位 |
| `data/not_musical.json` | 非音樂劇排除清單，支援 `titles`／`title_venue`／`title_prefix` |
| `data/works_distinct.json` | 同名異作拆分規則（Peter Pan vs Bennato 義大利原創…） |
| `data/local_titles.json` | 各地在地製作名 |
| `data/booking_horizon.json` | 開放式長壽劇的最後售票日，避免時間軸把它們顯示到數年後 |
| `data/curated_history.json` | 人工策展深歷史（archive 開始前就閉幕的重要檔期） |

---

## 怎麼跑

```bash
# 起本機 server（前端用 fetch 讀 JSON，必須走 http，不能直接開檔）
python -m http.server 8753            # 開 http://localhost:8753/

# 重新抓單一來源
python scrapers/westend.py
python scrapers/broadway.py
python scrapers/broadway_tours.py
python scrapers/shiki.py
TICKETMASTER_API_KEY=xxx python scrapers/ticketmaster.py

# 合併成 data/shows.json
python scrapers/build_shows.py

# 重建網站產物（改了 js/css 也要跑，版號是內容雜湊）
python scrapers/gen_catalog.py
node build/gen_variants.mjs
node build/gen_site.mjs
```

提交流程（CHANGELOG／版號／tag）見 **`docs/WORKFLOW.md`**。

---

## 自動更新與品質守門

GitHub Actions **每天兩次**（台北 06:00 & 18:00，`.github/workflows/update.yml`）跑全套 scraper、重建網站、提交資料並部署。

### 三層守門

| 層級 | 行為 | 用途 |
|---|---|---|
| **硬擋** | 失敗就**停在該步**，不建站、不提交，線上維持前一版 | 資料整批消失 |
| **`gate`** | 記入失敗清單，run 變紅，但照常部署 | 單一來源壞掉 |
| **`warn`** | 只提醒 | 已知積欠、實驗性來源 |

**為什麼需要硬擋**：`gate` 只會把 run 標紅，殘缺資料照樣提交部署。當某個來源被限流、整批抓失敗而 scraper 又把錯誤吞掉正常結束時，所有稽核都會通過——因為它們檢查的都是「留下來的資料對不對」，**沒有一項在看「有沒有整批消失」**。

- `scrapers/audit_counts.py`（硬擋）：總筆數比上一版跌超過 10% 就停。門檻取自歷史實測，日常波動在 -4.4% ~ +4.3%。
- `scrapers/_guard.py`（scraper 端）：抓到的資料比舊檔少超過 40% 就**不覆蓋舊檔**，並以非零退出碼讓 CI 變紅。**寧可不更新，也不要用殘缺資料蓋掉好資料**——舊檔留著，下游仍拿得到完整資料，下次抓正常就自己恢復。14 支 scraper 已採用。

### 稽核（CI 每次跑）

| 稽核 | 守什麼 |
|---|---|
| `audit_dates` | 日期結構：格式、閉幕早於開演、已閉幕仍在檔、無開演日、檔期逾 400 天未標長演 |
| `audit_geo` | 國界框 + 座標表自體檢（跨城市同座標的複製貼上指紋） |
| `audit_official` | 官網體檢；`--check-live` 另外連線驗每條官網是否還活著 |
| `audit_sentinels` | 12 個「不可能不在」的鐵桿劇 + 7 個來源最低筆數線 |
| `audit_manual` | 人工策展條目過期／久未查證 |
| `audit_dups` | 去重漏合併、同劇同城重複售票 URL、季票套餐群聚 |
| `audit_titles` / `audit_tournames` | 未歸組、分裂 group、presenter 名滲入 |
| `audit_sample_truth` | 每日隨機 15 卡直接對 Ticketmaster API 比場地／日期／標題／類型 |
| `audit_posters` / `audit_productions` | 海報健康與版本層海報 |
| `audit_catalog` | 全庫髒資料掃描（11 類，唯讀人工判讀） |

`audit_sentinels` 與資料量守門互補：**守門抓「突然壞」，哨兵抓「一直漏」**。

---

## 開發須知（踩過的坑）

**順序很重要**
- `build_shows.py` 的欄位衛生（HTML 實體解碼、座標清空、全大寫轉標題式）必須放在 **Ticketmaster 合併之後**，放前面等於整批 TM 資料繞過清理。
- 非音樂劇的關鍵字過濾必須比對**來源原始標題**。標題正規化會把「Movie Tour」這類證據從欄位裡刪掉，規則寫得再對也比不到。
- 加價套裝 listing（`… Ticket + Hotel Packages`）要在**去重之前**濾掉，否則它佔位、把正常 listing 擠掉，事後再刪會連整個場次一起弄丟。

**回饋迴圈**
- `tm_tours.py` 讀的是 `shows.json` **自己的輸出**，拿站上已有的 group 去搜同名 attraction。一筆混進來的髒資料（例如把演唱會當成劇名）下一輪就會長成一整輪巡演。所以非音樂劇命中且不是 `works.json` 註冊作品時要**整組刪**，切斷迴圈；已註冊作品只刪命中那一筆，免得「Les Misérables 電影放映」把真的悲慘世界殺掉。

**外部 API 配額**
- 不要為了讓某個修正提早生效而手動觸發完整重建，那會再吃一次所有外部 API 的當日配額。通常等下一次排程就好。

**座標**
- 中國大陸的 Google 座標是 **GCJ-02 偏移**，必須用 `scrapers/cn_venues.py` 的 `gcj02_to_wgs84` 轉換。
- 中文場館名共用「大／剧／院／中心」等字，**名稱重疊率不可作為判準**（會把常熟大剧院配到常州大剧院）。補座標要三個獨立來源互相印證。
- 城市標籤正規化按座標分群（80km）後群內統一，**不可單純按名字併**——Bloomington IN/IL、Duluth MN/GA、Rochester NY/MN 是不同城市。

**部署與網址**
- `_headers` 的具體路徑要寫**無副檔名**形式（`/me`，不是 `/me.html`）。Cloudflare Pages 會把 `/me.html` 用 308 導到 `/me`，而 `_headers` 比對的是該次回應的請求路徑——只寫 `.html` 版時，規則會生效在那個沒人停留的 308 上。兩種都列最保險。
- `404.html` 必須列進 workflow 的 `git add`。Pages 沒有它時，任何找不到的路徑都回 index.html + HTTP 200，那是 Google 判定的 soft 404。
- **Worker 不在 CI 部署範圍**，改完要手動 `cd worker && npx wrangler deploy`。
- my. 的 handle 一律 301 收斂到小寫，否則 `/danny` 與 `/DANNY` 各自 self-canonical ＝ 重複內容。

**海報**
- 海報繼承是**地區感知**的：同國優先 → 同字系圈，絕不跨圈，避免美國場次掛上日文海報。
- 反爬 CDN 的海報 rehost 到 `posters/`（同源，避開防盜連 403）。

---

## 現況

**約 2,070 筆演出、32 國、511 城**（隨每日 CI 變動）。最大三個市場：美國 797、英國 292、中國 244。

**待辦與已知限制**
- 英國巡演只吃 ATG + Ticketmaster 兩個來源，非這兩家的場館（Cardiff WMC、Leicester Curve…）會漏。
- `works.json` 註冊表仍有缺口（例如 The Music Man 這種經典未收錄），會影響 canonical 標題與血統分類。
- West End 少數冷門場館的 geocode 是近似位置，可編 `data/venues.json` 校正。
- 分潤框架已就位（`docs/DESIGN_affiliate.md`），Ticketmaster 走 Impact，其餘走 Sovrn catch-all。

---

## 文件索引

| 文件 | 內容 |
|---|---|
| `CHANGELOG.md` | 完整版本史與每次變動的來龍去脈 |
| `docs/WORKFLOW.md` | 提交流程（每次 commit 必照做） |
| `docs/SOURCES.md` | 資料來源登記表 |
| `docs/SETUP_ACCOUNTS.md` | Supabase 帳號系統設定 |
| `docs/SETUP_MY_SUBDOMAIN.md` | my. 子網域與 Worker 設定 |
| `docs/DESIGN_username_sharing.md` | handle／公開分享頁的設計依據 |
| `docs/DESIGN_productions.md` | 版本層（同一齣的各國製作）設計 |
| `docs/DESIGN_affiliate.md` | 分潤框架設計 |
| `docs/PERSONA_RULES.md` | 戰力圖六軸計分規則 |
| `docs/TOUR_SWEEP.md` | 巡演掃描機制 |
