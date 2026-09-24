# uchi-transit

Personal transit tracker for UChicago commute. Single-file HTML app hosted on GitHub Pages.
The goal is to let you check upcoming ETAs at your most-used stops and routes as fast as possible,
aggregating UChicago shuttle (Passio/UGo) and CTA bus data into one view.
Config is pasted in from a private notes app (not stored in the repo) so API keys and stop preferences stay off GitHub.

## Disclaimer

This project is not sponsored by, affiliated with, or operated by the Chicago Transit Authority (CTA), Metra, UChicago Transportation / UGo, Passio Technologies, or the University of Chicago. It fetches publicly available data from their APIs for personal use only.

**This app shows arrival time estimates only — it is not a wayfinding tool.** It does not plan routes, suggest which bus or train to take, or tell you where to go. For route planning, use the [CTA trip planner](https://www.transitchicago.com/travel-information/), [Metra schedules](https://metra.com/schedules), the Passio GO app, or Google Maps. You need to already know which stops and lines are relevant to your commute before configuring this app.

## Problem

I need to consult UChicago shuttles and CTAs to decide which to use for which I had to jump between apps. Both google maps and the passio app are map based which is slower then a simple number fetch. I just needed the ETA. And the CTA's text message ETA retrieval is very conveninet, but not when you want to compare two stops, or when you are not there and don't remember the code. 

## Architecture

- **Single file:** `index.html` — no build step; `protobuf.min.js` (protobufjs v7, vendored) is the only dependency and is served from the same origin
- **Config:** JSON pasted into the app on first visit → stored in localStorage under key `transit_cfg`
- **Hosting:** GitHub Pages (push `index.html` to repo root, enable Pages)
- **To update config:** hit "Config" button in the app header, paste new JSON, hit Load
- **localStorage keys:** `transit_cfg` (full config), `transit_stops` (saved stops list, JSON array), `transit_tab` (last active tab index + timestamp, restored on load if < 30 min old)
- **Auto-refresh:** fetches on tab switch and every 30 s; pauses automatically when the browser tab is hidden and resumes immediately on visibility
- **Debug panel:** each tab has a collapsible Debug section at the bottom showing the raw parsed feed data for the last refresh — useful for verifying stop IDs and diagnosing missing arrivals. See [debug-guide.md](debug-guide.md) for annotated examples.

## Principles
- Must be efficient and fast.
- Must be accessible (WCAG 2.0 AA compliant).
- Must be mobile screen responsive.
- Must have or be in dark mode for outdoor and night usage. Optimized for OLED: page and card backgrounds are pure black (`#000`); cards are separated by a border rather than a fill.
- Must be focused and simple.

## Stop IDs and route codes

The `stops/` folder has full stop tables (sourced from public GTFS feeds) for each line:

- [stops/route-4-x4.md](stops/route-4-x4.md) — CTA routes 4 and X4 (Cottage Grove / Cottage Grove Express)
- [stops/route-192.md](stops/route-192.md) — CTA route 192 (University of Chicago Hospitals Express)
- [stops/dcc.md](stops/dcc.md) — Downtown Campus Connector (UGo / Passio)
- [stops/metra-electric.md](stops/metra-electric.md) — Metra Electric District (all three branches)

## Data sources

### UGo (Passio) — CORS allowed, no API key needed
- Trip updates: `https://passio3.com/chicago/passioTransit/gtfs/realtime/tripUpdates`
- Vehicle positions: `https://passio3.com/chicago/passioTransit/gtfs/realtime/vehiclePositions` — fetched only when at least one stop has `lat`/`lon` configured. **Currently non-functional:** the endpoint returns 1165 bytes of binary with no `Content-Type` header that fails GTFS-RT protobuf decoding (`index out of range` inside a 74-byte sub-message); the trip updates endpoint works fine. The debug panel surfaces the actual decode error. The `lat`/`lon` config fields and bracketed ETA display are ready for when this is resolved.
- Format: binary protobuf (GTFS-RT), decoded with protobufjs from CDN
- UChicago system ID: `1068`
- **The Passio JSON API (`passiogo.com`) has no CORS — cannot use from browser.** To look up stop IDs from a terminal: POST `https://passiogo.com/mapGetData.php?getStops=2.73` with body `{"s0":"1068","sA":"1"}`. Unofficial API reference: [passiogo.readthedocs.io](https://passiogo.readthedocs.io/en/main/) and [github.com/athuler/PassioGo](https://github.com/athuler/PassioGo).
- **Loop routes and GTFS-RT:** for routes that run as a single loop (one trip per lap), a stop near the start of the loop will only appear as a future stop in a brief window at the beginning of each lap. If a stop reliably shows no ETAs despite active trips on the route, check its position in the loop — a stop at position 4/15 appears far less often than one at position 14/15.

### Metra Electric — proxied via Cloudflare Worker
- Trip updates: `https://gtfspublic.metrarr.com/gtfs/public/tripupdates?api_token=KEY`
- No CORS — requires the same Cloudflare Worker proxy as CTA (`worker.js`). Add `gtfspublic.metrarr.com` to the worker's allowlist (one line, already included in the repo's `worker.js`).
- Requires a free API key from [metra.com/metra-gtfs-api](https://metra.com/metra-gtfs-api) — license requires a non-affiliation disclaimer (see above) and routing data through a developer-owned proxy (satisfied by `worker.js`).
- Format: binary GTFS-RT protobuf — same `FeedMessage` schema as Passio
- **Direction filtering** via `destination_stop_id`: checks whether the destination stop appears *after* the target stop in each trip's remaining stops. No static GTFS lookup needed.
- Stop IDs: see [stops/metra-electric.md](stops/metra-electric.md)

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
  "metra_api_key": "YOUR_METRA_KEY",
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
            { "source": "cta", "route": "ROUTE_NUMBER", "stop_id": "STOP_ID", "direction": "Northbound" },
            { "source": "metra", "stop_id": "STOP_ID", "destination_stop_id": "TERMINUS_STOP_ID", "route_label": "ME → Millennium" }
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
- `cta_proxy_url` — URL of your Cloudflare Worker (see `worker.js`). Falls back to `https://api.allorigins.win/raw` if omitted. **Required for Metra** (binary protobuf — allorigins.win may corrupt binary responses).
- `metra_api_key` — API key for `gtfspublic.metrarr.com`. Free; register at [metra.com/metra-gtfs-api](https://metra.com/metra-gtfs-api). Required only if any tab has a `"source": "metra"` feed.
- `lat` / `lon` on a stop — enables vehicle-position ETA for Passio feeds at that stop. A haversine estimate `[N]` appears beside arrivals ≤ 12 min. (Currently non-functional — see Issues.)
- `routes` on a `cta-alerts` tab — array of CTA route numbers to filter bulletins. Omit to fetch all active bulletins.
- `source_label` on a `cta-alerts` tab — badge label on each alert card. Defaults to `"CTA"`. Set to `"UGo"` (or anything else) for a future Passio alerts tab.
- `source_icon` on a `cta-alerts` tab — emoji icon shown in the badge. Auto-detected from `source_label` (`"UGo"` → 🚐, otherwise 🚌); override if needed.
- `loop_last_stop` + `loop_offset_min` on a Passio feed entry — for stops that are early in a loop route and therefore rarely appear as a future stop in the GTFS-RT feed. Set `loop_last_stop` to the stop ID of the last stop on the loop (the stop reliably present in all active trips), and `loop_offset_min` to the travel time in minutes from that last stop back around to your target stop. The app will query the last stop instead and add the offset. Measure `loop_offset_min` from riding the route. Example: `"loop_last_stop": "8591", "loop_offset_min": 7`.
- `destination_stop_id` on a `metra` feed entry — filters by direction. Only trips that still have this stop in their future stops (after the target stop) are shown. Use `"MILLENNIUM"` for inbound trains and `"UNIVERSITY"`, `"BLUEISLAND"`, or `"93RD-SC"` for outbound by branch. Omit to show both directions.
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
- `"type": "cta-stop"`: ad-hoc stop lookup widget. The search input accepts a stop ID (any number, e.g. `316`, `14760`) or a route code (e.g. `4`, `X9`, `192`). Letter-containing input is treated as a route code only; pure-digit input fires both APIs in parallel — direction pills appear if the number is a valid route, ETA cards appear if it is a valid stop, and both can appear simultaneously if the number happens to be both.
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
        },
        {
          "label": "55th–57th Metra Station",
          "feeds": [
            { "source": "metra", "stop_id": "55-56-57TH", "destination_stop_id": "MILLENNIUM", "route_label": "ME → Millennium" }
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
- **No-service dash contrast** — the `—` shown for a route with no service (`.no-arr`, `#3a3a3c` on `#000`) is 1.85:1. Screen readers get "No service" from visually-hidden text, but the visible glyph is below the WCAG 1.4.3 text threshold.

### Resolved

- **Accessibility pass (WCAG 2.0 AA)**:
  - **Pinch zoom:** removed `maximum-scale=1` from the viewport meta (1.4.4).
  - **Text contrast:** tertiary greys raised to ≥ 4.5:1 against their actual background: `#78787c` on `#000` (4.78:1) and `#98989d` on `#2c2c2e` chips and inputs (4.85:1). The affected elements are direction labels, `[N]` ETAs, status text, stop IDs, the filter placeholder and the × remove button. Filled blue buttons use `#0066e0` so white text is 5.28:1; `#0a84ff` was 3.65:1.
  - **Stop list roles:** `role="listitem"` moved off the stop-list `<button>` onto a wrapper `div`, so the button keeps its role. The "No matching stops" message is no longer inside a `role="list"`.
  - **Arrival text for screen readers:** arrival rows carry their summary ("Due, 4 min, 14 min") as visually-hidden text instead of `aria-label` on a generic `div`. The direction pill row is `role="group"`. CTA Stop results previously had no text alternative for the `aria-hidden` chips and now use the same summary.
  - **Quieter announcements:** arrival rows, alerts, stop results and the stop list are no longer `aria-live`, so the 30s auto-refresh is silent. A single `role="status"` region announces "Arrivals updated" or "Alerts updated" after the refresh button, a short summary after a stop lookup, and the match count while filtering stops (debounced).
  - **Reduced motion:** a `prefers-reduced-motion` guard disables transitions and the refresh button press animation.

- **Route-code search on the CTA Stop tab** — the search input now accepts a route code in addition to a stop ID. For pure-digit input both `getdirections` and `getpredictions` fire in parallel (a number like `316` is a valid stop ID but could also be a route); direction pills appear if a matching route is found, ETA cards appear if a matching stop is found. Letter-containing input (e.g. `X4`) is route-only. Stop list responses are cached for 5 minutes to avoid redundant API calls when toggling directions.

- **Route 192 ETAs missing** — the CTA Bus Tracker API caps results at 3 predictions by default when `top` is not set. At stops shared with more-frequent routes (e.g. route 4), those 3 slots fill with the frequent route and 192 is silently omitted from the response. Fixed: batch requests use `top=50`; the CTA Stop tab uses `top=10`.
- **`stop_favorites` silently ignored** — `syncStopFavorites` was reading `tab.spot_favorites` after the localStorage key rename, so pre-populated favorites in the `cta-stop` tab config were never loaded. Fixed: reads `stop_favorites`, falls back to `spot_favorites` for old configs.
- **Passio vehicle positions debug showing `null`** — `fetchPassioVehicles` was swallowing errors with `.catch(() => null)`. Fixed: error is captured and surfaced in the debug block with the response size, content type, and decode message.

## Wishlist

- **Metra Electric direction label** — when no `destination_stop_id` is set and both inbound and outbound trains appear, the display doesn't distinguish direction. Could show the train headsign (e.g. "→ Millennium" / "→ University Park") if the GTFS-RT feed includes it, or derive it from the trip ID pattern.
- **Long-press shortcuts** — some apps surface shortcuts on long-press of the home screen icon; explore whether the Web App Manifest `shortcuts` key could expose quick-jump actions (e.g. "To Work", "From Work").
- **Arrival notifications** — "Notify me 5 min before [route] at [stop]" feature using the Notifications + Background Sync APIs. This feature needs to be thought through before implementing.

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
