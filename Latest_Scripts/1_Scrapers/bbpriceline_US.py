from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.crawler import CrawlerProcess
from multiprocessing import Process, Queue
from scrapy.conf import settings
from scrapy import log
from scrapy.http import Request
from libs import *
import re

from sqlalchemy import * 
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
from processed_forum_data5 import ProcessedRawForumData2

##establishing connection to the database
engine = create_engine('postgresql://postgres:areek@localhost:5432/acuity', echo=False)
Session = scoped_session(sessionmaker(bind=engine))
session = Session()
Base = declarative_base(bind=session) 
metadata = Base.metadata

class BBPricelineSpider(BaseSpider):
    name = "BBPricelinePostSpider"
    start_urls = ["http://www.betterbidding.com/"]

    def parse(self, response):

        #Finds all states in the main page betterbidding
        hxs = HtmlXPathSelector(response)
        states = hxs.select("//table[@class='ipb_table' and(contains(@summary, 'United'))]/tr")

        for state in states:
            #extract the url and send it to find_board
            url = state.select(".//h4/a/@href")
            if (url):
                url = url[0].extract()
                yield Request(url, callback=self.find_board)

    def find_board(self, response):

        #selects all board elements on state board page
        hxs = HtmlXPathSelector(response)
        boards = hxs.select("//table[@class='ipb_table']//h4/a")

        for board in boards:
            #chooses the element with priceline info and sends to parse_board
            check = re.search(r"(?i)(?<=>)priceline\s", board.extract())
            if (check):
                url = board.select(".//@href")
                if (url):
                    url = url[0].extract()
                    return Request(url, callback=self.parse_board)

    def parse_board(self, response):

        #selects all the board posts which are posted by the users
        hxs = HtmlXPathSelector(response)
        posts = hxs.select("//table[@class='ipb_table topic_list']/tr[contains(@class, 'row')]")

        title = hxs.select("//head/title/text()")[0].extract()
        state = title[12:-30]
        country = "US"
        target_site = "priceline"
        source_forum = "BB"
        post_counter = 0

        #finds the link to priceline hotel list and sends it to parse_priceline_list
        hotel_list = hxs.select("//a[contains(text(), 'Priceline Hotel List')]/@href").extract()
        if hotel_list:
            yield Request(hotel_list[0],
                          meta={'state':state},
                          callback = self.parse_priceline_list)
                          


    def parse_priceline_list(self, response):

        hxs = HtmlXPathSelector(response)
        post = hxs.select("//div[@class='post entry-content ']")
        state = response.request.meta['state']
        country = "US"
        target_site = "priceline"
        source_forum = "BB"
        url = ""

        if (post):
            post = post[0]
            #extracts the span bbc_underline tags, and all text 
            posts = post.select(".//span|.//text()")

            #initialize variables for loop
            city_area = ""
            hotel_name = ""
            star = 0
            amenities = ""

            for post in posts:
                post = post.extract()
                post = post.strip()

                #detects the region information
                if (post[0:28] == '<span class="bbc_underline">'):
                    city_area = re.search(r'(?s)(?<=\>).*(?=\<)', post).group()
                    region = re.search("(?s)(?<=\().*(?=\))", city_area)
                    if region: 
                        region = (region.group()).strip()
                        city_area = re.search(r'.*(?=\()', city_area).group()
                    else: region = " "

                else:
                    #detects if its the hotel info (usually starts with digit for star rating)
                    if (re.search(r'^\d.*', post)):
                        match_star = re.search(r'^\d\.\d\*|^\d\*', post)
                        if match_star:
                            star = match_star.group()
                            star = re.search(r'.*(?=\*)', star).group()
                        match_name = re.search(r'(?<=\s).*', post)
                        if match_name:
                            hotel_name = match_name.group()
                            hotel_name = re.sub(r'\(previously.*', "", hotel_name)
                            hotel_name = re.sub(r'\-\-', "", hotel_name)

                        entry = ProcessedRawForumData2(hotel_name, city_area, region, star, url, state, target_site, source_forum)
                        session.add(entry)

                    #may not start with digit, may start with Resort (hawaii list in particular)    
                    elif (re.search(r'^Resort', post)):
                          hotel_name = post
                          star = 0
                          entry = ProcessedRawForumData2(hotel_name, city_area, region, star, url, state, target_site, source_forum)
                          session.add(entry)
                    
              
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

    spider = BBPricelineSpider()
    crawler.queue.append_spider(spider)

    crawler.start()


if __name__ == '__main__':
	main()

        
