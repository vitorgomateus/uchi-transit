# uchi-transit

Personal transit tracker for UChicago commute. Single-file HTML app hosted on GitHub Pages.
Shows UGo shuttle ETAs and CTA bus arrivals. Config is pasted in from a private notes app
(not stored in the repo) so API keys and stop preferences stay off GitHub.

## Architecture

- **Single file:** `index.html` — no build step, no dependencies beyond a CDN protobufjs script
- **Config:** JSON pasted into the app on first visit → stored in localStorage
- **Hosting:** GitHub Pages (push `index.html` to repo root, enable Pages)
- **To update config:** hit "Config" button in the app header, paste new JSON, hit Load

## Data sources

### UGo (Passio) — CORS allowed, no API key needed
- Feed: `https://passio3.com/chicago/passioTransit/gtfs/realtime/tripUpdates`
- Format: binary protobuf (GTFS-RT), decoded with protobufjs from CDN
- UChicago system ID: `1068`
- **The Passio JSON API (`passiogo.com`) has no CORS — cannot use from browser**

### CTA Bus Tracker — proxied via Cloudflare Worker
- API: `https://www.ctabustracker.com/bustime/api/v2/getpredictions`
- No CORS on the API itself — deploy `worker.js` to Cloudflare Workers (free tier) and set `cta_proxy_url` in config
- Requires a free API key from ctabustracker.com
- JSONP is NOT supported by the CTA API (tested)

## Config JSON format

```json
{
  "passio_system_id": 1068,
  "cta_api_key": "YOUR_KEY_HERE",
  "cta_proxy_url": "https://your-worker.workers.dev",
  "tabs": [
    {
      "label": "Tab Name",
      "stops": [
        {
          "label": "Stop Name",
          "lat": 41.7886,
          "lon": -87.5987,
          "feeds": [
            { "source": "passio", "route_id": "ROUTE_ID", "stop_id": "STOP_ID", "route_label": "Route Name" },
            { "source": "cta", "route": "ROUTE_NUMBER", "stop_id": "STOP_ID", "direction": "Northbound" }
          ]
        }
      ]
    },
    {
      "label": "CTA Spot",
      "type": "cta-spot"
    }
  ]
}
```

Optional fields:
- `cta_proxy_url` — URL of your Cloudflare Worker (see `worker.js`). Falls back to `allorigins.win` if omitted.
- `lat` / `lon` on a stop — enables vehicle-position ETA for Passio feeds at that stop. A haversine estimate `[N]` appears beside arrivals ≤ 12 min.
- Multiple CTA feeds with the same `stop_id` in one stop are batched into a single API request.
- `spot_favorites` on the `cta-spot` tab — pre-populate the saved stops list. Merged into localStorage on config load; UI-added stops are appended. Cap is 6 total.

```json
{
  "label": "CTA Spot",
  "type": "cta-spot",
  "spot_favorites": [
    { "id": "2376", "label": "State & Roosevelt" },
    { "id": "14760", "label": "Michigan & 16th NB" }
  ]
}
```

Tab types:
- Default (omit `type`): list of `stops`, each containing a `feeds` array of Passio or CTA entries
- `"type": "cta-spot"`: ad-hoc stop number lookup widget

## Wishlist

- **Intersection stop lookup** — enter a cross-street (e.g. "Michigan and 16th") and get a list of all stops and routes passing through it, without needing to know stop IDs in advance.
- **Keyboard tab navigation** — arrow keys should move between tabs per the ARIA tabs spec.
- **Stale data indicator** — show a "updated N min ago" badge when the last refresh errored, so you know displayed times might be old.
- **CTA service alerts** — additional tab pulling from the CTA `getservicebulletins` endpoint; an icon on affected stop cards links to the relevant alert.
- **PWA / offline** — service worker caches the last good arrival data so the app shows something useful instead of errors when offline.
- **CTA Train Tracker** — L train ETAs via the CTA Train Tracker API (same proxy, different endpoint); same stop/feed schema would accommodate it cleanly.

## Deployment

```bash
git init
git add index.html
git commit -m "Initial commit"
gh repo create uchi-transit --public --push --source .
# Then: GitHub repo Settings → Pages → Branch: main, Folder: / (root)
```
