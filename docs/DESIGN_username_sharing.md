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

DNS：`my.themusicalmap.com` → Cloudflare（已管 DNS）。主站 `themusicalmap.com`/`www` 亦已於 2026-07-06（v2.4.0）遷至 Cloudflare Pages（GitHub Pages 留作熱備援）；Worker 回源同步改 `musicalmap.pages.dev`。

Worker 邏輯（`my.themusicalmap.com/<handle>`）：
1. 取 path 的 `<handle>`，小寫正規化。
2. 查 Supabase：先查 `profiles.handle`；查無再查 `handle_aliases.old_handle` → 命中則 **301 轉向** `my.themusicalmap.com/<現用handle>`。
3. 命中現用 handle → 內部 `fetch` GitHub Pages 的 `u.html`，回傳前**注入該人專屬 `<title>`/`og:title`/`og:image`/一段 prerender 摘要**（劇數/名字），解決個人頁純前端 render 爬蟲看不到的 SEO/AI 空白。真人瀏覽器照常跑前端 app（app 讀 `?u=`/path 取 handle）。
4. 查無 → 回 u.html 的 not-found 狀態（已存在 `#pub-empty`）。

保留字 / 靜態資源（logo、css、js）要在 Worker 放行，不要當 handle 解析。

---

## 多語化（2026-07-02 起,實證定案）

**語言必須進網址**:Google 官方明文建議每語言獨立 URL、反對 cookie/瀏覽器語言動態切換（Googlebot 不帶 Accept-Language、不留 cookie → 同 URL 只會被索引成預設語言）；有做個人頁多語+SEO 的 Strava（`?hl=`+28 hreflang）/X（`?lang=`+48 hreflang）/Last.fm（路徑式）零例外把語言放進 URL。本專案採 `?hl=` 參數式（Strava 模式）。

- ✅ **P1（v1.12.0）公開頁 u.html 繁中/英文**：`js/mm-strings.js` 字典＋`?hl=` 解析＋切換 pills；u-view runtime 全 `MM_T()`；en 模式地名/館名用資料原文；Worker 依 `?hl` 出 lang/title/meta＋hreflang 3 條＋canonical 各指自己；**u.html 移除 js/i18n.js**（其 applyStatic 同吃 data-i18n、會把本頁 key 蓋成字面值——兩套系統不可同頁共存）。e2e 19＋Worker 12 全 PASS。
- ✅ **P2（v1.13.0）me.html 繁中/英文**：mm-strings 擴充 me 專屬字典（登入閘/demo 橫幅/分享+帳號設定+onboarding 全訊息/徽章/persona/detail）；靜態 data-i18n + 4 個 script IIFE 動態 `MM_T()`；語言記在 localStorage `mm_lang`（與主站共用）；en 模式 countryZh/cityName/venueZh 回資料原文。e2e：繁中 onboarding 回歸 23 項 + 英文版 18 項全 PASS；截圖親驗。過程修：漏 `logout` key、`cityName`/FAB 漏接 EN_UI（截圖抓到城市仍中文）。
- ✅ **P3（v1.14.0）me-input.html 繁中/英文**：字典擴充 me-input 全 key（mi_/fld_/ph_/geo_/pick_/run_/recent_/added_ 等 ~70）；靜態掛 data-i18n（含 data-i18n-html 給含 `<br>`/`<b>` 的字串）；動態渲染模板（搜尋/手動表單/選製作/選城市/詳情/確認/toast/dateLabel EN_UI 分支/renderRecent）全 `MM_T()`；MON_ZH/yearOptions/月日 select 英文化；iframe 語言跟隨父頁 mm_lang。e2e 繁中回歸 + 英文版(含 embed 模式) + 手動表單零殘留全 PASS；截圖親驗。
- ✅ **P4（v1.15.0）zh-hans 簡體**：mm-strings 在 zh-hans 用 OpenCC(tw→cn) runtime 轉繁中字典（沿用主站機制）；OpenCC 只在偵測到 zh-hans 時 `document.write` 條件載入（繁中/英文使用者不下載）；localStorage 改讀 `mm_variant`（含簡繁，與主站精確共用）；u.html/me.html 加「简」pill；資料層地名/劇名譯名經 `MM_S`(OpenCC) 轉簡（u-view `mapped.zh` + countryZh/cityName/venueZh）；Worker 補 zh-hans title/desc/hreflang。e2e：u/me zh-hans 簡體正確 + 繁中/英文回歸 + 英文不下載 OpenCC + Worker zh-hans 全 PASS；截圖親驗簡繁差異。**足跡側多語化 P1–P4 全竣工。**
  - 已知小限制：me.html（登入者自己頁）的劇名中文譯名在簡體模式仍顯示繁體（資料為 MM.shows 共享，未逐處包 MS；u.html 公開頁已完整簡體）。海報圖內文字是圖片無法轉。

## 前端改動清單（v1.10.0 已實作，e2e 23 項 PASS + u-view 回歸 6 項 PASS）

> ⚠️ **v2.6.0（2026-07-07）版面整併**：帳號功能已集中到「帳號中心」——頁面頂部身分卡（公開/私密 pill＋專屬網址＋複製＋加入音樂劇/帳號設定/登出）＋統一帳號設定面板（`#acctModal` 擴充:帳號身分＋公開分享開關＋刪除帳號）。**舊「分享」modal 只剩 onboarding（首次強制取名）用途**；nav 分享/登出鈕移除。下列清單描述的是 v1.10.0 當時版面,機制（rename_handle/alias 301/onboarding chips）不變。e2e 34 項 PASS（2026-07-07）。

- [x] **帳號設定**入口（新）：`me.html` `#acctModal`，改 username（呼叫 `rename_handle`）+ display_name；成功提示「舊網址會自動轉到新網址」。（v2.6.0 起入口=身分卡「帳號設定」鈕）
- [x] **分享面板**：handle 改**唯讀顯示** + 「到帳號設定改」連結；儲存只動公開開關/欄位隱私。（v2.6.0 起公開開關/欄位隱私併入帳號設定面板）
- [x] **onboarding**：空白欄位 + label 在上（無 placeholder）+ 建議 chips（種子=email 前綴、逐顆預驗可用、主動點才填）；**強制**（無 X、ESC/backdrop 關不掉，唯一出口=登出）。
- [x] 舊網址自動轉新：`u-view.js` 查無 handle 時走 `resolve_handle` → `location.replace` 到現用名（RPC 未部署則靜默降級 not-found）；順帶修訪客輸入大寫 `?u=Danny` 查不到的 bug。
- [x] migration 未套用的降級：`rename_handle` 不存在 → 前端自動退回舊 `upsert` 路徑（unique 約束保底）。
- [x] 網址相容兩形式（v1.11.0）：`u-view.js` handle 來源＝`?u=` **或** `window.MM_HANDLE`（Worker 注入）。

## 實作順序與狀態

1. ✅ DB：`supabase/add_handle_aliases.sql` —— **2026-07-02 已套用＋全鏈路真人實測通過**：使用者實際改名 danny→danny_test→改回，(a) 舊網址 `?u=danny` 自動轉向新名 ✓ (b) 改回自己舊名合法 ✓ (c) alias `danny_test` 永久歸原主、`handle_available('danny_test')=false` 別人搶不走 ✓（線上 API 確認）。anon 面行為（保留字/查重/not_authenticated）亦全數線上驗證。**此機制無未實測環節。**
2. ✅ 前端：帳號設定改名 + 分享面板唯讀 + onboarding chips + 強制設定（v1.10.0）。
3. ✅ Cloudflare Worker **程式碼完成＋本機真測 14 項 PASS**（v1.11.0，`worker/my-worker.js`，打真 GH Pages＋真 Supabase：注入 MM_HANDLE/個人化 title/canonical/JSON-LD、不存在→404+noindex、靜態代理、保留字/尾斜線/robots）——**未部署**，步驟見 `docs/SETUP_MY_SUBDOMAIN.md`（需使用者 Cloudflare 帳號 wrangler login，約 10 分鐘）。alias→301 需等首次真實改名後才有資料可驗。
4. [ ] DNS 切 `my.` 子網域（`AAAA my 100::` 橘雲）＋ wrangler deploy——使用者執行。
5. [ ] 對照 [[project_musicalmap_domain_migration]]：themusicalmap.com 主站遷移一併規劃。

見 [[project_musicalmap_security]]（handle 唯一性/RLS 現況）、[[project_musicalmap_sharing]]。
