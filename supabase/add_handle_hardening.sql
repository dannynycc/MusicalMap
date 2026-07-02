-- handle 強化：修掉大小寫碰撞 + 加格式限制（2026-07-02 資安健檢）
-- 目的：
--   (1) 原本 handle 唯一約束「區分大小寫」，但所有查詢（public_sightings/handle_available）
--       用 lower() 比對 → Danny 與 danny 可同時註冊成功，訪問公開頁時 where lower(handle)=...
--       會 JOIN 到兩個 profile，把兩位陌生使用者的 sightings 混在同一頁輸出（隱私交叉污染）。
--   (2) handle 即將成為 my.themusicalmap.com/<handle> 網址的一部分，需擋掉會破壞路由/前端的字元。
-- 已在 Supabase Dashboard SQL editor 執行並實測生效。可重複執行（idempotent）。
-- 前置：schema.sql（profiles 建表）需已存在。

begin;

-- 1) 拔掉區分大小寫的舊唯一約束（handle text unique 自動建的）
alter table public.profiles drop constraint if exists profiles_handle_key;

-- 2) 換成「不分大小寫」的唯一索引 → Danny 與 danny 不能並存，消除混頁
create unique index if not exists profiles_handle_lower_uidx
  on public.profiles (lower(handle));

-- 3) 格式限制：刻意對齊前端 me.html 的 norm() 現行規則
--    （norm = trim → lowercase → replace /[^a-z0-9_-]/ → slice(0,30)）
--    允許連字號、保留原始大小寫（唯一性已由 lower 索引保證，不影響防碰撞）、
--    上限 30、下限 1（對齊前端無下限，避免前端放行卻在 DB 神秘存檔失敗）。
--    若日後要「下限 3」政策，前端 checkHandle + 這裡的 {1,30} 要一起改成 {3,30}。
alter table public.profiles
  add constraint handle_format
  check (handle is null or handle ~ '^[A-Za-z0-9_-]{1,30}$');

commit;

-- 驗證（實測結果 2026-07-02）：
--   select indexname, indexdef from pg_indexes where tablename='profiles';
--   → profiles_handle_lower_uidx ... USING btree (lower(handle))  ✓
--   → 舊 profiles_handle_key 已消失  ✓
