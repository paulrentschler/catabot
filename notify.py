from cata import Cata

import requests


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

    def teams(self):
        try:
            from local_settings import TEAMS_URL
        except ImportError:
            print('ERROR! TEAMS_URL is not defined in local_settings.py')
            return
        url = TEAMS_URL
        data = {
            '@type': 'MessageCard',
            '@context': 'http://schema.org/extentions',
            'summary': 'Incoming bus schedule',
            'sections': [],
        }
        for stop, results in self.stop_departures.items():
            departure = results[self.route][0]
            section = {
                'activityTitle': 'Next departure for stop {}'.format(stop),
                'activitySubtitle': 'Last updated: {}'.format(self.cata.last_updated),
                'facts': [{
                    'name': 'Bus',
                    'value': departure.bus.tilte(),
                }, {
                    'name': 'Scheduled',
                    'value': departure.scheduled,
                }, {
                    'name': 'Estimated',
                    'value': departure.estimated,
                }, {
                    'name': 'Status',
                    'value': departure.delta_label,
                }]
            }
            data['sections'].append(section)
        requests.post(url=url, json=data)


if __name__ == '__main__':
    notifier = Notify([356, 565])
    notifier.cli()
    # notifier.teams()
