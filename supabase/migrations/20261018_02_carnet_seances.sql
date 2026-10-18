-- Carnet de suivi (RPE × durée) — la table était attendue par l'appli mais n'existait pas.
create table if not exists public.carnet_seances (
  id bigint generated always as identity primary key,
  pompier_id integer not null references public.pompiers(id) on delete cascade,
  date date not null default current_date,
  type text,
  objectif_id text,
  objectif_label text,
  rpe numeric check (rpe between 0 and 10),
  duree_min numeric check (duree_min > 0),
  charge_ua integer,
  created_at timestamptz not null default now()
);
create index if not exists carnet_seances_pompier_idx on public.carnet_seances (pompier_id, date desc);
alter table public.carnet_seances enable row level security;
create policy "Lecture comptes connectés" on public.carnet_seances for select to authenticated using (true);
create policy "Ecriture admin" on public.carnet_seances for all to authenticated
  using (public.est_admin_icp()) with check (public.est_admin_icp());
