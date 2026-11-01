-- Onglet « Mon programme » : un profil d'entraînement par pompier.
-- Les blessures sont des données de santé : lisibles seulement par l'intéressé et l'administrateur.
create or replace function public.mon_pompier_id_icp()
returns integer language sql stable security definer set search_path = ''
as $$
  select c.pompier_id from public.comptes_app c
  where c.email = lower(auth.jwt() ->> 'email') limit 1;
$$;
revoke execute on function public.mon_pompier_id_icp() from public, anon;
grant execute on function public.mon_pompier_id_icp() to authenticated;

create table if not exists public.programme_profils (
  pompier_id integer primary key references public.pompiers(id) on delete cascade,
  objectif text not null,
  seances_sem integer not null check (seances_sem between 1 and 5),
  jours text not null default '',
  duree_min integer not null check (duree_min between 20 and 120),
  blessures jsonb not null default '[]'::jsonb,
  contre_indications text,
  rappel_heure text not null default '18:00',
  rappels jsonb not null default '{"seance":true,"bilan":true}'::jsonb,
  cree_le timestamptz not null default now(),
  maj_le timestamptz not null default now()
);
alter table public.programme_profils enable row level security;
create policy "Lecture perso ou admin" on public.programme_profils for select to authenticated
  using (pompier_id = public.mon_pompier_id_icp() or public.est_admin_icp());
create policy "Ecriture admin" on public.programme_profils for all to authenticated
  using (public.est_admin_icp()) with check (public.est_admin_icp());
create policy "Je gere mon profil" on public.programme_profils for all to authenticated
  using (pompier_id = public.mon_pompier_id_icp())
  with check (pompier_id = public.mon_pompier_id_icp());

-- chacun note ses propres séances dans le carnet (RPE x duree)
create policy "Je note mes seances" on public.carnet_seances for insert to authenticated
  with check (pompier_id = public.mon_pompier_id_icp());
create policy "Je retire mes seances" on public.carnet_seances for delete to authenticated
  using (pompier_id = public.mon_pompier_id_icp());
