// Edge Function « gerer-comptes » : création / mise à jour / suppression des
// comptes secondaires de l'appli Gestion ICP. Appelée depuis l'onglet Comptes.
// Seule cette fonction détient la clé de service (fournie automatiquement par
// Supabase) : l'appli elle-même ne peut jamais créer de compte ni lire un mot
// de passe. L'appelant doit être administrateur (fonction SQL est_admin_icp()).
import { createClient } from "npm:@supabase/supabase-js@2";

const cors = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
  "Access-Control-Allow-Methods": "POST, OPTIONS",
};

const ONGLETS = ["dashboard", "synthese", "fiche", "saisie", "terrain", "bilan", "progression", "cardio", "muscu", "seances", "echelles", "ppa", "export"];

function reponse(status: number, body: unknown) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { ...cors, "Content-Type": "application/json" },
  });
}

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") return new Response("ok", { headers: cors });
  if (req.method !== "POST") return reponse(405, { error: "Méthode non autorisée" });

  const url = Deno.env.get("SUPABASE_URL")!;
  const anon = Deno.env.get("SUPABASE_ANON_KEY")!;
  const service = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;

  // 1) Qui appelle ? (client avec le jeton de l'utilisateur connecté)
  const appelant = createClient(url, anon, {
    global: { headers: { Authorization: req.headers.get("Authorization") ?? "" } },
  });
  const { data: u } = await appelant.auth.getUser();
  if (!u?.user) return reponse(401, { error: "Non connecté" });
  const { data: estAdmin, error: errAdmin } = await appelant.rpc("est_admin_icp");
  if (errAdmin || estAdmin !== true) return reponse(403, { error: "Réservé à l'administrateur" });

  let body: { action?: string; email?: string; password?: string | null; onglets?: unknown; pompier_id?: unknown };
  try {
    body = await req.json();
  } catch {
    return reponse(400, { error: "Requête invalide" });
  }
  const email = (body.email ?? "").toString().trim().toLowerCase();
  if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) return reponse(400, { error: "Email invalide" });
  if (email === (u.user.email ?? "").toLowerCase()) {
    return reponse(400, { error: "Ton propre compte se gère avec le bouton « Mot de passe »" });
  }

  const admin = createClient(url, service, { auth: { persistSession: false, autoRefreshToken: false } });

  // Recherche du compte Auth par email (peu de comptes : une page suffit).
  const { data: liste, error: errListe } = await admin.auth.admin.listUsers({ page: 1, perPage: 1000 });
  if (errListe) return reponse(500, { error: errListe.message });
  const existant = liste.users.find((x) => (x.email ?? "").toLowerCase() === email);

  if (body.action === "supprimer") {
    if (existant) {
      const { error } = await admin.auth.admin.deleteUser(existant.id);
      if (error) return reponse(500, { error: error.message });
    }
    const { error } = await admin.from("comptes_app").delete().eq("email", email);
    if (error) return reponse(500, { error: error.message });
    await admin.from("mdp_provisoires").delete().eq("email", email);
    return reponse(200, { ok: true });
  }

  if (body.action === "enregistrer") {
    const password = body.password ? body.password.toString() : "";
    if (password && password.length < 8) return reponse(400, { error: "Mot de passe : 8 caractères minimum" });
    // Compte relié à un pompier : toujours sa fiche ; avec seulement « fiche », il ne voit que
    // sa ligne (la base filtre aussi). D'autres onglets (ex. vue chef) en font un compte d'équipe.
    const pompierId = Number.isInteger(body.pompier_id) ? (body.pompier_id as number) : null;
    const demandes = Array.isArray(body.onglets)
      ? body.onglets.filter((o): o is string => typeof o === "string" && ONGLETS.includes(o))
      : [];
    const onglets = pompierId !== null ? Array.from(new Set(["fiche", ...demandes])) : demandes;

    if (!existant) {
      if (!password) return reponse(400, { error: "Mot de passe obligatoire pour un nouveau compte" });
      const { error } = await admin.auth.admin.createUser({ email, password, email_confirm: true });
      if (error) return reponse(500, { error: error.message });
    } else if (password) {
      const { error } = await admin.auth.admin.updateUserById(existant.id, { password });
      if (error) return reponse(500, { error: error.message });
    }
    const { error } = await admin.from("comptes_app").upsert({ email, onglets, pompier_id: pompierId }, { onConflict: "email" });
    if (error) return reponse(500, { error: error.message });
    // Mot de passe provisoire : visible par l'admin jusqu'à ce que la personne choisisse le sien
    if (password) {
      await admin.from("mdp_provisoires").upsert(
        { email, mot_de_passe: password, cree_le: new Date().toISOString(), personnalise_le: null },
        { onConflict: "email" },
      );
    }
    return reponse(200, { ok: true, cree: !existant });
  }

  return reponse(400, { error: "Action inconnue" });
});
