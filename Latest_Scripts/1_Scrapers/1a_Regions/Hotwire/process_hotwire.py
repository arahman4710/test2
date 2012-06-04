import re
from sqlalchemy import *

from hotwire_cities_region_map import Hotwire_cities_region_map


from alchemy_session import get_alchemy_info

###################################
## Processes the hotwire api log which contains the city to region relationship of hotwire



(engine, session, Base, metadata) = get_alchemy_info ()

f = open("HOTWIRE_API.log", "r")
city = ""
state = ""
country = ""

for line in f.readlines():
	if re.search('.*\$$', line):
		city_state_country = line[10:-2]
		location_elems = re.split(", ", city_state_country)
		city = location_elems[0]
		state = location_elems[1]
		country = location_elems[2]
	else:
		region_name = line[10:-2]
		entry = Hotwire_cities_region_map(city, state, country, region_name)
		session.add(entry)
		session.commit()
    
                    

            

