# Gestion ICP : carnet de bord pour Claude

À lire en début de session. Ce dépôt est **public** et publié tel quel par GitHub Pages : **aucune donnée nominative** ici (noms de pompiers, e-mails, mots de passe, résultats). Tout cela est dans Supabase, lisible seulement après connexion.

## Le projet
- App web installable (PWA) en français : saisie et suivi des ICP (indices de condition physique) du centre de secours Cruzy-Quarante (SDIS 34), avec séances, défis, mode TV de la salle de sport et l'onglet « Mon sport ».
- **`index.html`** : toute l'application (environ 9 600 lignes, un seul script principal). **`rame.html`** : « Rame en direct » (scène 3D, rameur Concept2 PM5 et SkiErg en Bluetooth, affichage sur la télé avec `rame.html?ecran`). `tuto-rame.html`, `tuto-skierg.html` : tutos de connexion.
- **`sport/`** : copie de l'app personnelle mon-app-sport, avec un adaptateur Supabase à la place de Firebase et un profil unique (le pompier connecté). Pour la mettre à jour, voir le README : recopier son `index.html` puis réappliquer ces deux changements.
- `supabase/migrations/` : scripts SQL (tables, règles d'accès). `supabase/functions/` : `gerer-comptes` (comptes), `envoyer-rappels` (notifications). Ils sont déployés sur le projet Supabase, pas par ce dépôt.
- `audio/` : voix du Sergent-Chef et sons de la TV. `img/` : photos et images. `outils/` : ateliers d'animation (Blender, Mixamo, scripts Python) et `carte.cjs`.
- Tables Supabase utilisées : `pompiers`, `sessions_icp`, `carnet_seances`, `comptes_app`, `connexions_icp`, `historique_reference`, `journal_icp`, `mdp_provisoires`, `synthese_couleurs`, `sport_docs`…
- Droits : seuls les administrateurs (`est_admin_icp()` côté SQL, `isAdmin` dans l'app) peuvent écrire ; les autres comptes sont en lecture seule. Comptes « vue chef » : aperçu limité aux onglets autorisés.
- Onglets (`tab-…`) : dashboard, synthèse, fiche, saisie, terrain, bilan, progression, cardio, muscu, séances, échelles, programme, aide, défis, ménage, PPA, export, comptes.

## S'orienter dans le code
- **Carte complète : `docs/CARTE.md`** (sections `// ===== … =====` avec leur ligne de début, sous-sections `// --- … ---`, noms des fonctions, pour `index.html` et `rame.html`). La consulter avant de relire un fichier, puis lire seulement la zone utile (Grep sur le nom, puis Read avec offset).
- Après une modification de `index.html` ou de `rame.html`, lancer **`node outils/carte.cjs`**. GitHub vérifie la carte à chaque envoi (`.github/workflows/carte.yml`) et signale si elle est périmée.
- Changement d'onglet : `switchTab(id)`.

## Façon de travailler
1. Une modification = un commit au titre clair, en français, sous la forme « Zone : ce qui change » (ex. « Mode TV : … », « Défis : … », « Rame en direct : … »).
2. À chaque modification de l'app, augmenter `VERSION` dans `sw.js` (`icp-vNNN`) pour que les téléphones prennent la nouvelle version.
3. `node outils/carte.cjs`.
4. Vérifier dans un navigateur (Playwright est disponible) avant de publier : le site est mis en ligne dès que `main` change.

## Préférences de l'utilisateur
- Réponses en français, franches, sans jargon. Une seule étape à la fois quand il doit faire une manipulation lui-même (captures d'écran à l'appui).
- Ne jamais demander de mot de passe ni de clé dans la discussion : il les tape lui-même sur ses appareils. Aucune clé secrète dans ce dépôt public (la clé publique « anon » de Supabase est la seule admise).
- Quand il demande « des idées », proposer une liste numérotée : il répond par numéros.

## Personnages et ton
- Le Sergent-Chef et la Sergente-Chef (casque chromé) sont les mascottes : voix dans `audio/`, modèles 3D et animations faits dans `outils/`. Voir `docs/sergent-chef.md` et `docs/calendrier-defis.md`.
