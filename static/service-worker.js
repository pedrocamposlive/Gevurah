self.addEventListener('install', event => {
  console.log('[Service Worker] Instalado');
  event.waitUntil(self.skipWaiting());
});

self.addEventListener('activate', event => {
  console.log('[Service Worker] Ativado');
  event.waitUntil(self.clients.claim());
});

self.addEventListener('fetch', event => {
  event.respondWith(fetch(event.request));
});
