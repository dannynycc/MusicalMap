# 設計:帳號身份 username + 公開分享網址（my.themusicalmap.com/<handle>）

> 狀態:**已定案、待實作**（2026-07-02 決策，含兩份 web 實證調查）。
> 參考對標:`my.flightradar24.com/Chiang`。
> 這份是實作依據——照這裡做，不要憑印象重新發明。

## 需求（使用者原話）

把 `xxxxxx` 從「分享面板裡隨手可改的暱稱」升級成**帳號的固定身份（username）**：
- 首次登入後建立一個個人帳號代號（走 Google OAuth，不用密碼）。
- 之後分享用 `my.themusicalmap.com/xxxxxx`。
- **不能**在「分享頁面」隨時改名（難管理）；要改是回「帳號設定」改，改完之後都有效。

---

## 決策一:改名後舊 username 怎麼處理 = **永久保留給原主 + 301 轉向**

### 實證（2026-07-02 web 調查，附官方來源）

業界分三類，不是二選一：

| 類型 | 平台 | 舊名處理 |
|---|---|---|
| 社群帳號 | X、Instagram、Discord、Linktree | 立即釋放回公共池、**無轉向**，舊連結直接斷 |
| 冷卻折衷 | Twitch（≥6月/Partner永久）、YouTube（14天雙URL）、GitHub | 短期保留；GitHub profile 頁甚至 **404 不轉向** |
| **個人頁/內容平台** | **Medium（自動永久301）、Substack（可選永久301）** | **舊名永久保留 + 永久轉向** |
| 極端 | Reddit | 根本不能改名 |

**關鍵洞見**：選「立即釋放」的平台是因為名稱池稀缺（幾億人搶短名）+ 身分靠 follow 關係不靠 URL。**本專案兩者都不是**：名稱池近乎無限（沒人搶），且個人頁 URL 會被外部分享/索引（斷連結 = 流量與 SEO 蒸發 + 張冠李戴風險）。成本結構與 **Medium/Substack 一致**，故採其做法。

### 定案

- username 可在「帳號設定」改名。
- 舊 handle **永久保留給原帳號**，不釋放給別人。
- 別人點舊 `my.../oldname` → **301 永久轉向**現用 handle。
- ⚠️ **唯一工程風險（GitHub 翻車根因）**：註冊新 handle 時，唯一性檢查必須**同時擋「現用 handle」和「所有歷史 alias」**，否則有人註冊到別人的舊 alias，永久 redirect 會撞車。

### 來源
- X: https://help.x.com/en/managing-your-account/change-x-handle
- Instagram: https://help.instagram.com/876876079327341
- GitHub: https://docs.github.com/en/account-and-profile/concepts/username-changes
- TikTok: https://support.tiktok.com/en/getting-started/setting-up-your-profile/changing-your-username
- Reddit: https://support.reddithelp.com/hc/en-us/articles/204579479
- Discord: https://support.discord.com/hc/en-us/articles/12620128861463
- Twitch: https://blog.twitch.tv/en/2017/01/06/username-rename-recycling-policy-update-882431cb966b/
- YouTube: https://support.google.com/youtube/answer/15920820
- Medium: https://help.medium.com/hc/en-us/articles/115004746707
- Substack: https://support.substack.com/hc/en-us/articles/360037460112

---

## 決策二:onboarding 設 username = **空白欄位 + 可用建議 chips（不預填真名）**

### 實證（2026-07-02 web 調查，附官方/UX 來源）

- **跟本專案最像的 link-in-bio（Linktree、Bio.link、Carrd）全部空白**讓使用者自己打，無人拿 Google 名字預填公開 slug。
- 有預填的 Medium/Substack 種子是 **email 前綴 / 刊物名**，不是 display name。
- **預填真名最糟**：把 Google 真名預設進「公開、可索引、永久」URL，踩中隱私 + default-effect（預設值採用率 ×3.5，多數人不改 → 靠慣性推使用者曝光真名；Google+ nymwars、Blizzard RealID 皆因強推真名翻車）。
- UX 權威一致反對 placeholder 當 label/預填（NN/g、Baymard、GOV.UK、W3C：消失、對比、報讀器、被誤認成已填值）。
- **最佳解 = 建議 chips**（Google 註冊、Instagram 實用）：欄位空、每顆建議預先驗證可用、要主動點才填。同時做到不自動塞值 + 消除撞名往返 + 不留空白恐懼。

### 定案

- onboarding username 欄位**空白**，label 在欄位上方（非 placeholder）。
- 底下一排 **2–4 顆「可用建議 chips」**，每顆先過 `handle_available` 驗證，**要主動點才填入**；種子用 **email 前綴**（`danny.chen@gmail`→`dannychen`）不是 display name。
- **不要**把 Google display name 當 `value` 預填。
- 保底（若不做 chips）：純空白 + 即時「可用/已占用」驗證（Linktree 路線）。

### 來源
- NN/g Defaults: https://www.nngroup.com/articles/the-power-of-defaults/
- NN/g Placeholders harmful: https://www.nngroup.com/articles/form-design-placeholders/
- Baymard input fields: https://baymard.com/learn/input-fields
- GOV.UK text input: https://design-system.service.gov.uk/components/text-input/
- W3C WAI forms: https://www.w3.org/WAI/tutorials/forms/instructions/
- EFF pseudonyms: https://www.eff.org/deeplinks/2011/07/case-pseudonyms
- Google 建議地址: https://support.google.com/accounts/answer/27441
- Linktree: https://linktr.ee/help/en/articles/5434134

---

## 資料模型

現況（已上線）：
- `profiles.handle`：唯一（`profiles_handle_lower_uidx on lower(handle)`）、格式 `^[A-Za-z0-9_-]{1,30}$`、前端 `norm()` 對齊。
- `profiles.is_public` / `show_price` / `show_seat`（隱私開關，預設關）。

新增：
```sql
-- handle 別名歷史：改名後舊 handle 永久解析到原 user，供 301 轉向
create table public.handle_aliases (
  old_handle text primary key,             -- 一律小寫存
  user_id    uuid not null references auth.users(id) on delete cascade,
  created_at timestamptz not null default now()
);
alter table public.handle_aliases enable row level security;
create policy handle_aliases_read on handle_aliases for select using (true);  -- 公開解析用；不含敏感欄
-- 寫入只由改名的 SECURITY DEFINER 函式處理，anon/user 無直接寫權。
```

改名流程（帳號設定觸發，建議寫成一個 `rename_handle(new_handle)` SECURITY DEFINER 函式）：
1. 驗 new_handle 格式 + 非保留字。
2. **唯一性 union 檢查**：`new_handle` 不得存在於 `profiles.handle`（他人）**或** `handle_aliases.old_handle`（任何人的舊名）。
3. 把目前的 `profiles.handle` 寫進 `handle_aliases`（若非 null）。
4. 更新 `profiles.handle = new_handle`。

`handle_available(p_handle)` 需**同步更新**：改成 union 檢查 profiles + handle_aliases。
保留字黑名單（前端已有，Worker/DB 也要有）：`my www api admin app u me index null undefined theatres privacy terms ...`。

---

## Cloudflare Worker（my. 子網域）

DNS：`my.themusicalmap.com` → Cloudflare（已管 DNS）。主站 `themusicalmap.com`/`www` 維持 GitHub Pages。

Worker 邏輯（`my.themusicalmap.com/<handle>`）：
1. 取 path 的 `<handle>`，小寫正規化。
2. 查 Supabase：先查 `profiles.handle`；查無再查 `handle_aliases.old_handle` → 命中則 **301 轉向** `my.themusicalmap.com/<現用handle>`。
3. 命中現用 handle → 內部 `fetch` GitHub Pages 的 `u.html`，回傳前**注入該人專屬 `<title>`/`og:title`/`og:image`/一段 prerender 摘要**（劇數/名字），解決個人頁純前端 render 爬蟲看不到的 SEO/AI 空白。真人瀏覽器照常跑前端 app（app 讀 `?u=`/path 取 handle）。
4. 查無 → 回 u.html 的 not-found 狀態（已存在 `#pub-empty`）。

保留字 / 靜態資源（logo、css、js）要在 Worker 放行，不要當 handle 解析。

---

## 前端改動清單（v1.10.0 已實作，e2e 23 項 PASS + u-view 回歸 6 項 PASS）

- [x] **帳號設定**入口（新）：`me.html` `#acctModal`，改 username（呼叫 `rename_handle`）+ display_name；成功提示「舊網址會自動轉到新網址」。
- [x] **分享面板**：handle 改**唯讀顯示** + 「到帳號設定改」連結；儲存只動公開開關/欄位隱私。
- [x] **onboarding**：空白欄位 + label 在上（無 placeholder）+ 建議 chips（種子=email 前綴、逐顆預驗可用、主動點才填）；**強制**（無 X、ESC/backdrop 關不掉，唯一出口=登出）。
- [x] 舊網址自動轉新：`u-view.js` 查無 handle 時走 `resolve_handle` → `location.replace` 到現用名（RPC 未部署則靜默降級 not-found）；順帶修訪客輸入大寫 `?u=Danny` 查不到的 bug。
- [x] migration 未套用的降級：`rename_handle` 不存在 → 前端自動退回舊 `upsert` 路徑（unique 約束保底）。
- [ ] 網址由 `?u=handle` → 支援 `my.themusicalmap.com/handle`（前端取 handle 邏輯相容兩者）——留待 Worker 階段。

## 實作順序與狀態

1. ✅ DB：`supabase/add_handle_aliases.sql`（handle_aliases + rename_handle + handle_available 升級 + resolve_handle）——**檔案已就緒，待使用者在 Supabase Dashboard 執行**。
2. ✅ 前端：帳號設定改名 + 分享面板唯讀 + onboarding chips + 強制設定（v1.10.0）。
3. [ ] Cloudflare Worker：rewrite + alias 301 + 爬蟲 meta 注入。
4. [ ] DNS 切 `my.` 子網域；u.html 支援 path handle。
5. [ ] 對照 [[project_musicalmap_domain_migration]]：themusicalmap.com 主站遷移一併規劃。

見 [[project_musicalmap_security]]（handle 唯一性/RLS 現況）、[[project_musicalmap_sharing]]。
