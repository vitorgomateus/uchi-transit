"""Build schedules.json from CTA's static GTFS feed.

Bus Tracker only predicts a bus once its trip has started, so infrequent routes
(e.g. 192) show nothing until minutes before a bus arrives. The app falls back
to these scheduled times for routes listed here.

Usage:  python tools/build-schedules.py [ROUTE ...]      (default: 192)
        python tools/build-schedules.py --zip google_transit.zip 192 X4

CTA publishes a new feed every few weeks and each one only covers a few months,
so re-run this when the app's debug block reports the schedule has expired.
"""
import argparse, csv, io, json, os, sys, urllib.request, zipfile
from datetime import date

GTFS_URL = 'https://www.transitchicago.com/downloads/sch_data/google_transit.zip'
OUT      = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'schedules.json')


def rows(zf, name):
    with zf.open(name) as f:
        yield from csv.DictReader(io.TextIOWrapper(f, encoding='utf-8-sig'))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('routes', nargs='*', default=['192'])
    ap.add_argument('--zip', help='local google_transit.zip instead of downloading')
    args = ap.parse_args()

    if args.zip:
        zf = zipfile.ZipFile(args.zip)
    else:
        print('Downloading', GTFS_URL, file=sys.stderr)
        with urllib.request.urlopen(GTFS_URL) as res:
            zf = zipfile.ZipFile(io.BytesIO(res.read()))

    routes = set(args.routes)
    trips  = {r['trip_id']: r for r in rows(zf, 'trips.txt') if r['route_id'] in routes}
    svc_ids = {t['service_id'] for t in trips.values()}

    days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
    services = {}
    for r in rows(zf, 'calendar.txt'):
        if r['service_id'] in svc_ids:
            services[r['service_id']] = {
                'days': ''.join(r[d] for d in days), 'start': r['start_date'], 'end': r['end_date'],
                'add': [], 'remove': [],
            }
    for r in rows(zf, 'calendar_dates.txt'):
        if r['service_id'] in svc_ids:
            s = services.setdefault(r['service_id'], {'days': '0000000', 'start': r['date'], 'end': r['date'], 'add': [], 'remove': []})
            s['add' if r['exception_type'] == '1' else 'remove'].append(r['date'])

    print('Reading stop_times.txt', file=sys.stderr)
    by_trip = {}
    for r in rows(zf, 'stop_times.txt'):
        if r['trip_id'] in trips:
            by_trip.setdefault(r['trip_id'], []).append(r)

    # route → stop → [[service_id, "HH:MM", trip id, direction], ...] sorted by time.
    # A trip's last stop is drop-off only (and on loops like 192 it shares a stop ID
    # with the start of the other direction), so it's left out.
    out = {rt: {} for rt in routes}
    for trip_id, sts in by_trip.items():
        t = trips[trip_id]
        sts.sort(key=lambda r: int(r['stop_sequence']))
        for r in sts[:-1]:
            if r.get('pickup_type') == '1':
                continue
            out[t['route_id']].setdefault(r['stop_id'], []).append(
                [t['service_id'], r['departure_time'][:5], t.get('schd_trip_id') or trip_id, t.get('direction', '')])
    for stops in out.values():
        for lst in stops.values():
            lst.sort(key=lambda e: e[1])

    missing = [rt for rt, stops in out.items() if not stops]
    if missing:
        sys.exit('No trips found for route(s): ' + ', '.join(missing))

    with open(OUT, 'w', encoding='utf-8', newline='\n') as f:
        json.dump({'generated': date.today().isoformat(), 'services': services, 'routes': out},
                  f, separators=(',', ':'))
        f.write('\n')
    ends = sorted(s['end'] for s in services.values())
    print(f'Wrote {os.path.normpath(OUT)}: routes {", ".join(sorted(routes))}, valid until {ends[-1]}', file=sys.stderr)


if __name__ == '__main__':
    main()
