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
import re
import time
import MySQLdb
import urllib
import sys
import json

def printable(str):
 control = "".join(map(unichr, range(0,127)))
 control = re.escape( control)
 return re.sub("[^%s]" % control, "", str)


class Connection():
	database = MySQLdb.connect(user='root', passwd='areek', db='acuity')
	cursor = database.cursor()

class PLReviewSpider(BaseSpider):
        name = "PLReviewSpider"
        start_urls = ["http://www.priceline.com/"];
        allowed_domains = ["priceline.com"];
        input = []
        connection = Connection.database
        hotel_count=0
        review_count = 0

        def parse(self, response):
            for city in self.input:
                req = Request("http://travela.priceline.com/hotel/searchHotels.do?session_key=&plf=pclh&INIT_SESSION=true&irefid=HPSAVEDSEARCH_5&irefclickid=0|4250065863|14646582543&searchType=CITY&cityName="+city+"&numberOfRooms=1&hotelBrand=&searchHotelName=&starRating=-1&noDatesSearch=Y&KMode=Y&selectedTab=0&passingValues=YES&affiliateSubID=514A",callback=self.callfilter)
                req.meta["city"]=city
                yield req

        def callfilter(self,response):
            hxs=HtmlXPathSelector(response)
            jsk = hxs.select("//*[@name='jsk']/@value").extract()[0]
            key = hxs.select("//*[@name='key']/@value").extract()[0]
            passingValues = hxs.select("//*[@name='passingValues']/@value").extract()[0]
            affiliateSubID  = hxs.select("//*[@name='affiliateSubID']/@value").extract()[0]
            hotelBrand = hxs.select("//*[@name='hotelBrand']/@value").extract()[0]
            irefid = hxs.select("//*[@name='irefid']/@value").extract()[0]
            cityName = hxs.select("//*[@name='cityName']/@value").extract()[0]
            numberOfRooms = hxs.select("//*[@name='numberOfRooms']/@value").extract()[0]
            searchType = hxs.select("//*[@name='searchType']/@value").extract()[0]
            noDatesSearch = hxs.select("//*[@name='noDatesSearch']/@value").extract()[0]
            plf = hxs.select("//*[@name='plf']/@value").extract()[0]
            searchHotelName = hxs.select("//*[@name='searchHotelName']/@value").extract()[0]
            starRating = hxs.select("//*[@name='starRating']/@value").extract()[0]
            KMode = hxs.select("//*[@name='KMode']/@value").extract()[0]
            irefclickid = hxs.select("//*[@name='selectedTab']/@value").extract()[0]
            selectedTab = hxs.select("//*[@name='passingValues']/@value").extract()[0]
            session_key = hxs.select("//*[@name='session_key']/@value").extract()[0]
            o_num = hxs.select("//*[@name='o_num']/@value").extract()[0]
            data= {'passingValues': passingValues, 'affiliateSubID': affiliateSubID, 'hotelBrand': hotelBrand,
            'irefid':irefid, 'cityName': cityName, 'jsk': jsk, 'numberOfRooms':numberOfRooms, 'searchType':searchType,
            'noDatesSearch': noDatesSearch, 'plf': plf, 'searchHotelName': searchHotelName,
            'starRating':starRating, 'KMode': KMode, 'irefclickid':irefclickid, 'selectedTab': selectedTab,
            'session_key':session_key, 'key': key, 'o_num': o_num}
            request = FormRequest.from_response(response,formname='delayed-form' ,formdata = data,dont_click='true')   
            yield request
            req = Request("http://" + "travela.priceline.com" + "/hotel/searchResults.do?jsk="+jsk,callback=self.intermediate)
            req.meta["city"] = response.request.meta["city"]
            yield req


        def intermediate(self,response):
            hxs = HtmlXPathSelector(response)
            completeListing = hxs.select(".//*[@id='results']/div[4]/a/@href").extract()[0]
            req = Request("http://travela.priceline.com" + completeListing,callback=self.findplhotels)
            req.meta["city"] = response.request.meta["city"]
            yield req


        def findplhotels(self,response):
            hxs=HtmlXPathSelector(response)
            city = response.request.meta["city"]
            if hxs.select("//td[starts-with(@class, 'data')]"):
                for hotels in hxs.select("//td[starts-with(@class, 'data')]"):
                    name =""
                    rating =" / "
                    star =""
                    reviewURL =""
                    temp_name =hotels.select(".//p[1]/span/h3/a/text()")
                    temp_rating=hotels.select(".//p[3]/span/text()")
                    temp_reviewURL=hotels.select(".//p[3]/a/@href")
                    temp_star=hotels.select(".//a[contains(@class, 'def')]/img/@alt")
                    if  temp_name:
                        name = temp_name.extract()[0]
                    if temp_rating:
                        rating = temp_rating.extract()[0]
                    if temp_star:
                        star = temp_star.extract()[0]
                    if temp_reviewURL:
                        reviewURL = temp_reviewURL.extract()[0]
                    c = self.connection.cursor()
                    name = name.replace('&amp;', '')
                    temp_rating = printable(rating.split(' / ')[0])
                    temp_overall = printable(rating.split(' / ')[1])
                    temp_star = printable(star.replace('-Star', ''))
                    if temp_star == '':
                        temp_star = "0.0"
                    if temp_overall == '':
                        temp_overall = "0.0"
                    if temp_rating == '':
                        temp_rating = "0.0"
                    temp_rating = Decimal(temp_rating)
                    temp_overall = Decimal(temp_overall)
                    try:
                        temp_star = Decimal(temp_star)
                    except:
                        temp_star = '0.0'
                    try:
                        self.hotel_count +=1
                        c.execute("INSERT INTO `acuity`.`priceline_hotel_review_overview` \
                        (`Hotel_name`, `Rating`, `Star`, `Overall Rating`, `City`)VALUES('%s', '%s', '%s', '%s', '%s');" \
                        %(re.sub('''(['"])''', r'\\\1',printable(name)),temp_rating,temp_star,temp_overall,printable(city)))
                    except:
                        log.msg("INSERT INTO `acuity`.`priceline_hotel_review_overview` \
                        (`Hotel_name`, `Rating`, `Star`, `Overall Rating`, `City`)VALUES('%s', '%s', '%s', '%s', '%s');"\
                        %(re.sub('''(['"])''', r'\\\1',printable(name)),temp_rating,temp_star,temp_overall,printable(city)), level=log.ERROR)
                    self.connection.commit()
                    if reviewURL !="":
                        req = Request("http://travela.priceline.com%s" % reviewURL, callback = self.findplreviews)
                        req.meta["hotel"] = name
                        req.meta["paging"] = 0
                        yield req
            if hxs.select("//div[contains(@class , 'pagination_block')]"):
                if hxs.select("//img[@src = '/hotel/content/graphics/ht_right_arrow.gif']"):
                    extend_url = hxs.select("//div[contains(@class , 'pagination_block')]//a/@href").extract()[-1]
                    req = Request("http://travela.priceline.com/hotel/%s" % extend_url, callback=self.findplhotels )
                    req.meta["city"] = response.request.meta["city"]
                    yield req

                    
        def findplreviews(self,response):
            hxs=HtmlXPathSelector(response)
            hotel = response.request.meta["hotel"]
            if response.request.meta["paging"] != 1:
                if hxs.select("//div[@id='reviews']//div[@class = 'review']|//div[@class = 'review ']"):
                    scores = [] # 1 = Hotel Cleanliness 2 = Hotel Staff 3 = Location of Hotel 4 = Hotel Dining
                    if hxs.select("//div[@class = 'scores']"):
                        scores = hxs.select("//div[@class = 'scoresright']/div/text()").extract()
                        if len(scores) > 4:
                            scores[1] = Decimal(scores[1])
                            scores[2] = Decimal(scores[2])
                            scores[3] = Decimal(scores[3])
                            scores[4] = Decimal(scores[4])
                            c = self.connection.cursor()
                            try:
                                c.execute("UPDATE `acuity`.`priceline_hotel_review_overview` \
                                SET `Hotel Cleanliness` = '%s' , `Hotel Staff` = '%s' , `Location of Hotel` = '%s' , \
                                `Hotel Dining` = '%s' WHERE `Hotel_name` = '%s' ;" %(scores[1],scores[2],scores[3],scores[4],\
                                re.sub('''(['"])''', r'\\\1',printable(hotel))))
                            except:
                                log.msg("UPDATE `acuity`.`priceline_hotel_review_overview` \
                                SET `Hotel Cleanliness` = '%s' , `Hotel Staff` = '%s' , `Location of Hotel` = '%s' , \
                                `Hotel Dining` = '%s' WHERE `Hotel_name` = '%s' ;" %(scores[1],scores[2],scores[3],scores[4]\
                                ,printable(hotel)), level=log.ERROR)
                            self.connection.commit()
            for reviews in hxs.select("//div[@id='reviews']//div[@class = 'review']|//div[@class = 'review ']"):
                rating = "0.0"
                positiveReview=""
                negativeReview=""
                review=""
                posteddate=""
                reviewer=""
                temp_rating = reviews.select(".//div[3]/text()")
                temp_posteddate= reviews.select(".//div[2]/text()[1]")
                temp_reviewer = reviews.select(".//div[2]/text()[2]")
                temp_positiveReview = reviews.select(".//div[contains(@class,'review_positive')]/text()")
                temp_negativeReview = reviews.select(".//div[contains(@class,'review_negative')]/text()")
                temp_review = reviews.select(".//p/text()")
                    #do stuff for each review
                if temp_posteddate:
                    posteddate=temp_posteddate.extract()[0]
                if temp_reviewer:
                    reviewer=temp_reviewer.extract()[0]
                if temp_rating:
                    rating = temp_rating.extract()[0]
                if temp_positiveReview:
                    positiveReview=temp_positiveReview.extract()[0]
                if temp_negativeReview:
                    negativeReview=temp_negativeReview.extract()[0]
                if temp_review:
                    review = temp_review.extract()[0]
                    if reviews.select(".//*[contains(@id, 'span')]"):
                        review += reviews.select(".//*[contains(@id, 'span')]/text()").extract()[0]
                rating = Decimal(rating)
                c = self.connection.cursor()
                try:
                    self.review_count +=1
                    c.execute("INSERT INTO `priceline_hotel_review_description` (`Hotel_name`, \
                        `Rating`, `PostedDate` ,`Positive_review` , `Negative_review` , `Review` , `Reviewer`  ) \
                        VALUES ('%s','%s', '%s', '%s', '%s', '%s', '%s');" % \
                        (re.sub('''(['"])''', r'\\\1',printable(hotel)),rating,printable(posteddate),re.sub('''(['"])''', r'\\\1', \
                        printable(positiveReview)), re.sub('''(['"])''', r'\\\1',printable(negativeReview)),re.sub('''(['"])''', r'\\\1',\
                        printable(review)), re.sub('''(['"])''', r'\\\1',printable(reviewer)) ))
                    self.connection.commit()
                except:
                    log.msg("INSERT INTO `priceline_hotel_review_description` \
                        (`Hotel_name`, `Rating`, `PostedDate` ,`Positive_review` , `Negative_review` , \
                        `Review` , `Reviewer`  ) VALUES ('%s','%s', '%s', '%s', '%s', '%s', '%s');" % \
                        (printable(hotel),Decimal(rating),printable(posteddate), printable(positiveReview), printable(negativeReview),\
                        printable(review), printable(reviewer)),level=log.ERROR)
            if hxs.select("//div[contains(@class, 'review_paganation_right')]"):
                if hxs.select("//div[contains(@class, 'review_paganation_right')]/b/a"):
                    for links in hxs.select("//div[contains(@class, 'review_paganation_right')]/b/a"):
                        if links.select("./text()"):
                            linkText=links.select("./text()").extract()[0]
                            url = links.select("./@href").extract()[0]
                            if linkText.find("next") != -1:
                                req = Request("http://travela.priceline.com%s" % url,callback=self.findplreviews)
                                req.meta["hotel"] = hotel
                                req.meta["paging"] = 1
                                yield req


def main():
        log.start(logfile="PriceLine_review_spider_log.txt")
        settings.overrides['USER_AGENT'] = "Mozilla/4.0 (compatible;MSIE 7.0;Windows NT 6.0)"
        settings.overrides['SCHEDULER_ORDER'] = 'BFO'
        crawler = CrawlerProcess(settings)
        crawler.install()
        crawler.configure()
        spider = PLReviewSpider()
        db = Connection.database
        c = Connection.cursor
        c.execute("CREATE TABLE IF NOT EXISTS `priceline_hotel_review_overview` \
        (`Hotel_name` text,`Rating` float DEFAULT NULL,`Star` float DEFAULT NULL,`Overall Rating`\
        float DEFAULT NULL,`City` text,`Hotel Cleanliness` float DEFAULT NULL,`Hotel Staff` float \
        DEFAULT NULL,`Location of Hotel` float DEFAULT NULL,`Hotel Dining` float DEFAULT NULL,`NumberOfReviews` \
        int(11) DEFAULT NULL) ENGINE=InnoDB DEFAULT CHARSET=utf8")
        c.execute("CREATE TABLE IF NOT EXISTS `priceline_hotel_review_description` \
        (`Hotel_name` text,`Rating` float DEFAULT NULL,`PostedDate` text,`Positive_review` text,\
        `Negative_review` text,`Review` text,`Reviewer` text) ENGINE=InnoDB DEFAULT CHARSET=utf8")
        db.commit()
        cities = ['New York, New York','Los Angeles, California','Chicago, Illinois','Houston, Texas','Philadelphia, Pennsylvania',
        'Phoenix, Arizona','San Diego, California','Dallas, Texas','San Antonio, Texas','Detroit, Michigan','San Jose, California',
        'Indianapolis, Indiana','San Francisco, California','Jacksonville, Florida','Columbus, Ohio','Austin, Texas','Memphis, Tennessee',
        'Baltimore, Maryland','Milwaukee, Wisconsin','Boston, Massachusetts','Charlotte, North Carolina','El Paso, Texas','Washington, D.C.',
        'Seattle, Washington','Fort Worth, Texas','Denver, Colorado','Nashville, Tennessee','Portland, Oregon','Oklahoma City, Oklahoma',
        'Las Vegas, Nevada','Toronto','Ottawa, ON Canada','Vancouver, BC Canada','Calgary, AB Canada']
        spider.connection = Connection.database
        spider.input = cities
        crawler.queue.append_spider(spider)
        log.msg("Spidering PriceLine ...",level=log.INFO)
        crawler.start()
        #print "Spidering Ended with "+ spider.hotel_count +" Hotel Inputs and "+spider.review_count+" review counts from Priceline.com"
        log.msg("Calculating Number of reviews...",level=log.INFO)
        db = Connection.database
        c = Connection.cursor
        c.execute("select hotel_name from priceline_hotel_review_overview")
        for hotel in c.fetchall():
            c.execute("SELECT COUNT(*) FROM priceline_hotel_review_description WHERE hotel_name = '%s'" % re.sub('''(['"])''', r'\\\1',hotel[0]))
            numreview = c.fetchall()
            for number in numreview:
                c.execute("UPDATE `acuity`.`priceline_hotel_review_overview` SET `NumberOfReviews` = '%s' WHERE \
                `Hotel_name` = '%s';" % (number[0],re.sub('''(['"])''', r'\\\1',hotel[0]) ))
                db.commit()
        log.msg("COMPLETED!",level=log.INFO)
        Connection.database.close()

if __name__ == '__main__':
        main()

