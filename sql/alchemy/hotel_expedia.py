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
class Hotel_Expedia (Base):
   __tablename__ = 'hotel_expedia' # set the table name

   uid              = Column(Integer(),\
                             Sequence('expedia_info_sequence'),\
                             primary_key=True)
   expedia_id       = Column(Integer())# Unique id (from expedia)
   hotel_name       = Column(String()) # Unique hotel name
   country_code     = Column(String()) # Two letter unique country code
   low_rate         = Column(Float())  # The average low rate
   high_rate        = Column(Float())  # The average low rate
   desp_location    = Column(String()) # Brief desp. of the hotel and its location
   desp_facility    = Column(String()) # Brief desp of the hotel facility
   desp_guestroom   = Column(String()) # Brief desp of the guest room amenties
   desp_fees_etc    = Column(String()) # Various fees in string sep. by '|'
   desp_nearby_attr = Column(String()) # Near by attractions in string sep. by '|'
   facilities       = Column(String()) # facility codes sep. by '|'
   num_rooms        = Column(String()) # number of rooms
   num_suites       = Column(String()) # number of suites
   num_floors       = Column(String()) # number floors

   def __init__(self, valuesdict) :
      for i in valuesdict : self.__setattr__(i, valuesdict[i])
      session.add(self)
      session.commit()

class Facility_Expedia(Base) :
   __tablename__ = "facility_expedia"

   uid = Column(Integer(),\
                Sequence('facility_expedia_sequence'),\
                primary_key='True')
   facility_id   = Column(Integer())
   facility_name = Column(String())
   facility_type = Column(Integer())

   def __init__(self, valuesdict) :
      for i in valuesdict : self.__setattr__(i, valuesdict[i])
      session.add(self)
      session.commit()

metadata.create_all(engine)
