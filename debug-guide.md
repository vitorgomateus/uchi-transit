# Debug panel reference

The **Debug** section at the bottom of each tab expands into one collapsible block per data source fetched during the last refresh. **Copy debug info** copies a plain-text snapshot: the time, what each row shows, the tab's config (API keys are not included) and every block below.

---

## Passio TripUpdates (route …) — stops …

Passio's GTFS-RT trip-update feed, filtered down to the routes in the current tab. The label shows the route ID(s) and stop IDs being tracked, e.g. `Passio TripUpdates (route 5704) — stops 132968, 140009`.

```json
{
  "feed_timestamp": 1748000412,
  "fetched_at": "2025-05-23T14:00:12.345Z",
  "matching_trips": 2,
  "trips": [
    {
      "trip_id": "83021547",
      "route_id": "5704",
      "stops": [
        { "stop_id": "132968", "stop_seq": 5, "arr_min": 3,  "dep_min": 3  },
        { "stop_id": "132970", "stop_seq": 6, "arr_min": 8,  "dep_min": 8  },
        { "stop_id": "132975", "stop_seq": 7, "arr_min": 14, "dep_min": 14 }
      ]
    },
    {
      "trip_id": "83021548",
      "route_id": "5704",
      "stops": [
        { "stop_id": "132968", "stop_seq": 5, "arr_min": 21, "dep_min": 21 }
      ]
    }
  ]
}
```

| Field | Meaning |
|---|---|
| `feed_timestamp` | Unix seconds when Passio generated the feed (compare to `fetched_at` to see how stale the data is) |
| `fetched_at` | When the app actually fetched the feed |
| `matching_trips` | Number of active trips on your configured routes |
| `trip_id` | Passio's internal trip identifier (used to match vehicle positions) |
| `route_id` | Matches the `route` value in your config |
| `stop_id` | Matches the `stop_id` value in your config |
| `stop_seq` | Stop's sequence number along the route |
| `arr_min` | Minutes until arrival at that stop (negative = already past; `null` = no arrival time in feed) |
| `dep_min` | Minutes until departure (usually same as `arr_min` for buses) |

**What to check:** If your stop shows no arrivals, look for its `stop_id` in the matching trips list. If the stop_id appears but with a large or negative `arr_min`, the bus has already passed. If your `stop_id` doesn't appear at all in any trip, the route may not be serving that stop in this run.

---

## Passio VehiclePositions (route …)

Live GPS positions for all vehicles on the feed, used to compute the bracketed `[N]` position-based ETA shown alongside scheduled times.

```json
{
  "fetched_at": "2025-05-23T14:00:13.102Z",
  "total_entities": 4,
  "with_position": 4,
  "vehicles": [
    { "trip_id": "83021547", "route_id": "5704", "lat": 41.8901, "lon": -87.6234, "bearing": 180 },
    { "trip_id": "83021548", "route_id": "5704", "lat": 41.9013, "lon": -87.6241, "bearing": 183 },
    { "trip_id": "83021549", "route_id": "5704", "lat": 41.8750, "lon": -87.6228, "bearing":   2 },
    { "trip_id": null,       "route_id": "5704", "lat": 41.8820, "lon": -87.6230, "bearing":  90 }
  ]
}
```

| Field | Meaning |
|---|---|
| `total_entities` | All vehicles in the feed |
| `with_position` | Vehicles that have a GPS fix |
| `trip_id` | Matched against trip updates — `null` means the vehicle isn't linked to a specific trip |
| `bearing` | Heading in degrees (0 = north, 90 = east, 180 = south, 270 = west) |
| `lat` / `lon` | Current GPS coordinates |

**What to check:** If `with_position` is much lower than `total_entities`, some buses aren't reporting GPS. The bracketed ETA in the UI (`[3]`) is computed from the straight-line distance (Haversine) to your stop's `lat`/`lon` divided by 18.5 km/h — it's an estimate, not a schedule. The vehicle label from this feed is shown inline in each arrival chip (e.g. `5·48` = 5 min, vehicle 48).

If the debug block shows an error object instead of position data, the fetch failed — common causes: CORS rejection by Passio's CDN, non-binary response body (HTML error page), or a protobuf decode error. The trip updates and vehicle positions use the same origin, so a CORS failure on one but not the other usually indicates a missing endpoint or a different CDN rule for that path.

---

## CTA (…) — stops …

The CTA Bus Tracker response for every CTA feed in the tab, fetched in one request. The label shows which routes and stop IDs were requested, the prediction count and any error count, e.g. `CTA (192, 4, X4) — stops 316, 1591 — 2, 1 error`.

`errors` is CTA's `error` array. Each entry names the `stpid` and/or `rt` it is about; *No service scheduled* means nothing is running, anything else (e.g. *No data found for parameter*) usually means that route doesn't serve that stop, and the row shows the message. `predictions` holds one object per predicted arrival:

```json
{
  "fetched_at": "2025-05-23T14:00:12.345Z",
  "errors": [
    { "stpid": "1591", "rt": "X4", "msg": "No service scheduled" }
  ],
  "predictions": [
    {
      "tmstmp":      "20250523 14:00",
      "typ":         "A",
      "stpnm":       "Roosevelt & State",
      "stpid":       "316",
      "vid":         "8834",
      "dstp":        1823,
      "rt":          "192",
      "rtdd":        "192",
      "rtdir":       "Southbound",
      "des":         "Roseland",
      "prdtm":       "20250523 14:03",
      "tablockid":   "192 -501",
      "tatripid":    "1072671",
      "origtatripno":"259689263",
      "dly":         false,
      "prdctdn":     "3",
      "zone":        ""
    },
    {
      "tmstmp":      "20250523 14:00",
      "typ":         "A",
      "stpnm":       "Roosevelt & State",
      "stpid":       "316",
      "vid":         "8901",
      "dstp":        9144,
      "rt":          "192",
      "rtdir":       "Southbound",
      "des":         "Roseland",
      "prdtm":       "20250523 14:08",
      "tablockid":   "192 -502",
      "tatripid":    "1072682",
      "origtatripno":"259689271",
      "dly":         true,
      "prdctdn":     "8",
      "zone":        ""
    }
  ]
}
```

| Field | Meaning |
|---|---|
| `prdctdn` | **Minutes to arrival** — the value the app displays. `"DUE"` means ≤ 1 minute |
| `typ` | `A` = arrival prediction, `D` = departure prediction |
| `stpid` | Stop ID — matches `stop_id` in your config |
| `rt` | Route — matches `route` in your config |
| `vid` | Vehicle (bus) number |
| `dstp` | Distance to stop in **feet** |
| `dly` | `true` if the bus is running behind schedule |
| `prdtm` | Predicted arrival timestamp (`YYYYMMDD HH:MM`) |
| `tmstmp` | When the prediction was generated |
| `des` | Destination (headsign) |
| `rtdir` | Direction of travel |

**What to check:** If `predictions` has nothing for your stop + route, look in `errors` for an entry with that `stpid`/`rt`. *No service scheduled* collapses the row; any other message is shown on the row. If `dly` is `true` on everything, the route is running late. Cross-check `dstp` against `prdctdn` — a bus 5,000 ft away predicting arrival in 1 min is probably a GPS glitch.

---

## Schedule (…) — stops …

Timetable times from `schedules.json` for CTA feeds whose route is in that file (built by `tools/build-schedules.py`). Shown only for those routes.

```json
{
  "generated": "2026-10-30",
  "valid_until": "20261130",
  "rows": [
    {
      "route": "192",
      "stop_id": "15164",
      "direction": "Northbound",
      "upcoming": ["15:46 (43 min, trip 38963020)", "16:11 (68 min, trip 8343020)"]
    }
  ]
}
```

| Field | Meaning |
|---|---|
| `generated` | When the file was built |
| `valid_until` | Last date any service in the file covers. After it, a `warning` appears and no times show: rebuild the file |
| `upcoming` | Next five timetable departures today: time, minutes away, GTFS trip ID. This is before any are dropped for a live bus |

**What to check:** a timetable chip should disappear once its bus shows up live. Compare the trip IDs here with `tatripid` in the CTA section. If they match, the app pairs them by ID; if not, it falls back to dropping timetable times within 3 min of a live bus.
