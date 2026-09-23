# Metra Electric District (ME)

Source: Metra public static GTFS at `https://schedules.metrarail.com/gtfs/schedule.zip`.

---

**Setup requirements:**

- API key required — register at [metra.com/metra-gtfs-api](https://metra.com/metra-gtfs-api)
- CORS proxy required (same `worker.js` as CTA, with `gtfspublic.metrarr.com` added to the allowlist)
- Config fields: `"source": "metra"`, `"stop_id": "STOP_ID"`, optionally `"destination_stop_id": "STOP_ID"` to filter by direction

**Direction filtering:** Without `destination_stop_id`, both inbound and outbound trains show at a stop. To see only inbound trains (toward Millennium Station), add `"destination_stop_id": "MILLENNIUM"`. To see only outbound trains (toward University Park), add `"destination_stop_id": "UNIVERSITY"` (or the appropriate branch terminal).

---

## Main Line (University Park branch)

All three branches serve Hyde Park stops. Trains on any branch will appear when configuring those stops.

| Stop ID | Station Name |
|---------|--------------|
| `MILLENNIUM` | Millennium Station (downtown terminus) |
| `VANBUREN` | Van Buren St. |
| `MUSEUM` | Museum Campus/11th St. |
| `18TH-UP` | 18th St. |
| `MCCORMICK` | McCormick Place |
| `27TH-UP` | 27th St. |
| `47TH-UP` | 47th St. (Kenwood) |
| `51ST-53RD` | 51st/53rd St. (Hyde Park) |
| `55-56-57TH` | 55th – 56th – 57th St. |
| `59TH-UP` | 59th St. (U. of Chicago) ← closest to main campus |
| `63RD-UP` | 63rd St. |
| `75TH-UP` | 75th St. (Grand Crossing) |
| `79TH-UP` | 79th St. (Chatham) |
| `83RD-UP` | 83rd St. (Avalon Park) |
| `87TH-UP` | 87th St. (Woodruff) |
| `91ST-UP` | 91st St. |
| `103RD-UP` | 103rd St. (Rosemoor) |
| `107TH-UP` | 107th St. |
| `111TH-UP` | 111th St. (Pullman) |
| `KENSINGTN` | Kensington (branch split point) |
| `RIVERDALE` | Riverdale |
| `IVANHOE` | Ivanhoe |
| `147TH-UP` | 147th St. |
| `HARVEY` | Harvey |
| `HAZELCREST` | Hazel Crest |
| `CALUMET` | Calumet |
| `HOMEWOOD` | Homewood |
| `FLOSSMOOR` | Flossmoor |
| `OLYMPIA` | Olympia Fields |
| `211TH-UP` | 211th St. |
| `MATTESON` | Matteson |
| `RICHTON` | Richton Park |
| `UNIVERSITY` | University Park (south terminus) |

---

## Blue Island Branch

Diverges at Kensington. Does NOT serve 47th–111th St. stations on the main line.

| Stop ID | Station Name |
|---------|--------------|
| `MILLENNIUM` | Millennium Station |
| `VANBUREN` | Van Buren St. |
| `MUSEUM` | Museum Campus/11th St. |
| `51ST-53RD` | 51st/53rd St. (Hyde Park) |
| `55-56-57TH` | 55th – 56th – 57th St. |
| `59TH-UP` | 59th St. (U. of Chicago) |
| `63RD-UP` | 63rd St. |
| `KENSINGTN` | Kensington |
| `STATEST` | State St. |
| `STEWARTRID` | Stewart Ridge |
| `WPULLMAN` | West Pullman |
| `RACINE` | Racine |
| `ASHLAND` | Ashland |
| `BURROAK` | Burr Oak |
| `BLUEISLAND` | Blue Island (west terminus) |

---

## South Chicago Branch

Diverges at 63rd St. Does NOT serve most main line stations south of 63rd.

| Stop ID | Station Name |
|---------|--------------|
| `MILLENNIUM` | Millennium Station |
| `VANBUREN` | Van Buren St. |
| `MUSEUM` | Museum Campus/11th St. |
| `18TH-UP` | 18th St. |
| `MCCORMICK` | McCormick Place |
| `27TH-UP` | 27th St. |
| `47TH-UP` | 47th St. (Kenwood) |
| `51ST-53RD` | 51st/53rd St. (Hyde Park) |
| `55-56-57TH` | 55th – 56th – 57th St. |
| `59TH-UP` | 59th St. (U. of Chicago) |
| `63RD-UP` | 63rd St. (branch split point) |
| `STONYISLND` | Stony Island |
| `BRYNMAWR` | Bryn Mawr |
| `SOUTHSHORE` | South Shore |
| `WINDSORPK` | Windsor Park |
| `79TH-SC` | Cheltenham (79th St.) |
| `83RD-SC` | 83rd St. |
| `87TH-SC` | 87th St. |
| `93RD-SC` | South Chicago (93rd) (east terminus) |

---

**Branch note:** All three branches serve the Hyde Park stops (`51ST-53RD`, `55-56-57TH`, `59TH-UP`), so trains on any branch will appear when configuring those stops. To filter to a specific branch terminal, use `destination_stop_id` set to `UNIVERSITY`, `BLUEISLAND`, or `93RD-SC`.
