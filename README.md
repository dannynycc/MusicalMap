# MusicalMap

一張地圖，呈現**此刻全球正在上演的音樂劇** —— 常駐型（Broadway / West End）與巡演型（tour，顯示目前在哪座城市）。

視覺參考 [stayplot.com](https://www.stayplot.com/)：深色地圖鋪滿畫面、marker + cluster、點擊跳 popup、側欄同步列表 + 搜尋 + 篩選。

---

## 架構：資料層與呈現層分離

```
scrapers/  ──產出──>  data/*.json  ──merge──>  data/shows.json  ──讀取──>  前端 (index.html)
```

- **呈現層**（`index.html` / `css` / `js`）只讀 `data/shows.json`，不在乎資料怎麼來。換來源不用動地圖。
- **資料層**（`scrapers/`）每個來源各寫一支 scraper、各產一個 source 檔；`build_shows.py` 合併。re-scrape 單一來源不會蓋掉其他來源。

### 檔案

| 路徑 | 作用 |
|---|---|
| `index.html` | 頁面骨架，CDN 載入 Leaflet + MarkerCluster |
| `js/app.js` | 地圖、marker、側欄、搜尋/篩選、popup；含「此刻是否上演」判斷與 XSS 跳脫 |
| `css/style.css` | 深色 UI |
| `data/shows.json` | **前端唯一讀的檔**，由 build 產生 |
| `data/westend.json` | West End scraper 輸出（真實，verified:true） |
| `data/broadway.json` | Broadway seed（手填，verified:false，待 scraper） |
| `data/tours.json` | 巡演 seed-sample（**示範結構，勿信**） |
| `data/venues.json` | venue→座標 geocode 快取（手動可編） |
| `scrapers/geocode.py` | Nominatim geocoding + 永久快取 |
| `scrapers/westend.py` | londontheatre.co.uk scraper（解析 `__NEXT_DATA__`） |
| `scrapers/build_shows.py` | 合併所有 source → `shows.json` |

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
  "tour_name": null,           // 巡演才有，例 "Phantom — US Tour"
  "verified": true,            // false = 手填示範，UI 顯示「未驗證」標
  "source": "londontheatre.co.uk"
}
```

巡演的每一「站」是一筆獨立紀錄，用 `[start_date, end_date]` 表示在該城市的檔期。
**「目前在哪座城市」** = 今天落在哪一站的日期區間（見 `app.js` 的 `isPlayingNow`）。

---

## 怎麼跑

```bash
# 1) 起本機 server（前端用 fetch 讀 JSON，必須走 http，不能直接開檔）
cd D:/ClaudeCode/MusicalMap
python -m http.server 8753
# 瀏覽器開 http://localhost:8753/

# 2) 重新抓資料
python scrapers/westend.py        # 抓 West End（首次 geocode ~50s，之後走快取）
python scrapers/build_shows.py    # 合併成 data/shows.json
```

---

## 現況 / 待辦

- ✅ West End：52 部音樂劇，自動抓取 + geocode（43 間有座標）
- ⚠️ West End 9 間 venue geocode 失敗（名稱太模糊，如 "…Powered by TodayTix"）。
  修法：編 `data/venues.json` 對應 slug 手填正確 `lat`/`lng`。
- 🟡 Broadway：目前是 8 部手填 seed（`verified:false`）。
  待辦：寫 `scrapers/broadway.py` 抓 broadway-show-tickets.com（劇名在列表頁、venue/日期在細節頁）。
- 🟡 巡演：`data/tours.json` 只是示範結構，**勿當真實資料**。待辦：找巡演排程來源。
- 未驗證資料在 UI 會顯示黃色「未驗證」標，popup 也有警語。
