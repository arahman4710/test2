import Levenshtein
from scrapy.selector import HtmlXPathSelector,XmlXPathSelector
from scrapy.http import FormRequest
from scrapy.conf import settings
from scrapy.crawler import CrawlerProcess
from scrapy.spider import BaseSpider
from scrapy import signals,log
from scrapy.xlib.pydispatch import dispatcher
from scrapy.http import Request
from scrapy.contrib.spiders import XMLFeedSpider
import re
from datetime import date
import time
import MySQLdb
import urllib
import sys
import json


class hotwire_api_analysis(BaseSpider):
        name = "hotwire_api_analysis"
        download_delay = 0.5
        allowed_domains = ["hotwire.com"];
        input = []
        hotel_count=0
        review_count = 0
        original_amenties={}
        meta_regions = {}
        meta_amineties = {}
        city_names =['Houston, Texas, USA','Toronto','New York, New York','Los Angeles, California','Chicago, Illinois','Ottawa, ON Canada','Vancouver, BC Canada','Calgary, AB Canada','Boston, Massachusetts','Anchorage, AK']
        api_key='eupzwn43dwtmgxhmkw5pbta7'
        region_name={}
        diff = 4
        start_date ='01/16/2011'#str(date.today().strftime('%m/%d/20%y'))    #start date in the format mm/dd/yyyy
        end_date = '01/17/2011'#str(date.today().replace(day=date.today().day +diff ).strftime('%m/%d/20%y'))   #end date in the format mm/dd/yyyy
        log_file = open("C://Users//Areek//Documents//workspace//hotwire_api_analysis//src//res2//"+str(date.today())+"_"+str(time.strftime('%H-%M'))+".csv",'w')    #str(time.strftime('%x_%X')+
        start_urls = [base_query_format % (api_key, city_name, start_date, end_date) for city_name in city_names];


        def parse(self, response):
            #print response.url
            hxs = XmlXPathSelector(response)
            temp_regions = []
            hotel_list = []
            #region_url=''
            #regions={}
            #amineties={}
            #region_url= hxs.select("//Hotwire/Result/HotelResult[1]/DeepLink/text()").extract()[0]
            #print region_url
            temp_regions = hxs.select("//Hotwire/MetaData/HotelMetaData/Neighborhoods/Neighborhood")
            temp_amineties = hxs.select("//Hotwire/MetaData/HotelMetaData/Amenities/Amenity")
            hotel_list = hxs.select("//Hotwire/Result/HotelResult")
           #self.log_file.write("Hrefno.,Resultid,Region|City,Amenties,HotelStar,Average Price per night,Tax and fees,Nights,Total price,Recommandation,Tripadvisor Rating\n")

            if temp_amineties:
                for ami in temp_amineties:
                    code = str(ami.select(".//Code/text()").extract()[0])
                    ami_name = str(ami.select(".//Name/text()").extract()[0]).strip().lower()
                    self.meta_amineties[code]=ami_name

            if temp_regions:
                for reg in temp_regions:
                    region_name=reg.select(".//Name/text()").extract()[0].strip()
                    region_id=float(reg.select(".//Id/text()").extract()[0].strip())
                    region_city = reg.select(".//City/text()").extract()[0].strip()
                    self.meta_regions[region_id] = region_name+', '+region_city

            if hotel_list:
                for hotel in hotel_list:
                    temp_star=hotel.select(".//StarRating/text()").extract()[0]
                    hotel_region=hotel.select(".//NeighborhoodId/text()").extract()[0]
                    hotel_ami_list = hotel.select(".//AmenityCodes/Code/text()")
                    deep_link = hotel.select(".//DeepLink/text()").extract()[0].replace("&amp;","&")
                    result_id = hotel.select(".//ResultId/text()").extract()[0]
                    temp_avg_price = hotel.select(".//AveragePricePerNight/text()").extract()[0]
                    temp_hrefno = hotel.select(".//HWRefNumber/text()").extract()[0]
                    temp_taxnfees = hotel.select(".//TaxesAndFees/text()").extract()[0]
                    temp_nights = hotel.select(".//Nights/text()").extract()[0]
                    temp_tprice = hotel.select(".//TotalPrice/text()").extract()[0]
                    amenties =""
                    for ami_list in hotel_ami_list:
                        amenties+=self.meta_amineties[ami_list.extract()]+'|'
                    amenties=amenties[0:-1]
                    info = temp_hrefno+', '+result_id+', '+str(self.meta_regions[float(hotel_region)]).replace(",","|")+', '+amenties+', '+temp_star+', '+temp_avg_price+', '+temp_taxnfees+', '+temp_nights+', '+temp_tprice
                    reqq= Request(deep_link+result_id,callback=self.hotel_page)
                    reqq.meta["info"] = info
                    yield reqq

        def hotel_page(self,response):
            #print response.url
            tripadvisor_rating =''
            recommandation =''
            if response.body:
                hxs = HtmlXPathSelector(response)
                temp_tripadvisor_rating =hxs.select(".//div[@class ='tripAdvisor']/strong/text()|.//*[@id='areaInf']/div[1]/div[2]/strong/text()")
                temo_recommandation = hxs.select(".//*[@id='customerReviews']/div/div[1]/div[2]/text()")
                if temp_tripadvisor_rating:
                    tripadvisor_rating = temp_tripadvisor_rating.extract()[0].replace(" out of 5.0","").replace(" out of 5","")
                if temo_recommandation:
                    recommandation =temo_recommandation.extract()[0].replace("%","")
                self.log_file.write(response.request.meta["info"]+', '+recommandation+', '+tripadvisor_rating+'\n')




def main():
       # log.start(logfile="hotwire_api_analysis.txt")
        settings.overrides['USER_AGENT'] = "Mozilla/5.0 (Windows; U; Windows NT 6.0; en-US) AppleWebKit/534.10 (KHTML, like Gecko) Chrome/8.0.552.224 Safari/534.10"
        settings.overrides['SCHEDULER_ORDER'] = 'BFO'
        crawler = CrawlerProcess(settings)
        crawler.install()
        crawler.configure()
        spider=hotwire_api_analysis()
        crawler.queue.append_spider(spider)
        crawler.start()
        spider.log_file.close()


if __name__ == '__main__':
        main()
