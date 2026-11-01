-- Appli sport clonée dans l'onglet « Mon sport » : un espace de données par pompier.
-- Remplace Firebase/Firestore ; l'application y accède via un adaptateur qui présente
-- la même interface (collection / doc / set / get / delete / where).
create table if not exists public.sport_docs (
  coll text not null,
  doc_id text not null,
  pompier_id integer not null references public.pompiers(id) on delete cascade,
  data jsonb not null default '{}'::jsonb,
  maj timestamptz not null default now(),
  primary key (coll, doc_id)
);
create index if not exists sport_docs_pid_idx on public.sport_docs (pompier_id, coll);
alter table public.sport_docs enable row level security;
create policy "Mes donnees sport" on public.sport_docs for all to authenticated
  using (pompier_id = public.mon_pompier_id_icp())
  with check (pompier_id = public.mon_pompier_id_icp());
create policy "Admin" on public.sport_docs for all to authenticated
  using (public.est_admin_icp()) with check (public.est_admin_icp());
