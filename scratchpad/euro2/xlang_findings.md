# 跨語言一致性掃描:方法、失敗紀錄與發現(2026-09-01)

## 為什麼做
`Szeretve mind a vérpadig` 的簡中整篇是幻覺(1870 年代/阿爾帕德/伊洛娜),
而前一輪**只逐句比對繁中就結案**,完全看不到。
→ 同一個系統性漏洞可能也影響先前那 51 組,必須全庫掃一次。

## 方法演進(含兩次失敗,記下來別再走一次)

**v1 bigram Jaccard(全部字)**
全庫 473 組落在 0.071~0.145,沒有分界 → 一開始判斷「沒有區辨力」。
**錯在沒有基準線**:我沒有先算已知陽性的分數就下結論。

**v2 重複出現的 3 字序列(當專名代理)—— 作廢**
對已知陽性 0.000、修正後 1.000,看似完美。
但全庫有**大量 0.000**:`a christmas carol` 繁「史古基」vs 簡「斯克鲁奇」——
**繁簡各自獨立生成時,音譯人名本來就不同**。
這個指標其實在測「這篇是不是翻譯來的」,不是測幻覺。**不可用。**

**v3 = v1 + 基準線(採用)**
| | 分數 |
|---|---|
| 已知陽性(Szeretve 幻覺版) | **0.0578** |
| 全庫 473 組最低 | 0.0706 |
| 全庫第 1 百分位 | 0.0750 |
| 全庫中位數 | 0.1453 |

→ 沒有任何一組落到已知陽性的水準。
⚠ **但陽性樣本只有 1 個、差距只有 0.013,不能據此宣稱全庫乾淨**,
所以進一步**人工抽查最低分的組**——結果證明抽查是對的,三組全都有問題。

## 抽查結果(最低 3 組,全部有實質問題)

### 1. `serce ze szka musical zen`(0.0706)— 🔴 **繁中整篇偏離,在歐陸委託範圍內**
官方 teatrstudio.pl 逐字:
> „Serce ze szkła. Musical zen" **na motywach „Królowej Śniegu" Hansa Christiana Andersena
> i „Naku\*wiam zen" Marii Peszek**

= 取材自安徒生《冰雪女王》**與 Maria Peszek 本人的自傳散文**;
libretto Klaudia Hartung-Wójciak、音樂 Andrzej Smolik、導演 Cezary Tomaszewski;
主演 **Jan Peszek + Maria Peszek**(真實父女)。

| 語言 | 判定 |
|---|---|
| **英文** | ✓ 最完整。含官方角色表細節:四個 Gerda 化身 **Maryjka / Ren / Mania / Maryśka**、**Królowa Śniegu W Kryzysie**(危機中的冰雪女王)、Wrona/Kruk/Gołębica/Finka/Matka Kaja/Lapończyk/Zbójniczka、**Specjalistka Od Andersena**、Dejmek、**zima stulecia**、osiedle Teofilów;明寫 father–daughter |
| **簡中** | △ 抓到父女主線與冰雪女王、空教堂、沼澤、盜賊城堡、破敗街區,但**沒提取材自安徒生** |
| **繁中** | ✗ **寫成標準的安徒生《冰雪女王》童話**:「少女葛爾達尋找被冰雪女王帶走的朋友凱」。<br>完全沒有 Maria/Jan Peszek 父女這條主線(本作的另一半核心),<br>也把「多個 Gerda 化身」誤寫成單一少女主角 |

→ **繁中須重寫**(以已查證的英文版為源)。

### 2. `grand hotel`(0.0724)— ⚠ 不在歐陸委託範圍(百老匯),僅記錄
- **項鍊材質矛盾**:繁「**鑽石**項鍊」vs 簡「**珍珠**项链」;英文只寫 "steal jewels" 未指明。
  (原著 Vicki Baum《Menschen im Hotel》與 1932 電影皆為 **pearls**,繁中的「鑽石」可疑)
- **男爵死因動機不一致**:繁「聽見她求救,挺身阻止;混亂中普萊辛持槍殺死了他」
  vs 英/簡「**行竊時被 Preysing 當場抓到**而遭殺害」。英文逐字:
  "Preysing catches Felix **during the attempted robbery** and kills him"
- 繁中獨有「克林格萊因在費利克斯**引介下投資獲利**」→ 英文與簡中皆無

### 3. `screwtape letters`(0.0745)— ⚠ 不在歐陸委託範圍(美國製作),僅記錄
- 英文逐字:"With the seasoned demon **Lilith** as part of the operation"、
  "placing Wormwood and **Lilith** under increasing pressure"
- 繁中有「經驗豐富的女惡魔**莉莉絲**」✓ 與英文一致
- **簡中完全沒有 Lilith 這個角色** → 簡中漏

## 處置
- **範圍內**(歐陸原創):`serce ze szka musical zen` 繁中重寫。
- **範圍外**(grand hotel / screwtape letters 等非歐陸組):**不擅自大改**,
  整理成清單交使用者定奪——避免把「歐陸簡介查證」擴張成「全庫 473 組重審」。
- 掃描器留在 `scratchpad/euro2/xlang_scan3.py`,可隨時重跑;
  完整分數在 `scratchpad/euro2/xlang_scan2.json`(v2,僅供參考,指標已作廢)。

---

# 歐陸原創低分區:7 組全部人工複查完畢

掃描只是**線索**,判定一律靠人工讀三語 + 查官方。歐陸原創 54 組中分數最低的 7 組:

| 組 | 分數 | 判定 |
|---|---|---|
| serce ze szka musical zen | 0.0722 | 🔴 **繁中整篇偏離 → 已重譯** |
| forza venite gente | 0.0796 | ✅ 通過 |
| saturnin hybernia | 0.0805 | ✅ 通過 |
| rebelove karlin | 0.0860 | ✅ 通過 |
| il ragazzo dai pantaloni rosa | 0.0911 | ✅ 通過(**差點誤判,見下**) |
| julekalender | 0.0935 | ✅ 通過 |
| made in hungaria | 0.0880 | 🔴 **簡中主線被換掉 → 已重譯**(0.088 → **0.779**) |

## ⚠ `il ragazzo dai pantaloni rosa`:我差點第三次把對的改成錯的

一開始看到繁簡矛盾就準備判簡中錯:
- 繁「疼愛自己的母親泰蕾莎、**父親與弟弟**,日常看似平凡溫暖」
- 簡「**父母分居後**,安德烈背負起照顧弟弟的壓力」

it.wikipedia 第一段:「Andrea Spezzacatena è un adolescente che **vive con i genitori Teresa e Tommaso
e il fratello minore Daniele**」→ 看起來繁中對、簡中錯。
我還找到一則部落格寫 Andrea 羨慕「genitori divorziati come i suoi amici per regali, vacanze e
paghette doppie」(羨慕朋友父母離婚可以拿雙份禮物零用錢),差點就用它「證實」簡中誤讀。

**繼續往下讀才發現:**
> Andrea subisce un duro colpo quando **i suoi genitori gli annunciano di voler divorziare**.

父母**後來確實宣布要離婚**。繁中寫的是開場狀態,簡中寫的是後續發展,**兩者都正確**。
另外簡中的「音樂老師焦利」也有據——演員表逐字「**Settimo Palazzo: prof. Gioli**」。

→ **判定 0 修正。** 這是本次第三次「差點拿一個片段去訂正另一個」,
教訓同前:**讀完整段再判,單一段落不足以否定另一語言的敘述。**

## 其餘 5 組的查證重點

- **julekalender**:三語角色全對得上(Gammel Nok / Nasser / Benny / Oluf / Gertrud);
  簡中另有「小飛機墜落土豆田」,英文亦作 "A storm-tossed craft" → 簡中更精確,繁中只是略。✅
- **saturnin hybernia**:繁「吉羅特卡」/簡「伊罗特卡」/英 "Jirotka" 一致。
  ⚠ Jirotka 是**原著作者名**(Zdeněk Jirotka),小說裡敘事者無名——但前一輪已查證
  hybernia.eu 官方卡司框有「**Jirotka — Radek Melša**」,本舞台版就是把角色命名為 Jirotka。✅
- **rebelove karlin**:cs.wikipedia 逐字「v českém **pohraničí** v červnu až srpnu roku **1968**」、
  「tří **maturantek** – Terezy, Bugyny, Julči, a tří vojáků, **uprchlíků z armády**
  – Šimona, Boba a Emana」→ 繁中的年代、邊境、三名剛畢業女生、三名逃兵全部對上。
  音樂劇版角色表另有「**Farář**(牧師)– Vladislav Beneš / Petr Štěpánek」(zena-in.cz 2020 角色表)
  → 繁中「躲在**牧師**親戚所在的教堂」有據。✅
  ⚠ **未能證實(無反證,故不改)**:繁中的「幫父親打理**新開的咖啡館**」與「三名自稱**修理工**」
  在 cs.wikipedia 與官方角色表都查不到。條目本身極短,「查無」不等於「錯」→ 列為待查。
  另註:cs.wiki 載結局為「Tereza, **její otec a jeho přítelkyně emigrují. Šimon skončí ve vězení**」
  (泰蕾莎與父親及父親女友移民、西蒙入獄),繁簡兩版都只寫到「被迫分離」,未寫結局 → 是略非錯。
- **forza venite gente**:繁「嘉勒」/簡「圣女克拉拉」= Chiara/Clare 兩岸不同譯法,非矛盾;
  簡中把「貧窮」「魔鬼」列為登場人物,與本劇的擬人化角色設定相符。✅

---

# 翻譯稿的「用語有沒有真的換」檢查(2026-09-01 補做)

使用者原話:「拿繁中結果的去叫 perplexity 翻成簡體的語意(**並且使用中國用語**)」。
OpenCC 只轉字不轉詞,所以「有沒有換詞」要單獨驗。工具:`scripts/check_translation_locale.py`。

**4 篇繁→簡翻譯稿(vizeli / made in hungaria / aggiungi / a padlas)全部通過**,
而且人工讀過確認**遠超過轉字層次**:

| 繁(來源) | 簡(翻譯) |
|---|---|
| 處處**杯葛** | 处处**阻挠**(杯葛是台灣音譯詞) |
| **超級電腦** | **超级计算机** |
| **羅賓森** | **罗宾逊**(Robinson 大陸通譯) |
| 克**蕾**曼蒂娜 | 克**莱**曼蒂娜(音譯用字) |
| **通緝中的**匪徒 | **遭到通缉的**匪徒 |
| 分散警方**注意** | 分散警方**注意力** |

## ⚠ 工具本身第一版的詞對表有 14 組是錯規則

全庫掃出 13 組「問題」,結果**全是誤報**——最先看到的三筆就揭穿了:
「乐团」「团员」在大陸完全通用(交响乐团、乐团团员),根本不是台灣專用詞。
逐條檢視後砍掉 14 組(原因寫在腳本註解,含「影片→视频」「品質→质量」「大廈→大楼」
「鳳梨/馬鈴薯/番茄」「夥伴→伙伴(轉字後即相同,規則無效)」等),25 組 → **16 組**。
修完全庫重掃:473 組只剩 **1 齣劇**命中。

**教訓:自己做的檢查工具,規則表本身也要驗證**——沒驗證的規則表只會製造誤報,
比沒有工具更糟(會讓人去「修」根本沒錯的東西)。

## 真實命中 1 筆(非歐陸範圍 → 記錄不改,交使用者定奪)

`moon sorbet` / `月亮雪酪`(同一齣**台灣**劇的兩個 group)簡中:
> 酷热的夏夜,整栋公寓的人都躲进**冷气房**贪凉…热心的**主委**奶奶最先听见那神秘的滴答声

- 「**冷氣房**」是台灣用語,大陸說「**空调房**」
- 「**主委**」是台灣的公寓大廈管理委員會主委,大陸會說「业委会主任」或「居委会」

依本次的範圍紀律(委託是歐陸原創 54 組),**不擅自改**,列入待定奪清單。
