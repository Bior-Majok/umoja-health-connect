// Minimal offline support (FR6.2 / NFR08): cache the app shell so previously
// visited pages keep working without a connection, and cache health-education
// API responses so already-viewed content stays available offline.
const SHELL_CACHE = 'umoja-shell-v1';
const API_CACHE = 'umoja-api-v1';

const SHELL_ASSETS = [
  '/', '/style.css', '/app.js', '/i18n.js', '/emergency.js',
  '/index.html', '/register.html', '/dashboard.html', '/appointments.html',
  '/records.html', '/symptom-report.html', '/health-education.html', '/profile-edit.html',
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(SHELL_CACHE).then((cache) => cache.addAll(SHELL_ASSETS)).catch(() => {})
  );
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== SHELL_CACHE && k !== API_CACHE).map((k) => caches.delete(k)))
    )
  );
  self.clients.claim();
});

self.addEventListener('fetch', (event) => {
  const { request } = event;
  if (request.method !== 'GET') return;

  const url = new URL(request.url);

  if (url.pathname.startsWith('/api/health-education')) {
    event.respondWith(
      fetch(request)
        .then((res) => {
          const clone = res.clone();
          caches.open(API_CACHE).then((cache) => cache.put(request, clone));
          return res;
        })
        .catch(() => caches.match(request))
    );
    return;
  }

  if (url.origin === self.location.origin && !url.pathname.startsWith('/api/')) {
    event.respondWith(
      caches.match(request).then((cached) => cached || fetch(request))
    );
  }
});
