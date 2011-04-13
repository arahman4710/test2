from libs import *
import match

class HotelNamesSpider(BaseSpider):
	name = "HotelNamesSpider"    
	start_urls = ["http://www.hotelnames.net"];
	allowed_domains = ["hotelnames.net"];
	
	def parse(self, response):
		# 1  Selects the cities from the html
		#
		hxs = HtmlXPathSelector(response)
		cities = hxs.select("//select[@name='cityname']/option/text()")
		
		for city in cities[0:10]:
		
			# 2  Request the form with each city
			#
			city = city.extract()
			request = FormRequest.from_response(response, formnumber = 1, formdata = { 'cityname':  city }, callback = self.parse_regions)
			request.meta["city"] = city
			yield request

	
	def parse_regions(self, response):
	
		# 1  Selects the regions from the html
		#
		hxs = HtmlXPathSelector(response)
		regions = hxs.select("//select[@name='zonename']/option/text()")
		
		for region in regions:
			
			# 2  Requests the form with each region
			#
			region = region.extract()
			request = FormRequest.from_response(response, formnumber = 1, formdata = { 'zonename': region }, callback = self.parse_stars)
			request.meta["city"] = response.request.meta["city"]
			yield request
			
	def parse_stars(self, response):
		
		# 1  Selects the stars from the html
		#
		hxs = HtmlXPathSelector(response)
		stars = hxs.select("//select[@name='star']/option/text()")
		
		for star in stars:
			
			# 2  Requests the form with each star
			#
			star = star.extract()
			request = FormRequest.from_response(response, formnumber = 1, formdata = { 'star': star }, callback = self.parse_hotels)
			request.meta["city"] = response.request.meta["city"]
			yield request
	
	def parse_hotels(self, response):
	
		# 1  Selects the rows of responses from the html
		#
		hxs = HtmlXPathSelector(response)
		hotels = hxs.select("//table//tr")
		city = response.request.meta["city"]
		out = []
		
		for hotel in hotels:
			hotel = hotel.select(".//text()")
			hotel = hotel.extract()
			if len(hotel) == 4:
				star = find_star(hotel[0])
				if star:
					region = hotel[1]
					name = hotel[2]
					probability = hotel[3][:-1]
					out += [";".join(map(str, [region + " " + city, name, star]))]
					
		states = find_states(city)

		open("output/hotels", "a").write(printable("@".join(["~".join(out), states, "priceline", "hotelnames"])) + "\n")
				

def main():
	# shut off log
	#settings.overrides['LOG_ENABLED'] = False
	scrapymanager.configure()
	
	#spider = KayakPriceSpider()
	#spider.input = auto_queries()
	
	spider = HotelNamesSpider()
	scrapymanager.queue.append_spider(spider)
	settings.overrides['USER_AGENT'] = "Mozilla/4.0 (compatible;MSIE 7.0;Windows NT 6.0)"
	settings.overrides['SCHEDULER_ORDER'] = 'BFO'
	
	scrapymanager.start()
	
		
if __name__ == '__main__':
	main()