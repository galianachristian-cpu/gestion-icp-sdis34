# gestion-icp-sdis34

Saisie et suivi des ICP (indices de condition physique) — caserne Cruzy-Quarante, SDIS 34.
Publiée via GitHub Pages ; données dans Supabase.

## Organisation

- `index.html` : l'application (une seule page).
- `img/seance/` : photos des exercices, chargées à la demande.
- `manifest.webmanifest`, `sw.js`, `icons/` : installation sur l'écran d'accueil du téléphone.
- `supabase/functions/gerer-comptes/` : fonction serveur qui crée / modifie / supprime les comptes
  (onglet Comptes). Déployée sur le projet Supabase.
- `supabase/migrations/` : scripts SQL appliqués à la base (règles d'accès, tables).

## Sécurité

- Aucune donnée nominative dans ce dépôt public : tout est dans Supabase, lisible uniquement après connexion.
- Tous les comptes passent par Supabase Auth (mots de passe chiffrés). L'administrateur gère les comptes
  depuis l'onglet Comptes ; chacun peut changer son mot de passe (bouton 🔑).
- Seuls les administrateurs (`est_admin_icp()`) peuvent écrire ; les autres comptes sont en lecture seule.

## Mon sport (dossier `sport/`)

Copie de l'application personnelle **mon-app-sport** de Christian
(https://github.com/galianachristian-cpu/mon-app-sport), mise à disposition des pompiers
du centre dans l'onglet « 💪 Mon sport ».

Le code de l'application est repris tel quel. Seule la couche de stockage a changé :
Firebase/Firestore est remplacé par un adaptateur qui écrit dans la table Supabase
`sport_docs`, avec un espace par pompier. L'adaptateur présente la même interface que
Firestore (`collection` / `doc` / `set` / `get` / `delete` / `where`), si bien que le reste
de l'application n'a pas été modifié. Les profils en dur (Moi / Béa) sont remplacés par
le pompier connecté, transmis par l'onglet dans l'adresse (`?pid=&prenom=&nom=`).

Chaque identifiant de document est préfixé par le numéro du pompier, et les règles
d'accès Supabase limitent chacun à ses propres lignes.

Pour remonter une évolution faite dans l'application d'origine : recopier son `index.html`
puis réappliquer ces deux changements (adaptateur Supabase et profil unique).
