from cata import Cata

import requests
import time


class Notify(object):
    def __init__(self, stops, route=None, debug=False):
        self.debug = debug
        self.edts = {}
        self.stops = stops
        self.route = route
        self.cata = Cata()
        self.update()

    def cli(self):
        for stop, results in self.stop_departures.items():
            print('\n')
            print('Stop: {}'.format(self.cata.stop_name(stop)))
            print('last updated: {}'.format(self.cata.last_updated))
            for route, departures in results.items():
                print('{} -- {}'.format(
                    departures[0].route_name,
                    departures[0].bus.title(),
                ))
                for d in departures:
                    print('  - {}/{} ({})'.format(
                        d.scheduled,
                        d.estimated,
                        d.delta_label,
                    ))

    def _print(self, msg):
        if self.debug:
            print(msg)

    def teams(self, channel_url):
        data = {
            '@type': 'MessageCard',
            '@context': 'http://schema.org/extentions',
            'summary': 'Incoming bus schedule',
            'sections': [],
        }
        for stop, results in self.stop_departures.items():
            departure = results[self.route][0]
            section = {
                'activityTitle': 'Next departure for {}'.format(self.cata.stop_name(stop)),
                'activitySubtitle': 'Last updated: {}'.format(self.cata.last_updated),
                'facts': [{
                    'name': 'Bus',
                    'value': departure.bus.title(),
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
            key = '{}|{}|{}'.format(stop, departure.bus_number, departure.scheduled)
            self.edts[key] = departure.edt
            self._print('Adding EDT: {} = {}'.format(key, departure.edt))
        requests.post(url=channel_url, json=data)
        self._print('Sent Alert')

    def teams_monitor(self, channel_url):
        while True:
            time.sleep(60)
            self.update()
            existing_keys = [k for k in self.edts.keys()]
            self._print('self.edts: {}'.format(self.edts.keys()))
            self._print('existing_keys: {}'.format(existing_keys))
            for stop, results in self.stop_departures.items():
                departure = results[self.route][0]
                key = '{}|{}|{}'.format(stop, departure.bus_number, departure.scheduled)
                try:
                    existing_keys.remove(key)
                except ValueError:
                    pass
                self._print('remove existing: {}'.format(key))
                prev_edt = self.edts.get(key, None)
                if prev_edt is None:
                    continue
                status = ''
                if prev_edt > departure.edt:
                    status = 'catching up - better hurry!'
                elif prev_edt < departure.edt:
                    status = 'falling behind - take your time'
                if status:
                    delta = int(abs(prev_edt - departure.edt).seconds / 60)
                    data = {'text': '{} bus to {} now {}: {}'.format(
                        self.route,
                        self.cata.stop_name(stop),
                        departure.estimated,
                        status,
                    )}
                    requests.post(url=channel_url, json=data)
                    self._print('Sent update')
                self.edts[key] = departure.edt
            if existing_keys:
                for key in existing_keys:
                    del self.edts[key]
                    self._print('remove self.edts[{}]'.format(key))
            self._print('remaining self.edts: {}'.format(self.edts.keys()))
            if not self.edts.keys():
                break


    def update(self):
        self.stop_departures = {}
        for stop in self.stops:
            results = {}
            items = self.cata.departures(stop, self.route)
            for item in items:
                route = item.route
                if route not in results.keys():
                    results[route] = []
                results[route].append(item)
            self.stop_departures[stop] = results


if __name__ == '__main__':
    notifier = Notify([356, 565], 'B', debug=True)
    # notifier.cli()
    try:
        from local_settings import TEAMS_URL
    except ImportError:
        print('ERROR! TEAMS_URL is not defined in local_settings.py')
    else:
        notifier.teams(TEAMS_URL)
        notifier.teams_monitor(TEAMS_URL)
