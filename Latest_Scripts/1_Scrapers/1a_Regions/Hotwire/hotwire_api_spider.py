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
import sys
import pdb
import argparse 

import logging
logging.basicConfig(filename='HOTWIRE_API.log',filemode='w',level=logging.DEBUG)
##############################
# Used to get hotwire neighborhoods (region) and also the hotwire.com hotels
# city to region relationship stored in HOTWIRE_API.log, use process_hotwire to process into database

from city_table2 import CityTable_canadian
from hotwire_tables import * 

saving_results = True  # save raw xml for debugging etc 
raw_results = None 
request_generator_settings = None 


city_list = []
x = session.query(CityTable_canadian).distinct()
for instance in x:
	city_name = "%s, %s, %s" % (instance.name, instance.state, instance.country)
	if instance.name == "0":
		pass
	else:
		city_list.append(city_name)
		
all_city_names = city_list
one_city_name = ['Mississauga, ON'] 
#all_city_names =['Houston, Texas, USA','Toronto','New York, New York','Los Angeles, California','Chicago, Illinois','Ottawa, ON Canada','Vancouver, BC Canada','Calgary, AB Canada','Boston, Massachusetts','Anchorage, AK']  




base_query_format = "http://api.hotwire.com/v1/search/hotel?apikey=%(api_key)s&dest=%(city)s&rooms=%(rooms)s&adults=%(adults)s&children=%(children)s&startdate=%(start_date)s&enddate=%(end_date)s"
# base_query_format = "http://localhost/raw_data_hotwire"
# base_query_format = "http://localhost/raw_data_hotwire?apikey=%s&dest=%(city)s&rooms=$(rooms)s&adults=%(adults)s&children=%(children)s&startdate=%(start_date)s&enddate=%(end_date)s"
base_data_dir = "data"  # this really needs to be something better, or a database 

# debug_level controls amount of debugging information written :
#  set to 0 to turn debug messages off
#  I usually use 1-3 for most important messages
#                4-6 for medium level
#                6-9 for debugging stuff that mostly nobody should have to see
#                10  for debugging stuff that nobody wants to see, but is sometimes useful

debug_level = 1
        
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
        log.msg( "do_amenity :%s" % amenity,level=log.DEBUG ) 
    info = dict_extract(amenities_element_dict, amenity) 
    if debug_level > 5 : 
        log.msg("amenity info : %s" % info, level=log.DEBUG) 
    am = session.query(Amenity).filter_by(code=info['code']).all() 
    if am :
        return am[0].uid 
    am = Amenity(info) 
    return am.uid 

def do_neighborhoods(neighborhoods) :
    return [do_one_neighborhood(i) for i in neighborhoods] 

def do_one_neighborhood(nb) : 
    if debug_level > 9 : 
        log.msg("do one neighborhood", log.INFO) 
    result_dict = dict_extract(neighborhood_element_dict, nb)  
    logging.info("%s#" % result_dict['name'])
    nresult = session.query(Neighborhood).filter_by(id=result_dict['id']).all() 
    if nresult :   # we have it already 
        return nresult[0]
     
    [clat, clong] = map(float, result_dict["centroid"].split(",")) 
    result_dict['centroid'] = find_point(clat, clong).uid 
    
    if debug_level > 8 : 
        log.msg("About to do points", level=log.DEBUG) 
    points = nb.select(".//Shape/LatLong/text()")
    if debug_level > 8 : 
        log.msg( "points : %s"% points, level=log.DEBUG) 
    point_list = [] 
    for i in enumerate(points) :
        if debug_level > 8 : 
            log.msg( "doing a point : %s" % str(i) ,level=log.DEBUG) 
            log.msg( "i[1]=%s" % i[1] ,level=log.DEBUG) 
            log.msg( "i[1].extract()=%s" % i[1].extract() ,level=log.DEBUG) 
        [point_lat, point_long] = map(float, i[1].extract().split(",")) 
        point_list.append((i[0], point_lat, point_long)) 
    result_dict["point_list"] = PointList(point_list).uid 
    return Neighborhood(result_dict) 

def do_hotels(hotel_list, meta_info) :
    return [do_hotel(h, meta_info) for h in hotel_list] 

def do_hotel(hotel, meta_info) :
    if debug_level > 7 :     
        log.msg("doing hotel %s" % hotel,level=log.DEBUG) 
    dict = dict_extract(hotel_element_dict, hotel) 
    amenity_codes_raw = hotel.select(".//AmenityCodes/Code/text()") 
    if debug_level > 9 : 
        log.msg("raw amenity codes: %s" % amenity_codes_raw ,level=log.DEBUG) 
    amenity_codes = [i.extract() for i in amenity_codes_raw]
    if debug_level > 9 : 
        log.msg( "amenity codes=%s" % amenity_codes ,level=log.DEBUG) 
    dict['amenity_codes'] = amenity_codes 
    x = HotWireHotelInfo(dict, meta_info)
    session.add(x) 
    session.commit()

'''
def hotel_page(self,response):
	tripadvisor_rating = 0
        if response.body:
        	hxs = HtmlXPathSelector(response)
                temp_tripadvisor_rating =hxs.select(".//div[@class ='tripAdvisor']/strong/text()|.//*[@id='areaInf']/div[1]/div[2]/strong/text()")
                if temp_tripadvisor_rating:
                    tripadvisor_rating = temp_tripadvisor_rating.extract()[0].replace(" out of 5.0","").replace(" out of 5","")
        yield tripadvisor_rating
'''

def gen_date(offset, nights) : 
    """
    given an offset (number of days in the future to check) this returns a pair of strings
    (start_date, end_date) that is that number of days into the future and the day after
    that.

    Do this by getting the time, adding the right number of seconds and converting using
    strftime - which avoids having to cope with month endings by hand
    """ 

    cursecs = time.time() 
    startgmt = time.gmtime(cursecs + offset * 24 * 60 * 60)    # offset days in the future 
    endgmt = time.gmtime(cursecs + (offset+nights) * 24 * 60 * 60)  # offset + nights days in the future 
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
    
    # 
    # city_names = ['Anchorage, AK'] 
    # date_offsets = [0, 7, 14]  # offsets in days from today 
    date_offsets = [0] 
    api_key='eupzwn43dwtmgxhmkw5pbta7'
    diff = 4

    nowsecs = time.time() 

    def start_requests(self) :
        def gen_request() : 
            i = 0 
            for r in ( self.make_request(city=city, date_offset=date_offset,
                                         nights=nts, rooms=rms,
                                         adults=ads, children=cs )
                       for date_offset in request_generator_settings["offsets"]
                       for city        in request_generator_settings["city_names"]
                       for rms         in request_generator_settings["room_count"]
                       for ads         in request_generator_settings["adults"]
                       for cs          in request_generator_settings["child_range"]
                       for nts         in request_generator_settings["nights"]
                     ) :  
                yield r 
                if debug_level > 5 :
                    log.msg("query number %d" % i, log.DEBUG) 
                i += 1
                if i > request_generator_settings["result_count"] :
                    return
        return gen_request() 

    def make_request(self, **kwargs) : 
        (start_date, end_date) = gen_date(kwargs["date_offset"], kwargs["nights"]) 
        kwargs["start_date"] = start_date
        kwargs["end_date"]=end_date 
        kwargs["api_key"] = self.api_key 
        query = base_query_format % kwargs
        log.msg("query = <<%s>>" % query, level=log.INFO)  
        
        return Request(query, callback=self.parse, meta=kwargs) 

    def parse(self, response):
        if saving_results and raw_results : 
            raw_results.write(body_or_str(response) + "\n\n")
            raw_results.flush() # ensure whole xml response is written 
        hxs = XmlXPathSelector(response)
        city = response.request.meta['city']

        if debug_level > 0 :         
            log.msg( "doing amenities" ,level=log.DEBUG) 
            
        amenities = hxs.select("//Hotwire/MetaData/HotelMetaData/Amenities/Amenity")
        amenities_dict = do_amenities(amenities) 
        session.commit()
        	
        
        if debug_level > 0 : 
            log.msg( "doing neighborhoods" ,level=log.DEBUG) 
        neighborhoods = hxs.select("//Hotwire/MetaData/HotelMetaData/Neighborhoods/Neighborhood")
        logging.info("%s$" % city) ##### for the city - area hotwire mapping table
        neighborhoods_dict = do_neighborhoods(neighborhoods) 
        session.commit() 
        
        if debug_level > 0 : 
            log.msg( "doing hotels" ,level=log.DEBUG) 
        hotels = hxs.select("//Hotwire/Result/HotelResult") 
        hotels_list = do_hotels(hotels, response.meta) 
        session.commit() 
        return None

def main() :     

    global debug_level, raw_results, request_generator_settings 

    parser = argparse.ArgumentParser(description='Run spider')

    parser.add_argument('--do-all-cities',
                        help="do all cities or just test with one (default=one)",
                        dest='all_cities',
                        action='store_true') 

    parser.add_argument('--do-spider',
                        help='run spider if true (default=false)',
                        dest='do_spider',
                        action='store_true')

    parser.add_argument('--debug-level', nargs='?', type=int,
                        default=0,
                        help='debug level (0-10) default=0') 

    parser.add_argument('--adults',
                        default="1", 
                        help='number of adults, if comma separated use values from list') 
    parser.add_argument('--child_range',
                        default="0", 
                        help='number of children, if comma separated use values from list')
    parser.add_argument('--nights',
                        default="1", 
                        help='number of nights, if comma separated use values from list')

    parser.add_argument('--result-count', type=int, 
                        help='total number of results to fetch',
                        default=50000) 

    parser.add_argument('--offsets',
                        default="0", 
                        help='number of nights in the future to look (0=today), if comma separated use values from list') 

    parser.add_argument('--room-count',
                        default="1",
                        help='number of rooms, if comma separated use values from list') 

    arg_result = parser.parse_args()

    debug_level = arg_result.debug_level

    if debug_level > 0 : 
        log.start(logfile="hotwire_api_analysis.log")
        for i in vars(arg_result).items() :
            log.msg("command line var %s -> %s" % i, level=log.INFO)  

    if saving_results : # to save raw results.   
        yearday = time.strftime("%Y-%j", time.localtime())  # year and day of year - used both in directory and filename
        hourmin = time.strftime("%H-%M", time.localtime())  # hour and minute - used in filename to avoid overwriting

        raw_data_dir = None 

        try :
            raw_data_dir = os.path.join(base_data_dir, "raw", yearday) 
            os.makedirs(raw_data_dir) 
        except Exception, e:
            log.msg("unable to make data directory %s" % raw_data_dir) 
            log.msg("error_was %s" % e) 
            raw_data_dir = None 

        if raw_data_dir  : 
            try : 
                result_file_name = os.path.join(raw_data_dir, "raw-request-results-%s-%s" % (yearday, hourmin)) 
                raw_results = open(result_file_name, "w")  # year + day of year 
                if debug_level > 8 : 
                    log.msg( "results_fn= %s" % result_file_name , level=log.DEBUG) 
            except Exception, e : 
                log.msg("unable to open raw data file - won't be saving raw data", level=log.WARNING) 
                log.msg("error was %s" % e) 
                raw_results = None 

    request_generator_settings = vars(arg_result) 
    if arg_result.all_cities :
        request_generator_settings["city_names"] = all_city_names
    else : 
        request_generator_settings["city_names"] = one_city_name
    for arg in ["adults", "child_range", "nights", "room_count", "offsets"] : 
        request_generator_settings[arg] = commas_to_list(request_generator_settings[arg]) 
    if arg_result.do_spider : 
        log.msg("running spider")
#        pdb.set_trace()
        do_spider() 
    else :
        print 'not running spider\nto run spider with python -i use "do_spider()"'


def commas_to_list(s) :
    return map(int, s.split(",")) 

def do_spider() :
    log.start()
    settings.overrides['USER_AGENT'] = "Mozilla/5.0 (Windows; U; Windows NT 6.0; en-US) AppleWebKit/534.10 (KHTML, like Gecko) Chrome/8.0.552.224 Safari/534.10"
    settings.overrides['SCHEDULER_ORDER'] = 'BFO'
    settings.overrides['LOG_FILE'] = 'hotwire-scraping.log'
    settings.overrides['LOG_LEVEL'] = 'INFO' 
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
    main()
