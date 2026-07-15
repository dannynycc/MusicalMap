-- 2026-07-15 安全修補(實測確認的漏洞,見 CHANGELOG v2.44.3)
-- 背景:profiles_write / venues_insert 只驗 id/角色,未收欄位級權限,導致:
--   1) 任何登入者可直接 PATCH profiles.handle 繞過 rename_handle RPC 的
--      保留字 / 舊名 alias 查重 / 嚴格格式三道檢查(實測:danny 直寫 handle='admin' 成功)
--      → 可註冊保留名冒充、劫持他人退役 handle 的分享連結(流量劫持/冒名)。
--   2) venues INSERT with check(true) 未驗 created_by,可把劇院掛在他人名下(歸屬污染)。
-- 修法:handle 只准走 rename_handle(SECURITY DEFINER,不受下列 revoke 影響);
--       venues 收 created_by=本人。RLS policy 不動(隔離仍靠它),這裡補「欄位級 grant」與「INSERT check」。

-- ── 1) handle 鎖寫 ──────────────────────────────────────────────────
-- 注意:column-level `revoke update(handle)` 對已持有「table-level UPDATE」的角色無效
--       (2026-07-15 實測:revoke column 後 danny 仍能直寫 handle='admin')。
--       正解=收回整表 UPDATE,再精確授回「非 handle」欄位。
-- rename_handle 是 SECURITY DEFINER(以擁有者權限跑內部 update)→ 正常改名不受影響。
revoke update on public.profiles from authenticated, anon;
grant update(is_public, show_price, show_seat, display_name) on public.profiles to authenticated;
-- handle / id / created_at 不在授權清單 → 只能走 rename_handle RPC,不可直寫竄改。

-- ── 2) venues 歸屬 ──────────────────────────────────────────────────
drop policy if exists venues_insert on public.venues;
create policy venues_insert on public.venues for insert to authenticated
  with check (created_by = auth.uid() or created_by is null);

-- 驗證(在 SQL editor 執行後可跑):以下應各自回 permission denied / RLS 擋下
--   update public.profiles set handle='admin' where id=auth.uid();   -- 期望:permission denied for column handle
