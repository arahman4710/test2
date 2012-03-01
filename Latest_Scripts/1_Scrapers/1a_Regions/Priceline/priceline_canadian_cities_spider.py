from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.crawler import CrawlerProcess
from multiprocessing import Process, Queue
from scrapy.conf import settings
from scrapy import log
from scrapy.http import Request
from libs import *
from sqlalchemy import * 
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base

import sys
sys.path.insert(0, "/home/areek/Documents/fetchopia/backend_git/sql/alchemy/" )

from city_table import CityTable

##establishing connection to the database
engine = create_engine('postgresql://postgres:areek@localhost:5432/acuity', echo=False)
Session = scoped_session(sessionmaker(bind=engine))
session = Session()
Base = declarative_base(bind=session) 
metadata = Base.metadata

### This script updates the City Table with canadian cities and their province information
class Priceline_CA_Cities(BaseSpider):


    name = "Priceline_CA_Cities"
    start_urls = ["http://www.priceline.com/hotels/Lang/en-us/city_list.asp?session_key=334A050A354A050A20120214204630783070129544&plf=pcln&c=CA&l=101&r=CA"];

    def parse(self, response):


        hxs = HtmlXPathSelector(response)
        posts = hxs.select("//table[contains(@summary, 'This table lists')]/tr")
        counter = 0
        country = "Canada"

        for post in posts:
            if counter >= 1:
             	info = post.select(".//font/text()")
             	info = info.extract()
             	if len(info) == 4:
             		entry1 = CityTable(default, str(info[0]), str(info[1]), country)
             		session.add(entry1)
             		entry2 = CityTable(default, str(info[2]), str(info[3]), country)
             		session.add(entry2)
             	
             	else:
             		entry1 = CityTable(default, str(info[0]), str(info[1]), country)
             		session.add(entry1)

             	
	    
	    counter += 1
        



            

    
        

                
def main():
    log.start()
    settings.overrides['USER_AGENT'] = "Mozilla/4.0 (compatible;MSIE 7.0;Windows NT 6.0)"
    settings.overrides['DOWNLOAD_DELAY'] = 2;
    crawler = CrawlerProcess(settings)
    crawler.install()
    crawler.configure()

    spider = Priceline_CA_Cities()
    crawler.queue.append_spider(spider)

    crawler.start()


if __name__ == '__main__':
	main()

            
        

            
                
                
                
        
        
    
        
