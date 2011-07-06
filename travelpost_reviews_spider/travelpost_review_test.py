""" Get the spider running see whats going on! then get the vars into dictionaries
as soon as you know the vars were getting are fine"""

from decimal import *
from scrapy.selector import HtmlXPathSelector
from scrapy.http import FormRequest
from scrapy.conf import settings
from scrapy import signals,log
from scrapy.crawler import CrawlerProcess
from scrapy.spider import BaseSpider
from scrapy.xlib.pydispatch import dispatcher
from scrapy.http import Request
import re
import time

#sql alchemy imports 
from sqlalchemy import *
from sqlalchemy.sql import and_

# local imports 
#from alchemy_session import get_alchemy_info

import urllib
import sys

sys.path.insert(0, __file__)

#from hotel_reviews import *

def printable(str):
    control = "".join(map(unichr, range(0,127)))
    control = re.escape(control)
    return re.sub("[^%s]" % control, "", str)


"""To be replaced with sql alchemy"""
#class Connection():
#	database = MySQLdb.connect(user='root', passwd='areek', db='acuity')
#	cursor = database.cursor()

class ReviewSpider(BaseSpider):
        name = "ReviewSpider"    
        start_urls = ["http://www.travelpost.com/"];
        allowed_domains = ["travelpost.com"];
        input = []
        s=0
        review_count = 0

        def parse(self, response):
                for city in self.input:
                        print city
                        request = Request("http://www.travelpost.com/h/travelpost/tpsmarty?where="+city+"&lc=en&lc_cc=US&s=3&f=h",callback =self.findApproxCities)
                        request.meta["city"] = city
                        #request = Request("http://www.travelpost.com/search.aspx?srch=%s" % city,callback =self.findApproxCities)
                        yield request



        def findApproxCities(self,response):
            hxs=HtmlXPathSelector(response)
            print response.body
            city_id = hxs.select("html/body/ul/li[1]/@id").extract()[0]
            print city_id
            city_id = city_id.replace("citypage-","")
            city = response.request.meta["city"]
            #http://www.travelpost.com/search.aspx?srch=Houston,%20TX%C2%A0%C2%A0%E2%86%92%C2%A0%C2%A0All%20hotels&h=c31193
            resp= Request("http://www.travelpost.com/search.aspx?srch=%s&h=%s" % (city,city_id),callback=self.findhotels)
            resp.meta["backlink"] ="http://www.travelpost.com/search.aspx?srch=%s&h=%s" % (city,city_id)
            resp.meta["redir"] = 1
            yield resp
            '''
            if(hxs.select("//td[starts-with(@class, 'geofacet')]")):
                area=hxs.select(".//span/a/@href").extract()
                for one in area:
                    if(one.find("Canada")!=-1):
                        resp= Request("http://www.travelpost.com%s" % one,callback=self.findhotels)
                        resp.meta["backlink"] ="http://www.travelpost.com%s" % one
                        yield resp
                    if(one.find("United+States")!=-1):
                        resp= Request("http://www.travelpost.com%s" % one,callback=self.findhotels)
                        resp.meta["backlink"] ="http://www.travelpost.com%s" % one
                        yield resp
            else:
                resp= Request(response.url,callback=self.findhotels)
                resp.meta["backlink"] =response.url
                yield resp
            '''
        
        def findhotels(self,response):
            print response.url
            if response.url:
                if response.request.meta["backlink"]:
                    if response.request.meta["backlink"]==response.url or response.request.meta["redir"]:
                        hxs=HtmlXPathSelector(response)
                        for hotels in hxs.select("//table[starts-with(@id, 'rslt')]"):
                            if hotels.select(".//tr[2]/td/div[4]/span[2]/a/@href"):
                                insert_sql = "INSERT INTO `acuity`.`travelpost_hotel_review_overview` "
                                insert_param_sql = "( "
                                insert_value_sql = "VALUES ( "
                                temp_id = hotels.select(".//tr[2]/td[2]/table/tbody[1]/tr[1]/td[1]/a/@href")
                                temp_userrating = hotels.select(".//span[@class = 'userrating']/b/text()")
                                temp_url = hotels.select(".//tr[2]/td/div[4]/span[2]/a/@href")
                                hotelID=""
                                hotel=""
                                full_url=""
                                temp_name = hotels.select(".//tr[1]/td[1]/a/text()")
                                userrating="0.0"
                                if temp_id:
                                    hotelID = temp_id.extract()[0]
                                    print hotelID[hotelID.find("hid") + 3:hotelID.find("?")]
                                    insert_param_sql +="`hotelid`,"
                                    insert_value_sql +="'"+ str(hotelID[hotelID.find("hid") + 3:]) +"',"
                                    hotelID = str(hotelID[hotelID.find("hid") + 3:])#str(hotelID[hotelID.find("hid") + 3:hotelID.find("?")])
                                if temp_userrating:
                                    userrating=temp_userrating.extract()[0]
                                    insert_param_sql +="`averagerating`,"
                                    insert_value_sql +="'"+ printable(re.sub('''(['"])''', r'\\\1',userrating.strip())) +"',"
                                if temp_name:
                                    hotel= temp_name.extract()[0].replace("&amp;","")
                                    insert_param_sql +="`hotelname`,"
                                    insert_value_sql +="'"+ printable(re.sub('''(['"])''', r'\\\1',hotel.strip())) +"',"
                                if temp_url:
                                    full_url = "http://www.travelpost.com%s" % temp_url.extract()[0]
                                    insert_param_sql +="`hotelurl`,"
                                    insert_value_sql +="'"+ printable(re.sub('''(['"])''', r'\\\1',full_url.strip())) +"',"
                                insert_param_sql =  insert_param_sql[0:-1] + ")"
                                insert_value_sql = insert_value_sql[0:-1] + ");"
                                try:
                                    Connection.cursor.execute(insert_sql + insert_param_sql + insert_value_sql)
                                    Connection.database.commit()
                                except:
                                    log.msg(insert_sql + insert_param_sql + insert_value_sql,level=log.ERROR)
                                equest= Request(full_url,callback=self.getReview)
                                equest.meta["hotel"] = hotelID
                                equest.meta["backlink"] = full_url
                                yield equest
                    else:
                        return
                if hxs.select("//div[@id='page']"):
                        if hxs.select("//*[@id='page']/span/a/text()").extract()[-1][0] == 'N':
                            print "s"
                            equest = Request("http://www.travelpost.com%s" % hxs.select("//*[@id='page']/span/a/@href").extract()[-1],callback=self.findhotels)
                            equest.meta["backlink"] = "http://www.travelpost.com%s" % hxs.select("//*[@id='page']/span/a/@href").extract()[-1]
                            equest.meta["redir"] = 0
                            yield equest


        def getReview(self,response):
            if response.request.meta["backlink"]:
                if response.request.meta["backlink"]==response.url:
                    hxs=HtmlXPathSelector(response)
                    hotel = response.request.meta["hotel"]

                    for content in hxs.select("//table[@class='rec-prof']"):
                        #insert_sql = "INSERT INTO `acuity`.`travelpost_hotel_review_description` "
                        #insert_param_sql = "( `hotel_id`, "
                        #insert_value_sql = "VALUES ( '"+ printable(re.sub('''(['"])''', r'\\\1',hotel.strip())) +"', "
                        temp_reviewurl = content.select(".//td[contains(@class , 'title')]/a/@href|.//tr[3]/td[2]/div[1]/div/p[2]/a/@href")
                        temp_source = content.select(".//tr[2]/td/span[1]/img/@title")
                        temp_rate = content.select(".//tr[4]/td[1]/div[2]/text()|.//tr[3]/td[1]/div[2]/text()")
                        temp_date = content.select(".//tr[2]/td/span[2]/text()")
                        temp_reviewertype = content.select(".//tr[4]/td[2]/div[1]/span/div/text()|.//tr[3]/td[2]/div[1]/span/div/text()")
                        temp_content = content.select(".//tr[4]/td[2]/div[1]/div/p/text()|.//tr[3]/td[2]/div[1]/div/p/text()")
                        temp_id = content.select(".//tr[contains(@id, 'helpfulCounts')]/@id")
                        #if temp_id:
                        #    id = temp_id.extract()[0].replace("helpfulCounts","")
                        #    insert_param_sql +="`review_id`,"
                        #    insert_value_sql +="'"+ str(id) +"',"
                        #if temp_reviewurl:
                        #    url = temp_reviewurl.extract()[0]
                        #    if url[0]=='/':
                        #        url = "http://www.travelpost.com" + url
                        #    insert_param_sql +="`link`,"
                        #    insert_value_sql +="'"+ printable(re.sub('''(['"])''', r'\\\1',url.strip())) +"',"
                        #if temp_source:
                        #    source = temp_source.extract()[0]   #source
                        #    insert_param_sql +="`Source`,"
                        #    insert_value_sql +="'"+ printable(re.sub('''(['"])''', r'\\\1',source.strip())) +"',"
                        #if temp_rate:
                        #    rate = temp_rate.extract()[0]      #rating
                        #    insert_param_sql +="`rating`,"
                        #    insert_value_sql +="'"+ printable(re.sub('''(['"])''', r'\\\1',rate.strip())) +"',"
                        #if temp_date:
                        #    postedDate=  temp_date.extract()[0]   #postedDate
                        #    insert_param_sql +="`postedDate`,"
                        #    insert_value_sql +="'"+ printable(re.sub('''(['"])''', r'\\\1',postedDate.strip().replace("Posted ",""))) +"',"
                        #if temp_reviewertype:
                        #    reviewType = temp_reviewertype.extract()[0] #reviewerType
                        #    insert_param_sql +="`reviewerType`,"
                        #    insert_value_sql +="'"+ printable(re.sub('''(['"])''', r'\\\1',reviewType.strip())) +"',"
                        #if temp_content:
                        #    reviewContent =  temp_content.extract()    #reviewcontent
                        #    review=""
                        #    if reviewContent:
                        #        for rc in reviewContent:
                        #            review += rc.strip()
                        #    insert_param_sql +="`reviewContent`,"
                        #    insert_value_sql +="'"+ printable(re.sub('''(['"])''', r'\\\1',review.strip())) +"',"
                        #
                        #insert_param_sql =  insert_param_sql[0:-1] + ")"
                #    if value_sql[-1]==',':
                        #insert_value_sql = insert_value_sql[0:-1] + ");"
                        #try:
                        #    Connection.cursor.execute(insert_sql + insert_param_sql + insert_value_sql)
                        #    Connection.database.commit()
                        #except:
                        #    log.msg(insert_sql + insert_param_sql + insert_value_sql,level=log.ERROR)
                else:
                    return
            if hxs.select("//div[@id='page']"):
                if hxs.select("//*[@id='page']/span/a/text()").extract()[-1][0] == 'N':
                    #print "s"
                    response = Request("http://www.travelpost.com%s" % hxs.select("//*[@id='page']/span/a/@href").extract()[-1],callback=self.getReview)
                    response.meta["hotel"] = hotel
                    response.meta["backlink"] = "http://www.travelpost.com%s" % hxs.select("//*[@id='page']/span/a/@href").extract()[-1]
                    yield response 


def main():
        log.start(logfile="TravelPost_review_spider_log.txt")
        settings.overrides['USER_AGENT'] = "Mozilla/4.0 (compatible;MSIE 7.0;Windows NT 6.0)"
        settings.overrides['SCHEDULER_ORDER'] = 'BFO'
        #Connection.cursor.execute("CREATE TABLE IF NOT EXISTS `travelpost_hotel_review_overview` \
        #(`hotelname` TEXT,`numberofreviews` INT(11) DEFAULT NULL,`averagerating` DOUBLE DEFAULT NULL,\
        #`hotelid` INT(11) DEFAULT NULL,`hotelurl` TEXT) ENGINE=INNODB DEFAULT CHARSET=utf8")
        #Connection.database.commit()
        #Connection.cursor.execute("CREATE TABLE IF NOT EXISTS `travelpost_hotel_review_description` \
        #(`reviewerType` TEXT,`reviewContent` TEXT,`postedDate` TEXT,`link` TEXT,`rating` TEXT,\
        #`hotel_id` TEXT,`Source` TEXT,`review_id` INT(11) DEFAULT NULL) ENGINE=INNODB DEFAULT CHARSET=latin1")
        #Connection.database.commit()
        crawler = CrawlerProcess(settings)
        crawler.install()
        crawler.configure()
        spider = ReviewSpider()
        cities = ['New York, New York','Los Angeles, California','Chicago, Illinois','Houston, Texas','Philadelphia, Pennsylvania',
        'Phoenix, Arizona','San Diego, California','Dallas, Texas','San Antonio, Texas','Detroit, Michigan','San Jose, California',
        'Indianapolis, Indiana','San Francisco, California','Jacksonville, Florida','Columbus, Ohio','Austin, Texas','Memphis, Tennessee',
        'Baltimore, Maryland','Milwaukee, Wisconsin','Boston, Massachusetts','Charlotte, North Carolina','El Paso, Texas','Washington, D.C.',
        'Seattle, Washington','Fort Worth, Texas','Denver, Colorado','Nashville, Tennessee','Portland, Oregon','Oklahoma City, Oklahoma',
        'Las Vegas, Nevada','Toronto','Ottawa, ON Canada','Vancouver, BC Canada','Calgary, AB Canada']
        test_city = ['houston,Tx']
        spider.input = test_city
        crawler.queue.append_spider(spider)
        crawler.start()
        log.msg("Calculating Number of reviews...",level=log.INFO)
        #db = Connection.database
        #c = Connection.cursor
        #c.execute("select hotelid from travelpost_hotel_review_overview")
        #for hotel in c.fetchall():
        #    c.execute("SELECT COUNT(*) FROM travelpost_hotel_review_description WHERE hotel_id = '%s'" % hotel[0])
        #    numreview = c.fetchall()
        #    for number in numreview:
        #        c.execute("UPDATE `acuity`.`travelpost_hotel_review_overview` SET `numberofreviews` = '%s' WHERE \
        #        `hotelid` = '%s';" % (number[0],hotel[0] ))
        #        db.commit()
        #log.msg("COMPLETED!",level=log.INFO)
        #Connection.database.close()

                
if __name__ == '__main__':
        main()
