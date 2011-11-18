 # This script finds all regions for priceline and then maps Canonical hotels to these regions, the region hotel relationship is stored in PricelineRegionHotelMap table


import ray_casting
from collections import namedtuple
from sql import alchemy_session
from sql.alchemy.canon_hotel import CanonicalHotel
from sql.alchemy.priceline_city_region_map import PricelineCityRegionMap
from sql.alchemy.priceline_region_hotel_map import PricelineRegionHotelMap
from sql.alchemy.priceline_regions_table import PricelineRegionTable
from sql.alchemy.priceline_region_point_table import PricelineRegionPointTable

(engine, session,Base, metadata) = alchemy_session.get_alchemy_info()

Pt = namedtuple('Pt', 'x, y')

def region_finder():
    regions_dictionary ={}

    pl_region_recs = session.query(PricelineRegionTable).all()

    for region in pl_region_recs:
        region_points = session.query(PricelineRegionPointTable.latitude,PricelineRegionPointTable.longitude)\
        .filter(PricelineRegionPointTable.priceline_region_id == region.uid).order_by(PricelineRegionPointTable.order_id).distinct().all()
     
        regions_dictionary[region.uid] = ray_casting.make_region(region.name,region_points)
        
    return regions_dictionary


def region_mapper(regions_dictionary):
    
    hotels = session.query(CanonicalHotel).all()
    
    for hotel in hotels:
        
        for region in regions_dictionary.keys():
            
             if ray_casting.ispointinside(Pt(x=hotel.latitude, y=hotel.longitude),regions_dictionary[region]):
                
                existing_record  = session.query(PricelineRegionHotelMap).filter(PricelineRegionHotelMap.hotel_id == hotel.uid).filter(PricelineRegionHotelMap.priceline_region_id == region).count()
                
                if not existing_record:
                    
                    region_hotel_map_rec = PricelineRegionHotelMap(hotel.uid,region)
                    session.add(region_hotel_map_rec)
	session.commit()
                    


if __name__ == "__main__":
    
   
    region_mapper(region_finder())
