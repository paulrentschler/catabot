from cata import Cata



class Notify(object):
    def __init__(self, stops, route=None):
        self.stops = stops
        self.route = route
        self.stop_departures = {}
        self.cata = Cata()
        for stop in self.stops:
            results = {}
            items = self.cata.departures(stop, self.route)
            for item in items:
                route = item.route
                if route not in results.keys():
                    results[route] = []
                results[route].append(item)
            self.stop_departures[stop] = results

    def cli(self):
        for stop, results in self.stop_departures.items():
            print('\n')
            print('Stop: {}'.format(stop))
            print('last updated: {}'.format(self.cata.last_updated))
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


if __name__ == '__main__':
    notifier = Notify([356, 565])
    notifier.cli()

