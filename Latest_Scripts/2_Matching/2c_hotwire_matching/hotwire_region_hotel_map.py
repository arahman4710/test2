
from sqlalchemy import *

from alchemy_session import get_alchemy_info

from canon_hotel import CanonicalHotel
from hotwire_tables import Neighborhood

(engine, session, Base, metadata) = get_alchemy_info ()

debug_level = 0

#   Database Mapper Class for region hotel mapper table

#   This table keeps records of which internal hotels map to which priceline regions

#   This is stored in tables so that it becomes alot easier to figure out which hotels are in a specific region when matching hotels from forums

#   !NOTE: Ideal case would be to add another field to indicate which target site the hotel_id, region_id pair is for, rather then having a seperate table like this one for hotwire

class HotWireRegionHotelMap(Base) :

    __tablename__ = 'hotwire_region_hotel_mapping'

    uid = Column(Integer, Sequence('priceline_region_hotel_mapping_sequence'), primary_key=True)    #   primary key
    hotel_id = Column(Integer, ForeignKey('canonical_hotel.uid')) #   primary key for the internal hotel that is in question
    hotwire_neighborhood_id = Column(Integer())    #   primary key for the priceline region in question


    def __init__(self, hotel_id, hotwire_neighborhood_id):

        #   At initialization, assign all the params to their respective member variables

        self.hotel_id = hotel_id
        self.hotwire_neighborhood_id = hotwire_neighborhood_id


    def __str__(self) :

        #   Pretty printing

        return "< region_hotel hotel_id=%s pl_region_id=%s >" % (self.hotel_id, self.hotwire_neighborhood_id)


metadata.create_all(engine)