# 帳號功能設定指南(Supabase + Google 登入)

> 一次性設定,約 10 分鐘。完成後把 **2 個值** 貼給我:`Project URL` 與 `anon public key`。
> anon key 是公開金鑰(放前端用),真正的保護靠資料庫的 Row Level Security,外洩無妨。

## A. 建 Supabase 專案
1. 到 https://supabase.com → **用 GitHub 登入**(後台註冊只有 GitHub / Email,沒有 Google;用 GitHub 與你的 repo 同身分最一致）→ **New project**。
2. 填 Name(例 `musicalmap`)、設一組 DB 密碼(自己留存)、Region 選 `Northeast Asia (Tokyo)` 或 `Singapore`。
3. 等專案 build 好(~2 分鐘)。
4. 左下 **Project Settings → API**:
   - 複製 **Project URL**(形如 `https://xxxx.supabase.co`)
   - 複製 **Project API keys → `anon` `public`**(一長串)
   → 這兩個貼給我。

## B. 建資料表(套用 schema)
1. 左側 **SQL Editor → New query**。
2. 把 `supabase/schema.sql` 全部貼上 → **Run**。一次建好所有表 + 權限規則 + 種子。
3. 後續加欄位的 migration(既有資料庫補跑即可,皆 `add column if not exists`,可重複執行):
   - `supabase/add_url.sql` —— 每筆紀錄的連結(`url` / `links`)。
   - `supabase/add_production.sql` —— **版本層**(`production_key` / `poster_override`);沒跑的話版本/自訂海報選了不會被存下來(App 本身會優雅降級不報錯)。
   - `supabase/add_rating_precision.sql` —— **v0.79.0 (My Musicals v2 改版) 必跑**：`rating`(0–5 星)+ `precision`(日期精度 year/month/day)；新版 me.html 的星星評分與年/月/日統計需要。
   - `supabase/add_poster_override.sql` —— **v1.1.0 自訂海報必跑**：`poster_override`(每筆紀錄可填圖片 URL 覆蓋系統海報；清空還原)；沒跑的話自訂海報存不下來(App 會優雅降級不報錯)。（與舊 `add_production.sql` 的同名欄等效；v2 用這支獨立的、不含已棄用的 `production_key`。）
   - `supabase/add_share_privacy.sql` —— **v1.4.0 公開分享頁必跑**：profiles 加全域欄位隱私開關(`show_price` / `show_seat`，預設關)；**收緊 RLS**(sightings 公開讀取不再讓 anon 直接讀他人整列)；新增 `public_sightings(handle)` SECURITY DEFINER 遮罩函式(依開關決定 price/seat 是否回傳、note 一律不回)與 `handle_available(handle)` 查重函式。**沒跑的話公開頁 `u.html` 讀不到資料**(`js/u-view.js` 改讀此函式;v1.6.0 前為舊 `js/u.js`)。⚠️ 此 SQL 與新版前端必須**同時上線**(RLS 一收緊，舊版直接 `select("*")` 就會失效)。
   - `supabase/add_public_rating.sql` —— **v1.6.0 選跑**：`public_sightings` 多回傳 `rating`(星星)/`precision`(日期精度)，讓改版後的公開頁 `u.html` 顯示星星評分與正確日期粒度。皆非敏感;不跑也能運作(u-view.js 防禦式處理，只是星星不顯示、年精度日期顯示成完整日期)。
   - `supabase/add_handle_hardening.sql` —— **v1.9.7 資安健檢**：修 handle 大小寫碰撞(建 `profiles_handle_lower_uidx on lower(handle)`,取代區分大小寫的舊唯一約束 → `Danny`/`danny` 不再並存混頁)+ 加 `handle_format` CHECK(`^[A-Za-z0-9_-]{1,30}$`,對齊前端 `norm()`)。可重複執行。
   - `supabase/add_handle_aliases.sql` —— **v1.10.0 username 帳號身份化必跑**：`handle_aliases` 改名歷史表(舊名永久保留給原主)+ `rename_handle`(改名唯一入口,union 查重防撞車)+ `handle_available` 升級(含 alias/保留字)+ `resolve_handle`(舊網址→現用名,u.html 自動轉向)。**沒跑的話**:onboarding/改名自動退回舊 upsert 路徑(unique 約束保底,功能可用),但改名**不會**留 301 轉向、舊網址直接失效。可重複執行。
   - `supabase/fix_display_name_email_leak.sql` —— **display_name 不再落完整 email**：修 `handle_new_user()` 觸發器改用 `coalesce(full_name, split_part(email,'@',1))`,並一次性把既有落了 email 的 display_name 補成 @ 前綴。公開頁顯示名不再外洩 email。已套用 ✓。
   - `supabase/add_fav.sql` —— **v1.26.0 ♥最愛功能必跑**：`sightings` 加 `fav` 欄 + `public_sightings` 重建帶出 fav。沒跑的話海報卡點 ♥ 存不進雲端(其他功能不受影響)。已套用 ✓。
   - `supabase/add_delete_account.sql` —— **v1.30.0 刪除帳號(GDPR 被遺忘權)必跑**：`delete_my_account()` SECURITY DEFINER RPC,只刪呼叫者本人(auth.uid())的 sightings/profile/handle_aliases(cascade)+ venues.created_by 設 null(保留社群劇院)+ auth.users。沒跑的話「帳號設定→刪除我的帳號」會顯示刪除失敗。已套用 ✓。
   - `supabase/add_handle_alnum_check.sql` —— **v1.31.2 防繞過前端**：把 `handle_format` CHECK 收緊為 `^(?=.*[A-Za-z0-9])[A-Za-z0-9_-]{1,30}$`(至少一個字母數字),擋「---」類只有連字號/底線的名稱。前端已擋,此為 DB 防線。已套用 ✓。

## C. 開 Google 登入
1. **Authentication → Sign In / Providers → Google → Enable**。
2. 它會要 `Client ID` 和 `Client Secret`,需到 Google Cloud 拿:
   - https://console.cloud.google.com → 建/選一個專案 → **APIs & Services → Credentials → Create Credentials → OAuth client ID**。
   - Application type:**Web application**。
   - **Authorized JavaScript origins** 加:
     - `https://dannynycc.github.io`
     - `http://localhost:8753`(本機測試)
   - **Authorized redirect URIs** 加 Supabase 給你的那條(Google provider 頁面上會顯示,形如 `https://xxxx.supabase.co/auth/v1/callback`)。
   - 建立後複製 **Client ID / Client Secret** 貼回 Supabase 的 Google provider。
3. (OAuth consent screen 若要求)填 App name、support email,測試階段把你自己的 Gmail 加進 Test users 即可。

## D. 設定授權網域(Supabase 端)
- **Authentication → URL Configuration**:
  - **Site URL**:`https://dannynycc.github.io/MusicalMap/`
  - **Redirect URLs** 加:`https://dannynycc.github.io/MusicalMap/me.html` 與 `http://localhost:8753/me.html`

## 完成
把 A‑4 的兩個值貼我,我接上 `js/config.js`。在那之前我已把整套前端(登入、記錄表單、圖表、我的地圖)寫好,接上即可用。

---

## Google 登入品牌顯示（同意畫面顯示 supabase.co 的問題）

**現象**：點「用 Google 登入」時,Google 畫面顯示「登入 `gtuvrhdvwjlvneispcuq.supabase.co`」「繼續使用 …supabase.co」,看起來像詐騙。

**確定原因（2026-07-02 web 查證,官方雙方確認）**：
- Google 官方（support.google.com/cloud/answer/15549049）：**App 未通過「品牌驗證（brand verification）」前,同意畫面只顯示「應用程式網域」（從 OAuth redirect_uri 推導）,不顯示 App name / logo。**「登入 X」與「繼續使用 X」同源。
- Supabase 免費版 redirect = `xxx.supabase.co/auth/v1/callback` → 推導網域 = `supabase.co`。Supabase 官方（discussion #2532）自認免費版「該網域無法更改」,issue #33387 標為純外觀 external issue。
- ⚠️ **只填 App name 不會生效** —— 必須「品牌驗證 + 切 In production + 發佈品牌」,name/logo 才顯示。這是「設了 App name 仍顯示 domain」的真正原因。

**三種根治法（依成本）**：
| 方法 | 成本 | 說明 |
|---|---|---|
| A. Google 品牌驗證 | 免費,等數天~數週 | Search Console 驗證**自家網域** + 加進 authorized domains + In production + 送品牌驗證。卡點:`supabase.co` 你不擁有無法驗證 → 回覆 Google 驗證信說明「是第三方 redirect」才過（社群經驗,非官方條文,不保證一次過） |
| B. Supabase Pro Custom Domain | **$10/月** | 開 Pro,auth 端點換成 `auth.themusicalmap.com`,Google 畫面直接顯示自家網域,品牌驗證也變乾淨。官方 docs: platform/custom-domains |
| **C. Cloudflare Worker 代理（推薦,免費根治）** | 免費,寫一點 code | 用 `my.` 那套 Worker 把 `auth.themusicalmap.com/auth/v1/callback` 代理到 Supabase callback,redirect_uri 落自家網域 → 品牌驗證無卡點。見 `SETUP_MY_SUBDOMAIN.md` 收尾清單 |

**建議**：**跟主站遷移 themusicalmap.com 綁在一起用方法 C 做**（免費,且和 `my.` 子網域 Worker 同一套）。現網站還在 github.io、themusicalmap.com 未上線,A/C 都需自家網域,現在單獨處理會卡死。**現階段 supabase.co 顯示功能完全正常,純外觀,先接受,遷網域時一次解決。**

（App name = `MusicalMap`、logo〔120×120 正方形〕、隱私 `privacy.html` / 條款 `terms.html` 連結該填的先填好,遷網域走品牌驗證時就緒即可。）
