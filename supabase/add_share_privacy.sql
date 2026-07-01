-- me-v2 分享隱私：全域欄位開關 + 安全的公開讀取 + handle 查重
-- 目的：
--   (1) 公開分享頁不再讓 anon key 直接讀別人整列 sightings（原本 price/seat/note 全外洩）。
--   (2) 使用者用「全域欄位開關」決定公開頁要不要露出票價 / 座位。
--   (3) 取 username 時能繞過 RLS 正確查重（RLS 會藏私密帳號 → 普通 SELECT 會誤判可用）。
-- 在 Supabase SQL editor 執行一次。可重複執行（idempotent）。

-- 0) 補齊線上缺的欄位（先前 migration 未全套用）：links / production_key
--    （公開頁的多連結與版本海報需要；不動既有資料）
alter table public.sightings add column if not exists links jsonb;
alter table public.sightings add column if not exists production_key text;

-- 1) profiles：全域欄位隱私開關（預設票價關、座位關 → 最保守，公開也不會意外露出）
alter table public.profiles add column if not exists show_price boolean not null default false;
alter table public.profiles add column if not exists show_seat  boolean not null default false;

-- 2) 收緊 sightings 公開讀取：移除「公開帳號整列皆可讀」分支。
--    anon / 其他人一律只能讀自己的；別人的公開資料改走下面遮罩函式。
--    （擁有者本人在 me.html 用登入 session 讀自己的 → user_id = auth.uid() 仍成立，不受影響）
drop policy if exists sightings_read on sightings;
create policy sightings_read on sightings for select
  using (user_id = auth.uid());

-- 3) 公開讀取函式：依 handle 找「公開」帳號，回傳「遮罩後」的 sightings。
--    SECURITY DEFINER 會繞過 RLS，但：
--      • 只回 is_public = true 的帳號（非公開 → 0 筆）
--      • price / currency 只有 show_price 時才給，否則 null
--      • seat        只有 show_seat  時才給，否則 null
--      • note 完全不回傳（公開頁本來就不顯示筆記 → 永遠私密）
--    回傳欄位僅限 u.js 實際會用到的，減少 payload 也減少誤露面。
drop function if exists public.public_sightings(text);
create function public.public_sightings(p_handle text)
returns table (
  id             bigint,
  title          text,
  venue          text,
  city           text,
  country        text,
  lat            double precision,
  lng            double precision,
  seen_date      date,
  seat           text,
  price          numeric,
  currency       text,
  url            text,
  links          jsonb,
  poster_override text,
  production_key text
)
language sql security definer set search_path = public stable as $$
  select
    s.id, s.title, s.venue, s.city, s.country,
    s.lat, s.lng, s.seen_date,
    case when p.show_seat  then s.seat     else null end,
    case when p.show_price then s.price    else null end,
    case when p.show_price then s.currency else null end,
    s.url, s.links, s.poster_override, s.production_key
  from sightings s
  join profiles p on p.id = s.user_id
  where lower(p.handle) = lower(p_handle) and p.is_public
  order by s.seen_date desc nulls last;
$$;
grant execute on function public.public_sightings(text) to anon, authenticated;

-- 4) handle 查重：繞過 RLS 檢查 handle 是否可用（只回 boolean，不洩漏擁有者是誰）。
--    handle 一律以小寫儲存（前端 saveShare 已正規化），故用 lower() 比對大小寫不敏感。
drop function if exists public.handle_available(text);
create function public.handle_available(p_handle text)
returns boolean
language sql security definer set search_path = public stable as $$
  select not exists (select 1 from profiles where lower(handle) = lower(p_handle));
$$;
grant execute on function public.handle_available(text) to anon, authenticated;
