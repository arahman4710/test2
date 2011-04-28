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
import re
from datetime import date
import time
import MySQLdb
import urllib
import sys
import json
import os 

# debug_level controls amount of debugging information written :
#  set to 0 to turn debug messages off
#  I usually use 1-3 for most important messages
#                4-6 for medium level
#                6-9 for debugging stuff that mostly nobody should have to see
#                10  for debugging stuff that nobody wants to see, but is sometimes useful

debug_level = 0

connection = None
cursor = None

saving_results = True  # save raw xml for debugging etc 
raw_results = None 
hotel_info_fields = ['StarRating', 'NeighborhoodId', 'DeepLink', 'ResultId',
                     'AveragePricePerNight', 'HWRefNumber', 'TaxesAndFees',
                     'Nights', 'TotalPrice', "CheckInDate", "CheckOutDate",
                     'LodgingTypeCode'] 

base_query_format = "http://api.hotwire.com/v1/search/hotel?apikey=%s&dest=%s&rooms=1&adults=2&children=0&startdate=%s&enddate=%s"

base_data_dir = "data"  # this really needs to be something better, or a database 

amenity_dict = {} 
region_dict = {} 

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

    All information is saved in json format as dictionaries - this relieves us of the need to build a database
    schema unless required and is easy enough to convert to most other formats.   One such dictionary is
    written per line and the key name is the same as the name in the hotel_info_fields name.  There is
    also a "type" entry which is either 'hotel_info' for stuff from the hotel_list query or
    'hotel_page' for stuff from a deeplink query

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
    city_names = ['Anchorage, AK'] 
    # date_offsets = [0, 7, 14]  # offsets in days from today 
    date_offsets = [0] 
    api_key='eupzwn43dwtmgxhmkw5pbta7'
    region_name={}
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
        temp_regions = []
        hotel_list = []
        if False : 
            region_url=''
            regions={}
            amenities={}
            region_url= hxs.select("//Hotwire/Result/HotelResult[1]/DeepLink/text()").extract()[0]
            log.msg("region-url=%s" % region_url, level=log.INFO) 
        temp_regions = hxs.select("//Hotwire/MetaData/HotelMetaData/Neighborhoods/Neighborhood")
        temp_amenities = hxs.select("//Hotwire/MetaData/HotelMetaData/Amenities/Amenity")
        hotel_list = hxs.select("//Hotwire/Result/HotelResult")
        fetch_time = time.time() 

        # cope with amenities.   we already have a dict of these, and saved in a json file(maybe)
        # if we get a new amenity code, get the text for that and add it to the dictionary and
        # the json file. 
        if temp_amenities:
            for ami in temp_amenities:
                code = str(ami.select(".//Code/text()").extract()[0])
                if not code in self.amenity_dict : 
                    ami_name = str(ami.select(".//Name/text()").extract()[0]).strip().lower()
                    self.amenity_dict[code]=ami_name
                    cursor.execute('insert into amenities values(NULL, %s, %s)', (code, ami_name)) 

        # cope with regions - essentially the same as the amenities 
        if temp_regions:
            for reg in temp_regions:
                region_id=float(reg.select(".//Id/text()").extract()[0].strip())
                if not region_id in self.region_dict : 
                    region_name=reg.select(".//Name/text()").extract()[0].strip()
                    region_city = reg.select(".//City/text()").extract()[0].strip()
                    region_state = reg.select(".//State/text()").extract()[0].strip() 
                    region_centroid = reg.select("../Centroid/text()").extract()[0].strip() 
                    region_country =  reg.select("../Country/text()").extract()[0].strip() 
                    region_description = reg.select("../Description/text()").extract()[0].strip() 
        if hotel_list:
            for hotel in hotel_list:
                result_dict = {'type':'hotel_info', 'fetch-time':fetch_time } 
                for name in hotel_info_fields :
                    try : 
                        result_dict[name] = hotel.select('.//%s/text()'%name).extract()[0] 
                    except Exception, e:
                        log.msg("failed to extract %s from result" % name, level=log.INFO) 
                try : # has to be one that's different, i guess, this should produce a list of codes
                    result_dict['AmenityCodes'] = hotel.select(".//AmenityCodes/Code/text()").extract()
                except Exception, e:
                    log.msg("failed to read amenity codes for %s"% e, level=log.INFO)
                self.result_file.write(json.dumps(result_dict))
                self.result_file.write("\n") 
                self.result_file.flush() 
                deep_link = result_dict['DeepLink'].replace('&amp;', '&') 
                reqq= Request(deep_link,callback=self.hotel_page)
                reqq.meta["info"] = result_dict['HWRefNumber']
                yield reqq

    def hotel_page(self,response):
        log.msg("hotel_page url=%s" % response.url, level=log.INFO) 
        tripadvisor_rating =''
        recommendation =''
        if response.body:
            result_dict = {'type':'hotel_page', 'ref':response.meta["info"], 'fetch_time':time.time()} 
            
            hxs = HtmlXPathSelector(response)
            try : 
                result_dict['trip_advisor_rating'] = hxs.select(".//div[@class ='tripAdvisor']/strong/text()|.//*[@id='areaInf']/div[1]/div[2]/strong/text()").extract()[0] 
                result_dict['recommendations'] = hxs.select(".//*[@id='customerReviews']/div/div[1]/div[2]/text()").extract()[0] 
            except :
                log.msg("failed to get advisor_rating for %s" % result_dict['ref'], level=log.WARNING) 
            self.result_file.write(json.dumps(result_dict)) 
            self.result_file.write("\n") 
            self.result_file.flush() 

def load_general_db_info() :
    try : 
        cursor.execute('select * from Amenities')
        for i in cursor.fetchall() :
            amenity_dict[i[2]] = i[1] 
    except Exception, e : 
        print "Failed to read Amenities "
        print "exception : ", e 
    # fill in region_dict - used mostly to avoid reloading regions we've seen 
    cursor.execute('select RegionName, HotwireCityID from HotwireRegions')
    for i in cursor.fetchall() :
        region_dict[i[1]] = i[0] 
    
def main():
    global debug_level, raw_results 
    global connection, cursor 

    if debug_level > 0 : 
        log.start(logfile="hotwire_api_analysis.log")
    if saving_results : # to save raw results.   
        try : 
            results_fn = os.path.join(base_data_dir, "raw", "%d" % int(time.time())) # crude, dirs must exist 
            raw_results = open(results_fn, "w") 
        except Exception,e :
            log.msg("unable to open raw data file - won't be saving raw data", level=log.WARNING) 
    connection = MySQLdb.connect(user='jefu', db='acuity')
    cursor = connection.cursor()
    load_general_db_info() 
    settings.overrides['USER_AGENT'] = "Mozilla/5.0 (Windows; U; Windows NT 6.0; en-US) AppleWebKit/534.10 (KHTML, like Gecko) Chrome/8.0.552.224 Safari/534.10"
    settings.overrides['SCHEDULER_ORDER'] = 'BFO'
    crawler = CrawlerProcess(settings)
    crawler.install()
    crawler.configure()
    spider=hotwire_api_analysis()
    crawler.queue.append_spider(spider)
    crawler.start()
    if debug_level > 0 : 
        spider.log_file.close()


if __name__ == '__main__':
    print "not doing main"
    # main()
