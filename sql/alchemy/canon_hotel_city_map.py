from sqlalchemy import *
from alchemy_session import get_alchemy_info
(engine, session, Base, metadata) = get_alchemy_info ()

debug_level = 0

#   Database Mapper Class for Canon hotel city map

#   This table map the hotels for the cities 

class CanonHotelCityMap(Base) :

    __tablename__ = 'canon_hotel_city_map'

    uid = Column(Integer, Sequence('canon_hotel_city_map_sequence'), primary_key=True)
    hotel_id = Column(Integer())  #   id of the canon hotel id
    city_id = Column(Integer())   #   id of the city

    def __init__(self, hotel_id,city_id) :

        #   Assign the params to the member variables
        self.hotel_id = hotel_id
        self.city_id = city_id

    def __str__(self) :

        #   pretty printing

        return "< canon_hotel_city_map hotel_id=%d city_id=%s >" % (self.hotel_id, self.city_id)


metadata.create_all(engine)
