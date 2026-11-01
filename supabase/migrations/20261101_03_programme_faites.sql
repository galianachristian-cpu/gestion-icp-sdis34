-- Séances cochées dans l'onglet « Mon programme » : on coche, sans RPE ni unités de charge.
create table if not exists public.programme_faites (
  id bigint generated always as identity primary key,
  pompier_id integer not null references public.pompiers(id) on delete cascade,
  date date not null,
  fait_le timestamptz not null default now(),
  unique (pompier_id, date)
);
create index if not exists programme_faites_idx on public.programme_faites (pompier_id, date desc);
alter table public.programme_faites enable row level security;
create policy "Lecture perso ou admin" on public.programme_faites for select to authenticated
  using (pompier_id = public.mon_pompier_id_icp() or public.est_admin_icp());
create policy "Ecriture admin" on public.programme_faites for all to authenticated
  using (public.est_admin_icp()) with check (public.est_admin_icp());
create policy "Je coche mes seances" on public.programme_faites for all to authenticated
  using (pompier_id = public.mon_pompier_id_icp())
  with check (pompier_id = public.mon_pompier_id_icp());
