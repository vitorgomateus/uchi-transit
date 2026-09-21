# uchi-transit

Personal transit tracker for UChicago commute. Single-file HTML app hosted on GitHub Pages.
The goal is to let you check upcoming ETAs at your most-used stops and routes as fast as possible,
aggregating UChicago shuttle (Passio/UGo) and CTA bus data into one view.
Config is pasted in from a private notes app (not stored in the repo) so API keys and stop preferences stay off GitHub.

## Problem

I need to consult UChicago shuttles and CTAs to decide which to use for which I had to jump between apps. Both google maps and the passio app are map based which is slower then a simple number fetch. I just needed the ETA. And the CTA's text message ETA retrieval is very conveninet, but not when you want to compare two stops, or when you are not there and don't remember the code. 

## Architecture

- **Single file:** `index.html` — no build step, no dependencies beyond a CDN protobufjs script
- **Config:** JSON pasted into the app on first visit → stored in localStorage
- **Hosting:** GitHub Pages (push `index.html` to repo root, enable Pages)
- **To update config:** hit "Config" button in the app header, paste new JSON, hit Load

## Principles
- Must be efficient and fast.
- Must be accessible (WCAG 2.0 AA compliant).
- Must be mobile screen responsive.
- Must have or be in dark mode for outdoor and night usage.
- Must be focused and simple.

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

## Issues

- CTA spot lookup up should not be named "Spot". It was probably a typo introduced somehwere.
- **Manifest PWA load time** — app installed through the manifest is slow to load; investigate whether caching or preloading strategies could help. Might not be just the installed version but the website as well.
- **Route 192 ETAs missing** — route 192 shows no ETAs and the Passio vehicle debug panel is empty; investigate why the GTFS-RT feed is not returning trips for this route despite stop coords being present.
- **Passio vehicle debug empty** — vehicle debug panel appears empty even when stop coordinates are set; the haversine estimate logic may not be matching vehicle positions to the right stops.
- The timer showing the refresh should be next to or on the refresh button.

## Wishlist

- **Intersection stop lookup** — enter a cross-street (e.g. "Michigan and 16th") and get a list of all stops and routes passing through it, without needing to know stop IDs in advance. It probably makes sense to input the line as well, or be able to select a line to further filter, because it will be too noisy. This feature needs to be well thought of, before implementation.
- **Keyboard tab navigation** — arrow keys should move between tabs per the ARIA tabs spec.
- **CTA service alerts** — additional tab pulling from the CTA `getservicebulletins` endpoint; an icon on affected stop cards links to the relevant alert.
- **Long-press shortcuts** — some apps surface shortcuts on long-press of the home screen icon; explore whether the Web App Manifest `shortcuts` key could expose quick-jump actions (e.g. "To Work", "From Work").
- **CTA Spot refresh** — the stop search tab does not re-fetch on repeated requests; tapping Search again produces a fresh pull, but pressing the refresh button should also do it.
- **Placeholder / example config** — ship a minimal placeholder `config.json` (with a "To Work" tab, a "From Work" tab, and the CTA Spot tab) and a link to the GitHub README in the config dialog, so first-time users know what to paste. "To work" will have stop 1591 with line 4 and x4; and aggregated stop 2376 with line 192 and passio stop 132968 with the line "Downtown Campus Connector". "From work" will have stop 15148 with lines 4 and X4, and stop 15164 with lines 4 and 192, and passio stop 140009 with the line "Downtown Campus Connector".
- **Metra Electric** — explore including Metra Electric District train ETAs.
- **Arrival notifications** — "Notify me 5 min before [route] at [stop]" feature using the Notifications + Background Sync APIs. This feature needs to be thought through before implementing.
- **Show IDs next to names** — display stop IDs and vehicle IDs next to their labels and ETAs to aid debugging and config authoring.

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
