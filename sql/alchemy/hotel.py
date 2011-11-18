'''
Created on 2011-06-08

@author: Areek
'''

from sqlalchemy import * 
from sqlalchemy.orm import sessionmaker, scoped_session
# the declarative stuff lets you use objects with defined columns
# instead of creating the tables using DDL or the like
from sqlalchemy.ext.declarative import declarative_base
from alchemy_session import get_alchemy_info

from city_table import CityTable

(engine, session,Base, metadata) = get_alchemy_info () 


debug_level = 0 

class Hotel(Base) : 
    __tablename__ = 'hotels'  # set the table name
   
    hotel_id = Column(Integer(),  Sequence('canon_hotel_sequence'), primary_key=True)
    name = Column(String(255))       #   Unique hotel name
    address= Column(String(255))          #   The hotel's address
    city_id= Column(Integer, ForeignKey('city.uid'))         #   Unique id for the city
    latitude= Column(Float())       #   The geographical latitude of the hotel
    longitude= Column(Float())      #   The geographical longitude of the hotel
    rating= Column(String(255))           #   Star rating
    hotels_combined_id = Column(String(255))
    filename = Column(String(255))

    def __init__(self,id,name,address,city_id,latitude,longitude,rating,hotels_combined_id,filename):

        self.hotel_id  = id
        self.name = name
        self.address = address
        self.city_id = city_id
        self.latitude = latitude
        self.longitude = longitude
        self.rating = rating
        self.hotels_combined_id = hotels_combined_id
        self.filename = filename

    def __str__(self):

        return "< hotels name = %s >" % (self.name)

metadata.create_all(engine)
