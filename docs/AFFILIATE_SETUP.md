# 分潤 / 聯盟連結申請清單 AFFILIATE SETUP

> 目標:把地圖連出去的售票連結變成可抽成。技術面已就緒(`js/app.js` 的 `AFFILIATE`
> 設定 + `affiliateUrl()`),**只差申請帳號拿 ID**。拿到 ID 後填進 `AFFILIATE` 即生效。
>
> 重點原則:**連主頁(attraction page)帶追蹤碼就能抽成**,不必細到場次;點擊種
> cookie,使用者站內買哪場都算。資料層存乾淨 URL,包裝在前端 render 時套用。

---

## 0. 先備好(共用前提,沒這些會卡審核)

- [x] **隱私權政策頁**(`privacy.html`)+ **使用條款頁**(`terms.html`)— ✅ 已建立,首頁頁尾與各頁導覽皆可連達。
- [ ] **收款資料**:PayPal 或銀行帳戶。
- [ ] **稅表 W-8BEN**(你在台灣=非美國人,Impact/網路申請時會要你線上填,證明免美國預扣稅)。
- [ ] 網站網址:`https://dannynycc.github.io/MusicalMap/`(申請時填這個)。
- [ ] 簡述受眾:「全球音樂劇即時地圖,導流到各售票平台」。

---

## 1. Ticketmaster → Impact(量最大,先做)

我們連出去 **~915 條** TM 連結。

**申請**
1. 到 **https://app.impact.com**(或 https://impact.com)註冊 **Partner / Publisher** 帳號(免費)。
2. 填網站、受眾、收款、W-8BEN。
3. 進 Impact Marketplace 搜尋 **「Ticketmaster」**(Ticketmaster Global Affiliate Program)→ 申請加入。約幾天審核。

**核准後要拿的 ID**(Impact 後台 → Links / Track a Link 或 Account Settings)
- [ ] 你的 **Impact 追蹤網域**(像 `imp.pxf.io`,或你的 vanity 網域)
- [ ] **Account ID**(數字)
- [ ] **Ad ID** 與 **Campaign ID**(從 Ticketmaster 那個 program 的 link 產生器看到)

**對應連結格式**(已寫在 app.js 範本)
```
https://{追蹤網域}/c/{AccountID}/{AdID}/{CampaignID}?u={URL-encoded 目的網址}
```

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
   - 網站:`https://dannynycc.github.io/MusicalMap/`
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

## 3. LondonTheatre → Awin（西區佣金最高 ~10%）

我們連出去 **82 條** `londontheatre.co.uk` 連結。

⚠ **先釐清(重要,免得白做工)**:研究確認的是 **London Theatre Direct**(`londontheatredirect.com`)走 Impact/Awin ~10%。我們抓的是 `londontheatre.co.uk`(**不同網域**,購票可能導到 ATG 或他家)。
- [ ] 申請前先到地圖點一個 londontheatre.co.uk 的售票連結,看**最後在哪個網站結帳**:
      若導到 **ATG** → 第 2 項已涵蓋,**這項不用做**;若是 London Theatre Direct 或自家 → 才做下面。

**逐步申請(Awin)**
1. 開 **https://www.awin.com** → **Sign up → Publisher/Influencer**。
2. 填名字(英文本名)、國家(台灣)、網站 `dannynycc.github.io/MusicalMap`、推廣類型(content/editorial)、貼 profile。
3. ⚠ **Awin 要付一筆約 US$5 / €1 的「驗證押金」**(會退回你的 Awin 帳戶餘額,不是手續費)。需一張信用卡。
4. 通過 Awin 帳號審核後 → 在 **Advertisers** 搜 **「London Theatre Direct」**(或 LW Theatres / Broadway Direct)→ **Join programme** → 等該商家核准。
5. 收款/稅表:Awin 後台填(USD/美國銀行 + W-8BEN)。

**核准後要拿的東西**(Awin 後台 → Links / Link Builder)
- [ ] 你的 **awinaffid**(publisher ID,登入後在帳號資訊看得到)
- [ ] 該商家的 **awinmid**(merchant ID)— 用 Link Builder 產一條連結就看得到
- [ ] 或直接產一條連結整條貼給我,我拆出 mid/affid。

**連結格式**
```
https://www.awin1.com/cread.php?awinmid={MID}&awinaffid={AFFID}&ued={URL-encoded 目的網址}
```

---

## 4. 之後再考慮(非必要)

- **Stage Entertainment DE**:德國聯盟 ~4-7%,我們連結少,優先度低。
- **Broadway.org（428 條,無聯盟)**:百老匯聯盟官網,不能抽成。未來若想變現,可評估
  把 Broadway 連結改導到能抽成的平台(Broadway Direct via Awin、或 resale 的
  Vivid Seats / StubHub via Impact),但會動到使用體驗,另案討論。
- **無公開聯盟(維持純連出)**:Interpark(韓)、jegy.hu(匈)、OPENTIX/寬宏(台)、
  四季 / 寶塚(日)、teatromadrid(西)。

---

## 5. 拿到 ID 後給我這些,我直接填好上線

把以下貼給我(有哪個給哪個):
- Impact:追蹤網域、Account ID、(Ticketmaster 的)Ad ID + Campaign ID
- Partnerize(ATG):camref
- Awin(LondonTheatre):awinmid + awinaffid

我會填進 `js/app.js` 的 `AFFILIATE`、用幾個真連結測試會不會正確包裝,再 commit 上線。
