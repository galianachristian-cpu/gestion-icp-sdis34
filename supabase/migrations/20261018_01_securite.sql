-- Gestion ICP — sécurisation (appliqué le 18/10/2026 sur le projet efowmupcstdccmfxniot).
-- Les données nominatives ne figurent volontairement pas dans ce fichier (dépôt public).

-- Sauvegarde avant changements (schéma non exposé par l'API)
create schema if not exists sauvegarde;
revoke all on schema sauvegarde from anon, authenticated;
create table if not exists sauvegarde.pompiers_20261018 as select * from public.pompiers;

-- Qui est administrateur de l'appli ICP ?
create or replace function public.est_admin_icp()
returns boolean language sql stable security definer set search_path = ''
as $$
  select coalesce(
    lower(auth.jwt() ->> 'email') = 'galiana.christian@gmail.com'
    or exists (select 1 from public.comptes_app c
               where c.email = lower(auth.jwt() ->> 'email') and c.est_admin),
  false);
$$;
revoke execute on function public.est_admin_icp() from public, anon;
grant execute on function public.est_admin_icp() to authenticated;

-- Relevés papier 2022-2025 (sortis du code public ; contenu inséré à part)
create table if not exists public.historique_reference (
  campagne text primary key,
  lignes jsonb not null default '[]'::jsonb
);
alter table public.historique_reference enable row level security;
create policy "Lecture comptes connectés" on public.historique_reference for select to authenticated using (true);
create policy "Ecriture admin" on public.historique_reference for all to authenticated
  using (public.est_admin_icp()) with check (public.est_admin_icp());

-- comptes_app : plus de lecture publique ni de mot de passe en clair.
-- (Les comptes existants ont d'abord été recréés dans Supabase Auth avec leur
--  mot de passe actuel, chiffré bcrypt.)
create policy "Lecture propre ou admin" on public.comptes_app for select to authenticated
  using (email = lower(auth.jwt() ->> 'email') or public.est_admin_icp());
alter policy "Lecture publique" on public.comptes_app to authenticated
  using (email = lower(auth.jwt() ->> 'email') or public.est_admin_icp());
alter policy "Lecture publique" on public.comptes_app rename to "Lecture propre";
alter policy "Ecriture admin uniquement" on public.comptes_app
  using (public.est_admin_icp()) with check (public.est_admin_icp());
alter policy "Ecriture admin uniquement" on public.comptes_app rename to "Ecriture admin";
alter table public.comptes_app alter column mot_de_passe drop not null;
update public.comptes_app set mot_de_passe = null where mot_de_passe is not null;
-- À faire depuis le dashboard (SQL Editor) pour finir le ménage :
--   alter table public.comptes_app drop column mot_de_passe;
--   drop policy "Lecture propre ou admin" on public.comptes_app;   -- doublon de "Lecture propre"
--   drop policy "Ecriture admin (2)" on public.pompiers;           -- doublon de "Ecriture admin"

-- pompiers : rien sans connexion ; lecture pour les comptes connectés ; écriture admin
alter policy "Accès public (mode comptes simples)" on public.pompiers to authenticated
  using (public.est_admin_icp()) with check (public.est_admin_icp());
alter policy "Accès public (mode comptes simples)" on public.pompiers rename to "Ecriture admin";
create policy "Lecture comptes connectés" on public.pompiers for select to authenticated using (true);
alter policy "Authenticated full access" on public.pompiers
  using (public.est_admin_icp()) with check (public.est_admin_icp());
alter policy "Authenticated full access" on public.pompiers rename to "Ecriture admin (2)";
