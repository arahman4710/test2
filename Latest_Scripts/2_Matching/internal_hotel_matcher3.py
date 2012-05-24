
'''
@author: Areek
@desc: script to match Canonical hotels with hotels combined and expedia hotels
@notes: - work has been done on candaian cities only; functions implemented for US ones; still need to implement to store the matched results in db  
'''

import sys
import time
sys.path.insert(0, "/home/areek/Documents/fetchopia/backend_git/" )

from sql.alchemy import alchemy_session


from sql.alchemy.canon_hotel import CanonicalHotel
from sql.alchemy.hotel_combined import Hotel_Combined
from sql.alchemy.hotel_expedia import Hotel_Expedia


import Levenshtein
from collections import defaultdict
import re

import logging
logging.basicConfig(filename='internal_hotel_matcher2.log',filemode='w',level=logging.DEBUG)



match_brackets_pattern = re.compile(r'\(.+?\)')
match_street_no = re.compile('^[0-9]+')

(engine, session,Base, metadata) = alchemy_session.get_alchemy_info()

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
	
	return cleaned_addr

def clean_city_name(city):
    
    return re.sub(match_brackets_pattern,'',city).lower().replace("city","").replace("'","").replace('"','').strip()



#    matching function for hotel names
def find_htl_name_match_ratio(name_1,name_2): 
    
    return Levenshtein.ratio(normalize_name(name_1),normalize_name(name_2))

#	matching function for city
def find_city_match_ratio(city_1,city_2):
	
	return Levenshtein.ratio(city_1,city_2)
    
#    matching function for hotel address
def find_htl_address_match_ratio(add_1,add_2): 
    
    return Levenshtein.ratio(normalize_address(add_1),normalize_address(add_2)) 



#for each hotel in canon
#for each hotel in combined, thats in the canon hotel's lat long range
#try to find a match
def find_htls_in_city():
	
	matched = 0
	unmatched = 0
	canon_htls = session.query(CanonicalHotel).all()
	hotel_counter = 0
	
	for canon_htl in canon_htls:
		
		if hotel_counter == 20:
			break
			
		hotel_counter += 1
            	
        	#acceptable range for difference in lat long
            	tolerance = 0.005
            	
            	##find all the hotels in cmbd with lat long values in range of the canon hotel
            	cmbd_htls_by_specific_lat_long = session.query(Hotel_Combined).filter((canon_htl.latitude - tolerance) < Hotel_Combined.latitude < (canon_htl.latitude + tolerance))\
            	.filter((canon_htl.longitude -tolerance) < Hotel_Combined.longitude < (canon_htl.longitude + tolerance)).all()
            	
            	max_ratio = float(0)
		matched_tuple = ()
		
		for cmbd_htl in cmbd_htls_by_specific_lat_long:
				
			ratio = float()
			name_ratio = float()
			address_ratio = float()
				
			cleaned_address = cmbd_htl.address.replace('"','').replace("'","").strip(),canon_htl.address.replace('"','').replace("'","").strip()
				
			street_number_1 = re.match(match_street_no,cleaned_address[0])
			street_number_2 = re.match(match_street_no,cleaned_address[1])
				
			street_number_found = False
			street_number_match = False
				
			if street_number_1 and street_number_2:
					
				street_number_found = True
					
				if street_number_1.group(0) == street_number_2.group(0):
					
					street_number_match = True
					cleaned_address = tuple(map(lambda x: " ".join(sorted(re.sub(match_street_no,'',x).strip().split())),cleaned_address))
				
				
			name_ratio = find_htl_name_match_ratio(cmbd_htl.hotel_name,canon_htl.hotel_name) 
			address_ratio = find_htl_address_match_ratio(cleaned_address[0],cleaned_address[1])
				
			ratio = name_ratio + address_ratio
				
			if address_ratio > float(0.75):
				if street_number_match and street_number_found:
					ratio = float(2)
				
			if name_ratio > float(0.9):
				ratio = name_ratio*2
	
		
				
			if max_ratio < ratio:
				matched_tuple = (cmbd_htl,canon_htl,ratio,name_ratio,address_ratio)
				max_ratio = ratio
			
		## best match case
		if max_ratio > float(1.7):
		
			matched += 1
		
		## further matching case	
		elif max_ratio > float(1.2):
			if not matched_tuple:
				continue
			else: 
				## extract the components of the max matched tuple
				cmbd_htl = matched_tuple[0]
				canon_htl = matched_tuple[1]
				ratio = matched_tuple[2]
				name_ratio = matched_tuple[3]
				address_ratio = matched_tuple[4]
			
				cmbd_htl_clean_city = clean_city_name(cmbd_htl.city)
				canon_htl_clean_city = clean_city_name(canon_htl.city)
				##find the city match ratio
				city_ratio = find_city_match_ratio(cmbd_htl_clean_city, canon_htl_clean_city)
			
				##if name ratio is greater than 0.49 and the cities match, then its a match
				if (name_ratio > float(0.49)) and (city_ratio > float(0.8)):
					matched += 1
			
				else:
					logging.info("Similar name:: %s with %s ratio %f" % (cmbd_htl.hotel_name,canon_htl.hotel_name,name_ratio))
					logging.info("Unmatched address:: %s with %s ratio %f" % (cmbd_htl.address,canon_htl.address,address_ratio))
					logging.info("City and State are %s, %s for combined" % (cmbd_htl.city, cmbd_htl.state_code))
					logging.info("City and State are %s, %s for canonical" % (canon_htl.city, canon_htl.state_code))
					logging.info("max ratio %f and ratio %f" % (max_ratio, ratio))
					unmatched += 1
		else:
			if not matched_tuple:
				continue
			else:
				cmbd_htl = matched_tuple[0]
				canon_htl = matched_tuple[1]
				ratio = matched_tuple[2]
				name_ratio = matched_tuple[3]
				address_ratio = matched_tuple[4]
				logging.info("Similar name:: %s with %s ratio %f" % (cmbd_htl.hotel_name,canon_htl.hotel_name,name_ratio))
				logging.info("Unmatched address:: %s with %s ratio %f" % (cmbd_htl.address,canon_htl.address,address_ratio))
				logging.info("City and State are %s, %s for combined" % (cmbd_htl.city, cmbd_htl.state_code))
				logging.info("City and State are %s, %s for canonical" % (canon_htl.city, canon_htl.state_code))
				logging.info("max ratio %f and ratio %f" % (max_ratio, ratio))
			
				unmatched += 1


	print "for matching hotels:: matched: %d and unmatched: %d" % (matched, unmatched)
	

                        

	
	


if __name__ == '__main__':
	start = time.time()
	find_htls_in_city()
	print "it took", time.time() - start, "seconds."

    
