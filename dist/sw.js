// Orion PWA — minimal offline app-shell cache.
const CACHE = "orion-v4-16";
const SHELL = ["./", "./index.html", "./manifest.webmanifest", "./app-icon-180.png", "./app-icon-512.png", "./ngsl_gloss.json", "./LICENSE.txt", "./donate.png"];

self.addEventListener("install", (e) => {
  e.waitUntil((async () => {
    const c = await caches.open(CACHE);
    await Promise.allSettled(SHELL.map((u) => c.add(u)));
  })());
});

// Activate a waiting SW only when the user opts in via the in-app "刷新" button.
self.addEventListener("message", (e) => {
  if(e.data && e.data.type === "SKIP_WAITING") self.skipWaiting();
});

self.addEventListener("activate", (e) => {
  e.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k)))
    ).then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", (e) => {
  const req = e.request;
  if (req.method !== "GET" || new URL(req.url).origin !== self.location.origin) return;
  // SPA navigations -> cached index.html
  if (req.mode === "navigate") {
    e.respondWith(
      fetch(req)
        .then((res) => {
          // only cache real HTML navigations as the app shell — guard against non-HTML
          // responses (e.g. a <a download> to ngsl_gloss.json) that Chromium dispatches as 'navigate'
          const ct = res.headers.get('content-type') || '';
          if(res.ok && !res.redirected && res.type==='basic' && ct.includes('text/html')){ const copy = res.clone(); caches.open(CACHE).then((c) => c.put("./index.html", copy)); }
          return res;
        })
        .catch(() => caches.match(req).then((r) => r || caches.match("./index.html").then((r2) => r2 || caches.match("./"))))
    );
    return;
  }
  // cache-first for shell assets
  e.respondWith(
    caches.match(req).then((cached) => cached || fetch(req).then((res) => {
      if(res.ok && res.status===200 && res.type==='basic'){ const copy = res.clone(); caches.open(CACHE).then((c) => c.put(req, copy)); }
      return res;
    }).catch(() => cached))
  );
});
