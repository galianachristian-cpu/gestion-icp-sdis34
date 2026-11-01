# envoyer-rappels

Fonction déployée sur Supabase. Appelée toutes les 15 minutes par pg_cron
(`rappels-seances`), elle envoie une notification poussée aux appareils abonnés
dont l'heure et le jour correspondent, au plus une fois par jour et par appareil.
Les abonnements périmés (404/410) sont supprimés automatiquement.

Secrets attendus dans Supabase (Edge Functions → Secrets) :
- `VAPID_PUBLIC` : la clé publique, la même que dans l'appli (`PUSH_PUB`).
- `VAPID_PRIVATE` : la clé privée. À ne jamais mettre dans le code.
- `VAPID_SUBJECT` : `mailto:` suivi d'une adresse de contact.
- `CRON_SECRET` (facultatif) : si défini, la fonction n'accepte que les appels
  portant l'en-tête `x-cron-secret`. Il faut alors l'ajouter au job pg_cron.

Le code source complet se trouve dans le tableau de bord Supabase.
