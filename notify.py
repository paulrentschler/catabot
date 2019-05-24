from bs4 import BeautifulSoup

import requests


route = 'B'
stops = [356, ]
stop_status_url = 'https://realtime.catabus.com/InfoPoint/Stops/Stop/{stop}'

content = requests.get(stop_status_url.format(stop=stops[0])).text
soup = BeautifulSoup(content, 'html.parser')
departures_table = soup.find('table', class_='departures-grid')
departures_body = departures_table.find('tbody')
departures = departures_body.find_all('tr')
for departure in departures:
    route_abbr = departure.find(class_='route-abbr')
    print(route_abbr.text.strip())
import pdb; pdb.set_trace()
