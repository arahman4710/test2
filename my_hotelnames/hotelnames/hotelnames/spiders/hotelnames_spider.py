from decimal import *
from scrapy.selector import HtmlXPathSelector
from scrapy.http import FormRequest
from scrapy.conf import settings
from scrapy import signals,log
from scrapy.crawler import CrawlerProcess
from scrapy.spider import BaseSpider
from scrapy.xlib.pydispatch import dispatcher
from scrapy.http import Request
from scrapy.contrib.spiders import XMLFeedSpider
from datetime import date
import re
import time
import MySQLdb
import urllib
import sys
import json


class file():
    today = str(date.today())
    yesterday = str(date.today().replace(day=date.today().day - 1))
    connection = open("hotelnames-"+today+".csv",'a')

class HotelnamesSpider(BaseSpider):
        name = "hotelnames"
        start_urls = ["http://www.hotelnames.net"];
        allowed_domains = ["hotelnames.net"];

        def parse(self,response):
            hxs=HtmlXPathSelector(response)
            select_list = hxs.select("html/body/form/div/fieldset/p/select/option/@value").extract()
            for option in select_list:
                form_req =  FormRequest(url="http://hotelnames.net/zone.php",formdata={'cityname': option},callback=self.choose_zone)
                form_req.meta["city"] = option
                yield form_req

        def choose_zone(self,response):
            hxs=HtmlXPathSelector(response)
            city = response.request.meta["city"]
            zone_list = hxs.select("html/body/form/div/fieldset/p/select[2]/option/@value").extract()
            for zone in zone_list:
                form_req2 =  FormRequest(url="http://hotelnames.net/star.php",formdata={'cityname': city, 'zonename': zone},callback=self.choose_star)
                form_req2.meta["city"] = city
                form_req2.meta["zone"] = zone
                yield form_req2

        def choose_star(self,response):
            
            hxs=HtmlXPathSelector(response)
            city = response.request.meta["city"]
            zone = response.request.meta["zone"]
            star_list = hxs.select("html/body/form/div/fieldset/p/select[3]/option/@value").extract()

            for star in star_list:
                form_req3 =  FormRequest(url="http://hotelnames.net/query_new.php",formdata={'cityname': city,'zonename': zone, 'star': star},callback=self.parse_info)
                form_req3.meta["city"] = city
                form_req3.meta["zone"] = zone
                form_req3.meta["star"] = star
                yield form_req3
        
        def parse_info(self,response):
            hxs =HtmlXPathSelector(response)
            city = response.request.meta["city"]
            title = hxs.select("html/body/fieldset/div/h2/text()").extract()[0]
            table = hxs.select("html/body/fieldset/div/table/tr")
            col = table[2:]
            for row in col:
                star =  row.select(".//td[1]/text()").extract()[0]
                zone =  row.select(".//td[2]/text()").extract()[0].replace(","," ").strip()
                name = row.select(".//td[3]/a/text()").extract()[0].replace(","," ").strip()
                win_prob = row.select(".//td[4]/text()").extract()[0].strip()
                file.connection.write("%s, %s, %s, %s, %s\n" % (str(city),str(star),str(zone),str(name),str(win_prob)))

            
            
def main():
        log.start(logfile="hotel_name_spider_log.txt")
        settings.overrides['USER_AGENT'] = "Mozilla/4.0 (compatible;MSIE 7.0;Windows NT 6.0)"
        settings.overrides['SCHEDULER_ORDER'] = 'BFO'
        crawler = CrawlerProcess(settings)
        crawler.install()
        crawler.configure()
        spider=hotelnames_spider()
        crawler.queue.append_spider(spider)
        crawler.start()
        file.connection.close()
if __name__ == '__main__':
        main()
