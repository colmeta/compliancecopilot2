// Register Service Worker for PWA support
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/sw.js')
      .then((registration) => {
        console.log('CLARITY: Service Worker registered successfully:', registration.scope);
      })
      .catch((error) => {
        console.log('CLARITY: Service Worker registration failed:', error);
      });
  });
}
