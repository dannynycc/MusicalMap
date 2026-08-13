# 提交流程 WORKFLOW（每次 commit 必照做）

> 這份是「不會忘記」的單一事實來源。每次要 commit / push 前從頭走一遍。

## 每次 commit 的固定步驟
1. **跑真實時間**：`Get-Date -Format "yyyy-MM-dd HH:mm"`（台北時間）。
2. **更新 `CHANGELOG.md`**：在最上方加一個版本區塊，標題含日期＋時間（台北），用繁體中文，分「新增／修正／變更」。
3. **決定版號**（語意化版號）：
   - PATCH `+0.0.1`：bug / 資料 / scraper 修正、文案、小調整
   - MINOR `+0.1.0`：新功能、新資料來源、UI 大改
   - MAJOR `+1.0.0`：架構大改版 / 不相容變更
4. **所有 `.md` 保持最新**：掃 `README.md`、`docs/*.md`、`CHANGELOG.md`，把過時內容（數量、功能、待辦）改到正確。
5. **commit**：訊息簡述變動。
6. **打 tag**：`git tag vX.Y.Z`，版號與 CHANGELOG 一致。
7. **push**：`git push origin main --tags`。

## 稽核(每次加來源/大改後必跑)
- `python scrapers/audit_images.py` — 海報實測像素,模糊/失效=0 才過(全量版,手動)
- `python scrapers/audit_links.py` — 購票連結全量實測,DEAD=0 才過(TM 401=bot block 非死連)
- `python scrapers/audit_productions.py` — 版本層海報檢查,BROKEN=0 才過(列缺海報的版本/無縮圖的劇)

### CI 每日自動稽核(update.yml;11 支走 `gate`/`warn` + 1 支硬擋)

> ⚠️ **`|| ::warning` 模式已於 v2.56.0 廢止**(那個模式讓 workflow 永遠是綠的,三支中國
> scraper 因此壞了 29 天沒人發現)。現在分三層:
> - **硬擋**(v2.63.0):`audit_counts` 是獨立步驟,總筆數跌幅 >10% 就**停在那裡**,
>   不建站不提交,線上維持前一版。用於「資料整批消失」——`gate` 擋不住這種,
>   因為它只會標紅、殘缺資料照樣部署。
> - **`gate`**:失敗記入 FAILLOG,由排在部署之後的 `health` job 判定整個 run 紅不紅
>   (單一來源掛掉不阻止線上更新,但 GitHub 會寄通知)。
> - **`warn`**:已知積欠/實驗性來源,只提醒。目前＝`audit_tournames`／`audit_titles`／
>   `audit_sample_truth`／`philippines`。

`audit_dups`(去重漏合併+**同劇同城重複售票 URL**+**季票套餐群聚**,works_distinct 拆分組豁免,v2.36–v2.41)/`audit_manual`(手填過期)/`audit_productions`(版本層海報)/`audit_sentinels`(哨兵劇目+來源低水位)/`audit_official`(官網體檢+**死 key 檢查**——official_sites key 對不上任何 group 即報,v2.41.0)/`audit_geo`(國界框+座標指紋)/`audit_tournames`(presenter 滲入)/`audit_titles`(未歸組/分裂,KNOWN_DISTINCT 白名單與 works_distinct 同步)/`audit_sample_truth`(每日 15 卡對 TM API,含 genre 非音樂劇檢查;全 skip 時報 INCONCLUSIVE 不假 PASS)/`audit_posters`(釘圖健康/庫存圖 baseline/縮圖哨兵/抽樣尺寸)/**`audit_dates`**(v2.62.0:格式/閉幕早於開演/已閉幕超過寬限仍在檔/無開演日/開演日在三年後/檔期逾 400 天未標 `end_rolling`——在此之前全庫沒有任何結構性日期檢查)/**`audit_official --check-live`**(v2.61.3 起加連線驗證:官網域名會隨製作結束過期被買走,那次 363 條裡 9 條爛掉)。另 `philippines.py` 在 `warn` 層(v2.58.0 起已改純 HTTP `curl_cffi`,待排程實跑幾班再升級 `gate`)。

## 資料更新
- 改 scraper 或想刷新資料：`python scrapers/westend.py && python scrapers/broadway.py && python scrapers/build_shows.py`。
- GitHub Actions **每天兩次**（台北 06:00 & 18:00,`update.yml`;GitHub 排隊常延後 10–30 分鐘,實際起跑時間會浮動）自動跑**全套 34 支 scraper**（不只上面三支）並提交 `data/*.json` 與預渲染站點檔（`index.html`/`sitemap.xml`/三語變體;commit 訊息帶 `[skip ci]`）。
- ⚠️ **不要為了讓某個修正提早生效而手動 `workflow_dispatch` 觸發完整重建**：那會再吃一次所有外部 API 的當日配額。2026-08-12 就這樣把 Ticketmaster 配額用光（每個國家都回 429），資料掉了 27% 還全綠上線。通常等下一次排程就好。
- 14 支 scraper 已接 `scrapers/_guard.py` 的 `guard_shrink()`：抓到的資料比上一份少 >40% 就**不覆蓋舊檔**並以非零退出碼讓 CI 變紅——寧可不更新,也不要用殘缺資料蓋掉好資料。
- CI 自動提交後，下次本機動工前先 `git pull`。

## 版本對照
- 版號歷史見 `CHANGELOG.md`；git tag 與其一致。

## 自動防呆
- `.githooks/pre-commit` 會在 commit 時檢查：若有變更原始碼/設定但沒有同時更新 `CHANGELOG.md`，會擋下並提醒。
- 啟用（每個 clone 設定一次）：`git config core.hooksPath .githooks`
