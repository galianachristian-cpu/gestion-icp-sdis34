-- Défis collectifs du centre : créés par l'administrateur, alimentés par tous.
create table if not exists public.defis (
  id bigint generated always as identity primary key,
  titre text not null,
  theme text not null,
  unite text not null,
  objectif numeric not null check (objectif > 0),
  collectif boolean not null default true,
  debut date not null default current_date,
  fin date not null,
  recompense text,
  icone text not null default '🏆',
  couleur text not null default '#22d3ee',
  actif boolean not null default true,
  cree_le timestamptz not null default now(),
  check (fin >= debut)
);
create table if not exists public.defis_contrib (
  id bigint generated always as identity primary key,
  defi_id bigint not null references public.defis(id) on delete cascade,
  pompier_id integer not null references public.pompiers(id) on delete cascade,
  valeur numeric not null check (valeur > 0),
  date date not null default current_date,
  note text,
  cree_le timestamptz not null default now()
);
create index if not exists defis_contrib_idx on public.defis_contrib (defi_id, pompier_id);
alter table public.defis enable row level security;
alter table public.defis_contrib enable row level security;
create policy "Lecture defis" on public.defis for select to authenticated using (true);
create policy "Admin defis" on public.defis for all to authenticated
  using (public.est_admin_icp()) with check (public.est_admin_icp());
create policy "Lecture contrib" on public.defis_contrib for select to authenticated using (true);
create policy "Admin contrib" on public.defis_contrib for all to authenticated
  using (public.est_admin_icp()) with check (public.est_admin_icp());
create policy "Ma contribution" on public.defis_contrib for all to authenticated
  using (pompier_id = public.mon_pompier_id_icp())
  with check (pompier_id = public.mon_pompier_id_icp());
