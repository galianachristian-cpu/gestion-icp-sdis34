-- Réglages du diplôme de fin de défi (titre, phrases, signature, podium).
-- Vide = textes par défaut. Lecture / écriture : mêmes règles que le reste de la table defis.
alter table public.defis add column if not exists diplome jsonb;
comment on column public.defis.diplome is 'Réglages du diplôme de fin de défi (titre, phrases, signature, podium). Vide = textes par défaut.';
