-- me-v2 方法2：每筆紀錄可自訂海報網址（per-sighting poster override）。
-- 使用者在某齣紀錄填一個圖片 URL，覆蓋系統 catalog 帶出來的海報；清空即還原系統圖。
-- 各筆獨立（per-row 欄位）。純新增、不動既有資料、可回復（drop column 即還原）。
-- 渲染順序：poster_override → catalog 海報 → 首字母色塊。
alter table public.sightings add column if not exists poster_override text;
