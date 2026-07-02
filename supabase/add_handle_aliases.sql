-- username 帳號身份化（docs/DESIGN_username_sharing.md 決策一實作）
-- 改名政策：舊 handle 永久保留給原主 + 轉向新名（Medium 模式）。
--   (1) handle_aliases：改名歷史。舊名永不釋放給別人 → 杜絕張冠李戴。
--   (2) rename_handle()：唯一合法的改名入口（onboarding 首次設定也走它）。
--       唯一性檢查 union「現用 handle + 所有人的 alias」——GitHub 翻車根因就是沒做這個。
--   (3) handle_available()：升級成 union 查重（含 alias、含保留字；排除自己）。
--   (4) resolve_handle()：舊名 → 現用名（u.html / Cloudflare Worker 轉向用；只回公開帳號）。
-- 在 Supabase SQL editor 執行一次。可重複執行（idempotent）。
-- 前置：schema.sql + add_share_privacy.sql + add_handle_hardening.sql 已套用。

-- 0) 保留字（DB 層與前端 RESERVED 對齊；Worker 之後也要用同一份）
--    集中成一個 function 讓 rename/available 共用，改清單只改這裡。
create or replace function public.handle_reserved(p text)
returns boolean language sql immutable set search_path = public as $$
  select lower(p) = any (array[
    'u','me','index','admin','api','app','www','my','null','undefined',
    'theatres','privacy','terms','login','logout','signup','settings',
    'account','stats','static','assets','js','css','data','posters','logos',
    'en','zh-hant','zh-hans','help','about','official','map','share'
  ]);
$$;

-- 1) 改名歷史表。RLS 開但「不建任何 policy」= 無人可直接讀寫，
--    一切讀取走下面的 SECURITY DEFINER RPC（改名歷史不可被枚舉，隱私）。
create table if not exists public.handle_aliases (
  old_handle text primary key,                       -- 一律小寫
  user_id    uuid not null references auth.users(id) on delete cascade,
  created_at timestamptz not null default now()
);
alter table public.handle_aliases enable row level security;

-- 2) 改名 / 首次設定（唯一合法入口；前端不再直接 upsert handle）
--    回傳 code：'ok' | 'not_authenticated' | 'bad_format' | 'reserved' | 'taken'
create or replace function public.rename_handle(p_new text)
returns text
language plpgsql security definer set search_path = public as $$
declare
  uid uuid := auth.uid();
  n   text := lower(trim(coalesce(p_new,'')));
  old text;
begin
  if uid is null then return 'not_authenticated'; end if;
  if n !~ '^[a-z0-9_-]{1,30}$' then return 'bad_format'; end if;
  if handle_reserved(n) then return 'reserved'; end if;

  select lower(handle) into old from profiles where id = uid;
  if old is not null and old = n then return 'ok'; end if;   -- 改成自己現名 = no-op

  -- 唯一性 union 檢查：他人現用 handle + 他人任何舊 alias
  if exists (select 1 from profiles where lower(handle) = n and id <> uid) then return 'taken'; end if;
  if exists (select 1 from handle_aliases where old_handle = n and user_id <> uid) then return 'taken'; end if;

  -- 舊名入 alias（永久保留給原主；重複改名累積多筆皆保留）
  if old is not null then
    insert into handle_aliases(old_handle, user_id) values (old, uid)
    on conflict (old_handle) do nothing;
  end if;
  -- 改回自己的舊名 → 從 alias 拿回（該名此後又是現用名）
  delete from handle_aliases where old_handle = n and user_id = uid;

  insert into profiles(id, handle) values (uid, n)
  on conflict (id) do update set handle = excluded.handle;
  return 'ok';
end $$;
grant execute on function public.rename_handle(text) to authenticated;

-- 3) 查重升級：union alias + 保留字；「自己的現名/自己的舊名」視為可用（改回去是合法的）
create or replace function public.handle_available(p_handle text)
returns boolean
language sql security definer set search_path = public stable as $$
  select not handle_reserved(p_handle)
     and not exists (select 1 from profiles
                     where lower(handle) = lower(p_handle)
                       and id is distinct from auth.uid())
     and not exists (select 1 from handle_aliases
                     where old_handle = lower(p_handle)
                       and user_id is distinct from auth.uid());
$$;
grant execute on function public.handle_available(text) to anon, authenticated;

-- 4) 舊名解析：舊 handle → 現用 handle（u.html 前端轉向 + 未來 Cloudflare Worker 301 用）
--    只回「公開」帳號——非公開使用者的改名軌跡不外洩。
create or replace function public.resolve_handle(p_handle text)
returns text
language sql security definer set search_path = public stable as $$
  select p.handle
  from handle_aliases a join profiles p on p.id = a.user_id
  where a.old_handle = lower(p_handle) and p.is_public
  limit 1;
$$;
grant execute on function public.resolve_handle(text) to anon, authenticated;

-- 驗證（跑完可貼）：
--   select proname, prosecdef, proconfig from pg_proc p join pg_namespace n on n.oid=p.pronamespace
--   where n.nspname='public' and proname in ('rename_handle','handle_available','resolve_handle','handle_reserved');
--   select rename_handle('__test_bad!');  -- 應回 bad_format（登入 session 下測）
