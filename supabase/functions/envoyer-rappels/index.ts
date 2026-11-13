// Envoi des rappels de séance, même application fermée (Web Push).
// Appelée toutes les 15 minutes par pg_cron. Pour chaque appareil abonné dont
// l'heure et le jour correspondent, envoie une notification, une seule par jour.
// Défis du centre : prévient aussi tous les abonnés au départ d'un défi et quand le
// centre franchit 25, 50, 75 et 100 %, puis les paliers bonus 150, 200, 250 %…
// (une seule fois par palier, entre 8 h et 21 h 30). Session ICP : rappel à J-7 (une fois par session).
// Machine en panne : alerte à l'administrateur dans le quart d'heure.
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
    const sb = createClient(Deno.env.get("SUPABASE_URL")!, Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!);
    // Seul pg_cron peut déclencher l'envoi : il joint la clé gardée dans secrets_internes
    // (table illisible par l'appli). Repli sur la variable CRON_SECRET si elle est définie.
    let attendu = SECRET_CRON;
    if (!attendu) {
      const { data: s } = await sb.from("secrets_internes").select("valeur").eq("nom", "cron_rappels").maybeSingle();
      attendu = (s?.valeur ?? "").trim();
    }
    if (!attendu || (req.headers.get("x-cron-secret") ?? "") !== attendu) {
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
    // ----- Défis : départ et paliers -----
    const defisEnvoyes: string[] = [];
    if (!essai && minutes >= 8 * 60 && minutes <= 21 * 60 + 30) {
      const { data: defis } = await sb.from("defis").select("id,titre,theme,unite,objectif,debut,fin,palier_notifie")
        .eq("actif", true).lte("debut", aujourdhui).gte("fin", aujourdhui);
      for (const d of defis ?? []) {
        const { data: cs } = await sb.from("defis_contrib").select("valeur").eq("defi_id", d.id);
        const total = (cs ?? []).reduce((t: number, x: { valeur: number }) => t + Number(x.valeur || 0), 0);
        const pct = Math.floor(100 * total / Math.max(1, Number(d.objectif)));
        // au-delà de 100 % : paliers bonus tous les 50 % (150, 200, 250…)
        const palier = pct >= 100 ? Math.floor(pct / 50) * 50 : ([75, 50, 25, 0].find((p) => pct >= p) ?? 0);
        const deja = Number(d.palier_notifie ?? -1);
        if (palier <= deja) continue;
        // on note le palier AVANT d'envoyer : jamais deux fois la même notification
        const { data: maj } = await sb.from("defis").update({ palier_notifie: palier })
          .eq("id", d.id).eq("palier_notifie", deja).select("id");
        if (!maj || !maj.length) continue;
        const txt = `${d.titre ?? ""} ${d.theme ?? ""}`;
        const noel = /no[eë]l|p[eè]re[ -]no/i.test(txt), mov = /movember/i.test(txt);
        const km = (v: number) => String(Math.round(v * 10) / 10).replace(".", ",");
        const corps = palier === 0
          ? (noel ? "Le Père Noël chausse ses skis : chaque km compte, à vous de jouer !" : mov ? "Les moustaches sont lâchées : à vos rames !" : "Le défi du centre commence aujourd'hui. À vous de jouer !")
          : palier > 100
          ? `Sergent-Chef à tous : ${km(total)} ${d.unite}, soit ${palier} % de l'objectif. Vous pensiez avoir fini ? Prochain palier : ${km(Number(d.objectif) * (palier + 50) / 100)} ${d.unite}.`
          : palier === 100
          ? `Objectif atteint : ${km(total)} ${d.unite}. Bravo à tout le centre !`
          : (noel ? ["", "Les rennes sont attelés", "Les montagnes sont passées", "Le village est en vue"][palier / 25] + ` : ${km(total)} / ${km(Number(d.objectif))} ${d.unite}. On ne lâche rien !`
                  : `Le centre a passé ${palier} % : ${km(total)} / ${km(Number(d.objectif))} ${d.unite}. On continue !`);
        const titre = palier === 0 ? `🚀 C'est parti : ${d.titre}` : palier > 100 ? `🏅 ${d.titre} : palier bonus ${palier} % !` : palier === 100 ? `🎉 ${d.titre} : défi réussi !` : `🔥 ${d.titre} : ${palier} % !`;
        const charge = JSON.stringify({ titre, corps, url: "https://galianachristian-cpu.github.io/gestion-icp-sdis34/" });
        for (const a of abos ?? []) {
          try {
            await webpush.sendNotification({ endpoint: a.endpoint, keys: { p256dh: a.p256dh, auth: a.auth } }, charge);
            envoyes++;
          } catch (e) {
            const code = (e as { statusCode?: number }).statusCode;
            if (code === 404 || code === 410) { await sb.from("push_abos").delete().eq("id", a.id); retires++; }
          }
        }
        defisEnvoyes.push(`${d.id}:${palier}`);
      }
    }
    // ----- Session ICP dans 7 jours : un rappel à tous les abonnés, une seule fois par session -----
    const sessionsEnvoyees: number[] = [];
    if (!essai && minutes >= 9 * 60 && minutes <= 20 * 60) {
      const j7 = new Date(`${aujourdhui}T12:00:00Z`); j7.setUTCDate(j7.getUTCDate() + 7);
      const dateJ7 = j7.toISOString().slice(0, 10);
      const { data: ses } = await sb.from("sessions_icp").select("id,date,heure,lieu,rappel_j7").eq("date", dateJ7).eq("rappel_j7", false);
      for (const se of ses ?? []) {
        const { data: maj } = await sb.from("sessions_icp").update({ rappel_j7: true }).eq("id", se.id).eq("rappel_j7", false).select("id");
        if (!maj || !maj.length) continue;
        const quand = new Intl.DateTimeFormat("fr-FR", { weekday: "long", day: "numeric", month: "long", timeZone: "UTC" }).format(new Date(`${se.date}T12:00:00Z`));
        const charge = JSON.stringify({
          titre: "📅 Session ICP dans 7 jours",
          corps: `${quand}${se.heure ? " à " + se.heure : ""}${se.lieu ? " — " + se.lieu : ""}. Inscris-toi dans l'appli et regarde ta priorité sur ta fiche. Le Sergent-Chef compte sur toi.`,
          url: "https://galianachristian-cpu.github.io/gestion-icp-sdis34/",
        });
        for (const a of abos ?? []) {
          try { await webpush.sendNotification({ endpoint: a.endpoint, keys: { p256dh: a.p256dh, auth: a.auth } }, charge); envoyes++; }
          catch (e) { const code = (e as { statusCode?: number }).statusCode; if (code === 404 || code === 410) { await sb.from("push_abos").delete().eq("id", a.id); retires++; } }
        }
        sessionsEnvoyees.push(se.id);
      }
    }
    // ----- Machines en panne : alerte à l'administrateur (fiches listées dans secrets_internes) -----
    let pannesEnvoyees = 0;
    if (!essai) {
      const { data: np } = await sb.from("pannes").select("id,machine,description").eq("notifie", false).eq("statut", "ouverte");
      if (np && np.length) {
        const { data: cfg } = await sb.from("secrets_internes").select("valeur").eq("nom", "alerte_pannes_pompiers").maybeSingle();
        const ids = String(cfg?.valeur ?? "").split(",").map((x) => parseInt(x, 10)).filter((x) => !isNaN(x));
        for (const pa of np) {
          const { data: maj } = await sb.from("pannes").update({ notifie: true }).eq("id", pa.id).eq("notifie", false).select("id");
          if (!maj || !maj.length) continue;
          const charge = JSON.stringify({ titre: `🔧 ${pa.machine} : en panne`, corps: (pa.description ? pa.description + " — " : "") + "Signalé dans l'appli. La logistique compte sur toi.", url: "https://galianachristian-cpu.github.io/gestion-icp-sdis34/" });
          for (const a of (abos ?? []).filter((x: { pompier_id: number }) => ids.includes(x.pompier_id))) {
            try { await webpush.sendNotification({ endpoint: a.endpoint, keys: { p256dh: a.p256dh, auth: a.auth } }, charge); envoyes++; }
            catch (e) { const code = (e as { statusCode?: number }).statusCode; if (code === 404 || code === 410) { await sb.from("push_abos").delete().eq("id", a.id); retires++; } }
          }
          pannesEnvoyees++;
        }
      }
    }
    return Response.json({ heure: `${parts.hour}:${parts.minute}`, jour, abonnes: (abos ?? []).length, concernes: vus, envoyes, retires, defis: defisEnvoyes, sessions: sessionsEnvoyees, pannes: pannesEnvoyees });
  } catch (e) {
    return Response.json({ erreur: (e as Error).message }, { status: 500 });
  }
});
