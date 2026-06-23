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
- 支援三種網絡,各有連結格式:
  - **impact**:`https://{domain}/c/{ids}?u={dest}&subId1={SUBID}`(domain+ids 來自 Impact「Create a link」)
  - **partnerize**:`https://prf.hn/click/camref:{camref}/destination:{dest}`
  - **awin**:`https://www.awin1.com/cread.php?awinmid={mid}&awinaffid={affid}&ued={dest}`
- 每個程式**獨立 + dormant**:creds 沒填齊 → `affReady()` false → **passthrough**(連結照常,只是不抽成)。
- 防呆:已是追蹤網域(evyy.net/pxf.io/sjv.io/prf.hn/awin1.com)→ 不重複包。

### Layer B — 改導 matcher(`scrapers/todaytix.py`)✅ 已實作
- 抓 TodayTix 各城劇目清單(SSR,無反爬;URL `/{city}/shows/{id}-{slug}`)→ `{id, slug, title, url, city}`。
- 用**正規化標題 + 城市/地區**對應到我們的劇(複用 `build_shows.group_key` + `works.json` 別名)。
- 輸出 `data/todaytix.json` → `build_shows.py` 合併時給對到的劇**加一個 ticket_link**(乾淨 URL)。
- **自動化 + 安全**:用**信心門檻自動取捨**(精確正規化標題相符 + 城市相符 + 必為音樂劇),高信心自動收、低信心自動略過並 `log`(non-blocking),**不靠人工逐筆審**。掛 CI 每日跑。

### Layer C — 連結優先序(`build_shows.py`)✅ 已實作(TodayTix 插在 ticketing 最前)
- 一齣可能同時有 TM + TodayTix(+ATG)。依**佣金高低**排主連結:
  `MM_CONFIG.AFFILIATE_PRIORITY = [todaytix, londontheatre, atg, broadwaydirect, ticketmaster]`。
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

## 5. 各平台狀態

| host | 網絡 | 佣金 | 現連數 | 狀態 |
|---|---|---|---|---|
| `ticketmaster.` | Impact | ~$0.30/張(固定) | 581 | ✅ live |
| `atgtickets.` | Partnerize | — | 219 | 🔜 填 camref(Phase 1 已可包,等碼) |
| `londontheatre.co.uk` | Impact(TodayTix Group) | ~1–2% | 45 | 🔜 填 domain+ids |
| `todaytix.com` | Impact | ~1–2% | 0(待 matcher) | 🔜 Phase 2 + 填碼 |
| `broadwaydirect.com` | Awin(mid 28987) | 議定 | 0(待改導) | 🔜 填 affid + 改導 |

> 佣金算術:一張 $120 百老匯票,TodayTix 1–2% = $1.2–2.4,是 TM 固定 $0.30 的 **4–8 倍** → 故把 Broadway/West End 改導 TodayTix 是最大收入槓桿。

## 6. 動工順序(每步都不被後面推翻)

1. **Phase 1 ✅**:`affiliateUrl` 多網絡 + config(只改 `app.js`+`config.js`,不碰 build_shows,零 matching 風險)。TM 照常;ATG/londontheatre/BwayDirect dormant,填碼即生效。
2. **Phase 2**:`todaytix.py` matcher(CI 自動 + 信心門檻)→ `build_shows` 合併 + 優先序。把純百老匯從 TM 改導 TodayTix。
3. 使用者從**品牌官方 affiliate 頁**申請(冷敲 marketplace 會被拒——TM 經驗),拿到碼填 config。

## 7. 申請須知(操作)

- **一律從品牌自己的 affiliate 頁發起**,不要在 Impact/Partnerize/Awin 市集冷申請(TM 在 marketplace 被拒,從 TM 端發起才過)。
  - TodayTix:`hello.todaytix.com/affiliates-faq`(接 Impact)
  - ATG / LOVEtheatre:官網「Affiliate Programme」頁(接 Partnerize)
  - Broadway Direct:官網 affiliate 頁(接 Awin,merchant 28987)
- 拿到的「追蹤連結」整條貼回來,我從中取出 domain/ids(Impact)、camref(Partnerize)、affid(Awin)填進 config。
