-- 修 display_name 洩漏 email 的 fallback(2026-07-03,使用者「你有存嗎」追問挖出)
-- 問題:handle_new_user() 在 Google 帳號無 full_name 時把「完整 email」寫進 profiles.display_name,
--      而 display_name 是公開頁標題 → 設公開後整個 email 被公開展示。
-- 修法:(1) fallback 改用 email 的 @ 前綴;(2) 既有 display_name 恰等於自己 email 的資料列一併修正。

-- (1) 觸發器 fallback:full_name → email @ 前綴(不再落完整 email)
create or replace function handle_new_user() returns trigger
language plpgsql security definer set search_path = public as $$
begin
  insert into public.profiles (id, display_name)
  values (new.id, coalesce(new.raw_user_meta_data->>'full_name', split_part(new.email, '@', 1)))
  on conflict (id) do nothing;
  return new;
end; $$;

-- (2) 一次性修正:display_name 恰好等於本人 email 的列(精準比對,不動使用者自訂含 @ 的名稱)
update public.profiles p
set display_name = split_part(u.email, '@', 1)
from auth.users u
where u.id = p.id and p.display_name = u.email;

-- 驗證:應回 0 列
-- select p.id from public.profiles p join auth.users u on u.id=p.id where p.display_name=u.email;
