# envoyer-rappels

Appelée toutes les 15 minutes par pg_cron (`rappels-seances`). Envoie une
notification poussée aux appareils abonnés dont l'heure et le jour correspondent,
au plus une fois par jour et par appareil. Les abonnements périmés (404/410)
sont supprimés automatiquement.

`?test=<pompier_id>` envoie immédiatement une notification de test à tous les
appareils de ce pompier, sans tenir compte de l'heure ni du jour.

Secrets (Edge Functions → Secrets) :
- `VAPID_PUBLIC` : clé publique, la même que `PUSH_PUB` dans l'appli (87 caractères).
- `VAPID_PRIVATE` : clé privée (43 caractères), jamais dans le code.
- `VAPID_SUBJECT` : `mailto:` suivi d'une adresse de contact.
- `CRON_SECRET` (facultatif) : si défini, la fonction exige l'en-tête `x-cron-secret`.

Les clés sont nettoyées à la lecture (espaces, retours à la ligne, `=` final) :
une valeur collée avec un caractère en trop ne casse plus l'envoi.
