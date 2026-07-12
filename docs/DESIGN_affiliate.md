# 設計定案:多平台分潤(affiliate)架構

> 狀態:**Phase 1 + Phase 2 已實作(v0.60–0.61)**。TodayTix matcher 上線:103 條連結 / 76 作品,
> build_shows 掛到 101 筆紀錄(官方→TodayTix→其他票務排序)。等 TodayTix Impact 過審填碼即抽成。
> 目標:把地圖連出去的售票連結變成可抽成,跨多個劇場分潤網絡;並把 Broadway/West End
> 這個核心市場導向**抽成較高**的劇場專營平台。**儘可能自動化**(唯一無法自動的只有「申請帳號拿 ID」那一次)。

---

## 1. 兩種接法(核心區分,搞錯才會難改)

| 類型 | 適用平台 | 機制 |
|---|---|---|
| **A. 包現有連結（wrap）** | 已連的:`ticketmaster.`(581)、`atgtickets.`(219)、`londontheatre.co.uk`(45) | render 時把現有 URL 包上分潤碼 |
| **B. 改導新平台（re-point）** | 沒連的:`todaytix.com`、`broadwaydirect.com` | matcher **產生**每齣的深連結 → 當成一個 ticket_link → 再由 A 包 |

## 2. 防返工的最高原則

**資料層只存「乾淨原始 URL」;分潤碼一律在前端 render 時(`affiliateUrl()`)才包。**
- 換 ID / 加網絡 = 改 `js/config.js` 一行,**永不重建資料**。
- matcher 寫入的也是乾淨 URL(未過審前就是正常連結,過審填碼後自動被包成分潤連結)。
- **絕不把包好的追蹤 URL 存進 `data/*.json`。**

## 3. 三層架構

### Layer A — 分潤包裝(`js/app.js` `affiliateUrl`)✅ 已實作
- 設定在 `MM_CONFIG.AFFILIATE`(`js/config.js`),key = 外連 host 子字串,value = `{net, …creds}`。
- 支援四種網絡,各有連結格式:
  - **impact**:`https://{domain}/c/{ids}?u={dest}&subId1={SUBID}`(domain+ids 來自 Impact「Create a link」)
  - **partnerize**:`https://prf.hn/click/camref:{camref}/destination:{dest}`(目前無 active 條目,標 🔜 待升級)
  - **awin**:`https://www.awin1.com/cread.php?awinmid={mid}&awinaffid={affid}&ued={dest}`(目前無 active 條目,標 🔜 待升級)
  - **tmpl**(Sovrn/VigLink Redirect,**現況主力**):`redirect.viglink.com?key={key}&u={url}`——todaytix/londontheatre/atgtickets/broadway-show-tickets/atrapalo 皆走此(見 `js/config.js:41-50`);只有 ticketmaster 走 impact
- 每個程式**獨立 + dormant**:creds 沒填齊 → `affReady()` false → **passthrough**(連結照常,只是不抽成)。
- 防呆:已是追蹤網域(evyy.net/pxf.io/sjv.io/prf.hn/awin1.com)→ 不重複包。

### Layer B — 改導 matcher(`scrapers/todaytix.py`)✅ 已實作
- 抓 TodayTix 各城劇目清單(SSR,無反爬;URL `/{city}/shows/{id}-{slug}`)→ `{id, slug, title, url, city}`。
- 用**正規化標題 + 城市/地區**對應到我們的劇(複用 `build_shows.group_key` + `works.json` 別名)。
- 輸出 `data/todaytix.json` → `build_shows.py` 合併時給對到的劇**加一個 ticket_link**(乾淨 URL)。
- **自動化 + 安全**:用**信心門檻自動取捨**(精確正規化標題相符 + 城市相符 + 必為音樂劇),高信心自動收、低信心自動略過並 `log`(non-blocking),**不靠人工逐筆審**。掛 CI 每日跑。

### Layer C — 連結優先序(`build_shows.py`)✅ 已實作(TodayTix 插在 ticketing 最前)
- 一齣可能同時有 TM + TodayTix(+ATG)。依**佣金高低**排主連結:
  `MM_CONFIG.AFFILIATE_PRIORITY = [todaytix, londontheatre, atg, atrapalo, broadwaydirect, ticketmaster]`(現值見 `js/config.js:57-59`)。
- 用 **URL 的 host** 判定(跟 Layer A 同一套比對)—— **不新增任何資料欄位**,不會返工。
- 前端「購票」鈕顯示優先序第一個,其餘列次要。

## 4. 自動化程度(回應「儘可能自動化」)

| 環節 | 自動? |
|---|---|
| 分潤包裝(render) | ✅ 全自動 |
| TodayTix 劇目對應(matcher) | ✅ CI 每日自動 + 信心門檻自動取捨(無人工審) |
| 連結優先序 | ✅ 自動(host 規則) |
| 換 / 加 ID | 改 config 一行(半自動) |
| **申請帳號拿 ID** | ❌ **唯一無法自動**(需真人帳號 + 平台審核) |

## 5. 各平台狀態(2026-06-23 逐一查證)

| host | 網絡 | 現連數 | 查證結果 / 狀態 |
|---|---|---|---|
| `ticketmaster.` | Impact | 581 | ✅ **live**(固定 ~$0.30/張) |
| `atgtickets.` | **Partnerize** | 219 | ✅ **可申請(已驗證 active)**:`signup.partnerize.com/signup/en/ambassadortheatregroup`(5 天 cookie、"generous"%未明列)。填 camref 即生效 |
| `broadwaydirect.com` | **Awin** merchant **28987** | 0(待改導) | ✅ **存在(已驗證)**:註冊 Awin → 申請 28987(Nederlander 9 院)。填 affid + 改導 |
| `todaytix.com` | **Sovrn Commerce / VigLink** | 101(matcher) | ✅ **LIVE 變現(2026-06-23)**:Sovrn Commerce 已接(merchant 122507「Open」)。直接計畫關閉(FlexOffers 停收、hello.todaytix.com 死),改走 VigLink Redirect API:`redirect.viglink.com?key={key}&u={url}`(key 在 Site Settings 🔑,公開值)。已實測 302 導正確劇目頁 + 填入 config。Sovrn 抽一手、~1-2% |
| `londontheatre.co.uk` | TodayTix Group | 45 | ❌ 無自有計畫;TodayTix 直接關 → 需經 Sovrn(或其自有網絡,待查) |
| London Box Office | 自有(in-house) | 0(未連) | ✅ active:email 申請拿 Unique ID(48h);需改導才有流量 |
| broadway-show-tickets.com | **Sovrn catch-all** | 27 | ✅ 無直接計畫(affiliate 頁 404),但已經 Sovrn in-network 變現(`js/config.js:48`) |
| `atrapalo.com`(西班牙) | **Sovrn** merchant 53900 | — | ✅ 後補(v2 系列):Sovrn in-network,已入 config 與 AFFILIATE_PRIORITY |

> 收尾教訓(誠實):TodayTix 一開始被我當「最高槓桿/Impact 1-2%」,查證後 **Impact 是錯的、直接計畫已關**,只剩 Sovrn(抽成、率較低)。所以**近期確定能賺的是 ATG(Partnerize, 219)+ Broadway Direct(Awin)**;TodayTix 走 Sovrn 是「有總比沒有」。**驗證每一個、別憑搜尋/AI 背書**。

## 6. 動工順序(每步都不被後面推翻)

1. **Phase 1 ✅**:`affiliateUrl` 多網絡 + config(只改 `app.js`+`config.js`,不碰 build_shows,零 matching 風險)。TM 照常;ATG/londontheatre/BwayDirect dormant,填碼即生效。
2. **Phase 2**:`todaytix.py` matcher(CI 自動 + 信心門檻)→ `build_shows` 合併 + 優先序。把純百老匯從 TM 改導 TodayTix。
3. 使用者從**品牌官方 affiliate 頁**申請(冷敲 marketplace 會被拒——TM 經驗),拿到碼填 config。

## 7. 申請須知(操作)

- 直接計畫**一律從品牌自己的 affiliate 頁發起**,不要在市集冷申請(TM 在 marketplace 被拒,從 TM 端發起才過)。以下為 **2026-06-23 實測可開**的入口:
  - **ATG / LOVEtheatre**(Partnerize):`https://signup.partnerize.com/signup/en/ambassadortheatregroup`(✅ 驗證可開)
  - **Broadway Direct**(Awin):註冊 Awin → 申請 merchant **28987**(✅ Awin profile 驗證存在)
  - **TodayTix**(Sovrn):直接計畫已關;改 **Join Sovrn Commerce**(`commerce.sovrn.com`,免費),TodayTix merchant 122507 標「Open」→ 登入後建連結
  - ❌ `hello.todaytix.com`(舊官方 affiliate 頁)**已死(NXDOMAIN)**;FlexOffers 的 TodayTix 頁標「not currently offering」——皆勿用
- 拿到的「追蹤連結/樣本連結」整條貼回來,我取出 camref(Partnerize)、affid(Awin)、或 Sovrn 連結模板(`tmpl`)填進 `js/config.js`。
