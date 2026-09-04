# 中國原創批次 收尾步驟(照順序,每步都要驗)

> 寫下來是因為這條鏈有五個環節【失敗時不會報錯】,只會讓結果看起來成功但沒上線。

## 1. 等生成全部結束
```
powershell -NoProfile -Command "Get-CimInstance Win32_Process -Filter \"Name like 'python%'\" | Where-Object { $_.CommandLine -like '*px_gen*' } | Measure-Object | Select-Object -Expand Count"
```
必須是 `0`。🚨 `apply_fix.py` 會自己擋(px_gen 執行中拒寫,exit 2)——因為 px_gen 把整份
results 留在記憶體、每收一篇整檔覆寫,中途寫進去的修正會被靜默吃掉。

## 2. 備份 → 套用修正
```
cp regen_{zht,en,zhs}.json → *.prefix.json     # 給第 5 步的守門差異比對用
python scratchpad/cn82/apply_fix.py scratchpad/cn82/fixes3.json      # 繁中+英文(第三輪)
python scratchpad/cn82/apply_fix.py scratchpad/cn82/fixes_zhs.json   # 簡中
```
每條修正都斷言「原字串出現剛好 N 次」,改不到當場失敗、且【寫檔前就失敗】所以原檔不動。

## 3. 字形/用語正規化
```
python scripts/zht_glyph_norm.py scratchpad/cn82/regen_zht.json     # 繁中:祕/舞台/一齣/岳/身分/回歸/船夫 + 台灣定譯表
python scripts/zhs_quote_norm.py  scratchpad/cn82/regen_zhs.json     # 簡中:「」→“”
```
🚨 兩支都不可跑錯語言:`zhs_quote_norm` 對繁中檔會拒跑(exit 2);
`zht_glyph_norm` 的規則對簡中無意義(簡體沒有這些異體字)。

## 4. 雙向抽驗
舊字串不在、新字串在。至少抽 15 項,涵蓋三語。

## 5. 守門前後差異比對
```
python scratchpad/cn82/cn_gate.py <before>  > before.txt
python scratchpad/cn82/cn_gate.py <after>   > after.txt
diff before.txt after.txt
```
- 消失的告警要對得上我修的東西
- 🚨 **新增的告警要逐條解釋**。有些是修正的必然後果(例如霍普→Hope 之後拼音就對不上了),
  那不是問題;但要親眼確認每一條。

## 6. 重讀被改動的段落(不可省)
守門看不到插入句順不順。上一輪就抓到我的修正自己造成三個問題:
專名在相鄰兩句重複、開頭變成介紹原著而非本劇、同一人中英兩種寫法並存。

## 7. 重建 keymap(🚨 必須在生成全部結束【之後】)
```
for s in zht en zhs: python scratchpad/cn82/mk_keymap.py $s
```
然後驗命中率:`{t:g for g,t in keymap}` 對 `regen_*.json` 的 `show` 欄,三語都要 **69/69**。
🚨 keymap 從【結果檔】建不是從清單檔建——清單檔會被 mk_regen 重跑覆蓋,兩者一漂移就全毀
(實測英文曾 0/69,而 kb_merge 對不到【不會報錯】,只會用 group_key(整段 prompt) 算出垃圾鍵)。

## 8. 入庫
```
python scripts/kb_merge.py zh-hant scratchpad/cn82/regen_zht.json scratchpad/cn82/keymap_zht.json
python scripts/kb_merge.py en       scratchpad/cn82/regen_en.json  scratchpad/cn82/keymap_en.json
python scripts/kb_merge.py zh-hans  scratchpad/cn82/regen_zhs.json scratchpad/cn82/keymap_zhs.json
```
🚨 **逐行讀 `scripts/kb_merge.last.log`**:每一筆的 `<整段prompt> -> <group>` 都要是真 group,
不可以有看起來像 prompt 開頭的垃圾鍵。新增數應為 69(+補充 7),覆蓋數應為 0。

## 9. 前端過濾 + 建站
```
python scripts/build_served_synopses.py     # 庫 → data/synopses/(只留在 catalog 的)
node build/gen_site.mjs
```
讀 build_served 的 stderr:`庫 N/語 → 前端 served M/語`,以及【近似孤兒鍵】告警。

## 10. 部署 + 正式站驗證
🚨 不拿 localhost 或 curl 交卷。要在**正式站**上,用瀏覽器實際打開幾齣劇的頁面,
三語各看一遍,確認簡介真的顯示、而且是修正後的版本(挑幾個我改過的句子去對)。

## 11. 收尾
CHANGELOG(台北時間,先跑 `Get-Date`)+ 所有 md + commit + tag + push,
驗 `behind=0 ahead=0`,然後才 `CronDelete` 停 loop。
