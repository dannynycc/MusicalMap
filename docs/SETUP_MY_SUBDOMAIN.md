# 部署 my.themusicalmap.com（個人公開頁子網域）

> 狀態:**✅ 2026-07-06 已部署上線**（wrangler `custom_domain=true` 自動建 DNS+憑證,版本 4d807b44）。線上驗證過:`/danny` 200+MM_HANDLE 注入+個人化 title/canonical、舊名 301、不存在 404、根 302 回主站、css 代理 200、瀏覽器完整 render。
> 前置:themusicalmap.com 已在 Cloudflare 管 DNS（已完成）；`add_handle_aliases.sql` 已套用（已完成）。
> 設計依據:`docs/DESIGN_username_sharing.md`。

## 這個 Worker 做什麼

> 回源更新（2026-07-06 v2.4.0 託管遷移）：Worker 的 `GH_ORIGIN` 已改指 **Cloudflare Pages（musicalmap.pages.dev）**，下表「回源」皆指它（原 GitHub Pages 僅留作熱備援）。根路徑行為 v2.2.0 起改 FR24 模式。

| 訪問 | 行為 |
|---|---|
| `my.themusicalmap.com/danny` | 內部取回源的 `u.html`，注入 `window.MM_HANDLE='danny'` + 該使用者專屬 `<title>`/og/canonical/JSON-LD 後回傳 → 乾淨網址 + 爬蟲/AI 看得到內容；本人（`mm_owner` cookie 相符）同網址直接出編輯版 `me.html`（FR24 模式，v2.2.0） |
| `my.../danny2`（danny 的舊名） | 查 `resolve_handle` → **301** 到 `my.../danny`（舊分享連結永久有效） |
| `my.../不存在的名字` | 回 `u.html` 的 not-found 空狀態，HTTP **404** + noindex |
| `my.../css/...`、`/js/...`、任何含 `.` 或 `/` 的路徑 | 代理回源靜態資源（u.html 的相對路徑因此正常；cache-control 壓回 600s） |
| `my.../`（根） | 直接出 `me.html` app shell（登入閘，no-store；v2.2.0 起不再 302 主站） |
| 保留字（u/me/admin…） | 302 回主站 |
| `my.../robots.txt` | Worker 自己回 allow-all |

前端配合已上線（v1.11.0）:`u-view.js` 的 handle 來源是 `?u=` **或** `window.MM_HANDLE`，兩種形式並存。

## 部署步驟（需要你的 Cloudflare 帳號，約 10 分鐘）

1. **裝 wrangler 並登入**（第一次才要）:
   ```
   cd D:/ClaudeCode/MusicalMap/worker
   npx wrangler login        # 開瀏覽器授權你的 Cloudflare 帳號
   ```
2. **部署**:
   ```
   npx wrangler deploy
   ```
   `wrangler.toml` 已把 route 綁到 `my.themusicalmap.com/*`（zone: themusicalmap.com）。
3. **DNS**:Cloudflare DNS 加一筆 `my` 的記錄讓 route 生效——
   - Type `AAAA`、Name `my`、Content `100::`、**Proxy 開啟（橘雲）**
   -（`100::` 是佔位 IP；流量到橘雲就被 Worker route 攔走，不會真的連那個 IP。這是 Cloudflare Workers 綁自訂網域的標準做法。）
4. **驗證**（部署後跑）:
   - `curl -s https://my.themusicalmap.com/danny | grep MM_HANDLE` → 應看到 `window.MM_HANDLE="danny"`
   - `curl -s https://my.themusicalmap.com/danny | grep '<title>'` → 應含顯示名稱
   - `curl -sI https://my.themusicalmap.com/<某個舊名>` → `301` + `location: /現用名`
   - `curl -sI https://my.themusicalmap.com/沒這人xyz` → `404`
   - 瀏覽器開 `my.themusicalmap.com/danny` → 頁面完整 render（海報牆/地圖/統計）

## 之後的收尾（主站遷移時一起）

- [x] `GH_ORIGIN` 改成 `https://themusicalmap.com`（2026-07-06 主站遷移時完成）
- [x] 分享按鈕/複製連結改產 `my.themusicalmap.com/<handle>` 形式（2026-07-06,`me.html` `shareUrl()`+兩處 prefix 標籤）
- [x] `u.html?u=` 舊形式加轉向到 `my.` 形式（2026-07-06,u.html head 早期 script;僅主網域觸發、帶 `?hl=`、localhost 不轉方便本機測試）
- [ ] og:image 個人化（用該使用者第一張海報；需再打一次 `public_sightings`，目前用品牌 logo）
- [ ] **Google 登入品牌化（OAuth callback 代理）**：用同一個 Cloudflare Worker 把 `auth.themusicalmap.com/auth/v1/callback` 反向代理到 Supabase 的 `gtuvrhdvwjlvneispcuq.supabase.co/auth/v1/callback`，並把 Supabase Auth 的 redirect / Google OAuth client 的 authorized redirect URI 改成 `auth.themusicalmap.com`。這樣 Google 同意畫面顯示的網域就變成自家網域，走品牌驗證時也沒有「無法驗證 supabase.co」的卡點。詳見 `SETUP_ACCOUNTS.md` 的「Google 登入品牌顯示」段。

## 資安備註

Worker 內只有公開 anon key（RLS 把關）與公開資料查詢，無任何 secret，程式碼可放公開 repo。
保留字清單三處同步:DB `handle_reserved()`、`me.html` RESERVED、`worker/my-worker.js` RESERVED——改任何一處要三處一起。
