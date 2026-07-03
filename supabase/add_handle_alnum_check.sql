-- handle 至少要有一個英文字母或數字(2026-07-03)
-- 原 add_handle_hardening.sql 的 CHECK 只驗字元集 '^[A-Za-z0-9_-]{1,30}$',
-- 導致只有連字號/底線的名稱(如 "---"、"___"、"-_-")能通過→變成 /u.html?u=--- 這種怪網址。
-- 前端已擋(me.html 三處 check),此處是 DB 層防繞過前端的防線。
-- 在 Supabase SQL editor 執行一次。可重複執行。

alter table public.profiles drop constraint if exists handle_format;
alter table public.profiles
  add constraint handle_format
  check (handle is null or handle ~ '^(?=.*[A-Za-z0-9])[A-Za-z0-9_-]{1,30}$');

-- 驗證(應回 true / false):
-- select 'abc' ~ '^(?=.*[A-Za-z0-9])[A-Za-z0-9_-]{1,30}$';   -- true
-- select '---' ~ '^(?=.*[A-Za-z0-9])[A-Za-z0-9_-]{1,30}$';   -- false
