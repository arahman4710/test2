from libs import *
from hotel import *

class BBPricelinePostSpider(BaseSpider):
	name = "BBPricelinePostSpider"    
	start_urls = ["http://www.betterbidding.com/"];
	allowed_domains = ["www.betterbidding.com"];
	
	def parse(self, response):
	
		# 1  Finds all of the regions for USA
		#

                request= Request('http://www.betterbidding.com/index.php?showtopic=546&',callback=self.parse_priceline_list)
                request.meta['states'] = 'Texas'
                yield request
                '''
		hxs = HtmlXPathSelector(response)
		regions = hxs.select("//div[@id='fo_441']/table[@class='ipbtable']//tr")
		
		for region in regions:
		
			# 2  Find the board URL's from the current XPaths
			#
			url = region.select(".//td/b/a/@href")
			if (url):
			
				# 3  Format the response url and then crawl each of the boards
				#
				url = url[0].extract()
				yield Request(url, callback=self.find_board)
                '''
	
	def find_board(self, response):
		
		# 1  Finds all bolded elements in the board
		#
		hxs = HtmlXPathSelector(response)
		boards = hxs.select("//div[starts-with(@id, 'fo_')]//tr//b")
		
		for board in boards:
		
			# 2  Finds any board with "Priceline " in the title url
			#
			check = re.search("(?i)priceline\s", board.extract())
			if (check):
				url = board.select(".//@href")
				
				# 3  Extracts the url if found
				#
				if (url):
					url = url[0].extract()
					return Request(url, callback = self.parse_board)
	
	def parse_board(self, response):
		
		# 1  Finds all of the board posts
		#
		hxs = HtmlXPathSelector(response)
		posts = hxs.select("//div[@class='borderwrap']/table[@class='ipbtable']//tr/td[@class='row1' and @valign='middle']/div[2]")	
			
		# 1b  Matches the board title to a group of states
		#
		title = hxs.select("//head/title/text()")[0].extract()

                if 'Washington, DC' in title:
                    states = ['DC']
                else:
                    states = find_states(title)

                states = ",".join(map(lambda x: "'%s'" % x, states))
                
		if len(states) == 0:
			open("bbpl.log", "a").write("STATE SEARCH ERROR: `%s`\n" % title)
		
		# 2  Find the hotel list and parse it
		#
		list = hxs.select("//a[contains(text(), 'Priceline Hotel List')]/@href")
		if (list):
			list = list[0].extract()
			request = Request(list, callback = self.parse_priceline_list)
			request.meta['states'] = states
			yield request
		
		
		parse = []
		'''
		for post in posts:
			# 3  Iterate through the posts
			#
			title = post.select("./span//text()")
			subtitle = post.select("./div//text()")
			replies = post.select("../..//td[@class='row2'][1]//text()")
			post_url = post.select("./span/a/@href")
			
			if (title and subtitle and (len(replies) >= 3) and post_url):
				
				# 4  Extract as much information as possible from the posts titles
				#
				title = title[0].extract()
				subtitle = subtitle[0].extract()
				star = find_star(title)
				price = find_price(subtitle)
				name = find_name(title)
				dates = self.find_dates(subtitle)
				if (dates):
					date = dates[0]	
					nights = dates[1]
				else:
					date = False
					nights = False
				
				# 5  Get the remaining information from the post html
				#
				replies = replies[0].extract()
				post_url = post_url[0].extract()
				post_num = self.find_post_num(post_url)
				
				if (title and star and name and date and nights and replies and post_num and price):
					title = re.sub("\n", "", title)
					name = re.sub("\n", "", name)
					if not re.match("[0-9]+", replies):
						replies = -1
					parse += [CSV.pack(CSV(), [name, price, star, date, nights, replies, post_num], "#")]
					
		open("bbpl.log", "a").write("SAVING POSTS: `%s` , `%s`\n" % (states, response.url))
		parse = CSV.pack(CSV(), parse, "~")
		parse = CSV.pack(CSV(), [parse, states, "priceline", "bb"], "@")
		open("output/posts-bbpl", "a").write(CSV.prepare(CSV(), parse) + "\n")
		
		
		# 7  Find the link to the next page
		#
		next = hxs.select("//a[@title='Next page']/@href")
		if (next):
			next = next.extract()
			next = next[0]
			yield Request(next, callback = self.parse_board)
		else:
			print 'done'			
		'''
	def parse_priceline_list(self, response):


                # 0 print the states and return
                #
               # print str(response.request.meta['states'])
                #return

		# 1  Find the body of the post
		#
		hxs = HtmlXPathSelector(response)
		postes = hxs.select("//div[@class='postcolor']")
		
		
		if (postes):

                    for post in postes:
                        output = []
			# 2  Find the line breaks, hor. rules, links, and text
			#
			#post = post[0]
			posts = post.select(".//br|.//u|.//text()")
			
			# 3  Initialize the variables for use in the loop
			#
			region = ""
			star = 0
			newline = 1
			
			# 4  Iterate through and find all hotels
			#
			for post in posts:
				post = post.extract()
				post = post.strip()
                                #print '\n\n\n'
                                #print response.url
                                print 'BEFORE ',
                                print post
			#	print '_____POST________'
                        #        try:
                        #            print post
                        #        except:
                        #            print 'printing post'
                                # 4a  Set a newline
				#
				if (post == '<br>'):
					newline += 1
				
				# 4b  If the post is on a newline
				#
				if (newline):
					
					# 4c  ... and is underlined, set a new region and reset newline
					#
                                        #print '        '+post
					if (post[0:3] == '<u>'):
                                            is_state = 0
                                            for every in response.request.meta['states'].split(','):
                                                if post[3:-4].lower() == every[1:-1]:
                                                    is_state = 1
                                            if not is_state:
                                                region = post[3:-4]
                                                newline = 0

                                        # 4d If there are multiple states, detect the change in state
                                        #
                                        if ',' in str(response.request.meta['states']):
                                            if '<b>' in post:
                                                state = post[6:-8].lower()
                                               # print state

                                            if post[0:3] == '<u>':
                                                for every in response.request.meta['states'].split(','):
                                                    if post[3:-4].lower() == every[1:-1]:
                                                        state= post[3:-4].lower()
                                                #        print state
                                        
                                        else:
                                            state = str(response.request.meta['states']).lower()[1:-1]
                                            #print state
                                                        #4d i  search states list to see if we have a match and use it
                                                        # to get current state


                                        # 4di  If this is DC then let's call the state DC and city Washington
                                        #



                                        # 4d else use the single state we were given
                                        #



					# 4e  ... and is text, find hotel into and store it
					#
					if (not re.search("<|>", post)):
                                                print 'IN LOOP!    ',
                                                print post
						star = find_star(post)
						name = (find_name(post)).strip()
						if (star and name):
							city = re.search("(?s).*?(?=\(|$|-s)", region)
							if city: city = (city.group()).strip()
							else: city = " "
							
							rgn = re.search("(?s)(?<=\().*(?=\))", region)
							if rgn: rgn = (rgn.group()).strip()
							else: rgn = " "
                                                        
                                                        if state == 'dc':
                                                            city = 'Washington'
                                                        
                                                        #..add current state in every hotel record
                                                        '''
                                                        f = open('texas.csv','a')
                                                        f.write('\n')
                                                        f.write(rgn)
                                                        f.write('\n')
                                                        f.write('\t')
                                                        f.write(name)
                                                        f.write('\n')
                                                        f.close()
							'''
                                                        output += [CSV.pack(CSV(), [state,city, rgn, name, star,response.url], "#")]
                                                     #   print '_____OUTPUT________'
                                                     #   try:
                                                     #       print [CSV.pack(CSV(), [state,city, rgn, name, star], "#")]
                                                     #   except:
                                                     #       print 'Tried to print'
			open("bbpl.log", "a").write("SAVING HOTEL LIST: `%s` , `%s`\n" % (str(response.request.meta['states']), response.url))
			output = CSV.pack(CSV(), output, "~")
			output = CSV.pack(CSV(), [output, response.request.meta['states'], "priceline", "bb"], "@")
                       # print '_____OUTPUT________'
                       # print output
			open("output/hotels-bbpl4", "a").write(CSV.prepare(CSV(), output) + "\n")
			
			
	def date_diff(self, date1, date2):
		try:
			# 1  Try to calculate and return the difference
			#
			d1 = time.strptime(date1, "%m/%d/%y")
			d2 = time.strptime(date2, "%m/%d/%y")
			d1 = d1.tm_yday
			d2 = d2.tm_yday
			return [date1, d2 - d1]
		except:
			0
		
	def find_dates(self, str):
		
		# 1  Find the dates
		#
		date1 = re.search("[0-9]{1,2}/[0-9]{1,2}/[0-9]{1,2}", str)
		date2 = re.search("(?<=-)[0-9]{1,2}/[0-9]{1,2}/[0-9]{1,2}", str)
		
		# 2  Return the calculated difference
		#
		if (date1 and date2):
			date1 = date1.group()
			date2 = date2.group()
			return self.date_diff(date1, date2)

	def find_post_num(self, url):
		
		# Finds the post number from the url and returns it
		#
		num = re.search("(?<=/)[0-9]*$", url)
		if (num):
			return num.group()
		else:
			return False
	
	
def main():
	#log.start()
	settings.overrides['USER_AGENT'] = "Mozilla/4.0 (compatible;MSIE 7.0;Windows NT 6.0)"
	settings.overrides['SCHEDULER_ORDER'] = 'DFO'	
	
	crawler = CrawlerProcess(settings)
	crawler.install()
	crawler.configure()
	
	spider = BBPricelinePostSpider()
	crawler.queue.append_spider(spider)
	
	crawler.start()
	
		
if __name__ == '__main__':
	main()