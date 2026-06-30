-- me-v2：在 sightings 加兩個欄位給新的「我的音樂劇」UI。
-- rating    : 0–5 星評分（demo 的星星）
-- precision : 日期精度 'year' | 'month' | 'day' | 'none'（seen_date 一律存完整日期，
--             以年精度為例存 YYYY-01-01，靠這欄還原使用者只記到哪一級；星期/月份統計需要）
-- 純新增、不動既有資料、可回復（drop column 即還原）。既有列取預設值。
alter table public.sightings add column if not exists rating smallint default 0;
alter table public.sightings add column if not exists precision text;
