# 三語簡介 生成 + 嚴格查證 SOP（Runbook）

> 給下一個 session 的單一入口。讀完這份就知道「補一部劇情」要做什麼、標準在哪。
> 最高原則見 memory `feedback_core_rule`：**誠實優先於好看**。查不到就標查不到，不編。

## 0. 名詞：兩種驗證等級（帳本 `method` 欄）
- **method B（唯一合格標準）**＝ Perplexity 生成為「主體」（自然語言、像真人寫），
  **由 Claude 本人親自**用 claude-in-chrome 逐語言語意查核 + 多源交叉（**不派 agent 代查**）。
  **只修真錯，不改文風；主客不倒**（Perplexity 是主、我是校對，不是我重寫——我的文字 AI 感太重）。
  禁止「球員兼裁判」＝拿三語版本互比當查證（那只是內部一致性，不是外部真相）。詳見 §3。
- method A＝生成了但沒經 B 的外部查核。legacy＝早期入庫未標。none＝未查核。
- 帳本欄位：`external_multisource`(bool)、`verify_scope`（`multisource`=≥2 獨立網域 /
  `single`=單一外部源 / `internal`=無外部源、僅三語內部一致性，**冷門在地劇誠實標這個，不謊報多源**）。

## 1. 消歧義（生成前，**必做**）
同名作品先確認是哪一部，尤其「冷門外語音樂劇 vs 知名歌劇/話劇/電影」。
- 查 `data/works.json`(canonical/aliases) + `data/shows.json`(venue/tag) 定位。
- 在生成 prompt 的劇名後**釘住劇情核心**消歧義（Don Juan 教訓：中文查詢會漂到莫札特版；
  石像/多娜伊內絲=錯版訊號）。tag 與 venue 打架（如 tag=台灣原創但場館在大陸巡演）要先查清製作方。

## 2. 生成（Comet CDP 9223 → Perplexity，答案在 `.prose`）
```
# 先確認 CDP 活著： curl http://127.0.0.1:9223/json/version
python scripts/px_gen.py en       out_en.json  @list.json
python scripts/px_gen.py zh-hant  out_zht.json @list.json
python scripts/px_gen.py zh-hans  out_zhs.json @list.json
```
- list.json = 英文劇名陣列（當 prompt 前綴，內含消歧義描述）。
- zh-hant 會自動套 `scripts/polish.py` 台灣定譯表 `data/synopses_tw_terms.json`。
- 輸出 `[{show,synopsis,size,summary}]`；空生成/限流會重試（見 `feedback_perplexity_session_fail_is_ratelimit`）。

## 3. 嚴格查證 method B（生成後，**逐部逐語言**）

> 🚨 **這一步是這套方法的靈魂，不可省、不可外包。**
> - **必須由 Claude 本人親自做，不准派 subagent/Task/Explore 代查。** 使用者要的是「我」用
>   `claude-in-chrome` 一齣一齣、一個 source 一個 source 地看過去（先前 239 部帳本就是這樣，
>   每齣查 5、6 個 source）。派 agent 代查＝偷懶，一定被抓包。可同時開 2~3 個 Chrome tab 平行
>   查不同劇加速，但**讀與判斷都是我自己在做**。
> - **角色定位（主客不可顛倒）：Perplexity 的產出是「主體」，我只是「事實校對」。**
>   為什麼？Perplexity 講出來的話比較像真人、符合自然語言；**Claude 自己重寫的文字 AI 感太重**。
>   所以我的工作是「查事實對不對」，不是「換成我的寫法」。事實錯了才動，語感一律保留。

對每一部、每一種語言：
1. **我親自完整通讀** Perplexity 的產出（不是正則掃描、不是叫 agent 讀；見 `feedback_full_read_beats_automated_qa`），
   分析它的語意：角色、關係、情節、結局各是什麼主張。
2. **我用真 Chrome（claude-in-chrome）多源查證「這齣音樂劇本身」**（不是原著小說/電影）：
   目標 ≥2 個獨立網域，理想 5~6 個 source（對齊 239 部帳本的標準）。可用源：Wikipedia、官方站、
   劇評（Broadwayworld/Playbill/TheaterMania/在地劇評），韓劇加韓語源。WebFetch 常 403 的替代網域：
   broadwaymusicalhome.com / mtishows.com / broadway.com / gsarchive / 官方售票頁內嵌資料。
   **不是拿三語版本互相比對**（那只是內部一致性，是球員兼裁判）——要對「外部真相」。
3. **建 checklist**：把角色名、關係、關鍵情節點列出來，逐條拿外部真相對三語各版；
   **checklist 要輸出到 PowerShell 看得到**（使用者要看得到我到底查了什麼、查了幾個源）。
4. **判斷：語意對就維持原文不動；抓到事實錯→最小修正**。
   - 只改「事實錯的那一處」，**不動語感、不整段重寫**（除非整段是幻覺才重寫）。
   - **修完仍要是 Perplexity 的語感**，不是換成我的句子。改完讀一遍，若讀起來變「Claude 味」就退回、只改必要的字。
   - 簡中準確度 << 繁中，三語各自獨立查（錯誤不重疊；見 `feedback_zhhans_perplexity_less_accurate`）。
5. 沉浸式/重製作品查「該製作本身」，不套原作標準版（`feedback_immersive_production_not_source_plot`）。
6. 例外的文風調整：開頭書評框架 → 直接入戲（見 §7）屬既定策展政策，可修；這不算「改語感」，
   是把 Perplexity 偶爾冒出的影評腔拿掉，其餘句子照舊保留。

## 4. 記帳本（每部必更新，否則追溯斷掉）
- 交叉查核工作記錄：`data/gen_crosscheck_log.json`（method/sources/checklist/各語 correct|fixed/error）。
- 出處總帳：`data/synopses_verification.json`
  `verified[group]={method,date,langs,sources,errors_fixed,confidence,external_multisource,verify_scope}`。

## 5. 入庫管線（見 memory `project_musicalmap_kb_banking`）
```
python scripts/kb_merge.py <en|zh-hant|zh-hans> <results.json> <keymap.json>
python scripts/build_served_synopses.py     # library ∩ catalog → served；catalog<100 拒覆蓋
node build/gen_site.mjs                      # 重建三語 HTML，DATA_VER(md5) 破快取
```
- keymap 格式 `[[group,title],...]`，把在庫劇對到 DB group（解別名坑）；空 synopsis 自動跳過。
- sub-key：en→en、zh-hant→zh、zh-hans→zh-hans。檔案 indent=2 + CRLF。
- 🚨 **直接改過 served 要先同步回 library 再 build_served**，否則舊 library 覆蓋掉改進。
- 🚨 **每次 merge 後重掃殘留**：來源 slug（單一小寫 latin token）、「全劇總結」標題會被重新帶進來。

## 6. 上線 + 正式站驗證（不拿 localhost 交卷；`feedback_verify_on_production_not_localhost`）
- commit（只 stage 自己的檔）+ CHANGELOG（台北時間 HH:MM，先跑 Get-Date）+ tag + push。
- CF Pages 自動部署。驗：正式站 `themusicalmap.com` 的 `DATA_VER` == repo；
  `data/synopses/en.json` 的 `syn` 新 group 到位；抽該 group 卡片數 >0。
- ⚠️ push 事件 CI **不重建網站**，本機要補跑 gen_catalog/gen_variants/gen_site（`project_musicalmap_workflow`）。
- ⚠️ 凌晨別跟每日 CI 搶 push：先 `gh run list` 看有無進行中的 schedule run，避免 non-fast-forward 卡住當天資料刷新。

## 7. 開頭文風（策展政策，`project_musicalmap_kb_banking`）
「直接入戲」：第一句進場景，禁「《劇名》描寫/講述…」「以…為背景」書評口吻。
改寫第一句必連第二句一起看，避免語意重複。
