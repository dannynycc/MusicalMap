-- MusicalMap — personal "shows I've seen" backend (Supabase / Postgres)
-- Run once in Supabase SQL editor. Safe to re-run (idempotent-ish).

-- ── profiles: one row per authenticated user ───────────────────────────────
create table if not exists profiles (
  id          uuid primary key references auth.users on delete cascade,
  display_name text,
  handle      text unique,                 -- for future public url /me/<handle>
  is_public   boolean not null default false,
  created_at  timestamptz not null default now()
);

-- ── sightings: a musical the user has seen (denormalised for simplicity) ────
create table if not exists sightings (
  id         bigint generated always as identity primary key,
  user_id    uuid not null references auth.users on delete cascade default auth.uid(),
  title      text not null,
  venue      text,
  city       text,
  country    text,
  lat        double precision,
  lng        double precision,
  seen_date  date,
  seen_time  time,
  seat       text,
  price      numeric(10,2),
  currency   text,
  note       text,
  created_at timestamptz not null default now()
);
create index if not exists sightings_user_idx on sightings(user_id);

-- ── crowd-sourced venue dictionary (grows as users add new venues) ─────────
create table if not exists venues (
  id         bigint generated always as identity primary key,
  name       text not null,
  city       text,
  country    text,
  lat        double precision,
  lng        double precision,
  created_by uuid references auth.users,
  created_at timestamptz not null default now(),
  unique (name, city)
);

-- ── Row Level Security ─────────────────────────────────────────────────────
alter table profiles  enable row level security;
alter table sightings enable row level security;
alter table venues    enable row level security;

-- profiles: anyone can read public ones or their own; write only own
drop policy if exists profiles_read on profiles;
create policy profiles_read on profiles for select
  using (is_public or id = auth.uid());
drop policy if exists profiles_write on profiles;
create policy profiles_write on profiles for all
  using (id = auth.uid()) with check (id = auth.uid());

-- sightings: read own, or anyone's if that profile is public; write only own
drop policy if exists sightings_read on sightings;
create policy sightings_read on sightings for select using (
  user_id = auth.uid()
  or exists (select 1 from profiles p where p.id = sightings.user_id and p.is_public)
);
drop policy if exists sightings_write on sightings;
create policy sightings_write on sightings for all
  using (user_id = auth.uid()) with check (user_id = auth.uid());

-- venues: public read; any signed-in user may add
drop policy if exists venues_read on venues;
create policy venues_read on venues for select using (true);
drop policy if exists venues_insert on venues;
create policy venues_insert on venues for insert to authenticated with check (true);

-- ── auto-create a profile row on first sign-in ─────────────────────────────
create or replace function handle_new_user() returns trigger
language plpgsql security definer set search_path = public as $$
begin
  -- fallback 用 email 的 @ 前綴,不落完整 email(display_name 是公開頁標題,完整 email 會被公開展示;
  -- 見 supabase/fix_display_name_email_leak.sql, 2026-07-03)
  insert into public.profiles (id, display_name)
  values (new.id, coalesce(new.raw_user_meta_data->>'full_name', split_part(new.email, '@', 1)))
  on conflict (id) do nothing;
  return new;
end; $$;
drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created after insert on auth.users
  for each row execute function handle_new_user();
