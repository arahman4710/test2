import Levenshtein
import re
import time
import sys
import pdb

sys.path.insert(0, "/home/areek/Documents/fetchopia/backend_git/sql/alchemy/" )

from sqlalchemy import *
from alchemy_session import get_alchemy_info


from processed_forum_data_hotwire import ProcessedRawForumData_hotwire
from hotwire_tables import *


(engine, session,Base, metadata) = get_alchemy_info()

all_hotwire_hotels = session.query(ProcessedRawForumData_hotwire) ## all better bidding hotwire hotels scraped

def get_hotwire_amenity_info(amenity_list_id):
	
	items = session.query(AmenityListItem).filter(AmenityListItem.amenity_list_id == amenity_list_id)
	items_list_id = []
	for item in items.all():
		items_list_id.append(item.amenity_id)
	
	
	items_list_code = [] ##the amenity of this hotel in a list of codes ie. Airport Shuttle for AS and Near Beach for BA
	for instance in items_list_id:
		amenity_item = session.query(Amenity).filter(Amenity.uid == instance).first()
		items_list_code.append(str(amenity_item.code))
	
	return items_list_code
		
def generate_amenity_list(amenity):
	amenities_element_dict = {"Airport Shuttle":"AS", "Shuttle":"AS", "Business Center":"BC", "Business":"BC", "Boutique":"BH", "Complimentary Breakfast":"CB", "Fitness":"FC", "Fitness Center":"FC", 
	"Hi-Speed Internet":"HS", "High-Speed Internet Access":"HS", "High Speed Internet":"HS", "High-Speed internet":"HS", "High-Speed Internet":"HS", "Kitchenette":"KI", "Laundry":"LF", "Pool":"PO", 		"Restaurant":"RE", "Spa":"SF", "Smoke Free":"SR", "Suite":"SU", "Golf":"GN", "Slopeside":"SL", "Oceanfront":"OF", "AC":"AC", "Parking":"FP", "Suites":"SU", "Golf Nearby":"GN",
	"Tennis":"TN", "Near Beach":"BA", "Beachfront":"BF", "Casino":"CA", "Childrens Activities":"CH", "Resort":"RS", "A/C":"AC", "Condo":"C", "Kitchen":"KI", "24hr Front Desk":"HF", "Studio":"ST",
	"Front Desk":"FD", "1BR":"1B", "Daily Housekeeping":"DH", "Free Parking":"FP", "Laundry (in room)":"WD", "Smoke-free":"SR", "Smoke Free Rooms":"SR", "Smoke-Free":"SR", "Smoke free":"SR",
	"Pools":"PO", "Restaurants":"RE", "Hi-Speed internet":"HS", "24 Hour Front Desk":"HF", "Fully Equipped Kitchen":"FK", "Hi Speed Internet":"HS", "HI-Speed Internet":"HS",
	##spelling mistake cases
	"Suttlle":"AS", "Shuttlle":"AS",
	"Bussines":"BC",
	"Restuarant":"RE", "Restauraunt":"RE", "Restauant":"RE", "Restraurant":"RE", "Restaraunt":"RE", "Restaruant":"RE",
	"Fintess":"FC",
	"Complimetnary Breakfast":"CB", "Complementary Breakfast":"CB", "Comlimentary Breakfast":"CB", "Complimentry Breakfast":"CB", "Complimentary breakfast":"CB", "Comlimentary Breakfast":"CB",
	"Complimentry Breakfast":"CB",
	"Hi-Speed Interent":"HS", "Hi-Speed Intenet":"HS",
	"Pooll":"PO",
	"Kitchnette":"KI", "Kithenette":"KI", "Kithchenette":"KI",
	"Laundy":"LF", "Laudry":"LF",
	"Front Deks":"FD",
	"Children Activities":"CH",
	"Spa)":"SF",
	"&lt;none supplied by user&gt;":"None", "&lt;none shown by hotwire&gt;":"None", "&lt;none shown by Hotwire&gt;":"None", "&lt;none supplied&gt;":"None"	
	}
	
	amenity_items = re.split("\,", amenity)
	items_list_code = [] 
	for item in amenity_items:
		item = re.sub("^\s+", "", item) ##remove whitespace infront of amenity element
		item = re.sub("\s+$", "", item)
		if item in amenities_element_dict.keys():
			items_list_code.append(amenities_element_dict[item])
	
	return items_list_code

		


for instance in all_hotwire_hotels.all():

	##gets the city name of the bbhw hotel in question
	# gets rid of possible (region_name) in the city name
	bbhw_hotel_city = instance.city_area
	region_in_city_detect = re.search(".*(?=\()", bbhw_hotel_city)
	if region_in_city_detect:
		bbhw_hotel_city = region_in_city_detect.group()
	
	bb_amenity_info = generate_amenity_list(instance.amenities) ## make amenity list func turns raw amenity info into a list to compare
		
	possible_match = session.query(HotWireHotelInfo).filter(HotWireHotelInfo.city == bbhw_hotel_city)
	
	for match in possible_match:
	
		amenity_info = get_hotwire_amenity_info(match.amenity_list) ##function that gets amenity info from hotwirehotelinfo 
		
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
	
		
