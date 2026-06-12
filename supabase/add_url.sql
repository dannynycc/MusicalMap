-- Add an optional official-site / ticket link to each sighting.
-- Run once in the Supabase SQL editor.
alter table sightings add column if not exists url text;
