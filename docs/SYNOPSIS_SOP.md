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

## 0.5 讀到「這根本不是音樂劇」時：**直接踢，不要問**（2026-09-04）

證據標準已經定死在 `data/not_musical.json` 的 `_comment` 與各批 `_*_note` 裡：
**依據一律是製作方自己的官方文案**，平台的「音樂劇」分類欄不算（那是我們拉資料的條件，恆真）。
只要官方文案自稱舞台劇／音樂會／秀，或形式明顯不是音樂劇，就**直接寫進 `titles` 並附證據 note**，
重建後在報告裡說一聲即可 —— 這是既定規則的套用，不是需要裁決的新政策。

> 2026-09-04 我把《男孩、鼹鼠、狐狸和马》（官方全文自稱「沉浸式舞台剧」、從未出現「音乐剧」）與
> 《海底总动员》（標題寫「大型童话音乐剧」但正文寫「这部舞台剧」）拿去問使用者，被指正
> 「非音樂劇本來就該踢掉不是嗎」。**證據已達標的既定規則不要拿去問。**

**真正該問的**是沒有前例的**分類法**問題 —— 例如「香港作品站上沒有分類，要不要開一個」。
那種一旦決定會改變整個 taxonomy、且無法從既有規則推導，才用 AskUserQuestion 一次問完。

## 1. 消歧義（生成前，**必做**）
同名作品先確認是哪一部，尤其「冷門外語音樂劇 vs 知名歌劇/話劇/電影」。
- 查 `data/works.json`(canonical/aliases) + `data/shows.json`(venue/tag) 定位。
- tag 與 venue 打架（如 tag=台灣原創但場館在大陸巡演）要先查清製作方。

> 🚨🚨 **消歧義只釘「身份」，絕不餵「劇情」。** prompt 只給足以鎖定唯一那一齣的識別資訊
> ——**創作者 / 場館 / 年份 / 製作方**（例：「Pinocchio，Charlie Josephine 編劇、Jim Fortune 作曲、
> 2025 年 Shakespeare's Globe 首演那齣，不是迪士尼版也不是原著」）。**不可把角色名、情節點、結局
> 寫進 prompt。** 為什麼？把劇情餵進去，Perplexity 只會把我的字原封不動吐回來，我再拿它去「查證」
> ＝拿自己寫的東西對自己的 checklist＝球員兼裁判，§3 查證整個失效（2026-08-28 Pinocchio 犯過：
> 我把 Franzini/Fox&Cat/Coachman/Monstra/變真人全塞進 prompt 被抓包）。
> - 我 Chrome 研究得到的劇情 checklist 是**留給 §3 我自己驗證用**，不是餵給 Perplexity。
> - 冷門到 Perplexity 可能全然不知的作品（如台灣在地小劇）：仍以「身份」為主；若真需給一句劇情
>   梗概才鎖得住，也只給**一句最粗的定位**（如「講一對母女道別的原創音樂劇」），且要清楚意識到
>   被餵的那一句不能當成「查證通過」——那句仍要在 §3 獨立對外部源確認。
> - Don Juan 教訓仍成立：同名易漂（中文查 Don Juan 會漂到莫札特歌劇），但解法是釘**身份**
>   （法式音樂劇/2004 魁北克/作曲 Félix Gray），不是餵劇情。

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

> ⚡ **生成這一步可以外包／平行（與 §3 查證相反）。** 生成只是「叫 Perplexity 吐草稿」，
> 沒有判斷、不怕主客顛倒，所以**劇量多時可派幾個 agent 平行去 Perplexity 查**（各拿一批 list、
> 各連 CDP 跑 px_gen），大幅加速；劇量少也可以我自己一批批跑，只是慢。**但 §3 的查證絕不能這樣派**——
> 那一步是我本人的手工活。分工一句話：**生成可平行外包，查證必本人親做。**
> ⚠️ 平行時注意同一個 Comet CDP 9223 只有一個瀏覽器，多 agent 同時打同一 Perplexity 分頁會互搶；
> 若要真平行，各 agent 用不同分頁/不同 CDP 埠，或錯開批次，避免 session 互相干擾。

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

### 3.1 西葡批次(2026-09-02, 55 組)補上的五條規則

1. **錯誤「會不會重疊」有兩種情形，但結論一樣：各語獨立對外部真相查。**
   - 不重疊型（既有認知）：簡中準確度 << 繁中，各語錯在不同地方。
   - **重疊型（本批新增）**：官方文本【刻意留白或與通行版本不同】的地方，模型會用通行版本填滿，
     而且**三語會一起填、填得一模一樣**（`el flautista de hamelin` 的經典結局、
     `el ladron de arabia` 的迪士尼情節、`erase otra vez` 的無來源框架）。
   - ⚠ 所以「三語互相對照」**在兩種情形下都驗不出來** —— 三個版本同源於同一個模型，不是三個獨立來源。
     兩語甚至三語寫了同一件官方沒有的事，那是**同源痕跡，不是佐證**。

2. **比對基準殘缺 → 檢查會靜默漏報。**
   `快乐即逝` 的 `official_plot` 存成了截斷版（少了經紀人 Puck 與鎮長強迫兒子兩句），
   結果英文那一輪「沒判出 Puck 缺席」不是判斷失誤，是**基準裡根本沒有 Puck**。
   → 存官方原文時要確認**存的是完整版**；發現基準有缺口，先補基準再重跑已做過的語言。
   （同類：`feedback_vacuous_negative_test`，檢查的鑑別力取決於基準。）

3. **「懷疑有錯」不等於「有錯」——一律先查證再動手。**
   本批 **17 次**準備當成錯誤處理、查證後發現生成是對的
   （`un refugi al sol` 的法西斯病毒、`rita lee` 簡中獨有的四位巴西音樂人、
   `快乐即逝` 的經紀人帕克＝官方的 Puck…）。
   唯一一次先改後才發現原本正確的是 `mentidrags` 遺囑→信，已還原。
   → **憑印象刪掉不熟悉的具體名字，會刪掉大量正確內容。** 兩個來源用詞不同時，
   不可只憑其中一個宣告另一個錯。

4. **對真實在世者的未證實負面描述，優先級高於一般「未證實」。**
   `rocio durcal es inolvidable` 的英文與簡中都寫了「導演屢受挫折、想靠這部戲翻身」，
   六個來源皆無。即使沒指名，讀者也能直接對應到編劇兼導演 Juan Carlos Rubio 本人 → 直接刪，
   不是「可寫可不寫」的細節。

5. **寫簡介前先問「這到底是不是新作品」——譯名型別名沒有任何自動檢查抓得到。**
   `Assassinat per a dos` 被當成西葡原創寫了整套三語，其實是百老匯《Murder for Two》的
   加泰語版；works.json 早就有這部、也已登記西語別名 `Asesinato para dos`，**只缺加泰語別名**，
   結果同一部作品在庫裡有兩套三語簡介，連角色譯名都不一致。
   - **為什麼沒被擋下**：`discover_unmapped()` 比的是**標題相似度**，
     而「Assassinat per a dos」對「Murder for Two」的相似度是 0 —— 翻譯型別名它結構上就看不見。
     偵測器沒報 ≠ 沒問題。
   - **辨識鍵是內容不是標題**：用角色名、主創、時長、劇情梗去對。
     Focus 官方 fitxa 直接寫 `Títol original: Blood brothers / Willy Russell`（`Germans de sang`）
     是最乾脆的一種；沒寫的就對角色名（Marcus Moscowitz / Arthur Whitney / Dr. Griff…）。
   - ⚠ **反向同樣要防：譯名相同不等於同一部作品。**
     `El Mago de Oz`（Teatro Sanpol）是自家劇團 La Bicicleta 的原創改編，
     角色叫 **Dorita / Tía Enma / Achicoria / Profesor Maravilla**，歌詞是 J. J. Fischtel 寫的，
     跟已登記的百老匯 `The Wizard of Oz` 無關；葡萄牙的 `Cinderela` 同理。
     照標題無腦加別名會把在地原創錯併進百老匯組 —— **一律逐部查，不批次推定**
     （memory `feedback_origin_per_show_not_batch`）。
   - **合併後要驗差值不是驗最終狀態**：組別筆數一增一減、**總場次必須不變**；
     在地製作名要留在 `tour_name`；孤兒簡介要刪掉。

### 3.2 韓國批次(2026-09-03, 59 組)補上的八條規則

1. **官方【CAST／角色表圖】是必讀的第二基準，只對劇情文字會漏掉一整類錯。**
   本批最常見的錯不是情節寫錯，而是**把原著/小說/傳說的人物寫成這個製作的角色**：
   `휴남동 서점` 英簡把小說才有的 지미·상수·민철 寫成台上角色（官方캐스팅只有 5 角）、
   `Club 설화` 三語共同虛構了「까치와 까마귀」主持串場（官方 CHARACTER & CAST 只有四隻）、
   `늦봄의 길` 英文生出「Peimun」這個根本不是韓文的名字、
   `청사초롱` 英文憑空生出五名員工而真正的 수두매 反而消失。
   → **每部都要把三語裡出現的人名逐一對回官方角色表**；官方沒有的名字一律當紅旗。

2. **🚨 我自己讀圖轉錄進帳本的內容也會錯，而且錯了會污染重生成 prompt。**
   本批查出 **5 齣**：`좀비` 把角色標籤【아들(兒子)】讀成【아빠(爸爸)】（簡中因此寫出「另一位爸爸」）、
   `헤어드레서` 把兩位主角的招牌台詞【對調】、`오싹한 알바` 四句台詞【錯三句】且漏掉「알bar 在 20cm 玻璃牆內」、
   `놐놐놐` 把【기숙학교】讀成「가옥학교」、`Club 설화` 놀부 台詞誤植。
   → 用帳本的 `characters` 做判斷【之前】，先回原圖確認；發現不成詞的韓文（`소스코롤`、`너무슨`）就是轉錄壞掉的訊號。

3. **查到來源要當場落帳，否則等於沒查。**
   本批一度顯示「僅官方 27 齣」，但其中 13 齣我當天明明搜到 5～8 個來源，只是**讀完沒寫回 ledger.sources**。
   分級腳本讀的是帳本，不是我的記憶 → **搜完立刻寫，不要留到最後**。

4. **同一張官方詳情圖的不同段落是【一個】來源，不是四個。**
   海報／SYNOPSIS／CAST／INFORMATION 全部同源。把它們當成「5 源、7 源」會讓 `external_multisource`
   整批灌水。分級一律只數**獨立於主辦方**的來源（媒體、나무위키、PlayDB、觀後感、政府 KOPIS…）。

5. **外部來源要分「公演消息層級」與「劇情層級」。**
   `오셀로와 이아고` 找得到 6 個外部來源，但全部只寫「初演、9/8~11/22、大學路自由劇場」，
   **沒有一篇談劇情** → 劇情實質上仍是官方單一來源，要在帳本標明，不可當成劇情已被交叉驗證。

6. **官方與外部報導衝突時以官方為準，並把差異記進 `ledger.discrepancy`。**
   `달콤한 위로 초코파이`：2025 年兩家報紙寫麵包店是「동오제빵소」，但本製作 2026 官方詳情頁逐字是
   「명진제빵소」（且官方美食地圖列有真實店家 명진당）→ 採官方、記差異，不要拿報導去改官方。

7. **手改一律改在管線的【源頭檔】。**
   `merge_all.py` 每次執行都會用 `regen_*.json` 覆寫 `out_*.json`；改在 out_* 的補寫會**靜默消失且 exit 0**。
   背景工作跑著時更不能改它的輸出檔（px_gen 每完成一齣就整檔重寫）。
   改完必須**重跑完整管線 + 重跑把關**，用「把關數字有沒有回彈」當證據。（memory `feedback_edit_pipeline_source_not_output`）

8. **「懷疑有錯」仍然不等於「有錯」——本批 11 次被推翻，只有 1 次先刪才發現刪錯。**
   被推翻的包括：`Robert Alexander Schumann` 的中間名（德文維基證實）、`빨래` 的「빵」是真角色（제일서점 사장，
   본명 엄훈성）、`london record` 的「Charlie」（官方角色表有 찰리·샐리）、`종의 기원` 的「Yumin」、
   `widerstand` 的 Hagen/Jasper、`카페인` 的「끝에서 두 번째 여자」、`1457` 的「三名鬼怪」（實為 도깨비 삼남매）。
   唯一誤刪：`늦봄의 길` 的「지영」——부천문화재단官方 SYNOPSIS 寫著「지영이의 손에 이끌려 온 루다」，已復原。


### 3.3 歐陸/日台/百老匯批次(2026-09-03, 19 組)補上的六條規則

**一、先建【官方角色表】,它比劇情文案更能擋錯。**
這批六成的錯只有角色表擋得住,劇情文案完全看不出來:
- `Na prochach` 官方文案只說「被稱為美國最糟糕的家族」「一家製藥公司的老闆」,
  但角色表寫明台上姓氏是**虛構的 Barker**。沒有角色表就一定會寫成 Sackler/Purdue。
- `Romeo i Julia` 角色表有莎劇沒有的 **Dealer(毒販)**,加上官方內容警告列毒品/自殺/殺人
  → 是現代改編,套通用莎劇就是錯。
- `Piotruś Pan` 角色表有 **Dorosła Wendy** 與 **Jane** → 含長大後的框架,不只演小孩篇。
- `Két összeillő ember` 角色表**只有兩個角色**,寫出第三人就是錯。
劇院官網的角色表通常在「Obsada / Repartiment / 演員」區,抽取時**要抓到區塊結束**,
不可只抓前幾筆(我這批就因為截斷,把三個真實角色誤判成捏造)。

**二、第一輪生成的提示【只釘身份、不給情節】。**
把官方劇情餵進第一輪提示,產出就是照抄我給的東西,再拿同一份去「查證」等於球員兼裁判。
帳本要留在裁判席。**查證做完、錯誤逐項記錄之後**,第二輪才用官方事實去約束重生成。

**三、修 A 會引入 B,重生成後必須再讀一次。**
第二輪把角色表餵進提示擋住了捏造,卻**自己帶進三個新問題**:
- 模型開始**列名單**,把「Carole/Konferansjerka/Brenda」這種連斜線的角色欄位原樣抄進正文,
  讀起來像節目冊 → 提示要同時寫「用流暢散文,不要列出全體演員,不可抄含斜線的角色欄位」。
- `天堂邊緣` 英文稿**直接夾中文字**(「秀燕、何智 and 菲菲」)→ 匯出前要有機械關卡擋。
- `プリキュア` 因為提示幾乎全是否定句(不准編動機/性格/戰鬥),**英文 7 次全部回傳空白**;
  同一則提示在中文卻有產出 → 官方資訊極少的戲要改用**正面敘述**的提示。

**四、日文漢字名必須照抄,不可音譯或重造。**
`プリキュア` 繁中把官方的 **神白彩人**寫成神代彩人、**蜂針衣月**整個換成蜂張樹、
**百瀬昭彦**寫成百瀨明彥。繁化(御厨→御廚)是對的,改字就是錯。

**五、通用譯名優先於音譯。**
`Caperucita Roja` 第二輪被音譯成「卡佩露西塔」,第一輪用的是通用的「小紅帽」——
中文讀者看不懂音譯,是明顯退步。

**六、懷疑不等於有錯,刪改前先查(這批我判錯四次)。**
- `Bitwa o tron` 的 Kordecki/Skarga/Katarzyna Wielka:我以為捏造,實際全在官方名單上,
  是**我自己抽表時截斷**。
- `Szécsi Pál` 自殺:我以為是未查證的推定,匈牙利維基寫明「1974-04-30 夜,最後一次已來不及阻止」。
- `Łamignat` 的「强盗」:我以為與「雅加的丈夫」矛盾,波蘭維基寫「Jaga 和她的丈夫、**強盜** Łamignat」,
  兩者都對。
- `Tania Ruzs` 的日期:聚合站顯示 expired 2026-03-07,回查 atrapalo 官方是 9/4–10/30,與我方一致。
全部記在帳本的 `_overturned_suspicions`。

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
- 🚨 **看 `build_served` 的 `::warning::` 孤兒鍵告警**（2026-09-04 加）。庫裡有、catalog 沒有的鍵
  大多是檔期已過（正常，庫本來就長期保存）；但如果某個庫鍵**極接近**某個 catalog group，那通常是
  **鍵打錯**，簡介明明備好卻永遠送不出去，而且管線只印「庫 605 → served 527」完全看不出異常。
  實例：庫鍵 `生命最美好的5分鍾` vs catalog `生命最美好的5分鐘` —— 简体「钟」還原繁體時 鐘/鍾 選錯，
  這齣台灣劇（苗北 11/13，檔期還沒到）三語簡介一直沒被服務。⚠ **只告警不自動合併**：同一輪也撈到
  `テニスの王子様` vs `新テニスの王子様`，那是兩部不同作品，合併就錯了。
- 🚨 **每次 merge 後重掃殘留**：來源 slug（單一小寫 latin token）、「全劇總結」標題會被重新帶進來。
  → 用 §5.5 的 `defect_regression.py`，不要用肉眼。

## 5.5 入庫後的自動化把關（2026-09-01 建立；**四支都只是線索，不是判定**）

| 工具 | 抓什麼 | 已知局限（務必先讀） |
|---|---|---|
| `scripts/qa/defect_regression.py` | 七類**先前真的發生過**的缺陷：英文 slug 殘留、簡中清晨時間戳、「全劇總結」標題殘留、書評框架開頭、段落過少、說明性開場、引用/UI 殘留 | slug 檢測只比對**含連字號的多詞 group slug**。第一版寫成「連字號連三個以上小寫詞」，6 筆全誤報（`thirteen-year-old`、`good-and-evil`、`larger-than-life` 都是合法英文）；改成比對 group slug 後仍誤報單字 group（`metro` vs 正文的 the metro） |
| `scripts/qa/xlang_scan3.py` | 繁×簡**整篇講不同故事**（bigram Jaccard + 已知陽性基準線） | **一定要拿已知陽性當基準**，否則看不出門檻在哪。已知陽性 0.0578 / 全庫最低 0.0706 —— 只差 0.013，**低分不等於有問題**（翻譯稿分數高、獨立生成分數天然就低），一律人工複查 |
| `scripts/qa/year_scan.py` | 三語**年份**不一致（年份不受音譯影響，是唯一橫跨三語的硬錨點）+ 三語完整性 | **訊噪比很差，10 個裡 9 個誤報**：`"1990s"`/`"early-1960s"` 會被抓成 1990/1960；某語有某語無只是詳略差異。價值不在判定，而在**把視線帶到某一句**（曾順著 "In 1969" 讀到同句的專名錯字 Xintia→Cynthia） |
| `scripts/qa/check_translation_locale.py` | 繁→簡翻譯稿**有沒有真的換詞**（OpenCC 只轉字不轉詞） | 詞對表第一版 25 組裡有 **14 組是錯規則**（`乐团`/`团员`/`影片` 在大陸完全通用），全庫掃出的 13 組全是誤報。現為 16 組，砍掉的原因寫在腳本註解，**別再加回來** |

**2026-09-02 新增第五支 + 兩處改動**

| 工具 | 抓什麼 | 備註 |
|---|---|---|
| `scripts/qa/scan_bare_headings.py` | 正文**中間**的裸標題（「Themes」「主題」「全劇總結」單獨成段） | `px_gen.py` 的尾段守衛只砍**結尾**，砍不到夾在段落中間的，所以會一路寫進知識庫。判準：單行、長度 < 40、結尾不是句末標點。首次全庫掃描抓出 **32 篇**歷史殘留（15 繁 / 17 簡）。`--fix` 就地修 |

- `defect_regression.py` 改為**自動載入 `scripts/qa/fixtures/*_groups.json` 全部 fixture**
  （原本寫死 `euro_groups.json`）。加新批次只要丟一個 fixture 檔進去，涵蓋範圍 56 → 111 組。
- 檢查 G（引用/UI 殘留）擴充：`[1]` 被上游清掉數字後會留下**空的全形方括號 `［］`**，
  原規則只認有數字的版本。px_gen 的 `clean()` 也已就地清除。

🚨 **新掃描器上線前一定要做反向測試**：先注入一個已知缺陷確認抓得到、再移除確認回到 0。
否則「掃描 0 命中」可能只是規則根本沒作用——這次兩支新規則都跑過這個自檢。

**兩條血淚規則**
1. 🚨 **自己做的檢查工具，規則表本身也要驗證。** 沒驗證的規則表只會製造誤報，
   比沒有工具更糟——它會讓人去「修」根本沒錯的東西。
2. 🚨 **自動掃描全過 ≠ 品質好。** 四支全綠仍要人工讀；反過來，掃描報的低分/命中
   多半是誤報，**判定一律靠人工讀三語 + 查官方**（`feedback_full_read_beats_automated_qa`）。

**翻譯稿（`px_translate.py`）另有兩個專屬風險**
- `--dir en2zht`（英譯中）會留**翻譯腔**：`populated by`→「住著」、`separation`→「離散」、
  `breaking the story open`→「撕裂」、`bodily embarrassment`→「窘迫」。譯完必須通篇重讀潤稿。
- 潤稿時以「**專名集合前後必須完全相同**」為硬條件把關（拉丁專名數 + 各專名出現次數）。
  這條真的攔下過事故：為避免同句重複把第二個「冰雪女王」改成「另一面」，
  但官方角色表的 `Królowa Śniegu` 與 `Królowa Śniegu W Kryzysie` 是**兩個列名的角色**。

## 6. 上線 + 正式站驗證（不拿 localhost 交卷；`feedback_verify_on_production_not_localhost`）
- commit（只 stage 自己的檔）+ CHANGELOG（台北時間 HH:MM，先跑 Get-Date）+ tag + push。
- CF Pages 自動部署。驗：正式站 `themusicalmap.com` 的 `DATA_VER` == repo；
  `data/synopses/en.json` 的 `syn` 新 group 到位；抽該 group 卡片數 >0。
- ⚠️ push 事件 CI **不重建網站**，本機要補跑 gen_catalog/gen_variants/gen_site（`project_musicalmap_workflow`）。
- ⚠️ 凌晨別跟每日 CI 搶 push：先 `gh run list` 看有無進行中的 schedule run，避免 non-fast-forward 卡住當天資料刷新。

## 7. 開頭文風（策展政策，`project_musicalmap_kb_banking`）
「直接入戲」：第一句進場景，禁「《劇名》描寫/講述…」「以…為背景」書評口吻。
改寫第一句必連第二句一起看，避免語意重複。
