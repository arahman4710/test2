from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.crawler import CrawlerProcess
from multiprocessing import Process, Queue
from scrapy.conf import settings
from scrapy import log
from scrapy.http import Request
import re
from libs import *
from sqlalchemy import * 
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
import sys

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
#Scrapes the betterbidding forum site for all US hotwire hotel lists
#Additional manual processing for entries state field after running this script (Some US states are clustered together)


class BBHotwirePostSpider(BaseSpider):


    name = "BBHotwirePostSpider"
    start_urls = ["http://www.betterbidding.com/"];
    allowed_domains = ["betterbidding.com"];

    def parse(self, response):

        # 1  Finds all of the states for USA

        hxs = HtmlXPathSelector(response)
        states = hxs.select("//table[@class='ipb_table' and(contains(@summary, 'United'))]/tr")

        for state in states:

            # 2  Find the board URL's from the current XPaths

            url = state.select(".//h4/a/@href")
            if (url):
                url = url[0].extract()
                yield Request(url, callback=self.find_board)

    def find_board(self, response):

        #finds all the elements on region's board
        hxs = HtmlXPathSelector(response)
        boards = hxs.select("//table[@class='ipb_table']//h4/a")

        for board in boards:
            #Find the hotwire board of the region
            ##Grabs ALL hotwire related links in board (eg. California has 3 boards of LA, orange county and all other cities)
            check = re.search(r"[^\/]Hotwire", board.extract())
            if (check):
                url = board.select(".//@href")
                if (url):
                    url = url[0].extract()
                    return Request(url, callback = self.parse_board)

    def parse_board(self, response):

        #Finds all board posts
        hxs = HtmlXPathSelector(response)
        posts = hxs.select("//table[@class='ipb_table topic_list']/tr[contains(@class, 'row')]")

        title = hxs.select("//head/title/text()")[0].extract()
        state = title[10:-30]
        country = "US"
        target_site = "Hotwire"
        source_forum = "BB"
        
        #Feed the link to hotwire hotel lists to parse_hotel_list

        hotel_list = hxs.select("//a[contains(text(), 'Hotwire Hotel List')]/@href").extract()
        if hotel_list:
            yield Request(hotel_list[0],
                          meta={'state':state},
                          callback = self.parse_hotwire_list)


    def parse_hotwire_list(self, response):
    
#    	print "parsed this page::%s" % response.url

        hxs = HtmlXPathSelector(response)
        post = hxs.select("//div[@class='post entry-content ']")
        state = response.request.meta['state']
        country = "US"
        target_site = "Hotwire"
        source_forum = "BB"
        delete_flag = False

        if (post):
            post = post[0]
            #extracts the span bbc_underline tags, and all text 
            posts = post.select(".//span|.//text()|.//del")
	
	    ##initialize variables for loop		
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

                match_amenities = re.search("(?i)(?<=Amenities:).*", post)
                if (match_amenities):
                    #in case theres more amenity info specified by "OR" 
                    amenities_partial = match_amenities.group()
                    amenities += amenities_partial

                #no longer use of <u> tag, the span tag is the new detection
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
                        if (not re.search(r'(?<=,).*', hotel_name)) or (not re.search(r'.*\d.*', hotel_name)):
                            entry = ProcessedRawForumData_hotwire(hotel_name, city_area, region, star, state, country, amenities, target_site, source_forum)
                            session.add(entry)
                            session.commit()
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
                            hotel_name = re.sub(r'^now', "", hotel_name)
                            hotel_name = re.sub(r' not reported to the board\)', "", hotel_name)


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

            
        

            
                
                
                
        
        
    
        
