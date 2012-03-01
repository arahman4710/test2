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
import urllib

def printable(str):
    control = "".join(map(unichr, range(0,127)))
    control = re.escape( control)
    return re.sub("[^%s]" % control, "", str)

class KayakSpider(BaseSpider):
    name = "KayakSpider"
    start_urls = ["http://www.kayak.com/hotels"];
    allowed_domains = ["kayak.com"];
    selec_city=['Houston'];
    results=[];
    query_price=[];
    price_results={};

    def parse(self, response):

        start_date = str(date.today().strftime('%m/%d/20%y'))
        end_date = str(date.today().replace(day=date.today().day + 1).strftime('%m/%d/20%y'))
        for city in self.selec_city:
            city_request = city
            search = {'othercity': city_request, 'checkin_date': start_date, 'checkout_date': end_date}

            request = FormRequest.from_response(response, formdata = search, callback = self.callfilter)
            request.meta['city'] = city
            yield request

    def callfilter(self, response):

        query = re.search('(?<=\/)[^/]+($|\?)', response.url)
        query = query.group()
#        print response.url
        hxs = HtmlXPathSelector(response)
        temp_url=hxs.select(".//*[contains(@id,'priceAnchor')]/a/@target").extract()
        url = ''
        for one in temp_url:
            print str(one)
            url += str(one)
        request = Request("http://www.kayak.com/s/jsresults?ss=1&searchid=" + url[url.find('bookit_')+7:url.find('_',url.find('bookit_')+12,len(url))] + "&pn=0", callback = self.filtered)
        request.meta['city'] = response.request.meta['city']
        request.meta['page'] = 0
        return request

    def filtered(self, response):

        doc = printable(response.body)
        hxs = HtmlXPathSelector(response)
        hotels = hxs.select("//div[contains(@id, 'tbd') and not(contains(@class, 'opaque'))]/div[@class='inner']")
        found = 0

        for div in hotels:
            id = div.select(".//div[contains(@id, 'resultid')]/text()")
            name = div.select(".//div[contains(@id, 'hname')]/text()")
            address = div.select(".//a[@class='subtlelink'][1]/text()")
            star = div.select(".//div[contains(@class,'starsprite')]/@class")
            price = div.select(".//span[contains(@id,'priceAnchor')]/a/text()")
            if (id and name and address and price):
                found = 1
                id = id[0].extract()
                name = name[0].extract()
                address = address[0].extract()
                price = price[0].extract()
                print id, name, address, price

        if found:
            url = response.url
            page = response.request.meta['page']
            url = re.sub("pn.*?(&|$)", "pn=" + str(page + 1) + "&", response.url)

            request = Request(url, callback = self.filtered)
            request.meta['city'] = response.request.meta['city']
            request.meta['page'] = page + 1
            return request
        else:
            pass

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

    
                
                

        
