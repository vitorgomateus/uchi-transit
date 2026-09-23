# uchi-transit

Personal transit tracker for UChicago commute. Single-file HTML app hosted on GitHub Pages.
The goal is to let you check upcoming ETAs at your most-used stops and routes as fast as possible,
aggregating UChicago shuttle (Passio/UGo) and CTA bus data into one view.
Config is pasted in from a private notes app (not stored in the repo) so API keys and stop preferences stay off GitHub.

## Problem

I need to consult UChicago shuttles and CTAs to decide which to use for which I had to jump between apps. Both google maps and the passio app are map based which is slower then a simple number fetch. I just needed the ETA. And the CTA's text message ETA retrieval is very conveninet, but not when you want to compare two stops, or when you are not there and don't remember the code. 

## Architecture

- **Single file:** `index.html` — no build step; `protobuf.min.js` (protobufjs v7, vendored) is the only dependency and is served from the same origin
- **Config:** JSON pasted into the app on first visit → stored in localStorage under key `transit_cfg`
- **Hosting:** GitHub Pages (push `index.html` to repo root, enable Pages)
- **To update config:** hit "Config" button in the app header, paste new JSON, hit Load
- **localStorage keys:** `transit_cfg` (full config), `transit_stop` (last CTA Stop input), `transit_stops` (saved stops list, JSON array), `transit_tab` (last active tab index + timestamp, restored on load if < 30 min old)
- **Auto-refresh:** fetches on tab switch and every 30 s; pauses automatically when the browser tab is hidden and resumes immediately on visibility
- **Debug panel:** each tab has a collapsible Debug section at the bottom showing the raw parsed feed data for the last refresh — useful for verifying stop IDs and diagnosing missing arrivals. See [debug-guide.md](debug-guide.md) for annotated examples.

## Principles
- Must be efficient and fast.
- Must be accessible (WCAG 2.0 AA compliant).
- Must be mobile screen responsive.
- Must have or be in dark mode for outdoor and night usage.
- Must be focused and simple.

## Data sources

### UGo (Passio) — CORS allowed, no API key needed
- Trip updates: `https://passio3.com/chicago/passioTransit/gtfs/realtime/tripUpdates`
- Vehicle positions: `https://passio3.com/chicago/passioTransit/gtfs/realtime/vehiclePositions` — fetched only when at least one stop has `lat`/`lon` configured. **Currently non-functional:** the endpoint returns 1165 bytes of binary with no `Content-Type` header that fails GTFS-RT protobuf decoding (`index out of range` inside a 74-byte sub-message); the trip updates endpoint works fine. The debug panel surfaces the actual decode error. The `lat`/`lon` config fields and bracketed ETA display are ready for when this is resolved.
- Format: binary protobuf (GTFS-RT), decoded with protobufjs from CDN
- UChicago system ID: `1068`
- **The Passio JSON API (`passiogo.com`) has no CORS — cannot use from browser.** To look up stop IDs from a terminal: POST `https://passiogo.com/mapGetData.php?getStops=2.73` with body `{"s0":"1068","sA":"1"}`. Unofficial API reference: [passiogo.readthedocs.io](https://passiogo.readthedocs.io/en/main/) and [github.com/athuler/PassioGo](https://github.com/athuler/PassioGo).
- **Loop routes and GTFS-RT:** for routes that run as a single loop (one trip per lap), a stop near the start of the loop will only appear as a future stop in a brief window at the beginning of each lap. If a stop reliably shows no ETAs despite active trips on the route, check its position in the loop — a stop at position 4/15 appears far less often than one at position 14/15.

### CTA Bus Tracker — proxied via Cloudflare Worker
- API: `https://www.ctabustracker.com/bustime/api/v2/getpredictions`
- No CORS on the API itself — deploy `worker.js` to Cloudflare Workers (free tier) and set `cta_proxy_url` in config
- Requires a free API key from ctabustracker.com
- JSONP is NOT supported by the CTA API (tested)
- Official developer guide (PDF): [cta_Bus_Tracker_API_Developer_Guide_and_Documentation_20160929.pdf](https://www.transitchicago.com/assets/1/6/cta_Bus_Tracker_API_Developer_Guide_and_Documentation_20160929.pdf)
- **Unlike Passio's GTFS-RT feed, the CTA API is stop-centric:** `getpredictions` answers "what are the next arrivals at this stop?" directly, regardless of where in a route the vehicle currently is. Passio's GTFS-RT is trip-centric: it returns the remaining future stops for currently-running trips, so a stop that is early in a loop route may show no ETAs if all active vehicles have already passed it.

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
            { "source": "passio", "route": "ROUTE_ID", "stop_id": "STOP_ID", "route_label": "Route Name" },
            { "source": "cta", "route": "ROUTE_NUMBER", "stop_id": "STOP_ID", "direction": "Northbound" }
          ]
        }
      ]
    },
    {
      "label": "CTA Stop",
      "type": "cta-stop"
    }
  ]
}
```

Optional fields:
- `cta_proxy_url` — URL of your Cloudflare Worker (see `worker.js`). Falls back to `https://api.allorigins.win/raw` if omitted.
- `lat` / `lon` on a stop — enables vehicle-position ETA for Passio feeds at that stop. A haversine estimate `[N]` appears beside arrivals ≤ 12 min. (Currently non-functional — see Issues.)
- `routes` on a `cta-alerts` tab — array of CTA route numbers to filter bulletins. Omit to fetch all active bulletins.
- `source_label` on a `cta-alerts` tab — badge label on each alert card. Defaults to `"CTA"`. Set to `"UGo"` (or anything else) for a future Passio alerts tab.
- `source_icon` on a `cta-alerts` tab — emoji icon shown in the badge. Auto-detected from `source_label` (`"UGo"` → 🚐, otherwise 🚌); override if needed.
- `loop_last_stop` + `loop_offset_min` on a Passio feed entry — for stops that are early in a loop route and therefore rarely appear as a future stop in the GTFS-RT feed. Set `loop_last_stop` to the stop ID of the last stop on the loop (the stop reliably present in all active trips), and `loop_offset_min` to the travel time in minutes from that last stop back around to your target stop. The app will query the last stop instead and add the offset. Measure `loop_offset_min` from riding the route. Example: `"loop_last_stop": "8591", "loop_offset_min": 7`.
- `group` on a stop — stops sharing the same group string collapse into one card. Useful when a single physical location has different stop IDs across transit systems (e.g. the CTA and Passio stops at Roosevelt Station).
- Multiple CTA feeds with the same `stop_id` in one stop are batched into a single API request.
- `stop_favorites` on the `cta-stop` tab — pre-populate the saved stops list. Merged into localStorage on config load; UI-added stops are appended. Cap is 6 total.

```json
{
  "label": "CTA Stop",
  "type": "cta-stop",
  "stop_favorites": [
    { "id": "2376", "label": "State & Roosevelt" },
    { "id": "14760", "label": "Michigan & 16th NB" }
  ]
}
```

Tab types:
- Default (omit `type`): list of `stops`, each containing a `feeds` array of Passio or CTA entries
- `"type": "cta-stop"`: ad-hoc stop number lookup widget
- `"type": "cta-alerts"`: CTA service bulletins from `getservicebulletins`. Optional `routes` array filters to specific routes; omit for all alerts.

```json
{
  "label": "Alerts",
  "type": "cta-alerts",
  "routes": ["6", "55", "192"]
}
```

### Placeholder / example config

```json
{
  "passio_system_id": 1068,
  "cta_api_key": "YOUR_CTA_KEY",
  "cta_proxy_url": "https://your-worker.workers.dev",
  "tabs": [
    {
      "label": "To Work",
      "stops": [
        {
          "label": "Michigan & 16th",
          "feeds": [
            { "source": "cta", "route": "4",  "stop_id": "1591", "direction": "Southbound" },
            { "source": "cta", "route": "X4", "stop_id": "1591", "direction": "Southbound" }
          ]
        },
        {
          "label": "Roosevelt Station",
          "feeds": [
            { "source": "cta",    "route": "192",  "stop_id": "2376",   "direction": "Southbound" },
            { "source": "passio", "route": "5704", "stop_id": "132968", "route_label": "Downtown Campus Connector" }
          ]
        }
      ]
    },
    {
      "label": "From Work",
      "stops": [
        {
          "label": "Cottage Grove & 55th",
          "feeds": [
            { "source": "cta", "route": "4",  "stop_id": "15148", "direction": "Northbound" },
            { "source": "cta", "route": "X4", "stop_id": "15148", "direction": "Northbound" }
          ]
        },
        {
          "label": "Cottage Grove & 57th",
          "feeds": [
            { "source": "cta", "route": "4",   "stop_id": "15164", "direction": "Northbound" },
            { "source": "cta", "route": "192", "stop_id": "15164", "direction": "Northbound" }
          ]
        },
        {
          "label": "55th & University",
          "feeds": [
            { "source": "passio", "route": "5704", "stop_id": "140009", "route_label": "Downtown Campus Connector" }
          ]
        }
      ]
    },
    {
      "label": "CTA Stop",
      "type": "cta-stop"
    },
    {
      "label": "Alerts",
      "type": "cta-alerts",
      "routes": ["4", "192", "X4"]
    }
  ]
}
```

## Issues

- **Passio vehiclePositions endpoint returns undecodable binary** — the endpoint responds with 1165 bytes of binary with no `Content-Type`, which fails GTFS-RT protobuf decoding. Root cause unknown; may be a different binary format or a Passio server misconfiguration. The bracketed position-based ETA (`[N]`) feature is wired up but non-functional until this is resolved.

### Resolved

- **Route 192 ETAs missing** — the CTA Bus Tracker API caps results at 3 predictions by default when `top` is not set. At stops shared with more-frequent routes (e.g. route 4), those 3 slots fill with the frequent route and 192 is silently omitted from the response. Fixed: batch requests use `top=50`; the CTA Stop tab uses `top=10`.
- **`stop_favorites` silently ignored** — `syncStopFavorites` was reading `tab.spot_favorites` after the localStorage key rename, so pre-populated favorites in the `cta-stop` tab config were never loaded. Fixed: reads `stop_favorites`, falls back to `spot_favorites` for old configs.
- **Passio vehicle positions debug showing `null`** — `fetchPassioVehicles` was swallowing errors with `.catch(() => null)`. Fixed: error is captured and surfaced in the debug block with the response size, content type, and decode message.

## Wishlist

- **Metra Electric** — explore including Metra Electric District train ETAs.
- **Long-press shortcuts** — some apps surface shortcuts on long-press of the home screen icon; explore whether the Web App Manifest `shortcuts` key could expose quick-jump actions (e.g. "To Work", "From Work").
- **Arrival notifications** — "Notify me 5 min before [route] at [stop]" feature using the Notifications + Background Sync APIs. This feature needs to be thought through before implementing.
- **Intersection stop lookup** — enter a cross-street (e.g. "Michigan and 16th") and get a list of all stops and routes passing through it, without needing to know stop IDs in advance. It probably makes sense to input the line as well, or be able to select a line to further filter, because it will be too noisy. This feature needs to be well thought of, before implementation.

## Abandoned

- **PWA / offline** — service worker caches the last good arrival data so the app shows something useful instead of errors when offline. The website's purpose is to consutl live data. It has no purpose working offline.
- **CTA Train Tracker** — L train ETAs via the CTA Train Tracker API (same proxy, different endpoint); same stop/feed schema would accommodate it cleanly. CTA L trains come frequently, nobody checks when is the next one, you just go to the stop and get one.

## Deployment

```bash
git init
git add index.html
git commit -m "Initial commit"
gh repo create uchi-transit --public --push --source .
# Then: GitHub repo Settings → Pages → Branch: main, Folder: / (root)
```
