/* Mon Programme : service worker pour l'installation et l'usage hors ligne */
const CACHE = 'icp-sport-v1';
const CORE = ['./', './index.html', './manifest.webmanifest', './icon-192-v2.png', './icon-512-v2.png', './apple-touch-icon-v2.png', './garage-icon.png'];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => Promise.all(CORE.map(u => c.add(new Request(u, { cache: 'reload' })).catch(() => {})))).then(() => self.skipWaiting()));
});
self.addEventListener('activate', e => {
  e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== CACHE).map(k => caches.delete(k)))).then(() => self.clients.claim()));
});
self.addEventListener('fetch', e => {
  const req = e.request, url = new URL(req.url);
  if (req.method !== 'GET') return;
  // on ne gère que le dossier sport/ : le reste appartient à l'appli ICP
  if (url.origin === location.origin && !url.pathname.includes('/sport/')) return;
  // vidéo anti-veille : Safari la lit par morceaux, on la laisse au réseau
  if (/\.(mp4|webm)$/.test(url.pathname)) return;
  // page : réseau d'abord (toujours la dernière version), sinon la copie gardée
  if (req.mode === 'navigate' || (url.origin === location.origin && url.pathname.endsWith('.html'))){
    e.respondWith(fetch(req).then(r => { const c = r.clone(); caches.open(CACHE).then(x => x.put('./index.html', c)); return r; }).catch(() => caches.match('./index.html').then(r => r || caches.match('./'))));
    return;
  }
  // scripts Firebase, police et lecteur d'écran (versions fixes) : copie gardée d'abord
  if (url.hostname === 'www.gstatic.com' || url.hostname === 'fonts.googleapis.com' || url.hostname === 'fonts.gstatic.com' || (url.hostname === 'cdn.jsdelivr.net' && /tesseract/.test(url.pathname))){
    e.respondWith(caches.match(req).then(hit => hit || fetch(req).then(r => { const c = r.clone(); caches.open(CACHE).then(x => x.put(req, c)); return r; })));
    return;
  }
  // fichiers du site : copie gardée, mise à jour en arrière-plan
  if (url.origin === location.origin){
    e.respondWith(caches.match(req).then(hit => { const net = fetch(req).then(r => { const c = r.clone(); caches.open(CACHE).then(x => x.put(req, c)); return r; }).catch(() => hit); return hit || net; }));
  }
  // le reste (base Firestore, images externes) passe directement au réseau
});

// clic sur une notification de rappel : on rouvre l'appli
self.addEventListener('notificationclick', e => {
  e.notification.close();
  e.waitUntil(self.clients.matchAll({ type: 'window', includeUncontrolled: true }).then(cs => {
    const c = cs.find(x => 'focus' in x);
    return c ? c.focus() : self.clients.openWindow((e.notification.data && e.notification.data.url) || './');
  }));
});

/* Notifications poussées : affichage et ouverture de l'appli au clic. */
self.addEventListener('push', e => {
  let d = {};
  try { d = e.data ? e.data.json() : {}; } catch (err) { d = { titre: 'Rappel', corps: e.data ? e.data.text() : '' }; }
  e.waitUntil(self.registration.showNotification(d.titre || 'Rappel', {
    body: d.corps || '',
    icon: './icon-192-v2.png',
    badge: './icon-192-v2.png',
    tag: 'rappel-seance',
    data: { url: d.url || './index.html' }
  }));
});
self.addEventListener('notificationclick', e => {
  e.notification.close();
  const cible = (e.notification.data && e.notification.data.url) || './index.html';
  e.waitUntil(clients.matchAll({ type: 'window', includeUncontrolled: true }).then(l => {
    for (const c of l) { if ('focus' in c) return c.focus(); }
    return clients.openWindow(cible);
  }));
});
