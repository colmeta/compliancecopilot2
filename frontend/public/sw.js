// CLARITY Engine - Service Worker (PWA Support)
const CACHE_NAME = 'clarity-v2';
const urlsToCache = [
  '/',
  '/work',
  '/funding',
  '/docs',
];

// Install event - cache critical assets (with error handling)
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        console.log('CLARITY: Cache opened');
        // Cache each URL individually to prevent one failure from breaking all
        return Promise.allSettled(
          urlsToCache.map(url => 
            cache.add(url).catch(err => {
              console.warn(`CLARITY: Failed to cache ${url}:`, err);
              return null; // Continue even if one fails
            })
          )
        );
      })
      .catch((err) => {
        console.error('CLARITY: Cache installation failed:', err);
        // Don't fail the installation - continue anyway
      })
  );
  self.skipWaiting();
});

// Activate event - cleanup old caches
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName !== CACHE_NAME) {
            console.log('CLARITY: Deleting old cache:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
  self.clients.claim();
});

// Fetch event - network first, then cache (with error handling)
self.addEventListener('fetch', (event) => {
  // Only handle GET requests
  if (event.request.method !== 'GET') {
    return;
  }
  
  // Skip non-HTTP requests (like chrome-extension://)
  if (!event.request.url.startsWith('http')) {
    return;
  }
  
  event.respondWith(
    fetch(event.request)
      .then((response) => {
        // Only cache successful responses
        if (response && response.status === 200) {
          // Clone the response before caching
          const responseToCache = response.clone();
          
          // Cache in background (don't wait for it)
          caches.open(CACHE_NAME)
            .then((cache) => {
              cache.put(event.request, responseToCache).catch(err => {
                console.warn('CLARITY: Failed to cache response:', err);
              });
            })
            .catch(err => {
              console.warn('CLARITY: Cache open failed:', err);
            });
        }
        
        return response;
      })
      .catch((err) => {
        // If network fails, try cache
        return caches.match(event.request)
          .then((cachedResponse) => {
            if (cachedResponse) {
              return cachedResponse;
            }
            // If no cache, return a basic offline page or error
            return new Response('Offline - Please check your connection', {
              status: 503,
              statusText: 'Service Unavailable',
              headers: { 'Content-Type': 'text/plain' }
            });
          })
          .catch(() => {
            // Final fallback
            return new Response('Offline', {
              status: 503,
              statusText: 'Service Unavailable'
            });
          });
      })
  );
});
