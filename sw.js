// Service worker de Gestion ICP : rend l'appli installable et accélère les
// ouvertures suivantes. Les données (Supabase) ne passent JAMAIS par le cache.
const VERSION = 'icp-v4';
const COQUILLE = ['./', 'index.html', 'manifest.webmanifest'];

self.addEventListener('install', (e) => {
  e.waitUntil(caches.open(VERSION).then((c) => c.addAll(COQUILLE)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', (e) => {
  e.waitUntil(
    caches.keys()
      .then((cles) => Promise.all(cles.filter((k) => k !== VERSION).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (e) => {
  const req = e.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  if (url.hostname.endsWith('supabase.co')) return; // données : toujours en direct

  // Page : réseau d'abord (pour avoir toujours la dernière version), cache si hors ligne.
  if (req.mode === 'navigate') {
    e.respondWith(
      fetch(req)
        .then((r) => { const copie = r.clone(); caches.open(VERSION).then((c) => c.put('index.html', copie)); return r; })
        .catch(() => caches.match('index.html'))
    );
    return;
  }

  // Photos, icônes et bibliothèques (versions figées) : cache d'abord.
  const memeSite = url.origin === self.location.origin;
  const cdn = url.hostname === 'cdn.jsdelivr.net' || url.hostname === 'cdnjs.cloudflare.com';
  if (memeSite || cdn) {
    e.respondWith(
      caches.match(req).then((enCache) => enCache || fetch(req).then((r) => {
        if (r.ok) { const copie = r.clone(); caches.open(VERSION).then((c) => c.put(req, copie)); }
        return r;
      }))
    );
  }
});
