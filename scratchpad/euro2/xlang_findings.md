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
