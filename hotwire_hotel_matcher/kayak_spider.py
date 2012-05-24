
from tripadvisor_hotel_comparer import *
from decimal import *
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


def printable(str):
    control = "".join(map(unichr, range(0,127)))
    control = re.escape( control)
    return re.sub("[^%s]" % control, "", str)


class KayakSpider(BaseSpider):
	name = "KayakSpider"
	start_urls = ["http://www.kayak.com/hotels"];
	allowed_domains = ["kayak.com"];
	selec_city=[]
	results=[]
        query_price=[]
        price_results={}

	def parse(self, response):

		# 1  Finds all of the distinct city + state combinations from the table
		#
                '''
		db1= MySQLdb.connect(user='root', passwd='charles', db='acuity')
		c = db1.cursor()
		c.execute("SELECT city, state FROM cities WHERE NOT city='' AND NOT state=''")
		cities = c.fetchall()
		'''
                start_date=str(date.today().strftime('%m/%d/20%y'))
                end_date = str(date.today().replace(day=date.today().day + 1).strftime('%m/%d/20%y'))

		for city in self.selec_city:
			# 2a  Format the search parameters
			#
			city_request = city
			search = {'othercity': city_request, 'checkin_date': start_date, 'checkout_date': end_date}

			# 2b Create searches for each of the cities
			#    pass the city and state data along with each request
			#
			request = FormRequest.from_response(response, formdata = search, callback = self.callfilter)
			request.meta['city'] = city
			yield request


	def callfilter(self, response):

		# 1  Finds the query id of the current city/date combination
		#
                #print response.body
		query = re.search('(?<=\/)[^/]+($|\?)', response.url)
		query = query.group()

		# 2  Creates a query to the js results page and passes along the city request information
		#
                hxs = HtmlXPathSelector(response)
                temp_url=hxs.select(".//*[contains(@id,'priceAnchor')]/a/@target").extract()
                url=''
                for one in temp_url:
                    url+=str(one)
		request = Request("http://www.kayak.com/s/jsresults?ss=1&searchid=" + url[url.find('bookit_')+7:url.find('_',url.find('bookit_')+12,len(url))] + "&pn=0", callback = self.filtered)
		request.meta['city'] = response.request.meta['city']
		request.meta['page'] = 0
		return request

	def filtered(self, response):

		# 1  Find all the hotel information on the page
		#
		doc = printable(response.body)
               # print doc
		hxs = HtmlXPathSelector(response)
		hotels = hxs.select("//div[contains(@id, 'tbd') and not(contains(@class, 'opaque'))]/div[@class='inner']")
		found = 0
		#city = response.request.meta['city']
		#cityid = find_city(city[0], city[1], "united states", c)

                print 'IN'
		for div in hotels:

			# 2  Find the section containing hotel id, name, and address in the string
			#
                    
			id = div.select(".//div[contains(@id, 'resultid')]/text()")
			name = div.select(".//div[contains(@id, 'hname')]/text()")
			address = div.select(".//a[@class='subtlelink'][1]/text()")
                        star = div.select(".//div[contains(@class,'starsprite')]/@class")
                        #price =div.select(".//span[contains(@class,'pricerange')]/text()")
                        #replace starsprite star

			if (id and name and address):

				# 3  Isolate the information from the sections taken
				#
				found = 1
				#global global_found
				#global_found = 1
                                id = id[0].extract()
                                #new
                                if not self.query_price:
                                #

                                    name = name[0].extract()
                                    address = address[0].extract()
				#star = star[0].extract().replace("starsprite star","")
                                    self.results.append([printable(name),id,printable(address)])

                                #new
                                else:#.//span[contains(@class,'pricerange')]/text()
                                    price =div.select(".//span[contains(@id,'priceAnchor')]/a/text()")
                                    print id
                                    if int(id) in self.query_price:
                                        self.price_results[id] =price[0].extract()
                                        print price[0].extract()
                                        print 'got for '+str(id)
                                #
                                #price = price[0].extract().replace("$","")

				# 4  Match the hotel to one of our records or insert a new entry into the database
				#
				#match_hotel(id, name, address, cityid)

		if found:
			# Find the url of the next page
			#
			url = response.url
			page = response.request.meta['page']
			url = re.sub("pn.*?(&|$)", "pn=" + str(page + 1) + "&", response.url)

			# Navigate to the next page
			#
			request = Request(url, callback = self.filtered)
			request.meta['city'] = response.request.meta['city']
			request.meta['page'] = page + 1
			return request

		else:
			pass



def main():
        log.start(logfile="kayak_spider.txt")
        settings.overrides['USER_AGENT'] = "Mozilla/5.0 (Windows; U; Windows NT 6.0; en-US) AppleWebKit/534.10 (KHTML, like Gecko) Chrome/8.0.552.224 Safari/534.10"
        settings.overrides['SCHEDULER_ORDER'] = 'BFO'
        crawler = CrawlerProcess(settings)
        crawler.install()
        crawler.configure()
        spider=KayakSpider()
        spider.selec_city=['Houston,TX']
        crawler.queue.append_spider(spider)
        crawler.start()
        print spider.results
        lst=[]
        lst=spider.results
        com_kayak_internal(lst)
        #print spider.hotel_results

def qurey_price_kayak(kayak_id):
    
    settings.overrides['USER_AGENT'] = "Mozilla/5.0 (Windows; U; Windows NT 6.0; en-US) AppleWebKit/534.10 (KHTML, like Gecko) Chrome/8.0.552.224 Safari/534.10"
    settings.overrides['SCHEDULER_ORDER'] = 'BFO'
    crawler = CrawlerProcess(settings)
    crawler.install()
    crawler.configure()
    
    spider=KayakSpider()
    spider.selec_city=['Houston,TX']
    spider.query_price=kayak_id
    crawler.queue.append_spider(spider)
    for id in kayak_id:
        print '     '+str(id)
    crawler.start()
    print "saaa"
    return spider.price_results

def run_price_query(kayak_id):
    return qurey_price_kayak(kayak_id)

@print_timing
def main():
        read_file=open('output.csv','r')
        get_id={}
        for lines in read_file.readlines():
            line=lines.split(',')
            print lines
            get_id[line[1]]=line[2]
        read_file.close()
        print get_id.keys()
        live_price = run_price_query(map(int,get_id.keys()))
        print live_price
        update_file=open('res/hotwire_hotel.csv','r')
        write_file=open('res/hotwire_hotel_with_kayak_price.csv','w')
        print get_id.keys()
        for line in update_file.readlines():
            print line.split(',')[1]

            if line.split(',')[1] in get_id.values():
               print 'yes'
               key = [str(k) for k, v in get_id.iteritems() if v == line.split(',')[1]][0]
               if key in live_price:
                    write_file.write(line[:-2]+','+live_price[key]+'\n')
            else:
                write_file.write(line)

        update_file.close()
        write_file.close()

        
if __name__ == '__main__':
        main()
        #print temp
        #main()
