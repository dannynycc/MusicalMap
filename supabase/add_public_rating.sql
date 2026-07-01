-- 公開頁改版對齊 me.html：public_sightings 多回傳 rating（星星）與 precision（日期精度）。
-- 兩者皆非敏感（評分/日期粒度），公開沒問題。座位/票價仍受 show_seat/show_price 開關遮罩、note 仍不回。
-- 在 Supabase SQL editor 執行一次。可重複執行（create or replace）。

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
  rating         smallint,
  "precision"    text
)
language sql security definer set search_path = public stable as $$
  select
    s.id, s.title, s.venue, s.city, s.country,
    s.lat, s.lng, s.seen_date,
    case when p.show_seat  then s.seat     else null end,
    case when p.show_price then s.price    else null end,
    case when p.show_price then s.currency else null end,
    s.url, s.links, s.poster_override, s.production_key,
    s.rating, s.precision
  from sightings s
  join profiles p on p.id = s.user_id
  where lower(p.handle) = lower(p_handle) and p.is_public
  order by s.seen_date desc nulls last;
$$;
grant execute on function public.public_sightings(text) to anon, authenticated;
