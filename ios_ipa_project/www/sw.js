const CACHE_NAME = "minh-phu-hvac-v20261124-5";
const CORE_ASSETS = [
  "./",
  "./index.html",
  "./manifest.json",
  "./css/styles.css?v=20261124_5",
  "./js/data.js?v=20261124_5",
  "./js/app.js?v=20261124_5",
  "./js/quote.js?v=20261124_5",
  "./js/hvac_pro.js?v=20261124_5",
  "./assets/fonts/NotoSans-Regular.ttf",
  "./assets/fonts/NotoSans-Bold.ttf",
  "./assets/logo_minh_phu.png",
  "./assets/app_icon.png"
];

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(CORE_ASSETS)).then(() => self.skipWaiting())
  );
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE_NAME).map((k) => caches.delete(k)))
    ).then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", (event) => {
  if (event.request.method !== "GET" || event.request.url.includes("/api/")) return;
  event.respondWith(
    caches.match(event.request).then((cached) =>
      cached || fetch(event.request).then((resp) => {
        if (resp && resp.status === 200 && resp.type === "basic") {
          const copy = resp.clone();
          caches.open(CACHE_NAME).then((cache) => cache.put(event.request, copy));
        }
        return resp;
      }).catch(() => cached)
    )
  );
});
