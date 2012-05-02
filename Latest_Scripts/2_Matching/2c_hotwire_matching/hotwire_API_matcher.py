import Levenshtein
import re
import time
import sys
import pdb

sys.path.insert(0, "/home/areek/Documents/fetchopia/backend_git/sql/alchemy/" )

from sqlalchemy import *
from alchemy_session import get_alchemy_info


from processed_forum_data_hotwire import ProcessedRawForumData_hotwire
from matched_forum_hotel_hotwire_table import MatchedForumHotelTable
from hotwire_tables import *
from canon_hotel import CanonicalHotel


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

def main_match():
	
	bbhw_matched = session.query(MatchedForumHotelTable) ##all matched bbhw scraped to internal entries
	hotwire_hotels = session.query(HotWireHotelInfo) ##official hotwire.com hotel entries to match
	
	#1 loop through each hotwire.com hotel and find bbhw hotels within its neighborhood coords
	for hotel in hotwire_hotels.all():
	
		##making the ray casting region
		neighborhood = session.query(Neighborhood).filter(Neighborhood.uid == hotel.neighborhood_uid).one()	
		points = session.query(PointListEntry).filter(PointListEntry.listid == neighborhood.point_list)
		points_list = []
		for point in points.all():
			point_id = point.pid
		 	point_entry = session.query(Point).filter(Point.uid == point_id).first()
		 	point_lat = point_entry.latitude
		 	point_lon = point_entry.longitude
		 	pair = (point_lat, point_lon)
		 	points_list.append(pair)
		
	
		regions_coords = ray_casting.make_region(neighborhood.name, points_list)
		hotel_star = hotel.star_rating		
		
		# for each bbhw entry, check if the hotel lat long belongs to the official hotwire.com'sneighborhood
		
		for instance in bbhw_matched.all():					
		
			bbhw_info = session.query(ProcessedRawForumData_hotwire).filter(ProcessedRawForumData_hotwire.uid == instance.forum_hotel_id).first()
			internal_info = session.query(CanonicalHotel).filter(CanonicalHotel.uid == instance.hotel_id).first()
			
			if ray_casting.ispointinside(Pt(x=internal_info.latitude, y=internal_info.longitude),regions_coords):
			
				print "REGION match"
				##get amenity in list form for comparison
				bbhw_amenity = generate_amenity_list(bbhw_info.amenities)
				hotwire_hotel_amenity = get_hotwire_amenity_info(hotel.amenity_list)
				
				amenity_item_match_count = 0
				##count amenity items that are same
				for item in bbhw_amenity:
					if item in hotwire_hotel_amenity:
						amenity_item_match_count += 1
					
				amenity_match_percentage = amenity_item_match_count / len(hotwire_hotel_amenity)
				##if star is same and amenity match is good
				if float(bbhw_info.star) == hotel_star and amenity_match_percentage > float(0.9):
						
					print "FULL match"
					#hotel.processing_status = instance.uid
					#session.commit()

					
			
		
			

#main_match()

		
		
		
	
		
