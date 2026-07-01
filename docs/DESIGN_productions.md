# 設計定案:Production(製作/版本)三層資料模型

> 狀態:**已定案 + 第一版已實作上線(v0.57.0, 2026-06-22)**。本檔是這個功能的單一事實來源。
>
> **⚠ 2026-06-30 更新(v0.79.0 My Musicals v2 改版)**：足跡頁已從 `js/me.js`(FlightRadar 風)改版為**自含的 `me.html` + `me-input.html`**(舊版備份於 `me_ori.html`)。本檔以下「足跡表單(`js/me.js`)」段描述的是**舊版**;新版 me-input 的海報預設由 catalog 解析(`venues_catalog.posters` by title group)、**不用** `production_key`。但 **v1.1.0 起 me.html 有用 `poster_override`**(每筆紀錄可自訂海報 URL 覆蓋系統圖，渲染序 `poster_override → catalog → 首字母`，見 `add_poster_override.sql`)——與本檔舊設計的「自訂海報欄」概念相同、但實作在新版 me.html/me-input 而非舊 me.js。「製作三層資料模型(works/productions/shows)」與 `gen_catalog.py` 仍有效(新 me-input 同樣吃 `venues_catalog` 的 productions/posters)。
>
> **實作後的重要修訂(比原設計更省工):**
> - **`app.js`(live 地圖)完全不用動** —— 它本來就用每場自己的 `show.image`,北美巡演 13 城共用一張是「因為同屬北美巡演版」,倫敦/日本四季/各國各顯各的。所以「按版本拆海報」在 live 地圖早已成立,問題 2 其實**只發生在足跡頁(me.js)**。
> - **live 版本由 `gen_catalog.py` 自動依國家分群產生**(海報取該群現役場次的圖),不必在 works.json 手寫 `match` 規則。works.json 只需登記 **archival 版本**(沒在演的)+ 作品層 `poster`。全部作品自動受惠,不只旗艦劇。
> - 已上線:Phantom 10 版本(2 archival 含台灣巡演/25 週年 + 8 國 live)、Love Never Dies(archival-only,愛無止盡)。
> 動機:使用者回報兩個現象 —— (1) Love Never Dies 等「現在沒在演」的劇查不到、沒縮圖;
> (2) 同一齣劇(歌劇魅影)所有版本共用同一張海報。兩者其實是**同一個架構限制**的兩種表現。

---

## 1. 問題根因

目前縮圖與自動完成清單,**完全從「正在演的場次」(`data/shows.json`)長出來**:

```
shows.json (只有現役/即將演的場次)
   └ gen_catalog.py 按 group(作品) 收斂
        ├ titles[]  : 每個 group 一筆 → 餵自動完成
        └ posters{} : 每個 group「一張」海報(取該 group 第一場有圖的,其餘丟棄)
```

兩個限制直接掉出來:

- **沒在演的劇不存在**:不在 shows.json → 不在 titles → 自動完成不跳、`posterFor()` 回 null(顯示 ♪)。
  足跡 App 的本質是記「過去看過的」,過去看的劇很可能現在沒演 —— 這個洞很大,不是 LND 個案。
- **一作品只記一張海報**:27 場魅影原始資料其實有 8 種不同海報,但收斂成同一 group 後只留第一張。

根因:資料模型只有兩層 —— **作品(work/group)** 與 **場次(run = venue+date)**。
中間缺了 **製作/版本(production)** 這一層。使用者要的「正確縮圖」本質上是 production 層級的。

---

## 2. 三層模型

```
作品 Work          ── The Phantom of the Opera(canonical,唯一)
  └ 製作 Production ── 原始西區版 / 25週年RAH演唱會 / 世界巡演 / 四季日本版 / 台灣2026
       └ 場次 Run   ── 某劇院 × 某檔期(= 今天 shows.json 的一筆)
```

**關鍵設計:production 分兩種來源 `origin`**

| origin | 意義 | 海報怎麼上 |
|---|---|---|
| `live` | 有現役場次 | `match` 規則自動把 shows.json 的場次掛上去;**live 地圖也跟著拆海報** |
| `archival` | 沒現役場次(已落幕 / 歷史錄影 / 整齣劇都沒演) | 沒 `match`,只存在於作品主檔,專供足跡「手動選版本」 |

> 這個二分法讓 **Love Never Dies(整齣劇沒演)= 一個只有 archival production 的作品**,
> 與 **魅影 25 週年(其中一個版本沒演)** 共用同一套機制,不必為 LND 寫特例。

---

## 3. 資料格式:`works.json` 升級為作品主檔

改版前 works.json 只收「非預設 tradition 或 有非英文別名」的作品(當時 157 筆),且**無 poster 欄**。(現已升級為作品主檔,170 筆,帶 `poster`/`productions`。)
升級後每個作品可帶 `poster` 與 `productions[]`:

```jsonc
{
  "canonical": "The Phantom of the Opera",
  "tradition": "Broadway/West End",
  "aliases": ["歌劇魅影", "オペラ座の怪人", ...],
  "poster": "posters/phantom_default.jpg",          // 作品層 fallback(必填,若有 production)
  "productions": [
    {
      "key": "ph-original-we",                       // 全域唯一,kebab-case
      "label": "Original (West End / His Majesty's)",
      "label_zh": "原始西區版",
      "poster": "posters/phantom_we.jpg",
      "origin": "live",
      "match": { "venue_kw": ["majesty"], "city": "London" }
    },
    {
      "key": "ph-shiki-jp", "label": "Gekidan Shiki (Japan)", "label_zh": "四季劇團",
      "poster": "posters/phantom_shiki.jpg",
      "origin": "live",
      "match": { "source": "shiki", "country": "Japan" }
    },
    {
      "key": "ph-25th-rah", "label": "25th Anniversary (Royal Albert Hall)", "label_zh": "25週年演唱會",
      "poster": "posters/phantom_25th.jpg", "origin": "archival"
    },
    {
      "key": "ph-taiwan-2026", "label": "Taiwan Tour 2026", "label_zh": "台灣巡演 2026",
      "poster": "posters/phantom_tw2026.jpg", "origin": "archival"
    }
  ]
}
```

**Love Never Dies 範例(archival-only 作品):**

```jsonc
{
  "canonical": "Love Never Dies",
  "tradition": "Broadway/West End",
  "aliases": ["<官方中文名待查證>"],
  "poster": "posters/love_never_dies.jpg",
  "productions": []          // 整齣劇都沒現役 → 沒 production 也可,直接吃作品層海報
}
```

### `match` 欄位語意(只 `origin:"live"` 需要)
依**優先序**比對(前者命中即停):`source` → `country` → `venue_kw`(子字串,全小寫)→ `tour_name` → `year`(start_date 年份)。
- 一場 show 跑完所有 live production 的 match,**第一個命中**就標 `production_key`。
- **全沒中 → 掛該作品的 default**(= 第一個 production,或作品層),**不亂猜**。

---

## 4. 場次 → 製作 的配對(後端)

`build_shows.py` / `gen_catalog.py` 在產資料時:
1. 對每場 show 跑 §3 的 match,寫入 `production_key`。
2. `venues_catalog.json` 的 `posters` 改成兩層輸出:
   - `posters[group]` = 作品層 fallback(維持現有 key,向後相容)。
   - 新增 `productions{ production_key: {label, label_zh, poster, work_group, origin} }`。
3. `titles[]` 改成**每個登錄作品都輸出一筆**(脫離 shows.json),這樣沒在演的劇也進自動完成。

### 稽核(防誤配 / 防規則腐爛)
新增 `scrapers/audit_productions.py`,掛進 CI(non-blocking),列出:
- 掛到 default 的現役場次(可能漏寫 match 規則)。
- `match` 規則打到 0 場的 `live` production(規則過時)。
- `poster` 檔案不存在 / 不是 image 的 production。

> 守紀律:配對是**規則式、可稽核**的,不靠模糊推論當「驗證過」。

---

## 5. 足跡表單(`js/me.js`)

選劇名後:
1. 該作品有 `productions[]` → 跳出**第二個下拉「你看的是哪個版本?」**(附縮圖),含 archival 版本;
   預設「不確定 / 通用」→ 回作品層海報。
2. **「自訂海報」欄**:我們沒收錄的版本,使用者貼 URL(救任何冷門版)。

存進 sighting 的新欄位:
- `production_key`(text, nullable)
- `poster_override`(text, nullable)

### 海報解析順序(render 時,所有頁面共用)
```
poster_override  →  productions[production_key].poster  →  work.poster  →  ♪ 佔位
```
> **存 key 不存死圖**:之後修正某版海報會自動傳播到所有使用者;但使用者的 `poster_override` 永遠優先,不被蓋掉。

---

## 6. 要動到的範圍總表

| 範圍 | 改動 |
|---|---|
| `data/works.json` | 加 `poster`、`productions[]`;補要做 production 的英文旗艦作品(Wicked/Hamilton…目前不在表內) |
| `scrapers/build_shows.py` | show → production 配對,寫 `production_key` |
| `scrapers/gen_catalog.py` | titles 改「每作品都輸出」;posters 改 work + production 兩層 |
| `scrapers/audit_productions.py` | **新增**,稽核配對與海報,掛 CI |
| Supabase `sightings` | 加 `production_key text`、`poster_override text`(沿用既有「缺欄位自動降級重試」邏輯,無痛上線) |
| `js/me.js` | 版本下拉 + 自訂海報欄 + 解析順序 |
| `js/app.js`(live 地圖) | marker 海報改吃 `production_key`,同城多版本各顯各的 |
| `js/u-view.js` / `u.html`(公開分享) | 同一套解析順序 |
| `posters/` | 收錄海報一律 rehost(見 §7) |
| migration | 一支腳本回填舊 sighting 的 `production_key`(配對失敗留空 = 通用,不亂塞) |

---

## 7. 海報來源與 rehost 紀律

- 收錄的海報**一律下載 rehost 進 `posters/`**,不 hotlink 外站(避免日後失效)。
- 收錄前必驗:HTTP GET 確認 `content-type: image/*`(非 .tif)、來源 / 檔名對得上**這齣這版**。
- archival 版本(25 週年、台灣巡演)海報尤其要查證是「這齣這版」,non-null ≠ 正確。
- 不確定的版本:**寧可先用作品層通用圖,標明信心度,絕不亂塞一張假的**。
- 跑 `scrapers/audit_images.py` 實測像素,模糊 / 失效 = 0 才過。

---

## 8. 實作順序(分階段,逐步驗)

1. **資料模型**:works.json schema + 補旗艦劇(魅影 / 悲慘世界 / 貓 + 使用者指定)的 productions,海報查證 rehost。
2. **後端**:build_shows / gen_catalog 配對 + `audit_productions.py` + CI。
3. **前端足跡**:me.js 版本下拉 + 自訂海報 + 解析順序;Supabase 加欄位。
4. **live 地圖 + 公開頁**:app.js / u-view.js 套用。
5. **migration + 收尾**:回填舊紀錄;archival-only 作品(LND 等)一次補齊。

> 各階段獨立 commit,功能性改動以 MINOR 進版;最終整套上線。

---

## 9. 輸入進度

- ✅ **Love Never Dies 中文名**:確認 **愛無止盡**(中文維基條目名),別名另收「真愛不死」。
- ✅ **LND 海報**:使用者提供 San Jose 巡演版官方主視覺 → `posters/love_never_dies.jpg`(已親眼驗證)。
- ✅ **Phantom archival 海報**:台灣巡演 `posters/phantom_tw2026.jpg`、25 週年 RAH `posters/phantom_25th.jpg`(皆使用者提供 + 親眼驗證)。
- 🔜 **旗艦劇 archival 版本**:Wicked / Miss Saigon / Les Mis / Lion King 的「已落幕特定版本」海報待陸續補(live 版本已自動帶)。

## 10. 海報查證紀律(已落實)

每張收錄海報:`curl -sIL` 驗 `content-type: image/*` → 下載 rehost 進 `posters/` → **用 Read 工具親眼看過確認是「這齣這版」** → `scrapers/audit_productions.py` 檢查檔案存在且為圖檔(掛 CI)。前端改動用 headless Chrome 截圖驗 render(本次已截 Phantom 版本下拉 + LND 縮圖)。

---

## 11. 「系統性抓過去版本」的決策紀錄(2026-06-23,明天接這裡)

**問題**:archival(沒在演的)版本海報,怎麼系統性涵蓋到全球用戶?

**已評估並否決的來源:**
- **Wikidata**:對音樂劇的「各製作」太弱,連 musical 本體都不好搜到 → ✗。
- **Theatricalia**(實測製作數:Les Mis 14、Phantom 10、Miss Saigon 3、Lion King 3、**Wicked 0**、**Roméo et Juliette 0**):嚴重偏 UK 業餘劇場、**整個資料庫沒有 Wicked**、非英語音樂劇全掛零、**沒有海報**、且資料授權是 **ODbL(share-alike + 需標註)** → 撐不起全球覆蓋,**否決匯入器**。

**目前已能 scale 的部分:**
- 正在演的版本 = `gen_catalog.py` 自動依國家分群(海報取現役場次圖)。✅ 全球自動。
- 任何冷門版本的「**個人**足跡」= 每個用戶可自填 `poster_override`。✅ 不經人工,已 scale。

**未解 / 明天要繼續研究的:**
- 「**共享**層」的 scale:用戶 B 不必重貼用戶 A 已貼過的海報。
- 唯一能 scale 的方向 = **自助 UGC 貢獻迴路**:用戶貢獻版本+海報 → Supabase 待審表 → 核准後 me.js runtime 載入併進版本下拉(靜態 catalog 不重建)。卡點是**審核**(公開產品讓用戶貼任意圖 URL 有 spam/版權風險,需要「核准才公開」這一關)。
- **狀態:已暫緩(parked)**。使用者覺得卡住,決定先休息。現階段「使用者給海報→我驗證收錄」對單一主用戶已足夠;等真有用戶量再建 UGC 迴路。
- 明天從這節繼續討論 UGC 迴路要不要做、怎麼做審核。
