-- Planning de nettoyage de la salle de sport (onglet « Ménage »).
-- Une ligne = une personne a fait une mission un jour donné.
-- Chacun peut cocher sa propre mission le jour même ou la veille ; l'administrateur saisit tout le mois.
drop table if exists public.menage_taches;
create table public.menage_taches (
  id bigint generated always as identity primary key,
  annee integer not null check (annee between 2020 and 2100),
  mois integer not null check (mois between 1 and 12),
  jour integer not null check (jour between 1 and 31),
  mission text not null check (mission in ('aspirateur','sols','poussiere','materiel','poubelle','machines','autres')),
  initiales text not null check (initiales ~ '^[A-ZÀ-Ý]{2,4}$'),
  detail text,
  created_at timestamptz not null default now(),
  unique (annee, mois, jour, mission, initiales)
);
create index menage_taches_periode_idx on public.menage_taches (annee, mois);
alter table public.menage_taches enable row level security;

-- Code du compte connecté : 2 premières lettres du prénom + 2 du nom (Christian Galiana -> CHGA).
-- Sur 2 lettres, 7 paires de pompiers du centre se retrouvaient avec le même code.
create or replace function public.mes_initiales_icp()
returns text language sql stable security definer set search_path = ''
as $$
  select upper(left(btrim(p.prenom),2) || left(btrim(p.nom),2))
  from public.comptes_app c join public.pompiers p on p.id = c.pompier_id
  where c.email = lower(auth.jwt() ->> 'email')
  limit 1;
$$;
revoke execute on function public.mes_initiales_icp() from public, anon;
grant execute on function public.mes_initiales_icp() to authenticated;

create policy "Lecture comptes connectés" on public.menage_taches for select to authenticated using (true);
create policy "Ecriture admin" on public.menage_taches for all to authenticated
  using (public.est_admin_icp()) with check (public.est_admin_icp());
create policy "Je coche ma mission" on public.menage_taches for insert to authenticated
  with check (initiales = public.mes_initiales_icp()
    and make_date(annee, mois, jour) between current_date - 1 and current_date);
create policy "Je décoche ma mission" on public.menage_taches for delete to authenticated
  using (initiales = public.mes_initiales_icp()
    and make_date(annee, mois, jour) between current_date - 1 and current_date);
