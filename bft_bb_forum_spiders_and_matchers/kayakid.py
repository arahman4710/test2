from libs import *
from difflib import SequenceMatcher

global_found = 0

def rNA(s): return "".join(i for i in s if ord(i)<128)

def match_hotel(id, name, address, city):
	# Find the best match for the hotel, or add a new one to our database
	#
	matched = 0
	
	if not c.execute("SELECT * FROM kayakhotels WHERE kayakid='%s'" % id):
		address = re.sub("\(.*?\)", "", address)
		c.execute("SELECT * FROM hotels WHERE cities_cityid='%s'" % city)
		hotels = c.fetchall()
		
		for hotel in hotels:
			num1 = re.search("[0-9]*", address)
			num2 = re.search("[0-9]*", hotel[2])
			s = SequenceMatcher(None, address, hotel[2])
			
			if num1 and num2:
				num1 = num1.group()
				num2 = num2.group()
				
				if num1 == num2 and s.ratio() > 0.8:
					matched = 1
					c.execute("INSERT INTO kayakhotels VALUES ('%s','%s','%s')" % (id, hotel[0], name))
					break
					
	if not matched:
		open("logs/kayakid", "a").write("MATCH FAILED: %s; %s; %s\n" % (rNA(id), rNA(name), rNA(address)))
	
class KayakIdSpider(BaseSpider):
	name = "KayakIdSpider"    
	start_urls = ["http://www.kayak.com/hotels"];
	allowed_domains = ["kayak.com"];
	
	
	def parse(self, response):
	
		# 1  Finds all of the distinct city + state combinations from the table
		#
		db1= MySQLdb.connect(user='root', passwd='charles', db='acuity')
		c = db1.cursor()
		c.execute("SELECT city, state FROM cities WHERE NOT city='' AND NOT state=''")
		cities = c.fetchall()
		days = dates(10)
		day = 5

		for city in cities[0:2]:
			# 2a  Format the search parameters
			#
			cityname = city[0]
			statename = city[1]
			city_request = cityname + ", " + statename
			search = {'othercity': city_request, 'checkin_date': days[day], 'checkout_date': days[day + 1]}
			
			# 2b Create searches for each of the cities
			#    pass the city and state data along with each request
			#
			request = FormRequest.from_response(response, formdata = search, callback = self.callfilter)
			request.meta['city'] = city
			yield request
	
		
	def callfilter(self, response):
		
		# 1  Finds the query id of the current city/date combination
		#
		query = re.search('(?<=\/)[^/]+($|\?)', response.url)
		query = query.group()
		
		# 2  Creates a query to the js results page and passes along the city request information
		#
		request = Request("http://www.kayak.com/s/jsresults?ss=1&searchid=" + query + "&pn=0", callback = self.filtered)
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
		city = response.request.meta['city']
		cityid = find_city(city[0], city[1], "united states", c)
	
		
		for div in hotels:
			
			# 2  Find the section containing hotel id, name, and address in the string
			#
			id = div.select(".//div[contains(@id, 'resultid')]/text()")
			name = div.select(".//div[contains(@id, 'hname')]/text()")
			address = div.select(".//a[@class='subtlelink']/text()")
			
			if (id and name and address):
				
				# 3  Isolate the information from the sections taken
				#
				found = 1
				global global_found
				global_found = 1
				id = id[0].extract()
				name = name[0].extract()
				address = address[0].extract()
				
				# 4  Match the hotel to one of our records or insert a new entry into the database
				#
				match_hotel(id, name, address, cityid)
							
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
			
		elif response.request.meta['page'] == 0:
			# If no results are found output an error to the log file
			#
			city = response.request.meta['city']
			cityname = city[0]
			statename = city[1]
			open("logs/kayakid", "a").write("ERROR: no results found for %s, %s\n" % (cityname, statename))
		
		else:
			# At the end of a city output a success message
			#
			city = response.request.meta['city']
			cityname = city[0]
			statename = city[1]
			open("logs/kayakid", "a").write("CRAWLED: %s, %s\n" % (cityname, statename))
		

def main():
	# shut off log
	settings.overrides['USER_AGENT'] = "Mozilla/4.0 (compatible;MSIE 7.0;Windows NT 6.0)"
	settings.overrides['SCHEDULER_ORDER'] = 'BFO'
	scrapymanager.configure()
	
	
	spider = KayakIdSpider()
	scrapymanager.queue.append_spider(spider)
	
	scrapymanager.start()
	if not global_found:
		open("logs/kayakid", "a").write("ERROR: parsing service failed\n")
	
		
if __name__ == '__main__':
	#main()
	a = Hotel("Sheraton Bloomington", "1230 Blah street")
	print a
