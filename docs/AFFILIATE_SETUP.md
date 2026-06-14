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

我們連出去 **238 條** ATG 連結(西區 + ATG 自有劇院)。

**申請**
1. 從 **https://www.atgtickets.com/help/affiliates/**(或 https://www.lovetheatre.com/affiliates/）進入,依指示到 **Partnerize** 註冊/加入 ATG 計畫。
2. 同樣填網站、收款、稅表。

**核准後要拿的 ID**(Partnerize 後台)
- [ ] 你的 **camref**(Partnerize 給的追蹤碼)

**對應連結格式**
```
https://prf.hn/click/camref:{CAMREF}/destination:{目的網址}
```

**注意**:階梯佣金(賣越多%越高),且「每一筆都算、不只首購」。

---

## 3. LondonTheatre → Impact 或 Awin（西區佣金最高 ~10%）

我們連出去 **82 條** `londontheatre.co.uk` 連結。

⚠ **先釐清**:研究確認的是 **London Theatre Direct**(`londontheatredirect.com`)走 Impact/Awin、約 10%。我們抓的是 `londontheatre.co.uk`(不同網域,可能導購到 ATG 或他家)。
- [ ] 申請前先確認 `londontheatre.co.uk` 的購票最終落到誰、有沒有自己的聯盟;
      若它其實導到 ATG,則第 2 項(ATG/Partnerize)就涵蓋了,不必重複。
- [ ] 若要做 London Theatre Direct:到 **https://partners.londontheatredirect.com**(Impact)
      或 Awin 搜該商家加入。

**核准後要拿的 ID**
- Impact:同第 1 項(追蹤網域 + Account/Ad/Campaign ID)
- Awin:**awinmid**(商家 ID）+ **awinaffid**(你的 publisher ID）

**Awin 連結格式**
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
