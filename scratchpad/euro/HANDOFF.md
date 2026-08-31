# 歐陸原創 簡介收尾任務 — HANDOFF(最後更新 2026-08-31 下午,台北)
前 session id: bc41c276-8fdd-4b5e-9cd0-718cecae81fe。此檔 + 同資料夾 `*_triage.md`(判定證據)+ `verify_truth_*.md`(§3 用的外部 ground truth)為完整交接。

## 任務 flow(使用者鐵則,務必照做)
逐部 triage:①真歐陸原創音樂劇→寫三語簡介 ②外國名作在地版→重分類/合併(加 works.json alias 併回 canonical) ③非 book musical(gala/演唱會/選秀/致敬秀/卡巴萊/話劇/獨角秀)→加 not_musical 排除 ④冷門查不到 ≥3 可靠源→標「無法查證·不寫」絕不硬編。
- 生成:Perplexity 身份釘死(**不餵劇情**)出三語 → 我本人 §3 多來源交叉查證、修真錯保留 Perplexity 語感、標題查在地既有譯名不硬翻。
- 每步留證於 scratchpad/euro/*.md,不造假。使用者隨時抽查。
- build/部署後正式站眼見為憑(輪詢 DATA_VER + 抽驗簡介),不拿 localhost 交卷。
- 完整 runbook = repo `docs/SYNOPSIS_SOP.md`。

## ✅ triage 72/72 完成(本 session 補完最後 4 部,證據見 nordic_etc_triage.md / china_triage.md)
- 丹麥 Et Juleeventyr → ❌EXCLUDE(Det Ny Teater「En magisk monolog」獨角戲,一人飾 20 角,音樂僅音景設計)
- 丹麥 Ternet Ninja → ✅KEEP 真丹麥原創音樂劇(Ternet Ninja Live,2027 Tivoli 首演)
- 土耳其 Paris! The Show → ❌EXCLUDE(Gil Marsalla 法式香頌卡巴萊致敬秀,同既排除的 Piaf! The Show)
- 中國 玩偶 → 🔁重分類=中國原創(推翻 v2.94.1「芬蘭 PLAY ME 中文版」誤判;saoju 標原创+全華人主創,芬蘭 Play Me 實為 Svenska Teatern 教瑞典語的互動音樂劇,毫無交集)

## ✅ 已落盤的資料改動(已跑 build_shows 驗證生效;尚未 gen_site/部署)
`data/works.json`:
- Dirty Rotten Scoundrels += alias「A Riviéra vadorzói」
- 新 canonical「Zrínyi 1566」(歐陸原創)+ alias「Moravetz - Balásy - Horváth K. - Papp;」
- 新 canonical「Metro」(歐陸原創)+ alias「Musical Metro! To już 35 lat!」
- The Count of Monte Cristo:歐陸原創 → 法式音樂劇
- **(本 session)** 移除誤註冊的 canonical「玩偶」/alias「PLAY ME」→ fallback 回中國原創 ✅ 已驗
- **(本 session)** Roméo et Juliette += alias「RÓMEÓ ÉS JÚLIA - musical」(→法式)
- **(本 session)** Beauty and the Beast += alias「A Szépség és a Szörnyeteg」(→Broadway 迪士尼)
- **(本 session)** 新 canonical「A dzsungel könyve」(歐陸原創)+ aliases 長標題(Roxszínház)與「A DZSUNGEL KÖNYVE」→ #16/#17 合併
- **(本 session)** 新 canonical「Carmen」(歐陸原創;Wildhorn 作品,**世界首演 2008 布拉格 Karlín** → 首演地在歐陸,tag 正確)
`data/not_musical.json` 新增 12 筆(append-only):Oceania - Il Musical / Milovat k smrti / Má mě rád, nemá mě rád / OTEC V ŠESTINEDĚLÍ / Bitwa o tron. Musicalowy talent show / PARIS VARSOVIE LE CABARET MUSICAL Ewunia / Night of Famous Musicals / Efkan Şeşen / Prosjekt Prøysen / **Et Juleeventyr** / **Paris! The Show** / **MusicalPlusz 115.**
→ build_shows 後:1939 shows,歐陸原創 **53 group**(其中 pinocchio musical、oliver twist 已有簡介),**缺 51 部**。

## 🔄 進行中:51 部三語簡介
- 清單與 keymap:`scratchpad/euro/gen/list.json`(prompt 前綴,身份釘死不含劇情)、`gen/keymap.json`(`[[group, 前綴],…]`,給 kb_merge)。產生器 `gen/make_list.py`。
- 生成中(背景,Comet CDP 9223):
  - `python scripts/px_gen.py en scratchpad/euro/gen/out_en.json @scratchpad/euro/gen/list.json` → log_en.txt
  - `python scripts/px_gen.py zh-hant scratchpad/euro/gen/out_zht.json @…/list.json` → log_zht.txt
  - **zh-hans 尚未跑**(限流考量,同時最多 2 串流;en/zht 完成後再跑)
- ⚙️ 本 session 改了 `scripts/px_gen.py` 的字數提示(en 280→**250**、zh-hant 420→**390**+硬上限句):實測 Perplexity 一律超寫,舊提示會讓每部重試滿 7 次(慢 7 倍)。改後多半一次過。
- §3 查證用的外部 ground truth **已備妥**(我本人多源實讀,每部 3-7 個獨立網域):
  - `verify_truth_italy.md`(15 部)、`verify_truth_czech.md`(10 部)、`verify_truth_hungary.md`(13 部)、`verify_truth_poland_nordic_be.md`(波4 / 北歐8 / 比1)
- ⚠️ 仍待補的細節(生成結果若碰到這些主張要特別擋):
  - **A TRÓN**:分幕情節公開來源仍薄,具體情節點對不上外部源就不寫。
  - **Alice nel Paese delle Meraviglie**:2026-27 巡演 = ItaliaShow + Nati da un Sogno(Roberta Bonino 編導),此版劇情獨特(13 歲 Alice 想讓時鐘停下);**須先確認我方 15 場巡演即此製作**。
  - **Kapka medu pro Verunku**:官方摘要未點明 Verunka 本人在劇中的位置。
  - **Änglagård**:舞台版創作團隊未查到 → 不寫作曲者。
  - **Elvált nők klubja**:官方 stáblista 無作曲掛名 → 不提音樂來源(判定仍為匈牙利自製,非引進百老匯)。
  - **Mohács 500**:首演日兩來源不一致(8/8 vs 8/29)→ 不寫首演日。

## 🔧 本 session 對共用工具的改動(都已落 repo,不是暫時 hack)
1. `scripts/px_gen.py` 三處 prompt/清理修正,都是**系統性壓低品質**的問題:
   - en 字數提示 280→**250**、zh-hant 420→**390**+硬上限句:Perplexity 一律超寫約 25%,舊提示害每部重試滿 7 次(慢 7 倍)。
   - en 的「用**英語製作**慣用的角色/地名」→ 改成「保留該製作原文的名字,不要發明英文對應」:捷克/匈牙利/波蘭/北歐沒有英語製作,舊句誘導它自己編英文名(Saturnin 的 Milouš 被寫成《Jeeves》的 Bertie、doktor Vlach 寫成 Witherspoon)。**捷克 10 部的 EN 已用新 prompt 重生成**,新版角色名全部正確。
   - 中文 prompt 不再出現「全劇總結」四個字(它會被當標題印進正文);slug 清理規則從 3 字元放寬到 **2 字元**(舊規則漏掉 `hdk` 這種三字母劇院縮寫)。
2. 新增 `scripts/scan_synopsis_artifacts.py`(掃描 / `--fix`):抓「總結小標」與「來源 slug」殘留,library 與 served 兩邊都掃。**已用它修掉既有庫的 70 筆殘留**(繁 17 + 簡 18 個 group × library/served),正式站上原本看得到「全劇總結」四個字。SOP §5 的「每次 merge 後必重掃殘留」從此有工具可跑。
3. 已跑過 `scrapers/gen_catalog.py` + `build/gen_variants.mjs`;驗證 **51 個 group 全部在 catalog 內**(build_served 不會過濾掉任何一部)。

## ✅ 資料改動的回歸驗證(對 HEAD 逐 group 比對,確認沒有意外副作用)
- tag 場次分布:歐陸原創 201→177、Broadway/West End 1270→1272(+2)、法式音樂劇 34→36(+2),其餘各 tradition **完全不變**。
- **實際 tag 變動的 group 只有 2 個**,都是本次刻意改的:`玩偶`(歐陸原創→中國原創)、`count of monte cristo`(歐陸原創→法式音樂劇)。
- 消失的 18 個 group 全部有對應處置:重分類併入既有 canonical(`romeo es julia`、`a szepseg es a szornyeteg`、`a riviera vadorzoi`)、合併(`des laszlo…dzsungel…roxszinhaz`→ A dzsungel könyve、`moravetz balasy horvath k papp`→ Zrínyi 1566)、not_musical 排除(`musicalplusz 115`、`milovat k smrti`、`ma me rad nema me rad`、`otec v sestinedeli`、`oceania` 等)。
- 新增 group 1 個:`zrinyi 1566` ✓。

## 📋 §3 查證進度(我本人親做,紀錄在 `verify_fixes.md`)
- EN:1-25 查完(義 15 + 捷 10)。實質要修的:①A Christmas Carol 的「wife Rose」是幻覺 ②Belle e la Bestia 編了 Belle 的身世與「Belle 就是失落公主」的懸念 ③Il ragazzo 用電影情節而非舞台版 ④Raffaella 兩個查無據的人名 ⑤Caravaggio 把敘事者 Don Fernando 寫成壓迫者 ⑥Saturnin 把敘事者取名為作者的姓 Jirotka ⑦VY NEJSTE 的「Liga tolerance」查無據 ⑧**Zlatovláska 四處編造**(蛇寫成魚、兩個國王名、四個姊妹名、二婚結局)⑨Rebelové 的地名 Kostelec。
- ZH-HANT:1-13 查完。最嚴重是 **Aggiungi un posto a tavola 人物關係整組錯**(Clementina 被寫成 Consolazione 的女兒;實為市長之女且愛的是神父,Totò 愛的是 Consolazione),另有多篇「全劇總結」標題殘留、Gloria/Scugnizzi 開頭是書評框架、Peter Pan 的 Tiger Lily 譯成「莉莉公主」(台灣通行為虎蓮公主)。
- ZH-HANS:尚未生成。
- ⚠️ **改 `out_*.json` 一定要等該語言的 px_gen 完全結束**——它每完成一部就把記憶體裡的整個 results 陣列 dump 回檔案,中途改會被蓋掉。

## 後續管線(見 memory `project_musicalmap_kb_banking` / SOP §5-6)
`kb_merge.py <lang> out_*.json gen/keymap.json` → `build_served_synopses.py` → `node build/gen_catalog…/gen_variants.mjs` → `node build/gen_site.mjs`(bump DATA_VER)→ commit+CHANGELOG(HH:MM,先跑 Get-Date)+tag+push → 正式站輪詢 DATA_VER + 抽驗簡介。
🚨 改 served 後必先同步回 library 再 build_served;每次 merge 後重掃來源 slug/「全劇總結」標題殘留。

---

# 2026-08-31 深夜:三語 51/51 逐部深查(§3 method B)完成

## 使用者立的規矩(必須照做)
1. 「原本 tag 是歐陸的**每一齣**都要你**親自用 claude-in-chrome** 多 source(wiki、官方、劇評…**不要只有兩個**)深查、交叉比對」
2. 「教你針對**音樂劇**去做,不要被原著、或小說、或電影干擾」
3. 「我要看到你的過程、你要記錄下來、**必須留證據**」
4. 「**劇情故事的正確性、語意跟事實都很重要,缺一不可**,不要只偏哪一個做(繁中、簡中、英文都是)」

## 產出的證據
- `verify_chrome_evidence.md`(783 行)+ `verify_chrome_evidence_hu.md` — **英文 51/51**,每部記:打開的 URL、官方原文照抄、劇情/事實/語意三欄逐句表
- `verify_zh_findings.md` — **繁中 51 + 簡中 51**,同樣三維度,並標明每一處是 A(局部修)還是 B(需重生成)
- `gen/apply_fixes.py` — 全部修正的唯一入口,73+ 條精確替換,**每條都附查證理由與官方原文**;匹配不到就報錯

## 修正統計
| | 精確替換 | 專名全篇替換 | 重新生成 |
|---|---|---|---|
| 英文 | 19(含**撤回自己 1 處誤修**) | — | 0 |
| 繁中 | 27 | 6 | 2 部(已完成並複驗) |
| 簡中 | 28 | 6 | 8 部(進行中) |

## ⚠ 下一個 session 一定要知道的三件事

**1. `apply_fixes.py` 裡曾有 7 條「把對的改成錯的」規則,已刪除並留註記——不要復原。**
根因:拿原著小說/電影當標準去訂正**舞台製作**,而且用代讀工具看不到官方角色表(要展開折疊區/讀 innerHTML)。
第 8 條是 `A meseautó` 的 `Központi bank`(我當成查無據刪掉,其實官方角色表第一行就寫著),也已撤回。

**2. 判準只有一個:這個製作自己的官方怎麼寫。** 原著、電影、其他語言版本只能當**對照**,不能當標準。
本輪雙向都出過錯:
- 生成寫對舞台版而我差點改錯:`MADE IN HUNGÁRIA`(舞台版 **Ricky**,電影才是 Miki)、`Så som i himmelen`(舞台版死於**心臟**,電影是撞頭)、`Änglagård`(舞台版**開場拆信**,電影留懸念)、`The Julekalender`(舞台版拼 **Frits**)
- 生成被他作汙染:`A dzsungel könyve` 簡中的**迪士尼路易王**、`Pippi på sirkus` 繁中的原著警察 **Kling och Klang**、`Zlatovláska` 簡中的**灰姑娘**分揀種子、`Snowboarďáci` 繁中的電影三女孩名

**3. 回歸哨兵**:`out_*.json` 裡有 13 個「我曾改錯後復原」的字串必須still在
(en: `his wife Rose` / `named Jirotka` / `Cicus` / `Poliakoff` / `princess` / `Černovláska` / `Központi bank`;
zht: `瑞奇` / `草叢` / `'o russo`;zhs: `瑞奇` / `扬` / `伊罗特卡`)。改動後請重跑這組檢查。

## 尚未做的後續管線
1. 簡中 8 部重生成完成 → `gen/apply_regen.py` 回填 → **逐部複驗**(重生成不代表就對:繁中新版 Julekalender 仍有 1 處查無據細節被我抓到並修掉)
2. `python scripts/kb_merge.py en|zh-hant|zh-hans <out_*.json>` ×3
3. `python scripts/build_served_synopses.py`
4. `node scripts/gen_site.mjs`(bump DATA_VER)
5. commit + CHANGELOG(台北時間 HH:MM,**先跑 Get-Date**)+ tag + push
6. 到正式站 themusicalmap.com 驗 DATA_VER 與抽驗幾部簡介

## 2026-09-01 00:18 已完成部署

- commit `1fb992ed`(深查與修正)+ `71af9f2f`(rebase 後重產),tag **v2.98.29**,已 push,ahead/behind = 0
- DATA_VER `643f16a807`
- 前端 served:**en 48 / zh-hant 48 / zh-hans 46**
  - 51 部中 3 部(`Légy jó mindhalálig`、`A meseautó`、`Zrínyi 1566`)場次已結束而離開 catalog,
    簡介仍在 `synopses_library`,日後有新場次自動掛回(build_served 既有設計)
  - 簡中另有 2 部暫緩(`Aggiungi un posto a tavola`、`A Padlás`),見 `gen/out_zhs_HELD.json`

### 遺留待辦
1. **簡中 2 部**待日後重試生成:`Aggiungi un posto a tavola`、`A Padlás`
   —— 兩次生成都不通過,Perplexity 對這兩部可用資料不足。重試前建議先在 Chrome 讀官方頁,
   把**身份釘定**再加強(仍不可餵劇情),或等該劇有更多中文資料後再試。
2. **繁中 `Serce ze szkła`** 已通過但**未涵蓋自傳層次**(官方:Maria Peszek 與其父 Jan Peszek 的自傳線索)。
   簡中新版反而有;日後可考慮重生成繁中一次。
3. **簡中 `Europavisjonar` 字數 527**(區間 400–450)。單獨重跑過一次得 475 字,但新版內容更差
   (多出查無據的「戈爾巴喬夫與雷根」、把 glasnost 誤譯成「去玻璃化」、掉了斯托爾滕貝格與勒龐),
   故**保留 527 字的正確版**。日後若要壓字數,務必再複驗內容。

### 每次改動後請重跑
```
python scratchpad/euro/gen/apply_fixes.py       # 匹配不到即報錯
python scratchpad/euro/gen/regression_check.py  # 哨兵 + 禁用字串(綁定部別)
```

## 正式站驗證(2026-09-01 00:20,DATA_VER `643f16a807`)

在 themusicalmap.com 實際抓 `data/synopses/*.json` 抽驗 **20 項,全部通過**:
- 哨兵(我曾改錯後查證復原的內容,線上確實看得到):`a christmas carol bit` 的 **Rose**、
  `saturnin hybernia` 的 **Jirotka**、`macskafogo` 的 **Cicus**、`zlatovlaska` 的 **Černovláska**、
  `belle e la bestia` 的**公主記憶**
- 實際修好的錯:繁中 `anglagard` 的**贊德**、`made in hungaria` 的**瑞奇**、`mocal story` 的**布拉熱娜**、
  `vy nejste zena pane` 去掉的**寬容聯盟**、`pippi pa sirkus` 的**卡門西塔**、`julekalender` 的**歐魯夫**;
  簡中 `a dzsungel konyve` 的**圖娜**、`metro` 的**揚**、`saturnin hybernia` 的**伊羅特卡**、
  `mohacs 500` 的**拉約什二世**、`snowboardaci` 的**妹妹瑪爾塔**、`emil i lonneberga` 的**長工阿爾弗雷德**、
  `serce ze szka` 的**格爾達**、`musical 1989` 的**瓦文薩**、`europavisjonar` 的**斯托爾滕貝格**

### ⚠ 驗證時踩到兩次的坑:**slug ≠ 劇名**
抽驗時我兩度誤判成「未生效」,其實是查錯 key:
- `Saturnin` 的 slug 是 **`saturnin hybernia`**(不是 `saturnin`)
- `The Julekalender` 的 slug 是 **`julekalender`**(不是 `the julekalender`)
- 最容易誤判的一個:**`A Christmas Carol` 有兩部同名不同戲**——
  既有的英美版是 `a christmas carol`,本批的義大利 Compagnia BIT 版是 **`a christmas carol bit`**。
  我一度以為「我的內容沒寫進去」,其實是拿英美版的 key 去驗義大利版。
→ **驗證前一定先從 `gen/keymap.json` 取 slug**,不要用劇名猜。

## 繁中→簡中「純翻譯」路線(2026-09-01)

那 2 部簡中兩次生成都不通過,改採:**把已查證正確的繁中版交給 Perplexity 做在地化翻譯**
(只轉語言與用語,不得增刪改寫情節)。腳本:`scripts/px_translate.py`。

驗收比生成模式嚴格,因為重點是「不改語意」:
段落數必須與原文完全相同(防漏段)/ 字數比 0.80–1.25(防摘要化或灌水)/ 無繁體字殘留 / 無「以下、翻译如下」前言。

### ⚠ 踩到的坑:`keyboard.type` 遇換行會直接送出
Perplexity 的輸入框是 contenteditable,`p.keyboard.type(Q)` 打到 `\n` 時等同按 Enter → **訊息被提前送出**,
結果只送出第一行指令、原文根本沒貼進去。Perplexity 回的是「请把需要翻译的繁体中文剧情简介贴出来」,
長度 60 字、1 段 —— 這種失敗會「看起來像成功」(有回應、通過 clean),只有靠**段落數/字數比驗收**才抓得到。
修法:逐行 `type`,行間 `Shift+Enter`,最後才 `Enter` 送出。
