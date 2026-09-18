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

### CTA Bus Tracker — proxied via allorigins.win
- API: `https://www.ctabustracker.com/bustime/api/v2/getpredictions`
- No CORS on the API itself; requests go through `https://api.allorigins.win/raw?url=`
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
      "entries": [
        {
          "source": "passio",
          "route_id": "ROUTE_ID",
          "stop_id": "STOP_ID",
          "route_label": "Route Name",
          "stop_name": "Stop Name",
          "stop_lat": 41.7886,
          "stop_lon": -87.5987,
          "group": "optional-shared-key"
        },
        {
          "source": "cta",
          "route": "ROUTE_NUMBER",
          "direction": "Northbound",
          "stop_id": "STOP_ID",
          "stop_label": "Stop Name",
          "group": "optional-shared-key"
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
- `stop_lat` / `stop_lon` — enables vehicle-position ETA for Passio entries. When present, a haversine estimate `[N]` appears beside arrivals ≤ 12 min, showing whether the vehicle is closer or further than the scheduled time suggests.
- `group` — shared string key that collapses multiple entries (even across sources) into one stop card. Useful when a CTA and Passio stop are at the same physical location.

Tab types:
- Default (omit `type`): list of `entries`, each a Passio or CTA stop
- `"type": "cta-spot"`: ad-hoc stop number lookup widget

## Deployment

```bash
git init
git add index.html
git commit -m "Initial commit"
gh repo create uchi-transit --public --push --source .
# Then: GitHub repo Settings → Pages → Branch: main, Folder: / (root)
```
