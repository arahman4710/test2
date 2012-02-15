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
from Unprocessed_Raw_Postforum_Data import Unprocessed_Raw_Postforum_Data
from Unprocessed_Raw_Hotellist_Data import Unprocessed_Raw_Hotellist_Data

##establishing connection to the database
engine = create_engine('postgresql://postgres:areek@localhost:5432/acuity', echo=False)
Session = scoped_session(sessionmaker(bind=engine))
session = Session()
Base = declarative_base(bind=session) 
metadata = Base.metadata

class BBPricelinePostSpider(BaseSpider):

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
        #finds the priceline posts board
        post_board = hxs.select("//table[@class='ipb_table']//h4/a[@seotitle='priceline-canada']")
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
        target_site = "priceline"
        source_forum = "BB"
        post_counter = 0

        #selects the hotel list link from board and sends to parse in parse_hotwire_list
        hotel_list = hxs.select("//a[contains(text(), 'Priceline Hotel List')]/@href").extract()
        if hotel_list:
            yield Request(hotel_list[0], callback = self.parse_priceline_list)


        for post in posts:

            #iterate through the posts and extract information from post
            title = post.select(".//a[@id]/text()")
            subtitle = post.select(".//span[@class='desc']/text()")
            replies = post.select(".//a[@onclick]/text()")
            post_url = post.select(".//a[@id]/@href")
            
            if (title and subtitle and post_url and replies):

                #extract more information               
                title = title[0].extract()
                subtitle = subtitle[0].extract()
                star = find_star(title)
                price = find_price(subtitle)
                replies = replies[0].extract()
                hotel_name = find_name(title)
                post_url = post_url[0].extract()
                post_num = self.find_post_num(post_url)
                dates = self.find_dates(subtitle)
                if (dates):
                    date = dates[0]
                    nights = dates[1]
                else:
                    date = False
                    nights = False
                if (hotel_name and star and price and date and nights and post_num):
                	post_counter += 1
                	entry = Unprocessed_Raw_Postforum_Data(hotel_name, star, price, date, nights, replies, post_num, country, state, target_site, source_forum)
                	session.add(entry)
	
	assert session.query(Unprocessed_Raw_Postforum_Data).count() == post_counter ## make sure the entries in database equal amount of entries scraped
        session.commit()

        #Gets the next page link and sends it to parse_board
        next_page = hxs.select("//a[@title='Next page']/@href").extract()
        if next_page:
            yield Request(next_page[0], callback = self.parse_board)

    def parse_priceline_list(self, response):

        hxs = HtmlXPathSelector(response)

        #selects the element containing all the information
        post = hxs.select("//div[@class='post entry-content ']")
        state = ""
        country = "Canada"
        target_site = "priceline"
        source_forum = "BB"
        hotelpost_counter = 0

        if (post):
            post = post[0]

            #extracts all text from the post and also the span tags to detect new region 
            posts = post.select(".//span|.//text()")

            #initialize variables for iteration
            region = ""
            name = ""
            star = 0
            amenities = ""

            for post in posts:
                post = post.extract()
                post = post.strip()

                #detects the region information
                if (post[0:28] == '<span class="bbc_underline">'):
                    city_area = re.search(r'(?s)(?<=\>).*(?=\<)', post).group()

                else:
                    #detects if its the hotel info (usually starts with digit for star rating)
                    if (re.search(r'^\d.*', post)):
                        match_star = re.search(r'^\d\.\d\*|^\d\*', post)
                        if match_star:
                            star = match_star.group()
                        match_name = re.search(r'(?<=\s).*', post)
                        if match_name:
                            name = match_name.group()
                            name = re.sub(r'\(previously.*', "", name)
                            name = re.sub(r'\-\-', "", name)
                        region = re.search("(?s)(?<=\().*(?=\))", city_area)
                        if region: region = (region.group()).strip()
                        else: region = " "
                        hotelpost_counter += 1
                        entry = Unprocessed_Raw_Hotellist_Data(hotel_name, city_area, region, star, amenities, state, country, target_site, source_forum)
                        session.add(entry)

        assert session.query(Unprocessed_Raw_Hotellist_Data).count() == hotelpost_counter                             
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

    spider = BBPricelinePostSpider()
    crawler.queue.append_spider(spider)

    crawler.start()


if __name__ == '__main__':
	main()    
