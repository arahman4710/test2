import re
from sqlalchemy import *

from hotwire_cities_region_map import Hotwire_cities_region_map


#from alchemy_session import get_alchemy_info





#(engine, session, Base, metadata) = get_alchemy_info ()

f = open("test_input.txt", "r")
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
#		print city, state, country
	else:
		region_name = line[10:-2]
		entry = Hotwire_cities_region_map(city, state, country, region_name)
		session.add(entry)
		session.commit()
    
                    

            

