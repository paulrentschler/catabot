from cata import Cata


route = 'B'
stops = [356, 565, 1]

cata = Cata()
for stop in stops:
    results = {}
    items = cata.departures(stop)
    for item in items:
        route = item.route
        if route not in results.keys():
            results[route] = []
        results[route].append(item)
    print('\n')
    print('last updated: {}'.format(cata.last_updated))
    for route, departures in results.items():
        print('{} -- {}'.format(
            departures[0].route_name,
            departures[0].bus.title(),
        ))
        for d in departures:
            print('  - {}/{} {}'.format(
                d.scheduled,
                d.estimated,
                d.delta_label,
            ))

