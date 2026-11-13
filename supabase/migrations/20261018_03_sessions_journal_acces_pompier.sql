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

-- 2026-11-06 : onglets personnels (programme, defis, aide) : un compte pompier / chef qui les a garde
-- son type (sa seule fiche). annuaire_icp() : prénom, nom, grade de chacun (sans résultat) pour les défis.

-- 2026-11-06 : photos de profil (photos_pompiers : image JPEG 240 px en data URL, < 150 ko)
-- lecture : tout compte connu ; écriture : admin ou la personne elle-même (mon_pompier_id())

-- 2026-11-07 : type de compte « ecran » (télé / tablette de la salle, mode TV).
-- Compte sans pompier relié, onglets ⊆ {defis, aide} (dont defis) : type_compte_icp() = 'ecran'.
-- Il lit le défi, l'annuaire (prénoms) et les photos ; aucune ligne de pompiers, carnet_seances,
-- synthese_couleurs ni historique_reference (ces politiques n'acceptent pas 'ecran').
-- (Avant ce changement, un tel compte aurait été classé 'equipe' et aurait lu tous les résultats.)
--   ... when exists (... c.pompier_id is null and onglets ? 'defis'
--                    and onglets <@ '["defis","aide"]') then 'ecran'   -- inséré avant 'equipe'

-- 2026-11-07 : notifications des défis (fonction envoyer-rappels v7)
alter table public.defis add column if not exists palier_notifie integer not null default -1;
-- -1 rien envoyé, 0 départ annoncé, 25/50/75/100 dernier palier annoncé à tous les abonnés push.

-- 2026-11-07 : envoyer-rappels n'accepte plus que pg_cron (clé aléatoire, illisible par l'appli)
create table if not exists public.secrets_internes (nom text primary key, valeur text not null);
alter table public.secrets_internes enable row level security;
revoke all on public.secrets_internes from anon, authenticated;
insert into public.secrets_internes(nom, valeur) values ('cron_rappels', encode(extensions.gen_random_bytes(32), 'hex')) on conflict (nom) do nothing;
-- tâche pg_cron « rappels-seances » : en-tête x-cron-secret = (select valeur from public.secrets_internes where nom='cron_rappels')

-- 2026-11-07 : défis par garde
alter table public.pompiers add column if not exists garde text;
alter table public.defis add column if not exists par_garde boolean not null default false;
-- annuaire_icp() renvoie maintenant (id, prenom, nom, grade, garde) ; exécution réservée à authenticated.

-- 2026-11-11 : bravos entre collègues sur les séances d'un défi
create table if not exists public.defis_bravos (
  contrib_id bigint not null references public.defis_contrib(id) on delete cascade,
  pompier_id integer not null references public.pompiers(id) on delete cascade,
  cree_le timestamptz not null default now(),
  primary key (contrib_id, pompier_id)
);
alter table public.defis_bravos enable row level security;
-- lecture : tout compte connecté ; ajout / retrait : son propre bravo (pompier_id = mon_pompier_id_icp()) ou l'admin.

-- 2026-11-12 : annuaire_icp() renvoie aussi le sexe (id, prenom, nom, grade, garde, sexe) pour accorder les grades
-- et messages des défis (Mo Sisters) ; exécution réservée aux comptes connectés (authenticated, service_role).

-- 2026-11-12 : cases personnelles (calendrier de l'Avent, défi du jour), retrouvées sur tous les téléphones
create table if not exists public.cases_perso (
  email text not null default lower(auth.jwt() ->> 'email'),
  type text not null check (type in ('avent','defi_jour')),
  jour date not null,
  cree_le timestamptz not null default now(),
  primary key (email, type, jour)
);
-- RLS : chacun lit, ajoute et retire uniquement ses propres cases (email du jeton) ; l'admin peut lire.
-- Ajout refusé pour une date après demain (pas d'ouverture des cases futures du calendrier).

-- 2026-11-12 : inscriptions aux sessions ICP + rappel J-7
alter table public.sessions_icp add column if not exists places integer check (places is null or places > 0);
alter table public.sessions_icp add column if not exists rappel_j7 boolean not null default false;
create table if not exists public.inscriptions_icp (
  session_id bigint not null references public.sessions_icp(id) on delete cascade,
  pompier_id integer not null references public.pompiers(id) on delete cascade,
  cree_le timestamptz not null default now(),
  primary key (session_id, pompier_id)
);
-- RLS : lecture par les comptes connectés ; inscription / désinscription de soi (mon_pompier_id_icp) ou par l'admin.
-- Trigger verifier_inscription_icp : refus si la session est passée ou complète (places).
-- envoyer-rappels v10 : notification « Session ICP dans 7 jours » à tous les abonnés, une fois (rappel_j7).

-- 2026-11-13 : machines en panne + utilisation
-- table pannes (machine, description, photo, signale_par = email du jeton, statut ouverte/reparee, notifie) ;
-- RLS : lecture par les comptes connectés ; signalement par tout compte connecté (en son nom, statut ouverte) ;
-- mise à jour / suppression par l'admin. Alerte push (envoyer-rappels v11) aux fiches listées dans
-- secrets_internes.alerte_pannes_pompiers.
-- connexions_icp.installe : appli ouverte depuis l'écran d'accueil (noter_connexion(p_installe boolean default null)).

-- ===== 13/11/2026 : duels et mur des photos (migration « duels_et_mur_photos ») =====
-- duels : un pompier en défie un autre sur le défi en cours, jusqu'au dimanche.
--   id, defi_id, challenger, adversaire (pompiers.id), debut, fin (date),
--   statut propose / accepte / refuse / annule, notifie (push envoyé par envoyer-rappels), cree_le.
--   RLS : lecture par les comptes connectés ; création seulement avec challenger = mon_pompier_id_icp() ;
--   modification par l'un des deux participants ou l'admin ; suppression par l'admin.
-- photos_seances : photo d'une séance (contrib), publiée sur le mur et la TV après validation de l'admin.
--   id, contrib_id (unique), pompier_id, image (data URL JPEG, 400 000 caractères max), valide, cree_le.
--   RLS : lecture des photos validées, des siennes, ou tout pour l'admin ; ajout de sa propre photo,
--   sur sa propre séance, toujours valide = false ; validation par l'admin ; suppression par l'auteur ou l'admin.
