# 分潤 / 聯盟連結申請清單 AFFILIATE SETUP

> 目標:把地圖連出去的售票連結變成可抽成。技術面已就緒(`js/app.js` 的 `AFFILIATE`
> 設定 + `affiliateUrl()`),**只差申請帳號拿 ID**。拿到 ID 後填進 `AFFILIATE` 即生效。
>
> 重點原則:**連主頁(attraction page)帶追蹤碼就能抽成**,不必細到場次;點擊種
> cookie,使用者站內買哪場都算。資料層存乾淨 URL,包裝在前端 render 時套用。

---

## 0. 先備好(共用前提,沒這些會卡審核)

- [x] **隱私權政策頁**(`privacy.html`)+ **使用條款頁**(`terms.html`)— ✅ 已建立,首頁**頂部 nav**（v0.78.0 起 footer 移除、Privacy/Terms 改置頂部）與各頁導覽皆可連達。
- [x] **收款資料**:美國銀行帳戶 EFT(免手續費,直收 USD)— ✅ 已設定(Impact)。
- [x] **稅表 W-8BEN**(台灣=非美國人,0% 預扣、無 treaty、電子收件同意)— ✅ 已於 2026-06-23 線上送出。
- [ ] 網站網址:`https://themusicalmap.com/`(申請時填這個)。
- [ ] 簡述受眾:「全球音樂劇即時地圖,導流到各售票平台」。
- [x] **Sovrn 網站送審**:`themusicalmap.com` 已於 2026-07-06 送審(Pending)。⚠️ 機制:人工審核在網站**產生第一批分潤點擊後 3-5 個工作天**才啟動,送審只是排隊——舊 `dannynycc.github.io/MusicalMap/` 條目因全站 301 到新網域永遠不會再有點擊=永久 Pending,無害、後台無自助刪除(要刪只能信件 support@sovrn.com),放著即可。

---

## 1. Ticketmaster → Impact ✅ 已上線(2026-06-23)

地圖連出去的 TM 連結:**約 600 齣劇有 TM 連結**(美國最多,其次英/加/墨;確切數隨每日 CI 變動)。

**狀態:核准 + 帳務 + 程式全部完成。**
- ✅ Impact Partner 帳號核准。
- ✅ 間接稅(not registered)、收款(美國銀行 EFT)、地址(台灣)、**W-8BEN**(非美國人、0% 預扣、無 treaty、電子收件同意)全部送出。
- ✅ 追蹤連結 ID 已填進 **`js/config.js` 的 `MM_CONFIG.AFFILIATE["ticketmaster."]`**(多平台框架,見 `docs/DESIGN_affiliate.md`;不寫死在邏輯):
  `{net:"impact", domain:"ticketmaster.evyy.net", ids:"7408739/264167/4272"}` + `AFFILIATE_SUBID:"musicalmap"`。
- ✅ `js/app.js` 的 `affiliateUrl()` 會把任何 `ticketmaster.*` 售票連結包成 deep-link
  `https://ticketmaster.evyy.net/c/7408739/264167/4272?u={URL-encoded 該劇TM頁}&subId1=musicalmap`
  —— 使用者仍導向**該劇頁面**,只是帶上分潤追蹤;非 TM 連結原樣不動;已是追蹤網域的不重複包。
- ✅ `index.html` 補載 `config.js`(原本只有 me/u 頁載)。

**待後台驗證(誠實標注)**:美站 ticketmaster.com 有把握歸佣;英/加/澳等**各國 TM 網域是否同計畫歸佣**,要等有點擊後在 Impact dashboard 看 `subId1=musicalmap` 的數據確認。

**注意**:佣金低(約 $0.30/單,實際看後台合約);**開賣前 + 開賣首 24 小時的首賣不計佣**;30 天最後點擊歸因。

---

## 2. ATG Tickets → Partnerize

我們連出去 **238 條** ATG 連結(西區 + ATG 自有劇院)。佣金階梯式(賣越多%越高),且「每一筆都算、不只首購」。

**逐步申請**
1. 開 **https://www.atgtickets.com/help/affiliates/**(或 https://www.lovetheatre.com/affiliates/),找「apply / join the affiliate programme」連結 → 會帶到 **Partnerize** 的 ATG 計畫申請頁。
2. 沒有 Partnerize 帳號的話先**註冊 publisher**(也可用 Google / email)。
3. 填基本資料(沿用你已備好的):
   - 名字:**英文本名**(同 Impact)
   - 國家:**台灣**
   - 網站:`https://themusicalmap.com/`
   - 類型:**publisher / content / editorial**(若問)
   - 自我介紹:貼**那段 964 字 profile**(可截短)
4. **送出對 ATG 計畫的申請** → 等 ATG 核准(通常數天)。
5. 收款 & 稅表:Partnerize 後台 **Settings → Payment**,填收款(可用你的**美國銀行/USD**)+ **W-8BEN**(若要求)。
6. 可能要**驗證網站**:做法同 Impact(meta 標籤或檔案)→ 給我代碼我加進 repo。

**核准後要拿的東西**(Partnerize 後台 → Links / Create a Link)
- [ ] 隨便貼一個 ATG 網址產一條追蹤連結 → 連結長這樣 `https://prf.hn/click/camref:XXXX/destination:...`,把**整條貼給我**(我從中取出你的 **camref**)。

**連結格式**
```
https://prf.hn/click/camref:{CAMREF}/destination:{目的網址}
```

---

## 3. londontheatre.co.uk → TodayTix Group(走 Impact,~1-2%)

我們連出去 **82 條** `londontheatre.co.uk` 連結。

✅ **已查證(2026-06-14)**:`londontheatre.co.uk` **不是 ATG、也不是 London Theatre Direct**——它屬於 **TodayTix Group**(Encore 後台)。購票走 TodayTix 自家結帳。
→ 要抽成必須加入 **TodayTix Group 聯盟,走 Impact(impact.com)**,跟 Ticketmaster **同一個帳號/網路**。ATG(Partnerize)、Awin、London Theatre Direct 都**不會**給這些連結佣金。

**逐步**
1. 用**現有的 Impact 帳號**,找 **TodayTix Group** 計畫(Marketplace 搜尋,或找其 direct sign-up 連結;若 Marketplace 仍被擋就走 direct link,同 Ticketmaster 的繞法)。
2. 申請加入 → 等核准。
3. 核准後產一條追蹤連結(Impact `/c/...?u=` 格式),整條貼給我 → 我取出 Account/Ad/Campaign ID 填進 `AFFILIATE` 的 `"londontheatre.co.uk"` 那行。

**連結格式**(Impact,同 Ticketmaster)
```
https://{追蹤網域}/c/{AccountID}/{AdID}/{CampaignID}?u={URL-encoded 目的網址}
```

⚠ **策略提醒**:TodayTix 佣金低(~1-2%)。西區真正高報酬的是 **ATG(第 2 項,我們已有 238 連結)** 和 **London Theatre Direct(~5-10%,但那是另一個網站 `londontheatredirect.com`,我們目前沒連)**。
→ 若想拉高西區收益,未來可考慮把地圖的西區購票連結**改導向 ATG 或 London Theatre Direct**(資料層 westend.py 要改);這是另案。**現階段 82 條 londontheatre.co.uk 優先度低,可放到 Ticketmaster/ATG 之後再說。**

---

## 3b. atrapalo.com（西班牙）→ Sovrn ✅ 已上線(2026-06-26, v0.77.0)

地圖連出去的 atrapalo 連結:build 後約 **106 個西班牙場次**(`scrapers/atrapalo.py`,全西班牙 39 城)。

**狀態:零申請即可變現 —— atrapalo.com 已是 Sovrn/VigLink 目錄裡「Open(自動核准)」merchant(id 53900)。**
- ✅ 用**現有 Sovrn key**,跟 TodayTix/ATG **同一套 `?key=&u=` deep-link 模板**,`u=` 帶該劇頁面 → 保留「點到該劇頁」體驗。
- ✅ `js/config.js` 的 `AFFILIATE` 已加 `"atrapalo.com": { net:"tmpl", tmpl: SOVRN }`,並列入 `AFFILIATE_PRIORITY`。
- 佣金:CPS,實際 rate 由底層網路決定、Sovrn 再抽約 25%;entradas/musicales 類確切 rate 未公開(要登入 Sovrn 後台看 merchant detail)。cookie 天數未公開(TradeTracker 上顯示 7 天)。
- 母集團 atrapalo 屬 lastminute.com group;歐洲原生網路(TradeDoubler/TradeTracker/Awin)目錄雖有 atrapalo 但多標 closed/沉寂,且要 EUR 收款,對台灣個人 CP 值低 → **維持走 Sovrn 即可**。

> **策略決定(2026-06-26):用 atrapalo 取代 teatromadrid + teatrebarcelona。** 後兩者**無分潤**(官網/在地票務,拿不到佣金),放在地圖上反而把點擊從可抽成的 atrapalo 連結吸走。atrapalo 已涵蓋馬德里/巴塞隆納同批劇且能變現 → 計畫把 `madrid.json`／`barcelona.json` 移出 `build_shows` SOURCE_FILES。⚠ **待辦前先驗涵蓋度**:atrapalo 只列「在 atrapalo 開賣」的劇,teatromadrid(~70 齣)可能有 atrapalo 沒賣的劇會掉,撤除前須列出落差讓使用者定奪(誠實標注,不偷渡)。

---

## 4. 之後再考慮(非必要)

- **Stage Entertainment DE**:德國聯盟 ~4-7%,我們連結少,優先度低。
- **Broadway.org（428 條,無聯盟)**:百老匯聯盟官網,不能抽成。未來若想變現,可評估
  把 Broadway 連結改導到能抽成的平台(Broadway Direct via Awin、或 resale 的
  Vivid Seats / StubHub via Impact),但會動到使用體驗,另案討論。
- **無公開聯盟(維持純連出)**:Interpark(韓)、jegy.hu(匈)、OPENTIX/寬宏(台)、
  四季 / 寶塚(日)。〔teatromadrid／teatrebarcelona(西)無分潤 → 見 §3b,計畫以 atrapalo 取代〕

---

## 5. 拿到 ID 後給我這些,我直接填好上線

把以下貼給我(有哪個給哪個):
- Impact:追蹤網域、Account ID、(Ticketmaster 的)Ad ID + Campaign ID
- Partnerize(ATG):camref
- Awin(LondonTheatre):awinmid + awinaffid

我會填進 `js/app.js` 的 `AFFILIATE`、用幾個真連結測試會不會正確包裝,再 commit 上線。
