
import sys

sys.path.insert(0, "/home/areek/Documents/fetchopia/backend_git/" )

from sql import alchemy_session
from sql.alchemy.canon_hotel import CanonicalHotel
from sql.alchemy.city_table import CityTable
from sql.alchemy.priceline_city_region_map import PricelineCityRegionMap
from sql.alchemy.priceline_region_hotel_map import PricelineRegionHotelMap
from sql.alchemy.priceline_regions_table import PricelineRegionTable
from sql.alchemy.priceline_region_point_table import PricelineRegionPointTable
from sql.alchemy.priceline_city_region_map import PricelineCityRegionMap
from sql.alchemy.canon_hotel_city_map import CanonHotelCityMap

from Levenshtein import ratio

import re

(engine, session,Base, metadata) = alchemy_session.get_alchemy_info()

state_code_dict = {}

#1
##	get distinct states from current hotel table
##	convert state codes to state names
##	match state names with state names in the existing city table

match_brackets_pattern = re.compile(r'\(.+?\)')

with open('us_state_code','r') as f:
	for content in f.read().split('\n'):
		fields = content.split('\t')
		if len(fields) == 2:
			state,code = fields
			if code and state:
				state_code_dict[str(code).lower() ] =  str(state)
	state_code_dict[str('DC').lower()] = str('District of columbia')  	#special case
	



def get_us_state_list():

	return map(lambda x:x[0],session.query(CityTable.state).filter(CityTable.country == 'United States').distinct().all())

def get_us_city_list(state):
	
	return map(lambda x:x[0],session.query(CityTable).filter(CityTable.country == 'United States').filter(CityTable.state == state).distinct().all())

def get_us_state_list_from_hotel_table():
	
	return map(lambda x:x[0],session.query(CanonicalHotel.state_code).filter(CanonicalHotel.country_code == 'US').distinct().all())

def get_city_list_from_hotel_table(state):
	return map(lambda x:x[0],session.query(CanonicalHotel.city).filter(CanonicalHotel.country_code == 'US').filter(CanonicalHotel.state_code == state).distinct().all())
	

def get_corrosponding_state_name(state_code):
	
	return state_code_dict[state_code.lower()]


def insert_matched_city_hotel_map(city_id, hotel_city_name,hotel_state_code):
	
	hotel_ids = map(lambda x:x[0], session.query(CanonicalHotel.uid).filter(CanonicalHotel.state_code == hotel_state_code).filter(CanonicalHotel.city == hotel_city_name).all())
	
	session.add_all([CanonHotelCityMap(hotel_id,city_id) for hotel_id in hotel_ids]) 
	
	session.commit()
	
	return len(hotel_ids)

def city_match(hl_city,city_city):
	
	if not city_city: return False
	
	ct_city = city_city.lower().strip()
	hl_city = hl_city.lower().strip()
	
	if ratio(hl_city,ct_city) > 0.85:
		return True
	else:
		
		ct_city = re.sub(match_brackets_pattern,'',ct_city)
		hl_city = re.sub(match_brackets_pattern,'',hl_city)
		
		if ratio(hl_city,ct_city) > 0.85:
			return True
		
		return False
		

if __name__ == "__main__":

	# This script matches matches the Canonical hotels to cities with respect to priceline 
	
	priceline_city_ids = map(lambda x:x[0],session.query(PricelineCityRegionMap.city_id).distinct().all())
	gl_match = gl_unmatch = 0
	gl_matched_city_id = []
	for state in get_us_state_list_from_hotel_table():
	  	if state:
	  		print 'for %s' % state
	  		
	  		#	extract out list of cities from hotels table for the state
	  		
	  		hotel_city_lst = get_city_list_from_hotel_table(state)
	  		
	  		#	find the corrosponding state in the city table
	  		
	  		city_state_name = get_corrosponding_state_name(state)
			
			#	get the list of cities for that state from the cities table
			
			city_city_lst = session.query(CityTable).filter(CityTable.country == 'United States').filter(CityTable.state == city_state_name).distinct().all()
			
			#	checking if all the cities pl is interested in are acounted for
			'''
			for city in city_city_lst:
				
				if city.uid in priceline_city_ids:
					priceline_city_ids.remove(city.uid)
			
			print len(city_city_lst)
			'''
			#	try match all the cities with each other
			matched = unmatched = 0
			match_fl = False
			unmatched_city_lst = []
			matched_city_id = []
			
			for hl_city in hotel_city_lst:
				if hl_city:
					match_fl = False
					matched_city_id = []
					max_r = 0
					matched_id = -1
					#if hl_city.strip().lower() not in map(lambda x: x.name.strip().lower(),city_city_lst):
					for ct_city in city_city_lst:
						if ct_city.name:
							r = ratio(hl_city.lower().strip(),ct_city.name.lower().strip())
							if r > 0.85:

								match_fl = True
								matched_city_id.append(ct_city.uid)
								
								print 'inserting mapping of hotels to cities for %s ' % hl_city
								print 'Finished Inserting %d hotel-city map' % (insert_matched_city_hotel_map(ct_city.uid, hl_city,state))
							else:
								match_fl = False
							
					if matched_city_id:
						matched += 1
						gl_matched_city_id.extend(matched_city_id)
					else:
						unmatched += 1
					
			#print 'matched: %d and unmatched %d' %(matched, unmatched)
	  		gl_unmatch += unmatched
	  		gl_match += matched
	  		
	pl_unmatched = 0	
				
	print 'pl_cities unmatched %d out of %d' %(pl_unmatched,len(priceline_city_ids))

	city_state_list = get_us_state_list()
	city_state_list.remove(None)
	city_state_list = map(lambda x: x.lower(),city_state_list)
  	print 'glb match %d glb_unmatched %d' % (gl_match,gl_unmatch)

  	
		  		
