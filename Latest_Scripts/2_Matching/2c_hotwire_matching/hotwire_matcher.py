import Levenshtein
import re
import time
import sys
import pdb

sys.path.insert(0, "/home/areek/Documents/fetchopia/backend_git/sql/alchemy/" )

from sqlalchemy import *
from alchemy_session import get_alchemy_info

from processed_forum_data5 import ProcessedRawForumData2
from hotwire_tables import *


(engine, session,Base, metadata) = get_alchemy_info()

all_hotwire_hotels = session.query(ProcessedRawForumData2).filter(ProcessedRawForumData2.target_site == 'Hotwire') ## all better bidding hotwire hotels scraped

for instance in all_hotwire_hotels.all():
	
	possible_match = session.query(HotWireHotelInfo).filter(HotWireHotelInfo.state == hotwire state)
	
	for match in possible_match:
	
		amenity_info = get_amenity_info() ##function that gets amenity info from hotwirehotelinfo table's amenity_list column
		
		bb_amenity_info = make_amenity_list(instance.amenity) ## make amenity list func turns raw amenity info into a list to compare
		
		amenity_match_flag = False
		star_match_flag = False
		
		##if both lists of amenity have same elements
		if amenity_info == bb_amenity_info:
			#match 
			
			amenity_match_flag = True
		
		if match.star_rating == instance.star:
			star_match_flag = True
			
		if amenity_match_flag and star_match_flag:
			## log this in a table with a column for hotwire_id and bbhw_id
			
			entry = hotwire_forum_table(instance.uid, match.uid)
			session.add(entry)
			session.commit()
			
##after matching hotwire scraped hotels to bbhw scraped hotels
##match bbhw to internal hotels, with the help of internal hotel's lat/lng and hotwire's region points

for instance in all_hotwire_hotels.all():
	
	bbhw_id = instance.uid
	associated_hotwire_hotel_id = session.query(hotwire_forum_table.hotwire_id).filter(hotwire_forum_table.bbhw_id == bbhw_id).first()
	#get hotwire region points
	for hotel in session.query(CanonicalHotel).all():
		
		if ray.casting(hotel.lat, hotel.lng, hotwire_region_points):
			hotellist += hotel
		
		return hotellist
	
	##use hotellist (hotels within the region of the bbhw hotel) to match hotel name using levenshtein ratio
	if hotellist.count() > 0:

		for match in hotellist.all():
				
			name_ratio = find_htl_name_match_ratio(hotellist.hotel_name, kayak_name) 
			address_ratio = find_htl_address_match_ratio(hotellist.address,kayak_address)
					
			if address_ratio > float(0.98):
				address_ratio = 2
					
			if name_ratio > float(0.95):
				name_ratio = 2
				
			ratio = name_ratio + address_ratio
				
			if max_ratio < ratio:
				max_ratio = ratio
				max_match_tuple = (match, name_ratio, address_ratio)
				
		(match, name_ratio, address_ratio) = max_match_tuple

		if max_ratio > 1.35:
			canonical_id = match.uid
			kayak_id = instance.uid
			entry = kayak_internal_table(canonical_id, kayak_id)
			session.add(entry)					
			session.commit()
				
		else:
			pass ## not good enough a match
					
			
	else:
		continue ## no match for this kayak hotel case
	
		
