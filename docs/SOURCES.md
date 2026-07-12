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
| ATG Tickets(英國地方圈) | atgtickets.com/whats-on/uk/musicals/ | `atg.py` | **無公開 API**;SSR 卡片+分頁。單場館含日期收錄;**tour hub 已爬(phase 2 完成):UK 巡演 ~39 條 ~220 站,隨每日 CI 變動**(站點 JSON 嵌在 hub RSC;2026-07-12 實測 221 站);無日期單館卡仍剔除 | 2026-06-12 |
| Stage Entertainment(德國) | stage-entertainment.de | `stage_de.py` | **無公開 API**;SSR,slug 自帶城市;劇場用「頁面提及次數 ≥2」判定(nav 會提到所有劇場);自有劇場座標表;漢堡/柏林/斯圖加特 13 部駐演(TINA、Tanz der Vampire、Frozen、獅子王、MJ…) | 2026-06-12 |
| OPENTIX 兩廳院售票(台灣) | search.opentix.life/search(JSON API) | `opentix.py` | 台灣當期音樂劇(category 戲劇-音樂劇);自帶 WGS-84 座標+海報+檔期;排除合唱/演唱會/工作坊 | 2026-06-12 |
| utiki 售票引擎(台灣:寬宏 KHAM + udn售票 + MNA) | kham.com.tw(分類 80) / tickets.udnfunlife.com(搜尋 音樂劇) / ticket.mna.com.tw(分類 77 音樂,需 cookie);同一套 UTK ASP.NET 引擎 | `utiki.py` | KHAM 走 listing→場次頁 eventTABLE(`PLACE_NAME`+地址);UDN listing 卡片帶日期+場館(多場館巡演)+銷售狀態;MNA 卡片帶日期、場館取自詳情頁場次表(分類混雜故只留標題含「音樂劇」)。排除合唱/演唱會/工作坊/交響音樂會、已結束;座標交 Google geocode。萬世巨星/史瑞克/魔女宅急便 | 2026-06-13 |

| 日本(東宝+2.5次元+東急シアターオーブ) | toho.co.jp/stage/lineup / j25musical.jp(日本2.5次元ミュージカル協会) / theatre-orb.com | `japan.py`(scrape_toho/scrape_j25/scrape_orb;與 shiki/takarazuka 並存) | **東宝**:card-lineup 取『』劇名+日期+場館,只留ミュージカル前綴。**2.5次元**:逐檔解析「【城市公演】日期 場館」多城巡演。**東急シアターオーブ**(音樂劇專用館):lineup 各檔 detail 取 og:title+「公演日程」。日文大 IP 中英並列+去重(シカゴ→Chicago…);TM 誤分類非音樂劇全域過濾(movie tour 等);Google 建築級座標。北海道下半年稀少=結構性(四季撤札幌/hitaru 非音樂劇)。**WIP:梅田芸術劇場(類型混雜待解)** | 2026-06-14 |
| 西班牙(馬德里) | teatromadrid.com | `madrid.py` | 馬德里音樂劇(西語 tag);**無分潤**,保留作涵蓋 | 2026-06-13 |
| 西班牙(巴塞隆納) | teatrebarcelona.com | `barcelona.py` | 巴塞隆納音樂劇(WordPress,同 madrid 平台) | 2026-06-25 |
| **西班牙全境(主力)** | atrapalo.com/entradas/musicales | `atrapalo.py` | 全西班牙 39 城~138 齣;Playwright 過 Fastly 挑戰→curl_cffi 抓頁面 JSON-LD(劇名/場館/**經緯度**/檔期/價/海報);**Sovrn 分潤**(merchant 53900);重疊劇主源,EXTRA_PRODUCTS 補非-musicales 分類 | 2026-06-26 |
| 東歐(匈牙利等) | jegy.hu 等 | `easteurope.py` | 匈牙利/捷克等地方場館,EE 區 | 2026-06-13 |
| 義/瑞/荷/波/挪/奧/中東 | teatro.it / showtic(瑞典) / stage(荷蘭) / ebilet(波蘭) / 挪威 / VBW(奧地利) / platinumlist(中東) | `italy.py` `sweden.py` `netherlands.py` `poland.py` `norway.py` `austria.py` `middleeast.py` | 各國原創/巡演;德奧(VBW)→德奧 tag,其餘多→歐陸其他 | 2026-06-13 |
| **中國**(逆向官方 API) | 上海文廣 shcstheatre.com(`/webapi.ashx`) / 保利 weixin.polyt.cn(`/platform-backend`,header `Channel: theatre_wx`) / ypiao / 中演院線 zhongyan / **聚橙 juooo** | `china.py` `china_poly.py` `china_ypiao.py` `china_chinaticket.py` `china_juooo.py` | 全國 ~100 齣/40+ 城;GCJ-02→WGS-84 座標轉換;保利真實日期取自 `/good/shows/{id}` showInfoDetailList[].showTime;售票連結→大麥搜尋。**2026-07-13 全數體檢**:5 支本地實跑全通(保利 88/文廣 5/ypiao 7/中演 1/聚橙 4),與 CI 一致——文廣/中演檔案多日未動是上游檔期真沒變,非 scraper 壞;中演音樂劇庫存本就少 | 2026-07-13 |
| **聚橙 juooo**(逆向官方 API,2026-06-23) | 城市清單 `api.juooo.com/city/city/getCityList`;節目 `gw.juooo.com/gw/show/showSearch`(POST form,body `cate_parent_id=79`(音樂劇)`+city_id+page`,**不需簽章**);座標 `gw/show/showDetail` → `result.show.venue.coordinate`(GCJ-02→WGS-84,自給自足不靠 cn_venues);售票 `m.juooo.com/ticket/{schedular_id}` | `china_juooo.py` | **逐城市遍歷全 253 城**(showSearch 分城市,故全掃任何城市有音樂劇都抓得到);目前僅 3 齣(全深圳安托山公共文化中心,聚橙自營庫存集中深圳,北京/上海在 juooo 上 0 場)。即便量少仍自動更新,庫存一變多即涵蓋 | 2026-06-23 |
| 葡萄牙 | bol.pt(JSON-LD Event) | `portugal.py` | Evita @ Lisboa;JSON-LD 自帶座標+城市 | 2026-06-15 |
| 全劇巡演自動掃 | Ticketmaster attraction 比對 | `tm_tours.py` | 對**全部** group 做 attraction 比對,新巡演站點自動入圖(每日 CI);**v2.29.4 起自帶 TM attraction 官方海報**(舊版寫死 None 依賴繼承→曾致美國站掛日文圖) | 2026-07-13 |

## 人工策展(manual.json)

| 來源 | 網址 | 內容 | 登記日 |
|---|---|---|---|
| 上海大劇院 | shgtheatre.com(內部 API `thvendor/ticket/program/getProgramById.xhtml`) | 魅影 40 週年上海告別季 9/29–11/29 | 2026-06-12 |
| Live Nation FR | livenation.fr/rom%C3%A9o-and-juliette-tickets-adp1652218 | Roméo et Juliette 2027-28 巴黎+7 站 | 2026-06-12 |
| NDM 捷克 | ndm.cz/en/operetta-musical/inscenation/6392-elisabeth/ | Elisabeth(Ostrava,repertory) | 2026-06-12 |
| **巴西**(Sympla/T4F/SESI) | sympla.com.br、ticketsforfun、sesisp.org.br(主流票務 Sympla=Cloudflare、Ingresso=SPA、場館站=Akamai 全反爬) | 6 齣:TINA、Wicked(里約)、Shrek、Diana(以上 Broadway/West End)+ Rita Lee、Minha Estrela Dalva(葡語原創)。逐齣 web 查證日期+售票+Nominatim geocode | 2026-06-15 |
| **阿根廷**(布宜諾斯艾利斯) | plateanet.com(403)、atrapalo.com.ar | 2 齣:Annie(Teatro Broadway)、Anastasia(Teatro Astral),Corrientes 大道劇場區,百老匯原作西語製作→Broadway/West End | 2026-06-15 |
| **南非**(Oliver!) | webtickets.co.za(Mamma Mia 由 Ticketmaster.co.za 自動抓,非 manual) | Oliver!(開普敦 Artscape + 約堡 Teatro Montecasino,2026-12→2027-03) | 2026-06-15 |
| **新加坡**(SISTIC/SRT/MBS) | sistic.com.sg、srt.com.sg、marinabaysands.com(MBS=Akamai HTTP2 擋;SISTIC 有官方 API「STIX」但 production 需 Bearer 授權,用戶無法取得→維持手填) | 4 齣到 2027:Legally Blonde(Esplanade)、Jesus Christ Superstar、Cats、Moulin Rouge!(以上 Sands Theatre) | 2026-06-15 |
| **葡萄牙** | bol.pt(JSON-LD,已有 `portugal.py` 自動抓) | Evita @ Capitólio Lisboa | 2026-06-15 |
| **德國波鴻**(Starlight Express) | starlight-express.info、售票 atgtickets.de(德國 ATG,未接自動來源) | 星光快車 1988– 專用劇場 Starlight Express Theater 常設(open-end),全球最長跑之一;OSM 實查座標;哨兵劇目之一 | 2026-07-09 |
| 各劇巡演段(雜) | 官網/票務 | Les Mis Arena(RAH/Radio City)、Miss Saigon(UK 巡演)、Beetlejuice(澳)、Chicago(東京/大阪/杜拜)、SIX(澳)、Heathers(坎培拉)、Les Mis Arena 等 | 2026-06-15 |

> **海報**:反爬 CDN(Sympla 等)的海報 hotlink 會 403/破圖 → 下載 rehost 到 `posters/`(同源)。國際知名劇缺圖則借資料庫同劇現有海報(**僅限同國/同字系圈**,v2.29.3 起絕不跨圈借)。手填劇新鮮度由 `scrapers/audit_manual.py`(CI)守門。

## 已評估/部分涵蓋

| 來源 | 網址 | 狀態 |
|---|---|---|
| Wicked 官方巡演 | tour.wickedthemusical.com | 曾接 scraper,後被 broadway.org 彙總取代(資料一致且更全) |
| Les Misérables 官方 | lesmis.com | 倫敦(westend)、US tour(tours)已涵蓋;Japan/Spain 站見 intl/手動;World Tour 待來源 |
| **大麥 Damai**(✅ 已接,人工協助批次,2026-06-24) | damai.cn | 阿里系,**BaXia 風控**:web `search.htm`→x5sec 滑塊;mtop API 要 `x-sign`+`x-mini-wua`+`x-sgext`(安全 SDK 簽章,server/SDK 端),無人值守 CI 繞不過。**改走人工協助**:`china_damai.py launch`(真 Chrome 開遠端除錯埠)→人解滑塊→`probe`/`harvest`(用同 session 控速翻頁,pageSize 鎖 30、每頁 15~25s 隨機抖動、撞 x5sec 即停)。實測**慢速仍會頻繁 re-challenge,需真人全程顧著解(~15 次/全量)**。`harvest`→`china_damai_raw.json`(跨次累積,2026-07-12 重抓後 1,036 筆);`build`→濾真音樂劇(剔舞劇/芭蕾/歌劇/文旅秀/券包)→劇名+城市去重(優先取未完結場次,舊快照不遮蔽新檔期)→`china_damai.json`(**2026-07-12:296 場次/60 城**,v2.29.1 剔除拼盤後;首批 2026-06-24 為 247/52),含**精準 `detail.damai.cn/item.htm?id={projectid}` 連結**,取代舊搜尋頁。座標走 Google 國際 API(WGS-84,非 GCJ-02);上海星空间/十二楼等微劇場一度 geocode 困難,8 個已於後續全數定位補入 `venue_coords.json`(歷程見 `docs/DAMAI_未定位場館待查.md`)。**非 CI 自動,需手動跑** |
| **猫眼 Maoyan** | show.maoyan.com | 同大麥那套反爬(x5sec);大麥已用人工協助批次解,猫眼暫不另接(劇目高度重疊) |
| **聚橙 juooo**(✅ 已接,見上表) | juooo.com | 一度誤判「geo 鎖深圳」,實為打錯端點;showSearch 不需簽章、city_id 可遍歷全國,已接 `china_juooo.py` |

## 已知盲區(誠實列出)

| 盲區 | 現況 |
|---|---|
| **Ticketek(澳洲另一大票務)** | Hamilton 墨爾本等在 Ticketek 不在 TM;待評估接入 |
| QPAC qtix 等場館自售(澳) | Beetlejuice Brisbane 靠 manual 補;同類場館需逐一 |
| musicalsontour.co.uk(UK 聚合) | Cloudflare 連 headless 都擋,無法接;UK 已由 ATG hub 覆蓋 |
| ATG 無日期單館卡(約 10 筆,細節頁日期 JS-only) | 已剔除不誤顯;待接其 availability 端點 |
| 四季全国ツアー | API 無固定城市 |
| 台灣 | 已由 OPENTIX(兩廳院)+ utiki(寬宏/udn)覆蓋當期音樂劇;其他在地售票(年代 ticket.com.tw 等)待評估 |
| 南美 / 新加坡 | ✅ 已涵蓋(manual):巴西/阿根廷/新加坡。SISTIC 有官方 API 但需授權(用戶無法取得)→ 維持手填 |
| 曼谷(泰) | 多為泰國本土製作(Scenario 歷年引進國際巡演但 2026 無確認檔期);Solaire(馬尼拉)座標已備,待未來檔期 |
| 港 / 馬來 / 印尼 / 越南 | 未有來源(港/星巡演多走 SISTIC/Base Entertainment) |

## 巡演查證
逐劇查證進度與方法見 **`docs/TOUR_SWEEP.md`**(tm_tours.py 全劇自動掃 + 逐劇 web 查證總表)。

## 待辦 / 候選

- 全国ツアー(四季):API 無固定城市,需逐區排程頁才有場館 → 待評估
- Ticketmaster affiliate 分潤:需用戶申請聯盟帳號(Impact/Partnerize),通過後把追蹤碼包進售票連結
- 韓國(Interpark)、德語區 Stage Entertainment(musicals.de)等:用戶尚未指定,候選
