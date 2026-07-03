# 資安 / SEO 通盤健檢報告 — 2026-07-02

> 對 MusicalMap（GitHub Pages 靜態站 + Supabase 後端）做的完整資安、SEO、AI-search 健檢紀錄。
> **後續（2026-07-03/04，見 CHANGELOG）**：另修 display_name 落 email(`fix_display_name_email_leak.sql`)、公開頁自訂海報可當追蹤信標(v1.29.13,posterFull 一律走代理+referrerpolicy)、handle 至少需字母數字(v1.31.2 前端+DB `add_handle_alnum_check.sql`)、新增刪除帳號 GDPR RPC(`add_delete_account.sql`)。本報告為 07-02 當日快照，不回改。
> 涵蓋：RLS/授權、SQL injection、XSS、金鑰、供應鏈、SEO、AI-search，以及 themusicalmap.com 遷移與 `my.` 子網域架構建議。

## 架構前提（理解一切的基礎）

前端（GitHub Pages 靜態 HTML/JS）**直連 Supabase**，anon publishable key 公開在 `js/config.js`。因此：

- **傳統 SQL injection 架構天生免疫**（見下），真正的攻擊面是 **RLS（未授權存取）**——攻擊者可拿公開 anon key 繞過前端直打 REST API，擋他的是 Row Level Security，不是 injection 防護。
- 前端「藏起來」不等於安全；任何敏感過濾必須在 DB 層（RLS / SECURITY DEFINER 遮罩函式）完成。

---

## 一、後端 RLS / 授權（線上 `pg_policies` 實測，非讀檔推測）

| 對象 | 線上實際狀態 | 結論 |
|---|---|---|
| `sightings` 讀 / 寫 | 都是 `(user_id = auth.uid())` | ✅ 票價/座位/筆記不對匿名外洩 |
| `profiles` 讀 | `(is_public OR id = auth.uid())` | ✅ 公開目錄設計 |
| `profiles` 寫 | `(id = auth.uid())` | ✅ 限本人 |
| `venues` 讀 | `true` | ✅ 字典資料，可接受 |
| `public_sightings` / `handle_available` / `handle_new_user` | 皆 SECURITY DEFINER + `search_path=public` | ✅ 無提權、無 mutable search_path |

### Critical（已確認是啞彈）
最初 `schema.sql` 的 `sightings_read` 帶 `... OR (is_public)` 分支，會讓匿名 anon key 直接讀走公開帳號**整列**（含 price/seat/note）。修法 `add_share_privacy.sql` 把它收緊成 `user_id = auth.uid()`，公開資料改走遮罩 RPC。**線上實測 `qual = (user_id = auth.uid())` → migration 已套用，此洞已關閉。**

### 遮罩 RPC（已驗證正確）
`public_sightings(p_handle)`：`SECURITY DEFINER` 繞 RLS，但 `where ... and p.is_public`（非公開回 0 筆）、price/seat 依 `show_price`/`show_seat` 開關遮罩、**note 完全不在回傳欄位**。參數化 `p_handle`，無動態 SQL。

---

## 二、SQL Injection（靜態分析：零可利用面）

- **DB 函式**：grep 全 `supabase/*.sql` 找 `EXECUTE` / `format(` / `||` 拼接 → 只命中 `grant execute` 與 trigger `execute function`，**無任何動態 SQL**。函式一律靜態 SQL + 綁定參數（`where lower(handle)=lower(p_handle)`）。
- **前端**：grep 全 `js/*.js` 找 supabase-js filter → 唯一 DB 呼叫是 `u-view.js` 的 `.rpc('public_sightings',{p_handle})`（物件參數綁定）；其餘 `.eq()/.upsert()` 皆參數化；**無 `.or(\`col.eq.${input}\`)` 字串拼接 filter**（PostgREST query injection 也不存在）。

### 🚨 維持免疫的兩條鐵則（未來寫 code 絕不可破）
1. RPC/DB 函式**不可寫動態 SQL**：禁止 `EXECUTE 'SELECT...' || 變數` / `format()` 拼使用者輸入。
2. 前端**不可字串拼接 filter**：禁止 `.or(\`col.eq.${input}\`)`，一律 `.eq('col', value)` / `.rpc('fn',{param:value})`。

破這兩條任一 = 立刻開注入洞。

---

## 三、XSS / 金鑰 / 供應鏈（前端）

- **公開頁 `u-view.js`（最高風險面，render 別人資料）**：所有使用者欄位（劇名/劇院/城市/座位/票價/URL）全過 `esc()`，URL 另過 `safeUrl()` 限 http/https，note 在公開頁根本不 render。✅ 無 stored XSS。
- **金鑰**：`config.js` 是 `sb_publishable_` 公鑰（設計上公開），非 service_role；Mapbox `pk.` 公 token（已設 URL referer 限制）；affiliate ID 本就出現在外連 URL。全庫 grep 無 service_role / 密鑰洩漏；git 全歷史無 `service_role`。✅
- **外連**：全部帶 `rel="noopener"`。無 `eval`/`new Function`。✅

### 待強化（非流血傷口）
- **CDN 無 SRI（Medium）**：`u.html`/`me.html` 從 jsdelivr 載 `@supabase/supabase-js@2`、`chart.js@4`，浮動版號且無 `integrity`。jsdelivr 若被入侵→登入頁被注入可竊 token。修法：釘完整版本號 + `integrity="sha384-..."` + `crossorigin="anonymous"`。
- **無 CSP（Low）**：GitHub Pages 不能設 header，可用 `<meta http-equiv>` 補一層。
- **`me.html` 內嵌 render 未跳脫（Low）**：只 render 自己資料（RLS 保護），self-XSS only。
- **postMessage 未驗 origin（Low）**：`me.html:870`，動作僅關彈窗，危害極小。
- **`js/me.js` 死程式碼**：只被 `me_ori.html`（舊備份）引用，正式 `me.html` 未載入。可清。

---

## 四、本次已修（DB，2026-07-02）

見 `supabase/add_handle_hardening.sql`。已在 Dashboard 執行並實測生效：

1. **handle 大小寫碰撞（Medium）**：原 `handle unique` 區分大小寫、查詢卻 `lower()` → `Danny`/`danny` 可並存並在公開頁互相混資料。已改：drop `profiles_handle_key`，建 `profiles_handle_lower_uidx on (lower(handle))`。
2. **handle 格式限制（Low）**：加 `handle_format` CHECK = `^[A-Za-z0-9_-]{1,30}$`，**刻意對齊前端 `me.html` 的 `norm()`**（允許 `-`、上限 30、無下限；保留字黑名單前端已有 `u/me/index/admin/api/app/www/...`）。

---

## 五、SEO / AI-search（現況良好）

- **SEO ~85/100**：三語 hreflang、canonical、sitemap、JSON-LD（WebApplication + Event ItemList）、**給爬蟲的 prerendered 劇目清單**（關鍵，否則 JS 地圖爬蟲全看不到）。
  - 待修：`sitemap.xml` 移掉 `me.html`（登入閘，爬蟲只看到「載入中」）；`u.html`/`me.html` 缺 canonical；遷網域時全站 domain 要改。
- **AI-search ~90/100**：`llms.txt` 完整、`robots.txt` 放行 GPTBot/ClaudeBot/PerplexityBot/OAI-SearchBot/Google-Extended。
- **共同缺口**：個人公開頁 `u.html` 純前端 render → 爬蟲/AI 抓不到內容。靠下面架構解。

---

## 六、themusicalmap.com 遷移 + `my.themusicalmap.com/<handle>` 架構建議

**技術現實**：GitHub Pages 一個 repo 只能綁一個自訂網域，且**不支援 server rewrite**（`/handle` → `u.html?u=handle` 做不到）。

**建議（用已在使用的 Cloudflare）**：
- 主站 `themusicalmap.com` / `www` → 維持 GitHub Pages。
- 個人頁 `my.themusicalmap.com/<handle>` → **Cloudflare Worker**：
  1. 把 `/<handle>` 內部 rewrite 到 `u.html`，handle 當參數傳入 → 乾淨網址成立。
  2. **順便解 SEO/AI 空白**：Worker 在回傳前幫爬蟲注入該人專屬 `<title>`/`og:title`/`og:image`/prerender 摘要（這正是 flightradar24 個人頁能被搜到的原因——它們不是純前端）。
- **handle 政策**：小寫正規化 + `lower(handle)` 唯一索引（已做）、字元 `[a-z0-9_-]`、保留字黑名單（前端已做，`my/www/api/admin` 等）。
- **傾向**：`my.<domain>/<handle>` 優於 `<domain>/u/<handle>`——網域層就分開個人空間與主站，未來快取/SEO/隱私策略更好切。

---

## 待辦清單（依優先序）

- [x] CDN 加 SRI（Medium）— **v1.10.2 完成**：`me.html`/`me-input.html`/`u.html` 的 supabase(2.110.0)/chart.js(4.5.1) + `gen_site.mjs` 模板的 leaflet(1.9.4)/markercluster(1.5.3)/opencc(1.3.1)，全部釘版號 + sha384 integrity + crossorigin；e2e 10 項驗證各頁 CDN 在 SRI 下正常載入。
- [x] `sitemap.xml` 移掉 `me.html` — **v1.10.2 完成**（改在 `gen_site.mjs` 產生器層移除，非手改產物）；`me.html` head 加 `noindex`。`u.html` canonical 留待 Worker 階段（query-param 型網址 canonical 需與 `my.` 形式一起定）。
- [x] 清 `js/me.js` 死程式碼 — **v1.10.2 完成**：`js/me.js` + `me_ori.html` 一併移除（git 歷史可找回）。
- [x] `my.themusicalmap.com` Cloudflare Worker — **v1.11.0 程式碼完成＋本機真測 14 項 PASS**（`worker/my-worker.js`；未部署，見 `docs/SETUP_MY_SUBDOMAIN.md`）
- [ ] 遷 themusicalmap.com 時全站 domain / sitemap / canonical 更新
- [ ] （Low，未做）meta CSP、postMessage origin 驗證、me.html 內嵌 render 補 esc
