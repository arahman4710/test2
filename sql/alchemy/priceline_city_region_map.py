
from sqlalchemy import *

from alchemy_session import get_alchemy_info

from hotel import Hotel

(engine, session, Base, metadata) = get_alchemy_info ()

debug_level = 0


#   Database Mapper Class for priceline_regions_cities_mapping table


#   This table will relate internal cities in the db with existing priceline regions!


class PricelineCityRegionMap(Base) :

	__tablename__ = 'priceline_regions_cities_mapping'

	uid = Column(Integer, Sequence('priceline_regions_cities_mapping_sequence'), primary_key=True)  #   primary key
	city_id = Column(Integer, ForeignKey('hotels.hotel_id'))   #   primary key for internal city
	priceline_region_id = Column(String(100))   #    priceline regions id


	def __init__(self, uid, cities_cityid, priceline_regionid) :
		#   Assign params to member variables

            self.uid = uid
            self.city_id = cities_cityid
            self.priceline_region_id = priceline_regionid

	def __str__(self) :

        #   pretty printing

		return "< regionscitiesmap cities_cityid = %s priceline_region_id = %s >" % (self.city_id, self.priceline_region_id)

metadata.create_all(engine)