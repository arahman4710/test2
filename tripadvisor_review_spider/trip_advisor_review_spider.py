from decimal import *
from scrapy.selector import HtmlXPathSelector
from scrapy.http import FormRequest
from scrapy.conf import settings
from scrapy.crawler import CrawlerProcess
from scrapy.spider import BaseSpider
from scrapy import signals,log
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

def parse_xpath(selector,xpath):
    temp = selector.select(xpath)
    if temp:
        return temp.extract()
    else:
        return None

class Connection():
	database = MySQLdb.connect(user='root', passwd='areek', db='acuity')
	cursor = database.cursor()

class Travel_advisor_review_spider(BaseSpider):
        name = "Travel_advisor_review_spider"
        start_urls = ["http://www.tripadvisor.com/"];
        allowed_domains = ["tripadvisor.com"];
        input = []
        hotel_count=0
        review_count = 0
        ameneties= {}

        def parse(self, response):


            for input in self.input:
                req = FormRequest.from_response(response,formname='HAC_FORM' ,formdata = {'q':input },callback=self.Hotel_Page)
                req.meta["city"] = input
                yield req

        def Hotel_Page(self,response):
            hxs = HtmlXPathSelector(response)
            city = response.request.meta["city"]
            hotels = hxs.select(".//div[contains(@id,'hotel_')]")
            if hotels:
                for hotel in hotels:
                    insert_sql = "INSERT INTO `acuity`.`tripadvisor_hotel_review_overview` "
                    param_sql = "("
                    value_sql = "VALUES("
                    temp_hotelid = hotel.select(".//@id")
                    temp_hotelurl = hotel.select(".//div[contains(@class, 'title')]/a/@href")
                    temp_hotelname = hotel.select(".//div[contains(@class, 'title')]/a/text()")
                    temp_hotelstar = hotel.select(".//div[contains(@class, 'title')]/span/img/@alt")
                    temp_ameneties = hotel.select(".//div[contains(@class, 'amenities')]/var/@title")
                    hotelurl=''
                    hotelameneties=[]
                    hotelstar=''
                    hotelname=''
                    hotelid=''
                    if temp_hotelid:
                        hotelid = temp_hotelid.extract()[0].replace("hotel_","")
                        param_sql +="`Hotel_id`,"
                        value_sql +="'"+ hotelid +"',"
                        param_sql +="`City`,"
                        value_sql +="'"+ re.sub('''(['"])''', r'\\\1',city) +"',"
                    if temp_hotelname:
                        hotelname = printable(temp_hotelname.extract()[0].strip().replace("&amp;",""))
                        param_sql +="`Hotel_name`,"
                        value_sql +="'"+ re.sub('''(['"])''', r'\\\1',hotelname) +"',"
                    if temp_hotelurl:
                        hotelurl = "http://www.tripadvisor.com" + temp_hotelurl.extract()[0]
                        param_sql +="`Hotel_url`,"
                        value_sql +="'"+ re.sub('''(['"])''', r'\\\1', printable(hotelurl)) +"',"
                    if temp_hotelstar:
                        hotelstar = temp_hotelstar.extract()[0].strip().replace(" of 5","")
                        param_sql +="`Hotel_star`,"
                        value_sql +="'"+ hotelstar +"',"
                    param_sql =  param_sql[0:-1] + ")"
                    value_sql = value_sql[0:-1] + ");"
                    try:
                        Connection.cursor.execute(insert_sql + param_sql + value_sql)
                        Connection.database.commit()
                    except:
                        log.msg(insert_sql + param_sql + value_sql,level=log.ERROR)

                    if temp_ameneties:
                        hotelameneties = temp_ameneties.extract()
                        for amenety in hotelameneties:
                            if amenety in self.ameneties:
                                value =  self.ameneties[amenety]
                                Connection.cursor.execute("INSERT INTO `acuity`.`tripadvisor_amenity_hotel` \
                                (`Hotel_id`, `Amenity_id` ) VALUES ('"+str(hotelid) +"', '"+ str(value) +"');")
                                Connection.database.commit()
                                #update intermediate table
                            else:
                                Connection.cursor.execute("select * from amenities")
                                new_id = len(Connection.cursor.fetchall()) + 1
                                Connection.cursor.execute("INSERT INTO `acuity`.`amenities` \
                                ( `AmenityId` ,`AmenityName` ) VALUES ('"+str(new_id)+"' , '"+amenety+"');")
                                Connection.database.commit()
                                self.ameneties[amenety] = new_id
                                Connection.cursor.execute("INSERT INTO `acuity`.`tripadvisor_amenity_hotel` \
                                (`Hotel_id`, `Amenity_id` ) VALUES ('"+str(hotelid) +"', '"+str(self.ameneties[amenety]) +"');")
                                Connection.database.commit()

                    if temp_hotelurl:
                        hotelurl = hotelurl.replace("Hotel_Review", "ShowUserReviews")
                        review_req = Request(hotelurl,callback=self.review_page)
                        review_req.meta["paging"] = 0
                        review_req.meta["hotel"] = hotelid
                        yield review_req
            next_page = hxs.select(".//a[contains(@class, 'guiArw sprite-pageNext js_HACpager')]/@href")
            if next_page:
                req = Request("http://www.tripadvisor.com%s" % next_page.extract()[0],callback=self.Hotel_Page)
                req.meta["city"] =city
                yield req

        def review_page(self,response):
            hxs = HtmlXPathSelector(response)
            hotel = response.request.meta["hotel"]
            if response.request.meta["paging"] == 0:
                update_sql = "UPDATE `acuity`.`tripadvisor_hotel_review_overview` SET "
                temp_hotel_popularity = hxs.select(".//div[@class = 'rs popularity ']|.//div[@class = 'rs popularity']")
                temp_hotel_popularity2 = hxs.select(".//div[@class = 'rs popularity additional ']|.//div[@class = 'rs popularity additional']")
                temp_hotel_rating = hxs.select(".//div[contains(@id , 'TAB_RATING')]/div[1]/span[1]/img/@alt")
                temp_hotel_recommended = hxs.select(".//div[contains(@id , 'TAB_RATING')]/div[contains(@class, 'wrpReviewGraph')]/var[contains(@class, 'recommended' )]")
                temp_street_ad = hxs.select(".//address/span[contains( @class ,'street-address')]/text()")
                temp_postal_code = hxs.select(".//address/span[contains( @class ,'locality')]/span[contains( @property ,'postal-code')]/text()")
                hotel_recommended=""
                hotel_rating = ""
                hotel_popularity = ""
                hotel_popularity2=""
                street_ad = ""
                postal_code = ""
                if temp_street_ad:
                    street_ad = temp_street_ad.extract()[0].strip()
                    update_sql += "`Address` = '"+re.sub('''(['"])''', r'\\\1',printable(street_ad))+"' ,"
                if temp_postal_code:
                    postal_code = temp_postal_code.extract()[0].strip()
                    update_sql += "`Postal_code` = '"+postal_code+"' ,"
                if temp_hotel_recommended:
                    hotel_recommended = temp_hotel_recommended.select(".//span/text()").extract()[0] 
                    update_sql += "`Hotel_recommendation_percentage` = '"+hotel_recommended+"' ,"
                if temp_hotel_popularity:
                    hotel_popularity = temp_hotel_popularity.select(".//var/b/text()").extract()[0] + ' '
                    hotel_popularity += temp_hotel_popularity.select(".//span/text()").extract()[0]
                    hotel_popularity += temp_hotel_popularity.select(".//span/i/a/text()").extract()[0]
                    update_sql += "`Hotel_popularity_overall` = '"+hotel_popularity+"' ,"
                if temp_hotel_popularity2:
                    hotel_popularity2 =  temp_hotel_popularity2.select(".//span/span/text()").extract()[0]+ ' '
                    hotel_popularity2 += temp_hotel_popularity2.select(".//span/b/text()").extract()[0]+ ' '
                    hotel_popularity2 += temp_hotel_popularity2.select(".//span/i/text()").extract()[0]
                    hotel_popularity2 += temp_hotel_popularity2.select(".//span/i/a/text()").extract()[0]
                    update_sql += "`Hotel_popularity_specific` = '"+hotel_popularity2+"' ,"
                if temp_hotel_rating:
                    hotel_rating = temp_hotel_rating.extract()[0]
                    update_sql += "`Hotel_rating` = '"+hotel_rating.replace(" of 5 stars", "")+"' ,"
                update_sql = update_sql[0:-1] + " WHERE `Hotel_id` = '"+str(hotel)+"';"
                try:
                    Connection.cursor.execute(update_sql)
                    Connection.database.commit()
                except:
                    log.msg(update_sql,level=log.ERROR)

            #above should be under another condition paging or not condition
            temp_reviews = hxs.select(".//div[contains(@id, 'UR')]")
            if temp_reviews:
                for review in temp_reviews:
                    insert_sql = "INSERT INTO `acuity`.`tripadvisor_hotel_review_description` "
                    insert_param_sql = "( "
                    insert_value_sql = "VALUES ( "
                    temp_id=review.select(".//@id")
                    temp_title = review.select(".//div[contains(@class, 'quote')]/text()")
                    temp_rating = review.select(".//div[contains(@class, 'rating')]/span/img/@alt")
                    temp_review = review.select(".//div[contains(@class , 'entry')]/p/text()")
                    temp_postedDate = review.select(".//div[contains(@class , 'date new')]/text()[1]|.//div[contains(@class , 'date ')]/text()[1]")
                    temp_reviewer_location = review.select(".//div[contains(@class, 'location')]/text()[1]")
                    temp_triptype = review.select(".//div[contains(@class , 'date new')]/span/text()|.//div[contains(@class , 'date ')]/span/text()")
                    temp_rating_listing = review.select(".//div[contains(@class , 'rating-list')]/ul/li/ul/li")
                    temp_stay_info = review.select(".//ul[contains(@class , 'stayNfo')]/li")
                    review_posted_date=""
                    reviewer_location = ""
                    review_id=""
                    review_title =""
                    review_content = ""
                    review_rating=""
                    review_triptype=""
                    review_stay_info = []
                    review_rating_listing = []
                    if temp_rating:
                        review_rating = temp_rating.extract()[0]
                        insert_param_sql +="`Review_rating`,"
                        insert_value_sql +="'"+ str(review_rating.replace(" of 5 stars","")) +"',"
                    if temp_id:
                        review_id = temp_id.extract()[0].replace("UR","")
                        insert_param_sql +="`Review_id`,"
                        insert_value_sql +="'"+ str(review_id) +"',"
                        review_url =  response.url[:response.url.find("-r")] + "-r"+ review_id + response.url[response.url.find("-",response.url.find("-r")+2):]
                        insert_param_sql +="`Review_url`,"
                        insert_value_sql +="'"+ re.sub('''(['"])''', r'\\\1',printable(review_url)) +"',"
                    if temp_title:
                        review_title = temp_title.extract()[0]
                        insert_param_sql +="`Review_title`,"
                        insert_value_sql +="'"+ re.sub('''(['"])''', r'\\\1',printable(review_title.strip())) +"',"
                    if temp_review:
                        review_content =temp_review.extract()[0]
                        insert_param_sql +="`Review_content`,"
                        insert_value_sql +="'"+ re.sub('''(['"])''', r'\\\1',printable(review_content.strip())) +"',"
                    if temp_reviewer_location:
                        reviewer_location = temp_reviewer_location.extract()[0]
                        insert_param_sql +="`Reviewer_location`,"
                        insert_value_sql +="'"+ re.sub('''(['"])''', r'\\\1',printable(reviewer_location.strip())) +"',"
                    if temp_postedDate:
                        review_posted_date = temp_postedDate.extract()[0].replace("|","")
                        insert_param_sql +="`Posted_date`,"
                        insert_value_sql +="'"+ re.sub('''(['"])''', r'\\\1',printable(review_posted_date.strip())) +"',"
                    if temp_triptype:
                        review_triptype = temp_triptype.extract()[0].replace("Trip type:","")
                        insert_param_sql +="`Reviewer_TripType`,"
                        insert_value_sql +="'"+ re.sub('''(['"])''', r'\\\1',printable(review_triptype.strip())) +"',"
                    insert_param_sql +="`Hotel_id`,"
                    insert_value_sql +="'"+ str(hotel) +"',"
                    
                    
                    if temp_rating_listing:
                        rating_info =""
                        for urating in temp_rating_listing:
                            review_rating_listing.append([urating.select(".//span/img/@alt").extract()[0].replace(" of 5 stars","").strip(),\
                            urating.select(".//text()[2]").extract()[0].strip()])
                            rating_info +=urating.select(".//text()[2]").extract()[0].strip()+' : '+ \
                            urating.select(".//span/img/@alt").extract()[0].replace(" of 5 stars","").strip() + ", "
                        insert_param_sql +="`User_rating`,"
                        insert_value_sql +="'"+ re.sub('''(['"])''', r'\\\1',printable(rating_info.strip())) +"',"
                    if temp_stay_info:
                        user_info=""
                        for info in temp_stay_info:
                            review_stay_info.append([info.select(".//b/text()").extract()[0].strip(),info.select("./text()").extract()[0].strip()])
                            user_info += info.select(".//b/text()").extract()[0].strip() +" : " +info.select("./text()").extract()[0].strip()+ ", "
                        insert_param_sql +="`User_information`,"
                        insert_value_sql +="'"+ re.sub('''(['"])''', r'\\\1',printable(user_info.strip())) +"',"
                    insert_param_sql =  insert_param_sql[0:-1] + ")"
                    insert_value_sql = insert_value_sql[0:-1] + ");"
                    try:
                        Connection.cursor.execute(insert_sql + insert_param_sql + insert_value_sql)
                        Connection.database.commit()
                    except:
                        log.msg(insert_sql + insert_param_sql + insert_value_sql,level=log.ERROR)
            next_page = hxs.select(".//a[contains(@class, 'guiArw sprite-pageNext')]/@href")
            if next_page:
                next_url = next_page.extract()[0]
                review_req = Request("http://www.tripadvisor.com%s" % next_url,callback=self.review_page)
                review_req.meta["paging"] = 1
                review_req.meta["hotel"] = hotel
                yield review_req



def main():
        log.start(logfile="TripAdvisor_review_spider_log.txt")
        settings.overrides['USER_AGENT'] = "Mozilla/4.0 (compatible;MSIE 7.0;Windows NT 6.0)"
        settings.overrides['SCHEDULER_ORDER'] = 'BFO'
        Connection.cursor.execute("CREATE TABLE IF NOT EXISTS `tripadvisor_hotel_review_overview` \
        (`Hotel_id` INT(11) DEFAULT NULL,`Hotel_name` TEXT,`Hotel_star` FLOAT DEFAULT NULL,`Hotel_url` TEXT,\
        `Hotel_recommendation_percentage` FLOAT DEFAULT NULL,`Hotel_popularity_overall` TEXT,`Hotel_popularity_specific` TEXT, \
        `Hotel_rating` FLOAT DEFAULT NULL, `NumberOfReview` int(11) DEFAULT NULL,`City` text,`Address` text,`Postal_code` text,\
        `internal_hotelid` int(11) DEFAULT NULL,  PRIMARY KEY (`Hotel_id`),KEY `FK_tripadvisor_hotel_review_overview` (`internal_hotelid`)\
        ,CONSTRAINT `FK_tripadvisor_hotel_review_overview` FOREIGN KEY (`internal_hotelid`) REFERENCES `hotels` (`HotelId`)) ENGINE=INNODB DEFAULT CHARSET=utf8")
        Connection.database.commit()
        Connection.cursor.execute("CREATE TABLE IF NOT EXISTS`tripadvisor_hotel_review_description`\
        (`Review_id` INT(11) DEFAULT NULL,`Review_title` TEXT,`Review_rating` FLOAT DEFAULT NULL,\
        `Posted_date` TEXT,`Review_content` TEXT,`Reviewer_TripType` TEXT,`Reviewer_location` TEXT,\
        `Hotel_id` int(11) NOT NULL, `Review_url` text, `User_rating` text,`User_information` text, \
        PRIMARY KEY (`Review_id`),KEY `FK_tripadvisor_hotel_review_description` (`Hotel_id`),\
        CONSTRAINT `FK_tripadvisor_hotel_review_description` FOREIGN KEY (`Hotel_id`) \
        REFERENCES `tripadvisor_hotel_review_overview` (`Hotel_id`)) \
        ENGINE=INNODB DEFAULT CHARSET=utf8")
        Connection.database.commit()
        Connection.cursor.execute("CREATE TABLE IF NOT EXISTS `amenities` \
        (`AmenityId` INT(11) NOT NULL AUTO_INCREMENT,`AmenityName` VARCHAR(45) NOT NULL,\
        PRIMARY KEY (`AmenityId`)) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8")
        Connection.database.commit()
        Connection.cursor.execute("CREATE TABLE IF NOT EXISTS `tripadvisor_amenity_hotel` \
        (`Hotel_id` INT(11) DEFAULT NULL,`Amenity_id` INT(11) DEFAULT NULL,\
        KEY `FK_tripadvisor_amenity_hotel` (`Hotel_id`),KEY `FK_tripadvisor_amenity_amenity` \
        (`Amenity_id`),CONSTRAINT `FK_tripadvisor_amenity_amenity` FOREIGN KEY (`Amenity_id`) \
        REFERENCES `amenities` (`AmenityId`),CONSTRAINT `FK_tripadvisor_amenity_hotel` FOREIGN KEY (`Hotel_id`)\
        REFERENCES `tripadvisor_hotel_review_overview` (`Hotel_id`)) ENGINE=INNODB DEFAULT CHARSET=utf8")
        Connection.database.commit()
        Connection.cursor.execute("select * from amenities")
        current_amenities = {}
        for amenity in Connection.cursor.fetchall():
            current_amenities[amenity[1]] = amenity[0]
        Connection.cursor.execute("CREATE TABLE IF NOT EXISTS `tripadvisor_amenity_hotel` \
        (`Hotel_id` INT(11) DEFAULT NULL,`Amenity_id` INT(11) DEFAULT NULL) ENGINE=INNODB DEFAULT CHARSET=utf8")
        Connection.database.commit()
        crawler = CrawlerProcess(settings)
        crawler.install()
        crawler.configure()
        spider = Travel_advisor_review_spider()
        spider.input =['Bloomington, Minnesota, USA']#['Houston, Texas, USA']

        actual_in =['New York, New York','Los Angeles, California','Chicago, Illinois','Houston, Texas','Philadelphia, Pennsylvania',
        'Phoenix, Arizona','San Diego, California','Dallas, Texas','San Antonio, Texas','Detroit, Michigan','San Jose, California',
        'Indianapolis, Indiana','San Francisco, California','Jacksonville, Florida','Columbus, Ohio','Austin, Texas','Memphis, Tennessee',
        'Baltimore, Maryland','Milwaukee, Wisconsin','Boston, Massachusetts','Charlotte, North Carolina','El Paso, Texas','Washington, D.C.',
        'Seattle, Washington','Fort Worth, Texas','Denver, Colorado','Nashville, Tennessee','Portland, Oregon','Oklahoma City, Oklahoma',
        'Las Vegas, Nevada','Toronto','Ottawa, ON Canada','Vancouver, BC Canada','Calgary, AB Canada']
        spider.ameneties = current_amenities
        crawler.queue.append_spider(spider)
        crawler.start()
        log.msg("Calculating Number of reviews...",level=log.INFO)
        db = Connection.database
        c = Connection.cursor
        c.execute("select Hotel_id from tripadvisor_hotel_review_overview")
        for hotel in c.fetchall():
            c.execute("SELECT COUNT(*) FROM tripadvisor_hotel_review_description WHERE Hotel_id = '%s'" % hotel[0])
            numreview = c.fetchall()
            for number in numreview:
                c.execute("UPDATE `acuity`.`tripadvisor_hotel_review_overview` SET `NumberOfReview` = '%s' WHERE \
                `Hotel_id` = '%s';" % (number[0],hotel[0]) )
                db.commit()
        log.msg("COMPLETED!",level=log.INFO)
        Connection.database.close()
        
if __name__ == '__main__':
        main()

