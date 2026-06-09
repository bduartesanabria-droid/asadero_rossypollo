var CACHE_NAME = 'rossypollo-v1';
var urlsToCache = [
  '/',
  '/static/css/style.css',
  '/static/js/main.js',
];

self.addEventListener('install', function(event) {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(function(cache) {
        return cache.addAll(urlsToCache);
      })
  );
});

self.addEventListener('fetch', function(event) {
  event.respondWith(
    caches.match(event.request)
      .then(function(response) {
        if (response) return response;
        return fetch(event.request).then(function(response) {
          if (!response || response.status !== 200 || response.type !== 'basic') return response;
          var responseToCache = response.clone();
          caches.open(CACHE_NAME).then(function(cache) {
            if (event.request.method === 'GET') {
              cache.put(event.request, responseToCache);
            }
          });
          return response;
        });
      })
  );
});

self.addEventListener('activate', function(event) {
  event.waitUntil(
    caches.keys().then(function(cacheNames) {
      return Promise.all(
        cacheNames.map(function(cacheName) {
          if (cacheName !== CACHE_NAME) return caches.delete(cacheName);
        })
      );
    })
  );
});
