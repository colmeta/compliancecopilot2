// Register Service Worker for PWA support (with enhanced error handling)
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/sw.js', { scope: '/' })
      .then((registration) => {
        console.log('CLARITY: Service Worker registered successfully:', registration.scope);
        
        // Check for updates periodically
        setInterval(() => {
          registration.update().catch(err => {
            console.warn('CLARITY: Service Worker update check failed:', err);
          });
        }, 60000); // Check every minute
        
        // Handle updates
        registration.addEventListener('updatefound', () => {
          const newWorker = registration.installing;
          if (newWorker) {
            newWorker.addEventListener('statechange', () => {
              if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
                // New service worker available - could notify user here
                console.log('CLARITY: New service worker available');
              }
            });
          }
        });
      })
      .catch((error) => {
        console.error('CLARITY: Service Worker registration failed:', error);
        // Don't break the app if service worker fails
      });
    
    // Handle service worker errors
    navigator.serviceWorker.addEventListener('error', (event) => {
      console.error('CLARITY: Service Worker error:', event.error);
    });
  });
} else {
  console.log('CLARITY: Service Workers not supported in this browser');
}
