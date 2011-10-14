
from sqlalchemy import *

from alchemy_session import get_alchemy_info

from priceline_area_table import PricelineAreaTable
from city_table import CityTable

(engine, session, Base, metadata) = get_alchemy_info ()

debug_level = 0

#   Database Mapper Class for priceline_area_city table

#   This table relates priceline areas to our internal cities (which internal cities are made up of a priceline area?)

class PricelineAreaCityTable(Base) :

    __tablename__ = 'priceline_area_city_table'

    uid = Column(Integer, Sequence('priceline_area_city_sequence'), primary_key=True)  #   primary key
    priceline_area_id =  Column(Integer, ForeignKey('priceline_area_table.uid'))  #   foreign key for priceline area
    city_id =  Column(Integer, ForeignKey('city.uid'))  #   foreign key for internal city


    def __init__(self, uid, priceline_area_id,city_id) :

        #   Assign params to member variables

        self.uid = uid
        self.priceline_area_id = priceline_area_id
        self.city_id = city_id


    def __str__(self) :

        #   pretty printing

        return "< priceline_area_city priceline_area_id = %s self.city_id = %s >" % (self.priceline_area_id,self.city_id)


metadata.create_all(engine)