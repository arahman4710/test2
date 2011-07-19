import string 
import datetime 

from sqlalchemy import * 
from sqlalchemy.orm import sessionmaker, scoped_session

# the declarative stuff lets you use objects with defined columns
# instead of creating the tables using DDL or the like

from sqlalchemy.ext.declarative import declarative_base

debug_level = 0 

engine = create_engine('postgresql:///testing', echo=True)
Session = scoped_session(sessionmaker(bind=engine)) 
session = Session() 

# set up base class for sqlalchemy 
# all our classes that mirror the database will have this as a base 

Base = declarative_base() 
metadata = Base.metadata

#
# this table reflects (pretty much 1-1) the information in the
# http://affiliates.hotelscombined.com
# the standard feed (do we need the advanced feed?) 
# database - and there will be code to reload the table
# from their csv file 
# also see the wiki page at 
# https://github.com/fetchopia/scraping/wiki/Hotel-table
# 
class CanonicalHotel(Base) : 
   __tablename__ = 'canonical_hotel'  # set the table name 
   
   uid = Column(Integer(),  Sequence('canon_hotel_sequence'), primary_key=True)
   hotel_id= Column(Integer())        #   Unique id (from hotelscombined) 
   hotel_filename= Column(String())   #   Redirection url to view hotel details/rates. http://www.hotelscombined.com/Hotel/[hotelFileName].htm?a_aid=21174
   hotel_name= Column(String())       #   Unique hotel name
   rating= Column(String())           #   Star rating
   city_id= Column(Integer())         #   Unique id for the city
   city_filename= Column(String())    #   Redirection url for city page. http://www.hotelscombined.com/City/[cityFileName].htm?a_aid=21174
   city_name= Column(String())        #   Name of the city
   state_id= Column(String())         #   Unique id for the state (Optional)
   state_filename= Column(String())   #   Redirection url for the state page. http://www.hotelscombined.com/State/[stateFileName].htm?a_aid=21174 (Optional)
   state_name= Column(String())       #   Name of the state (Optional)
   country_code= Column(String())     #   Two letter unique country code
   country_filename= Column(String()) #   Redirection url for the country page. http://www.hotelscombined.com/Country/[countryFileName].htm?a_aid=21174
   country_name= Column(String())     #   Name of the country
   image_id= Column(String())         #   The hotel's default image. The format is http://media.hotelscombined.com/HI[imageid].jpg e.g. For the imageId '123456' the URL will be http://media.hotelscombined.com/HI123456.jpg and for the thumbnail the URL will be http://media.hotelscombined.com/HT123456.jpg
   address= Column(String())          #   The hotel's address
   min_rate= Column(Float())          #   The average low rate
   currency_code= Column(String())    #   The currency code for the 'minRate' column
   location = Column(Integer())       #   a reference to a Point
   # Latitude= Column(String())       #   The geographical latitude of the hotel
   # Longitude= Column(String())      #   The geographical longitude of the hotel
   number_of_reviews= Column(Integer())#   The number of times this hotel has been reviewed
   consumer_rating= Column(Float())   #   The overall rating for this hotel
   property_type= Column(Integer())   #   An Enumerator for the type of the hotel. See wiki  
   chain_id= Column(String())         #   The chain ID for this hotel
   facilities_list = Column(Integer())       # a list of amenities at this hotel 

   def __init__(self, valuesdict) : 
      for i in valuesdict :
         self.__setattr__(i, valuesdict[i]) 
      session.add(self)
      session.commit()

class FacilitiesList(Base) :
   __tablename__ = "facilities_list"

   uid = Column(Integer(), Sequence('facilities_list_sequence'), primary_key='True')
   string_value = Column(String())

   def __init__(self, facilities_string) :
      self.string_value = facilities_string
      session.add(self)
      session.commit() 
      
def find_facilities_list(str) :
   reslist = session.query(FacilitiesList).filter_by(string_value=str).all() 
   if reslist : 
      return reslist[0] 
   else :
      return FacilitiesList(str) 

def get_hotel_by_id(hotelId) :
   return session.query(CanonicalHotel).filter_by(hotel_id=int(hotelId)).scalar()
   
metadata.create_all(engine) 
      
# Property types are an Integer with the following possible values :
   #   0 - Hotel
   #   1 - Motel
   #   2 - Inn
   #   3 - Bed & Breakfast
   #   4 - Vacation Rental
   #   5 - Hostel
   #   6 - Retreat
   #   7 - Resort
   #   8 - Other
   #   9 - Apartment
