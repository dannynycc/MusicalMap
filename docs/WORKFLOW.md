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
- `python scrapers/audit_images.py` — 海報實測像素,模糊/失效=0 才過
- `python scrapers/audit_links.py` — 購票連結全量實測,DEAD=0 才過(TM 401=bot block 非死連)
- `python scrapers/audit_productions.py` — 版本層海報檢查,BROKEN=0 才過(列缺海報的版本/無縮圖的劇)

## 資料更新
- 改 scraper 或想刷新資料：`python scrapers/westend.py && python scrapers/broadway.py && python scrapers/build_shows.py`。
- GitHub Actions **每天兩次**（台北 06:00 & 18:00,`update.yml`）自動跑**全套 ~30 支 scraper**（不只上面三支）並提交 `data/*.json` 與預渲染站點檔（`index.html`/`sitemap.xml`/三語變體;commit 訊息帶 `[skip ci]`）。
- CI 自動提交後，下次本機動工前先 `git pull`。

## 版本對照
- 版號歷史見 `CHANGELOG.md`；git tag 與其一致。

## 自動防呆
- `.githooks/pre-commit` 會在 commit 時檢查：若有變更原始碼/設定但沒有同時更新 `CHANGELOG.md`，會擋下並提醒。
- 啟用（每個 clone 設定一次）：`git config core.hooksPath .githooks`
