-- 「標最愛 ♥」功能(2026-07-03):sightings 加 fav 欄 + 公開讀取函式帶出 fav
-- 在 Supabase SQL editor 執行一次,可重複執行(idempotent)。

-- 1) fav 欄位(預設 false,不動既有資料)
alter table public.sightings add column if not exists fav boolean not null default false;

-- 2) 重建 public_sightings:沿用 add_share_privacy.sql 的遮罩邏輯,回傳欄位追加 fav
--    (fav 非敏感欄位,公開頁直接顯示 ♥)
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
  production_key text,
  fav            boolean
)
language sql security definer set search_path = public stable as $$
  select
    s.id, s.title, s.venue, s.city, s.country,
    s.lat, s.lng, s.seen_date,
    case when p.show_seat  then s.seat     else null end,
    case when p.show_price then s.price    else null end,
    case when p.show_price then s.currency else null end,
    s.url, s.links, s.poster_override, s.production_key,
    s.fav
  from sightings s
  join profiles p on p.id = s.user_id
  where lower(p.handle) = lower(p_handle) and p.is_public
  order by s.seen_date desc nulls last;
$$;
grant execute on function public.public_sightings(text) to anon, authenticated;

-- 驗證:select proname from pg_proc where proname='public_sightings';  應存在
