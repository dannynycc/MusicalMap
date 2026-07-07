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

## [v2.8.6] - 2026-07-07 14:20
### 修正 — 複製網址在 clipboard API 不可用時靜默無回饋（PM 稽核循環 R9,第二批 backlog）

- **真 bug**:me.html hero 帳號列的複製鈕 `pfCopy` 與 settings.html 的 `shareCopy`,`navigator.clipboard.writeText` 失敗時是空 `catch(e){}`——非 HTTPS context、使用者拒絕剪貼簿權限、企業瀏覽器政策擋 clipboard 時,按複製完全無反應、無提示、無 fallback。舊版 shareCopy(v2.5 前)本有「選取文字讓使用者 Ctrl+C」的 fallback,v2.6 帳號中心改版時漏帶。
- 修:兩處 catch 補 fallback——選取網址文字（Range/Selection）+按鈕變「已選取，按 Ctrl+C / Selected — press Ctrl+C」（新 i18n key `copy_manual` 繁英）。
- e2e 補斷言:mock `clipboard.writeText` reject → 驗按鈕提示手動複製 + 網址文字已被選取（2 項 PASS）。三主題(midnight/gallery/cream)pill 對比度截圖人眼驗清晰（綠色語意 status 色三底皆可讀）。`?v=228`;主 e2e 57 項全 PASS。

## [v2.8.5] - 2026-07-07 14:01
### 修正 — 8 個手寫頁的 mm-acct-menu.js 漏 bump cache（PM 稽核循環 R5,死 code 掃描時抓到）

- **真 bug**:`js/mm-acct-menu.js` 在 v2.8.2 改過（頭像 img 絕對定位修正,防撐爆圓框）,但 me/settings/u/about/guide/privacy/terms/theatres 八個手寫頁的 `?v=` 全釘死在 226 沒跟著 bump→這些頁的既有訪客最多 4hr（CF Pages .js 快取）拿到舊版、頭像仍撐爆。主站 index 走 gen_site content-hash 自動更新沒事,手寫頁是手動釘版號才漏掉。
- 修:八頁 `mm-acct-menu.js?v=226→227`,與 mm-strings 對齊。
- **流程教訓**:改共用 JS 檔（mm-acct-menu/mm-strings）時,cache-bust bump 必須掃「所有手動釘版號的手寫頁」,不能只 bump 當下在改的那頁。
- e2e 57 項全 PASS。

## [v2.8.4] - 2026-07-07 13:38
### 清理 — i18n 孤兒 key 掃描（PM 稽核循環 R3）:刪 9 個無使用 key

- 寫掃描器對 mm-strings 210+ key 全 repo（含 data.js/me-catalog.js 等資料層）比對使用處,真孤兒 9 個（繁英各一份）全刪:
  `del_zone`（settings 改 adv_zone 後遺留）、`footer2_me`（me.html 舊 footer）、`first_west_end/first_broadway/first`（舊版徽章遺留）、`nav_account/menu_my/pc_account`（大頭照選單 label 已內建於 mm-acct-menu.js）、`fld_title`（me-input 只用 fld_title_req）。
- persona `p_*` 等 16 個初判候選中 7 個為掃描器漏含 data.js 的假陽性,已修掃描器複驗=零孤兒。
- `?v=227` bump;e2e 57 項全 PASS。

## [v2.8.3] - 2026-07-07 13:32
### 修正 — 首次登入 onboarding 建議 chips 渲染三份（PM 稽核循環 R2 於 375px 截圖抓到）

- 根因:Supabase auth 事件（INITIAL_SESSION/SIGNED_IN + getSession）會多次觸發 `mmAuthReady` → `maybeOnboard`/`buildChips` 併發執行,`box.innerHTML=''` 在各自 await 前就跑完,三個併發各自 append → 使用者首次登入看到三排重複建議、focus trap 疊三層監聽。
- 修:`maybeOnboard()` 加 `if(FORCED)return` 重入防護（FORCED 首次進入即設,後續呼叫直接擋）。
- 桌面 e2e 先前只驗 chips 存在沒驗數量所以漏掉;補「chips 只渲染一份」斷言,e2e **57 項全 PASS**;375px onboarding/u.html 公開頁(長名)無橫向溢出稽核同輪 PASS。

## [v2.8.2] - 2026-07-07 12:00
### 修正 — settings 手機版橫向溢出（使用者質疑「才一個?」後補掃出的真 bug）

- 使用者質疑通盤檢查只抓一個 bug 不可信——正確。補掃四個未覆蓋面向（RWD 375px×3頁、其餘五頁頭像替換、無 handle 新帳號流程、超長名字溢出）,**再抓到一個**:settings 在 375px 寬**橫向溢出 19px**（scrollW 394）。
- 根因（Playwright 逐元素隱藏+override 實驗定位）:style.css `body{display:flex;flex-direction:column}`＋`main.legal{margin:0 auto}` → main 以 fit-content 佈局,被 handle 輸入列固有寬（nowrap 網址前綴＋input 預設 `size=20`）撐爆。about/privacy 全是可換行文字所以沒踩到。
- 修:`main.legal{min-width:0;max-width:min(760px,100%)}`＋`.handle-row input{width:0}`（固有寬歸零,寬度全由 flex 分配）。
- 驗證:補充稽核 **15 項全 PASS**（guide/privacy/terms/theatres/u 五頁頭像替換、settings/me/index 375px 無溢出、無 handle 首次設名、長名不溢出）＋桌面 e2e **56 項全 PASS**＋375px 截圖親驗。

## [v2.8.1] - 2026-07-07 11:46
### 修正 — settings.html 改用主站淺色紙感＋補頁尾（使用者抓到:我沒對照指定參考頁就交卷）

- **檢討**:使用者指定「風格照 about 頁」,我卻沿用 me-v2 的深色主題、也沒放全站頁尾——功能 e2e 都驗了,但**沒把參考頁打開逐項對照**,被使用者抓包。此為流程疏失,教訓入記憶。
- **重建 settings.html**:改走 about/legal 淺色紙感骨架——`css/style.css`＋`#topbar` 導覽（brand+tagline+語言 pills+地圖首頁/怎麼使用/我的音樂劇 CTA,登入過自動換頭像）＋`.site-foot` 頁尾（回到地圖/我的音樂劇/怎麼使用/隱私/條款）;表單欄位配色改 paper/gold tokens;登入閘同步改淺色;nav 頭像改與全站一致走 autoMount(cookie)。me-v2.css 內 st-* 深色樣式移除（bump ?v=262）。
- **通盤重驗時再抓到一個 bug**:未登入閘訊息把 `gate_signin` 的 HTML 當純文字印出（我用 textContent,me.html 慣例是 innerHTML;字串為自家字典無用戶輸入）→ 修正＋截圖驗證。
- **儲存回饋位置**（本輪使用者另一指示）:「✓ 已儲存/錯誤」訊息顯示在儲存按鈕旁（欄位下仍留錯誤細節）,提示文字讓位。
- 驗證:e2e **56 項全 PASS**（新增:底色亮度、style.css 非 me-v2、頁尾存在與連結、儲存訊息在按鈕旁、autoMount 頭像）;繁/英/簡＋未登入閘截圖親驗。

## [v2.8.0] - 2026-07-07 11:22
### 改進 — Google 大頭貼上 nav + settings 版面微調（使用者指示四項）

- **nav 頭像=Google 大頭貼**:me/settings 從 session `user_metadata.avatar_url` 取得,同時種跨子網域 `mm_av` cookie 給主站等 cookie-only 頁;元件端只信 googleusercontent/gstatic 圖床(防 cookie 塞怪網址)、`referrerPolicy=no-referrer`、載入失敗自動退回首字母。settings 頁頂 monogram 同步換大頭貼。
  - **文案同步（隱私宣稱不可與功能打架）**:原「Google 授權會附帶頭像,本站不使用」6 處全改——gate_secure/how_b4_p/pp_s2_li1 繁英+guide/privacy 靜態 HTML;新宣稱=「頭像只顯示給你本人(登入後選單與設定頁),不會出現在公開頁」;隱私政策「最後更新」bump 2026-07-07。terms 無頭像字句(掃過)。
  - **修 CSS bug**:頭像 img 在 `display:grid` auto 軌內 `height:100%` 解析不到定值→照圖片比例撐爆圓框;改 `position:absolute;inset:0` 定位(先量 computed 32×32/50×50 再截圖雙驗)。
- **me.html hero**:「最新一場 …」整行移除（使用者指示,hero 留大數字+帳號列）。
- **settings.html**:儲存鈕移到「公開分享」下方、「登出」上方（附說明:開關即時生效,身分修改才要按儲存）;「危險操作」→「**進階操作**」(adv_zone)且**預設收合**(`<details>`,展開才見刪除帳號)。
- 驗證:e2e 擴到 **50 項全 PASS**(新增:大頭貼 img 出現於 nav/設定頁頂、最新一場已移除、儲存鈕 DOM 順序、進階預設收合/展開可見刪除鈕);`?v=226` bump+gen_site 重產;截圖親驗。

## [v2.7.0] - 2026-07-07 10:53
### 改版 — 帳號介面全面重構（使用者定稿版）:專屬設定頁 settings.html + 全站 nav 大頭照選單 + hero 帳號列

**使用者對 v2.6.0 的修正指示**:①主站等各頁右上角「我的音樂劇」→登入後換成**大頭照展開選單**（我的音樂劇/帳號設定/登出）,未登入照常顯示 CTA（比登入更有 incentive）;②帳號設定=**專屬頁面**（非彈窗）,含 Display name/Profile privacy/Sign out/Delete account,風格維持本站金色紙感（FR24 只取結構）;③v2.6.0 的身分卡整區移除,「公開狀態 pill/專屬網址+複製/＋加入音樂劇」三樣整合進 hero。

- **`settings.html`（新）**:單欄設定頁——身分頭部（monogram+名稱+登入 email+加入於）、帳號身分（顯示名稱+username 改名,即時查重,儲存鈕）、公開分享（公開開關+票價/座位+分享連結複製,**開關即時生效** FR24 式,失敗自動回滾）、登出、危險操作（刪除帳號）。輕量 auth（不同步 sightings）;`?signout=1`=全站登出入口（signOut+清 cookie/快取→回主站）;主網域開啟自動轉 my. 子網域（session 同源）;noindex;三語。
- **`js/mm-acct-menu.js`（新,全自包元件）**:monogram 頭像+下拉選單,自帶樣式與三語標籤;autoMount 偵測 `mm_owner` cookie,把 nav 上的「我的音樂劇」CTA 換成頭像（未登入不動）。掛進 **index(gen_site 模板)/about/guide/privacy/terms/theatres/u.html** 七處+me/settings 手動掛載;u.html 的「＋建立你自己的」CTA 補 `id="mine-link"` 一併適用。
- **me.html**:v2.6.0 profcard 整區移除;hero 下緣新增帳號列（公開中/未公開 pill→settings、`my./handle` ↗+複製、＋加入音樂劇）;nav 掛頭像選單;acctModal 刪除（帳號設定改連 settings.html）;分享 modal 維持 onboarding 專用。
- **Worker**:保留字 `/settings` 改 302 到 `my./settings.html`（同源才讀得到 session）,不再丟回主站。**需 wrangler deploy**。
- **gen_site.mjs**:模板掛 mm-acct-menu(defer);元件檔納入 VER 資產雜湊;三語 index 重產。
- **i18n**:pc_private「私密→未公開」（使用者用語）;新 key nav_account/menu_my/st_*;移除 pc_shows_n/pc_show_one(卡片已拆,hero 有 bignums 不重複);`?v=225` 全站 bump。
- **驗證**:Playwright(真 Chrome+mock Supabase)e2e **45 項全 PASS**——me hero 列/複製/加入/頭像選單三項連結/登出、onboarding 回歸、settings 頁載值/改名 RPC/顯示名/開關即時存+回滾路徑/頁面登出/`?signout=1`、主站 index 無 cookie=CTA・有 cookie=頭像+選單連結、about 頁 spot check、EN/簡中（账号设定/Account settings）;繁英簡+捲動底部截圖親驗（fullPage 接縫確認為拼接假象,真捲動無縫）。

## [v2.6.1] - 2026-07-07 10:13
### 修正 — me-v2.css 加 `?v=` cache-bust（使用者回報上線後看不到帳號中心）

- 使用者於 v2.6.0 上線後回報「沒看到」。查證:三個入口（`/me`、my. 子網域本人/訪客）**HTML 皆已是新版**（`max-age=0, must-revalidate` 每次重新驗證）,但 **CF Pages 對 `.css` 出 `max-age=14400`（4 小時）**——`css/me-v2.css` 一直沒掛 `?v=`,瀏覽器最多 4 小時內拿舊樣式,新的身分卡會以無樣式狀態呈現。JS 早有 `?v=` 慣例,CSS 漏掉。
- 修:`me.html`/`u.html` 的 me-v2.css 連結掛 `?v=261`,之後改 CSS 一律同步 bump。

## [v2.6.0] - 2026-07-07 09:41
### 新功能 — me.html 帳號中心：頁面頂部身分卡 + 統一帳號設定面板（參考 my.flightradar24 個人頁）

**個人頁新增專屬 profile 介面,帳號相關事宜（取名/改名、公開與否、加入音樂劇、登出、刪除帳號）全部集中一處,不再散在 nav 按鈕與兩個 modal。**

- **身分卡 `#profCard`**（header 下方,登入後顯示）:金色首字母 monogram + 顯示名稱 + **公開中/私密狀態 pill**（一眼可見,點了直接開設定）+ 專屬網址 `my.themusicalmap.com/<handle>`（可點開公開頁 + 複製鈕）+ 副標（加入於 年月 · N 部音樂劇,收藏數只算真實紀錄不拿範例資料冒充）+ 三顆動作鈕:**＋加入音樂劇 / 帳號設定 / 登出**。樣式進 `css/me-v2.css`（u.html 無此節點不受影響）,窄幅 RWD 按鈕滿版。
- **統一帳號設定面板**（原 `#acctModal` 擴充）:「帳號身分」（username 改名走 `rename_handle`+顯示名稱）+「公開分享」（公開開關/顯示票價/顯示座位/分享連結+複製,自舊分享 modal 整併移入）+「危險操作」（刪除帳號）。儲存合併為一顆:改名走 RPC、其餘欄位有變才一次 `upsert`;只有真的改名才顯示「舊網址會自動轉向」訊息。開面板時開關一律從已儲存狀態重置,取消不殘留。
- **舊「分享」modal 縮編為 onboarding 專用**（首次登入強制取名,原 23 項 e2e 流程不動:空白欄位+建議 chips+唯一出口登出）;nav 的「分享」「登出」按鈕移除（功能都在身分卡）。孤兒 i18n key（share_title/share_lead/share_url_label/handle_to_acct_*/nav_share）清除。
- **修既有 bug**:刪除帳號流程呼叫的 `clearLocal()` 定義在另一個 IIFE 作用域,實際執行會 ReferenceError→刪除成功卻誤報「刪除失敗」;改走 `window.mmClearLocal` 橋接。
- **i18n**:新 key `pc_*`（pill/提示/加入於/複製網址/N 部音樂劇）+ `pf_sec_*`（面板段落標題）,繁英雙字典、簡中 OpenCC 自動轉（驗證出「账号身份/公开分享/公开中」）;`mm-strings.js?v=224` 全站 bump（7 頁）。
- **驗證**:Playwright 真 Chrome e2e **34 項全 PASS**（mock Supabase:種 session token+攔 REST/RPC/auth）——身分卡渲染/pill 狀態/複製網址進剪貼簿/開關儲存後 pill 即時翻轉/改名後卡片網址更新/ESC/點 pill 開面板/加入音樂劇 iframe/登出 signOut/onboarding 強制流程回歸（chips=email 前綴/設名後卡片即現網址）/英文+簡中面板;繁/英/簡截圖親驗。inline script 10 塊 V8 語法解析全過。
- **過程備註**:本次曾與一個誤啟動的背景分身 session 並行改檔（身分卡方案來自該分身）,已由使用者裁示本 session 主導,成果為兩方案合體:分身的卡片殼 + 本 session 的面板整併與驗證。

## [v2.5.1] - 2026-07-07 01:05
### 文件 — 全 repo MD 過時掃描更新（13 檔全查,5 檔修）+ 站外事項收尾入檔
- README:worker/ 條目「已寫好未部署」→ 已上線(2026-07-06,回源 CF Pages,含 FR24 根路徑模式)。
- SETUP_MY_SUBDOMAIN:Worker 行為表全面翻新——回源 GitHub Pages→**Cloudflare Pages(musicalmap.pages.dev,v2.4.0)**;根路徑 302 主站→**直接出 me.html(FR24 模式,v2.2.0)**;本人 cookie 同網址編輯版;保留字獨立列。
- DESIGN_username_sharing:「主站維持 GitHub Pages」→ 主站亦已遷 CF Pages(GH 熱備援)。
- SETUP_ACCOUNTS:OAuth 品牌驗證前置補進度——Search Console 網域驗證+sitemap 完成(2026-07-06)、GA4 上線(G-GC07MYC1MY,獨立帳戶 MusicalMap)、CF WA 站點 f5debd92。
- AFFILIATE_SETUP:補 Sovrn 網站送審狀態(themusicalmap.com 2026-07-06 送審;審核由首批分潤點擊觸發;舊 github.io 條目永久 Pending 屬預期、勿刪)。
- 站外(無 code):GA4 資源已移入獨立帳戶 MusicalMap(400154354),與 SunFlightMap 平行;CF WA 邊緣凍結 22:05 自癒,f5debd92 全鏈路 204+GraphQL 驗證通過。

## [v2.5.0] - 2026-07-06 21:04
### 新增 — Google Analytics(GA4)全站上線 + 隱私聲明同步更新 + CF WA 殭屍注入結案
- **GA4 埋碼**:評估 ID `G-GC07MYC1MY`(資源 MusicalMap/串流「MusicalMap 主站」,同一 ID 涵蓋主站與 my. 網域,報表以 hostname 區分)。插入點=gen_site 模板(三語生成頁)+8 手寫頁(about/guide/privacy/terms/theatres/**me/u/me-input**——後三頁經 Worker 原樣供 my.,埋檔案即涵蓋);root 路由頁不埋(立即轉走);不加 SRI(gtag.js 滾動更新,釘 hash 靜默斷統計)。
- **隱私聲明翻新**(privacy.html+mm-strings.js 繁英兩處,hans 由 OpenCC 轉):§1 揭露 CF WA(無 cookie)+GA 統計、託管宣稱 GitHub Pages→Cloudflare Pages(v2.4.0 遷移後過時);§3 揭露 GA 統計 cookie。
- **CF WA 未結案項處置**(v2.4.4 交接案,設定操作非 code):實證 Pages 整合 snippet POST 到死端點(404)且壓制正常 beacon→**已停用 Pages WA 整合**+CI 重佈清除;Worker 部署更新至 v2.4.3 版(repo 已 no-op 但線上是舊版);**邊緣注入凍結在已刪站 token 93711998→8f6e**,站點重建×2/rum off-on/ruleset 全試無效,判定 CF 側傳播故障,資料持續入 8f6e(僅 GraphQL 可查)待自癒,詳見記憶 project_musicalmap_analytics。
- Search Console 網域資源+TXT 驗證+sitemap 提交、sovrn themusicalmap.com 送審——同日站外設定,無 code 變更。

## [v2.4.4] - 2026-07-06 18:20
### 交接 — Web Analytics 未結案狀態入檔(使用者換 session)
- 全站已統一 Pages 專案層 WA token(9683049c,建置時注入,殭屍已清);待確認新站點入帳(09:54Z 後 >10 分零入帳,可能是新站首次延遲)。分析查詢 token 存 scrapers/.cf_analytics_token(本 commit 加入 .gitignore 保護)。下一步=使用者 Global API Key 做 RUM API 手術;僅限 Cloudflare 原生解法。完整交接見記憶 project_musicalmap_analytics。

## [v2.4.3] - 2026-07-06 16:50
### 定案 — Web Analytics 全面改走 zone 自動注入,拆除全部手工統計碼(v2.4.1/v2.4.2 作法作廢)
- **API 鐵證翻案**:手動 snippet 上報在本帳號**從未入帳過任何一筆**(15 分鐘輪詢×多輪+7 天對照全零);唯一有效機制=zone RUM 自動注入(edge 對瀏覽器請求的 HTML 回應加 beacon——**注入器跳過非瀏覽器 UA,所以 curl 檢查永遠看不到、曾誤判為無效**)。
- 拆除:gen_site 模板+5 手寫頁 beacon、Worker CF_BEACON/withBeacon 注入(留 no-op 掛點)。使用者把站點切回「Enable(自動注入)」。
- **結案驗收**:受控真實造訪(16:42)→ GraphQL 入帳確認 my./danny + 主站 zh-hant 各 1 筆,歸戶 siteTag `8f6e823a…`(zone 整合實體;涵蓋主站+www+my. 含 Worker 動態頁)。
- **儀表板正解**:dash.cloudflare.com/23cd…/web-analytics/overview?siteTag=8f6e823a5c2e4ec285b61d9f11569682(直達網址;清單卡片的預覽數字不可信)。

## [v2.4.2] - 2026-07-06 14:33
### 修正 — Web Analytics 站點重建,全站統一單一 token
- 事故鏈:WA 介面同時存在「網域整合站點(收全部)+手動站點(空殼)」的三胞胎混亂 → 使用者把清單裡兩張卡都刪除 → **站點卡片刪除=其 token 立即失效,全站上報被拒收**(API 實證:刪除後兩次受控真實造訪等 11 分鐘零入帳;歷史 13 筆保留)。
- 修:使用者重建**唯一**站點(themusicalmap.com,手動 snippet 模式)→ 全站換新 token `c6bab841…`(gen_site 模板+5 手寫頁+Worker CF_BEACON),Pages 直傳+Worker 部署+線上抽驗兩網域皆新 token。主機分流看儀表板 Hosts 維度。
- 驗收標準改為 **GraphQL 原始入帳**(rumPageloadEventsAdaptiveGroups),不再信清單卡片預覽數字(快取極懶)。教訓已寫 worker 註解+記憶。

## [v2.4.1] - 2026-07-06 12:43
### 新增 — Cloudflare Web Analytics 訪客層統計全站上線(兩站點分流)
- **my.themusicalmap.com 站點**:Worker 對四個 HTML 出口注入 beacon(根入口/訪客公開頁/本人編輯頁/代理 .html 如 me-input)——my. 頁面是 Worker 動態組出,zone 自動注入碰不到,故 Worker 注入;`withBeacon()` 有防重複 guard。已部署+四出口線上驗證各 1 份。
- **themusicalmap.com 站點**:zone 自動注入對 Pages 出貨實測無效(0 注入)→ 改埋進頁面本身:gen_site.mjs 變體模板+5 個手寫頁(guide/about/privacy/terms/theatres),root 路由頁不埋(立即轉走)。站點設定改「Enable with JS Snippet installation」關掉自動注入避免將來雙計數。
- **token 分流鐵則**:me/u/me-input 原始檔**不可**埋主站 token(它們經 my. 出貨,Worker 注入 my. token;埋了會因防重 guard 讓 my. 流量記到主站站點)。本機驗證:主站 8 頁各 1 份主站 token、me/u/me-input=0。
- SRI 刻意例外(全站 CDN 釘 SRI 的唯一例外):beacon 由 CF 滾動更新,釘 hash 會靜默斷統計;出貨方即 Cloudflare,已在信任鏈內。註解已載明。
- 免費方案更正:zone Traffic 的完整機器人分析是付費功能,免費版看不到(先前說法有誤);真人數據看 Web Analytics 兩站點儀表板。

## [v2.4.0] - 2026-07-06 12:08
### 重大 — 託管切換完成:themusicalmap.com 改由 Cloudflare Pages 出貨(全流量進 Cloudflare,可完整監控)
- 使用者在 Pages 專案掛 Custom domains(themusicalmap.com+www),DNS 由 CF 自動改 CNAME→musicalmap.pages.dev;切換空窗僅 ~15 秒(輪詢實測 12:06:33 522→12:06:49 200)。
- Worker `GH_ORIGIN`→`https://musicalmap.pages.dev`(同家調貨;CI 雙部署保證與 GH 位元級一致)。
- 驗收全過:主網域 16 路徑 200(Server: cloudflare)、www 200、舊 github.io 首頁+深層連結仍 301、my. 三情境(訪客 200/本人 cookie 200/不存在 404)、線上 playwright e2e 七項 PASS、主站截圖 render 正常。
- **GitHub Pages 保留原地當熱備援**(CI 照常雙部署;反悔=DNS 改回 A 記錄即回滾)。
- 架構現況:主站+my. 全部 Cloudflare 出貨;GitHub=程式碼+每日爬蟲 CI。剩使用者一鍵:Pages 專案開 Web Analytics(訪客層統計)。

## [v2.3.1] - 2026-07-06 11:54
### 新增 — CI 雙部署:每次 push 同步部署 GitHub Pages + Cloudflare Pages
- update.yml 加 `deploy-cloudflare` job(wrangler-action@v3):下載 build job 的同一份 Pages artifact 解包後 `pages deploy` 到 musicalmap 專案——兩邊內容位元級一致。與 GH Pages 部署平行跑,互不阻擋。
- 憑證:使用者建立 Cloudflare API token(僅 Account→Cloudflare Pages→Edit 權限,無 IP 限制無到期)→ 存 repo Secrets `CLOUDFLARE_API_TOKEN`+`CLOUDFLARE_ACCOUNT_ID`(先驗證過 token 可列出 Pages 專案)。
- Supabase 端:使用者已重跑 add_handle_aliases.sql(保留字 guide/me-input 生效)。
- 本 push 本身即是雙部署首跑驗證。

## [v2.3.0] - 2026-07-06 11:40
### 準備 — Cloudflare Pages 遷移前置:全站內部連結無副檔名化 + 平行預覽站
- 使用者拍板遷移託管到 Cloudflare Pages(目標=在 Cloudflare 精準監控所有流量)。採零風險路徑:先平行預覽,DNS 最後才切。
- **全站內部連結去 .html**(CF Pages 會把 .html 網址 308 到無副檔名;GH Pages 兩種都直達 → 先改連結,兩平台皆零轉向):手寫頁 guide/about/privacy/terms/theatres 相對連結改根路徑(/guide 等);**me/u/me-input(跑在 my. 網域)改完整網址 https://themusicalmap.com/...(相對路徑會被 Worker 當 handle 查詢)**;app.js attribution 三連結、gen_site.mjs 模板與 sitemap、llms.txt(me 連結改 https://my.themusicalmap.com/)。註解裡的隱藏連結一併修。**保留不動**:me-input.html iframe 引用(靠 .html 走 Worker 代理共享登入態)、Worker 伺服器端 fetch。
- **保留字補漏**:RESERVED 三處清單(me.html/worker/DB migration)都缺 guide → 補 guide+me-input;**DB 端需使用者在 Supabase 重跑 add_handle_aliases.sql**(冪等)。
- **平行預覽站** https://musicalmap.pages.dev(專案 musicalmap,wrangler 直傳,241 檔遠低於 2 萬上限):9 條路徑 200 全零轉向、四頁內部 .html 連結數=0;正式站(GH)無副檔名路徑 5 條全 200(切換前相容確認);me.html e2e 七項回歸 PASS。
- 待辦(使用者 Cloudflare 後台):連接 Git 整合(push 自動雙部署)→ 評估後把 themusicalmap.com 自訂網域掛到 Pages 專案(=正式切換,Worker GH_ORIGIN 同步改)。

## [v2.2.4] - 2026-07-06 11:11
### 修正 — 使用者短暫看到 saved_ok 字面(字典檔快取空窗根治)
- 病因鏈:新增字串只存在新字典,使用者瀏覽器抱著舊字典(且 v2.2.3 之前被 Cloudflare 給了 4h TTL)→ 新程式要不到字串,把內部代號顯示出來。**非設計行為,是缺陷**。
- 根治:mm-strings.js 引用全站(7 頁)加版本參數 `?v=223`,之後每次改字典同步 bump——瀏覽器視為新網址立即抓新版,不再有新程式配舊字典的空窗。**規則:改 mm-strings.js 必 bump 此版本參數(7 個 html 一起)**。

## [v2.2.3] - 2026-07-06 11:08
### 修正 — my. 網域靜態資源瀏覽器快取過長(部署後最多 4 小時舊 JS)
- Worker 代理 GH Pages 資源時 Cloudflare 把瀏覽器 cache-control 拉到預設 4 小時(14400);部署新版後 my. 使用者可能拿舊 JS/CSS 數小時(本次 saved_ok 字典殘影即此因)。修:代理回應一律改寫 `public, max-age=600`,與主站 GH Pages 對齊。
- 線上驗證:mm-strings.js 標頭=600、`saved_ok: '✓ 已儲存'` 字串就位;儲存自動關閉 e2e 線上七項 PASS(v2.2.2 首測抓錯 run id 搶跑,重測通過)。

## [v2.2.2] - 2026-07-06 11:05
### 修正 — 分享面板「儲存」成功後不會自動關閉(使用者實測回報)
- `me.html` `save()` 非 onboarding 分支成功後從未呼叫 `close()`(只有首次取名那條會關)。修:成功→按鈕短暫顯示「✓ 已儲存」(新字串 `saved_ok`,繁英+簡中 runtime 轉)→450ms 自動關閉;失敗仍留在面板顯示錯誤。
- 驗證:playwright 真頁 e2e(真 DOM,僅 Supabase 寫入 stub)七項 PASS——開面板/網址=my./danny/儲存顯示✓/自動關閉/按鈕復原/重開/X 關閉;push 後對線上站重跑同測。
- 登入回跳問題結案:病因=Supabase Redirect URLs 未含 my. 網域(用 /auth/v1/verify 不需帳號實測證實),使用者加 `https://my.themusicalmap.com/**`+Site URL 改 my. 後,線上實測回跳正確。

## [v2.2.1] - 2026-07-06 10:48
### 修正 — 熱路徑零轉向(使用者指正「頁面跳來跳去效率差」)
- 全站導覽「我的音樂劇」直連 `https://my.themusicalmap.com/`(手寫頁 about/guide/privacy/terms/theatres/u.html 共 14 處 + gen_site.mjs 模板帶 ?hl,三語頁重建)——不再經 me.html 再跳。
- Worker 根路徑 `/` 改**直接出 app 內容**(原 302 到 /me.html 也省掉);登入後網址列變 /<handle> 用 replaceState 原地改字,不重載。
- 轉向只保留三種舊連結救援(舊書籤 me.html/舊分享 u.html?u=/github.io 301),正常動線零轉向。

## [v2.2.0] - 2026-07-06 10:44
### 重大 — FR24 式同網址模式:my.themusicalmap.com/<handle> 一個網址,本人=編輯版、訪客=唯讀版
- 使用者指正:FlightRadar24 是同一網址(my.flightradar24.com/Chiang),登入與否只差能否編輯——不是「管理後台/公開頁」兩個網址。照此重構:
- **Worker**:`/<handle>` 先看 `mm_owner` cookie——與路徑相符(本人)→ 同網址出 me.html 編輯版(`private, no-store`);否則照舊出 u.html 公開版(補 `Vary: Cookie`,防登入前後拿到彼此的瀏覽器快取)。cookie 僅選版面,偽造只拿到登入閘,資料權限仍由 Supabase session+RLS 把關。根路徑 `/` 改 302 到 `/me.html`(my.=個人應用的家)。
- **me.html**:登入取得 handle 後種 `mm_owner` cookie(Domain=.themusicalmap.com)+`history.replaceState` 把網址列改成 `/<handle>`(改名同步換、alias 接舊名);登出/刪帳號清 cookie→同網址變回公開版。主網域 `themusicalmap.com/me.html` 一律轉到 `my.themusicalmap.com/me.html`(localhost 不轉)。
- 驗證(線上 curl):根 302→/me.html、/me.html 200、/danny 無 cookie=u.html 公開版、本人 cookie=me.html 編輯版、他人 cookie=公開版、Vary/快取標頭正確。登入後編輯流程需真人 OAuth 驗收。
- **使用者待辦**:Supabase Redirect URLs 加 `https://my.themusicalmap.com/**`(沒加則 my. 網域 Google 登入無法回跳)。
- 下一步(使用者已給 FR24 Account settings 截圖參考):帳號設定重整為獨立設定區(Display name/隱私分級 pills 版面)。

## [v2.1.0] - 2026-07-06 10:29
### 新功能 — my.themusicalmap.com/<username> 個人公開頁上線（FR24 式乾淨網址）
- **Cloudflare Worker 部署完成**（使用者 wrangler login 授權後 `npx wrangler deploy`;`wrangler.toml` 改 `custom_domain=true` 讓 Cloudflare 自動建 `my` DNS+憑證,免手動 AAAA 100::）。版本 4d807b44。
- 線上逐項驗證:`/danny` 200+`window.MM_HANDLE` 注入+個人化 `<title>`/canonical、不存在的名字 404、根路徑 302 回主站、robots.txt allow、`css/me-v2.css` 代理 200、headless 截圖完整 render(hero 統計/海報牆/即將上演緞帶)。
- `me.html`:`shareUrl()` 改產 `https://my.themusicalmap.com/<handle>`;onboarding 與帳號設定兩處 prefix 標籤 `…/u.html?u=`→`my.themusicalmap.com/`。
- `u.html`:head 加早期轉向 script——主網域 `u.html?u=xxx` 一律 `location.replace` 到 `my.themusicalmap.com/xxx`(帶 `?hl=`;localhost 與 my. 網域不觸發,本機測試不受影響)。
- docs/SETUP_MY_SUBDOMAIN.md 狀態更新,收尾清單 3/4 勾掉(剩 og:image 個人化);首次登入強制取名/建議名/改名舊名 301 為 v1.10.0 既有功能,本版只換網址形式。

## [v2.0.0] - 2026-07-06 10:01
### 重大 — 主站遷移至自訂網域 https://themusicalmap.com（網域/DNS 於 2026-06-24 已就緒，今日完成程式面；網址全面變更=不相容變更，進 MAJOR）
- `build/gen_site.mjs`:`BASE` `/MusicalMap/`→`/`、`SITE`→`https://themusicalmap.com`,重建三語頁(en/zh-hans/zh-hant,各 1,728 筆)+root router+`sitemap.xml`+`robots.txt`。
- 新增 repo 根 `CNAME`(`themusicalmap.com`)——CI push 部署把 repo 現狀當 artifact,`CNAME` 在根即被 Pages 認領。
- 手寫頁絕對網址全換新網域:about/guide/privacy/terms/theatres/u.html(canonical/hreflang/og:url/og:image)、`llms.txt`、`js/mm-strings.js`(隱私政策 pp_intro 繁英)、README、docs/AFFILIATE_SETUP、docs/SETUP_ACCOUNTS(Google OAuth origins 改新網域;「未上線」過時敘述更新)、worker/my-worker.js `GH_ORIGIN`。CHANGELOG 歷史條目與 `js/config.js` Mapbox 白名單註解(陳述事實)不改。
- 程式面不用改的(查證過):me.html OAuth `redirectTo` 用 `location.origin` 動態值;Mapbox token 白名單 2026-06-24 建立時已含裸網域 `themusicalmap.com`(自動涵蓋子網域)。
- 驗證:全 repo grep 無舊網址殘留(歷史/事實註解除外);本機 http.server+headless Chrome 截圖確認 en 頁資產(BASE=/)全載入、地圖/卡片/海報正常 render。
- **站外待辦**:Supabase Redirect URLs 加 `https://themusicalmap.com/me.html`(使用者後台操作);GitHub Pages Custom domain+HTTPS(push 後 gh api 設定);sovrn 後台 +Site 重送審。

## [v1.33.2] - 2026-07-04 00:56
### 已知問題(待修) — 刪除帳號實機失敗
- 使用者實機測「帳號設定→刪除我的帳號」→ 跳 error(migration `add_delete_account.sql` 已套用)。
- **高度懷疑(待錯誤訊息確認,不寫死)**:RPC 第 33 行 `delete from auth.users` 失敗——SECURITY DEFINER 以建立者身分執行,但 Supabase 的 `auth.users` 由 `supabase_auth_admin` 擁有,一般 postgres/SQL editor 角色可能無 DELETE 權限(permission denied for table users);前面刪 public schema(sightings/profiles/aliases)應正常,卡在最後刪 auth 帳號。
- **正解方向**:改用 Supabase 官方推薦的 **Edge Function + service_role** 呼叫 `auth.admin.deleteUser()`(SQL 直刪 auth.users 在 Supabase 不可靠)。待使用者提供完整錯誤訊息確認病因後實作。

## [v1.33.1] - 2026-07-04 00:48
### 變更 — 全 md freshness 掃描(今日收尾)
- 嚴格掃過全 repo 13 個 .md。更新:README(劇目數 ~1,600→~1,700、My Musicals 段補 v1.26–v1.33 近期功能:♥最愛/刪帳號/簡體搜尋/i18n 邊界修/鍵盤可及/手機底部 sheet 含「仍有超框待續」註記);SETUP_ACCOUNTS(補 4 個漏列 migration:fix_display_name_email_leak/add_fav/add_delete_account/add_handle_alnum_check,標「已套用 ✓」);SECURITY_AUDIT_2026-07-02 加後續指標(不回改日期快照)。WORKFLOW/CHANGELOG 已最新;其餘設計/資料 docs 今日未觸及、無過時。
- **待續(明日)**:手機地圖底部 sheet 雖不再閃退,仍有超框改進空間(使用者真機回報)。

## [v1.33.0] - 2026-07-04 00:38
### 修正 — 手機地圖圖卡「閃一下就消失」真因 + 改底部彈出 sheet(使用者真機回報,v1.31.0 沒解決)
- **真因(用 playwright 逐幀追出)**:v1.31.0 的 closeOnClick:false 防不了這個——popup 開啟時 Leaflet 的 **autoPan** 想把大卡平移進小手機地圖,那個地圖移動觸發 **markercluster 重新聚合**→marker 連同 popup 一起被移除=閃一下消失。(我上次太快把 headless 的「開了又關」當假象放過,是疏忽。)
- **修**:① `autoPan` 依裝置——手機 false(不觸發 re-cluster)、桌面 true(維持靠邊 popup 自動帶進視野)。② `focusShow` 拆掉並發的 map.setView+zoomToShowLayer(兩動畫打架),只留 zoomToShowLayer。③ **手機版 popup 改「底部彈出 sheet」**:position:fixed 貼畫面底、滿寬、可上下捲、關閉鈕右上角圓形;popupopen 時把 popup 元素移到 <body>(繞過 Leaflet pane 的 transform 讓 fixed 生效)。
- **驗證(playwright iPhone12)**:popup 開啟並「保持」(opened/finalOpen/stayedAfterOpen 全 true)、觸碰卡片內容不消失、截圖確認海報+標題+劇院+城市+檔期+購票鍵完整顯示;桌面回歸 fitsScreen:true、非 sheet、無 error。

## [v1.32.1] - 2026-07-03 23:06
### 修正 — 無障礙 R20:詳情海報放大鍵盤可及(a11y 一致性掃描收尾)
- 延續 R19 星級評分,系統性掃全站可點元素的鍵盤可及性:絕大多數是 `<button>`(原生)或已有 role+keydown(♥/編輯/刪除/護照戳章/檢視切換/年份 chips/地圖 pin/城市列/combo 下拉);**唯一剩的滑鼠限定=詳情海報 `#dt-poster`(div+onclick 開原圖)**。
- 修:有海報時加 `tabindex=0`+`role=button`+`aria-label`(dt_zoom)+Enter/Space keydown;無海報時移除(不可互動)。me.html + u-view.js(公開頁)同步。實測 tabindex/role/aria/keydown 齊、零 error。鍵盤可及性掃描收斂完成。

## [v1.32.0] - 2026-07-03 23:01
### 修正 — 無障礙 R19:星級評分鍵盤/螢幕閱讀器無法操作
- **根因**:評分星星是純 `<span class="st">★</span>`,只有 onclick(滑鼠)+title,**無 tabindex/role/keydown**→鍵盤與螢幕閱讀器使用者完全無法評分(me.html 卡片按鈕早有 role+keydown,此處漏)。
- **修**:`#rate` 加 `role="group"`;每顆星加 `tabindex=0` + `role="button"` + `aria-label`(N 顆星) + keydown(Enter/Space 選定、方向鍵 +1/-1 並移焦點) + `aria-pressed` 狀態;補 `:focus-visible` 金色外框。實測真流程:Enter 設第3顆→ArrowRight 增到4(rateval「4/5」)、aria-pressed=true、focus 可見,零 error。
- 涵蓋兩個表單(手動新增 backfill + 詳情編輯),共用 buildRating。

## [v1.31.4] - 2026-07-03 22:52
### 修正 — 功能完整度 R17:改名殘留掃描(u.html meta「觀劇護照」)
- 延續 R16 的「改名沒同步」角度,全 repo 掃 session 內做過的改名舊術語。結果:觀劇足跡(0)、劇庫(只註解)、使用說明/身份/・(皆註解或正規化 regex,非殘留)。**唯一真殘留=u.html meta description 的「觀劇護照」**(同一句還混用「音樂劇護照」,自我矛盾;og:description 已統一)→改為「音樂劇護照」。
- 確認:音樂劇護照 20 次(標準)vs 觀劇護照 0(修後);mi_loading_lib 實為「載入音樂劇資料庫中…」正確。改名全 repo 同步完成。

## [v1.31.3] - 2026-07-03 22:49
### 修正 — 功能完整度 R16:i18n.js 漏掉「使用說明→怎麼使用」改名(theatres nav 舊標籤)
- **根因**:v1.26.0 把「使用說明」改「怎麼使用」只改了 mm-strings.js,漏了 i18n.js(另一套字典)。首頁 nav 因走 gen_site.mjs 烘焙值(無 data-i18n)沒中招,但 **theatres.html 用 i18n.js 的 `nav_guide` → 顯示舊的「使用說明」**,與全站不一致。
- **修**:i18n.js `nav_guide` 使用說明→怎麼使用;theatres.html 靜態 fallback 同步。實測 theatres zh nav 顯示「地圖首頁·怎麼使用」✓。(英文/簡中經 i18n.js 的 Guide/OpenCC 自動轉,正確。)
- 同輪驗證(皆正常):統計計算精準(星期分布無時區 bug、unique/cities/countries 全對)、8 頁英文模式無未翻譯殘留(除刻意的語言 pill 原生標籤)、display name 用 textContent 無 XSS、排序/時間軸/播放正確。
- 已知小 gap(未修):theatres.html 僅 zh/en 兩語(用舊 i18n.js),無 zh-hans;次要工具頁,影響低。

## [v1.31.2] - 2026-07-03 22:37
### 修正 — 功能完整度 R14:handle 只有 -/_ 也能過(如 "---")
- **根因**:handle 驗證只擋空字串+保留字+字元集,`norm("---")="---"` 非空、非保留字→通過→變成 /u.html?u=--- 這種無意義網址。DB CHECK `^[A-Za-z0-9_-]{1,30}$` 也只驗字元集,不要求含字母數字。實測 "---"/"___"/"-_-" 修前顯示「檢查中…」(=已通過格式)。
- **修**:前端 me.html 三處(check/onboarding save/acctSave)加 `/[a-z0-9]/` 檢查——至少一個字母或數字,否則顯示輸入提示不可存;**DB migration `add_handle_alnum_check.sql`** 用 lookahead 收緊 CHECK 為 `^(?=.*[A-Za-z0-9])[A-Za-z0-9_-]{1,30}$`(防繞過前端)。實測 "---"/"___"/"-_-" 修後顯示提示、不可存;其餘(音樂劇→空拒/大寫→小寫/admin 保留/特殊字元濾/單字元 a/數字 12)皆正確。
- ⚠️ migration 待執行(前端已上線,DB 為防線)。

## [v1.31.1] - 2026-07-03 22:29
### 修正 — 手機詳情彈窗同類超框(延續 v1.31.0 popup 修法主動找到)
- **根因**:me/u 的詳情彈窗(#detail)手機版海報 `min-height:240px` 且無上限→以完整比例撐到 ~530px 佔滿畫面,把劇院/日期/座位/票價/評分/心得/售票連結全擠出畫面,`overflow:hidden` 再裁掉。截圖確認只剩標題可見。與使用者回報的地圖 popup 同一種病。
- **修**:手機版(≤680px)海報限高 34vh、彈窗改 `overflow-y:auto` 可捲、dt-body padding 縮小、標題字級降。截圖確認海報適中、所有資訊(★評分/劇院/城市/日期/時間/座位/票價/連結/心得)完整顯示且可捲。me-v2.css 一處修正同時涵蓋 me.html 與公開頁 u.html。

## [v1.31.0] - 2026-07-03 22:24
### 修正 — 手機地圖 popup 兩個 bug(使用者實機回報)
- **Bug 1 超框**:桌面 popup 是「海報 340px 高橫排卡」,手機短地圖框(58%)裝不下→超出畫面、UI 差。修:手機版(≤680px)改**直式**——海報在上(限高 26vh)、內容在下、整卡 `max-height:64vh` + `overflow-y:auto` 可上下捲;pop-body inline 寬度用 `100%!important` 蓋掉。實測 fitsScreen ✓、截圖確認完整顯示。
- **Bug 2 觸碰消失**:一觸卡片就關閉→看不到售票資訊。根因=Leaflet popup `closeOnClick` 預設 true(點地圖/卡片就關)。修:bindPopup 加 `closeOnClick:false`——只有 × 鈕或點別的 marker 才換卡,觸碰卡片內容不再消失;加 `autoPanPadding` 讓超框卡自動平移進視野。
- 驗證:注入 popup DOM 量電腦 computed style(column/poster 172px/content overflow auto/fitsScreen true) + iPhone 12 截圖確認直式完整;服務端 JS 已含 closeOnClick:false。

## [v1.30.2] - 2026-07-03 21:31
### 修正 — 功能完整度 R11:城邦地名重複(新加坡, 新加坡)
- 城邦(新加坡/香港/澳門等)city===country 時,首頁 popup/tooltip/側欄 + me/u 卡片/詳情都顯示「新加坡, 新加坡」重複。加 `cityCountry()` helper(翻譯後比對,相等只顯示一次),套 app.js 3 處+me.html 2 處+u-view.js 2 處。實測 popup 顯示單一「新加坡」、全頁無殘留、零 error。影響現行 4 齣新加坡場次。

## [v1.30.1] - 2026-07-03 21:18
### 修正 — 功能完整度 R9:persona 對低資料使用者無意義 + 英文複數瑕疵
- **根因**:`personality()` 無最低資料門檻→0 齣顯示「你在 0 個地方看過戲，幾乎每齣都嚐鮮」、1 齣「你在 1 個地方看過戲，幾乎每齣都嚐鮮」(只看過一齣卻說「每齣都嚐鮮」),新使用者剛登入看到很尷尬。實測 mock 0/1/2 齣確認。
- **修**:少於 3 齣回 `enough:false` + 鼓勵句(「再記錄 N 齣，這裡就會浮現你的劇迷輪廓」/「Log a few more shows…」);me.html+u-view.js 渲染端條件處理(不硬算類型);3+ 齣才顯示真 persona。實測 0/2 齣→鼓勵句、3/5 齣→真類型,三語零 error。
- 順修:英文 `p_blurb_local_place` 的「in {n} place(s)」偷懶複數(該分支 n 恆為 1)→改「You've kept your theatre-going close to home」;u-view persona 渲染補 esc()。
- 註:v1.30.0 刪帳號 migration 使用者已執行 ✓,刪帳號功能完整生效。

## [v1.30.0] - 2026-07-03 21:09
### 新功能 — 刪除帳號(high-level 一級缺口:GDPR 被遺忘權+基本信任)
- **背景**:高階檢查發現使用者用 Google 登入交了資料,卻**無法刪除自己的帳號**——GDPR「被遺忘權」硬要求+要登入的產品該有的退出機制,是切正式域名前的紅線。
- **前端**(已上線):帳號設定 modal 加「危險操作」區+「刪除我的帳號」按鈕(紅框、需輸入 username 二次確認防誤刪)→呼叫 `delete_my_account` RPC→登出+清本機+回首頁。三語(簡中 OpenCC 自動轉),零 error。
- **⚠️ migration 待執行**:`supabase/add_delete_account.sql` 需在 Supabase SQL editor 貼上執行,按鈕才會真的生效(未執行前點刪除會顯示「刪除失敗」)。RPC 為 SECURITY DEFINER 但只刪 auth.uid() 本人:sightings/profiles/handle_aliases(cascade)+ venues.created_by 設 null(保留社群劇院)+ auth.users。

## [v1.29.13] - 2026-07-03 21:03
### 修正 — 隱私/安全 R7:公開頁自訂海報可被當追蹤信標(high-level 檢查延伸)
- **根因**:公開頁 u.html 的自訂海報主圖走 wsrv 代理(訪客 IP 不外洩,正確),但 `posterFull` 保留了**原始未代理 URL**——proxy 失敗時 onerror 會讓「訪客」瀏覽器直連海報主機、點圖也開原始 URL。攻擊情境:某人拿自己的公開頁當追蹤信標(設惡意海報 URL+讓 wsrv 失敗)→蒐集所有瀏覽者 IP,牴觸本站「不追蹤」立場。主圖也缺 referrerpolicy(洩漏 profile URL 給海報主機)。
- **修**:u-view.js 的 posterFull 一律改走 resolvePoster(=proxyImg),公開頁**不再保留任何原始自訂 URL**(唯一使用點 L52 已經 proxyImg);主海報 img 補 `referrerpolicy="no-referrer"`。owner 自己的 me.html 不受影響(自己的 URL,無第三方風險)。實測 u.html 三語載入乾淨、無 raw override 洩漏點、零 error。
- 註:owner 頁點圖看原圖的 full-res 在公開頁改為看 600px 代理圖(可接受;公開頁本就不該曝露原始 URL)。

## [v1.29.12] - 2026-07-03 20:54
### 修正 — 功能完整度 R6:guide 語言偏好不持久(唯一沒讀 mm_variant 的內容頁)
- **根因**:about/me/privacy 都設 `MM_USE_LANG_PREF` 讀 localStorage `mm_variant`,唯獨 **guide.html 沒設**→英文使用者直開/收藏/被分享 guide.html(無 ?hl=)會被丟回中文(navigator 判定),與全站不一致。從 /en/ 首頁點 nav 因連結帶 ?hl=en 沒事,但脫離該路徑就露餡。
- **修**:guide.html 補 `window.MM_USE_LANG_PREF=true` + head OpenCC 偵測腳本加 mm_variant 分支(比照 me.html)。實測:英文偏好直開 guide(無hl)現在正確顯示英文,零 error。
- 另驗(皆正常,無需改):theatres.html 5165 劇院全有座標、搜尋用 v.search 欄(簡體/日文/英文全名皆可,如「Aichi Prefectural Art Theater」找得到)、空結果乾淨;index 分類 pill 篩選正常(德奧 688→10);編輯既有紀錄 8 欄全往返;公開頁 u.html 與 me.html 對等+隱私 note/price/seat 伺服器層遮罩。

## [v1.29.11] - 2026-07-03 20:40
### 修正 — 功能完整度 R3:劇院搜尋補簡體/別名(同 R2 根因,延伸到 venue)
- **根因**:劇院 combo 只比對顯示名(cnorm 僅處理 臺→台/灣→湾),沒用 catalog venues 的 `search` 欄(含簡體、日文、別名)。→ 簡中使用者打簡體劇院名(爱知县艺术剧场 vs 存的 愛知県芸術劇場)搜不到。
- **修**:MVENUE 帶上 `_s=v.search`;setupCombo 新增 `opts.searchOf`——比對時取 max(顯示名, searchOf 分數);mVenue combo 傳入 searchOf。實測 5048 劇院全有 search 欄,簡體「爱知县艺术剧场」修前=0 命中、修後=命中愛知県芸術劇場,零 error。
- 已知限制(誠實標註,未修):cities 為純英文鍵、無 search 欄→簡中打中文城市名搜不到;但城市下拉是英文可點選+選劇時自動帶入,影響低。

## [v1.29.10] - 2026-07-03 20:33
### 修正 — 功能完整度 R2:搜尋漏掉 catalog 的 search 欄(簡體/別譯搜不到)
- **根因**:me-input 的搜尋 INDEX 只 norm(en/zh/group/首字母),**沒用 catalog 已備好的 `search` 欄**(含簡體名、日文名、別譯)。→ 簡中使用者打簡體劇名(女巫前传、悲惨世界、歌剧魅影、狮子王)或別譯(魔法坏女巫)**搜不到**,只有繁體/英文找得到。guide 宣稱「中英文搜尋都行」對簡中族群其實跛腳。
- **修**:buildCatalog 把 `t.search` 帶進 CATALOG,INDEX hay 併入 `norm(w.search)`。實測:女巫前传/魔法坏女巫/悲惨世界/歌剧魅影/狮子王/les mis 全部找到,繁體英文不受影響,零 error。

## [v1.29.9] - 2026-07-03 20:28
### 修正 — 功能完整度 R1:貨幣選單名稱未 i18n(loop 功能驗收)
- **guide 逐句對碼(你最在意的)**:▶ 自動逐月播放=真(time-play+playTimer)、每一齣附售票連結=100%(1721/1721)、多數有官方網站=63% 成立、表單日期/評分/座位/心得四欄齊、♥/三檢視/統計/分享隱私/Google 登入前面驗過——**guide 無空頭宣稱**。
- **抓到 i18n 缺口**:貨幣選單第三欄名稱 `CUR_INFO[].name` 寫死繁中(新台幣/英鎊/日圓…),月份有 EN 分支但貨幣沒有→**英文使用者在英文介面看到繁中貨幣名**、簡中使用者看到繁中(非簡中)。加 `CUR_EN`(18 幣英文名)+`CUR_SC`(與繁中相異的簡中名:英镑/日元/新台币/港币…)+`curName()` 依語言選;兩處貨幣選單改用。實測三語正確、零 error。
- 另查:themusicalmap.com 未上線(無 CNAME+憑證失敗)、Worker 未部署(灰雲不跑)、CI 健康(每日自動更新,1721 筆新鮮)、核心分享功能可用(?u= 直連)。

## [v1.29.8] - 2026-07-03 20:07
### 修正 — 日期選擇邊界:不合法日期(2/31)不可選(loop 體檢)
- **根因**:日期「日」下拉硬編碼 1–31,不隨月份調整→可選出 2/31、4/31 等不存在日期。存 DB 時 Postgres `date` 欄位會拒絕(out of range)→雲端寫入失敗→(R3 後)顯示通用「儲存失敗」toast,使用者無從得知是日期問題,死路。
- **修**:新增 `daysInMonth(y,mo)`(委派 JS Date,閏年/世紀閏年自動正確:2024/2=29、2023/2=28、2000/2=29、1900/2=28)+ `syncDayOptions()` 依年月重建「日」下拉,只列合法天數;原選日超出新月上限(31→2月)自動夾到最後一天。兩表單(手動新增 mDay/詳情編輯 dDay)的年月 onchange 都接上,編輯既有日期時初始也同步。
- **驗證**:純邏輯 9 case 全對(含世紀閏年)、DOM 實測 2024/2 從 31 夾到 29、全站回歸 0 error。

## [v1.29.7] - 2026-07-03 19:59
### 修正 — 無障礙 R13:自訂 modal 的 focus trap + dialog 語意(loop 體檢)
- **背景**:詳情視窗是原生 `<dialog>`(自帶焦點陷阱+Escape),但**分享/帳號設定 modal 是自訂 `<div>`**——Escape 有處理,但開啟時焦點沒移進去、Tab 會跑到背景遮罩後的頁面控件、且無 `role="dialog"`(螢幕閱讀器不知是彈窗)。首次登入強制 onboarding(必設帳號)這個關鍵流程尤其受影響。
- **修**:兩張卡加 `role="dialog" aria-modal="true" aria-labelledby`;新增 `trapModal()`——開啟時焦點移入第一個可聚焦元素、Tab/Shift+Tab 在卡片內循環,關閉時解除。三個開啟路徑(maybeOnboard/openShare/openAcct)都接上,close/closeAcct 解除。實測靜態 aria 屬性齊全、focus DOM 正確、全站回歸 0 error。
- 未動:log modal 內是 me-input iframe(自管焦點,跨 iframe 陷阱複雜且它有 Escape+背景關閉),維持現狀。

## [v1.29.6] - 2026-07-03 19:49
### 修正 — 資料儲存邊界:票價欄輸入淨化 + localStorage 配額防護(loop 體檢)
- **票價欄無驗證**(`inputmode=decimal` 的文字框,非 type=number):可打字母/多小數點/負號→存 DB 時 `+price` 得 NaN 靜默存 null(使用者輸入消失)、或存成負價。加即時淨化 `sanitizePrice`(只留數字+單一小數點、去負號、上限 12 字),兩處價格欄綁定改走 `bindField`。playwright 實測 6 種惡意輸入(abc/-50/12.3.4/1e5/12abc34)全正確淨化。
- **localStorage 配額防護**:me.html syncFromCloud 的 `setItem('mm-log')` 原無獨立 try(收藏極多時 QuotaExceeded→被外層當「讀取失敗」誤報)。改獨立 try/catch:雲端已抓到資料、渲染照常,僅無法離線快取,不擋流程、不誤報。
- 全站 18 組回歸 0 error。

## [v1.29.5] - 2026-07-03 19:42
### 修正 — 320px 窄機溢出 + 超長字串容錯(loop 體檢)
- **guide 在 320px(iPhone SE/小 Android)橫向溢出**:header 的 brand+繁简EN+「我的音樂劇」CTA 擠不下→CTA 頂出。加 ≤360px 規則(brand 15px/img 25px、hl-pick padding 收緊、CTA 12px)。實測 guide 三語 + index/me/about/privacy/terms/theatres/u 全數 320px 無溢出。
- **超長字串容錯**:注入誇張長劇名(100 字)+超長劇院/城市名 → me 頁統計卡/海報牆/hero 未撐破(既有 text-overflow/word-break 生效),確認良好。

## [v1.29.4] - 2026-07-03 19:36
### 修正 — 圖片載入失敗 fallback 補完(loop 體檢)
- **背景**:海報牆/詳情/popup 的 `<img>` 都有 onerror→優雅退回(色塊/文字),但**清單檢視縮圖 + 輸入端「確認/最近加入」縮圖(5 處)無 onerror**——自訂海報貼壞 URL(使用者可貼任意網址)時顯示破圖 icon。
- 修:5 處縮圖加 `onerror`(me.html 清單 this.remove()、me-input 三處 this.remove()/visibility:hidden)→壞 URL 降級為容器底色,無破圖。playwright 實測:壞 URL 的清單縮圖 img 被移除(imgLeft:0)、海報牆退回文字 fallback、零錯誤。
- 未動:地圖 marker/側欄縮圖用 CSS background-image(無法偵測載入失敗),但那些吃 catalog 官方 URL(可靠),非使用者自訂;風險低。全站 18 組回歸 0 error。

## [v1.29.3] - 2026-07-03 19:27
### 修正 — 行動裝置審計 R9:me.html 手機橫向溢出 + 觸控目標(loop 體檢)
- **me.html 375px 橫向溢出**(scrollW 425>375,個人頁左右晃):header nav(語言/地圖首頁/使用說明/主題/分享/登出)擠不下→登出鈕頂出視窗。修:≤560px 隱藏兩個文字導航連結(比照首頁,footer 已有)、nav 允許 wrap、chips max-width 限制。實測 scrollW 375=375 無溢出。
- **觸控目標補到 ≥24px 底線**:me 頁主題色點 19×19→26×26、語言 pill 高 23→29(inline style 需在 me.html 內覆寫,me-v2.css 因載入順序壓不過);pin 31px、其餘達標。
- 掃描結論:index/guide/about/privacy 五頁手機無橫向溢出;index tagchip(22px)等次要篩選控制未動(非溢出、非主操作)。

## [v1.29.2] - 2026-07-03 19:17
### 修正 — 全站 console error 回歸掃描(0 錯) + SEO/social meta 補齊(loop 體檢)
- **回歸掃描**:18 個「頁面×語言×互動(me 切三檢視)」組合監聽 pageerror/console error → **全 0**,確認 R2-R7 改動無新副作用、TDZ 修乾淨。
- **SEO/social meta 補齊**:掃出缺漏並補——首頁補 og:image(主要分享網址原本社群分享無縮圖);guide/about 補 twitter:card;privacy/terms 從「只有 title」補齊 description+og:title/desc/image/url+twitter:card(可索引內容頁原本 Google 摘要差、分享無預覽);theatres 補 og:*+twitter;u.html 靜態補 description。重掃:所有可索引頁 meta 完整。
- 保留正確的「缺」:me=noindex 登入閘(不需 meta);u 的 canonical/og:url 由 Cloudflare Worker 依 handle 動態注入(靜態不可寫死,否則所有公開頁指向同一 URL)。

## [v1.29.1] - 2026-07-03 19:08
### 修正 — 穩定度審計 R7:登入閘卡死防護 + 撈到並修 TDZ 錯誤(loop 體檢)
- **登入閘卡死防護**:`getSession()` 原無 `.catch()`(reject→unhandled)、`syncFromCloud` 的 sightings select 原無逾時(網路 hang 非 error 時→永卡「同步中」)。修:getSession 加 catch→失敗回登入頁;select 加 12s `abortSignal` 逾時;同步失敗畫面加「重試」按鈕(gate_retry 三語),不再只能重整。實測新訪客路徑正常顯示登入頁、abortSignal 為有效方法。
- **意外撈到 TDZ 錯誤(v1.27.2 我自己引入的 regression)**:R2 把 hero「最新一場」改成 `esc(cityName(...))`,但那段 IIFE(line ~284)執行時 `CITYZH`(const,line 454)還在暫時死區→`ReferenceError: Cannot access 'CITYZH' before initialization`,**hero(最新一場+大數字)整塊從 v1.27.2 起靜默掛掉**(console 有錯但畫面只是少了那行)。修:CITYZH/cityName 宣告上移到 hero 之前,刪除原處重複宣告。實測 hero 恢復「最新一場 Hadestown 倫敦 · 2025.02」(中文城市名回來)、零 pageerror。

## [v1.29.0] - 2026-07-03 18:57
### 效能 — 首頁側欄縮圖延遲載入(loop 體檢;首頁 load 21.5s→1.7s)
- **根因**:側欄 688 個劇目的縮圖用 CSS inline `background-image`(原生 lazy 管不到),渲染時**全部立即載**——實測首屏抓 ~115MB 圖片(jpg 253 檔/57MB+png 80/12MB+gif 19/6MB),`load` 事件到 **21.5 秒**。
- **修**:縮圖改寫 `data-bg` + IntersectionObserver(rootMargin 300px 提前預載),只載捲進視野附近的;不支援 IO 的瀏覽器降級為立即載。地圖 marker/hover 卡維持原樣(Leaflet 只渲染可見的、hover 才載,本就不重)。
- **實測(重量對比)**:load 21516ms→1746ms(**-92%**);jpg 253檔/57MB→7檔/2.5MB;png 80檔/12MB→4檔/163KB;首屏總傳輸 ~115MB→~7.5MB(**-93%**)。截圖確認可見縮圖照常顯示、功能無損。

## [v1.28.2] - 2026-07-03 18:49
### 修正 — 無障礙審計 R5:月份滑桿與海報 marker 缺可及名稱(loop 體檢)
- **月份時間軸滑桿** `#time-range` 原本無任何名稱→螢幕閱讀器只念「slider」+ 0-36 數字,不知是什麼、也不知選了幾月。加 `aria-label`(月份時間軸/Month timeline)+ 動態 `aria-valuetext`(隨 setMonth 更新為「2026年07月」),閱讀器現在念得出月份。
- **海報 marker** 是背景圖 div,原本無可及名稱→閱讀器讀不到是哪一齣、滑鼠停留也無 tooltip title。marker 加 `title`/`alt`=「劇名 · 城市 · 國家」+ `keyboard:true`(Leaflet 鍵盤聚焦)。實測:掃描的 noName/inputNoLabel 全清空,marker title 內容正確。
- 掃描結論:五頁 img alt、按鈕可及名稱、role=button 鍵盤、input label、html lang 其餘皆合格,無新問題。

## [v1.28.1] - 2026-07-03 18:42
### 修正 — 穩定度審計 R4:刪除/最愛的雲端失敗一致性(loop 體檢;延續 R3 資料完整性)
- **刪除復活 bug**:`mmDeleteShow` 的 `.delete()` 失敗是回傳 `{error}` 不拋例外(try/catch 抓不到),原碼照樣刪本機+reload → 雲端還在 → 下次 syncFromCloud 那筆「復活」。修:先確認雲端刪成功(檢查 error)再動本機,失敗顯示「刪除失敗，雲端未更新…」alert 且本機不動。playwright e2e(攔 DELETE→500)實測:失敗時 logLen 維持不變、alert 觸發、本機未誤刪。
- **♥ 最愛失敗還原**:fav 雲端 update 失敗原本只 console.warn,本機/UI 已翻 → 下次 sync 靜默還原,UI 說謊。修:失敗時本機翻回+`mmRevertFav` 就地把卡片 ♥ 還原(不重刷),UI 與雲端保持一致。
- delete_cloud_fail i18n 三語。

## [v1.28.0] - 2026-07-03 18:34
### 修正 — 穩定度審計 R3:雲端寫入失敗導致「靜默永久丟失紀錄」(loop 體檢;此輪最嚴重)
- **根因**:me-input 新增/編輯音樂劇時,雲端寫入失敗**只 console.error 後照常往下走**——顯示「🎭 已蓋章!」成功 toast、只存 localStorage(sid=null)。下次 session 的 syncFromCloud 用雲端資料覆蓋 localStorage → **這筆使用者以為存好的紀錄永久消失**。對「永久保存你的觀劇紀錄」這個產品核心承諾是最致命的 bug。編輯路徑同理:失敗仍顯示「已更新」,下次同步把編輯蓋回舊值。
- **修**:cloudUpsert 回傳的 error 現在會擋下流程——不蓋章、不關窗、儲存鈕重新啟用,顯示「⚠ 儲存到雲端失敗，請檢查網路後再按一次『加入』（先別關閉，以免這筆遺失）」(三語);本機草稿保留不清,使用者可直接重試。playwright e2e(攔截 sightings POST/PATCH→500)實測:失敗時 logLen 維持 0、顯示錯誤而非成功。
- 順修 R2 漏網:me.html 刪除復原 toast 的劇名補 esc()。

## [v1.27.2] - 2026-07-03 18:27
### 修正 — 穩定度審計 R2:me.html 自渲染 HTML 未跳脫(loop 體檢)
- 實測(注入含 `<b>`/`"`/`<hr>` 的劇名/劇院/城市):海報卡標題、清單、統計榜、護照戳章 SVG、hero「最新一場」全被當 HTML 解析→**版面被打壞 + self-XSS**(手動新增的自由文字劇名/劇院/城市/座位)。u-view.js(公開頁)早有 `esc()`,me.html 這條路徑沒有。
- 修:me.html 補 `esc()` helper,套進所有 innerHTML 內插使用者資料處(posterEl/renderLog/renderPassport+stampSvg/barList/badges/citylist/pins/newest/detail-dl,共 ~18 處);aria-label 原只跳脫 `"` 改用 esc 涵蓋 `<>`。playwright 注入實測:`<b id=pwned>` 標籤不再被解析(0)、`<hr>` 不再注入(0),顯示為字面文字。
- 註:危害有限(資料是使用者自己輸入,非他人)但破版是真的;公開頁 u.html 讀他人資料的路徑本就安全。

## [v1.27.1] - 2026-07-03 18:11
### 修正 — 穩定度審計 R1:首頁資料載入失敗的誤導空狀態(loop 體檢)
- 實測(block data fetch):失敗時顯示「沒有符合的音樂劇，試試清除搜尋或取消篩選」+「本月上演：0 部音樂劇」——誤導使用者;根因=錯誤訊息寫進**早已不存在的 #data-note**(移除頁尾時留下的黑洞)。
- 修:`LOAD_FAILED` 旗標 → 空狀態顯示「演出資料載入失敗/請檢查網路連線後重新整理頁面」(三語,原文案是開發者向的「見 README」也一併改掉,dev 提示移 console);計數列不顯示假「0 部」。
- 同輪驗證通過:me.html 快取為壞 JSON/形狀錯誤 → 安全 fallback 範例、零 JS 錯誤 ✓。

## [v1.27.0] - 2026-07-03 17:59
### 新功能 — 場館英文名第二批完成(124 館;agent 全量查證) + UI 四修(使用者指示)
- **場館英文名第二批**:中國 119 館(53 高+19 中信心採用,47 家小型沉浸式劇場查無官方英文誠實留空)+其他國 58 館(台 20/俄 14/日 12/希 9/匈 2/義 1;28 高+20 中,10 留空)。合併 103 新條目+14 補空 en 進 cn/tw/jp/eu_venues;順手修 13 筆「en 欄被塞中文」的舊髒資料(模糊比對草稿補回 7 筆)。**catalog 缺英文名 227→75**,剩餘全為查證後無官方英文名者,零編造;en 欄 CJK 殘留歸零。SYNC_VER 6→7。草稿含來源:`data/_venue_en_draft2_{cn,row}.json`。
- **♥ 不重刷**(使用者抓 UX):標最愛改就地切換(按鈕亮起+卡片 ♥ 即時增減),本機快取即改、雲端背景同步;統計/徽章數字下次載入跟上。
- **首頁補「關於」入口**(使用者抓漏):地圖 attribution 列改為「關於 · 隱私權 · 條款」三語。
- **統計卡 4+3 一排**(使用者嫌 2×2 留白多):statgrid 改 12 欄制,四張榜單卡一排+三張圖表一排;≤1100 降 2×2、手機單欄;guide 統計截圖三語重拍(1300px 新版型)。
- **共用頁尾**:guide 款 footer(左標語+右金色連結)套到 about/privacy/terms(`.site-foot` 入 style.css),三頁與 guide 一致。
- **About 擺放調查(agent 實查 17 個獨立開發者產品)**:indie 主流=無正式 About 或放 footer(頂部 nav 僅 4/17);最有效做法=首頁/guide 一句第一人稱引言連到 About——已在 guide 結尾加「這個網站由一位音樂劇迷獨立打造——背後的故事 →」(三語)。

## [v1.26.0] - 2026-07-03 17:32
### 新功能 — ♥ 最愛功能 + 主題減至三色 + 頁名軟化 + 簡中手寫層(使用者多點指示)
- **♥ 最愛(極簡版)**:sightings 加 fav 欄(⚠ **migration `supabase/add_fav.sql` 待使用者在後台執行**,含 public_sightings 重建帶 fav);海報卡 hover 動作區加 ♥ 切換(標了亮粉色),同步雲端+本機快取後 reload;公開頁 u.html 一併顯示;SYNC_VER 5→6;guide 海報牆文案恢復「點卡片上的 ♥」(現在是真功能了)。輸入表單不加欄位(保持簡單)。
- **主題色 5→3**:移除 neon/deco 兩色(使用者指示);曾選過的使用者由 no-flash script 正規化回 midnight(me/u/me-input 三處)。
- **頁名軟化**:「使用說明」→「怎麼使用」、「關於」→「關於本站」(使用者嫌生硬;en Guide/About 本就自然不動);全站 nav/footer/title/eyebrow 同步。About 維持 footer 級入口(業界慣例,頂部 nav 留功能項)。
- **重複資訊收斂**:About「資料哪裡來」段的免責與分潤細節與使用條款重複→縮為一句「詳見使用條款」;其餘頁間僅一句話級輕度重疊(guide b4 vs privacy §2),保留。
- **簡中手寫覆蓋層(HANS_OVERRIDE)**:OpenCC 轉字+CN_FIX 轉詞後句式仍台灣腔;mm-strings 新增 build 後覆蓋機制,About 全頁改大陸語感手寫(「放到了一起」「愛蹲 Stage Door」「乾脆自己動手做一個」);短 UI 標籤仍走自動轉換。About 頁字型補 Noto Serif TC+簡中動態載 SC(修 h1 忽粗忽細,同 guide 病因)。
- 註:場館英文名第二批 agent 因 Claude 月費用上限中斷,待額度恢復重跑。

## [v1.25.1] - 2026-07-03 16:54
### 調整 — 隱私權政策補 email 通知條款(使用者指示:一開始就該寫)
- §2 新增段落(三語):可能不定期以 email 通知重大功能更新/帳號相關服務異動、每封附退訂方式、可來信停止;明確排除第三方廣告與提供他人。為日後電子報/功能通知預留合法基礎。
- 另:Supabase migration `fix_display_name_email_leak.sql` 使用者已於後台執行完成 ✓(待辦劃掉)。

## [v1.25.0] - 2026-07-03 16:47
### 新功能 — About 頁上線(使用者提供真實動機)
- `about.html`(三語,legal 骨架+serif 大標):四段式——定位/為什麼做(使用者親述:地圖迷×劇迷×Stage Door,想永久收藏觀劇紀錄找不到平台就自己做,做了才發現全球多語音樂劇市場的潛力想幫忙推廣)/這裡有什麼/資料哪裡來+聯絡。
- 接入:guide/privacy/terms/me/u footer 加「關於」連結(nav_about 三語鍵);sitemap 收錄;llms.txt Key pages 補 About。頂部 nav 維持精簡不放。
- 定位說明:傳統 SEO 直接效益≈0(無搜尋量),價值在 E-E-A-T 信任信號與 AI search 可引用自述(與 llms.txt 互相印證)。

## [v1.24.7] - 2026-07-03 16:30
### 調整 — llms.txt 更新(AI search 自述檔過時)
- 雙語→三語(補简体中文與三語網址);Key pages 補 guide(How it works)與 My Musicals(海報牆/護照/統計/自訂海報連結/公開分享頁);theatres 註明「暫不在導覽但可直達」。About 頁討論結論:傳統 SEO 直接效益≈0、AI search 有實質但不可量化的幫助;llms.txt 先行更新,About 待使用者提供「為什麼做」動機再寫。

## [v1.24.6] - 2026-07-03 16:25
### 新功能 — guide 自訂海報/連結獨立賣點 section(使用者指示:單獨列,不埋段落)
- 從 how_b1_p 抽出,新 section「獨家/海報與連結，都能換成你的」插在表單與統計之間,配專屬截圖(Wicked 表單:自訂海報網址+即時預覽縮圖+官網連結,三語各一張,`build/gen_guide_custom.cjs` 入 repo);統計 row 改 flip 維持交錯。三語驗證 6 張截圖皆載對應語言版。

## [v1.24.5] - 2026-07-03 16:16
### 調整 — me 頁「關於你」+ footer 去開發感 + guide 補自訂海報/連結功能(使用者三點指示)
- 「關於這位劇迷」→ me 頁改「關於你」(About you);公開頁 u.html 看的是別人,保留「關於這位劇迷」——拆成 sec_you_me/sec_you 兩鍵。
- me 頁 footer 兩句開發感文案(「海報牆與護照…兩種看法」「目前顯示的是範例紀錄…」)移除,只留導航連結;後者對已登入者本來就是錯的(顯示的是真資料不是範例)。
- guide「加入一齣」補獨家功能一句(對碼確認存在:posterOverride+url 欄):「每一齣還能自訂海報圖與連結：貼上你最愛的那版劇照，或當年的節目頁。」三語。

## [v1.24.4] - 2026-07-03 16:14
### 資安 — 修 display_name 洩漏完整 email 的 fallback(使用者「你有存嗎」追問挖出)
- **email 儲存現況(對碼確認)**:auth.users 系統表存 email(登入辨識必要);前端只在記憶體用 @ 前綴產生網址名稱建議,自建表(profiles/sightings)無 email 欄。
- **地雷**:`handle_new_user()` 觸發器在 Google 帳號無 full_name 時把**完整 email**寫進 `profiles.display_name`——而 display_name 是公開頁標題,設公開後 email 會被公開展示(機率低但設計錯誤)。
- 修法:fallback 改 `split_part(email,'@',1)`(@ 前綴);附一次性 UPDATE 修正既有恰等於本人 email 的 display_name(精準比對,不動自訂名稱)。schema.sql 源頭同步修。
- ⚠ **migration 待套用**:`supabase/fix_display_name_email_leak.sql` 需在 Supabase 後台 SQL editor 執行(本機無 CLI)。

## [v1.24.3] - 2026-07-03 16:02
### 調整 — 頭像說法精確化 + 「設定公開」用字(使用者兩點指示)
- 頭像:說明機制後改為「附帶但不使用」的準確表述——Google 基本資料授權把名稱與頭像綁定提供、無法只取名稱(顯示名稱是公開頁標題預設值,必須要);本站不使用、不顯示、不存自有資料表。gate_secure/how_b4(三語)改「名稱與 email（Google 授權會附帶頭像，本站不使用）」;privacy §2 詳述綁定機制。
- 「到『分享』打開公開開關」→「到『分享』設定公開」(使用者用字)。

## [v1.24.2] - 2026-07-03 15:56
### 修正 — 文案宣稱 vs 實際功能全面對碼稽核(使用者要求;Fable 5 逐句對照 code/DB/資料驗證,未派 agent)
- 稽核方法:三語所有「功能宣稱」句逐一對照 me.html/u-view/schema.sql/shows.json。屬實的不動(「每一齣都附售票連結」=1721/1721 實測、改名舊網址轉新=RPC 實證、「筆記永遠不上公開頁」=遮罩 RPC 實證、護照每場一章、統計各卡、時間軸、affiliate 揭露等)。
- **修 3 類不實/過時**:(1) how_b3_p「公開頁在登入取名時就準備好了——傳給朋友就行」過度宣稱——schema `is_public default false`、onboarding 只設名字不開公開,朋友點開是 404;改為「到『分享』打開公開開關」(三語)。(2) me-input footer「資料存在瀏覽器(localStorage)」是雲端同步前的舊文案;改「紀錄存進你的帳號、跨裝置同步」。(3)「只讀取名稱與 email」六處漏列頭像——Google OAuth 基本授權含 avatar(存於 auth 中繼資料,雖未顯示);gate_secure/how_b4/privacy §2 三語補「與頭像」並註明目前未顯示。
- 簡中七頁迴歸全過。(v1.24.1=查證草稿檔補入 repo,無獨立條目)

## [v1.24.0] - 2026-07-03 15:48
### 新功能 — 場館官方英文名補齊第一批(38 館;agent 官方來源逐一查證)
- 現行檔期引用最多的 40 個缺英文名場館:agent 逐一查官網/維基/官方售票頁,23 高信心+15 中信心採用、**2 筆查無官方英文名誠實留空不編造**(包河凤凰剧院/星空间28号);草稿含來源網址存 `data/_venue_en_draft.json` 供追溯。
- 合併進區域對照檔:`cn_venues.json` +28 新條目、+10 補既有空 en(诸暨西施/衢州保利等其實早有條目但 en=""——catalog 沒英文的另一半根因);`tw_venues.json` +2(臺北國家戲劇院=National Theater、城市舞台=Metropolitan Hall);`jp_venues.json` +1(Pia Arena MM)。
- 重產 venues_catalog:實測 38 館 name 皆為「English 原文」;全 catalog 缺英文名 227→190(剩餘多為引用少場館+俄/希臘,後續批次)。SYNC_VER 4→5(catalog 顯示資料更新)。
- 防呆備註採納:保利上海城市剧院=Shanghai City Theatre(≠上海保利大劇院);臺北國家戲劇院官方英文=National Theater(NTCH 戲劇廳);城市舞台英文不含「藝文推廣處」機關名。

## [v1.23.1] - 2026-07-03 15:43
### 修正 — guide 移除「標最愛 ♥」不實文案(使用者抓到)
- 「最愛的標上 ♥」寫的是**不存在的功能**:♥ 只在 demo 範例資料上渲染,真實使用者無處可標(輸入表單無此欄、sightings 表無此欄、同步一律 fav:false)。文案與 alt 移除該句(三語)。
- 註:demo 海報牆截圖上仍看得到範例卡的 ♥;若要讓它成真功能(DB 加 fav 欄+表單愛心+同步)或把 demo 的 ♥ 也拿掉,待使用者決定。

## [v1.23.0] - 2026-07-03 15:34
### 新功能 — guide 截圖裁切總修 + 劇院英文名回 catalog 查(使用者三點抓錯)
- **截圖裁切通盤修正**(使用者連抓海報牆/統計卡被切):根因=用固定高度裁而非元素邊界。海報牆改寬版 1440(7 欄)+「第 2 排卡片底部」精準邊界=14 張完整海報零裁切;統計卡改拍完整 .statgrid 元素(7 卡+圖表全入鏡);表單裁在第一筆結果底部。三語重產,修正版腳本入 repo(`build/gen_guide_wall.cjs`/`gen_guide_stats_form.cjs`)。
- **en 模式劇院名回 catalog 查官方英文名**(使用者質疑「上海大劇院/帝国劇場怎麼可能沒英文」——對,catalog 有 `Shanghai Grand Theatre 上海大劇院`,是我上一版只做字串抽取沒查表):me.html 同步時 `venueEnOf()` 以 CJK 名查 catalog search/name 對出英文,存 `p.venueEn`,**SYNC_VER 3→4** 強制全 session 重同步;u-view 同邏輯 runtime 處理;「上海大劇院 Lyric Theatre」正確變 Shanghai Grand Theatre(不再誤用廳名)。demo 資料 6 筆中文館名補官方英文(Imperial Theatre 帝国劇場 等),en/zh 雙模式實測正確。
- **catalog 缺英文名盤點**(agent 全量掃描):5157 館中 **227 館 name 無英文**(中國 166/台灣 22/俄 14/日 13/希 9),**180 館正被現行檔期使用**(含臺北國家戲劇院、武汉琴台大剧院等一線館);根因=`cn_venues.json` 等區域檔僅百餘筆,查無 en 即落回原文;正確補法=往 `data/cn_venues.json`/`tw_venues.json` 等補 `{native,en}` 條目(gen_catalog 邏輯不用改)。**資料補名待辦**,見下一步。
- 修自埋雷:venue 對映 IIFE 先於 `const EN_UI` 宣告執行會 TDZ 錯誤讓登入者看到範例資料——改行內判斷(commit 前抓到)。

## [v1.22.2] - 2026-07-03 15:18
### 調整 — 英文模式在地化三連修 + guide 開場句去推銷味(使用者指示)
- **en 模式不顯示中文劇名**:me/u 海報卡/清單/詳情 modal 的 zh 行以 CSS 隱藏(me-v2.css,`html[lang="en"]`);me-input 搜尋結果/城市卡/最近加入同步;toast/確認刪除等 JS 組字改語言感知(`PN()` helper,en 用英文名)。實測 en 頁中文劇名 0 個、繁中頁 22 個不變。
- **en 模式劇院名抽英文**:`venueZh` 原本 en 直接回傳原字串(「National Taichung Theater 臺中國家歌劇院 大劇院」整串上榜);改為抽非 CJK token(→「National Taichung Theater」),**沒有英文名的本地館(上海大劇院/帝国劇場)保留原文**(使用者的「另當別論」規則);_cjk 已含假名+諺文,「샤롯데씨어터 Charlotte Theater」→「Charlotte Theater」。六組真實字串單元驗證通過。
- **guide Part1 開場句去推銷味**:「想看哪一齣，直接連過去訂票」(第一句就賣票太顯眼)→「放大、拖一拖，看看世界哪個角落的燈正亮著」;en 同步(lights on 劇場意象);訂票資訊仍在 a2 專段。

## [v1.22.1] - 2026-07-03 15:07
### 文案 — 英文 bridge 句採使用者版本
- how_bridge:「Don’t leave them…」→「Don’t leave **memories** all alone in the moonlight — stamp them in.」——them 原無明確先行詞,memories 讓句子自立且直接點題 Cats〈Memory〉原詞。

## [v1.22.0] - 2026-07-03 15:03
### 新功能 — guide 截圖三語各自產製 + 海報牆主視覺 + 英文歌詞彩蛋(使用者指示)
- **截圖分語言**:原本 assets/guide/*.webp 只有繁中一套、三語共用(使用者抓到)。改為 `assets/guide/{zh-hant,zh-hans,en}/` 三套 ×5 張(map/popup/form/stats/wall),全部用去 emoji 後的最新 UI 重截(playwright:美東視角地圖含英文版「Jul 2026」時間列、Wicked popup、phantom/歌劇魅影搜尋表單、統計卡、海報牆);guide 依 `MM_HL` 動態載對應語言,靜態預設繁中(SEO/no-JS)。產製腳本入 repo(`build/gen_guide_shots.cjs`+`guide_shots_to_webp.py`)。
- **海報牆進 guide 當 Part 2 主視覺**(使用者主打):新 section「你的海報牆/看過的，掛成一面牆」＋三語文案(how_b0_*),排在加入表單與統計之前;me.html 登入頁 preview 也從統計圖換成海報牆。
- **英文歌詞彩蛋(僅英文版,中文不動)**:bridge=Cats Memory(Don’t leave them all alone in the moonlight — stamp them in.)、購票=Hamilton(Be in the room where it happens)、統計=Rent Seasons of Love(How do you measure a year? In shows, cities and stamps)、結尾=Do-Re-Mi(Let’s start at the very beginning…)、空護照=Sunday in the Park(a blank page, so many possibilities)。
- **時間軸文案修正**(使用者抓錯):滑桿 min=0 不能拉回過去→改「拖到未來的月份」;獨立成段(與海報段落空行);「按 ▶ 可以自動逐月播放，看巡演在城市之間移動分布變化」。
- app.js 曝露 `window.mmMap`(截圖/測試設視角用)。

## [v1.21.0] - 2026-07-03 14:35
### 新功能 — 全站去 emoji + 月份列語言修正 + 側欄全展開 + 文案批次(使用者多點指示)
- **全站 emoji 盤點消除**:掃描器逐檔列出 71 顆,彩色圖像式全清——統計卡 🎭🌏🏙🏛📅、徽章 🏅(含渲染層 icon 欄)、檢視切換 🖼🛂📋、👋banner、toast 🎭、⚠ 警告前綴、🔍搜尋、📍✏️🤔 表單、🌐 theatres、死鍵 🗺📊📋;功能符號改用文字字符(❤️→♥ 帶色、🗑→✕)。保留的 ★✓✗✕✎♪ 是文字符號非 emoji。順手修 u.html 徽章劇名未跳脫的 XSS 縫隙(esc)。
- **英文頁月份顯示「2026年07月」修正**:根因=原生 `<input type=month>` 格式跟「瀏覽器 UI 語言」走、不理頁面 lang;改為頁面語言格式化的 label(fmtYM)覆蓋、原生 input 透明墊底只出月曆。實測 en「Jul 2026」/中文「2026年07月」。
- **側欄多城市巡演一律預設展開**(原 >6 站折疊);使用者手動收合的重渲染時維持收合(closedKeys)。
- **文案**:建立我的觀劇護照→建立我的音樂劇護照(全站);demo Hadestown 中文名 地獄樂町→冥界;guide「各音樂劇的海報/相鄰的」「都幫你統計好了」「你的個人專屬頁面，一鍵就能分享」;how_b3_p 舊流程殘留修正(「設一個網址名稱」→「公開頁在登入取名時就準備好了」,因首次登入已強制設名);時間軸用法寫進使用說明(拖月份/▶ 播放);統計卡「最常看的音樂劇」。en 同步。
- 簡中七頁迴歸全過。

## [v1.20.4] - 2026-07-03 13:57
### 文案 — 「劇庫」→「音樂劇資料庫」(使用者指示)
- mm-strings 繁中 3 鍵(載入中/找不到/手動輸入)+mi_hint 改「音樂劇資料庫」;簡中經既有 CN_FIX「资料库→数据库」自動轉成「音乐剧数据库」,playwright 實測兩語皆正確;英文 catalogue 不變。code 註解/console 內的「劇庫」非使用者可見,不動。

## [v1.20.3] - 2026-07-03 13:46
### 文案 — 三語復查(渲染級全頁傾印)抓到的漏網之魚(使用者指示)
- **方法升級**:不只讀字典——playwright 把 21 個「頁面×語言」組合真實渲染後倒出全部可見文字逐行檢查(me.html 本機隱藏登入閘檢查閘後 demo 渲染、含分享/帳號設定 modal),另掃 7 支 JS 的非註解硬編碼中文。
- **me-input 開發殘留**:頁頂「Demo v3 · 輸入端／看呈現端」連到已不存在的 demo3-merged.html——整段移除。
- **persona 暱稱間隔號**:data.js `nick.join('・')`(日文中黑)→「 · 」(me/u 的「環球旅人 · 當代派 · 大製作控」)。
- **en persona 敘述句主詞斷裂**:'tastes lean contemporary'→'with tastes that lean contemporary'、'can’t resist…'→'unable to resist…'、'prefers…'→'partial to…',整句 appositive 鏈成立。
- mi_hint「試試:」→「試試：」、「劇目庫」→「劇庫」統一。
- 硬編碼掃描結論:u-view.js 國名字典(南韓/紐西蘭/義大利)、data.js demo 心得、app.js 平台名(寬宏/udn 售票)全為道地台灣用語,無需改。簡中 me 頁實測:繁「身分」/簡「身份」雙向各自正確。

## [v1.20.2] - 2026-07-03 13:29
### 文案 — 繁中全站台灣母語級校對(使用者指示;Fable 5 逐字典 review)
- 逐字檢查繁中三來源(gen_site zh-hant / i18n.js zh / mm-strings zh-hant + 法務頁)。整體評價:既有繁中是道地台灣用語(登入/網址/幣別/選填/非必填/一樓 H23/臺中國家歌劇院),不需重寫。
- 修正:**「身份」→「身分」**(台灣教育部標準;3 個 dict key + me.html 兩處靜態字;CN_FIX 補「身分→身份」反向詞條讓簡中維持大陸標準);日文間隔號「・」→「／」「、」「·」(哪一年／月／日、評分、座位…、劇院 · 城市);「目錄」→「劇庫」統一(與 mi_loading_lib 一致);placeholder「例 」→「例：」(4 處);「試試清除搜尋或開啟其他篩選」→「…或取消篩選」;「大多數人是在加入以前看過的劇」→「大多數人記錄的是…」。
- 簡中 7 頁迴歸重跑全過(身分→身份反向轉換生效)。

## [v1.20.1] - 2026-07-03 13:20
### 文案 — 英文全站母語級校對(使用者指示;Fable 5 逐字典 review)
- 逐字檢查三個英文來源(i18n.js en / mm-strings.js en / gen_site.mjs en)。整體評價:既有英文(Opus 4.8 寫)大multipart分道地——英式拼寫一致(theatregoer/catalogue/favourites)、劇場術語正確(Stalls/Circle/run dates)、guide 文案有水準,不需重寫。
- 修正 10 處:日文間隔號「・」混入英文(Year・month・day → Year / month / day、Theatre・City → Theatre · City);時間軸按鈕 today "Now"→"This month"(與烘焙文案一致);"No musicals match"→"No matching musicals";"No “{v}” in the catalogue"→"No results for…";"Which sensitive details to show…"→"Which details should appear on your public page?";"Fill to the day"→"Add the exact date";劇場慣用語 watch→see("See enough, and a shape emerges")、viewing→theatregoing;"Dot = a city with shows seen"→"…with shows logged";theatres tagline "musical theatres"→"musical-theatre venues"。

## [v1.20.0] - 2026-07-03 13:15
### 新功能 — 法務連結移到地圖 attribution 列(Google Maps 慣例;使用者採納建議)
- 隱私/條款從頂部 nav 移除,改進地圖右下 attribution 列(`Leaflet | © Mapbox © OpenStreetMap, 隱私權 · 條款`;app.js `addAttribution`,i18n 三語 privacy_short/terms_short)。全螢幕地圖 app 無頁尾,這是 Google Maps/FR24 的標準位置;手機版原本 nav 藏掉法務連結,現在 attribution 列看得到。
- 全站頂部 nav 精簡為:[繁简EN] 地圖首頁 · 使用說明 · [我的音樂劇],index/guide/privacy/terms 四處同步;法務頁互連與 guide/me/u 的法務連結留在各自 footer。

## [v1.19.3] - 2026-07-03 12:47
### 調整 — 簡中用語層補齊「每一個」簡中頁 + 我的音樂劇足跡(使用者兩點回饋)
- **CN_FIX 補上主站首頁**:簡中首頁走 js/i18n.js(與 mm-strings 不同系統),原本只有 OpenCC 逐字轉;i18n.js 加同一套詞彙層(與 mm-strings 同步維護)。新增詞條:即时→实时、隐私权政策→隐私政策、范例→示例、示范资料→示例数据;gen_site 簡中 baked 文案(title/desc/h1「实时地图」、nav「隐私政策」)同步。
- **逐頁實測**:7 個簡中頁(index/guide/me/u/me-input/privacy/terms)可見文字掃 8 個台灣用語關鍵詞全零殘留(排除 script/css 註解與劇名地名資料)。
- **「我的觀劇足跡」→「我的音樂劇足跡」**:me/u 的城市地圖 section 標題(mm-strings sec_map + 兩頁靜態字)。
- me-input title 分隔符統一「—」;me.html 品牌字空格(flex gap 拆字)已在 v1.19.2 修,本版線上覆驗。

## [v1.19.2] - 2026-07-03 12:38
### 調整 — nav 慣例排序 + guide 標題/品牌字修正 + deploy 重試(使用者三點回饋)
- **nav 排序改業界慣例**:內容頁在前、法務頁在後——地圖首頁 · 使用說明 · 隱私權政策 · 使用條款(隱私/條款是查閱型,慣例放最後或 footer;使用說明是使用者真的會點的,前移)。index 三語+guide+privacy+terms 同步,me/u footer 本來就是此順序。
- **guide 補品牌 tagline**:「此刻全球正在上演的音樂劇」比照首頁(data-i18n=legal_tagline 三語,手機隱藏)。
- **修「Musical Map」多一個空格**:根因=guide/me/u/me-input 的 `.brand` 是 flex 容器,裸文字節點 `Musical` 和 `<b>Map</b>` 被當兩個 flex item 被 `gap` 撐開;包進單一 `<span>` 修正,五處全修。三頁 header 量測 x 座標仍全等(745/860/930/1000/1084/1154)。
- **deploy 失敗信根治**:v1.17.1/v1.18.1/v1.19.1 三次失敗全是 GitHub Pages 對連續部署的暫時性 throttle(`Deployment failed, try again later`);workflow deploy job 加「失敗等 120 秒自動重試一次」,重試再敗才算真失敗。

## [v1.19.1] - 2026-07-03 12:30
### 文案 — 「劇名/shows」統一改「音樂劇名/musicals」(使用者指示)
- 首頁搜尋欄三語:搜尋音樂劇名、城市、劇院… / 搜寻音乐剧名… / Search musicals, cities, theatres…(gen_site + i18n.js `search_ph`,en 順帶 venues→theatres 統一)。
- guide:「搜劇名」→「搜音樂劇名」、en「Add a show」→「Add a musical」;輸入端搜尋框「打中文或英文劇名」→「…音樂劇名」。
- 全 repo 掃過其餘「劇名/shows」:My Musicals 內部語境(看過場次/{n} shows)不改,theatres 頁搜劇院不涉及。

## [v1.19.0] - 2026-07-03 12:25
### 新功能 — guide nav 補齊對齊 + 簡中字型/用語修正(使用者三點回饋)
- **guide.html nav 補齊**:加上 隱私權政策/使用條款/使用說明,與首頁/法務頁完全同項目同順序;header 幾何比照首頁(58px 滿版、連結 14px/600、CTA 9×16 墨丸、手機 52px);playwright 實測 index/guide/privacy 三頁 nav 各元素 x 座標完全一致(745/860/930/1014/1084/1154),跨頁切換上排零跳動。
- **簡中忽粗忽細修正**:根因=guide/me/u/me-input 載的是 Noto **TC**(繁中)字型,簡體獨有字(张/图/乐/剧/记)字型裡沒有→回退系統字混排。簡中模式動態補載 Noto Sans/Serif **SC** + `html[lang="zh-Hans"]` 字型覆寫(只簡中使用者下載);實測 body 字型=Noto Sans SC。
- **簡中用語自然化**:OpenCC 只轉字不轉詞,mm-strings 加 `CN_FIX` 詞彙後處理層(只作用 UI 字典,不動劇名/地名):登入→登录、登出→退出登录、连结→链接、每一出→每一部、建立→创建、装置→设备、帐号→账号、储存→存储、工作阶段→会话、透过→通过、币别→币种、资料库→数据库、智慧财产→知识产权、准据法→适用法律。實測 guide/me 簡中頁「免登录/创建我的观剧护照/每一部/跨设备同步」全數生效。

## [v1.18.1] - 2026-07-03 12:15
### 調整 — 「本月上演」即時計數移到搜尋欄下方(使用者指示)
- `#count` 從 header 移進側欄 `#controls`(搜尋欄下、分隔線上);header 右側只剩 nav。CSS 對應搬移(舊 `#topbar #count`/手機隱藏規則移除,新位置手機也看得到);`body:not(.ready)` 防閃規則沿用。

## [v1.18.0] - 2026-07-03 12:00
### 新功能 — 隱私/條款三語化 + 全站 nav 完全對齊(使用者回饋)
- **privacy/terms 三語內容**:接上 mm-strings 系統(`?hl=` → 主站共用偏好 `mm_variant` → navigator)——英文全文進字典(pp_*/tou_* 共 40+ 鍵)、簡中由 OpenCC runtime 轉繁中、html lang/title/meta 隨語言;語言 pills 改 `data-hl-link`(改寫 `?hl=` 留在本頁),**不再點简/EN 就跳回首頁**;head 補 hreflang 三語 alternate。
- **index 也放「地圖首頁」**:三語首頁 nav 加同位置「地圖首頁」(en: Map home/hans: 地图首页),全站每頁 nav 順序完全一致:[繁简EN pills] 地圖首頁 隱私權政策 使用條款 使用說明 [我的音樂劇]。
- **pills 永遠在 nav 最前**:guide/me/u 的語言 pills 從 nav 中段移到最前,與首頁/法務頁對齊,跨頁切換上排零跳動。
- **首頁 nav 連結帶語言**:privacy/terms 連結補 `?hl=${variant}`(英文/簡中使用者點進去直接對的語言);「我的音樂劇」連結修掉無作用的 `?lang=` 改 `?hl=`(me.html 只認 hl)。
- 驗證:playwright — privacy `?hl=en` 全英文/`?hl=zh-hans` 全簡中、terms 點 EN pill 留在 terms.html、index nav 五項順序、guide/me pills 最前,全過;截圖確認。

## [v1.17.2] - 2026-07-03 11:41
### 調整 — privacy/terms header 與首頁完全同排版(使用者指示)
- privacy/terms 的 topnav 改成與首頁一模一樣的順序與位置:繁/简/EN pills + 隱私權政策 + 使用條款 + 使用說明 + 「我的音樂劇」CTA,只在最前面多一個「地圖首頁」——跨頁切換上排不跳動。pills 連到各語言首頁(這兩頁本身僅繁中)。
- 註:v1.17.1 的 Pages deploy 在 GitHub 端失敗(`Deployment failed, try again later`,同 v1.16.3 當天的平台抽風),本次 push 觸發新 deploy 一併補上。

## [v1.17.1] - 2026-07-03 11:35
### 修正 — 360px 窄機(Galaxy 級)header 溢出
- v1.17.0 上線後複驗發現:headless 扣捲軸的 ~360px 有效寬度下,「我的音樂劇」CTA 被推出右緣。手機版 header 全面收緊(brand logo 28px/字 17px、lang pill padding 7px、CTA 13px/7×12、gap 6px),playwright 實測 360/375/412px `scrollWidth==viewport`、CTA 單行 31px 全過。

## [v1.17.0] - 2026-07-03 11:28
### 新功能 — 全站畫風/命名/導航統一(使用者 8 點回饋 + 自主體檢)
- **站名統一「我的音樂劇」**:index 三語(`gen_site.mjs` t.mine)、theatres CTA、me 登入頁大標(`mm-strings gate_signin`)、i18n.js `nav_mine`、privacy/terms 內文全部由「⭐ 我的音樂劇足跡」改為「我的音樂劇」(en: My Musicals),去 ⭐。
- **語言切換統一「繁 简 EN」精簡 pills**(比照 guide `.hl-pick`):`gen_site langSwitch()` 去 🌐 全字版;順帶修掉 375px 手機 header 語言鈕折行疊字的爆版。active pill 金色。
- **Google 登入按鈕走 Google 品牌風**:白底 + 官方四色 G(inline SVG,無外連)+ `#dadce0` 邊框,取代無辨識度的純金膠囊。
- **修「載入中仍顯示登入按鈕」真因**:舊按鈕 inline style 寫死 `display:inline-flex`,優先權蓋掉 `hidden` 屬性 → 按鈕永遠藏不住。改為 CSS class + `#gate-login[hidden]{display:none}`;playwright e2e 驗證 loading/無後端路徑按鈕與 preview 皆真隱藏。
- **登入頁補導航與 preview**:閘頂加品牌列(logo+MusicalMap+「地圖首頁」→ index);登入鈕下方加登入後畫面 preview(`assets/guide/stats.webp`)+「先逛演出地圖/看使用說明」出口,登出後不再是死路。
- **全站 ivory 統一畫風**:`css/style.css` tokens 換成 guide 的 `--paper/#f4efe4` 色系(header/sidebar/panel/border/muted 全暖色化,teal 留給地圖元件),index 三語+privacy+terms+theatres 生效;me/u 深色個人頁維持不變。
- **品牌字統一**:index/privacy/terms/theatres 的 MusicalMap wordmark 改 Fraunces 900 + 金色「Map」(與 guide/me/u 一致);guide 30×30 方框壓變形的 logo 改回 122×200 原比例(me 登入閘同修)。
- **nav/footer 一致化**:「🗺 演出地圖」→「地圖首頁」(mm-strings/i18n.js/privacy/terms/theatres,en: Map home);index 頂欄三連結(隱私/條款/使用說明)同字級;guide/me/u footer 補齊 隱私權政策+使用條款 連結;privacy/terms nav 補使用說明、footer 統一「地圖首頁 · 使用說明 · 法務 · 聯絡」。
- **自主體檢加修**:全站補 favicon(原本只 guide 有);`<title>` 統一「X — MusicalMap」(me/u 原 `·`/無品牌);u.html og:title 足跡→我的音樂劇;index nav 的 privacy/terms 連結拿掉無作用的 `?lang=` 參數;privacy/terms「最後更新」bump 2026-07-03。
- **驗證**:本機 `/MusicalMap/` 前綴 server + headless 截圖(5 頁×桌機/手機)+playwright 量測(375px header scrollWidth=375 無溢出、CTA nowrap)+跨語言 e2e(guide/me `?hl=en`、zh-hans index)全過;背景色像素實測 `#f4efe4`。

## [v1.16.3] - 2026-07-03 09:58
### 調整 — guide 地圖截圖換美東(紐約)視角;全站暫藏「所有劇院」入口
- **guide 地圖 fig 換視角**:亞洲視角 → 美東視角(NYC「48」聚合圈醒目,Mamma Mia/LOTR/Suffs/The Notebook/Matilda 海報+各城市圓圈+月份時間軸)。也試拍 NYC 特寫(z7)但資訊密度低+有未載入空卡,棄用。`map.webp` 同尺寸 1600×1336 覆蓋,HTML 不用改。
- **「所有劇院」連結全站暫藏**(theatres.html 頁面保留、可直達、sitemap 續收):`guide.html`/`me.html`/`u.html` nav 註解掉;`gen_site.mjs` 模板註解 + 本機重產三語首頁(en/zh-hans/zh-hant)。要恢復時解註解+重跑 gen_site 即可。
- **驗證**:playwright 開 index(zh-hant)/guide/me/u 四頁,「所有劇院」皆不可見、其餘 nav 連結正常。

## [v1.16.2] - 2026-07-03 09:19
### 修正 — guide 頁全面體檢:手機版壞版、內文不實宣稱、截圖錯置(Fable 5 重新檢視)
- **手機版修復(390px 實測溢出 155px → 0)**:h1 `word-break:keep-all` + em nowrap 造成整頁橫向溢出、右緣文字被切 → 移除 keep-all(em 保留 nowrap,「音樂劇。」不拆字);header nav 無手機處理(「我的音樂劇」CTA 整顆被擠出畫面外、文字連結被壓成直排)→ ≤700px 收掉文字連結、≤430px 縮小 brand/CTA/語言切換;b3/b4 欄的 inline `border-left+44px` 手機殘留 → 改 `.copy.divided` class,堆疊時轉上緣分隔線。
- **內文事實修正(對照 code/資料逐句查證)**:「不抽成」刪除(affiliate 分潤機制上線中,不能這樣寫);「每一齣都附官方網站與售票連結」→「每一齣都附售票連結,多數還有官方網站」(實測 1658/1658 有售票連結、1095/1658 有官網);「每個標記=城市/圓越大=劇越多/藍駐演紅巡演」全段改寫(舊文描述的是截錯的個人足跡地圖;產品無藍紅圖例)→ 改為海報 marker+聚合數字圓圈的真實行為;刪「簡介」(popup 無此欄位);全篇半形標點改全形(，；),en 同步修正。
- **四張截圖全部重截(舊圖三張有事)**:map.png 截錯畫面(是 u.html 個人足跡地圖,非主站地圖)→ 主站實截(海報 marker+聚圈+月份時間軸);wall.png(個人收藏頁)配「一鍵訂票」圖文無關 → 換 Wicked popup 實截(購票方塊+官網標題連結);passport.png 構圖弱且不對題 → 換記錄表單搜尋「歌劇魅影」實截;stats.png 截壞(卡片標題被切+一整塊空卡,肇因 `.reveal` 捲動動畫未觸發)→ 先捲動觸發 reveal、藏 sticky 後重截,七卡完整。
- **效能**:4 張 PNG 3.8MB → 4 張 WebP 388KB(-90%);`<img>` 補 width/height(防 CLS)+`decoding=async`;preconnect 補 `fonts.gstatic.com` crossorigin。
- **i18n/SEO**:mm-strings 語言切換「繁」改明寫 `?hl=zh-hant`(原本刪參數→簡體/英文瀏覽器按「繁」被 navigator 重偵測彈回,永遠切不回繁;全站共用機制一併修好);`<title>`/meta description/og 隨語言切換(apply() 新增 `data-i18n-content`,新 key `how_title`/`how_meta`);補 canonical+hreflang alternates(?hl= 三變體,同 theatres.html 模式)+og:url。
- **驗證**:playwright 量像素(390 溢出=0、CTA 可見、divided 手機轉上緣線)+ 桌機/手機/en/zh-hans 四情境全頁截圖親看 + 四圖捲動後載入 OK + 零 console error + 零殘留 key。

## [v1.16.1] - 2026-07-02 23:10
### 接上 — guide 頁 nav 連結 + sitemap 收錄(讓訪客/爬蟲找到)
- **各頁 nav 加「使用說明」連結指向 `guide.html`**:首頁(`gen_site.mjs` t 加 guide + nav 連結,依語言帶 `?hl=`)、`me.html`/`u.html`(mm-strings 加 `nav_guide` key)、`theatres.html`(i18n.js DICT 加 `nav_guide`,zh-hans 自動 OpenCC 轉)。
- **`sitemap.xml` 收錄 `/guide`**(gen_site 產生器層,重產)。
- **驗證**:playwright — 首頁/me/u/theatres 四頁 nav 的 guide 連結都存在、i18n 正確套用(非 key 字面)、指向 guide.html、無 JS error;guide.html 可達,全 PASS。
- guide 頁多語 nav 也加了 nav_guide(繁/簡/英)。**guide 頁正式接上全站入口。**

## [v1.16.0] - 2026-07-02 21:41
### 新功能 — 使用說明頁 guide.html(editorial 藝文風,三語)
- **新增 `guide.html`**(網址 /guide):全球地圖探索(免登入)+ My Musicals 記錄/護照/分享的使用說明。**「觀劇手帳」editorial 風格,不是科技 SaaS**——暖米白紙本紋理底 + Fraunces 襯線大標 + 大號金色襯線數字(01/02)+ 真實產品截圖不對稱交錯 + italic 轉場句 + 深色收尾框。**零 emoji、零漸層、零對稱 feature 卡、標題非 Inter**(避開所有 AI slop 訊號)。
- **4 個 web 研究 agent 統合設計**:how-it-works 結構最佳實踐(Linear/Letterboxd)、藝文文化平台調性(避 SaaS 味,editorial/襯線/紙本)、crafted vs AI 模板的 16 個 slop 特徵清單、精確視覺規格(字體階層/8pt 間距/大數字 step)。
- **真實素材** `assets/guide/`:地圖/海報牆/護照戳章/統計截圖(playwright 從實站 u.html?u=danny 截,關動畫強制可見)。文案 benefit-first、有聲音(不空泛行銷詞)。
- **三語(繁/簡/英)** 走 mm-strings + `?hl=` + OpenCC;新增 how 專屬 key(去 emoji、editorial 文案)。
- **驗證**:playwright 三語全頁截圖**親眼看過**(繁/英確認 editorial 質感)+ 4 素材載入 + 零殘留 key + 零 emoji + 無 JS error 全 PASS;修 h1 中文斷字(word-break)、en 內文彎引號字寬(en --sans 用西文字體)。
- 待辦:主站各頁 nav 加「使用說明」連結 + sitemap 收錄(讓訪客/爬蟲找到)。

## [v1.15.2] - 2026-07-02 20:58
### 文件 — Google 登入品牌顯示(supabase.co)查證結論存檔
- **web 查證確定結論寫入 `docs/SETUP_ACCOUNTS.md`(新增「Google 登入品牌顯示」段)+ `docs/SETUP_MY_SUBDOMAIN.md`(收尾清單加 auth callback 代理)**:OAuth 同意畫面顯示 `xxx.supabase.co` 是官方雙方確認的規則——Google「App 未通過品牌驗證前只顯示應用程式網域」+ Supabase 免費版「回呼網域無法更改」;**只填 App name 無效**,需品牌驗證+In production+發佈。
- 三種根治法:(A)Google 品牌驗證免費但要等+處理 supabase.co 無法驗證;(B)Supabase Pro Custom Domain $10/月;(C)**推薦免費根治=Cloudflare Worker 代理 auth callback 到 auth.themusicalmap.com,跟主站遷移+my. Worker 綁一起做**。
- MD sweep:SETUP_ACCOUNTS/SETUP_MY_SUBDOMAIN 已補;其餘 md 本次(gate/OAuth 修正)未涉及、無過時。

## [v1.15.1] - 2026-07-02 17:41
### 修正 — 登出後 gate 卡「Loading…」+ 登入畫面美化(真人 flow 驗證)
- **修真 bug**:`gate-msg` 掛了 `data-i18n="gate_loading"`(P2 誤加),`showLogin()` 動態設登入文案後,mm-strings 的 `apply()`(DOMContentLoaded)掃到 data-i18n **把它蓋回「Loading…」**→ 登出後出現「Loading…」與登入按鈕並存。修:gate-msg 移除 data-i18n(它是 showGate 動態容器);sb 建立後立即 `showGate(T('gate_loading'))` 用當前語言。**e2e stub 沒抓到(沒測真實無 session 的 gate flow),真人才現形。**
- **登入畫面美化**(原「整片黑+置中 Loading+按鈕」很醜):加 logo、徑向漸層背景、按鈕陰影,新增**安全說明**「用 Google 帳戶安全登入,只讀名稱與 email,不會代你張貼」(回應使用者對 OAuth 畫面「像詐騙」的疑慮)。
- **驗證**:playwright 真實登出狀態(headless 無 Google session = 登出後)跑真 supabase getSession → showLogin,en/繁中各驗:登入文案(非 Loading)、按鈕、安全說明、logo 皆顯示、無 JS error;截圖親驗美化。
- 註:OAuth 同意畫面顯示 `xxx.supabase.co`(像詐騙)是 Google Cloud OAuth consent screen 的 App name 未設,需在 Google Cloud Console 設定(見 docs,前端改不了)。

## [v1.15.0] - 2026-07-02 16:02
### 新功能 — 足跡側簡體中文(zh-hans)P4:多語化竣工
- **OpenCC runtime 繁→簡**:`js/mm-strings.js` 在 zh-hans 時用 `OpenCC.Converter({from:'tw',to:'cn'})`(沿用主站 i18n.js 機制)把繁中字典 runtime 轉簡體;無 OpenCC 降級繁中。**OpenCC 只在偵測到 zh-hans 時 `document.write` 條件載入**(繁中/英文使用者不下載 65KB),三頁 head 判斷語言(?hl / mm_variant / navigator)一致。
- **localStorage 改讀 `mm_variant`**(en/zh-hans/zh-hant,含簡繁精確,與主站共用),優先於舊 `mm_lang`(en/zh);切換寫回兩者。
- **資料層地名/劇名譯名也轉簡**:mm-strings 暴露 `MM_S`(zh-hans=OpenCC,否則 identity);`u-view.js`/`me.html` 的 countryZh/cityName/venueZh 包 MS;u-view `mapped.zh`(劇名譯名)亦包 → u.html 公開頁完整簡體。
- **簡中語言 pill**:u.html/me.html nav 加「简」(繁/简/EN);修 pill active 判斷(不再讓繁中 pill 在簡中借用)。
- **Worker**:`worker/my-worker.js` 補 zh-hans title/desc(簡體硬編)+ hreflang zh-Hans(4 條互列)。
- **驗證**:playwright — u/me zh-hans 簡體正確(观剧统计/我的观剧足迹/海报墙/上海大剧院/歌剧魅影) + 繁中/英文回歸不受影響 + 英文版不下載 OpenCC(條件載入生效) + Worker zh-hans 8 項全 PASS;截圖親驗簡繁差異。過程修 regression:u-view render 內 `const S=MM.shows` 遮蔽我加的 S(MM_S)→ 改名 MS。
- 已知小限制:me.html 劇名中文譯名簡體模式仍繁體(共享資料未逐處包 MS;u.html 已完整);海報圖內文字是圖片無法轉。
- **🎉 足跡側多語化 P1–P4 全竣工**(u.html/me.html/me-input.html × 繁中/簡中/英文)。

## [v1.14.0] - 2026-07-02 15:41
### 新功能 — me-input.html 輸入表單多語化 P3(繁中/英文)
- **`js/mm-strings.js` 擴充 me-input 專屬字典**(~70 key:mi_/fld_/ph_/geo_/pick_/run_/recent_/added_/star_n/toast_* 等 + 海報/連結欄);apply() 新增 `data-i18n-html`(給含 `<br>`/`<b>` 的信任 UI 文案,非使用者輸入)。
- **me-input.html 全面 i18n**:head 載 mm-strings + `MM_USE_LANG_PREF`(iframe 語言跟隨父頁 me.html 寫入的 `mm_lang`);主 script 注入 `T/TN/EN_UI`;靜態(header/hero/footer/sheet/theme)掛 data-i18n;動態渲染模板全改 `MM_T()`——搜尋提示、手動表單、選製作/選城市清單、詳情表單、確認畫面、toast、`dateLabel`(EN_UI 用英文月份格式)、renderRecent、MON_ZH/yearOptions/月日 select。
- **驗證**:playwright — 繁中回歸(搜尋提示中文/搜尋有結果/無 error) + 英文版(h1/搜尋提示/placeholder/手動表單 8 欄位全英文/sheet UI 零中文殘留/無 error) + embed 模式(iframe 自動開表單、英文、無 error)全 PASS;繁中/英文截圖親驗。
- 註:demo 開發標記(`Demo v3 · 輸入端` 導覽,embed 下隱藏)刻意保留未 i18n。

## [v1.13.0] - 2026-07-02 15:07
### 新功能 — me.html 個人主頁多語化 P2(繁中/英文)
- **`js/mm-strings.js` 擴充 me.html 專屬字典**（~70 條）:登入閘各狀態、demo 橫幅、分享 modal + 帳號設定 modal + onboarding 全部訊息、徽章/persona/詳情 modal、刪除確認/toast/復原。
- **語言記在 localStorage `mm_lang`（與主站共用）**:`?hl=` 優先 → `mm_lang`(en/zh) → navigator → 繁中;切換寫回。nav 加 EN/繁中 pills。（登入頁 noindex,無 SEO 需求,故用 localStorage 而非只認網址。）
- **me.html 全面 i18n**:靜態掛 `data-i18n`;4 個內嵌 script IIFE(render/分享/登入同步/刪除)動態字串改 `MM_T()`;`<html lang>` 動態;en 模式 `countryZh`/`cityName`/`venueZh` 顯示資料原文。h1 硬編「Danny 的音樂劇收藏」改中性多語標題。
- **驗證**:playwright — 繁中 onboarding 回歸 23 項 PASS + 英文版 me.html 18 項 PASS(nav/seg/統計/persona/詳情 modal/城市名英文/UI 零中文殘留/無 JS error) + u.html 回歸 6 項 PASS;繁中/英文截圖親驗。
- **過程抓到並修的真 bug**:(1)字典漏 `logout` key（e2e 抓到顯示 key 字面）;(2)`cityName`/FAB「加入音樂劇」漏接 EN_UI → 英文版城市仍顯示「倫敦/漢堡/台北」（截圖抓到,已補 EN_UI 分支）。

## [v1.12.0] - 2026-07-02 13:59
### 新功能 — 公開收藏頁(u.html)三語化 P1:繁中/英文 + 語言進網址(?hl=)
- **`js/mm-strings.js`(新)**:足跡側 UI 字典(繁中+英文,zh-hans 暫 fallback 繁中)+ 語言解析(`?hl=` 參數優先 → Worker 注入 → navigator → 繁中)+ `data-i18n` 靜態套用 + 語言切換 pills(繁中/EN,連結式、保留 `?u=`,爬蟲可發現變體)。**語言進網址是 SEO 需求**(Google 官方反對 cookie/瀏覽器語言切換——Googlebot 不帶 Accept-Language 不留 cookie;Strava/X/Last.fm 個人頁實務零例外,見 DESIGN 文件實證)。
- **`u.html`**:全部靜態中文節點掛 `data-i18n`;**移除 `js/i18n.js`**——它的 applyStatic 同吃 `data-i18n` 屬性、在本頁字典查無 key 時會把 key 字面蓋進畫面(e2e 抓到的真衝突),本頁由 mm-strings 全權接管。
- **`js/u-view.js`**:~40 處 runtime 中文改 `MM_T()`;en 模式國家/城市/劇院顯示資料原文(不做中文在地化);XSS `esc()` 紀律不變(字典值進 innerHTML 也跳脫)。
- **`data.js`**:`personality()` 語言化(有 mm-strings 用字典,me.html 未載入則沿用中文字面,零 regression)。
- **`worker/my-worker.js`**:`?hl=` 支援——`<html lang>`/title/description/og 依語言出、注入 `MM_HL`、**hreflang 3 條互列**(zh-Hant=無參數版=x-default、en=?hl=en)+ canonical 各語言指自己。
- **驗證**:i18n e2e **19 項 PASS**(zh 現狀不變/en 抽查 8 處+UI 容器零中文殘留/persona 英文/切換 pills/me.html 回歸含 personality 中文 fallback;真 Supabase danny 資料)+ Worker 直測 **12 項 PASS**(en/無參數/404 三態的 title/lang/canonical/hreflang);zh+en 截圖親驗。
- 尚未做(P2+):me.html/me-input.html 的多語、zh-hans 接 OpenCC、Worker meta 的 zh-hans 版。

## [v1.11.1] - 2026-07-02 13:13
### 驗證 — 改名轉向全鏈路真人實測通過
- 使用者實際操作:帳號設定 danny→danny_test→改回 danny。(a)舊網址 `?u=danny` 自動轉向 ✓(b)改回自己舊名合法 ✓(c)alias `danny_test` 永久歸原主、`handle_available=false` 別人搶不走 ✓(線上 API 確認)。username 機制無未實測環節。

## [v1.11.0] - 2026-07-02 12:59
### 新功能 — my.themusicalmap.com Cloudflare Worker(程式碼完成,待部署)
- **`worker/my-worker.js`(新)**:`my.themusicalmap.com/<handle>` 三合一——(1)乾淨網址:內部取 u.html 注入 `window.MM_HANDLE`;(2)舊名 301:查無 handle → `resolve_handle` → 301 現用名(alias 永久有效);(3)爬蟲可見:注入該使用者專屬 title/description/og/canonical/JSON-LD ProfilePage(解決個人頁純前端 render 爬蟲空白,對標 FR24)。另處理:靜態資源代理、不存在→404+noindex、保留字/根→主站、尾斜線 301、robots.txt。無 secret(anon key+RLS),可放公開 repo。
- **`worker/wrangler.toml` + `docs/SETUP_MY_SUBDOMAIN.md`(新)**:部署步驟(wrangler login/deploy + DNS `AAAA my 100::` 橘雲)+ 驗證清單 + 主站遷移時的收尾清單。
- **`js/u-view.js`**:handle 來源改「`?u=` 或 `window.MM_HANDLE`」,兩種網址形式並存,`?u=` 零影響。
- **驗證**:Worker handler 本機直測(真 GH Pages+真 Supabase)14 項 PASS(/danny 注入+個人化 meta/大寫/404+noindex/css 代理/根/保留字/尾斜線/robots);u-view `?u=` 回歸 6 項 PASS。alias→301 需等首次真實改名後可驗。

## [v1.10.2] - 2026-07-02 12:54
### 資安/SEO — CDN SRI + sitemap 修正 + 死 code 清理(健檢待辦 3 項收掉)
- **CDN 供應鏈防護(SRI)**:所有第三方 script/css 釘死版號 + `integrity`(sha384) + `crossorigin` —— `me.html`/`me-input.html`/`u.html` 的 supabase-js(2.110.0)、chart.js(4.5.1);`build/gen_site.mjs` 模板的 leaflet(1.9.4)、markercluster(1.5.3)、opencc-js(1.3.1),重產三語 index。CDN 被竄改時瀏覽器直接拒載,護住登入頁 token。
- **sitemap 移掉 me.html**:登入閘頁爬蟲只看到「載入中」。第一次手改 `sitemap.xml` 被 `gen_site.mjs` 重產蓋回,**改在產生器層移除**才是正解;另 me.html head 加 `noindex`。
- **死 code 清理**:`js/me.js` + `me_ori.html` 移除(僅互相引用、正式頁未載入;git 歷史可找回)。README/DESIGN_productions 註記同步。
- **驗證**:playwright 對「與線上一致的 /MusicalMap/ 路徑結構」跑 SRI e2e 10 項全 PASS(主地圖 leaflet 渲染/zh-hans OpenCC/me supabase+Chart/me-input/u.html danny 真資料);onboarding e2e 23 項回歸 PASS。(過程學到:本機從 repo root 起 server 會因絕對路徑 `/MusicalMap/` 全 404,要從上層目錄起。)

## [v1.10.1] - 2026-07-02 12:35
### 文件 — add_handle_aliases migration 已套用+線上實測記錄
- 使用者已在 Supabase Dashboard 執行 `add_handle_aliases.sql`(Success)。
- **線上實測**:anon 直打 REST 驗 `handle_available`(danny→false/保留字 admin→false/隨機→true)、`resolve_handle`(無 alias→null)、`rename_handle`(anon→not_authenticated 擋下);GitHub Pages v1.10.0 部署確認(me.html 含 acctModal/u-view 含 resolve_handle);**真線上站** u-view 回歸 6 項 PASS(danny/Danny/不存在)。
- 尚待真人一次:登入後在帳號設定實際改名,驗「舊網址自動轉向」完整迴圈。

## [v1.10.0] - 2026-07-02 12:27
### 新功能 — username 帳號身份化(DESIGN_username_sharing 決策一+二實作)
- **DB migration `supabase/add_handle_aliases.sql`(待 Dashboard 執行)**:`handle_aliases` 改名歷史表(RLS 開、無 policy=不可枚舉)+ `rename_handle`(改名唯一入口;union 查重「他人現用名+他人舊 alias」防 GitHub 式撞車;改回自己舊名合法)+ `handle_available` 升級(含 alias+保留字、排除自己)+ `resolve_handle`(舊名→現用名,只回公開帳號)+ `handle_reserved`(保留字集中一處)。
- **onboarding 強制化**:首次登入無 handle 必須取名(無 X、ESC/backdrop 關不掉、唯一出口=登出);欄位**空白不預填**(label 在上,無 placeholder)+**可用建議 chips**(種子=email 前綴、逐顆預驗可用、主動點才填)。
- **分享面板 handle 改唯讀**:顯示固定網址+「帳號設定」連結;儲存只動公開/票價/座位開關。
- **帳號設定 modal(新)**:改 username(走 rename_handle,提示「舊網址自動轉新」)+ 顯示名稱。
- **舊網址自動轉新**:u-view.js 查無 handle → `resolve_handle` 解析 301-style `location.replace`;RPC 未部署靜默降級。**順帶修 bug**:訪客輸入大寫 `?u=Danny` 因 `.eq` 區分大小寫查不到 → 統一小寫後命中。
- **降級保護**:migration 未套用時 rename_handle 不存在 → 前端自動退回舊 upsert(unique 約束保底),功能不中斷。
- **驗證**:playwright 真 e2e 23 項 PASS(強制/chips 只列可用/ESC 關不掉/唯讀/改名 taken→成功/不重彈)+ u-view 真線上回歸 6 項 PASS(danny/Danny/不存在);截圖親驗 onboarding 與帳號設定 render。過程抓到並修掉 `.share-field{display:block}` 蓋掉 `hidden` 的 CSS 特異性 bug(補 `.share-field[hidden]{display:none}`)。
- MD sweep:README(分享頁段改述新機制)、SETUP_ACCOUNTS(migration 清單+降級行為)、DESIGN_username_sharing(清單勾選+狀態)。

## [v1.9.8] - 2026-07-02 12:08
### 設計 — my.themusicalmap.com/<handle> 帳號身份 + 分享網址架構定案(含實證)
- 新增 `docs/DESIGN_username_sharing.md`:username 從「分享面板暱稱」升級為「帳號固定身份」的完整實作依據。**待實作**。
- **決策一(改名政策)**:改名後舊 handle **永久保留給原主 + 301 轉向新名**。依 web 實證——業界分三類(社群帳號立即釋放 / 冷卻折衷 / 個人頁永久保留),本專案成本結構同 Medium/Substack(名稱池無限、URL 會外部分享)故採永久保留。附 10 平台官方來源。唯一工程風險=唯一性檢查要 union `handle_aliases`(GitHub 翻車根因)。
- **決策二(onboarding)**:username 欄位**空白 + 可用建議 chips**(預驗可用、主動點才填、種子用 email 前綴),**不預填 Google 真名**(隱私 + default-effect 地雷)。依 NN/g/Baymard/GOV.UK/W3C + Linktree/Bio.link 同類產品皆空白之實證。
- 含資料模型(`handle_aliases` 表 + `rename_handle` 函式 + union 查重)、Cloudflare Worker(rewrite + alias 301 + 爬蟲 meta 注入)、前端改動清單、實作順序。
- 過程修正:先前憑印象的建議(「業界都永久保留」「預填 Google 名字」)經實證調查後修正——預填真名實為最糟選項。

## [v1.9.7] - 2026-07-02 10:53
### 資安 — 通盤健檢 + handle 強化(修大小寫碰撞 + 格式限制)
- **完整資安/SEO/AI-search 健檢**,結論存檔 `docs/SECURITY_AUDIT_2026-07-02.md`(RLS/授權、SQL injection、XSS、金鑰、供應鏈、SEO、AI-search、themusicalmap.com + `my.` 子網域架構建議)。
- **線上 `pg_policies` 實測確認**:`sightings_read/write=(user_id=auth.uid())`(遮罩 migration 已套用、price/seat/note 不外洩,Critical 是啞彈);`public_sightings/handle_available/handle_new_user` 皆 SECURITY DEFINER + `search_path=public`。
- **修 handle 大小寫碰撞(Medium)**:原 `handle unique` 區分大小寫、查詢用 `lower()` → `Danny`/`danny` 可並存並在公開頁互相混資料。改成 `profiles_handle_lower_uidx on (lower(handle))`,drop 舊 `profiles_handle_key`。DB 修復 SQL 存檔 `supabase/add_handle_hardening.sql`,已在 Dashboard 執行+實測生效。
- **加 handle 格式 CHECK(Low)**:`^[A-Za-z0-9_-]{1,30}$`,刻意對齊前端 `me.html` 的 `norm()`(允許 `-`、上限 30、無下限),零 regression。
- **SQL injection 靜態分析=零可利用面**:grep 全 SQL 無動態 SQL、全前端無字串拼 filter。記下兩條免疫鐵則(不可動態 SQL、不可 `.or(\`${input}\`)`)於報告與記憶。
- 待辦(未動 code):CDN 加 SRI、`sitemap.xml` 移 `me.html`、清 `js/me.js` 死 code、`my.themusicalmap.com` Cloudflare Worker。

## [v1.9.6] - 2026-07-02 01:03
### 文件 — 完整 MD freshness sweep(對齊 v1.6–v1.9.5 現況)
- 逐個掃過所有 `.md`。修正過時處:
  - `README.md`:劇院數 `5117 → 5,100+`(避免 CI 增長再過時);My Musicals 段補上近版現況——金框海報卡 + 下方常駐資訊、中文頁只顯示中文(國家繁中/劇院去廳別)、點詳情海報開新分頁看原圖、可預先輸入未來場次(標「即將上演」不計入已看統計)、自訂海報貼大圖自動經 wsrv.nl 縮圖加速(失敗退原圖)。
  - `docs/SETUP_ACCOUNTS.md`:`public_sightings` 讀取端 `u.js → js/u-view.js`(v1.6.0 已改名)。
- 確認**其餘 md 皆現行無過時**:`WORKFLOW.md`(提交流程)、`DESIGN_productions.md`(已 u-view)、`AFFILIATE_SETUP/DESIGN_affiliate/SOURCES/TOUR_SWEEP/DAMAI`(scraper/affiliate/資料領域,本輪前端改動未涉及);CHANGELOG 內舊版的 `u.js`/`me_ori` 為歷史紀錄、保留不改。works.json 170 筆與文件一致。

## [v1.9.5] - 2026-07-01 21:37
### 調整 — 海報放大改回「開新分頁看原圖」(依使用者需求)
- 依使用者需求:詳情窗點海報 → **開新分頁直接顯示原始高解析大圖**(`window.open(posterFull)`),不再用頁內 lightbox。移除 lightbox(showLightbox 函式 + `#mm-lightbox` CSS)。提示改「↗ 點圖開新分頁看原圖」。
- **真 e2e 驗證**(playwright):點詳情窗海報 → 捕捉新分頁 → 確認 URL = 原始圖(`romeoetjulietteofficiel.com/...RJ_23.jpg`,非 wsrv 代理版)。

## [v1.9.4] - 2026-07-01 21:23
### 修正 — 海報放大 lightbox 開了但圖是透明的(onload 沒觸發)
- **真 e2e(playwright 真的點進去)抓到的 bug**：v1.9.3 lightbox `<dialog>` 有開,但圖**資料載入了(naturalWidth=1690)卻 opacity 卡在 0、spinner 不消失** → 圖透明看不到。原因:`img.onload` 在 dialog `showModal` 時序下有時**不觸發**,revealing 的 opacity/spinner 邏輯掛在 onload → 沒跑。修:加 **`img.decode()`**(解碼完成 Promise,比 load 事件可靠)+ `complete` 檢查當保底來 reveal。
- **驗證方式升級**：改用 **playwright 真 e2e**(開 u.html?u=danny → 點卡片 → 點詳情窗海報 → 等 img `opacity===1 && naturalWidth>0`),本機驗 exit=0 + 截圖確認完整原圖顯示,再驗線上部署版。(先前只用隔離 harness 驗單元件,漏掉整頁互動時序 bug。)

## [v1.9.3] - 2026-07-01 21:12
### 修正 — 點海報放大沒反應 + 刪除加確認視窗
- **lightbox 點了沒反應**：詳情窗是原生 `<dialog>`(showModal→瀏覽器 top layer)，v1.9.2 的 lightbox 只是普通 div + `z-index:9999`，**top layer 蓋不過** → lightbox 其實有開但被詳情窗擋在後面。修：lightbox 改成 `<dialog>` + `showModal()`(第二個 dialog 疊在第一個之上)，`::backdrop` 當暗底，點任意處/✕/ESC 關閉。harness 截圖驗證 lightbox 確實疊在詳情窗上、顯示原始高解析。
- **刪除加確認**：海報卡右上垃圾桶原本**點了直接刪**(易誤觸)。加 `confirm` 確認視窗「確定要刪除《X》?(仍可從復原救回)」。

## [v1.9.2] - 2026-07-01 21:04
### 改善 — 海報放大改成頁內 lightbox（原本開新分頁看不到）
- 詳情窗點海報「看原圖」原本是 `window.open` 開**新瀏覽器分頁** → 使用者常沒注意到、體驗不明顯。改成**頁內全螢幕 lightbox**：點海報 → 當頁暗背景放大**原始高解析大圖**(`posterFull`)，點任意處 / ✕ / ESC 關閉;載入中顯示「載入原圖中…」、失敗顯示提示。提示文字改「🔍 點圖放大看原圖」。兩頁共用 `css/me-v2.css` + 各自 showLightbox。harness 截圖驗證 lightbox 版面。

## [v1.9.1] - 2026-07-01 20:48
### 修正 — v1.9.0 海報代理弄壞部分自訂圖(wp.com 破圖)+ zoom 用原圖
- **回歸修正**：v1.9.0 對所有自訂海報套 wsrv 代理，但 wsrv 對「已帶 query 參數的縮圖 CDN URL」(如 `i0.wp.com/...?w=410&ssl=1`)會回 **HTTP 400** → 破圖(實測 Les Misérables 那張)。修：(1)`proxyImg` **跳過**已含寬度參數(`?w=`)或 wp.com 縮圖 CDN 的 URL(本來就已優化、不需代理);(2)所有 `img.onerror` 加**保底 fallback**：代理版失敗 → 自動退回**原圖** → 原圖也失敗才顯示字母色塊。截圖驗證 Les Mis(fallback 原圖)+ Roméo(代理 97KB)皆正常載入。
- **zoom 用原始高解析**：詳情窗點海報放大 → 開**原圖**(`posterFull`)而非 600px 代理版;show 物件加 `posterFull` 帶原始 URL。

## [v1.9.0] - 2026-07-01 16:48
### 調整 — 海報牆卡片微調 + 詳情窗日期時間分開 + 自訂海報自動縮圖
- **英文標題顏色**跟隨方案 A：`#efe7d6` 暖奶油白(亮色主題 gallery/cream 保留深色 --ink1 避免看不見)。
- **海報牆卡片不再顯示星星評等**(移除 `.stars`)。
- **詳情窗日期/時間分開兩行**：原本「Feb 12, 2023 · 19:30」擠一起，改成「日期 2023/02/12」+「時間 19:30」各自一列，日期改斜線格式。
- **自訂海報自動縮圖加速**：使用者自訂海報常是原始大圖(實測 Roméo et Juliette 那張 1.66 MB)→ 自動走免費即時縮圖代理 **wsrv.nl**(縮寬 600 + webp + q82，實測 → 97 KB，**小 16 倍**)。**只代理自訂海報**，catalog 官方海報維持原樣(已優化、避免依賴風險)；代理失敗有 `img onerror → fallback` 保底。第三方依賴：wsrv.nl(images.weserv.nl 備援)。
- me.html 與 u-view.js 同步；共用 css/me-v2.css。

## [v1.8.2] - 2026-07-01 12:25
### 修正 — 卡片 hover 兩階段抖動
- 金框改版時加了「整卡上浮」(`.card:hover` translateY @ --dur-2)，但原本「海報自己上浮+放大」(`.card:hover .poster` translateY+scale @ --dur-3)仍在，且我的 `transform:none` 覆蓋排在原規則之前(同 specificity → 後者勝)。兩條不同時長的 transform 疊在一起 → hover 兩階段、不順。移除原 poster 位移規則，只留整卡單一平滑上浮。註：hover 體感為動態，靜態截圖無法驗，屬確定性修正。

## [v1.8.1] - 2026-07-01 12:20
### 修正 — 卡片日期被 nowrap 截斷（2024/06/... → 完整）
- v1.8.0 把「城市·國家·日期」擠在同一行，窄卡 nowrap 溢出把日期截成「2024/06/...」。改成**日期獨立一行**(`.cap-date`)保證完整顯示。2x 放大截圖驗證(2026/11/17、2026/06/07 完整)。

## [v1.8.0] - 2026-07-01 12:14
### 改版 — 中文頁只顯示中文（國家/劇院）+ 卡片資訊移到海報下方
- **國家名繁中**：最常去的國家、城市榜、詳情窗、卡片 從「United States/Taiwan」改顯示「美國/台灣」。**掃全庫 59 國**建完整對照表(含 UK/USA/UAE 縮寫 + normCountry 正規化形)。
- **劇院名只顯示中文 + 去廳別**：存的是「English 中文 廳別」混合字串。改為抽當地文字(中/日/韓：CJK+假名+諺文)、去掉「大/中/小劇院、歌劇廳、演藝廳…」等**獨立**廳別後綴、臺→台。單一 token 館名不砍(上海大劇院/國家戲劇院保留)。**最常去的劇院**依去廳別中文名**合併同一劇院不同廳**計數。掃全庫 522 個當地文字場館驗證，僅 6 個含品牌拉丁名的邊角 case 殘留(合理)。
- **卡片資訊挪到海報下方**：原本蓋在海報上的 hover 覆蓋層(劇院/城市·國家/日期)移到海報**下方常駐**，海報保持乾淨；日期改**完整斜線格式 2024/06/08**(原本 2024.06)。
- me.html 與 u-view.js 同步；共用 `css/me-v2.css`。**驗證**：本機截圖 ?u=danny 卡片(上海大劇院 / 上海·中國 / 2026/11/17)；venueZh 對 danny 實際 venue + 全庫掃描實測(台中國家歌劇院 大劇院 → 台中國家歌劇院)。
- 註：日文場館的「大ホール」等日文廳別未砍(非中文廳別詞)，顯示完整日文名，可接受。

## [v1.7.3] - 2026-07-01 11:54
### 修正 — 海報牆英文標題下伸字母(g/y/p)被裁
- v1.7.2 改襯線體後，Georgia 下伸較深 + `-webkit-line-clamp` 的 `overflow:hidden` + line-height 1.28 太緊 → "Saigon"/"King" 的 g 底部被切。改 line-height 1.42 + `padding-bottom:2px` 給下伸空間。3x 放大截圖驗證 g/y/p/Q 皆完整不裁。

## [v1.7.2] - 2026-07-01 11:48
### 調整 — 海報牆英文標題改用襯線字體（跟隨方案 A）
- 海報卡英文標題 `.card .cap .en` 從 sans-serif(Inter)改為方案 A 的設定 `"Noto Serif TC","Songti TC",Georgia,serif`(英文落在 Georgia 襯線體)，14px/600，更有節目單質感。中文副標維持原字體。兩頁共用 `css/me-v2.css`。

## [v1.7.1] - 2026-07-01 11:41
### 修正 — me.html 看不到新中文名（The Lion King 無「獅子王」）+ 海報貼齊金框
- **root cause（已實測確認，非臆測）**：me.html 渲染純吃 localStorage 快取(`mm-log` 的 `e.w.zh`)，只有 `syncFromCloud` 時才從 catalog 重取 zh；且「本 session 已同步過」會**跳過 re-sync**。使用者的快取是在 v1.7.0(獅子王)之前同步的 → 愛無止盡有、獅子王沒有(u.html 無此問題因為它每次即時從 catalog 取)。實測：用 me.html 的 `loadCatalogMaps`+`sightingToEntry` 邏輯跑線上 catalog，`The Lion King → 獅子王` ✓，證明只差 re-sync。
- **修**：`SYNC_VER` `'2'→'3'` 強制所有 session 重新同步(這正是 SYNC_VER 的用途) → re-sync 重跑 mapping 取得新中文名。**並更新註解**：往後改 catalog 顯示資料(zh/海報)也要 bump，避免同類復發。
- **海報貼齊金框(使用者要求)**：卡片 `padding:0`、海報滿版貼到金框、放大、中間不留空隙；改「整卡上浮」取代原本 poster 位移(避免被金框 `overflow:hidden` 裁切)。兩頁共用 `css/me-v2.css`。
- 誠實：mapping 產出獅子王 + SYNC_VER 強制 re-sync 皆已驗；me.html 登入實機無法自動化(Google OAuth 擋自動化)，使用者硬重載即會 re-sync 顯示。

## [v1.7.0] - 2026-07-01 11:28
### 新功能 — 區分「已看過 vs 即將上演」+ 卡片金框
- **問題**：使用者會預先輸入還沒發生的未來場次，但全站(最新一場/大數字/統計/戳章)都當成「已看過」。
- **判定**：用「場次日期 vs 今天」自動分過去/未來，不改 DB schema。部分日期採該粒度最後一天(年精度→年底、月精度→月底)，當天算已看。`data.js` 加 `isPast/isFuture`、`stats(which)` 支援 past 篩選、`recent(pastOnly)`。
- **統計只算已看過**：最新一場、hero 大數字、統計榜/折線圖、persona、地圖城市榜 全部只計已發生；hero 另加弱化「· 即將 N 場」提示。
- **海報牆(方案 A)**：未來卡在**同牆混排**、特殊樣式 —— 去飽和+面紗+左上「即將上演」金緞帶+底部日期；**hover 恢復原本色彩亮度**(緞帶保留、面紗淡出)露出完整海報。
- **護照**：未來場次**不蓋章**(戳章=到場證明)，改虛線「即將上演」占位；「N STAMPS」只算已到場。
- **卡片金框**：海報卡加一圈金色細框(包住海報+文字，深色卡底)，hover 微亮。兩頁共用 `css/me-v2.css` 一次生效。
- me.html 與 u-view.js **同步**修改(6 處)；css 樣式共用。**驗證**：本機截圖 `?u=danny`(有 2026-11 未來場)—— 最新一場正確跳成已發生的、大數字排除未來(13/8/8/2)、未來卡緞帶+面紗+日期+金框皆正確、牆版面正常。hover 復原為標準 CSS(靜態圖無法截，信心高)。

### 修正 — 補 6 齣帶冠詞劇的中文名（The Lion King 等）
- `gen_catalog.py` 的 zh 查表 key 帶「the」但 group 去掉冠詞 → 對不上而漏中文名。改為查表兩邊都剝掉開頭 the/a/an。補上：獅子王 / 摩門經 / 鐘樓怪人 / 小美人魚 / 金牌製作人 / 真善美。

## [v1.6.0] - 2026-07-01 10:49
### 改版 — 公開分享頁 u.html 全面比照 me.html（護照/海報牆風）+ CSS 共用
- 舊 u.html 還停在改版前設計(css/me.css + Roboto)，與 me.html 兩套系統、看起來落後。本版把 u.html **重建成唯讀版 me.html**：同一套護照風 hero、海報牆/護照/清單三檢視、點陣世界地圖 + 城市榜、統計儀表板(4 榜 + 各年/各月/各星期折線圖)、persona/徽章、詳情視窗。
- **根治分岔**:把 me.html 內嵌 CSS 抽成共用 **`css/me-v2.css`**，me.html 與 u.html 都 link 它 → 以後改樣式一次兩頁同步(這是先前兩頁各改各的病根)。
- 新 `js/u-view.js`:讀 `?u=<handle>` → profiles gate → RPC `public_sightings` → 把每筆映射成 me.html 的 show 物件(沿用 catalog 海報/中文名解析)→ 跑移植過來的 render(唯讀，無新增/編輯/刪除)。移除舊 `js/u.js`(已被取代)。
- **🔒 修 stored XSS**:移植 me.html 的 render 時,`innerHTML` 未跳脫使用者欄位。me.html 只 render 自己資料(自我 XSS 無害)，但**公開頁 render 別人的資料給訪客** → 惡意 handle 在劇名/劇院/城市/座位塞 `<img onerror>` 會在訪客端執行。已對所有進 innerHTML/屬性/SVG 的使用者欄位加 `esc()` 跳脫。
- DB:`supabase/add_public_rating.sql`(選跑)讓 `public_sightings` 多回 `rating`(星星)/`precision`(日期精度)；u-view.js 防禦式處理，沒跑也能運作(只是星星不顯示、年精度日期顯示完整)。
- **驗證**:本機 headless 截圖 `?u=danny` — hero/大數字/海報牆/三檢視/地圖+城市榜/統計 全部如 me.html;XSS 跳脫後 render 正常;not-found 狀態正確。(海報圖 headless 抓外部 CDN 慢屬時序假象，非版面 bug。)

## [v1.5.0] - 2026-07-01 10:19
### 新功能 — 觀劇統計加「各月 / 各星期」分布，三張都改折線圖
- me.html 統計儀表板原本只有一張「各年」且是 CSS 柱狀圖 → 改成**三張折線圖**：📅各年 / 📅各月 / 📅各星期(綠 teal / 藍 / 紫 indigo),白線+面積填色+圓點+格線,**與公開頁 `u.html` 同一套 `lineChart` 樣式**。
- 資料用既有 `MM.stats()`(`perYear`/`perMonth`/`perWeekday`,吃真實收藏)。只加一支 Chart.js CDN(與 u.html 同一支)。
- 註:僅記到「年」精度的紀錄不會被硬算進某月/週幾(NaN 自然略過),比公開頁把它算成 1 月更誠實,故月/週分布對此類紀錄可能與 u.html 略有出入。
- 驗證:headless 截圖確認三圖 render + 配色 + 版面(各年|各月一排、各星期在下)如參考圖。

## [v1.4.0] - 2026-07-01 09:50
### 新功能 — 公開分享頁(FR24 式個人頁)＋ 全域欄位隱私開關
- **推廣飛輪**:每個帳號可設唯一 `handle` → 公開頁 `u.html?u=<handle>`(像 `my.flightradar24.com/Chiang`),把看過的音樂劇分享出去。骨架(profiles.handle/is_public/u.html/RLS)先前已存在,本版補完三缺。
- **首次登入 onboarding**:登入後若尚未取名 → 彈輕量 modal,用 Google 名字**預填**建議 handle、**即時查重**(✓可用/✗已被使用)、撞名自動補數字、可「之後再說」。me.html nav 新增「分享」入口(handle/公開開關/欄位開關/複製連結)。
- **全域欄位隱私開關**:使用者自訂公開頁是否顯示**票價(`show_price`)/座位(`show_seat`)**(預設都關);**筆記永遠不進公開頁**。
- **🔒 修一個真實資料外洩**:原本 anon key 對 `sightings` 做 `select("*")` 可讀到公開帳號的**整列**(price/seat/note 全外洩,已實測證實)。本版**收緊 RLS**(anon 不再能直接讀他人 sightings)+ 公開讀取改走 `public_sightings(handle)` **SECURITY DEFINER 遮罩函式**(依開關 null 掉 price/seat、note 不回)。前端藏=假隱私,改為**資料庫層**強制。另加 `handle_available(handle)` 繞 RLS 查重(普通 SELECT 會被 RLS 藏私密帳號而誤判可用)。
- DB migration:`supabase/add_share_privacy.sql`(必跑,見 `docs/SETUP_ACCOUNTS.md`)。前端:`me.html`、`js/u.js`(改讀遮罩 RPC)、`u.html`(加 og/twitter 社群預覽 meta;每人專屬預覽圖待自訂網域一起做)。
- **驗證**:onboarding modal headless 截圖(預填/即時查重/公開開關展欄位/實心遮罩 皆正確);raw REST API 實測:查重 RPC ✓、anon `select(*)` 對他人回 `[]`(漏洞封死)、`public_sightings` 回傳 price/seat=null。「開關開→顯示」的反向未驗(需帳號登入)。
- 註:漂亮網址 `/u/<handle>` 與每人專屬 og 預覽圖,依決定留待 `themusicalmap.com` 上線一起做;現階段維持 `?u=<handle>`。

### 修正 — Love Never Dies 補中文名《愛無止盡》
- `scrapers/gen_catalog.py` 的 `ZH` 譯名字典漏收 → `venues_catalog.json` 該筆 `zh=null` → My Musicals 卡片無中文副標。補 `"love never dies": "愛無止盡"`(維基繁中正式條目名;中國多用《真愛不死》,已在 search 欄可搜)。

## [v1.3.2] - 2026-06-30 16:53
### 修正 — 城市清單中英混雜（改用完整繁中城市對照）
- 真因：me.html 的 `CITYZH` 是**寫死的 21 個城市**，有倫敦/紐約/芝加哥/台北卻沒台中/聖荷西等 → 有的顯示中文有的英文。
- 修：用 `data/i18n_maps.json`（`cities` 簡中 200 + `cities_tw` 繁中覆蓋）經 **opencc 簡→繁** 產出完整「英文→繁中」城市對照（200 城，臺→台 口語化），取代寫死的 21 城。台中→台中、聖荷西、舊金山、芝加哥…一致繁中。
- 加 `cityName()`：剝除「San Jose, **CA**」這種州別後綴再查；查不到中文（如 East Lansing）就保留英文、不強翻。
- 套用到城市清單、Top Cities、清單檢視。**全自動實測**：cityName 邏輯(含後綴剝除)＋城市清單渲染 6 城（台中/聖荷西/舊金山/芝加哥/台北 繁中、East Lansing 英文），0 錯誤。
- 註：對照表為產生後內嵌；之後 i18n_maps 增城需重產（純顯示，不影響資料）。

## [v1.3.1] - 2026-06-30 15:00
### 修正 — 詳情視窗切換不同劇時會閃前一張海報
- 真因：`openDetail` 直接 `img.src=新網址`，`<img>` 在新圖 decode 完成前仍顯示**舊圖**像素 → 切換瞬間閃前一齣海報。海報牆卡片本有「載入完才淡入」機制，但詳情大圖沒套。
- 修：詳情海報加 `opacity:0` 預設、`.ready` 才 `opacity:1`；換不同海報時**先移除 `.ready`（舊圖瞬間隱藏）**、只在 `onload` 才加回 `.ready` 淡入；同一張(重開)直接顯示；`onerror` 也補 ready 避免卡空白。
- 注意：不用 `img.complete` 同步判斷（已快取的圖 complete=true 會立刻重顯舊像素，仍會閃）——只認 `onload`。
- **全自動實測**：開 A(自訂海報)載入後 ready；切到 B 的瞬間 src 已換、ready=false(舊圖隱藏)；B 載入完 ready=true 淡入；CSS opacity 0/1 正確。0 錯誤。

## [v1.3.0] - 2026-06-30 14:51
### 修復＋改進 — 編輯模式補回缺漏欄位、詳情視窗改版
v2 移植時編輯流程漏掉數個舊版有的能力（資料都在、是 UI 沒做）。一次補齊：
- **編輯按鈕**：編輯既有紀錄時顯示「**更新**」（新增才是「加入」）。
- **時間 seen_time**：新增/編輯表單日期區加「時間（選填）」欄；編輯回填現值。（先前整合區把 `time` 寫死成空字串，詳情頁看不到時間 → 已修為讀 `e.time`。）
- **編輯可改城市/劇院**：編輯模式在製作卡下方加可改的城市/劇院 combo（重用手動表單的地理對映）；改城市用城市定位、改劇院用劇院定位（修掉「改城市卻被舊劇院蓋成舊國家」的 bug）。
- **詳情視窗**：寬度 720→**1060px（約大一倍）**、海報欄 260→400px；**移除「製作」列**（v2 已無製作概念，且常為空）；**點海報→開新視窗看完整大圖**（hover 顯示「點圖看完整海報」提示）。
- **全自動實測**：新增按鈕「加入」/編輯按鈕「更新」；新增帶時間→雲端 seen_time；編輯回填時間+城市/劇院欄在；改城市 London→country 正確變 UK；改時間→雲端更新；詳情視窗 1060px、無製作列、時間顯示、點海報開正確 URL。全程 **0 錯誤**。

## [v1.2.1] - 2026-06-30 14:27
### 修正 — 對映改版後本地快取沒重新同步（使用者看不到剛補回的 url）
- 真因：`onSignedIn` 用 `sessionStorage.mev2_synced===uid` 判「本 session 已同步」就不再重抓；舊 session 的 `mm-log` 快取是**改版前的對映**(缺 url/poster)，所以即使程式更新、UI 也讀到舊快取。
- 修：加 **`SYNC_VER`（同步版本，現為 '2'）**，旗標改存 `uid@VER`；`sightingToEntry` 對映改版時 bump 版本 → 所有 session 載入時偵測版本不符 → 自動重新同步雲端（一次 reload）→ 補上新欄位。未來改對映只要 +1 即自動傳播，不用使用者登出。
- **全自動實測**：模擬舊快取(mm-log 拔掉 url + 舊格式旗標)→ reload → 自動重新同步 → url 回來、旗標升級 @2。0 錯誤。
- 立即手動替代法：登出再登入亦會強制重新同步。

## [v1.2.0] - 2026-06-30 14:19
### 修復＋新功能 — 把「連結／售票網址」(url) 重新顯示並可編輯
v2 改版時新版 me.html 沒把既有的 `url` 欄位撈出來顯示（**資料一直都在、沒被刪**，只是 UI 沒surface）。本版補回：
- **me.html**：`sightingToEntry` 讀 `url`、整合區 map `s.url`、詳情頁加「連結」列（可點、開新分頁、顯示網域）；`entryToRec` 寫 `url`（編輯/復原都保住）。
- **me-input.html**：新增/編輯表單「細節」區加「連結 / 售票網址（選填）」欄（id=`url`，沿用現成 forEach 接線；編輯回填）。
- **修掉資料邊角**：先前「刪除→復原」是重新 insert、未帶 `url` 會讓該筆 url 變空；現 `mmEntryToRec` 含 `url`，復原完整保住。
- 不需 migration（`url` 欄早於 add_url.sql 就存在）。
- **全自動實測（test 帳號）**：新增帶 url→雲端存+詳情顯示連結；**只改評分不碰 url→url 不被洗掉**（PostgREST 部分更新）；刪除→復原→url 仍在。0 錯誤。

## [v1.1.0] - 2026-06-30 13:26
### 新功能 — 每筆紀錄可自訂海報網址（per-sighting poster URL override，方法 2）
使用者可在某齣紀錄填一個圖片 URL，覆蓋系統 catalog 帶出來的海報；清空即還原系統圖。各筆獨立互不影響。
- **DB**：`sightings` 加 `poster_override text`（`supabase/add_poster_override.sql`，已套用）。
- **me.html**：`sightingToEntry` 渲染順序 `poster_override → catalog 海報 → 首字母色塊`；`entryToRec` 寫入 `poster_override`。
- **me-input.html**：新增/編輯表單「細節」區加「自訂海報網址（選填）」欄 + **即時預覽**；編輯時回填現有值；清空自動還原系統海報（`systemPosterFor` 計算 base）。
- **容錯**：`cloudUpsert` 寫雲端時若欄位未 migrate 自動去掉 `poster_override` 重試（樂觀寫入+降級），程式與 migration 解耦、存檔永不壞。
- **全自動實測（test 帳號）**：加 Wicked+自訂URL→雲端存住→重整圖卡換圖；加 Phantom 無自訂→用系統圖且 Wicked 仍保有自訂（獨立性）；編輯 Wicked 回填URL→清空→還原系統圖。全程 **0 錯誤**。
- 註：自訂的是 URL（仍熱連結到使用者貼的外站圖），非上傳檔案；方法 1（上傳到 Storage）為後續選項。

## [v1.0.0] - 2026-06-30 12:36 🎉 里程碑
### MAJOR — 「我的音樂劇」帳號版上線，專案從 0.x 畢業
這是一個**里程碑標記**，不是新的程式變更：今天的 v0.79.0–v0.79.3 把「我的音樂劇」從桌面 demo 完整 migrate 成正式版帳號制頁面（`me.html` + `me-input.html`，Supabase Google 登入 + 雲端收藏，舊版備份 `me_ori.html`），加上即時同步修正、移除國旗、補齊文件。使用者決定以此宣告 **v1.0.0**：作為願意當成穩定基準的版本。
- 內容同 v0.79.0–v0.79.3（見下，granular 歷程保留）。本 tag 疊在同一 HEAD（`89b52f1`）作里程碑指標，未改動程式。
- 此後版號從 1.x 起算（MAJOR=架構大改/不相容、MINOR=新功能/UI 大改、PATCH=修正）。

## [v0.79.3] - 2026-06-30 12:32
### 文件 — 補做完整 MD freshness（v0.79.0 改版漏掉的文件同步）
- 自承：v0.79.0 發布時只更新 README + CHANGELOG，未逐檔審所有 .md。本次補齊：
- `docs/SETUP_ACCOUNTS.md`：migration 清單加 `add_rating_precision.sql`（v2 必跑：rating + precision 欄位）。
- `docs/DESIGN_productions.md`：頂部加註「足跡頁 v0.79.0 已從 js/me.js 改版為 me.html+me-input(海報改 catalog 解析、不寫 production_key)；本檔『足跡表單(me.js)』段描述舊版(現 me_ori.html)」。製作三層模型本身仍有效。
- 其餘 docs(AFFILIATE/DAMAI/DESIGN_affiliate/SOURCES/TOUR_SWEEP/WORKFLOW) 與此次 me 改版無關、無過時。

## [v0.79.2] - 2026-06-30 12:25
### 調整 — 移除所有國旗 emoji（使用者要求）
- `me.html` + `me-input.html`：`FLAG` 對照表清空為 `{}`、`flag()` 回傳空字串；移除海報卡角 `.flag` badge、護照 visa、清單/詳情城市列、Top Countries、選製作清單、geo「對上」訊息、stamp-badge 的國旗顯示。
- 加 `.flag:empty/.pcard .fl:empty/.stamp-badge:empty{display:none}` 收掉空位、不留破版。
- 實測(test 帳號登入+新增)：海報牆/英雄/城市/護照/清單/詳情/選製作/geo **全無國旗 emoji**、版面完好、0 錯誤。正式版其他頁(app.js/theatres/u)本就無國旗(只有 🌐 品牌地球,非國旗,保留)。

## [v0.79.1] - 2026-06-30 12:05
### 修正 — My Musicals Google 登入後卡在「同步你的收藏中…」
- 真因：Google OAuth 是「轉址回來＋網址帶 `#access_token`」，與密碼登入(無轉址,先前自動測沒涵蓋)不同。轉址後 reload 帶著 hash 重載→Supabase 重新處理→期間 `getSession` 短暫回 null→舊 onAuth 把「已同步」旗標清掉→再同步→**無限迴圈卡在同步中**。
- 修(多重保護)：(1) 只在 `SIGNED_OUT` 事件清旗標,忽略暫態 null session；(2) reload 前 `history.replaceState` 去掉 `#token`；(3) 每 user 每 session 最多重載一次(防迴圈)；(4) `syncFromCloud` 加並發鎖+try/catch(失敗顯示錯誤非靜默卡死)+`loadCatalogMaps` 9s 逾時。
- 回歸：mev2-test 密碼登入完整來回(登入→新增→刪除)仍 0 錯誤。**OAuth 轉址本身仍無法 headless 驗,請重新整理 me.html 再登入確認。**

## [v0.79.0] - 2026-06-30 11:49
### 新功能 — 「我的音樂劇」(My Musicals) 帳號版改版上線（demo4 → 正式版 me.html）
舊 FlightRadar 風 me 頁改名備份為 `me_ori.html`；新版為桌面 demo4 移植，繁中、海報牆/護照/清單三檢視 + 統計儀表板 + 點陣地圖，登入後雲端同步。各階段本機 Playwright 實測（含用 dashboard 測試帳號 + signInWithPassword 跑完整登入後雲端來回），全程 0 錯誤。
- **P1 換頁骨架**：桌面 demo4（demo4.html + demo4-input.html）移植進正式版 → `me.html`→`me_ori.html`(舊頁備份保留)；新 `me.html`(呈現端) + `me-input.html`(輸入 iframe)。本機實測渲染/輸入 modal/搜尋皆正常、0 錯誤。
- **P2 劇庫接正式版資料（已實測 0 錯）**：新增 `me-catalog.js` 非同步 fetch `data/venues_catalog.json`+`data/shows.json`；me-input 的 `CATALOG`/`INDEX` 改延後組裝（titles+當期 shows 組出含座標的 prods）、`buildManualDB` 改吃正式版 **5117 劇院**(含中文名/台↔臺變體/座標)+440 城市；輸入端啟動前等資料就緒(載入中狀態)。**作品 130→568、劇院 363→5117**；實測劇院打「台中歌劇院」→ 正確跳出 3 個臺中國家歌劇院。**移除已不再使用的 catalog.js**。
- **P3a Supabase migration SQL（✅ 已套用＋驗證）**：`supabase/add_rating_precision.sql` 在 sightings 加 `rating smallint` + `precision text`。使用者已於 dashboard 執行；用測試帳號(mev2-test，dashboard 建+auto-confirm)實測 insert 含 rating/precision→讀回→delete 全通、RLS 正常。**取得可用 test session→登入後雲端來回可全自動 Playwright 測**。
- **P3b me.html 接 Supabase（✅ 完成＋全自動實測）**：登入閘 overlay（未登入→Google 落地頁／已登入→抓 sightings→寫 mm-log 快取→渲染）；`syncFromCloud` 用 `.eq('user_id',uid)` 只撈自己的；sightingToEntry 對映（zh/海報 render 時由 venues_catalog 解析、date 由 precision 還原部分日期、帶 sid）；mmDeleteShow/復原 改打雲端。
- **P3c me-input 接 Supabase（✅ 完成＋實測）**：save 雙寫（雲端 insert/update by sid + localStorage 快取）；entryToRec 對映；防重複按。
- **🐛 修 RLS 過濾 bug**：`sightings_read` 政策含「公開帳號可讀」，故 `select('*')` 會撈到別人公開收藏→個人頁加 `.eq('user_id')` 只撈自己（正式版 me.js 也有此潛在 bug，目前只一個公開帳號才沒爆）。
- **全自動測（用 dashboard 建的 mev2-test 帳號 + signInWithPassword 繞過 Google UI）**：登入→空狀態→新增 Wicked(雲端存★3)→牆顯示真海報+中文名+地圖→編輯改★5(同筆 update 非新增)→刪除(雲端歸0)，**全程 0 錯誤**，測試資料已清。**僅剩 Google 按鈕本身的點擊需使用者真瀏覽器確認**（signInWithOAuth 一行，已 code review）。
- 已知小事：登入後 0 筆收藏時牆顯示 22 張 demo 範例（demo 既有空狀態預覽，之後可換成更乾淨的空狀態 CTA）。
- **P4/P6 收尾（✅ 實測 0 錯）**：新 me.html header 加正式版導覽「所有劇院」(→theatres.html，劇院清單頁已存在)、「演出地圖」(→index.html)，加**登出**鈕(→signOut→回登入閘)。實測登入後 nav 齊全、登出回未登入閘。sitemap(gen_site:244 仍含 me.html，不用改)、me-input/me_ori 不需索引。城市/國家清單已靠輸入端正式版資料(台中歌劇院等)+個人頁統計運作。
- **狀態：功能完整、全自動實測通過(登入/載入/新增/編輯/刪除/導覽/登出)。待使用者用自己 Google 帳號在瀏覽器點一次登入驗收(唯一無法 headless 自動的一步；redirectTo=.../me.html 與舊頁同路徑、應已在 Supabase 白名單)，確認後即可 merge feat/me-v2→main。** i18n(英文)依決定延後。
- P3b/c 接 Supabase 載入/save/delete（見下）。
- i18n 英文版依決定延後（v2 先繁中）。
- **僅 Google 登入按鈕本身的點擊無法 headless 自動驗（signInWithOAuth 已 code review、redirectTo 與舊頁同路徑 `/me.html` 已在白名單）；上線後請用 Google 帳號實際登入一次確認。舊版 `me_ori.html` 為即時回退備援。**

## [v0.78.4] - 2026-06-28 15:45
### 文件 — README 數字審計，修 official_sites 過時筆數
- 被追問「100% 確定嗎」後做數字審計：`README.md` 的 `official_sites.json` 寫 **184 筆、實際 208 筆**（別的 session 長上去、我先前沒驗就引用）→ 改為 208。
- 同時核對：works.json 170 ✓、shows ~1,600（實 1642、近似值含「隨 CI 變動」）✓、31 國 ✓、venue_coords 1093（README 未引用、無誤）。
- **誠實標註**：docs/*.md 內各 scraper 來源的精確筆數（如 SOURCES「大麥 711 筆/138 齣」、DESIGN_affiliate「101 筆」）多為**特定日期的 harvest 記錄**，需跑各 scraper 才能逐一核實，本次**未全部驗證**；非本次 UI 改動造成。

## [v0.78.3] - 2026-06-28 15:33
### 文件 — 補做 v0.78.0~0.78.2 漏掉的 MD freshness sweep
- 老實說：v0.78.1/0.78.2 當下只更新 CHANGELOG、沒真的逐一掃所有 .md，違反 WORKFLOW 第 4 步。本次補做完整 sweep。
- `README.md`：版面段落把「類型篩選」從「側欄內」更正為「**移到地圖上方的 filter bar**」；補上 header 即時計數、側欄只剩搜尋＋列表、多城市「圓點+豎線脊柱＋各站不同海報」、footer 已移除（Privacy/Terms 改置頂部 nav）。（v0.78.0 sweep 只 grep 英文 filter/sidebar、漏了中文「側欄/類型篩選」。）
- `docs/AFFILIATE_SETUP.md`：Privacy/Terms 連達位置由「首頁頁尾」更正為「首頁頂部 nav」（footer 已移除）。
- 其餘 .md 逐一確認非過時（SOURCES/SETUP_ACCOUNTS/DESIGN_*/TOUR_SWEEP/WORKFLOW/DAMAI）。

## [v0.78.2] - 2026-06-27 21:11
### 修正 — 多城市脊柱：圓點與豎線沒接好（有縫）
- v0.78.1 的脊柱豎線 `top:25 bottom:-9`，3x 放大像素檢查發現**底端差幾 px 接不到下一個圓點、有縫**。改 `top:18 bottom:-16`：豎線從圓點中心穿出、底端延伸進下一個圓點（圓點不透明 + z-index 高、會蓋住多出段）→ 圓點與豎線無縫相連。已 3x 放大截圖逐段確認。
- 改動檔：`css/style.css`（+ 重產三語 index.html）。

## [v0.78.1] - 2026-06-27 20:50
### 修正 — 多城市列表救回「圓圈+豎線脊柱」（保留各站不同海報）
- `v0.72.0`「多城市每站顯示各自海報」當時把 `v0.70.0` 的圓圈脊柱（路線時間軸）拿掉、只剩各站小海報。本次把**脊柱加回來、同時保留各站海報**（兩者並存）：`.stop::before`（青色空心圓點）+ `.stop::after`（連接豎線、末站不畫線）、`.stops-inner` 左側留 26px 給脊柱；圓點/線用 `--acc`/`--acc2` 隨卡片交替色。
- **各站海報確實不同、有意義**（先前誤判「同一張、冗餘」是沒查就講，已更正）：實測 Wicked 4 站海報來自 4 個來源（紐約 headout／倫敦 ctfassets／Omaha 巡演 craft.cloud／**馬德里 atrapalo 西班牙黃色版**），故脊柱與海報並存、非二選一。
- 改動檔：`css/style.css`（+ 重產三語 index.html）。實測 render Wicked 4 站：脊柱圓點+豎線有畫、4 張海報各自正確。

## [v0.78.0] - 2026-06-26 14:55
### UI 大改 — 分類過濾移到地圖上方橫條、計數移 header、側欄全給列表、footer 移除
- **分類過濾 pills 從窄側欄搬到「地圖區上方的 filter bar」**：9 個傳統分類**全名**一行排開（label 走 i18n：分類／分类／Category），塞不下時出現**細淡色橫向捲軸**（非換行、非切字、非縮放，純 CSS 原生捲軸）。側欄因此全留給劇目列表，一次可見劇目從 ~2-3 張增為 ~8-9 張。
- **側欄列表改「依分類分組排序」**（`render()`：同類劇目排一起、最大類在前），**無分類標題行**（純排序，使用者反映點開式 UX 差故不做收合）；卡片緊湊化（海報 62×93→44×63、字級下調）。
- **本月計數移到 header**（tagline 旁，`Playing this month: N musicals · M locations`），不再佔側欄一行；過長以 ellipsis 收。
- **footer 整條移除**：Privacy/Terms 移到頂端 nav（桌面顯示）；「Updated/Sources」資料註記移除（`app.js` 加 `if (els.note)` 守衛，避免缺元素時 crash）。
- **RWD**：桌面 filter bar 在地圖上方；手機（<680px）側欄上、地圖下，filter bar 可橫滑；手機 nav 隱藏 All theatres／Privacy／Terms 並縮 padding/gap，避免 header 溢出（實測 `documentElement` pageOverflow 0）。
- 改動檔：`build/gen_site.mjs`（body 結構 + i18n `filterLabel` 三語）、`css/style.css`（filter bar／原生捲軸／緊湊卡／RWD；順手中性化既有 "stayplot" 註解）、`js/app.js`（列表依分類排序 + data-note 守衛）。**實測桌面 1600/1250 + 手機 430 真實產生頁**（含多城市「N Cities」合併、捲軸出現/隱藏、無水平溢出）。

## [v0.77.16] - 2026-06-26 11:04
### 修正 — 切語言再閃「0 部音樂劇」（接 v0.77.15）
- v0.77.15 藏了 prerendered 清單,但漏藏計數 `#count`:資料 fetch 完成前 render() 先用空資料跑一次→閃「本月上演:0 部音樂劇·0 個地點」。改 CSS 把 `#count` 也隱藏到 `body.ready` 為止。實測 ready 後顯示真數字(274 部·343 地點),非 0。

## [v0.77.15] - 2026-06-26 10:55
### 修正 — 切換語言時閃過 prerendered SEO 清單（FOUC）＋ MD freshness
- 切語言會跳轉到另一個變體頁（`/en//zh-hans//zh-hant/`），JS 接手前那份「給爬蟲的 prerendered 純文字劇目清單」(`<ul id="show-list">`)先閃出來，體驗差。改：CSS 預設 `body:not(.ready) #show-list { visibility:hidden }`，`app.js` 首次 render 後加 `body.ready` 才顯示 → 不再閃（爬蟲仍從原始 HTML 取得清單、Googlebot 跑 JS 拿到真內容，SEO 不受影響）。實測 ready 切換 visibility 正確。
- **MD freshness（補做漏掉的 sweep）**：`docs/SOURCES.md` 補上本 session 與 v0.76 漏記的西班牙來源 —— `atrapalo.py`（全西班牙主力、Sovrn 分潤）、`barcelona.py`（teatrebarcelona）。

## [v0.77.14] - 2026-06-26 10:47
### 補完 — 最後 11 個 Google 查無的場館座標（agent 用 saoju.net + OSM 查證）
- 上海/深圳/杭州的「星空间」黑盒小劇場（藏在亚洲大厦/第一百货/世茂广场/大世界等大樓內）＋ 西班牙 La Puebla de Montalbán 文化中心，Google Places 查無。agent 用 saoju.net + OpenStreetMap 交叉驗證（確認皆 WGS84、免 GCJ-02 轉換）補上座標。深圳安托山（2024 新建、OSM 未收）為估算、信心低，其餘中高。
- **結果：venue_coords 979→1092，仍沒驗證的場次 = 0**。本 session 場館位置精度全數 Google/agent 驗證（含修掉 Parker ~2km 偏移）。

## [v0.77.13] - 2026-06-26 10:43
### 調整 — 側欄列表卡片城市後面加上國家（與 popup 一致）
- 側欄 `locTrio` 原本只顯示城市（馬德里），改為「城市, 國家」（馬德里, 西班牙），跟 popup 同格式；國家隨介面語言翻譯（上海,中國／首爾,韓國／紐約,美國），缺國家則只顯示城市。
- 實測（真頁面）：側欄顯示「馬德里, 西班牙」「上海, 中國」「首爾, 韓國」。

## [v0.77.12] - 2026-06-26 10:36
### 修正 — 場館座標精度（Google 建築級）＋ 再剔除非音樂劇（冰上/馬戲/佛朗明哥）
- **場館座標**：使用者發現 All Shook Up @ Parker Arts Culture and Events Center 釘點偏約 2km（TM 來源座標粗略）。跑 `geocode_google.py`（金鑰在 `scrapers/.gmaps_key`）對 113 個未驗證場館做 Google 建築級 geocode：87 個自動寫入 + 15 個「同場館譯名/簡稱不同」手動確認寫入（Parker→PACE Center 39.516892,-104.757619「20000 Pikes Peak Ave」、Oscarsteatern→Oscar Theater、Hala Stulecia→Centennial Hall、Eccles/Alliance/Det Norske…）。**venue_coords.json 979→1081**，其中 34 個與來源差 >30m 被修正。11 個中國黑盒小劇場 Google 查無 → 另派 agent 查。
- **再剔除非音樂劇**（接 v0.77.11 芭蕾）：`NOT_MUSICAL_RE` 加 `on ice / cirque / circus spectacular / flamenco / opera locos` → 移除 Disney on Ice、Yllana: The Opera Locos、Come Alive Circus Spectacular、Scrooge Cirque、Flamenco On Fire。保留誤判的真音樂劇（Operation Mincemeat、Threepenny Opera、Maradona/FRIDA Opera Musical）。
- 誠實反省：先誤稱「Google 金鑰沒設」（只看 env 沒看 `.gmaps_key` 檔）被使用者抓；金鑰早就在。

## [v0.77.11] - 2026-06-26 10:25
### 修正 — 芭蕾舞劇混入音樂劇地圖（Cinderella Ballet）
- 使用者發現「Cinderella Ballet」(Yucaipa, TM)出現在地圖、tag 百老匯/西區 —— 芭蕾不是音樂劇。`NOT_MUSICAL_RE` 加 `\bballett?\b|芭蕾`（**刻意不加 `opera`，否則誤殺 Phantom of the Opera**）。
- 驗證：Cinderella Ballet→剔除(0)、Phantom of the Opera→29 筆全在、真 Cinderella 音樂劇→10 筆全在。
- 誠實反省：我前一輪用 `title=='Cinderella'` 精準比對去查、漏掉 title 是「Cinderella Ballet」的那筆，誤稱「已排除」被使用者打臉。寬鬆比對(`'ballet' in title`)才對。

## [v0.77.10] - 2026-06-26 10:01
### 修正 — 我的 merge regression 把開放式駐演劇關閉（Wicked London 等顯示「至 X」）
- **regression 源**：v0.77.2 我加的去重 merge（Pass 1 `_merge_into` + Pass 2）會「拉寬日期」`end_date = max(ends)`。倫敦 Wicked 在 westend(end=None, resident) 與 ATG(end=2027-01-03, type=tour 訂票上限) 同場館合併時，把 None **補成 2027-01-03** → `end_rolling` 判定（只認 `not end_date`）漏掉它 → 顯示「至 2027/1/3」而非「長期上演」。**不是 CI 覆蓋資料，是我的合併邏輯每次 build 重犯。**
- **修**：merge 時若 keeper 是「開放式駐演」（`end_date is None` 且 `type in (resident, sit-down)`），**不繼承另一來源的訂票上限 end**（那個 None 是「長期上演」的刻意值）。Pass 1/2 兩處都修。
- 實測恢復：Wicked／Lion King／Phantom／Les Misérables／Mamma Mia!／Hamilton／Book of Mormon（倫敦）全部 `end_rolling=True`「長期上演」。

## [v0.77.9] - 2026-06-26 09:50
### 修正 — v0.77.8 的隱藏 CSS 優先級不足（teatromadrid 仍顯示）
- v0.77.8 的 `.pop-tile-hidden { display:none }` 優先級 (0,1,0) **低於** `.mm-popup .pop-tile` (0,2,0) → 在實際 popup 內被蓋過、根本沒隱藏（使用者實測仍看到 TeatroMadrid，加 `?x=1` 也在 → 證實非快取、是真 bug）。
- 改為 `.mm-popup .pop-tile.pop-tile-hidden { display:none }`（0,3,0）確實勝出。**驗證瑕疵反省**：前次把測試元素放在 `.mm-popup` 外面量 computed style 才誤判 none；本次在真 `.mm-popup` 容器內量 → atrapalo `flex`、teatromadrid `none`。
- 重產 prerendered HTML bump cache-bust 版本號使更新即時生效。

## [v0.77.8] - 2026-06-26 08:52
### 調整 — 無分潤購票鈕改「CSS 隱藏」而非移除（可隨時開回）
- 接續 v0.77.7：原本把非分潤鈕（teatromadrid…）從 DOM 過濾掉；改為**保留在 DOM、用 `.pop-tile-hidden { display:none }` 隱藏**。未來要開回，刪掉 `css/style.css` 那一條 CSS 規則即可，不必動邏輯。
- `app.js` 改為對非分潤鈕加 `pop-tile-hidden` class（當有分潤鈕時）。實測 Wicked Madrid：atrapalo 鈕 `pop-tile`（顯示）、teatromadrid 鈕 `pop-tile pop-tile-hidden`（computed `display:none`）。
- **修部署 cache-bust**：push 部署不重建 prerendered HTML（workflow build 步驟 `if != push`），導致 app.js/css 改了但頁面仍引用舊 `?v=` hash、瀏覽器吃舊快取。本機跑 `gen_variants`+`gen_site` 重產 HTML（新內容 hash `854d9c843f`）並提交，使更新立即生效。

## [v0.77.7] - 2026-06-26 08:41
### 修正 — 重疊劇隱藏無分潤購票鈕（分潤優先）
- 問題：Wicked Madrid 等「atrapalo + teatromadrid 都有」的劇，購票區同時擺 Atrápalo（可分潤）與 TeatroMadrid（不可分潤）兩鈕 → 無分潤鈕稀釋點擊。
- `app.js` popupHtml：購票鈕若**存在可分潤來源**（domain 在 `MM_CONFIG.AFFILIATE`：atrapalo/ticketmaster/todaytix/atg…），就**濾掉非分潤鈕**（teatromadrid/teatrebarcelona 等）。非分潤鈕**僅在它是唯一購票途徑時保留**（teatromadrid 獨家劇不受影響）。官網仍掛在標題。
- 實測 Wicked Madrid：過濾前 `[atrapalo, teatromadrid]` → 後 `[atrapalo]`。

## [v0.77.6] - 2026-06-26 02:08
### 修正 — 搜尋語言無關（簡繁 + 異體字 + 英文通吃）
- 問題：繁中模式搜「台北」找不到顯示為「臺北」的劇（潘朵拉的音樂盒）；搜「taipei」也找不到。**顯示語言只管呈現，搜尋卻被綁死在當前變體的字形**。
- **前端 `fold()`** 加異體字正規化 `臺→台`：搜「台北」「台灣」「台中」皆對到「臺北/臺灣/臺中」。
- **build 層 `gen_variants` 新增語言無關 `search` 欄位**：每筆含該欄位在 **英文＋繁體＋簡體三種形式的聯集**（用 OpenCC 雙向 + place/venuesEn），三個變體檔共用同一 blob。前端 `visibleShows` 納入 `s.search` 比對。
- 效果（實測，繁中模式下）：搜 `taipei`／`Taipei`／`台北`／`臺北`／`taiwan`／`戏曲中心`(簡)／`戲曲中心`(繁)／`潘朵拉` **全部命中同一齣** —— 符合「任意語言/字形皆可搜」。

## [v0.77.5] - 2026-06-26 01:48
### 補完 — 23 部登錄正典劇的官網（agent 查證 + HTTP 200）
- 為先前「無官網條目」的正典劇補上官方網站（多為 multi-country 劇、無單一品牌站，採版權方官方頁，與專案既有 frankwildhorn/VBW 同做法）：Cinderella(R&H)、Shrek／Guys and Dolls／Into the Woods／Company／Dracula／The Full Monty／Rocky／Murder Ballad／A Christmas Carol(MTI)、The Addams Family(TRW)、A Chorus Line／Nine／La Cage aux Folles／Thrill Me／Altar Boyz／Finian's Rainbow／I Love You You're Perfect Now Change(Concord)、The Last Five Years(JRB)、Brokeback Mountain(@sohoplace)、Daddy Long Legs、We Will Rock You、Our Ladies of Perpetual Succour(NT Scotland)。
- **誠實標示**：Hedwig and the Angry Inch、The Prince of Egypt 雖有真官網但 TLS/連線失敗（curl 回 000）→ **不寫入**，不加死連結；Amélie／Romeo und Julia(德文版) 查無可驗證專屬官網 → 維持無連結。
### 修正 — Frozen 德國官網改用品牌站
- agent 二度查證「官網指向製作商頁」的 52 個條目：絕大多數（Shiki/VBW/HDK/Stage Entertainment）確為合法官方製作方、無獨立品牌站，維持現狀。**唯一真漏：Frozen 德國** 有獨立品牌微站 `eiskoenigin.com`（與 Moulin Rouge /netherlands/ 同型）→ stage-entertainment.de 改為 `https://eiskoenigin.com/`（HTTP 200 驗活）。
- MJ the Musical 德國候選品牌站 `mj-dasmusical.de` 本機與 agent 端皆連不上（curl 000，疑地理封鎖）→ 暫不寫入，待手動覆核。

## [v0.77.4] - 2026-06-26 01:41
### 修正 — 官網分區漏洞（AU/NZ 在地官網）＋ Beetlejuice 官網沒掛 bug ＋ TM 忠實製作名
- **AU/NZ 在地官網補齊**（原本 fallback 到美國/全球站或錯站）：Anastasia→anastasiathemusical.com.au、Hair→hairthemusical.com.au、Moulin Rouge!→moulinrougemusical.com.au、Menopause→menopausethemusical.com.au、Spamalot→drewanthonycreative.com.au、A Beautiful Noise→theneildiamondmusical.com.au；NZ：Matilda→capitaltheatretrust.co.nz、The Little Mermaid→aucklandlive.co.nz（原本竟連到日本四季 shiki.jp）。皆 agent 查證 + HTTP 200 驗活。
- **Beetlejuice 官網沒掛 bug 修復**：`build_shows` 在「唯一連結就是官網」（manual 劇 ticket_url == 官網）時，原本只設 `link_kind` 卻沒把連結標成 `official` → 前端標題不掛官網。改為直接 materialize 成 official 連結。影響所有此型手動劇。
- **Moulin Rouge nl 官網**：stage-entertainment.nl（推廣頁）→ moulinrougemusical.com/netherlands/（自家品牌站）。
- **TM 忠實製作名**：`ticketmaster.py` 新增 `display_name()`（保留「(Australia)」「The Broadway Musical」等製作描述、砍每場次無障礙/ALL-CAPS/Tickets 雜訊），存為 `tour_name` → 卡片顯示如「Anastasia - The Broadway Musical (Australia)」。**下次 TM scrape 生效**。
- **全面稽核**：官網「無條目」501 部作品（多為中/日/台/西在地原創，無全球官網屬正常）、其中**登錄正典卻缺官網 41 部**；官網指向第三方域名 52 個（多數為 Shiki/VBW/HDK/Stage 等合法製作方）。缺官網與品牌站取代兩批已派 agent 查證中。

## [v0.77.3] - 2026-06-26 01:16
### 新增 — 補抓 atrapalo「非 musicales 分類」的劇（La Sireneta、Asesinato para dos）
- 有些 teatromadrid/barcelona 獨家劇其實 atrapalo 也賣，只是歸在 `/entradas/musicales/` 分類**外**（兒童劇/話劇），列表爬不到。`scrapers/atrapalo.py` 新增 `EXTRA_PRODUCTS` 商品 URL 清單 + `fetch_detail_event`：直接抓詳情頁，從 `og:title`＋venue blob（座標）＋JSON-LD 日期/價格組成記錄，過期的自動略過。
- 補進 **The Little Mermaid（La Sireneta, BCN）** 與 **Murder for Two（Asesinato para dos, MAD）** → 兩者現由 atrapalo 主源、帶分潤、與 teatromadrid/barcelona 正確合併成單一釘點。atrapalo 136→**138**。
- `data/works.json`：The Little Mermaid 加加泰隆尼亞語別名 **「La Sireneta」**（中央登錄，`canonical_title` 全專案受惠）。
- **查證（4tickets/oneboxtds 無法分潤）**：teatromadrid 結帳走的 `4tickets.es`／`oneboxtds.com` 都是純 B2B 白標票務、無 publisher 聯盟、不在任何聯盟網路（諷刺的是 atrapalo 正是 OneBox 的下游零售通路）→ 確認「用 atrapalo 變現、teatromadrid 留作免費資訊」的路線正確。
- 結果：仍真正 teatromadrid 獨家的全球正典僅剩 **Moulin Rouge!**（atrapalo 上是巴黎歌舞秀非音樂劇）與 **Sunday in the Park with George**（atrapalo 無）。

## [v0.77.2] - 2026-06-26 00:59
### 修正 — atrapalo 漏抓大劇（無座標/撞號）＋ 分潤反客為主
- **救回被漏抓的大劇**：El Rey León（→The Lion King）、Cenicienta（→Cinderella）、El Alma al aire 列表 JSON-LD 的 `location/geo` 是 null 被跳過。新增 `backfill_coords`：抓詳情頁的 `"venue":{…,"latitude","longitude","city"}` blob **直接取建築級座標**（免 geocode；Nominatim 僅後援）。atrapalo 127→**136 齣**（全數上圖）。
- **修 id 撞號**：同 slug 不同城市的巡演（Princess Story…）被當重複收掉，id 改含 `_e` 編號。
- **分潤反客為主修正**：① `build_shows` Pass 1（同 group+city+venue 去重）原本直接丟掉次源、連結不留 → 改為**合併被丟源的購票連結**（對齊 Pass 2「no booking source lost」），atrapalo 分潤連結得以掛上 teatromadrid 釘點。② **SOURCE_PRIORITY 把 atrapalo 提到 teatromadrid 之前**＋Pass 2 去重 score 改「source 優先」→ 重疊劇（Lion King/Wicked/Cinderella/Sound of Music…9/9）主源變 **atrapalo（可分潤）**，teatromadrid 只保它的獨家。
- **查證**：teatromadrid 購票走自家 `4tickets.es`／`oneboxtds.com`，**與 atrapalo 無關**（「teatromadrid 走 atrapalo 分潤」傳聞不成立）。
- Google Maps API 已獲授權當 geocode 後援（venue blob 已直供座標，目前用不到、CI 也免 key）。

## [v0.77.1] - 2026-06-26 00:32
### 修正 — atrapalo 重複釘點 ＋ 接進每日 CI（資料中心 IP 實測通過）
- **去重複釘點**：atrapalo 標題帶「, el musical en Madrid」城市後綴，原本沒跟 teatromadrid 的「Wicked」合併→雙釘點。`clean_title` 改為「strip『el musical』及其後全部（含 en〈城市〉）＋ `&`→`y`」，Wicked／Sound of Music 等正確 canonical 合併（shows 1753→1750）。
- **接進每日主 pipeline**：`.github/workflows/update.yml` 加 `curl_cffi`＋`playwright`＋`playwright install chromium`，madrid 之後跑 `atrapalo.py`。**probe 實測**：GitHub Actions ubuntu runner（Azure 資料中心 IP）**成功過 Fastly 挑戰**（136 events / 127 shows，47 秒），推翻「資料中心 IP 必被擋」的預期 → 每日 CI 可行。移除一次性 `atrapalo_probe.yml`。
- **策略決定（保留涵蓋＋分潤優先）**：teatromadrid/barcelona **不撤**（用別名庫 works.json 驗證:其有 6 部 atrapalo 沒有的 Broadway/West End 正典獨家——The Lion King／The Little Mermaid／Cinderella／Moulin Rouge!／Sunday in the Park with George／Murder for Two）；重疊劇靠 `AFFILIATE_PRIORITY` 讓購票主連結走 atrapalo 分潤。

## [v0.77.0] - 2026-06-26 00:06
### 新增 — atrapalo.com 全西班牙音樂劇來源（打通 Fastly bot 牆 + Sovrn 分潤）
- 新 scraper `scrapers/atrapalo.py`，抓 atrapalo.com `/entradas/musicales/`（西班牙最大票務站），**單一來源涵蓋全西班牙 39 城（馬德里/巴塞隆納/瓦倫西亞/塞維亞/畢爾包…）共 127 齣**，資料直接取自頁面內嵌的 **JSON-LD `ItemList`（TheaterEvent）**：劇名、場館、**經緯度（免 geocode）**、檔期、海報、價格全結構化。
- **打通 Fastly NextGen WAF「Client Challenge」**：純 GET 會被丟 JS 挑戰頁（clearance cookie `_fs_ch_cp_*`，TTL 1h）。採 **hybrid**：Playwright（真 Chromium）載入第 1 頁過挑戰、取 cookie，再交給 **curl_cffi（Chrome TLS 指紋）帶 cookie 純 GET 後續分頁**（p-2…p-4）——瀏覽器只當一次性開鎖，99% 抓取走輕量 GET。
- **接入每日 build**：`build_shows` SOURCE_FILES 加 `atrapalo.json`；與既有 teatromadrid／barcelona 來源依（劇目, 城市）自動去重、合併購票連結；西語劇名沿用 `madrid.py` 對照表 canonical 化（Sonrisas y lágrimas→The Sound of Music、Los Miserables→Les Misérables、Dear Evan Hansen…），本地製作保留原名。
- **分潤**：`js/config.js` 把 `atrapalo.com` 掛上現有 **Sovrn/VigLink** key（merchant 53900「Open」，零申請、同一把 key、`u=` deep-link 保留「點到該劇頁」）。實測 build 後 106 個場次帶 atrapalo 連結。
- **CI 實測**：新增一次性 probe workflow `atrapalo_probe.yml`（`workflow_dispatch`），測 GitHub Actions 資料中心 IP 能否過 Fastly 挑戰（研究警告資料中心 IP 易被重罰）；過了再接進每日主 pipeline。
- 移除上個 session 半成品 `scrapers/entradas.py`（Eventim，被 atrapalo 取代）。

## [v0.76.0] - 2026-06-25 22:53
### 新增 — Barcelona 音樂劇來源（teatrebarcelona.com）
- 新 scraper `scrapers/barcelona.py`（與 teatromadrid 同 WordPress 平台），抓巴塞隆納音樂劇 **27 齣**。canonical 西方劇自動 merge（La sireneta→The Little Mermaid、Sonrisas y lágrimas→The Sound of Music、Mamma Mia!…），本地加泰隆尼亞製作保留原名為 tour_name。已加入 `build_shows` SOURCE_FILES。

## [v0.75.0] - 2026-06-25 22:41
### 系統性修復 — 在地製作的名稱與官網（127 個組合，5 路 agent 查證）
- popup 標題現在顯示**在地製作真名**：墨西哥 El Rey León／El Fantasma de la Ópera、日本 ライオンキング／オペラ座の怪人、德國 Der König der Löwen／Die Eiskönigin、法國 Le Roi Lion、中國 剧院魅影／玛蒂尔达、匈牙利／捷克在地名…（`data/local_titles.json`，60 個在地名，build_shows 套用）。
- **官網精準命中在地版**：＋63 個在地官網（elreyleonelmusical.mx、shiki.jp、stage-entertainment.de／fr／nl、tohostage.com、teatromadrid 在地站…）。
- 修「官網 URL 已存在卻被標成 ticketing 票券」（如墨西哥 Lion King 的 elreyleonelmusical.mx 被誤標 Broadway.org）→ 提升為 official 並移到最前。
- 馬德里：`madrid.py` 的 tour_name 一律存西語製作名（Asesinato para dos、Gutenberg, el mejor musical del mundo…），不再被英文 canonical 覆蓋。

## [v0.74.0] - 2026-06-25 19:02
### 修復 — Madrid 漏抓近一半 ＋ 製作層級資料補完
- **Madrid parse 不完整修復**：teatromadrid 列表 85 齣，原本因 11 個劇院 geocode 失敗被跳過、只抓 47。補上 11 個劇院精確座標（Teatro Sanpol／Capitol Gran Vía／OCASO Coliseum／Gran Teatro Pavón／IFEMA／Movistar Arena…），madrid.json 47→**70**，Cenicienta 等救回。（13 齣「場館＋日期未定」維持暫不上圖，待 teatromadrid 公布。）
- **去除「（西語版）」**：這是 `madrid.py` 自己加的中文註記，改成乾淨西文製作名（Los miserables, el musical…）。
- **tour_name 自動補完**：54 個美國巡演分站（Gatsby／Hamilton／Wicked…）從同團複製巡演名，popup 標題一致（修掉 country 正規化順序的 backfill bug）。
- **官網精準命中（全面）**：17 個美國巡演 tour 站 ＋ 10 個在地版官網（agent 查證並驗活），`build_shows` 以「`{區域}_tour`」選址。

## [v0.73.1] - 2026-06-25 18:38
### 補完 — 其他劇的巡演／在地版官網「依此類推」＋「N Cities」字色加深
- **官網精準命中擴及全部**：agent 查證後補進 `official_sites.json` —— 17 個美國巡演的 tour 站（Hamilton→/us-tour、Lion King→/tour、Les Mis→us-tour.lesmis.com…）＋ 10 個在地版（馬德里 El Rey León→elreyleon.es、Chicago 東京→chicagothemusical.jp、Wicked 巴西→wickedbrasil.com…）。
- **「N Cities」字色／字級**：多城市卡的「4 Cities」原本太淺，改成跟下方城市（New York, NY）同樣 14px／#33445c。

## [v0.73.0] - 2026-06-25 18:30
### 修正 — 每個製作用自己的名字 ＋ 精準官網（資料模型）
- **popup 標題用製作真名**：有 `tour_name` 的（巡演／在地版）顯示自己的名字（Wicked — North American Tour、Wicked, el musical），不再統一「Wicked」；原本重複的副標行移除。
- **官網精準命中**：`build_shows` 新增「`{區域}_tour`」選址 — 巡演連自己的 tour 站、在地版連該地官網。Wicked 範例：巡演→tour.wickedthemusical.com、馬德里→wickedelmusical.com、紐約／倫敦各自正確。
- **移除「（西語版）」**：`madrid.json` 裡先前加的中文註記全部拿掉，留乾淨西文名。
- 其他劇的巡演／在地版官網「依此類推」逐步補（研究中）。

## [v0.72.0] - 2026-06-25 18:08
### 新增 — 多城市每站顯示各自海報
- 多城市展開後，每個城市的站點顯示**該製作自己的海報**（如 Wicked 紐約綠色經典版／倫敦版／巡演版／馬德里西語版各不同），取代原本的脊柱。
- 標題列的**大海報固定用最經典版本**：優先選常駐製作（Broadway／West End resident）的海報，不會被某個巡演或在地版本取代。
- 無海報的站點以音符圖示墊底。機制 `js/app.js`（showGroupItem）＋ `css/style.css`（`.stop-thumb`）。

## [v0.71.2] - 2026-06-25 17:50
### 微調 — 單城卡的圓圈改成豎線
- 單一城市卡左側原本是浮著的空心圓圈，看起來較散；改成一條短**豎線**（沿劇院／城市／日期三行），更乾淨、也跟多城市的脊柱同一套視覺語言。

## [v0.71.1] - 2026-06-25 17:21
### 修正 — 購票連結 hover 不再露出醜的聯盟轉址網址
- 購票圖示 ＋ 標題官網連結:hover 時 status bar 改顯示**乾淨的目的地網址**（如 www.todaytix.com），聯盟轉址（redirect.viglink.com…）改在 `onmousedown` 才換上 → 點擊與中鍵開新分頁仍走分潤、但不再外露難看的轉址字串。

## [v0.71.0] - 2026-06-25 17:11
### 新增 — 英文版場館官方英文名（`venues_en`）
- 中／日／韓／台 共 252 個非英文場館，agent 查證官方英文名 **200 個**，英文版顯示英文（臺中國家歌劇院→National Taichung Theater、電通四季劇場→Dentsu Shiki Theatre [UMI]、北京保利劇院→Beijing Poly Theatre、衛武營→National Kaohsiung Center for the Arts、寶塚大劇場→Takarazuka Grand Theatre、上劇場→Theatre Above…）；**無官方英文名的**（小劇場／星空間等）保留原文。受惠 **315 場**。中文版不受影響。
- 機制：`data/venues_en.json` ＋ `build/gen_variants.mjs`（英文版查表、否則 OpenCC）。

## [v0.70.2] - 2026-06-25 17:02
### 精簡 — 篩選標籤縮短 ＋ footer 移到視窗底部（釋出 sidebar 空間）
- 篩選標籤拿掉「音樂劇」字尾（百老匯/西區、德奧、法語、西葡、中國、台灣、日本、韓國），chip 變短、擠的行數變少（英文版本來就短，简中由 OpenCC 自動跟進）。
- 「更新於／來源／隱私／條款」footer 從 sidebar 列表底部移到**視窗底部全寬細長條**，把垂直空間還給音樂劇列表。

## [v0.70.1] - 2026-06-25 16:53
### 微調 — 左側列表字級再放大一級
- 標題 15.5→17、劇院 13.5→14.5、城市 13→14、日期 12.5→13.5、城市數 12→13px。（線上原本就是 demo 同尺寸，使用者希望實際再大一點。）

## [v0.70.0] - 2026-06-25 15:05
### 重新設計 — 左側音樂劇列表（多輪 UI/UX 研究 ＋ 使用者共同打磨）
- **每劇一塊淡底色、綠/金交替** → 一眼看出每齣劇的範圍；主題色（漸層／圓圈／脊柱／狀態）隨該劇底色一致。
- **單城卡**：海報 ＋ 標題 ＋ 圓圈標示的「劇院 ／ 城市 ／ 日期」一組（縮排、無連接線）。
- **多城市**：標題列「N 個城市」，下方漸層區塊用圓圈 ＋ 脊柱串起各站，每站「劇院 ／ 城市 ／ 日期」且**可點擊**（滑過變色、右側箭頭）；≤6 站自動展開、可同時展開多齣。
- **字級放大**（標題 15.5／劇院 13.5／城市 13）、城市文字加深、行高放鬆。
- 「長期上演／Long-running」狀態點加**輕柔呼吸動畫**（尊重 `prefers-reduced-motion`）。
- 英文版城市帶州碼（City, ST）、劇院／城市分行避免孤字；繁中／简中／英文一致。
- 機制：`js/app.js`（showGroupItem 重寫 ＋ 交替 parity）、`css/style.css`（主題色變數＋脊柱＋漸層＋動畫）、`js/i18n.js`（Long-running、city_count）。

## [v0.69.7] - 2026-06-25 11:57
### 微調 — 多城市展開時隱藏重複的「城市 · N locations」摘要行
- v0.69.6 展開後,標題下方仍留「城市清單 · N locations」摘要,跟下方 sublist 重複。展開時(`.show-group.open`)隱藏該摘要行,跟核准的版型一致;收合時(大型巡演)仍顯示摘要。

## [v0.69.6] - 2026-06-25 11:50
### 改進 — 左側列表加劇院 + 多城市 sublist 補日期 + ≤3 城自動展開
- **單一城市**：加回劇院名（獨立一行），版面變成 標題／劇院／城市·日期。
- **多城市展開**：每個地點從「劇院　城市」改成「劇院／城市·日期」兩行（補上各地日期）。
- **≤3 城自動展開**：少數城市的劇一開始就展開（不用點）；大型巡演維持收合避免洗版。
- 機制 `js/app.js`（showGroupItem ＋ 自動展開）＋ `css/style.css`（`.item-venue`、`.sub-item` 改堆疊）。

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
