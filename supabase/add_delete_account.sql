-- 自助刪除帳號(GDPR 被遺忘權;2026-07-03)
-- 使用者可從「帳號設定 → 危險操作 → 刪除我的帳號」永久刪除自己的帳號與所有資料。
-- 在 Supabase SQL editor 執行一次。可重複執行(idempotent)。
--
-- 資安:SECURITY DEFINER 但只刪「呼叫者本人」(auth.uid())的資料,不能刪別人;
--   只授權 authenticated 執行。sightings/profiles/handle_aliases 有 on delete cascade,
--   但明確刪一次當保險;venues.created_by 無 cascade → 設 null(保留社群貢獻的劇院,只解除作者連結)。

create or replace function public.delete_my_account()
returns void
language plpgsql
security definer
set search_path = public, auth
as $$
declare uid uuid := auth.uid();
begin
  if uid is null then
    raise exception 'not authenticated';
  end if;

  delete from public.sightings where user_id = uid;

  if to_regclass('public.handle_aliases') is not null then
    delete from public.handle_aliases where user_id = uid;
  end if;

  -- 眾包劇院表:無 cascade,不刪劇院(別人也在用)只解除作者連結,否則刪 auth.users 會被 FK 擋
  update public.venues set created_by = null where created_by = uid;

  delete from public.profiles where id = uid;

  -- 最後刪 auth.users(級聯清乾淨剩餘的帳號資料);SECURITY DEFINER owner 有此權限
  delete from auth.users where id = uid;
end;
$$;

revoke all on function public.delete_my_account() from public, anon;
grant execute on function public.delete_my_account() to authenticated;

-- 驗證:select proname from pg_proc where proname = 'delete_my_account';  應存在一列
