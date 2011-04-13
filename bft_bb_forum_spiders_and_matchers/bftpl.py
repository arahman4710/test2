from libs import *
from hotel import *

from scrapy.selector import HtmlXPathSelector
from scrapy.http import FormRequest
from scrapy.conf import settings
from scrapy.crawler import CrawlerProcess
from scrapy.spider import BaseSpider
from scrapy.xlib.pydispatch import dispatcher
from scrapy.http import Request
from scrapy import log
from scrapy import log, signals, project
from multiprocessing import Process, Queue

class BFTPostSpider(BaseSpider):
	name = "BFTPostSpider"    
	start_urls = ["http://biddingfortravel.yuku.com/"];
	allowed_domains = ["biddingfortravel.yuku.com"];
	
	def parse(self, response):
	
		# 1  Finds all of the regions for USA
		#
		hxs = HtmlXPathSelector(response)
		regions = hxs.select("//table[@summary='USA Hotels Forums']/tbody/tr")
		
		for region in regions:
		
			# 2  Find the board URL's from the current XPaths
			#
			url = region.select(".//h3//@href")
			
			if (url):
			
				# 3  Format the response url and then crawl each of the boards
				#
				url = url[0].extract()
				url = response.url + url[1:]
				yield Request(url, callback = self.parse_board)
	
	def parse_board(self, response):
		
		# 1a  Finds all of the board posts
		#
		hxs = HtmlXPathSelector(response)
		posts = hxs.select("//table[@summary='forum topics']/tbody/tr[not(contains(@class, 'sticky'))]")
		
		# 1b  Matches the board title to a group of states
		#
		title = hxs.select("//head/title/text()")[0].extract()
		states = find_states(title)
		states = ",".join(map(lambda x: "'%s'" % x, states))
		if len(states) == 0:
			open("bftpl.log", "a").write("STATE SEARCH ERROR: `%s`\n" % title)
	
		# 2a  Parse the hotel list page
		#
		if (response.url[-5:] == '.html'):
			hotel_list = hxs.select("//tr[contains(@class,'sticky')]/td[@class='topic-titles']/a/@href")
			
			if (hotel_list):
				url = hotel_list[0].extract()
				request = Request("http://biddingfortravel.yuku.com" + url, callback = self.parse_hotel_list)
				request.meta['states'] = states
				yield request
		
		parse = []
		
		for post in posts:
			# 2b  Iterate through the posts
			#
			title = post.select(".//td[@class='topic-titles']/a/text()")
			replies = post.select(".//td[@class='replies']//text()")
			post_url = post.select(".//td[@class='topic-titles']/a/@href")
			
			if (title and replies and post_url):
				
				# 3  Extract as much information as possible from the posts titles
				#
				title = title[0].extract()
				star = find_star(title)
				price = find_price(title)
				name = find_name(title)
				dates = self.find_dates(title, '2010')
				if (dates):
					date = dates[0]	
					nights = dates[1]
				else:
					date = False
					nights = False
				
				# 4a  Get the remaining information from the post html
				#
				replies = replies[0].extract()
				post_url = post_url[0].extract()
				post_num = self.find_post_num(post_url)
				
				if (title and star and name and date and nights and replies and post_num and price):
					title = re.sub("\n", "", title)
					name = re.sub("\n", "", name)
					parse += [CSV.pack(CSV(), [name, price, star, date, nights, replies, post_num], "#")]
					
		# 4b  Process all of the hotels using the match_hotel function
		#
		open("bftpl.log", "a").write("SAVING POSTS: `%s` , `%s`\n" % (states, response.url))
		parse = CSV.pack(CSV(), parse, "~")
		parse = CSV.pack(CSV(), [parse, states, "priceline", "bft"], "@")
		open("output_edit/posts-bftpl", "a").write(CSV.prepare(CSV(), parse) + "\n")
		
		
		# 5  Find the link to the next page
		#
		"//div[@class='pager-links']/a"
		".//text()"
		next = hxs.select("//div[@class='next active']/a/@href")
		if (next):
			next = next.extract()
			next = next[0]
			yield Request("http://biddingfortravel.yuku.com" + next, callback = self.parse_board)
	
	def parse_hotel_list(self, response):
	
		# 1  Find the body of the post
		#
		hxs = HtmlXPathSelector(response)
		post = hxs.select("//div[contains(@class, 'post-body')]")
		output = []
		
		if (post):
			# 2  Find the line breaks, hor. rules, links, and text
			#
			post = post[0]
			posts = post.select(".//br|.//a|.//text()")
			
			# 3  Initialize the variables for use in the loop
			#
			city = ""
			region = ""
			newcity = 1
			star = 0
			linked = 0
			newline = 1
			
			# 4  Iterate through and find all hotels
			#
			for post in posts:
				post = post.extract()
				post = post.strip()
				
				if (newline):
					
					# 4a  Check if the line is the text of a link
					#
					if (linked):
						title = re.search("^[^<>]*$", post)
						if (title):
							title = title.group()
							city = re.sub("\n", "", city)
							region = re.sub("\n", "", region)
							title = re.sub("\n", "", title)
							if (re.search("(?i)possible", title)):
								continue
							title = re.sub("\n", "", title)
							output += [CSV.pack(CSV(), [city, region, title, star], "#")]
							#output += [";;".join([rNA(city), rNA(region), rNA(title), rNA(str(star))])]
							linked = 0
							newline = 0
						continue
							
					# 4b  Check for a link
					#
					a = re.search("(?is)<a.*>.*</a>", post)
					if (a):
						linked = 1
						continue
					
					# 4c  If the text doesn't belong to a link
					#
					if (not linked):
						
						# 4d  Find a star rating
						#
						title = find_star(post)
						if (title):
							star = title
							continue
						
						# 4e  Find a possible hotel
						#
						title = re.search("(?i)possible:", post)
						if (title):
							continue
						
						# 4f  Find a new city
						#
						title = re.search("^[^a-z<>]*$", post)
						if (title):
							title = (title.group()).strip()
							if (title):
								city = title
								region = ""
								newcity = 0
								newline = 0
							continue
						
						# 4g  Find a new region
						#
						title = re.search("^[^<>]+$", post)
						if (title):
							title = title.group()
							if (re.search("(?is)(possible)|([0-9].*star)", title)):
								continue
							region = title
							newline = 0
							continue
						
						continue
						
				# 4g  Check for a newline
				#
				br = re.search("^<br.*>$", post)
				if (br):
					newline = 1
					continue
			
		# 5  Output to a file with fields separated by ';' and entries by '\n'
		#
		open("bftpl.log", "a").write("SAVING HOTEL LIST: `%s` , `%s`\n" % (str(response.request.meta['states']), response.url)) 
		output = CSV.pack(CSV(), output, "~")
		output = CSV.pack(CSV(), [output, response.request.meta['states'], "priceline", "bft"], "@")
		open("output_edit/hotels-bftpl", "a").write(CSV.prepare(CSV(), output) + '\n')
				
	def date_diff(self, date1, date2, year):
		try:
			# 1  Make sure the dates are valid
			#
			if ((0 < int(date1[0]) < 12) and (0 < int(date2[0]) < 12)
			and (0 < int(date1[1]) < 31) and (0 < int(date2[1]) < 31)):
				0 # Dates are mm/dd
				
			elif ((0 < int(date1[1]) < 12) and (0 < int(date2[1]) < 12)
			and (0 < int(date1[0]) < 31) and (0 < int(date2[0]) < 31)):
				0 # Dates are dd/mm, reverse them
				sw1 = date1[0]
				sw2 = date2[0]
				date1[0] = date1[1]
				date2[0] = date2[1]
				date1[1] = sw1
				date2[1] = sw2
			
			else: raise Exception() # Invalid date -> throw exception
				
			
			# 2  Convert the dates to a usable format
			#
			date1 = "%s/%s/%s" % (date1[0], date1[1], year)
			date2 = "%s/%s/%s" % (date2[0], date2[1], year)
			
			d1 = time.strptime(date1, "%m/%d/%Y")
			d2 = time.strptime(date2, "%m/%d/%Y")
			d1 = d1.tm_yday
			d2 = d2.tm_yday
			
			return [date1, d2 - d1]
		except:
			0
		
	def find_dates(self, str, year):
		
		# 1  Remove anything that might interfere with parsing
		#
		str = re.sub("(?i)[^a-z]*\*", "", str)
		
		# 2  Make suitable replacements so dates are easier to work with
		#
		str = re.sub("(?i)((january)|(jan\.?))\s*", "1/", str)
		str = re.sub("(?i)((february)|(feb\.?))\s*", "2/", str)
		str = re.sub("(?i)((march)|(mar\.?))\s*", "3/", str)
		str = re.sub("(?i)((april)|(apr\.?))\s*", "4/", str)
		str = re.sub("(?i)(may)\s*", "5/", str)
		str = re.sub("(?i)((june)|(jun\.?))\s+", "6/", str)
		str = re.sub("(?i)((july)|(jul\.?))\s+", "7/", str)
		str = re.sub("(?i)((august)|(aug\.?))\s*", "8/", str)
		str = re.sub("(?i)((september)|(sept\.?))\s*", "9/", str)
		str = re.sub("(?i)((october)|(oct\.?))\s*", "10/", str)
		str = re.sub("(?i)((november)|(nov\.?))\s*", "11/", str)
		str = re.sub("(?i)((december)|(dec\.?))\s*", "12/", str)
		# 3  Try to match a date range     mm/dd - mm/dd
		#
		dates = re.search("(?<!/)[0-9]{1,2}/[0-9]{1,2}\s*-\s*[0-9]{1,2}/[0-9]{1,2}(?!/)", str)
		if (dates):
		
			# 3a  Split the string and create proper dates
			#
			dates = re.findall("[0-9]{1,2}/[0-9]{1,2}", dates.group())
			year = (time.gmtime(time.time())).tm_year
			date1 = re.split("/", dates[0])
			date2 = re.split("/", dates[1])
			
			# 3b  Calculate the date and return it
			#
			return self.date_diff(date1, date2, year)
			
		
		# 4  Try fixing a range to make it usable     mm/dd - dd
		#
		dates = re.search("(?<!/)[0-9]{1,2}/[0-9]{1,2}\s*-\s*[0-9]{1,2}(?!/)", str)
		if (dates):
			# 4a  Setup the string to do the same calculation as 3b
			#
			dates = dates.group()
			dates = re.split("-", dates)
			month = (re.split("/", dates[0]))[0]
			
			year = (time.gmtime(time.time())).tm_year
			date1 = re.split("/", dates[0])
			date2 = [month, dates[1]]
			
			# 4b  Calculate the date and return it
			#
			return self.date_diff(date1, date2, year)
			
			
		# 5  Match a single day     mm/dd
		#
		dates = re.search("(?<!/)[0-9]{1,2}/[0-9]{1,2}(?!/)", str)
		if (dates):
			year = (time.gmtime(time.time())).tm_year
			return [dates.group() + "/%d" % year, 1]
		
		# 6  If there are no matches return false
		#
		return False

	def find_post_num(self, url):
		
		# Finds the post number from the url and returns it
		#
		num = re.search("(?<=/)[0-9]*(?=/)", url)
		if (num):
			return num.group()
		else:
			return False
	
		
def main():
	log.start()
	settings.overrides['USER_AGENT'] = "Mozilla/4.0 (compatible;MSIE 7.0;Windows NT 6.0)"
	settings.overrides['SCHEDULER_ORDER'] = 'DFO'	
	
	crawler = CrawlerProcess(settings)
	crawler.install()
	crawler.configure()
	
	spider = BFTPostSpider()
	crawler.queue.append_spider(spider)
	
	crawler.start()
			
if __name__ == '__main__':
	main()