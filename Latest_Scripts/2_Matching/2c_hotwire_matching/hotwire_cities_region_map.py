
from sqlalchemy import *
from alchemy_session import get_alchemy_info


(engine, session, Base, metadata) = get_alchemy_info ()

debug_level = 0

#   Database Mapper Class for unmatched_forum_hotel_table table

#   This table will keep track of unmatched forum hotels that were not matched satisfactorily when the matching algorithm was applied

class Hotwire_cities_region_map(Base) :

    __tablename__ = 'hotwire_cities_region_map'

    uid = Column(Integer, primary_key=True)
    city = Column(String(500)) #   name of the fourm the hotel was originally scraped from
    state = Column(String(500))  #   name of the site the forums were referring to for this hotel
    country = Column(String(500))   #   the address of the page where this entry was originally scraped from
    region_name = Column(Integer())   #   can be either blank or may have the primary key of the internal hotel it was matched with after

    def __init__(self, city, state, country, region_name) :

        #   Assign the params to the member variables

        self.city = city
        self.state = state
        self.country = country
        self.region_name = region_name


metadata.create_all(engine)
