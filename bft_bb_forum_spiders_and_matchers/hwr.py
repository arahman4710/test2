from scrapy.selector import HtmlXPathSelector
from scrapy.http import FormRequest
from scrapy.conf import settings
from scrapy import signals
from scrapy.crawler import CrawlerProcess
from scrapy.spider import BaseSpider
from scrapy.xlib.pydispatch import dispatcher
from scrapy.http import Request
from scrapy import log

import re
import MySQLdb

class HWRegionSpider(BaseSpider):
	name = "HWRegionSpider"
	allowed_domains = ["hotwire.com"];
	
	def start_requests(self):
		cities = open("cities.txt").read()
		cities = cities.split("\n")
		# Make sure not to go over the API limit
		for city in cities[:1]:
			#635xqf9gyrepe275jjsxgfsb navid
			#ndcta58my7us8fjgzg5dq9gq mine
			yield Request('''http://api.hotwire.com/v1/search/hotel?apikey=ndcta58my7us8fjgzg5dq9gq&dest=%s&rooms=1&adults=2&children=0&startdate=01/20/2011&enddate=01/23/2011''' % city, callback=self.parse)
		
	def statify(self, str):
		states = { 'AL':'Alabama', 'AK':'Alaska', 'AS':'American Samoa', \
		'AZ':'Arizona', 'AR':'Arkansas', 'CA':'California', 'CO':'Colorado', \
		'CT':'Connecticut', 'DE':'Delaware', 'DC':'District of Columbia', \
		'FM':'Federated States of Micronesia', 'FL':'Florida', 'GA':'Georgia', \
		'GU':'Guam', 'HI':'Hawaii', 'ID':'Idaho', 'IL':'Illinois', 'IN':'Indiana', \
		'IA':'Iowa', 'KS':'Kansas', 'KY':'Kentucky', 'LA':'Louisiana', \
		'ME':'Maine', 'MH':'Marshall Islands', 'MD':'Maryland', 'MA':'Massachusetts', \
		'MI':'Michigan', 'MN':'Minnesota', 'MS':'Mississippi', 'MO':'Missouri', \
		'MT':'Montana', 'NE':'Nebraska', 'NV':'Nevada', 'NH':'New Hampshire', \
		'NJ':'New Jersey', 'NM':'New Mexico', 'NY':'New York', 'NC':'North Carolina', \
		'ND':'North Dakota', 'MP':'Northern Mariana Islands', 'OH':'Ohio', \
		'OK':'Oklahoma', 'OR':'Oregon', 'PW':'Palau', 'PA':'Pennsylvania', \
		'PR':'Puerto Rico', 'RI':'Rhode Island', 'SC':'South Carolina', \
		'SD':'South Dakota', 'TN':'Tennessee', 'TX':'Texas', 'UT':'Utah', \
		'VT':'Vermont', 'VI':'Virgin Islands', 'VA':'Virginia', 'WA':'Washington', \
		'WV':'West Virginia', 'WI':'Wisconsin', 'WY':'Wyoming' }
		
		str = str.upper()
		if str in states.keys():
			return states[str]
		else:
			return None
	
	def countrify(self, str):
		if str == "US":
			return "United States"
		elif str == "CA":
			return "Canada"
		return None
	
	def find_city(self, city, state, country, c):
		city = c.execute("SELECT cityid FROM cities WHERE city='%s' AND state='%s' AND country='%s'" % (city, state, country))
		if city:
			return c.fetchone()[0]
		
		c.execute("INSERT INTO cities (city, state, country) VALUES ('%s','%s','%s')" % (city, state, country))
		c.execute("SELECT cityid FROM cities ORDER BY cityid DESC LIMIT 1")
		return c.fetchone()[0]
	
	def parse(self, response):
		open("results", "a").write(response.body + "\n")
		database = MySQLdb.connect(user='root', passwd='charles', db='acuity')
		c = database.cursor()
		hxs = HtmlXPathSelector(response)
		areas = hxs.select("//neighborhoods/neighborhood")
		link = hxs.select("//deeplink/text()")
		print link.extract()[0]
		
		for area in areas:
			id = area.select(".//id/text()")[0].extract()
			
			if not c.execute("SELECT * FROM hotwireregions WHERE hotwireid=%s" % id):
				state = area.select(".//state/text()")[0].extract()
				state = self.statify(state)
				
				country = area.select(".//country/text()")[0].extract()
				country = self.countrify(country)
				
				if state and country:
					city = area.select(".//city/text()")[0].extract()
					city = self.find_city(city, state, country, c)
					
					if city:
						center = area.select(".//centroid/text()")[0].extract()
						[clat, clng] = re.findall("[0-9]*\.[0-9]*", center)
						
						name = area.select(".//name/text()")[0].extract()
						points = area.select(".//shape/latlong/text()").extract()
						
						c.execute('''INSERT INTO hotwireregions (hotwireid, regionname, cities_cityid, latitude, longitude, active) VALUES
						(%s,"%s","%s",%s,%s,"%s")''' % (str(id), str(name), str(city), str(clat), str(clng), 1))
						if c.execute('''SELECT hotwireregionid FROM hotwireregions ORDER BY hotwireregionid DESC LIMIT 1'''):
							last = c.fetchone()[0]
							for i in range(len(points)):
								[plat, plng] = re.findall("[0-9]*\.[0-9]*", points[i])
								c.execute('''INSERT INTO hotwirepoints (hotwireregions_hotwireregionid, orderid, latitude, longitude) VALUES
								("%s","%s","%s","%s")''' % (str(last), str(i), str(plat), str(plng)))
							
						
						
	
def main():
	log.start()
	settings.overrides['USER_AGENT'] = "Mozilla/4.0 (compatible;MSIE 7.0;Windows NT 6.0)"
	settings.overrides['SCHEDULER_ORDER'] = 'DFO'	
	settings.overrides['CONCURRENT_REQUESTS_PER_SPIDER'] = 1
	
	crawler = CrawlerProcess(settings)
	crawler.install()
	crawler.configure()
	
	spider = HWRegionSpider()
	crawler.queue.append_spider(spider)
	
	crawler.start()
	
		
if __name__ == '__main__':
	main()