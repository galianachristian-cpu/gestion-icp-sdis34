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
