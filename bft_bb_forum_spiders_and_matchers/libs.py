from scrapy.selector import HtmlXPathSelector
from scrapy.http import FormRequest
from scrapy.conf import settings
from scrapy import signals
from scrapy.crawler import CrawlerProcess
from scrapy.spider import BaseSpider
from scrapy.xlib.pydispatch import dispatcher
from scrapy.http import Request
from scrapy import log
import Levenshtein

import re
import time
import MySQLdb
import urllib
import sys
import string


def printable(str):
 control = "".join(map(unichr, range(0,127)))
 control = re.escape( control)
 return re.sub("[^%s]" % control, "", str)

def rNA(str):
	control = "".join(map(unichr, range(31,127)))
	control = re.escape(control)
	return re.sub("[^%s]" % control, "", str)


def find_city(city, state, country, c):

	city = city.strip()
	city = re.sub("[^a-zA-Z\s]", "", city)
	state = state.strip()
	state = re.sub("[^a-zA-Z\s]", "", state)
	country = country.strip()
	country = re.sub("[^a-zA-Z\s]", "", country)

	c.execute("SELECT cityid FROM cities WHERE city='%s' AND state='%s' AND country='%s'" % (city, state, country))
	r = c.fetchone()
	if r:
		return str(r[0])
	else:
		c.execute("INSERT INTO cities (city, state, country) VALUES ('%s', '%s', '%s')" % (city, state, country))
		c.execute("SELECT max(cityid) FROM cities")
		city_id = c.fetchone()[0]
		return str(city_id)

def find_states(input):
	db = MySQLdb.connect(user="root", passwd="areek", db="acuity")
	c = db.cursor()
	out = []
	input = input.lower()
        #input = str
	los = ["Alabama", "Alaska", "Arizona", "Arkansas",
			  "California", "Colorado", "Connecticut", "Delaware",
			  "Florida", "Georgia", "Hawaii", "Idaho", "Illinois",
			  "Indiana", "Iowa", "Kansas", "Kentucky", "Louisiana",
			  "Maine", "Maryland", "Massachusetts", "Michigan",
			  "Minnesota", "Mississippi", "Missouri", "Montana",
			  "Nebraska", "Nevada", "New Hampshire", "New Jersey",
			  "New Mexico", "New York", "North Carolina",
			  "North Dakota", "Ohio", "Oklahoma", "Oregon",
			  "Pennsylvania", "Rhode Island", "South Carolina",
			  "South Dakota", "Tennessee", "Texas", "Utah",
			  "Vermont", "Virginia", "Washington", "Washington,DC", "West Virginia",
			  "Wisconsin", "Wyoming"]
	los = map(lambda x: x.lower(), los)
	
	# 1a  Try to find if its grouped by '* states'
	#
	states = re.search("(?i)([a-z]{1})\s*states", input)
	if states:
		for i in range(len(los)):
			if los[i][0].lower() == states.group(1):
				out += [los[i]]
		
		return out	
		
	# 1b  Finally, try to match states within the name

       # print input
        input = printable(input)
        if ' and ' in input and ' - ' not in input:
            input = input.split(' and ')
        if ' - ' in input:
            input = input.split(' - ')[1].split(' / ')

        for state in los:
            for one in input: 
                if Levenshtein.ratio(str(re.search("(?s).*?(?=\(|$|-s)", one).group(0)).strip(),str(state).strip()) > 0.9:
                    out += [state]
        
        return out

		
def dates(length):
	days = []
	
	# Calculates the next "length" days into the future and returns each in a mm/dd/yyyy format
	#
	for day in range(0, length):
		cur = time.time()
		cur += day * 86400
		cur = time.localtime(cur)
		days.append(time.strftime("%m/%d/%Y", cur))
	return days
	
def cmp(str1, str2):

	# 1  Splits the strings into individual words
	#
	str1 = re.split("(?i)[^a-z]", str1.lower())
	str2 = re.split("(?i)[^a-z]", str2.lower())
	
	# 2  Makes sure the smaller word is in str1
	#
	if (len(str1) > len(str2)):
		a = str1
		str1 = str2
		str2 = a
	
	matches = 0
	
	# 3  Calculates probability of match by:
	#    (words from str1 found in str2) / number of words in str1
	#
	for word in str1:
		if word in str2:
			matches += 1
	
	# 4  Rounds off the value and returns it
	#
	return round(float(matches) / float(len(str1)), 2)

def cmp_abbr(str1, str2):
	
	# 1  Finds the smaller string and puts it in str1
	#
	if (len(str1) > len(str2)):
		a = str1
		str1 = str2
		str2 = a
	
	str1 = list(str1)
	index = 0
	
	# 2  Counts how many characters from str1 match in str2 in the same order
	#
	for char in str1:
		loc = str2.find(char, index)
		if (loc >= 0):
			index = loc
		else:
			return False
	
	return True
	
def check_table():
	
	# 1  Connects to the database
	#
	db = MySQLdb.connect(user='root', passwd='areek', db='acuity_backup')
	c = db.cursor()
	c.execute("SELECT hotels.HotelName, k_hotels.name, k_hotels.hotel_id FROM hotels, k_hotels WHERE hotels.HotelId=k_hotels.hotel_id")
	hotels = c.fetchall()
	count = 0
	
	# 2  Checks how accurate hotels are based on
	#    (words from smaller string in the larger string) / words in the smaller string
	#
	for a in hotels:
		like = cmp(a[0], a[1])
		
		# 3  Choose how accurent you want to check (0 <= like <= 1)
		#
		if (like != 1):
			print 'test'
			
			# 4  Add whatever code you want to do with the results
			#
			#c.execute("DELETE FROM k_hotels WHERE hotel_id = %s" % a[2])
	print count

def makegraph():

	# Initializers for the function
	#
	days = dates(60)
	db = MySQLdb.connect(user='root', passwd='areek', db='acuity_backup')
	c = db.cursor()
	data = ''
	
	# Loop through all days and find the prices
	#
	for day in days:
		c.execute("SELECT base FROM kayak_prices WHERE kayak_id='32587' AND checkin='%s' ORDER BY base ASC" % day)
		price = c.fetchone()
		if (price != None):
			data += str(price[0]) + ","
		else:
			print 0
			
	print 'http://chart.apis.google.com/chart?cht=lc&chs=500x300&chxt=x,y&chd=' + data

def auto_queries():
	
	# Settings for the queries to output
	#
	length = 60
	length += 1
	days = dates(length)
	hotels = [199674, 23092, 38773, 311523, 198891, 67372, 35032,
		25906, 19648, 198892, 30049, 35508, 30343, 37593, 30378, 23667,
		66092, 30355, 28133, 29139, 32587, 175667, 33404, 35856, 33546,
		163238, 35700, 129297, 258035, 35695, 66202, 193764, 8775, 300246,
		19377, 31699, 38626, 36911, 45047, 61425, 66208, 36558, 35719,
		194486, 12830, 12094, 16010, 199461, 33753, 18934, 66417, 44033,
		315045, 41928, 21080, 16159, 39496, 40296, 8501, 16971]
	requests = []
	
	# Creates a list of queries "length" days into the future for the hotels in the "hotels" array
	#
	for day in range(0, length - 1):
		for hotel in hotels:
			requests.append({'hotel': hotel, 'checkin_date': days[day], 'checkout_date': days[day + 1]})
	
	return requests
		
def find_name(str):
	
	# 1  Cleans the string and splits it into word groups
	#
	cleaned = re.sub(",", " ", str)
	
	cleaned = re.sub("(?i)[^a-z0-9\s]", "", cleaned)
	names = re.split("[0-9]*", cleaned)
	
	
	# 2  Finds the largest substring and returns it
	#
	max = ""
	for name in names:
		if (len(name) > len(max)):
			max = name
	
	
	return max

def find_price(str):

	# Finds the price in the string and returns it if found
	#
	price = re.search("(?<=\$)[0-9]+(\.[0-9]{2})?", str) # $42(.__)
	if (price):
		return price.group()
	else:
		price = re.search("[0-9]+\.[0-9]{2}", str) # 42.00
		if (price):
			return price.group()
		else:
			return False
	
def find_star(str):

	# 1  Normalizes the string for finding the star rating
	#
	str = re.sub("(?i)\s*stars?","*", str) # star(s) -> *
	str = re.sub("(?i)\s*(half)|(1/2)\s*", ".5", str) # (half or 1/2) -> .5
	str = re.sub("(?i)\s*and\s*a?", "", str) # and (a) -> ""
	str = re.sub("(?i)one", "1", str) # one -> 1
	str = re.sub("(?i)two", "2", str) # two -> 2
	str = re.sub("(?i)three", "3", str) # three -> 3
	str = re.sub("(?i)four", "4", str) # four -> 4
	str = re.sub("(?i)five", "5", str) # five -> 5

	# 2  Finds the star rating in the new string and returns it if found
	#
	star = re.search("[0-9]*(\.5)?(?=\*)", str)
	if (star):
		return star.group()
	
	# 3  Checks if its a resort and returns -1 if so
	#
	star = re.search("(?i)resort", str)
	if (star):
		return -1
	else:
		return False

	
if __name__ == "__main__":
	print find_states("Florida and north dakota")