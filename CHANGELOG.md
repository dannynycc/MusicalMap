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
