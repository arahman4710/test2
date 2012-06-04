from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.crawler import CrawlerProcess
from multiprocessing import Process, Queue
from scrapy.conf import settings
from scrapy import log
from scrapy.http import Request
import re
from libs import *
import sys

from sqlalchemy import * 
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base

sys.path.insert(0, "/home/areek/Documents/fetchopia/backend_git/sql/alchemy/" )
from processed_forum_data_hotwire import ProcessedRawForumData_hotwire

##establishing connection to the database
engine = create_engine('postgresql://postgres:areek@localhost:5432/acuity', echo=False)
Session = scoped_session(sessionmaker(bind=engine))
session = Session()
Base = declarative_base(bind=session) 
metadata = Base.metadata

#####################################################################
#David@fetchopia 
#Date:4/25/2012
#Description:
#Scrapes the betterbidding forum site for all Canada hotwire hotel lists
#Additional manual processing for entries state field after running this script (Canadian hotels have no states)

class BBHotwirePostSpider(BaseSpider):

    name = "BBHotwirePostSpider"
    start_urls = ["http://www.betterbidding.com/"]
    allowed_domains = ["betterbidding.com"]

    def parse(self, response):

        hxs = HtmlXPathSelector(response)

        #Finds the Internation table
        canada_board = hxs.select("//table[@class='ipb_table' and (contains(@summary, 'International'))]")

        #Grabs the canada link under international table
        url = canada_board.select(".//h4/a[@seotitle='canada']/@href")

        #sends the link to find_board
        if (url):
            url = url[0].extract()
            yield Request(url, callback=self.find_board)

    def find_board(self, response):
        
        hxs = HtmlXPathSelector(response)
        #finds the hotwire posts board
        post_board = hxs.select("//table[@class='ipb_table']//h4/a[@seotitle='hotwire-canada']")
        url = post_board.select(".//@href")

        #sends the posts board to parse_board
        if (url):
            url = url[0].extract()
            return Request(url, callback = self.parse_board)

    def parse_board(self, response):

        hxs = HtmlXPathSelector(response)

        #selects all the posts in board
        posts = hxs.select("//table[@class='ipb_table topic_list']/tr[contains(@class, 'row')]")

        state = ""
        country = "Canada"
        target_site = "Hotwire"
        source_forum = "BB"

        #selects the hotel list link from board and sends to parse in parse_hotwire_list
        hotel_list = hxs.select("//a[contains(text(), 'Hotwire Hotel List')]/@href").extract()
        if hotel_list:
            yield Request(hotel_list[0], callback = self.parse_hotwire_list)

	
	

    def parse_hotwire_list(self, response):

        hxs = HtmlXPathSelector(response)

        #selects the element containing all the information
        post = hxs.select("//div[@class='post entry-content ']")
        state = ""
        country = "Canada"
        target_site = "Hotwire"
        source_forum = "BB"
        delete_flag = False

        if (post):
            post = post[0]

            #extracts all text from the post and also the span tags to detect new region 
            posts = post.select(".//span|.//text()|.//del")

            #initialize variables for iteration
            region = ""
            hotel_name = ""
            star = 0
            amenities = ""

            for post in posts:
                post = post.extract()
                post = post.strip()

                #cases for ignoring the post
                case1 = re.search(r'^\(.*same as.*', post)
                case2 = re.search(r'^OR', post)
                case3 = re.search(r'^\(with.*', post)
                case4 = re.search(r'^\(can.*be:', post)
                case5 = re.search(r'^\(may be:.*', post)
                
                if (post[0:4] == '<del'):
                	delete_flag = True
                	continue
                
                if delete_flag == True:
                	delete_flag = False
                	continue

                #checks if post is amenities
                match_amenities = re.search("(?i)(?<=amenities:).*", post)
                if (match_amenities):
                    #in case theres more amenity info specified by "OR" 
                    amenities_partial = match_amenities.group()
                    amenities += amenities_partial

                #no longer use of <u> tag, the span tag is the new detection for region name
                if(post[0:28] == '<span class="bbc_underline">'):
                    city_area = re.search(r'(?s)(?<=\>).*(?=\<)', post).group()
                    region = re.search("(?s)(?<=\().*(?=\))", city_area)
                    if region:
                    	region = (region.group()).strip()
                    	city_area = re.search(r'.*(?=\()', city_area).group()
                    else: region = ""
                    

                elif ((not case1) and (not case2) and (not case3) and (not case4) and (not case5)):
                    #if information collected, then store and reset amenities
                    if ((len(hotel_name)>0) and (len(amenities)>0)):
                        if ((not re.search(r'(?<=,).*', hotel_name)) or (re.search(r'.*\d.*', hotel_name))):	
                            entry = ProcessedRawForumData_hotwire(hotel_name, city_area, region, star, state, country, amenities, target_site, source_forum)
                            session.add(entry)
                            amenities = ""

                    else:
                        match_star = re.search(r'^\d\.\d\*|^\d\*', post)
                        if match_star:
                            star = match_star.group()
                            star = re.search(r'.*(?=\*)', star).group()
                        match_name = re.search(r'(?<=\s).*', post)
                        if match_name:
                            hotel_name = match_name.group()
                            hotel_name = re.sub(r'\(previously.*', "", hotel_name)
                                 
        session.commit()
        
    def date_diff(self, date1, date2):
        try:
            d1 = time.strptime(date1, "%m/%d/%y")
            d2 = time.strptime(date2, "%m/%d/%y")
            d1 = d1.tm_yday
            d2 = d2.tm_yday
            return [date1, d2 - d1]
        except:
            0

    def find_dates(self, date_str):
        date1 = re.search("[0-9]{1,2}/[0-9]{1,2}/[0-9]{1,2}", date_str)
        date2 = re.search("(?<=-)[0-9]{1,2}/[0-9]{1,2}/[0-9]{1,2}", date_str)

        if (date1 and date2):
            date1 = date1.group()
            date2 = date2.group()
            return self.date_diff(date1, date2)

    def find_post_num(self, url):
        num = re.search("(?<=/)[0-9]*$", url)
        if (num):
            return num.group()
        else:
            return False
            
            
            
def main():
    log.start()
    settings.overrides['USER_AGENT'] = "Mozilla/4.0 (compatible;MSIE 7.0;Windows NT 6.0)"
    settings.overrides['DOWNLOAD_DELAY'] = 2;
    crawler = CrawlerProcess(settings)
    crawler.install()
    crawler.configure()

    spider = BBHotwirePostSpider()
    crawler.queue.append_spider(spider)

    crawler.start()


if __name__ == '__main__':
	main()    
