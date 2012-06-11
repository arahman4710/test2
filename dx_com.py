# -*- coding: UTF-8 -*-
# Spider for 'dx.com'
#Author: (Anik) Sajidur Rahman 
import re
from urllib import quote

from scrapy.spider import BaseSpider
from scrapy.http import  Request
from scrapy.selector import HtmlXPathSelector
from scrapy.contrib.loader import XPathItemLoader
from scrapy.contrib.loader.processor import TakeFirst
from scrapy import log
from dealextremeproject.items import DealextremeItem

class Dealextreme(BaseSpider):
    
    name = 'dx'
    start_urls = ['http://www.dx.com/']
    URL = 'http://www.dx.com'
    failed = set()
    def parse(self, response):
        return Request('http://www.dx.com/c/health-beauty-1799/wigs-1729?page=1&pagesize=52&pagesort=relevance',
                       callback=self.list_items)
#        hxs = HtmlXPathSelector(response)
#        for category in hxs.select("//div[@class='category']//ul[@class='sub_menu']//a/@href").extract():
#            if '-warehouse' in category:continue
##            if 'cell-phones-511' not in category:continue
#            yield Request(self.URL+category.strip()+'?page=1&pagesize=40&pagesort=popularity',
#                           callback=self.list_items)
    
    
    def list_items(self, response):
        hxs = HtmlXPathSelector(response)
        current_page = hxs.select("//div[@class='ProductPager']/a[contains(@class, 'Selected')]/text()").extract()
        try:
            start_idx = (int(current_page[0])*40)-40
        except Exception:
            start_idx = 1
        counter = 1
        for item in hxs.select("//div[@id='proList']/ul[@class='productList subList']/li/div[@class='photo']"):
            index = item.select(".//a[@href]").extract()[0].index('"')
            index2 = item.select(".//a[@href]").extract()[0].index('"',index+1)
            href  = item.select(".//a[@href]").extract()[0][index+1:index2]
            url = self.URL + href
            yield Request(url.strip(), meta={'counter':unicode(counter+start_idx)},
                          callback=self.get_item)
            counter += 1
        
        next_page = hxs.select("//div[@class='page_wrapper']/a[contains(text(), 'Next')]/@href").extract()
        if next_page:
            yield Request(self.URL+next_page[0].strip(), callback=self.list_items)
    
    def get_item(self, response):
        hxs = HtmlXPathSelector(response)
        l = XPathItemLoader(DealextremeItem(), hxs)
        l.add_value('url', [unicode(response.url)])
        l.add_value('popularity', [response.request.meta['counter']])
        l.add_xpath('categories', "//div[@class='position']/a[not(@href='/')]/text()")
        l.add_xpath('title', "//div[@class='pinfo_wrapper']/h1/text()".strip(), TakeFirst())
        l.add_xpath('price', "//span[@id='price']//text()", TakeFirst())
        l.add_xpath('sku', "//span[@id='sku']/text()", TakeFirst())
        l.add_xpath('diggs', "//span[@class='db-count']/text()", TakeFirst())

        l.add_xpath('shipping', "//table[@class='product_detail']/tbody/tr[3]/td[2]/text()",TakeFirst())    #not finished    
##        l.add_xpath('us_sku', "//div[@id='warehouse']//a/text()", TakeFirst()) #nf
        l.add_xpath('reviews', "//div[@class='reviewTxt']/text()",
                    TakeFirst(), re=r"\((\d+?) votes")  #maybe finished
        l.add_xpath('images', "//ul[@id='product-small-images']/li/a/@href") #maybe finished
        l.add_xpath('rating', "//b[@class='starts']//text()")
##        if hxs.select("//img[@alt='IN STOCK']"):    #nf
##            l.add_value('in_stock', [u'True'])
##        else:
##            l.add_value('in_stock', [u'False'])
##        
        l.add_value('overview', [u'\r\n'.join([i.strip() for i in
                        hxs.select("//div[@id='overview']//text()").extract()
                        if i.strip()])])
        l.add_value('specifications', [u'\r\n'.join([i.strip() for i in 
                            hxs.select("//div[@id='specification']//text()").extract()
                                                if i.strip()])])
        l.add_xpath('gplus',"//span[@id='aggregateCount']//text()")
        l.add_xpath('fb',"//span[@class='connect_widget_not_connected_text']//text()")
        l.add_xpath('videos',"//div[@id='customer-videos-containter']/@href")
        item = l.load_item()
        item['shipping'][0] = item['shipping'][0].strip()
        item['title'] = [(item['title'][0].strip())]
        item['categories'][0] = [item['categories'][0].replace("&amp"," ")]
        return item





##        fb = hxs.select("//div[@class='facebook']//iframe/@src").extract()
##        item = l.load_item()
##        for f in item:
##            if f in ['images', 'categories',]:continue
##            if isinstance(item[f], list):
##                item[f] = item[f][0]
##            if isinstance(item[f], basestring):
##                item[f] = item[f].strip()
##        if 'sku' not in item or not item['sku']:
##            if response.url in self.failed:
##                self.log('failed to get item - %s' %response.url, log.ERROR)
##                self.failed.remove(response.url)
##                return
##            else:
##                self.failed.add(response.url)
##                return Request(response.url, meta={'counter':response.request.meta['counter']},
##                           priority=-1,
##                           callback=self.get_item)
##        try:
##            print item['title']
##        except Exception:pass
##        user_images = hxs.select("//div[@class='Description']//a[span[@id='customerPicturesCount']]/@href").extract() #nf
##        if videos:
##            item['videos'] = self.URL + videos[0]
##        if user_images:
##            item['user_images'] = self.URL + user_images[0]
##        if fb:
##            item['gplus'] = 'https://plusone.google.com/_/+1/fastbutton?url=' +\
##                            quote(gplus[0])
##            return Request(fb[0], meta={'item':item, 'type':'fb'},
##                           callback=self.get_likes)
##        elif gplus:
##            return Request(gplus[0], meta={'item':item, 'type':'gplus'},
##                           callback=self.get_likes)
##        return self.media_request(item)
##        return self.sku_request(item)
##        
##    def get_likes(self, response):
##        hxs = HtmlXPathSelector(response)
##        item = response.request.meta['item']
##        if response.request.meta['type']=='fb':
##            likes = hxs.select("//span[@class='connect_widget_not_connected_text']"\
##                               "/text()").re(r"(\d+?) likes")
##            item['fb'] = likes[0] if likes else u''
##            if item['gplus']:
##                return Request(item['gplus'], meta={'item':item, 'type':'gplus'},
##                           callback=self.get_likes)
##        else:
##            g = hxs.select("//span[@id='aggregateCount']/text()").extract()
##            item['gplus'] = g[0] if g else u''
##        return self.media_request(item)
##    
##    def media_request(self, item):
##        if 'videos' in item and item['videos']:
##            return Request(item['videos'], meta={'item':item},
##                           callback=self.list_videos)
##        if 'user_images' in item and item['user_images']:
##            return Request(item['user_images'], meta={'item':item},
##                           callback=self.list_images)
##        return self.sku_request(item)
##        
##    def list_videos(self, response): #nf
##        hxs = HtmlXPathSelector(response)
##        item = response.request.meta['item']
##        item['videos'] = ['http://www.youtube.com/watch?v='+i for i in
##                          hxs.select("//table//a/@href").re("play\('(.+?)',")]
##        if 'user_images' in item and item['user_images']:
##            return Request(item['user_images'], meta={'item':item},
##                           callback=self.list_images)
##        return self.sku_request(item)
##    
##    def list_images(self, response): #nf
##        hxs = HtmlXPathSelector(response)
##        item = response.request.meta['item']
##        item['user_images'] = [self.URL + i for i in 
##                               hxs.select("//table//a/@href").re("enlarge\('(.+?)',")]
##        return self.sku_request(item)
##    
##    def sku_request(self, item): #maybe done
##        if 'sku' in item and item['sku']:
##            return Request('http://www.dealextreme.com/ajax/WarehouseCheck.ashx?sku=%s' %item['sku'],
##                       meta={'item':item}, callback=self.get_sku)
##        return item
##        
##    def get_sku(self, response):  #maybe done
##        item = response.request.meta['item']
##        sku = re.findall(r">(\d+?)<", response.body )
##        item['us_sku'] = sku[0] if sku else u''
##        return item
##        
##        
##        
