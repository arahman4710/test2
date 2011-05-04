# scrapy imports 
from scrapy.selector import HtmlXPathSelector,XmlXPathSelector
from scrapy.http import FormRequest
from scrapy.conf import settings
from scrapy.crawler import CrawlerProcess
from scrapy.spider import BaseSpider
from scrapy import signals,log
from scrapy.xlib.pydispatch import dispatcher
from scrapy.http import Request
from scrapy.contrib.spiders import XMLFeedSpider
from scrapy.utils.response import body_or_str

#sql alchemy imports 
from sqlalchemy import * 
from sqlalchemy.sql import and_
from sqlalchemy.orm import sessionmaker
import re
import datetime 
import time
import urllib
import sys
import os 

# debug_level controls amount of debugging information written :
#  set to 0 to turn debug messages off
#  I usually use 1-3 for most important messages
#                4-6 for medium level
#                6-9 for debugging stuff that mostly nobody should have to see
#                10  for debugging stuff that nobody wants to see, but is sometimes useful

debug_level = 1


# the declarative stuff lets you use objects with defined columns
# instead of creating the tables using DDL or the like

from sqlalchemy.ext.declarative import declarative_base

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


saving_results = True  # save raw xml for debugging etc 
raw_results = None 

base_query_format = "http://api.hotwire.com/v1/search/hotel?apikey=%s&dest=%s&rooms=1&adults=2&children=0&startdate=%s&enddate=%s"

base_data_dir = "data"  # this really needs to be something better, or a database 
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
   id = Column(String(10))
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
        
def simple_extract(name, ctxt) : 
    if debug_level > 8 : 
        print "simple extract : ", name, ctxt 
    res = ctxt.select(".//%s/text()"% name).extract()[0] 
    if debug_level > 8 : 
        print "    extracts : ", res 
    return res 

# many of the results come in simple enough format that this utility
# routine simplifies extracting them and saving them
# the names to be found in the xml are the keys and the names they
# translate to as columns are the values 

def dict_extract(name_dict, ctxt) :  
    result_dict = {}
    for i in name_dict :
        if debug_level > 5 : 
            print "finding <<%s>> in xml" % i 
        result_dict[name_dict[i]] = simple_extract(i, ctxt) 
    return result_dict 

# and here are the dictionaries that dict_extract uses

amenities_element_dict = {"Name":"name", "Code":"code", "Description":"description"} 

neighborhood_element_dict = {"Id":"id", "Name":"name", "City":"city", "State":"state", "Country":"country", "Centroid":"centroid"} 

hotel_element_dict = {'TotalPrice': 'total_price', 'CheckOutDate': 'checkout_date', 'HWRefNumber': 'hw_ref_number', 'AveragePricePerNight': 'average_price_per_night', 'ResultId': 'result_id', 'CurrencyCode': 'currency_code', 'TaxesAndFees': 'taxes_and_fees', 'StarRating': 'star_rating', 'LodgingTypeCode': 'lodging_type_code', 'Rooms': 'rooms', 'NeighborhoodId': 'neighborhood_id', 'DeepLink': 'deep_link', 'SubTotal': 'subtotal', 'CheckInDate': 'checkin_date'}

# this makes all the tables - so must come after class definitions 
metadata.create_all(engine) 

def do_amenities(amenities) :
    return [do_amenity(i) for i in amenities ] 

def do_amenity(amenity) : 
    if debug_level > 5 : 
        print "do_amenity :", amenity 
    info = dict_extract(amenities_element_dict, amenity) 
    if debug_level > 5 : 
        print "amenity info :", info 
    am = session.query(Amenity).filter_by(code=info['code']).all() 
    if am :
        return am[0].uid 
    am = Amenity(info) 
    return am.uid 

def do_neighborhoods(neighborhoods) :
    return [do_one_neighborhood(i) for i in neighborhoods] 

def do_one_neighborhood(nb) : 
    print "do one neighborhood" 
    result_dict = dict_extract(neighborhood_element_dict, nb)  
    nresult = session.query(Neighborhood).filter_by(id=result_dict['id']).all() 
    if nresult :   # we have it already 
        return nresult[0]
     
    [clat, clong] = map(float, result_dict["centroid"].split(",")) 
    result_dict['centroid'] = find_point(clat, clong).uid 
    
    if debug_level > 8 : 
        print "About to do points" 
    points = nb.select(".//Shape/LatLong/text()")
    if debug_level > 8 : 
        print "points : ", points 
    point_list = [] 
    for i in enumerate(points) :
        if debug_level > 8 : 
            print "doing a point :", i 
            print "i[1]=", i[1] 
            print "i[1].extract()=", i[1].extract() 
        [point_lat, point_long] = map(float, i[1].extract().split(",")) 
        point_list.append((i[0], point_lat, point_long)) 
    result_dict["point_list"] = PointList(point_list).uid 
    return Neighborhood(result_dict) 

def do_hotels(hotel_list) :
    return [do_hotel(h) for h in hotel_list] 

def do_hotel(hotel) :
    if debug_level > 7 :     
        print hotel
    dict = dict_extract(hotel_element_dict, hotel) 
    amenity_codes_raw = hotel.select(".//AmenityCodes/Code/text()") 
    if debug_level > 8 : 
        print amenity_codes_raw 
    amenity_codes = [i.extract() for i in amenity_codes_raw]
    if debug_level > 8 : 
        print amenity_codes 
    dict['amenity_codes'] = amenity_codes 
    x = HotWireHotelInfo(dict)
    session.add(x) 
    session.commit()

# this makes all the tables - so must come after class definitions 
metadata.create_all(engine) 

def gendate(offset, cursecs) : 
    """
    given an offset (number of days in the future to check) this returns a pair of strings
    (start_date, end_date) that is that number of days into the future and the day after
    that.

    Do this by getting the time, adding the right number of seconds and converting using
    strftime - which avoids having to cope with month endings by hand
    """ 
    startgmt = time.gmtime(cursecs + offset * 24 * 60 * 60)    # offset days in the future 
    endgmt = time.gmtime(cursecs + (offset+1) * 24 * 60 * 60)  # offset + 1 days in the future 
    start_date = time.strftime("%m/%d/%Y", startgmt)    #start date in the format mm/dd/yyyy
    end_date = time.strftime("%m/%d/%Y", endgmt)      #end date in the format mm/dd/yyyy
    return (start_date, end_date) 

class hotwire_api_analysis(BaseSpider):
    """
    uses a list of cities to query the hotwire api for specific dates offset from the current
    date.

    Grabs information from the returned xml and saves it all to a file named "year-day.result"
    where day is the day number in the year (this avoids month ending problems and the like)


    Each hotel_info query returns a 'HWRefNumber' which is then linked into the hotel_page query results. 

    Each query result also includes a fetch_time which is in seconds past the epoch.   Informational, but
    may be handy.  
    """ 
    name = "hotwire_api"
    DOWNLOAD_DELAY = 0.5
    allowed_domains = ["hotwire.com"]
    input = []
    hotel_count=0
    review_count = 0

    #List of names of cities to query - this and the offset list should ideally be read
    # from a file or database.
    
    # city_names =['Houston, Texas, USA','Toronto','New York, New York','Los Angeles, California','Chicago, Illinois','Ottawa, ON Canada','Vancouver, BC Canada','Calgary, AB Canada','Boston, Massachusetts','Anchorage, AK']
    # city_names = ['Anchorage, AK'] 
    city_names = ['Boston, MA'] 
    # date_offsets = [0, 7, 14]  # offsets in days from today 
    date_offsets = [0] 
    api_key='eupzwn43dwtmgxhmkw5pbta7'
    diff = 4

    nowsecs = time.time() 

    date_list = [gendate(i, nowsecs) for i in date_offsets ] 

    yearday = time.strftime("%Y-%j", time.localtime())  # year and day of year - used both in directory and filename
    hourmin = time.strftime("%H-%M", time.localtime())  # hour and minute - used in filename to avoid overwriting
    result_file_dir =  os.path.join(base_data_dir, yearday) 
    try : 
        os.makedirs(result_file_dir) 
    except : 
        log.msg("failed to make output directory: " + result_file_dir, level=log.WARNING) 
    result_file_name = os.path.join(base_data_dir, yearday, "hotel_info-%s-%s" % (yearday, hourmin)) 
    result_file = open(result_file_name, "w")  # year + day of year 

    start_urls = [base_query_format % (api_key, city_name, start_date, end_date) for city_name in city_names for (start_date, end_date) in date_list ]

    for i in start_urls : 
        log.msg("start url : %s" % i, level=log.INFO) 

    def parse(self, response):
        if saving_results and raw_results : 
            raw_results.write(body_or_str(response) + "\n\n")
            raw_results.flush() # ensure whole xml response is written 
        hxs = XmlXPathSelector(response)

        if debug_level > 0 :         
            print "doing amenities" 
        amenities = hxs.select("//Hotwire/MetaData/HotelMetaData/Amenities/Amenity")
        amenities_dict = do_amenities(amenities) 
        session.commit()
        
        if debug_level > 0 : 
            print "doing neighborhoods" 
        neighborhoods = hxs.select("//Hotwire/MetaData/HotelMetaData/Neighborhoods/Neighborhood") 
        neighborhoods_dict = do_neighborhoods(neighborhoods) 
        session.commit() 
        
        if debug_level > 0 : 
            print "doing hotels" 
        hotels = hxs.select("//Hotwire/Result/HotelResult") 
        hotels_list = do_hotels(hotels) 
        session.commit() 
        return (amenities_dict, neighborhoods_dict, hotels_list) 
    
def main() :     
    global debug_level, raw_results 

    if debug_level > 0 : 
        log.start(logfile="hotwire_api_analysis.log")
    if saving_results : # to save raw results.   
        try : 
            try :
                os.mkdirs(os.path.join(base_data_dir, "raw")) 
            except :
                pass 
            results_fn = os.path.join(base_data_dir, "raw", "%d" % int(time.time())) # crude, dirs must exist 
            if debug_level > 8 : 
                print "results_fn=", results_fn 
            raw_results = open(results_fn, "w") 
        except Exception,e :
            log.msg("unable to open raw data file - won't be saving raw data", level=log.WARNING) 

    settings.overrides['USER_AGENT'] = "Mozilla/5.0 (Windows; U; Windows NT 6.0; en-US) AppleWebKit/534.10 (KHTML, like Gecko) Chrome/8.0.552.224 Safari/534.10"
    settings.overrides['SCHEDULER_ORDER'] = 'BFO'
    crawler = CrawlerProcess(settings)
    crawler.install()
    crawler.configure()
    spider=hotwire_api_analysis()
    crawler.queue.append_spider(spider)
    crawler.start()
    if debug_level > 0 : 
        try : 
            spider.log_file.close()
        except : 
            pass 

if __name__ == '__main__':
    print "not doing main"
    # main()
