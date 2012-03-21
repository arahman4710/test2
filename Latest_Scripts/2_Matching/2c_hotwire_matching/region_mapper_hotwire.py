 # This script finds all regions for priceline and then maps Canonical hotels to these regions, the region hotel relationship is stored in PricelineRegionHotelMap table
import sys

sys.path.insert(0, "/home/areek/Documents/fetchopia/backend_git/sql/alchemy/" )

import ray_casting
from collections import namedtuple
from alchemy_session import get_alchemy_info
from canon_hotel import CanonicalHotel
from hotwire_region_hotel_map import HotWireRegionHotelMap

from hotwire_tables import *


(engine, session,Base, metadata) = get_alchemy_info()


Pt = namedtuple('Pt', 'x, y')

def region_finder():
    regions_dictionary ={}

    pl_region_recs = session.query(Neighborhood).all()

    for region in pl_region_recs:
    
	points = session.query(PointListEntry).filter(PointListEntry.listid == region.point_list)
	points_list = []
	for point in points.all():
		 point_id = point.pid
		 point_entry = session.query(Point).filter(Point.uid == point_id).first()
		 point_lat = point_entry.latitude
		 point_lon = point_entry.longitude
		 pair = (point_lat, point_lon)
		 points_list.append(pair)
	
	regions_dictionary[region.uid] = ray_casting.make_region(region.name, points_list)

    return regions_dictionary
	
			    
#    	points = eval(region.points)     
#        regions_dictionary[region.uid] = ray_casting.make_region(region.name,points)
        
#    return regions_dictionary


def region_mapper(regions_dictionary):
    
    hotels = session.query(CanonicalHotel).filter(CanonicalHotel.country_code == "US").all()
    
    for hotel in hotels:
        
        for region in regions_dictionary.keys():
            
             if ray_casting.ispointinside(Pt(x=hotel.latitude, y=hotel.longitude),regions_dictionary[region]):
                
                entry = HotWireRegionHotelMap(hotel.uid, region)
                session.add(entry)
                session.commit()
                
                
                    


if __name__ == "__main__":
    
   
    region_mapper(region_finder())
