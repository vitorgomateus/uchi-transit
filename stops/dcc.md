# DCC — Downtown Campus Connector (UGo / Passio)

**Passio GTFS-RT route ID:** `5704`. Set `"route": "5704"` in your config feed entry.

This is a single-loop route — the bus runs one continuous loop, not a back-and-forth. Stop positions are numbered in loop order. Position 1 was not returned by the Passio API; the loop appears to start at position 2.

---

## Stops (loop order)

| Loop Position | Stop ID | Stop Name |
|---------------|---------|-----------|
| 2 | `8654` | 59th & Ellis |
| 3 | `8612` | Goldblatt Pavilion |
| 4 | `140009` | 55th Street & University |
| 5 | `151794` | S Lake Park & E 53rd St |
| 6 | `155005` | S Lake Park Ave & E Hyde Park Blvd |
| 7 | `132965` | S Michigan Ave/Roosevelt |
| 8 | `155006` | E Randolph St & S Michigan Ave |
| 9 | `132963` | Gleacher Center |
| 10 | `132964` | UCHICAGO Medicine - River East |
| 11 | `151792` | N (Upper) Wacker Dr & W Madison St |
| 12 | `151793` | S (Upper) Wacker Dr & W Adams St |
| 13 | `132967` | UCHICAGO Medicine - South Loop |
| 14 | `132968` | Roosevelt Station |
| 15 | `8591` | Rockefeller Chapel |

---

**Loop routing note:** Stops early in the loop (positions 2–6) may show no ETAs even when buses are running, because all active trips have already passed them in the current lap. Use the `loop_last_stop` + `loop_offset_min` config fields: set `loop_last_stop` to `"8591"` (Rockefeller Chapel, position 15) and measure `loop_offset_min` by riding the route (it varies by traffic). See the README for full details.
