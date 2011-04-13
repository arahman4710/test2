import kayak_spider
from decimal import *

'''
first get the subset from tripadvisor table by hotel_star, tripadvisor_rating
and amenities listing

match tripadvisor with hotels

get the region and point testing

refine the list
'''

from tripadvisor_hotel_comparer import *
from kayak_spider import *
from ray_casting import *
import Levenshtein
from scrapy.selector import HtmlXPathSelector,XmlXPathSelector
from scrapy.http import FormRequest
from scrapy.conf import settings
from scrapy.crawler import CrawlerProcess
from scrapy.spider import BaseSpider
from scrapy import signals,log,project
from scrapy.xlib.pydispatch import dispatcher
from scrapy.http import Request
from scrapy.contrib.spiders import XMLFeedSpider
from multiprocessing import Process, Queue
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

def parse_xpath(selector,xpath):
    temp = selector.select(xpath)
    if temp:
        return temp.extract()
    else:
        return None



class Connection():
	database = MySQLdb.connect(user='root', passwd='areek', db='acuity')
	cursor = database.cursor()

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
		doc = response.body
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
                                else:
                                    price =div.select(".//span[contains(@id,'priceAnchor')]/a/text()")
                                    print id
                                    if int(id) in self.query_price:
                                        self.price_results[id] =price[0].extract()
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




class hotwire_hotel_comparer(BaseSpider):
        name = "Hotwire_hotel_comparer"
        #download_delay = 0.5
        allowed_domains = ["hotwire.com"];
        input = []
        hotel_count=0
        review_count = 0
        original_amenties={}
        meta_regions = {}
        meta_amineties = {}
        hotel_results={}
        city_name ='Houston, Texas, USA'
        api_key='eupzwn43dwtmgxhmkw5pbta7'
        region_name={}
        start_date =str(date.today().strftime('%m/%d/20%y'))
        end_date = str(date.today().replace(day=date.today().day + 1).strftime('%m/%d/20%y'))
        log_file = open('res/hotwire_hotel'+".csv",'w')#+str(date.today())+"_"+str(time.strftime('%H-%M'))
        start_urls = ["http://api.hotwire.com"+"/v1/search/hotel?apikey="+api_key+"&dest="+city_name+"&rooms=1&adults=2&children=0&startdate="+start_date+"&enddate="+end_date];

        def parse(self, response):
            #yield Request("http://www.hotwire.com/hotel/deeplink-details.jsp?actionType=303NTY2MTg3NjU2Mzo5MzIzNjkwOTA2OA--588086261045.0014.7859.78SRFCPOREBCLFHS01%2F01%2F201101%2F02%2F201113300H145.0013.5USD&resultId=NTY2MTg3NjU2Mzo5MzIzNjkwOTA2OA--&inputId=api-results",\
#            callback=self.hotel_page)
            print response.url
            hxs = XmlXPathSelector(response)
            temp_regions = []
            hotel_list = []
            region_url=''
            regions={}
            amineties={}
            region_url= hxs.select("//Hotwire/Result/HotelResult[1]/DeepLink/text()").extract()[0]
            #print region_url
            temp_regions = hxs.select("//Hotwire/MetaData/HotelMetaData/Neighborhoods/Neighborhood")
            temp_amineties = hxs.select("//Hotwire/MetaData/HotelMetaData/Amenities/Amenity")
            hotel_list = hxs.select("//Hotwire/Result/HotelResult")


            if temp_amineties:
                for ami in temp_amineties:
                    code = ami.select(".//Code/text()").extract()[0]
                    ami_name = str(ami.select(".//Name/text()").extract()[0]).strip().lower()
                    if ami_name in self.original_amenties.keys():
                        amineties[code]=self.original_amenties[ami_name]    #if direct amenties match save our amenity id in the val of their aminety code
                    else:
                        if ami_name.replace("(s)","") in self.original_amenties.keys(): #stips out plurals
                            amineties[code]=self.original_amenties[ami_name.replace("(s)","")]
                        else:
                            if ami_name =='pool(s)':
                                amineties[code] = self.original_amenties['swimming pool']
                            else:
                               # print ami_name
                           #     if ami_name.find("high-speed internet")!=-1:
                           #         amineties[code] = self.original_amenties['free high-speed internet']
                           #     else:
                                amineties[code] = "Null"
                self.meta_amineties = amineties
                print amineties
            '''
            working with regions
            '''
            if temp_regions:
                for reg in temp_regions:
                    latlngs=reg.select(".//Shape/LatLong/text()").extract()
                    region_name=reg.select(".//Name/text()").extract()[0].strip()
                    region_id=float(reg.select(".//Id/text()").extract()[0].strip())
                    #print region_name
                    point_latlng =[]
                    temp_edges = []
                    for latlng in latlngs:
                        cordins = latlng.split(',')
                        lat = float(cordins[0])
                        lng = float(cordins[1])
                        point_latlng.append(Pt(x=lat, y=lng))
                    for i in range(len(point_latlng)-1):
                        temp_edges.append(Edge(a=point_latlng[i], b=point_latlng[i+1]))
                    self.region_name[region_id]=region_name
                    regions[float(region_id)]= Poly(name= region_name, edges=temp_edges)

                self.meta_regions = regions

            if hotel_list:
                for hotel in hotel_list:
                    temp_star=hotel.select(".//StarRating/text()").extract()[0]
                    hotel_region=hotel.select(".//NeighborhoodId/text()").extract()[0]
                    hotel_ami_list = hotel.select(".//AmenityCodes/Code/text()")
                    deep_link = hotel.select(".//DeepLink/text()").extract()[0].replace("&amp;","&")
                    result_id = hotel.select(".//ResultId/text()").extract()[0]
                    avg_price = hotel.select(".//AveragePricePerNight/text()").extract()[0]
                    tot_price = hotel.select(".//TotalPrice/text()").extract()[0]
                   # print "before: "+deep_link+result_id
                    reqq= Request(deep_link+result_id,callback=self.hotel_page)
                    
                    #yield reqq
                    ami_list=[]
                    if hotel_ami_list:
                        aami_list = hotel_ami_list.extract()
                        for hotel_ami in aami_list:
                            '''
                            if s_temp_ls:
                                temp_ls = s_temp_ls.extract()[0]    #store amenity codes
                           # print "   "+temp_ls
                           '''
                            if amineties[hotel_ami] != 'Null':
                                ami_list.append(hotel_ami)
                        #print deep_link
                        #print hotel_ami_list.extract()
                        #print ami_list
                        reqq.meta["ami_list"] = ami_list
                        reqq.meta["avg_price"] = avg_price
                        reqq.meta["tot_price"] = tot_price
                        reqq.meta["hotel_star"] = temp_star
                        reqq.meta["neighbourhood"] = hotel_region.strip()
                        reqq.meta["region_name"] = self.region_name[float(hotel_region.strip())]
                        yield reqq
                        #if amineties[hotel_ami.select(".//Code/text()").extract()[0]] != 'Null':
                    '''
(SELECT hotels.hotelid,hotels.hotelname,hotels.Latitude,hotels.Longitude FROM hotels LEFT JOIN
tripadvisor_hotel_review_overview ON tripadvisor_hotel_review_overview.internal_hotelid = hotels.hotelid
JOIN tripadvisor_amenity_hotel
ON tripadvisor_hotel_review_overview.Hotel_id = tripadvisor_amenity_hotel.hotel_id
JOIN amenities ON amenities.AmenityId=tripadvisor_amenity_hotel.Amenity_id
WHERE
tripadvisor_hotel_review_overview.Hotel_rating =3.5
AND
amenities.AmenityId IN (2,5,6,3,1)
AND
tripadvisor_hotel_review_overview.Hotel_star >= 3
AND
tripadvisor_hotel_review_overview.Hotel_star <= 4
GROUP BY tripadvisor_hotel_review_overview.hotel_id
HAVING COUNT(*) = 5
)
                    '''


            



            #yield Request(region_url,callback=self.hotel_page)
           # for input in self.input:
           #     req = FormRequest.from_response(response,formname='HAC_FORM' ,formdata = {'q':input },callback=self.Hotel_Page)
           #     req.meta["city"] = input
           #     yield req
        def hotel_page(self,response):
            tripadvisor_rating =''
            if response.body:
                hxs = HtmlXPathSelector(response)
                temp_tripadvisor_rating =hxs.select(".//div[@class ='tripAdvisor']/strong/text()|.//*[@id='areaInf']/div[1]/div[2]/strong/text()")
                if temp_tripadvisor_rating:
                    tripadvisor_rating = temp_tripadvisor_rating.extract()[0].replace(" out of 5.0","").replace(" out of 5","")
            
            print response.url
            #print response.body
            hotel_star = response.request.meta["hotel_star"]
            hotel_a_list = response.request.meta["ami_list"]
            hotel_avg_price = response.request.meta["avg_price"]
            hotel_tot_price = response.request.meta["tot_price"]
            hotel_region_code =  float(response.request.meta["neighbourhood"])
            print hotel_star
            print hotel_a_list
            print tripadvisor_rating
            display = 'Region Name: '+ response.request.meta["region_name"].replace(","," ")+','+' Avg Price: '+hotel_avg_price+','+' Total Price: '+hotel_tot_price+','
            selec_sql = "SELECT DISTINCT hotels.hotelid,hotels.hotelname,hotels.Latitude,hotels.Longitude,CASE tripadvisor_hotel_review_overview.hotel_star WHEN NULL THEN hotels.Rating \
            ELSE tripadvisor_hotel_review_overview.hotel_star END FROM hotels LEFT JOIN \
            tripadvisor_hotel_review_overview ON tripadvisor_hotel_review_overview.internal_hotelid = hotels.hotelid \
            JOIN tripadvisor_amenity_hotel ON tripadvisor_hotel_review_overview.Hotel_id = tripadvisor_amenity_hotel.hotel_id\
            JOIN amenities ON amenities.AmenityId=tripadvisor_amenity_hotel.Amenity_id WHERE tripadvisor_hotel_review_overview.city like '%"+self.city_name+"%' AND "
            condition_sql = ""
            group_sql = ""
            if tripadvisor_rating and not (tripadvisor_rating=='0.0'):
                display+='Tripadvisor rating: '+tripadvisor_rating+','
                condition_sql+="tripadvisor_hotel_review_overview.Hotel_rating = "+tripadvisor_rating+" AND "
            if hotel_a_list:
                display+="Amenities: "
                a_s =""
                group_sql = "GROUP BY tripadvisor_hotel_review_overview.hotel_id HAVING COUNT(*) = "+str(len(hotel_a_list))
                for hotel_a in hotel_a_list:
                    display+=hotel_a+','
                    a_s+=str(self.meta_amineties[hotel_a])+','
                condition_sql+="amenities.AmenityId IN ("+a_s[:-1]+") AND "
        
            if hotel_star:
                display += "Hotel Star: "+str(hotel_star)+','
                #(CASE tripadvisor_hotel_review_overview.hotel_star WHEN NULL THEN hotels.Rating ELSE tripadvisor_hotel_review_overview.hotel_star END )
                condition_sql+="(CASE tripadvisor_hotel_review_overview.hotel_star WHEN NULL THEN hotels.Rating ELSE tripadvisor_hotel_review_overview.hotel_star END ) >= "+str(float(hotel_star)-0.5)+" \
                AND (CASE tripadvisor_hotel_review_overview.hotel_star WHEN NULL THEN hotels.Rating ELSE tripadvisor_hotel_review_overview.hotel_star END ) <= "+str(float(hotel_star)+0.5)+" AND "
        
            if condition_sql:
                selec_sql += condition_sql[:-4]
                if group_sql:
                    selec_sql+=group_sql
            else:
                selec_sql = selec_sql[:-4]
            print selec_sql
            Connection.cursor.execute(selec_sql)
            hotel_list = Connection.cursor.fetchall()
            #print self.meta_regions.keys()
            #print hotel_region_code
            self.log_file.write(display+'\n')
            #self.hotel_results[self.meta_regions[hotel_region_code]+'|'+hotel_star]={}
            h_lst={}
            for hotel in hotel_list:
                #var_lat = [hotel[2],hotel[2]+0.1,hotel[2]-0.1]
                #var_lng = [hotel[3],hotel[3]+0.1,hotel[3]-0.1]
                #print self.meta_regions.keys()
                #done = 0
                #for lat in var_lat:
                #    for lng in var_lng:
                if ispointinside(Pt(x=hotel[2], y=hotel[3]), self.meta_regions[hotel_region_code]):
                    self.log_file.write(','+hotel[1].replace(","," ")+','+hotel[4]+',\n')
                    h_lst[hotel[0]] = hotel[1:]
            self.hotel_results[self.region_name[hotel_region_code]+'|'+hotel_star] = h_lst

              #'select * from kayakhotels where hotels_hotelid in '+str(map(str,hotel_id)).replace('[','(').replace(']',')')
              #              done =1
              #              break
              #      if done:
              #          break

def qurey_price_kayak(kayak_id,crawler):
    '''
    settings.overrides['USER_AGENT'] = "Mozilla/5.0 (Windows; U; Windows NT 6.0; en-US) AppleWebKit/534.10 (KHTML, like Gecko) Chrome/8.0.552.224 Safari/534.10"
    settings.overrides['SCHEDULER_ORDER'] = 'BFO'
    crawler = CrawlerProcess(settings)
    crawler.install()
    crawler.configure()
    '''
    spider=KayakSpider()
    spider.selec_city=['Houston,TX']
    spider.query_price=kayak_id
    crawler.queue.append_spider(spider)
    for id in kayak_id:
        print '     '+str(id)
    crawler.start()
    print "saaa"
    return spider.price_results

def run_price_query(kayak_id,crawler):
    return qurey_price_kayak(kayak_id,crawler)

@print_timing
def main():
        log.start(logfile="hotwire_hotel_comparer.txt")
        settings.overrides['USER_AGENT'] = "Mozilla/5.0 (Windows; U; Windows NT 6.0; en-US) AppleWebKit/534.10 (KHTML, like Gecko) Chrome/8.0.552.224 Safari/534.10"
        settings.overrides['SCHEDULER_ORDER'] = 'BFO'
        crawler = CrawlerProcess(settings)
        crawler.install()
        crawler.configure()
        spider=hotwire_hotel_comparer()
        Connection.cursor.execute("select * from amenities")
        current_amenities = {}
        for amenity in Connection.cursor.fetchall():
            current_amenities[str(amenity[1]).lower().strip()] = amenity[0]
        spider.original_amenties=current_amenities
        #Connection.cursor.execute("select * from tripadvisor_hotel_review_overview")
        crawler.queue.append_spider(spider)
        #print run_price_query([45770L, 35987L, 32587L, 17513L, 143359L, 35262L, 23092L, 37792L, 17249L, 18934L, 33187L, 21161L, 34351L, 34469L, 21978L, 66179L, 45586L, 70261L, 40791L, 3065L, 168366L, 36207L, 66188L, 93846L, 33546L, 31984L, 36558L, 31981L, 16010L, 35237L, 35695L, 35680L, 35766L, 8L, 40209L, 34355L, 244241L, 23097L, 35700L, 41108L, 12942L, 33753L, 177422L, 20510L, 4024L, 175667L, 35765L, 36500L, 96980L, 178976L, 32667L, 7207L, 4020L, 207305L, 30355L, 199674L, 12094L, 37554L, 66177L, 66195L, 36598L, 3978L, 66198L, 38008L, 66204L, 66161L, 13364L, 197171L, 33404L, 204760L, 30378L, 23698L, 155673L, 12073L, 168736L, 37648L, 155674L, 10527L, 36214L, 12509L, 23272L, 13692L, 66178L, 177549L, 5543L, 36630L, 196961L, 100413L, 4064L, 300265L, 102519L, 185495L, 65961L, 18114L, 35719L, 34796L, 21486L, 11359L, 174843L, 37097L, 66159L, 1877L, 155678L, 6100L, 258035L, 15492L, 156393L, 66168L, 32040L, 18107L, 3138L, 33657L, 66194L, 35783L, 26577L, 24767L, 15680L, 42168L, 155679L, 35508L, 41380L, 189889L, 2026L, 39639L, 26623L, 168513L, 310133L, 155672L, 34358L, 5545L, 335306L, 12830L, 21651L, 323582L, 66192L, 91707L, 66201L, 172798L, 66170L, 34274L, 10114L, 128950L, 20501L, 26471L, 16740L, 34170L, 21447L, 66186L, 284107L, 66176L, 39595L, 66166L, 99650L, 129343L, 335326L, 19164L, 103958L, 5793L, 66184L, 95182L, 95760L, 14222L, 66200L, 348204L, 96150L, 335316L, 36016L, 341680L, 171277L],crawler)
        crawler.start()
        search_price_hotelid = []
        kayak_to_us={}
        kayak_id =[]
        local_cp = spider.hotel_results
        for region in local_cp.items():
            print region[0]
            search_price_hotelid.extend(region[1].keys())
            for detail in region[1].items():
                print detail
        Connection.cursor.execute('select * from kayakhotels where hotels_hotelid in '+str(map(str,search_price_hotelid)).replace('[','(').replace(']',')'))
        dictionary_kayak={}
        out_file=open('output.csv','w')
        for al in Connection.cursor.fetchall():
            for region in local_cp.keys():
            #kayak_to_us[al[0]]
                if al[1] in local_cp[region]:
                    dictionary_kayak[al[0]] = local_cp[region][al[1]]
                    en_t=str(region)+','+str(al[0])+','
                    en_t +="".join([str(x).replace(',',' ')+',' for x in local_cp[region][al[1]]])
                    out_file.write(en_t+'\n')
        out_file.close()
        '''
        for it in dictionary_kayak.items():
            en_t=str(region)+','+str(it[0])+','
            en_t +="".join([str(x).replace(',',' ')+',' for x in it[1]])
            out_file.write(en_t+'\n')
#        out_file.write(dictionary_kayak)
        
        print 'fin'
        
            #kayak_to_us[al[0]]=al[1]
            #kayak_id.append(al[0])

            #pass kayak_id to kayak_spider with query parem, get dict with price as vals return here 
        # @type spider_output dict
       # map_hotelid_
        #for one in spider.hotel_results.items():
         #   for details in one: #dict entry [0] is region_name,star and [1] list of hotels
        print kayak_id
        #live_price = run_price_query(kayak_id,crawler)
        relate_price = {}
        for p in live_price.items():
            relate_price[kayak_to_us[p[0]]] = p[1]

        for reg in local_cp.items():
            for det in reg[1].items():
                # @type relate_price dict
                if relate_price.has_key(det[0]):
                    reg[1][det[0]].append(relate_price[det[0]])
                    
        print local_cp
        '''
        spider.log_file.close()


if __name__ == '__main__':
        main()