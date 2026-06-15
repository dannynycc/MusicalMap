# 巡演查證總表 TOUR SWEEP

> **目的**:把「Beetlejuice 式查證」(官網分區 + 巡演逐站 + 多售票源)系統化套用到**全部**劇目。
> **雙軸查證法(用戶定義)**:
> **軸① 從劇出發** — 每部音樂劇查「現在在哪些地方演」:tm_tours.py 全劇自動掃(每日 CI)+ 官網 /tour /international 頁逐劇 web 查證(Tier 1 表)。
> **軸② 從城市出發** — 鎖定大城市查「這城市正在演什麼」:接城市級來源(如 teatromadrid)或逐城 web 查證(城市表)。
> 「查證為無」也算完成。**未查證的列「待查」,不准留白裝沒事。**

## Tier 1 — 全球大型 franchise(逐劇 web 查證)

| 劇目 | 巡演查證狀態 | 官網(分區) | 最後查證 |
|---|---|---|---|
| The Phantom of the Opera | ✅ NA tour(broadway.org 11 站)+ 上海告別季(manual)+ 名古屋(四季)。World tour 其他站:**待查** | global ✓ | 2026-06-12 |
| Les Misérables | ✅ London + Madrid + NA tour + **Arena Spectacular**(RAH 6/18、Radio City NY 7/23,manual;Birmingham 6/14 已落幕由 audit_manual 抓出移除→歷史檔保留)。World Tour:**新加坡 3/24–5/10、馬尼拉 1/20–2/15 均已落幕**(已查證) | global ✓ | 2026-06-15 |
| Miss Saigon | ✅ UK & Ireland tour 4 站(manual)+ ATG hub 自動 | uk ✓ | 2026-06-12 |
| Beetlejuice | ✅ London(westend)+ NA tour(TM)+ **澳洲巡演**(Brisbane/Adelaide manual;Perth/Sydney TM) | us/uk/au ✓ | 2026-06-12 |
| Wicked | ✅ NYC/London/NA tour。UK tour **2023-25 已結束(查證無進行中)** | us/uk ✓ | 2026-06-12 |
| The Lion King | ✅ NYC/London/漢堡/東京(有明)/巴黎/馬德里/墨西哥城/NA tour。UK tour **已結束(查證無)** | uk ✓ | 2026-06-12 |
| Aladdin | ✅ NYC/London?/東京/NA?。UK&Ireland tour **已結束 2025/1(查證無)** | — | 2026-06-12 |
| Mamma Mia! | ✅ London/NA tour/橫濱(四季)/蘇黎世/維也納/布雷根茨(TM)。國際巡演其他:**待查** | global ✓ | 2026-06-12 |
| Hamilton | ✅ NYC/London/NA tour。雪梨 2025/1 結束;**墨爾本 Her Majesty's 檔期未獲官方日期確認→不入庫,待查**(AU 售票在 Ticketek=新盲區) | global ✓ | 2026-06-12 |
| MJ | ✅ NYC/漢堡(Stage)/伯斯(TM+查證)。NA tour:tm_tours 待確認 | us/au ✓ | 2026-06-12 |
| SIX | ✅ NYC/London/NA tour/AU?。**待查 AU/NZ 分團** | global ✓ | 2026-06-12 |
| Moulin Rouge! | ✅ NYC/London/科隆/NA tour/烏特勒支/**新加坡 Sands 2027-02-16~04-04(manual,SISTIC)**。**待查 AU** | global ✓ | 2026-06-15 |
| CATS | ✅ UK tour(ATG hub 自動)+ **新加坡 Sands 2026-10-29~11-15(manual)** + 南非開普敦/約堡(Ticketmaster.co.za)。 | — | 2026-06-15 |
| Chicago | ✅ NYC + **東京 8/19-30 + 大阪 9/3-6 + 杜拜 12/16-20**(官網 /international,manual)| global ✓ | 2026-06-12 |
| Starlight Express | 波鴻(Stage)✓ + UK tour(ATG)。 | — | 2026-06-12 |
| Frozen | 東京(四季)/斯圖加特(Stage)✓。**待查 UK tour** | — | 待查 |
| Elisabeth | ✅ Ostrava(NDM)+ 宝塚/東京(宝塚)。**待查 維也納/匈牙利 revival** | — | 2026-06-12 |
| Tanz der Vampire | 斯圖加特(Stage)✓。**待查 維也納/其他德語區** | — | 待查 |
| Book of Mormon | NYC/London ✓。**待查 UK tour/國際** | global ✓ | 待查 |
| Tina | 漢堡?(Stage Berlin ✓)/丹麥 3 城(TM)。**待查 UK/NA** | — | 待查 |

## 軸② — 大城市覆蓋表

| 城市 | 覆蓋來源 | 狀態 |
|---|---|---|
| New York / London | broadway-show-tickets / londontheatre+ATG | ✅ 結構化 |
| 英國地方城市(Manchester/Glasgow/Edinburgh…) | ATG hub 33 巡演 201 站 + TM GB | ✅ 結構化 |
| 東京/橫濱/舞濱/名古屋/大阪/福岡 | 四季 API + 宝塚 + TM JP(無)| ✅(四季/宝塚以外的在地製作:**待查**,如東寶/帝國劇場) |
| 首爾/大邱 | Interpark API | ✅ 結構化(東豪/Charlotte 系已含) |
| 漢堡/柏林/斯圖加特/波鴻/科隆 | Stage Entertainment + TM DE | ✅ 結構化 |
| **馬德里** | **teatromadrid.com**(2026-06-12 接入,55 部,西語正名映射) | ✅ 結構化 |
| 雪梨/墨爾本/布里斯本/伯斯/阿德雷德 | TM AU + manual(QPAC) | 🟡 部分(**Ticketek 未接**:Hamilton 墨爾本等) |
| 巴黎 | intl(獅子王)+ Live Nation FR(manual) | 🟡 **待城市級來源**(Mogador/Châtelet) |
| 維也納 | TM AT(2 筆) | 🟡 **待查 VBW(Raimund/Ronacher)**(Elisabeth 系本家!) |
| 上海/北京 | 上海大劇院 manual(API 已知可接) | 🟡 待 SHG 全列表接入;北京待查 |
| 多倫多 | TM CA | ✅ 結構化 |
| 墨西哥城 | intl + TM MX(舊掃描) | 🟡 待查 OCESA |
| 新加坡 | SISTIC/SRT/MBS + manual | ✅ 4 齣到 2027(Legally Blonde/JCS/Cats/Moulin Rouge);SISTIC「STIX」API 需授權,用戶無法取得→手填 |
| 開普敦/約堡(南非) | Ticketmaster.co.za + manual | ✅ Mamma Mia!(自動)+ Oliver!(manual) |
| 聖保羅/里約/布宜諾斯艾利斯 | manual(反爬) | ✅ 巴西 6 / 阿根廷 2 |
| 香港/台北 | 台北已由 OPENTIX/utiki 覆蓋;香港無來源 | 🟡 香港待查 |
| 曼谷/馬尼拉 | 無 | ❌ 多為本土製作;國際巡演 2026 已落幕(待未來檔期) |

## Tier 2 — 區域劇目
由結構來源自動覆蓋(broadway.org 297 站、ATG hub UK tours、TM 16+2 國、四季、宝塚、Interpark、Stage)。`tm_tours.py` 每日對**全部** group 做 attraction 比對,新增站點自動入圖。

## 維護規則
1. 每次 session 從「待查」挑最少 5 部 web 查證,更新本表(含日期)。
2. 用戶點名的劇 → 立即查證 + 回填本表。
3. 查證結果只能來自官網/官方公告/可靠媒體;date 不確定就不入庫,在本表註記。
