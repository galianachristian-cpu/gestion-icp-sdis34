-- Planning des sessions ICP
create table if not exists public.sessions_icp (
  id bigint generated always as identity primary key,
  date date not null, heure text, lieu text, note text,
  created_at timestamptz not null default now()
);
alter table public.sessions_icp enable row level security;
create policy "Lecture comptes connectés" on public.sessions_icp for select to authenticated using (true);
create policy "Ecriture admin" on public.sessions_icp for all to authenticated
  using (public.est_admin_icp()) with check (public.est_admin_icp());

-- Accès personnel : un compte relié à un pompier ne voit que sa propre fiche
alter table public.comptes_app add column if not exists pompier_id integer references public.pompiers(id) on delete set null;
create or replace function public.mon_pompier_id() returns integer language sql stable security definer set search_path = '' as $$
  select c.pompier_id from public.comptes_app c where c.email = lower(auth.jwt() ->> 'email');
$$;
alter policy "Lecture comptes connectés" on public.pompiers using (public.mon_pompier_id() is null or id = public.mon_pompier_id());
alter policy "Lecture comptes connectés" on public.historique_reference using (public.mon_pompier_id() is null);
alter policy "Lecture comptes connectés" on public.carnet_seances using (public.mon_pompier_id() is null or pompier_id = public.mon_pompier_id());

-- Journal des modifications (déclencheur sur pompiers, lecture admin)
create table if not exists public.journal_icp (
  id bigint generated always as identity primary key,
  quand timestamptz not null default now(), qui text, operation text not null,
  pompier_id integer, pompier text, changements jsonb
);
alter table public.journal_icp enable row level security;
create policy "Lecture admin" on public.journal_icp for select to authenticated using (public.est_admin_icp());
-- fonction journaliser_pompier() + trigger journal_pompiers : voir le projet Supabase.

-- Sauvegardes : schéma « sauvegarde » (non exposé), copie hebdomadaire par pg_cron
-- (8 emplacements tournants) et fonction sauvegarde_export(clé) pour la copie externe.

-- Types de comptes : admin / équipe / pompier ; un compte sans rôle ne lit rien
-- (fonction type_compte_icp(), politiques de lecture mises à jour ; un pompier
--  supprimé supprime son accès : comptes_app.pompier_id ... on delete cascade).

-- Mots de passe provisoires (générés par l'admin), lisibles par l'admin seulement,
-- effacés dès que la personne choisit le sien (rpc mdp_personnalise()).
create table if not exists public.mdp_provisoires (
  email text primary key, mot_de_passe text,
  cree_le timestamptz not null default now(), personnalise_le timestamptz
);
alter table public.mdp_provisoires enable row level security;
create policy "Lecture admin" on public.mdp_provisoires for select to authenticated using (public.est_admin_icp());

-- 2026-10-24 : un compte relié à un pompier n'est « pompier » (sa seule ligne) que s'il n'a que l'onglet
-- « fiche ». Avec d'autres onglets (vue chef : ["fiche","synthese"]), il est traité comme un compte d'équipe.
CREATE OR REPLACE FUNCTION public.type_compte_icp()
 RETURNS text LANGUAGE sql STABLE SECURITY DEFINER SET search_path TO ''
AS $function$
  select case
    when public.est_admin_icp() then 'admin'
    when exists (select 1 from public.comptes_app c where c.email = lower(auth.jwt() ->> 'email')
                 and c.pompier_id is not null and coalesce(c.onglets,'[]'::jsonb) <@ '["fiche"]'::jsonb) then 'pompier'
    when exists (select 1 from public.comptes_app c where c.email = lower(auth.jwt() ->> 'email')) then 'equipe'
    else null end;
$function$;

-- 2026-10-24 : grade facultatif (affiché « CNE Chamayou » dans l'entête, l'accueil et la fiche)
alter table public.pompiers add column if not exists grade text;

-- 2026-10-24 : fonction facultative (ex. « Chef de centre »), affichée avec le grade complet et les galons
alter table public.pompiers add column if not exists fonction text;

-- 2026-10-24 : comptes « chef » (onglets fiche + synthese) : seule leur ligne de résultats ; la synthèse
-- de tous vient de synthese_couleurs (couleurs 1/2/3 et présence, publiée par l'admin à chaque sauvegarde).
create table if not exists public.synthese_couleurs(campagne text primary key, lignes jsonb not null default '[]'::jsonb, maj timestamptz not null default now());
alter table public.synthese_couleurs enable row level security;
-- policies : lecture type_compte_icp() in ('admin','equipe','chef') ; écriture est_admin_icp()
-- type_compte_icp() renvoie 'chef' si onglets ? 'synthese' et onglets <@ ["fiche","synthese"]
-- pompiers / carnet_seances : 'pompier' et 'chef' ne lisent que id = mon_pompier_id()

-- 2026-10-24 : journal des connexions (ouverture de l'appli, au plus 1 par quart d'heure et par compte)
create table if not exists public.connexions_icp(id bigserial primary key, email text not null, quand timestamptz not null default now());
alter table public.connexions_icp enable row level security;
-- lecture : est_admin_icp() ; écriture uniquement via la fonction noter_connexion() (security definer)

-- 2026-10-24 : fiches confidentielles (chefs) : lisibles seulement par l'admin et la personne elle-même
alter table public.pompiers add column if not exists confidentiel boolean default false;
-- pompiers_confidentiels() (security definer) ; policies pompiers / carnet_seances : 'equipe' exclut ces fiches ;
-- l'appli ne les publie pas dans synthese_couleurs.
