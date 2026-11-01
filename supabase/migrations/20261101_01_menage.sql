-- Planning de nettoyage de la salle de sport (onglet « Ménage »).
-- Une ligne = une case de la feuille papier : jour + mission + initiales.
create table if not exists public.menage_taches (
  id bigint generated always as identity primary key,
  annee integer not null check (annee between 2020 and 2100),
  mois integer not null check (mois between 1 and 12),
  jour integer not null check (jour between 1 and 31),
  mission text not null check (mission in ('aspirateur','sols','poussiere','materiel','autres')),
  initiales text not null,
  created_at timestamptz not null default now(),
  unique (annee, mois, jour, mission)
);
create index if not exists menage_taches_periode_idx on public.menage_taches (annee, mois);
alter table public.menage_taches enable row level security;
drop policy if exists "Lecture comptes connectés" on public.menage_taches;
drop policy if exists "Ecriture admin" on public.menage_taches;
create policy "Lecture comptes connectés" on public.menage_taches for select to authenticated using (true);
create policy "Ecriture admin" on public.menage_taches for all to authenticated
  using (public.est_admin_icp()) with check (public.est_admin_icp());
