

from sqlalchemy import *
import decimal
from alchemy_session import get_alchemy_info


(engine, session, Base, metadata) = get_alchemy_info ()

debug_level = 0

#   Database Mapper Class for priceline_region table

#   This table contains all information regarding priceline regions

class PricelineRegionTable(Base) :

    __tablename__ = 'priceline_region_table'

    uid = Column(Integer, Sequence('priceline_region_sequence'), primary_key=True)  #   primary key
    priceline_id =  Column(Integer())  #   priceline id retrived from scraping priceline system
    name =  Column(String(500))  #   name of the priceline region
    latitude = Column(Float())    #   latitude of the center of the region
    longitude = Column(Float())    #   longitude of the center of the region
    active = Column(Integer())  #   Determines whether the region is active or not
    star_availability = Column(String(500))    # this is a bitstring representing the presence of hotel with a specific star the bitstring is formatted as follows ( 5 4.5 4 3.5 3 2.5 2 1 => 4.5 being resorts )

    def __init__(self, uid, priceline_id, name,latitude,longitude, active,star_availability ) :

        #   Assign params to member variables

        self.uid = uid
        self.priceline_id = priceline_id
        self.name = name
        self.latitude = latitude
        self.longitude = longitude
        self.active = active
        self.star_availability = star_availability

    def __str__(self) :

        #   pretty printing

        return "< priceline_region name = %s position = (%s, %s) star_availability = %s >" % (self.name,self.latitude,self.longitude,self.star_availability)


metadata.create_all(engine)