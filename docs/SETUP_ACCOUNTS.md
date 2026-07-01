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
