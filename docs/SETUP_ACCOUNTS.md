# 帳號功能設定指南(Supabase + Google 登入)

> 一次性設定,約 10 分鐘。完成後把 **2 個值** 貼給我:`Project URL` 與 `anon public key`。
> anon key 是公開金鑰(放前端用),真正的保護靠資料庫的 Row Level Security,外洩無妨。

## A. 建 Supabase 專案
1. 到 https://supabase.com → 用 GitHub/Google 登入 → **New project**。
2. 填 Name(例 `musicalmap`)、設一組 DB 密碼(自己留存)、Region 選 `Northeast Asia (Tokyo)` 或 `Singapore`。
3. 等專案 build 好(~2 分鐘)。
4. 左下 **Project Settings → API**:
   - 複製 **Project URL**(形如 `https://xxxx.supabase.co`)
   - 複製 **Project API keys → `anon` `public`**(一長串)
   → 這兩個貼給我。

## B. 建資料表(套用 schema)
1. 左側 **SQL Editor → New query**。
2. 把 `supabase/schema.sql` 全部貼上 → **Run**。一次建好所有表 + 權限規則 + 種子。

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
