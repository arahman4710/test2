import string
import sys
import datetime

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
class CanonicalHotel (Base):
   __tablename__ = 'canonical_hotel' # set the table name

   uid          = Column(Integer(), Sequence('canon_hotel_sequence'), primary_key=True)
   hotel_id     = Column(Integer())# Unique id (from hotelscombined)
   hotel_name   = Column(String()) # Unique hotel name
   address      = Column(String()) # The hotel's address
   city         = Column(String()) # Name of the city
   state_code   = Column(String()) # Name of the state (Optional)
   country_code = Column(String()) # Two letter unique country code
   postal_code  = Column(String()) # Postal code
   low_rate     = Column(Float())  # The average low rate
   high_rate    = Column(Float())  # The average low rate
   currency_code= Column(String()) # The currency code for the 'minRate' column
   latitude     = Column(Float())  # The geographical latitude of the hotel
   longitude    = Column(Float())  # The geographical longitude of the hotel
   property_type= Column(String())# An Enumerator for the type of the hotel. See wiki
   chain_name   = Column(String()) # The chain ID for this hotel
   status_code  = Column(String()) # Hotel data source Indicator 

   def __init__(self, valuesdict) :
      for i in valuesdict : self.__setattr__(i, valuesdict[i])
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
