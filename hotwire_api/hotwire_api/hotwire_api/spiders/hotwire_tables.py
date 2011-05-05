import datetime 

from sqlalchemy import * 
from sqlalchemy.orm import sessionmaker


# the declarative stuff lets you use objects with defined columns
# instead of creating the tables using DDL or the like

from sqlalchemy.ext.declarative import declarative_base

debug_level = 0 

# set up base class for sqlalchemy 
# all our classes that mirror the database will have this as a base 

Base = declarative_base() 

# if echo=True it gives verbose info on the sql 
engine = create_engine('postgresql:///testing', echo=True)
# engine = create_engine('mysql://jefu:@localhost/testing', echo=True)

# factory to build the proper Session class 
Session = sessionmaker(bind=engine) 
# and instantiate it 
session = Session() 
# this will be used to create the tables - done after class definitions 
metadata = Base.metadata

class Amenity(Base) : 
   __tablename__ = 'amenity'    # set the table name 
 
   # variables declared in a class using "Column"
   # these are going to be reflected in the table built
   # other variables in the class will not 
   uid  = Column(Integer, primary_key=True) 
   name = Column(String())               
   code = Column(String())  
   description = Column(String()) 

   def __init__(self, namesdict) : 
       for i in namesdict : 
           self.__setattr__(i, namesdict[i]) 
       session.add(self) 
       session.commit() 

class AmenityList(Base) :
    __tablename__ = 'amenity_list' 

    uid = Column(Integer, Sequence('amenity_list_sequence'), primary_key=True)

    def __init__(self, amenitylist) : 
        session.add(self) 
        session.commit() 
        for i in amenitylist :
            amenity = session.query(Amenity).filter_by(code=i).all() 
            AmenityListItem(self.uid, amenity[0].uid) 
            
class AmenityListItem(Base) :
    __tablename__ = 'amenity_list_item'

    uid = Column(Integer, Sequence('amenity_list_item_sequence'), primary_key=True) 
    amenity_list_id = Column(Integer,  ForeignKey('amenity_list.uid'))
    amenity_id = Column(Integer, ForeignKey('amenity.uid')) 

    def __init__(self, listid, amid) : 
        self.amenity_id = amid 
        self.amenity_list_id = listid  
        session.add(self) 
        session.commit() 

class Neighborhood (Base) : 
   __tablename__ = 'neighborhood'
   
   uid = Column(Integer, Sequence('neighborhood_sequence'), primary_key=True) 
   id = Column(String())
   name = Column(String())
   city = Column(String())
   state = Column(String())
   country = Column(String())
   centroid = Column(Integer, ForeignKey('point.uid'))
   point_list = Column(Integer(), ForeignKey('point_list.uid')) 

   def __init__(self, namesdict) : 
       for i in namesdict : 
           self.__setattr__(i, namesdict[i]) 
       session.add(self)
       session.commit() 
 
class HotWireHotelInfo (Base) : 
   __tablename__ = 'hotwire_hotel_info'

   uid = Column(Integer, Sequence('hotwire_hotel_sequence'), primary_key=True) 
   datetime_fetched = Column(Date(), default=datetime.datetime.now()) 
   processing_status = Column(String())  
   currency_code = Column(String())
   deep_link = Column(String())
   result_id = Column(String())
   hw_ref_number = Column(String())
   subtotal = Column(Float()) 
   taxes_and_fees = Column(Float())
   total_price = Column(Float())
   amenity_list = Column(Integer, ForeignKey('amenity_list.uid'))
   checkin_date = Column(Date())
   checkout_date = Column(Date())
   neighborhood_uid = Column(Integer, ForeignKey('neighborhood.uid')) 
   neighborhood_id = Column(String())
   lodging_type_code = Column(String())
   average_price_per_night = Column(Float())
   star_rating = Column(Float())
   rooms = Column(Integer())

   def __init__(self, namesdict) : 
       for i in namesdict :   # simple attribute setting 
           if debug_level > 5 :
               print i, namesdict[i] 
           self.__setattr__(i, namesdict[i]) 

       self.checkin_date = fix_date(self.checkin_date) 
       self.checkout_date = fix_date(self.checkout_date) 
       self.amenity_list = AmenityList(self.amenity_codes).uid
       neighborhood = session.query(Neighborhood).filter_by(id=self.neighborhood_id).all()
       self.neighborhood_uid = neighborhood[0].uid 

       self.processing_status = 'unprocessed' 
       if debug_level > 5 : 
           print "neighborhood_uid = ", self.neighborhood_uid 

       session.add(self)
       session.commit()
       
def get_amenity(c) : 
    amenity = session.query(Amenity).filter_by(code='code').one()
    return amenity 

# date in format separated by "/" (m/d/y) change to " and (y:m:d) 
def fix_date(d) : 
    x = d.split('/')
    return "-".join([x[2], x[0], x[1]]) 

class PointList(Base) :
    __tablename__ = 'point_list'

    uid = Column(Integer, Sequence('point_list_sequence'), primary_key=True) 

    def __init__(self, points) : 
        if debug_level > 5 : 
           print "building point list from :", points 
        session.add(self) 
        session.commit() 
        for (i, lati, longi) in points : 
            pt = find_point(lati, longi) 
            ple = PointListEntry(self.uid, pt.uid, i)
        
class PointListEntry(Base) :
    __tablename__ = 'point_list_entry'
    uid = Column(Integer, Sequence('pointlist_entry_sequence'), primary_key=True) 
    listid = Column(Integer, ForeignKey('point_list.uid')) 
    pid = Column(Integer, ForeignKey('point.uid')) 
    index = Column(Integer) 

    def __init__(self, listid, pointid, index) :
        if debug_level > 5 : 
            print "point list entry for ", listid, pointid, index 
        self.pid = pointid
        self.listid = listid
        self.index = index 
        session.add(self)    # adds to database
        session.commit()     # commits the add and reads back - for instance the uid 

def find_point(lati, longi) :
    reslist = session.query(Point).filter(and_(Point.latitude==lati, Point.longitude==longi)).all() 
    if reslist :
        if debug_level > 5 : 
            print "find point finds point in db" 
        res = reslist[0]
    else : 
        res = Point(lati, longi) 
    if debug_level > 5 : 
        print "find point for lati=%s longi=%s returns point (%s,%s,%s)" % (lati, longi, res.uid, res.latitude, res.longitude) 
    return res 

class Point(Base) :     
    __tablename__ = 'point'

    uid = Column(Integer, Sequence('point_sequence'), primary_key=True) 
    latitude = Column(Float) 
    longitude = Column(Float) 

    def __init__(self, lati, longi) :
        self.latitude = lati
        self.longitude = longi 
        session.add(self) 
        session.commit() 
        if debug_level > 5 : 
            print "new point uid=%d lat=%s long=%s" % (self.uid, self.latitude, self.longitude)
