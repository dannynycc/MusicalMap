-- Defense-in-depth: enforce the handle reserved-word ban directly on the profiles
-- table (2026-07-15), so handle integrity no longer depends SOLELY on the
-- "handle_new_user auto-creates the row → PK conflict → DELETE revoked" invariant.
--
-- Background (all probed against the live DB before writing this):
--   * `handle` is nullable; new signups get handle = NULL — the `handle_new_user`
--     trigger inserts (id, display_name, ...) and NEVER references `handle`
--     (verified: prosrc ~* 'handle' = false). The handle is set later during
--     onboarding via the SECURITY DEFINER `rename_handle` RPC.
--   * `rename_handle` already rejects reserved words / alias collisions / bad format;
--     table-level UPDATE(handle) and DELETE are revoked, so rename_handle is the only
--     path that sets a non-null handle today.
--   * The residual gap: table INSERT is granted (needed for the display_name upsert),
--     and the only DB guard on an inserted handle was the loose `handle_format` CHECK
--     (^[A-Za-z0-9_-]{1,30}$) + the unique index on lower(handle). Neither enforces the
--     reserved list. So a session with NO profile row could in theory POST
--     /rest/v1/profiles {id:<own uid>, handle:'admin'} and claim a reserved word,
--     bypassing rename_handle. (Currently blocked only because every auth user already
--     has a row → PK conflict, and DELETE is revoked so the row can't be cleared first.)
--
-- This guard closes that class permanently. It reuses the SAME `handle_reserved(text)`
-- function rename_handle uses (IMMUTABLE, lowercases internally) so the rule is
-- identical — a legit rename that rename_handle allows can never be blocked here.
--
-- Verified on production immediately after applying (three INSERTs with an existing
-- uid, all fail naturally → zero writes):
--   A) handle='admin'            -> "handle admin is reserved"          (attack blocked)
--   B) handle=NULL               -> duplicate key on profiles_pkey      (signup path untouched)
--   C) handle='danny_guard_test' -> duplicate key on profiles_pkey      (legit rename untouched)
--
-- Format-level rules (all-numeric ban, edge/consecutive symbols) are intentionally NOT
-- duplicated here: replicating rename_handle's exact regex risks blocking a legit rename
-- on any mismatch, and those cases are low-value (bounded by the existing handle_format
-- CHECK and not name-takeovers). Reserved-word is the meaningful attack, and it is closed.

create or replace function public.profiles_handle_guard()
returns trigger language plpgsql as $g$
begin
  if new.handle is not null
     and (tg_op = 'INSERT' or new.handle is distinct from old.handle)
     and public.handle_reserved(new.handle) then
    raise exception 'handle % is reserved', new.handle using errcode = '23514';
  end if;
  return new;
end;
$g$;

drop trigger if exists profiles_handle_guard_trg on public.profiles;
create trigger profiles_handle_guard_trg
  before insert or update of handle on public.profiles
  for each row execute function public.profiles_handle_guard();
