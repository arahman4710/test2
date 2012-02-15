import string
import sys
import datetime
import canon_hotel
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker, scoped_session
# the declarative stuff lets you use objects with defined columns
# instead of creating the tables using DDL or the like
from sqlalchemy.ext.declarative import declarative_base

#sys.path.insert(0, "/work/jeff/backend/sql/alchemy/" )
#sys.path.insert(0, "C:/Documents and Settings/proj/fetchopia/hotels/hotwire/sql" )
from alchemy_session import get_alchemy_info

(engine, session,Base, metadata) = get_alchemy_info ()

debug_level = 0

# set up base class for sqlalchemy
# all our classes that mirror the database will have this as a base

#
# this table reflects (pretty much 1-1) the information in the
# http://affiliates.hotelscombined.com
# the standard feed (do we need the advanced feed?)
# database - and there will be code to reload the table
# from their csv file
# also see the wiki page at
# https://github.com/fetchopia/scraping/wiki/Hotel-table
#

#from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey
#metadata = MetaData()
class Hotel_Combined (Base):
   __tablename__ = 'hotel_combined' # set the table name

   uid           = Column(Integer(),\
                          Sequence('hotel_combined_sequence'),\
                          primary_key=True)
   combined_id     = Column(Integer())
   hotel_name      = Column(String()) # Unique hotel name
   address         = Column(String()) # The hotel's address
   city            = Column(String()) # Name of the city
   state_code      = Column(String()) # Name of the state (Optional)
   country_code    = Column(String()) # Two letter unique country code
   currency_code   = Column(String()) # currency code
   latitude        = Column(Float())  # The geographical latitude of the hotel
   longitude       = Column(Float())  # The geographical longitude of the hotel
   property_type   = Column(Integer())# An Enumerator for the type of the hotel
   hotel_image     = Column(String()) # http://media.hotelscombined.com/HI[hotel_image].jpg
   rating          = Column(Float()) # rating
   min_rate        = Column(Float()) # min. rate per night
   consumer_rating = Column(Float()) # consumer rating
   num_review      = Column(Integer())# number of review
   chain_id        = Column(String()) # The chain ID for this hotel
   facilities      = Column(String()) # Facility code; sep. by '|'

   def __init__(self, valuesdict) :
      for i in valuesdict : self.__setattr__(i, valuesdict[i])
      session.add(self)
      session.commit()

class Facility_Combined(Base) :
   __tablename__ = "facility_combined"

   uid = Column(Integer(),\
                Sequence('facility_combined_sequence'),\
                primary_key='True')
   facility_id   = Column(Integer())
   facility_name = Column(String())
   facility_type = Column(Integer())

   def __init__(self, valuesdict) :
      for i in valuesdict : self.__setattr__(i, valuesdict[i])
      session.add(self)
      session.commit()

metadata.create_all(engine)

# Property types are an Integer with the following possible values :
   # 0 - Hotel
   # 1 - Motel
   # 2 - Inn
   # 3 - Bed & Breakfast
   # 4 - Vacation Rental
   # 5 - Hostel
   # 6 - Retreat
   # 7 - Resort
   # 8 - Other
   # 9 - Apartment
