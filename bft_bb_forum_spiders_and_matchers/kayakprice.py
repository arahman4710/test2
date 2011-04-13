from libs import *


class KayakPriceSpider(BaseSpider):
	name = "KayakPriceSpider"    
	start_urls = ["http://www.kayak.com/hotels"];
	allowed_domains = ["kayak.com"];
	input = []
	queries = []
	
	def is_queried(self, search):
	
		# 1  Goes through the queries and returns a list if the
		#    same city/days combo has already been requested
		#
		output = []
		for query in self.queries:
			test_in = (query['checkin_date'] == search['checkin_date'])
			test_out = (query['checkout_date'] == search['checkout_date'])
			test_city = (query['othercity'] == search['othercity'])
			if (test_in and test_out and test_city):
				output.append(query)
		
		return output
	
	def parse(self, response):
		
		# 1  Iterates through the input and initiates all of the searches
		#
		for search in self.input[0:10]:
		
			# 2  Finds the city of the current hotel from the database
			#
			# hotel = search['hotel']
			# db = MySQLdb.connect(user='root', passwd='charles', db='acuity')
			# c = db.cursor()
			# c.execute("SELECT hotels.cityname, hotels.statename FROM hotels, k_hotels WHERE hotels.hotelid=k_hotels.hotel_id AND k_hotels.k_id=%s" % hotel)
			# city = c.fetchone()
			
			
			# 3  Formats the city name into a kayak-usable format
			#
			# cityname = re.search(".*?(?=(\(|$))", city[0])
			# cityname = cityname.group()
			# statename = city[1]
			# city = cityname + ", " + statename
			
			# 4  Creates the form data and determines if we already have a request for the same city/days
			#    If we have a request, use that, otherwise make a new one
			#
			search.update({'othercity': city})
			
			if (self.is_queried(search)):
				self.queries.append(search)				
			else:
				self.queries.append(search)
				request = FormRequest.from_response(response, formdata = search, callback = self.callfilter)
				request.meta['search_data'] = search
				yield request
		

	
	def callfilter(self, response):
	
		# 1  Finds the kayak search id of the current page
		#
		query = re.search('(?<=\/)[^/]+($|\?)', response.url)
		query = query.group()
		searches = self.is_queried(response.request.meta['search_data'])
		
		# 2  Goes through all of the searches for the current city/days
		#
		for search in searches:
		
			# 3  Combines the kayak search id and the kayak hotel id to find the prices page
			#		
			hotel = search['hotel']
			request = Request("http://www.kayak.com/h/hotel/details.vtl?searchid=%s&hid=%s&light=1&bookiturl=a&page=rates" % (query, hotel), callback = self.filtered)
			request.meta['search_data'] = search
			yield request
	
	def filtered(self, response):
	
		# 1  Find the price table from the results page
		#
		hxs = HtmlXPathSelector(response)
		pricetable = hxs.select("//table[contains(@class, 'bookingDetails')]")
		pricetable = pricetable[0]
		
		# 2  Find the rows of the table that are shown
		#
		pricerows = pricetable.select("tr[@style!=' display:none; ']")
		
		# 3  Go through the rows and get the:
		#     - Provider name
		#     - Base price
		#     - Taxes and fees
		#
		for row in pricerows:
			prices = row.select("td[contains(@class, 'amt base')]//text()")
			if (len(prices) >= 3):
				
				# 4  Find the provider name, 
				#
				name = re.search("(?i)(?<=amt base).*?(?=[^a-z])", row.extract())
				base = re.search("[0-9]+", prices[0].extract())
				taxes = re.search("[0-9]+", prices[1].extract())
				
				if (name and base and taxes):
					
					# 5  Finish getting info and get the original dates searched
					#
					info = response.request.meta['search_data']
					
					name = (name.group())[0:20]
					base = base.group()
					taxes = taxes.group()
					kayak_id = info['hotel']
					checkin = info['checkin_date']
					checkout = info['checkout_date']
					now = time.time()
					
					#db = MySQLdb.connect(user='root', passwd='charles', db='acuity')
					#c = db.cursor()
					# c.execute("INSERT INTO kayak_prices VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (kayak_id, name, today, checkin, checkout, base, taxes))
					#print "we should: INSERT INTO kayak_prices VALUES ('%s', '%s', '%s', '%s', '%s', '%s',

def main():
	# shut off log
	settings.overrides['USER_AGENT'] = "Mozilla/4.0 (compatible;MSIE 7.0;Windows NT 6.0)"
	settings.overrides['SCHEDULER_ORDER'] = 'BFO'
	scrapymanager.configure()
	
	spider = KayakPriceSpider()
	spider.input = [35102]
	scrapymanager.queue.append_spider(spider)
	
	scrapymanager.start()
	
		
if __name__ == '__main__':
	main()