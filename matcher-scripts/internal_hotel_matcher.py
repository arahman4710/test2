
'''
@author: Areek
@desc: script to match Canonical hotels with hotels combined and expedia hotels
@notes: - work has been done on candaian cities only; functions implemented for US ones; still need to implement to store the matched results in db  
'''

import sys

sys.path.insert(0, "/home/areek/Documents/fetchopia/backend_git/" )

from sql.alchemy import alchemy_session


from sql.alchemy.canon_hotel import CanonicalHotel
from sql.alchemy.hotel_combined import Hotel_Combined
from sql.alchemy.hotel_expedia import Hotel_Expedia


import Levenshtein
from collections import defaultdict
import re

import logging
logging.basicConfig(filename='internal_hotel_matcher.log',filemode='w',level=logging.DEBUG)



match_brackets_pattern = re.compile(r'\(.+?\)')
match_street_no = re.compile('^[0-9]+')

(engine, session,Base, metadata) = alchemy_session.get_alchemy_info()

state_code_dict = {}

with open('us_state_code','r') as f:
	for content in f.read().split('\n'):
		fields = content.split('\t')
		if len(fields) == 2:
			state,code = fields
			state_code_dict[str(state)] = str(code)
	state_code_dict[str('District of Columbia')] = str('DC')	#special case


def normalize_name(name):
	
	cleaned_name = name.replace(" and ","&").replace(" And ","&").replace("Hotel","").strip().lower()
	return " ".join(sorted(cleaned_name.split()))

def normalize_address(addr):
	
	cleaned_addr = addr.lower().replace(".","").replace(" drive"," dr")\
        .replace(" parkwy"," pkwy").replace(" boulevard"," blvd").\
        replace("@","at").replace(" street"," st").replace(" &amp; "," & ").\
        replace(" road"," rd").replace(" east"," e").replace(" north"," n").\
        replace(" south"," s").replace(" west"," w").replace(" avenue"," ave").\
        replace(" freeway"," frwy").replace(" fwy"," frwy").replace(" parkway"," pkwy").replace("rue ","st ").replace(" rue"," st")
	
	return cleaned_addr#" ".join(sorted(cleaned_addr.split()))
 

        
#	returns a dictionary of list of us cities with states from hotels combined

def get_htl_cmbnd_us_cities():
    
    combined_state_city = session.query(Hotel_Combined.state_code,Hotel_Combined.city).filter(Hotel_Combined.country_code == u'US').distinct()

    country_state_dict = defaultdict(list)
    country_state_list = map(lambda x:(str(x[0]).replace("'","").replace('"',''),str(x[1]).replace("'","").replace('"','')),combined_state_city)
    	
    for state,city in country_state_list:
    	country_state_dict[state.strip()].append(re.sub(match_brackets_pattern,'',city).strip())
    
    return country_state_dict    	
    

#	returns a list of canadian cities from hotels combined

def get_ca_cities(hotel_src):
	
		return map(lambda x:str(x[0]),session.query(hotel_src.city).filter(hotel_src.country_code == u'CA').distinct())

'''
def get_ca_cities(hotel_src):
	if hotel_src == 'Hotel_Combined':
		return map(lambda x:(str(x[0]).replace("'","").replace('"','').strip()),session.query(Hotel_Combined.city).filter(Hotel_Combined.country_code == u'CA').distinct())
	elif hotel_src == 'CanonicalHotel':
		return map(lambda x:(str(x[0]).replace("'","").replace('"','').strip()),session.query(CanonicalHotel.city).filter(CanonicalHotel.country_code == u'CA').distinct())
'''		

def clean_city_name(city):
    
    return re.sub(match_brackets_pattern,'',city).lower().replace("city","").replace("'","").replace('"','').strip()

def get_canon_us_cities():
    
    state_city = session.query(CanonicalHotel.state_code,CanonicalHotel.city).filter(CanonicalHotel.country_code == u'US').distinct()

    country_state_dict = defaultdict(list)
    country_state_list = map(lambda x:(str(x[0]).replace("'","").replace('"',''),str(x[1]).replace("'","").replace('"','')),state_city)
    	
    for state,city in country_state_list:
    	country_state_dict[state.strip()].append(re.sub(match_brackets_pattern,'',city).strip())
    
    return country_state_dict   

def get_matched_cmbd_canon_city_list():
	
	htl_cmbd_ca_cities = get_ca_cities(Hotel_Combined)
	canon_htl_ca_cities = get_ca_cities(CanonicalHotel)
	#print len(htl_cmbd_ca_cities)
	unmatched = 0
	for cmbd_city in htl_cmbd_ca_cities:
		
		cmbd_cleaned_city = clean_city_name(cmbd_city)
        
		canon_clean_city_dict = {}
        
		for canon_city_name in canon_htl_ca_cities:
			canon_clean_city_dict[clean_city_name(canon_city_name)] = canon_city_name 
        
		if cmbd_cleaned_city in canon_clean_city_dict.keys():
			
			logging.debug("get_matched_cmbd_canon_city_list(): found clean match between hotels for %s" % cmbd_city)
			
			yield (cmbd_city,canon_clean_city_dict[cmbd_cleaned_city])
		
		else:
			
			logging.debug("get_matched_cmbd_canon_city_list(): going to levenstein's match, straight forward match failed for %s" % cmbd_city)
			
			max_match_ratio = float(0)
			max_matched_cities = ()
			
			for canon_city in canon_clean_city_dict.keys():
				
				instance_ratio = find_city_match_ratio(canon_city,cmbd_cleaned_city)
				
				if max_match_ratio < instance_ratio:
					
					max_match_ratio = instance_ratio  
					max_matched_cities = (cmbd_city,canon_clean_city_dict[canon_city])
			
			if max_match_ratio > 0.8:
				
				logging.debug("get_matched_cmbd_canon_city_list(): good match ratio found for %s" % cmbd_city)
				yield max_matched_cities
				
			else:
				unmatched += 1
				logging.error("get_matched_cmbd_canon_city_list(): low match ratio found for %s with %s having a match ratio of %f" % (cmbd_city,max_matched_cities[1],max_match_ratio))
				#yield None
			
		
	logging.debug("get_matched_cmbd_canon_city_list(): %d entries are still unmatched" % unmatched) 

def get_htl_in_city(htl_src,city,state = None):
	
	if state: return session.query(htl_src).filter(htl_src.state_code == state).filter(htl_src.city == city)	

	return session.query(htl_src).filter(htl_src.city == city)


#    matching function for hotel names
def find_htl_name_match_ratio(name_1,name_2): 
    
    return Levenshtein.ratio(normalize_name(name_1),normalize_name(name_2))

#	matching function for city
def find_city_match_ratio(city_1,city_2):
	
	return Levenshtein.ratio(city_1,city_2)
    
#    matching function for hotel address
def find_htl_address_match_ratio(add_1,add_2): 
    
    return Levenshtein.ratio(normalize_address(add_1),normalize_address(add_2)) 

def find_htls_in_city():
	
	matched = 0
	unmatched = 0
	
	for cmbd_htls,canon_htls in find_hotels_by_specific_city():
            
		for cmbd_htl in cmbd_htls:
			
			max_ratio = float(0)
			matched_tuple = ()
                
			for canon_htl in canon_htls:
				
				ratio = float()
				name_ratio = float()
				address_ratio = float()
				
				cleaned_address = cmbd_htl.address.replace('"','').replace("'","").strip(),canon_htl.address.replace('"','').replace("'","").strip()
				
				street_no_1 = re.match(match_street_no,cleaned_address[0])
				street_no_2 = re.match(match_street_no,cleaned_address[1])
				
				street_no_found = False
				street_no_match = False
				
				if street_no_1 and street_no_2:
					
					street_no_found = True
					
					if street_no_1.group(0) == street_no_2.group(0):
					
						street_no_match = True
						cleaned_address = tuple(map(lambda x: " ".join(sorted(re.sub(match_street_no,'',x).strip().split())),cleaned_address))
				
				
				name_ratio = find_htl_name_match_ratio(cmbd_htl.hotel_name,canon_htl.hotel_name) 
				address_ratio = find_htl_address_match_ratio(cleaned_address[0],cleaned_address[1])
				
				ratio = name_ratio + address_ratio
				
				if address_ratio > float(0.75):
					if street_no_match and street_no_found:
						logging.debug("find_htls_in_city(): hotel not matched:: street_no_match true for %s with %s" % cleaned_address)
						ratio = float(2)
				
				if name_ratio > float(0.9):
					ratio = name_ratio*2
				
				if max_ratio < ratio:
					#logging.debug("find_htls_in_city(): good match ratio found for %s with ratio %f" % (cmbd_htl.hotel_name,canon_htl.hotel_name,ratio))
					matched_tuple = (cmbd_htl,canon_htl,ratio,name_ratio,address_ratio)
					max_ratio = ratio
					
			(cmbd_htl,canon_htl,max_ratio,name_ratio,address_ratio) = matched_tuple
			
			if max_ratio > 1.7:
				logging.info("find_htls_in_city(): hotel matched:: %s with %s ratio %f" % (cmbd_htl.hotel_name,canon_htl.hotel_name,max_ratio))
				matched += 1
			else:
				logging.error("find_htls_in_city(): hotel not matched:: %s with %s ratio %f" % (cmbd_htl.hotel_name,canon_htl.hotel_name,name_ratio))
				logging.error("find_htls_in_city(): hotel not matched address:: %s with %s ratio %f" % (cmbd_htl.address,canon_htl.address,address_ratio))
				unmatched += 1

		#break	#DEBUG!
	
	logging.info("find_htls_in_city(): Total hotels matched:: %d and Total hotels unmatched:: %d" % (matched,unmatched))
	

                        

def find_hotels_by_specific_city():
	
	for matched_city in get_matched_cmbd_canon_city_list():
            
		if not matched_city: continue
		
		if len(matched_city) == 2:	# for canada
			
			cmbd_city,canon_city = matched_city
            
            #    get hotel records for particular city
			cmbd_htls = get_htl_in_city(Hotel_Combined,cmbd_city)
			canon_htls = get_htl_in_city(CanonicalHotel,canon_city)
            
			logging.info("find_hotels_by_specific_city(): %d hotels found in Hotel_Combined %d hotels found in Cononical Hotel" % (len(cmbd_htls.all()),len(canon_htls.all())))
			
			yield (cmbd_htls.all(),canon_htls.all())

		
		else:	# for US
			
			cmbd_city,cmbd_state,canon_city,canon_state = matched_city
			print cmbd_city,canon_city
	
	
	


if __name__ == '__main__':
	for one in find_htls_in_city():
   		pass#find_hotels_by_specific_city()
    
