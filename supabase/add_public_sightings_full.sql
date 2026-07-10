-- 統一版 public_sightings(2026-07-10):同時回傳 rating + precision + fav。
--
-- 背景/為何需要:先前三份 migration(add_share_privacy / add_public_rating / add_fav)
-- 各自 drop+create public_sightings,彼此互斥——只有「最後執行的那份」生效。線上實測
-- (攔 /danny 的 RPC 回應)確認當前生效的是 add_fav 版:有 fav、但**缺 rating 與 precision**。
-- 後果(公開分享頁 js/u-view.js 消費這兩欄):
--   1) row.rating 不存在 → 每齣戲一律顯示 0 星(評分排序也失效)。
--   2) row.precision 不存在 → precisionOf(seen_date) 因 seen_date 是完整 date(YYYY-MM-DD)
--      永遠判成 'day' → 使用者「只記得年份」的舊劇(存成 YYYY-01-01)在公開頁被**捏造**成
--      精確的 1 月 1 日(海報卡日期、護照戳章、詳情頁全中招)。
--
-- 這份把三欄一次補齊,取代所有舊定義。在 Supabase SQL editor 執行一次,idempotent。

-- 欄位存在性保險(可能已由舊 migration 建過)
alter table public.sightings add column if not exists rating    smallint default 0;
alter table public.sightings add column if not exists precision text;
alter table public.sightings add column if not exists fav       boolean not null default false;

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
  precision      text,
  seat           text,
  price          numeric,
  currency       text,
  url            text,
  links          jsonb,
  poster_override text,
  production_key text,
  rating         smallint,
  fav            boolean
)
language sql security definer set search_path = public stable as $$
  select
    s.id, s.title, s.venue, s.city, s.country,
    s.lat, s.lng, s.seen_date, s.precision,
    case when p.show_seat  then s.seat     else null end,
    case when p.show_price then s.price    else null end,
    case when p.show_price then s.currency else null end,
    s.url, s.links, s.poster_override, s.production_key,
    s.rating, s.fav
  from sightings s
  join profiles p on p.id = s.user_id
  where lower(p.handle) = lower(p_handle) and p.is_public
  order by s.seen_date desc nulls last;
$$;
grant execute on function public.public_sightings(text) to anon, authenticated;

-- 驗證:select id, rating, precision, fav from public.public_sightings('danny') limit 3;
