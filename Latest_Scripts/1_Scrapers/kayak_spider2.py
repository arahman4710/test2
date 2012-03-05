from decimal import *
import Levenshtein
from scrapy.selector import HtmlXPathSelector,XmlXPathSelector
from scrapy.http import Request
from scrapy.http import FormRequest
from scrapy.conf import settings
from scrapy.crawler import CrawlerProcess
from scrapy.spider import BaseSpider
from scrapy import signals,log
from scrapy.xlib.pydispatch import dispatcher
from scrapy.contrib.spiders import XMLFeedSpider
import re
from datetime import date
import time
import urllib

def printable(str):
    control = "".join(map(unichr, range(0,127)))
    control = re.escape( control)
    return re.sub("[^%s]" % control, "", str)

class KayakSpider(BaseSpider):
    name = "KayakSpider"
    start_urls = ["http://www.kayak.com/hotels"];
    allowed_domains = ["kayak.com"];
    selec_city=['Miami, FL'];
    results=[];
    query_price=[];
    price_results={};

    def parse(self, response):

        start_date = str(date.today().strftime('%m/%d/20%y'))
        end_date = str(date.today().replace(day=date.today().day + 1).strftime('%m/%d/20%y'))
        for city in self.selec_city:
            city_request = city
            search = {'othercity': city_request, 'checkin_date': start_date, 'checkout_date': end_date}

            request = FormRequest.from_response(response, formnumber = 1, formdata = search, callback = self.do_city)
            request.meta['city'] = city
            yield request

    def do_city(self, response):
        ## iterates through the pages of hotels within a city
        url = response.url
        hxs = HtmlXPathSelector(response)
        total_hotels_in_city = hxs.select("//span[@id='showingnumber']/text()")
        pages = int(total_hotels_in_city.extract()[0]) / 15 ##find out how many pages of hotels to iterate through within city
        x = 0
        while x <= pages:
            y = str(x)
            pattern = "&pn=0"
            new_pattern = re.sub("0", y, pattern)
            nextpage_request = Request(url + new_pattern, callback = self.callfilter)
            nextpage_request.meta['city'] = response.request.meta['city']
            x += 1
            yield nextpage_request
            
    def callfilter(self, response):

        hxs = HtmlXPathSelector(response)
        hotel_list = hxs.select("//div[contains(@id, 'tbd')]/@data-resultid")
        for hotel in hotel_list:
            hid = hotel.extract() ##unique hotel id from kayak
            request = Request("http://www.kayak.com/h/hotel/details.vtl?hid=" + hid, callback = self.filtered) 
            request.meta['city'] = response.request.meta['city']
            request.meta['hid'] = hid
            yield request

    def filtered(self, response):

        doc = printable(response.body)
        hxs = HtmlXPathSelector(response)
        
        name = hxs.select(".//div[@class='overviewDataName']/text()")
        name = name.extract()[0]
        address = hxs.select(".//div[@class='address']/text()")
        address = address.extract()[0]
        price = hxs.select(".//span[@class='hoteldetailPrice']/text()")
        price = price.extract()[0]

        star = hxs.select(".//div[contains(@class,'starsprite')]/@class")
        if star:
            star = star.extract()[0]
            star = star[-1:]

        print name, address, star, price

def main():
    log.start()
    settings.overrides['USER_AGENT'] = "Mozilla/4.0 (Windows; U; Windows NT 6.0; en-US) AppleWebKit/534.10 (KHTML, like Gecko) Chrome/8.0.552.224 Safari/534.10"
    settings.overrides['SCHEDULER_ORDER'] = 'BFO'
    crawler = CrawlerProcess(settings)
    crawler.install()
    crawler.configure()
    spider = KayakSpider()
    crawler.queue.append_spider(spider)
    crawler.start()

if __name__ == '__main__':
    main()

    
                
                

        
