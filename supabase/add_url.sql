-- Optional links on each sighting (official site / ticket pages).
-- Run once in the Supabase SQL editor. `links` holds an array of URLs; `url` is
-- kept as the first link for backward compatibility.
alter table sightings add column if not exists url text;
alter table sightings add column if not exists links jsonb;
