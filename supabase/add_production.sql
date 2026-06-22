-- Production (製作/版本) layer on each sighting.
-- Run once in the Supabase SQL editor.
--   production_key : which production/version the user saw (e.g. "ph-25th-rah",
--                    "phantom of the opera::UK"). Resolves to a curated poster.
--   poster_override: a user-supplied poster URL for versions we don't list.
-- The app degrades gracefully if these are absent (it just won't persist them),
-- so adding them is what actually turns the feature on for saved logs.
alter table sightings add column if not exists production_key text;
alter table sightings add column if not exists poster_override text;
