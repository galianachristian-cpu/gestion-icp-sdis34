// Envoi des rappels de séance, même application fermée (Web Push).
// Appelée toutes les 15 minutes par pg_cron. Pour chaque appareil abonné dont
// l'heure et le jour correspondent, envoie une notification, une seule par jour.
import "jsr:@supabase/functions-js/edge-runtime.d.ts";
import { createClient } from "npm:@supabase/supabase-js@2.47.10";
import webpush from "npm:web-push@3.6.7";

// Les clés sont saisies à la main dans le tableau de bord : on retire les espaces,
// les retours à la ligne et le « = » de remplissage qui s'y glissent facilement.
const propre = (s: string) => (s ?? "").replace(/\s+/g, "").replace(/=+$/, "");

const PUB = propre(Deno.env.get("VAPID_PUBLIC") ?? "");
const PRIV = propre(Deno.env.get("VAPID_PRIVATE") ?? "");
const SUJET = (Deno.env.get("VAPID_SUBJECT") ?? "mailto:contact@example.org").trim();
const SECRET_CRON = (Deno.env.get("CRON_SECRET") ?? "").trim();

Deno.serve(async (req: Request) => {
  try {
    if (SECRET_CRON && (req.headers.get("x-cron-secret") ?? "") !== SECRET_CRON) {
      return new Response("non autorisé", { status: 401 });
    }
    if (PUB.length !== 87 || PRIV.length !== 43) {
      return Response.json({
        erreur: "clés VAPID invalides",
        attendu: "publique 87 caractères, privée 43",
        recu: { publique: PUB.length, privee: PRIV.length },
      }, { status: 500 });
    }
    webpush.setVapidDetails(SUJET, PUB, PRIV);
    const sb = createClient(Deno.env.get("SUPABASE_URL")!, Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!);

    // heure de Paris, quel que soit le fuseau du serveur
    const fmt = new Intl.DateTimeFormat("fr-FR", {
      timeZone: "Europe/Paris", hour: "2-digit", minute: "2-digit",
      year: "numeric", month: "2-digit", day: "2-digit",
    });
    const parts = Object.fromEntries(fmt.formatToParts(new Date()).map((p) => [p.type, p.value]));
    const minutes = parseInt(parts.hour, 10) * 60 + parseInt(parts.minute, 10);
    const aujourdhui = `${parts.year}-${parts.month}-${parts.day}`;
    const jour = (new Date(`${aujourdhui}T12:00:00Z`).getUTCDay() + 6) % 7;

    const url = new URL(req.url);
    const essai = url.searchParams.get("test"); // ?test=<pompier_id> : envoi immédiat

    const { data: abos, error } = await sb.from("push_abos").select("*").eq("actif", true);
    if (error) return Response.json({ erreur: error.message }, { status: 500 });

    let envoyes = 0, retires = 0, vus = 0;
    for (const a of abos ?? []) {
      if (essai) {
        if (String(a.pompier_id) !== essai) continue;
      } else {
        if (a.dernier_envoi === aujourdhui) continue;
        const jours = String(a.jours || "").split(",").filter((x: string) => x !== "").map(Number);
        if (jours.length && jours.indexOf(jour) === -1) continue;
        const [hh, mm] = String(a.heure || "18:00").split(":").map(Number);
        const cible = hh * 60 + mm;
        if (minutes < cible || minutes >= cible + 20) continue;
      }
      vus++;
      const charge = JSON.stringify({
        titre: essai ? "✅ Test réussi" : "🏋️ Ta séance t'attend",
        corps: essai ? "Les rappels fonctionnent sur cet appareil." : "Salle de la caserne. Ouvre Mon sport quand tu veux.",
        url: "https://galianachristian-cpu.github.io/gestion-icp-sdis34/",
      });
      try {
        await webpush.sendNotification(
          { endpoint: a.endpoint, keys: { p256dh: a.p256dh, auth: a.auth } },
          charge,
        );
        envoyes++;
        if (!essai) await sb.from("push_abos").update({ dernier_envoi: aujourdhui }).eq("id", a.id);
      } catch (e) {
        const code = (e as { statusCode?: number }).statusCode;
        if (code === 404 || code === 410) {
          await sb.from("push_abos").delete().eq("id", a.id);
          retires++;
        }
      }
    }
    return Response.json({ heure: `${parts.hour}:${parts.minute}`, jour, abonnes: (abos ?? []).length, concernes: vus, envoyes, retires });
  } catch (e) {
    return Response.json({ erreur: (e as Error).message }, { status: 500 });
  }
});
