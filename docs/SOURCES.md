# 資料來源登記表 SOURCES

> **維護規則**:用戶提供的每一個來源網址都登記在此(含日期與處理狀態)。大部分音樂劇都在這些場館/平台上演;新增來源時先查此表避免重複,接好後更新狀態。每次 commit 檢查此表 freshness。

## 已接自動 scraper

| 來源 | 網址 | Scraper | 涵蓋 | 登記日 |
|---|---|---|---|---|
| Broadway 列表 | broadway-show-tickets.com/musicals/ | `broadway.py` | 紐約百老匯 28 部(含座標) | 2026-06-11 |
| West End 列表 | londontheatre.co.uk/whats-on/musicals?categories=Musicals | `westend.py` | 倫敦西區 52 部 | 2026-06-11 |
| 北美巡演彙總 | broadway.org/tours(含 /zh/tours) | `broadway_tours.py` | 28 劇 297 站,官方 The Broadway League | 2026-06-11 |
| 國際製作 | broadway.org/broadway-shows-international | `intl.py` | 巴黎/漢堡/科隆/墨西哥城/烏特勒支/馬德里(+東京,已被四季取代) | 2026-06-11 |
| Ticketmaster | developer.ticketmaster.com(Discovery API);入口例 ticketmaster.com.au/browse/musicals… | `ticketmaster.py` | 16 國 gap 補洞(澳/紐/愛/加/北歐/義/星…);**日期=可購票窗非開演日** | 2026-06-11 |
| 劇団四季 | shiki.jp(中文版 shiki.jp/zh-tw/) | `shiki.py`(JSON API `api_stage_list`) | 日本 9 劇場 10 製作,精確檔期;全国ツアー無固定城市未收 | 2026-06-12 |
| 宝塚歌劇団 | kageki.hankyu.co.jp(中文版 /tc/revue/) | `takarazuka.py`(解析各製作頁公演期間) | 6 製作 12 檔(宝塚大劇場→東京宝塚劇場接力),含寶塚版 Elisabeth | 2026-06-12 |
| 韓國 Interpark | world.nol.com/zh-CN/ticket/genre/MUSICAL/products(開放 API `/api/ent-channel-out/v1/goods/list`) | `interpark.py` | 59 部、39 含座標(首爾 32/大邱 6/大田 1);**真實開演日**;海報用 `posterImageUrl`(large 路徑會 404);API size 參數被偷偷 cap 在 ~15、totalPages 不可信 | 2026-06-12 |
| ATG Tickets(英國地方圈) | atgtickets.com/whats-on/uk/musicals/ | `atg.py` | **無公開 API**;SSR 卡片+分頁。單場館含日期收錄;**tour hub 已爬(phase 2 完成):33 條 UK 巡演 205 站**(站點 JSON 嵌在 hub RSC);無日期單館卡仍剔除 | 2026-06-12 |
| Stage Entertainment(德國) | stage-entertainment.de | `stage_de.py` | **無公開 API**;SSR,slug 自帶城市;劇場用「頁面提及次數 ≥2」判定(nav 會提到所有劇場);自有劇場座標表;漢堡/柏林/斯圖加特 13 部駐演(TINA、Tanz der Vampire、Frozen、獅子王、MJ…) | 2026-06-12 |
| OPENTIX 兩廳院售票(台灣) | search.opentix.life/search(JSON API) | `opentix.py` | 台灣當期音樂劇(category 戲劇-音樂劇);自帶 WGS-84 座標+海報+檔期;排除合唱/演唱會/工作坊 | 2026-06-12 |
| utiki 售票引擎(台灣:寬宏 KHAM + udn售票) | kham.com.tw(分類 80) / tickets.udnfunlife.com(搜尋 音樂劇);同一套 UTK ASP.NET 引擎 | `utiki.py` | KHAM 走 listing→場次頁 eventTABLE(`PLACE_NAME`+地址);UDN listing 卡片直接帶日期+場館(多場館巡演)+銷售狀態。排除合唱/演唱會/工作坊/交響音樂會、已結束;座標交 Google geocode。萬世巨星/史瑞克 | 2026-06-13 |

## 人工策展(manual.json)

| 來源 | 網址 | 內容 | 登記日 |
|---|---|---|---|
| 上海大劇院 | shgtheatre.com(內部 API `thvendor/ticket/program/getProgramById.xhtml`) | 魅影 40 週年上海告別季 9/29–11/29 | 2026-06-12 |
| Live Nation FR | livenation.fr/rom%C3%A9o-and-juliette-tickets-adp1652218 | Roméo et Juliette 2027-28 巴黎+7 站 | 2026-06-12 |
| NDM 捷克 | ndm.cz/en/operetta-musical/inscenation/6392-elisabeth/ | Elisabeth(Ostrava,repertory) | 2026-06-12 |

## 已評估/部分涵蓋

| 來源 | 網址 | 狀態 |
|---|---|---|
| Wicked 官方巡演 | tour.wickedthemusical.com | 曾接 scraper,後被 broadway.org 彙總取代(資料一致且更全) |
| Les Misérables 官方 | lesmis.com | 倫敦(westend)、US tour(tours)已涵蓋;Japan/Spain 站見 intl/手動;World Tour 待來源 |

## 已知盲區(誠實列出)

| 盲區 | 現況 |
|---|---|
| **Ticketek(澳洲另一大票務)** | Hamilton 墨爾本等在 Ticketek 不在 TM;待評估接入 |
| QPAC qtix 等場館自售(澳) | Beetlejuice Brisbane 靠 manual 補;同類場館需逐一 |
| musicalsontour.co.uk(UK 聚合) | Cloudflare 連 headless 都擋,無法接;UK 已由 ATG hub 覆蓋 |
| ATG 無日期單館卡(約 10 筆,細節頁日期 JS-only) | 已剔除不誤顯;待接其 availability 端點 |
| 四季全国ツアー | API 無固定城市 |
| 台灣 | 已由 OPENTIX(兩廳院)+ utiki(寬宏/udn)覆蓋當期音樂劇;其他在地售票(年代 ticket.com.tw 等)待評估 |
| 韓國以外亞洲(港/星巡演)、南美、Stage NL/ES | 未有來源 |

## 巡演查證
逐劇查證進度與方法見 **`docs/TOUR_SWEEP.md`**(tm_tours.py 全劇自動掃 + 逐劇 web 查證總表)。

## 待辦 / 候選

- 全国ツアー(四季):API 無固定城市,需逐區排程頁才有場館 → 待評估
- Ticketmaster affiliate 分潤:需用戶申請聯盟帳號(Impact/Partnerize),通過後把追蹤碼包進售票連結
- 韓國(Interpark)、德語區 Stage Entertainment(musicals.de)等:用戶尚未指定,候選
