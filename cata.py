from bs4 import BeautifulSoup
from datetime import datetime

import requests


class Departure(object):
    ROUTES = {
        'B': 'Boalsburg',
        'C': 'Houserville',
        'HM': 'Toftrees/Nittany Mall',
        'RL': 'Red Link',
        'XB': 'Bellefonte',
        'XG': 'Pleasant Gap',
    }

    def __init__(self, html):
        try:
            self.route = html.find(class_='route-abbr').text.strip().upper()
        except AttributeError:
            self.route = None
        else:
            try:
                self.bus_number = int(html.find(class_='bus-cell').text.strip())
            except (AttributeError, ValueError):
                self.bus_number = None
            for field in ('sdt', 'edt'):
                class_ = '{}-cell'.format(field)
                try:
                    time_str = html.find(class_=class_).text.strip()
                except AttributeError:
                    setattr(self, field, None)
                else:
                    setattr(self, field, self._convert_dt(time_str))

    @property
    def bus(self):
        if self.bus_number is None:
            return 'n/a'
        else:
            bus = self.bus_number
            if bus >= 32 and bus <= 36:
                desc = 'rumble '
            elif bus < 40:
                desc = 'newer big '
            elif bus <= 60:
                desc = 'newest big '
            elif bus >= 70 and bus < 80:
                desc = 'medium '
            else:
                desc = ''
            return '{}bus #{}'.format(desc, self.bus_number)

    def _convert_dt(self, time_str):
        dt_str = '{} {}'.format(datetime.now().strftime('%Y/%m/%d'), time_str)
        return datetime.strptime(dt_str, '%Y/%m/%d %I:%M %p')

    @property
    def delta(self):
        try:
            return int(abs(self.sdt - self.edt).seconds / 60)
        except TypeError:
            return 0

    @property
    def delta_label(self):
        if self.is_early:
            return 'early: {} min'.format(self.delta)
        elif self.is_late:
            return 'LATE: {} min'.format(self.delta)
        else:
            return 'on-time'

    @property
    def estimated(self):
        return self._format_dt(self.edt)

    def _format_dt(self, dt):
        try:
            return dt.strftime('%-I:%M%p').lower()
        except AttributeError:
            return 'n/a'

    @property
    def is_early(self):
        try:
            return self.edt < self.sdt
        except TypeError:
            return False

    @property
    def is_late(self):
        try:
            return self.edt > self.sdt
        except TypeError:
            return False

    @property
    def is_valid(self):
        if self.route is None:
            return False
        if self.sdt is None or self.edt is None:
            return False
        return True

    @property
    def route_name(self):
        if self.route is None:
            return 'n/a'
        try:
            return '{}: {}'.format(self.route, self.ROUTES[self.route])
        except KeyError:
            return self.route

    @property
    def scheduled(self):
        return self._format_dt(self.sdt)


class Cata(object):
    url = 'https://realtime.catabus.com/InfoPoint/Stops/Stop/{stop}'

    def __init__(self):
        self.last_updated = None

    def _get_data(self, html, class_):
        try:
            return html.find(class_=class_).text.strip()
        except AttributeError:
            return 'n/a'

    def _get_last_updated(self, html):
        try:
            last_updated = html.find(class_='last-updated')
            heading = last_updated.find(class_='heading').text
            text = last_updated.text.replace(heading, '').strip()
        except AttributeError:
            self.last_updated = None
        else:
            try:
                obj = datetime.strptime(text, '%m/%d/%Y %I:%M %p')
            except (TypeError, ValueError):
                self.last_updated = None
            else:
                self.last_updated = obj

    def departures(self, stop, route=None):
        results = []
        content = requests.get(self.url.format(stop=stop))
        soup = BeautifulSoup(content.text, 'html.parser')
        self._get_last_updated(soup)
        table = soup.find('table', class_='departures-grid')
        try:
            rows = table.tbody.find_all('tr')
        except AttributeError:
            return results
        for row in rows:
            departure = Departure(row)
            if departure.is_valid:
                if route is not None:
                    if departure.route == route:
                        results.append(departure)
                else:
                    results.append(departure)
        return results

    def stop_name(self, stop):
        if stop == 356:
            return 'Curtin Rd at Visual Arts Building - Stop 356'
        elif stop == 565:
            return 'E Beaver Ave at Beaver Hill Apts - Stop 565'
        return 'Stop {}'.format(stop)
