-- Trace d'usage de l'appli sport : un jour où la personne a enregistré quelque chose.
-- Volontairement sans aucun détail de contenu : sert seulement à mesurer la participation.
create table if not exists public.sport_activite (
  pompier_id integer not null references public.pompiers(id) on delete cascade,
  jour date not null,
  primary key (pompier_id, jour)
);
alter table public.sport_activite enable row level security;
create policy "La mienne" on public.sport_activite for all to authenticated
  using (pompier_id = public.mon_pompier_id_icp())
  with check (pompier_id = public.mon_pompier_id_icp());
create policy "Lecture admin" on public.sport_activite for select to authenticated
  using (public.est_admin_icp());
