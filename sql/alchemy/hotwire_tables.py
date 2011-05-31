import datetime 
import sys

if '/work/jeff/backend/sql/alchemy' not in sys.path :
   sys.path.insert(0,'/work/jeff/backend/sql/alchemy') 

# the declarative stuff lets you use objects with defined columns
# instead of creating the tables using DDL or the like

from sqlalchemy import * 

from alchemy_session import get_alchemy_info
from point import Point 
from amenity import Amenity, find_amenity_string

(engine, session, Base, metadata) = get_alchemy_info () 
# engine = create_engine('postgresql:///testing', echo=True)
# engine = create_engine('mysql://jefu:@localhost/testing', echo=True)

# factory to build the proper Session class 
# Session = scoped_session(sessionmaker(bind=engine) )
# and instantiate it 
# session = Session() 

debug_level = 0 

class Neighborhood (Base) : 
   __tablename__ = 'neighborhood'
   
   uid = Column(Integer, Sequence('neighborhood_sequence'), primary_key=True) 
   id = Column(String())                                           # hotwire's id for this neighborhood
   name = Column(String())                                         # hotwire name for the neighborhood
   city = Column(String())                                         # city 
   state = Column(String())                                        # state  (2 character state id) 
   country = Column(String())                                      # country (country id?) 
   centroid = Column(Integer, ForeignKey('point.uid'))             # centroid (a Point) 
   point_list = Column(Integer(), ForeignKey('point_list.uid'))    # id for ordered list of points 

   def __init__(self, namesdict) : 
       for i in namesdict : 
           self.__setattr__(i, namesdict[i]) 
       session.add(self)
       session.commit() 
 
class HotWireHotelInfo (Base) : 
   __tablename__ = 'hotwire_hotel_info'

   uid = Column(Integer, Sequence('hotwire_hotel_sequence'), primary_key=True) 
   datetime_fetched = Column(Date(), default=datetime.datetime.now())   # when this was fetched 
   processing_status = Column(String())                                 # has it been processed and if so what stage is it in 
   currency_code = Column(String())                                     # currency code the quote is in 
   deep_link = Column(String())                                         # deep link to use on hotwire - see hotwire api for more info
   result_id = Column(String())                                         # a unique id from hotwire 
   hw_ref_number = Column(String())                                     # hotwire reference number 
   subtotal = Column(Float())                                           # total for lodging 
   taxes_and_fees = Column(Float())                                     # taxes and fees 
   total_price = Column(Float())                                        # total price 
   amenity_list = Column(Integer) # , ForeignKey('amenity_list.uid'))       # a list of amenities at this hotel 
   checkin_date = Column(Date())                                        # the check in date we asked about 
   checkout_date = Column(Date())                                       # and the check out date 
   neighborhood_uid = Column(Integer, ForeignKey('neighborhood.uid'))   # neighborhood id (our neighborhood primary key) 
   neighborhood_id = Column(String())                                   # hotwire's neighborhood id 
   lodging_type_code = Column(String())                                 # lodging type code "h"= hotel etc (see hotwire api) 
   average_price_per_night = Column(Float())                            # average price per night 
   star_rating = Column(Float())                                        # star rating 
   rooms = Column(Integer())                                            # number of rooms requested 
   adults = Column(Integer())                                           # number of adults requested 
   children = Column(Integer())                                         # number of children requested 
   nights = Column(Integer())                                           # number of nights requested 
   date_offset = Column(Integer())                                      # how far in the future did we make this request for 
   city = Column(String())                                              # what city were we asking about 

   def __init__(self, namesdict, meta_dict) : 
       for i in namesdict :   # simple attribute setting 
           if debug_level > 5 :
               print i, namesdict[i] 
           self.__setattr__(i, namesdict[i]) 

       self.checkin_date = fix_date(self.checkin_date) 
       self.checkout_date = fix_date(self.checkout_date) 
       self.amenity_list = find_amenity_string(self.amenity_codes)
       neighborhood = session.query(Neighborhood).filter_by(id=self.neighborhood_id).all()
       self.neighborhood_uid = neighborhood[0].uid 

       self.processing_status = 'unprocessed' 
       if debug_level > 5 : 
           print "neighborhood_uid = ", self.neighborhood_uid 

       for i in meta_dict.items() : 
          self.__setattr__(i[0], i[1]) 

       session.add(self)
       session.commit()
       
# date in format separated by "/" (m/d/y) change to " and (y:m:d) 
def fix_date(d) : 
    x = d.split('/')
    return "-".join([x[2], x[0], x[1]]) 

metadata.create_all(engine)
