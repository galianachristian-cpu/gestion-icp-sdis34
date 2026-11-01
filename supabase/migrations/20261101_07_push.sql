-- Notifications poussées : abonnements par appareil, envoi par la fonction
-- « envoyer-rappels » déclenchée toutes les 15 minutes par pg_cron.
create extension if not exists pg_net with schema extensions;
create table if not exists public.push_abos (
  id bigint generated always as identity primary key,
  pompier_id integer not null references public.pompiers(id) on delete cascade,
  endpoint text not null unique,
  p256dh text not null,
  auth text not null,
  heure text not null default '18:00',
  jours text not null default '0,2,4',
  actif boolean not null default true,
  dernier_envoi date,
  cree_le timestamptz not null default now()
);
create index if not exists push_abos_pid_idx on public.push_abos (pompier_id);
alter table public.push_abos enable row level security;
create policy "Mes appareils" on public.push_abos for all to authenticated
  using (pompier_id = public.mon_pompier_id_icp())
  with check (pompier_id = public.mon_pompier_id_icp());
create policy "Admin push" on public.push_abos for all to authenticated
  using (public.est_admin_icp()) with check (public.est_admin_icp());

-- Déclenchement (appliqué le 01/11/2026) :
-- select cron.schedule('rappels-seances', '*/15 * * * *',
--   $$select net.http_post(
--       url := 'https://<projet>.supabase.co/functions/v1/envoyer-rappels',
--       headers := '{"Content-Type":"application/json"}'::jsonb)$$);
