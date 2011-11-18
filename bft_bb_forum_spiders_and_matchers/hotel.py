# Imports related to Scrapy
#
import os
import htmlentitydefs
os.environ.setdefault("SCRAPY_SETTINGS_MODULE", "project.settings")

from scrapy.conf import settings
from scrapy.crawler import CrawlerProcess
from scrapy.xlib.pydispatch import dispatcher
from scrapy import log, signals, project
from multiprocessing import Process, Queue
from threading import Thread


from scrapy.spider import BaseSpider


# General Imports 
#
import MySQLdb
import re
import difflib

class Connection(): ###
	database = MySQLdb.connect(user='root', passwd='areek', db='acuity_backup')
	cursor = database.cursor()

def num(val):
	try:
		float(val)
		return True
	except:
		return None


class States(Connection):
	cursor = Connection.cursor
	states = ["Alabama", "Alaska", "Arizona", "Arkansas",
			  "California", "Colorada", "Connecticut", "Delaware",
			  "Florida", "Georgia", "Hawaii", "Idaho", "Illinois",
			  "Indiana", "Iowa", "Kansas", "Kentucky", "Louisiana",
			  "Maine", "Maryland", "Massachusetts", "Michigan",
			  "Minnesota", "Mississippi", "Missouri", "Montana",
			  "Nebraska", "Nevada", "New Hampshire", "New Jersey",
			  "New Mexico", "New York", "North Carolina",
			  "North Dakota", "Ohio", "Oklahoma", "Oregon",
			  "Pennsylvania", "Rhode Island", "South Carolina",
			  "South Dakota", "Tennessee", "Texas", "Utah",
			  "Vermont", "Virginia", "Washington", "West Virginia",
			  "Wisconsin", "Wyoming"]
			  		  
	def fast_state_match(self, val):
		states = map(lambda x: x.lower(), self.states)
		val = val.lower()
		
		for state in states:
			if state == val:
				return val
		return None
			
	def state_match(self, val):
		fast = self.fast_state_match(val)
		if not fast:
			best = [0, ""]
			for state in self.states:
				matcher = difflib.SequenceMatcher(None, state, val)
				rat = matcher.ratio()
				
				if rat > best[0]:
					best = [rat, state]
					
			if best[0] > 0.8:
				return best[1]
			else:
				return None
		else:
			return fast.capitalize()
	
	def find_states(self, val):
		state = self.state_match(val)
		if state:
			return [state]
		elif self.cursor.execute('''SELECT * FROM cities'''):
			cities = self.cursor.fetchall()
			best = [0, []]
			for city in cities:
				s = difflib.SequenceMatcher(None, val, city[1])
				r = s.ratio()
				if r > best[0]:
					best = [r, city]
			if best[0] > 0.9:
				return [best[1][2]]
		
		letter = re.search("(?i)(.)\s+states", val)
		if letter:
			letter = letter.group(1)
			return filter(lambda x: x.lower().startswith(letter.lower()), self.states)
		
		return []
	
	def find_state(self, val):
		states = self.find_states(val)
		if states:
			return states[0]
		return None
	
class CSV():
	def pack(self, array, delimiter):
		array = map(str, array)
		array = map(lambda x: re.sub(r"(\%s)" % delimiter, r"\\\1", x), array)
		return delimiter.join(array)
		
	def unpack(self, str, delimiter):
		str = re.split(r"(?<!\\)\%s" % delimiter, str)
		str = map(lambda x: re.sub(r"\\(\%s)" % delimiter, r"\1", x), str)
		return str
	
	def unentify(self, str):
		def repl(w):
			w = w.group(1)
			e = htmlentitydefs.entitydefs
			if w in e.keys():
				return e[w]
			else:
				return ""
		return re.sub("&(\w+);", repl, str)
	
	def delnewlines(self, str):
		return re.sub("\\n", "", str)
		
	def prepare(self, str):
		return self.delnewlines(self.unentify(str))
	
	
# Classes for hotels and matching
#
class Rating(): ###
	def __init__(self, rating=None):
		self.rating = rating
	
	def __setattr__(self, rating, val):
		try:
			self.__dict__["rating"] = float(rating)
		except:
			self.__dict__["rating"] = None			
	
	def __eq__(self, other):
		assert other.__class__.__name__ == "Rating"
		
		if self.rating \
		and other.rating:
			diff = abs(self.rating - other.rating)
			
			if diff == 0: return 1
			elif diff == 0.5: return 0.9
			elif diff == 1: return 0.7
			elif diff == 1.5: return 0.4
			elif diff == 2: return 0.1
			else: return 0
			
		return 0

class LatLng():
	def __init__(self, latlng=None):
		if latlng.__class__.__name__ == "dict" \
		and 'latitude' in latlng.keys() \
		and 'longitude' in latlng.keys():
			self.latitude = latlng['latitude']
			self.longitude = latlng['longitude']
		else:
			self.latitude = None
			self.longitude = None
		
	def __eq__(self, other):
		# If both latlng's are valid calculate the Manhattan distance
		#
		assert other.__class__.__name__ == "LatLng"
		
		if self.longitude and other.longitude \
		and self.latitude and other.latitude:
			dist = self.manhattan(self, other)
			
			# Return 1 if latlng's are within a few blocks
			# Return some number below one otherwise
			#
			if dist < 0.01: return 1
			elif dist < 0.02: return 0.8
			elif dist < 0.04: return 0.5
			elif dist < 0.08: return 0.2
		
		return 0

	def manhattan(self, other):
		return (self.latitude - other.latitude) \
			 + (self.longitude - other.longitude)
			
	def euclidean(self, other):
		return ((self.latitude - other.latitude) ** 2 \
			  + (self.longitude - other.longitude) ** 2) ** 0.5
				
class Phone(): ###
	def __init__(self, phone=None):
		self.number = phone
		
	def __setattr__(self, number, val):
		nums = ""
		for char in str(phone):
			if ord(char) <= 57 and ord(char) >= 48:
				nums += char
		self.__dict__["number"] = nums
	
	def __eq__(self, other):
		assert other.__class__.__name__ == "Phone"
		
		if self.number and other.number:
			s = difflib.SequenceMatcher(None, self.number, other.number)
			return s.ratio()
		return 0
		
class City(Connection):
	Connection.cursor
	
	def __init__(self, id=None, city=None, state=None, country=None):
		# Initialize all needed variables (incase it isn't done elsewhere)
		self.id = id
		self.city = city
		self.state = state
		self.country = country
		
		# 1  Find a city based on ID
		#
		if id:
			# Assert because cityid should only be input from valid sources from our db
			# If the city can't be found the only explanation should be a broken foreign key
			assert self.cursor.execute("SELECT * FROM cities WHERE cityid=%s" % id)
			info = self.cursor.fetchone()
			self.id = id
			self.city = info[1]
			self.state = info[2]
			self.country = info[3]
		elif city and state and country:
			# 2  Find a city based on exact city and state
			#
			if self.cursor.execute("SELECT * FROM cities WHERE city='%s' AND state='%s'" % (city, state)):
				info = self.cursor.fetchone()
				self.id = info[0]
				self.city = info[1]
				self.state = info[2]
				self.country = info[3]
			# 3  Find a city based on exact state and rough city (atleast 80% similarity)
			#
			elif self.cursor.execute("SELECT * FROM cities WHERE state='%s'" % state):
				best = [0,[]]
				results = self.cursor.fetchall()
				# Accumulate the best match
				for place in results:
					s = SequenceMatcher(None, place[1], city)
					rat = s.ratio()
					if rat > best[0]:
						best = [rat, place]
				# If the match is good enough set it
				if best[0] > 0.8:
					info = best[1]
					self.id = info[0]
					self.city = info[1]
					self.state = info[2]
					self.country = info[3]
				
	def __eq__(self, other):
		assert other.__class__.__name__ == "City"
		
		if self.id and other.id \
		and other.id == self.id:
			return 1
		
		return 0

class String():
	def __init__(self, string=None):
		if string:
			string = str(string)
		else:
			string = ""
		self.string = string
		
		self.string = string
		
	def __eq__(self, other):
		assert other.__class__.__name__ == "String"
		
		if self.string and other.string:
			# Strip the strings and prepare for comparisons
			#
			str1 = re.sub("[^a-z0-9\s]+", "", self.string.lower())
			str1 = re.split("[^a-z0-9]+", str1)
			str2 = re.sub("[^a-z0-9\s]+", "", other.string.lower())
			str2 = re.split("[^a-z0-9]+", str2)

			cmp = 0
			
			# Iterate through and find the best match for each part in the first string
			#
			if len(str1) > len(str2):
				tmp = str1
				str1 = str2
				str2 = tmp
			
			for w1 in str1:
				best = ["", 0]
				
				for w2 in str2:
					s = difflib.SequenceMatcher(None, w1, w2)
					r = s.ratio()
					if r > best[1]:
						best = [w1, r]
				
				# If it's a number and the match is good, half its % difference to 1
				#
				if num(best[0]) and best[1] > 0.6:
					best[1] = (1 + best[1]) / 2
					
				cmp += best[1]
				
			
			# 3  Calculates the total match / average length of the strings
			#
			return float(cmp) / ((float(len(str1)) + float(len(str2))) / 2)
		return 0
		
class Hotel(Connection): ###
	Connection.cursor

	def __init__(self, id=None, name=None, address=None, city=None, phone=None, latlng=None, rating=None):
		self.id = id
		self.name = name
		self.address = address
		self.city = city
		self.phone = phone
		self.latlng = latlng
		self.rating = rating

	def __setattr__(self, id, val):
		self.__dict__["id"] = self.intify(val)
	def __setattr__(self, name, val):
		self.__dict__["name"] = String(val)
	def __setattr__(self, address, val):
		self.__dict__["address"] = String(val)
	def __setattr__(self, city, val):
		self.__dict__["city"] = City(val)
	def __setattr__(self, phone, val):
		self.__dict__["phone"] = Phone(val)
	def __setattr__(self, latlng, val):
		self.__dict__["latlng"] = LatLng(val)
	def __setattr__(self, rating, val):
		self.__dict__["rating"] = Rating(rating)
		
	def __eq__(self, other):
		# Compare each part of the hotel and add its result to an array
		#
		compares = []
		compares.append([self.compare_id(other), 1])
		compares.append([self.name == other.name, 1])
		compares.append([self.address == other.address, 1])
		compares.append([self.city == other.city, 1])
		compares.append([self.phone == other.phone, 1])
		compares.append([self.latlng == other.latlng, 1])
		compares.append([self.rating == other.rating, 1])
		
		total = 0
		cnt = 0
		
		# First value is the ratio, second value is 
		#
		for a in compares:
			if a[0]:
				total += a[0] * a[1]
				cnt += a[1]
		
		return float(total) / float(cnt)

	def intify(self, num):
		try:
			int(num)
			return num
		except:
			return None
	
	def compare_id(self, other):
		assert other.__class__.__name__ == "Hotel"
	
		if self.id and other.id \
		and self.id == other.id:
			return 1
		else:
			return 0

if __name__ == "__main__":
	pass