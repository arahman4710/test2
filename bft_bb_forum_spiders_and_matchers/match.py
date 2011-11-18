import re
import MySQLdb
from difflib import SequenceMatcher
import copy
import sys

# Functions to get a bunch of items from our database to process through
#
def get_regions(state, site):

	# Return a list of regions for a certain state in either our hotwire or priceline records
	#
	db = MySQLdb.connect(user="root", passwd="areek", db="acuity_backup")
	c = db.cursor()

	c.execute("SELECT %sregionid, regionname FROM %sregions WHERE cities_cityid IN (SELECT cityid FROM cities WHERE state IN (%s))" % (site, site, state))
	regions = c.fetchall()
	
	return regions

def get_points(state, site):
	# Return a list of points for a certain state in either our hotwire or priceline records
	#
	db = MySQLdb.connect(user="root", passwd="areek", db="acuity_backup")
	c = db.cursor()
	
	c.execute('''SELECT %spoints.latitude, %spoints.longitude, %sregions.%sregionid, %sregions.regionname FROM %spoints, %sregions
				 WHERE %sregions.%sregionid = %spoints.%sregions_%sregionid AND (SELECT state FROM cities WHERE cityid = %sregions.cities_cityid) IN (%s)
				 ORDER BY pointid''' % ((site,) * 13 + (state,)))
	points = c.fetchall()
	
	return points
	
def get_site_hotels(state, site):

	# Return a list of hotels for a certain state in either our hotwire or priceline records
	#
	db = MySQLdb.connect(user="root", passwd="areek", db="acuity_backup")
	c = db.cursor()

	c.execute("SELECT %sid.%sregions_%sregionid, %sid.%sid, hotels.hotelid, hotels.hotelname FROM hotels, %sid WHERE hotels.cities_cityid IN (SELECT cityid FROM cities WHERE state IN (%s)) AND hotels.hotelid IN (SELECT hotels_hotelid FROM %sid)" % (site, site, site, site, site, site, state, site))
	site_hotels = c.fetchall()
	
	return site_hotels
	
def get_state_hotels(state):

	# Return a list of regions and hotels for a certain state in either our hotwire or priceline records
	#
	db = MySQLdb.connect(user="root", passwd="areek", db="acuity_backup")
	c = db.cursor()

	c.execute("SELECT hotelid, hotelname, latitude, longitude FROM hotels WHERE cities_cityid IN (SELECT cityid FROM cities WHERE state IN (%s))" % state)
	return c.fetchall()
	
def get_ids(hotels, site):
	db = MySQLdb.connect(user="root", passwd="areek", db="acuity_backup")
	c = db.cursor()
	
	for i in range(len(hotels)):
		c.execute("SELECT pricelineid FROM pricelineid WHERE hotels_hotelid='%s'" % hotels[i][0])
		id = c.fetchone()
		if id:
			hotels[i] += (id[0],)
		else:
			hotels[i] += (-1,)
	
	return hotels

# Functions to accumulate a list of possible matches
#
def acc_lst(new, lst, num):
	i = 0
	flag = 0
	
	while i < len(lst):
		if new[0] > lst[i][0]:
			lst.insert(i, new)
			flag = 1
			break
		i += 1
		
	if not flag:
		lst += [new]
		
	while len(lst) > num:
		lst.pop()
		
	return lst

def acc_regions(region_name, regions):
	out = []

	for region in regions:
		cur = a_in_b(region_name, region[1])
		if cur[0] > 0.5:
			acc_lst([cur[0], cur[1], region], out, 1)
	
	out = map(lambda x: x[1:], out)
	return out

def acc_hotels(hotel_name, city_name, region_name, hotels):
	out = []
	
	for hotel in hotels:
		hotel_match = a_in_b(hotel_name, hotel[1])
		city_match = a_in_b(city_name, hotel[1])
		region_match = a_in_b(region_name, hotel[1])
		if hotel_match[0] >= 0.5 \
		and (city_match[0] >= 0.5 \
			or region_match[0] >= 0.25):
			acc_lst([hotel_match[0], hotel], out, 5)
	
	out = map(lambda x: x[1], out)
	return out
	
	
# Functions to help with matching
#
def strip(orig, words):
	for word in words:
		orig = re.sub("(?i)%s" % word, " ", orig)
	orig = re.sub("\s{2,}", " ", orig)
	
	return orig
	
def a_in_b(a, b):

	# 1  Splits the strings into individual words
	#
	a = re.split("[^a-z]*", a.lower())
	b = re.split("[^a-z]*", b.lower())
	
	# 2  Calculates probability of match by:
	#    (best ratio of str1 found in str2) / number of words in str1
	#
	ratio = 0
	words = []
	cmp = 0
	
	for w1 in a:
		best = ["", 0]
		
		for w2 in b:
			s = SequenceMatcher(None, w1, w2)
			r = s.ratio()
			if r > best[1] and r > 0.8:
				best = [w2, r]
		
		words += [best[0]]
		cmp += best[1]
		
	
	# 3  Rounds off the value and returns it
	#
	return [round(float(cmp) / float(len(a)), 2), words]

def find_region(p, points):
	cur_points = []
	last_id = -1
	last_region = ""
	
	for point in points:
		if not point[2] == last_id:
			if in_region(p, cur_points):
				return (last_id, last_region)
				
			cur_points = [point]
			last_id = point[2]
			last_region = point[3]
		else:
			cur_points += [point]
	
	return (-1, "No region match")
	
def in_region(p, points):
	cnt = 0
	points = map(lambda x: [x[0], x[1]], points)
	p = [p[2], p[3]]

	for edge in edges(points):
		if cross(p, edge):
			cnt += 1
			
	return cnt % 2
	
def cross(p, edge):
	_eps = 0.00001
	_huge = sys.float_info.max
	_tiny = sys.float_info.min

	a,b = edge
	if a[1] > b[1]:
		a,b = b,a
	if p[1] == a[1] or p[1] == b[1]:
		p = [p[0], p[1] + _eps]

	intersect = False

	if (p[1] > b[1] or p[1] < a[1]) or (
		p[0] > max(a[0], b[0])):
		return False

	if p[0] < min(a[0], b[0]):
		intersect = True
	else:
		if abs(a[0] - b[0]) > _tiny:
			m_red = (b[1] - a[1]) / float(b[0] - a[0])
		else:
			m_red = _huge
		if abs(a[0] - p[0]) > _tiny:
			m_blue = (p[1] - a[1]) / float(p[0] - a[0])
		else:
			m_blue = _huge
		intersect = m_blue >= m_red
	return intersect

def edges(points):
	if len(points) > 2:
		for i in range(len(points) - 1):
			yield [points[i], points[i + 1]]
		yield [points[0], points[-1]]



# Main matching functions for hotels
#
def match_hotel(hotel, regions, state_hotels, points, site):
	
	# If there is no region, set it equal to the city
	#
	if hotel[1] == "":
		hotel[1] = hotel[0];
	
	#  Match the region with the list (currently only matches one region), and strip that info from the hotel name
	#
	r1 = acc_regions(hotel[1], regions) # Matching region by region
	r2 = acc_regions(hotel[0], regions) # Matching region by city
	if r1:
		matched_region = r1[0][1]
		region_words = r1[0][0]
	elif r2:
		matched_region = r2[0][1]
		region_words = r2[0][0]
	else:
		return []
		
	stripped = strip(hotel[2], region_words)
	
	#  Accumulate a list of possible hotels matching both the region and the hotel
	#
	state_hotels = acc_hotels(stripped, hotel[0], hotel[1], state_hotels)
	state_hotels = get_ids(state_hotels, site)
	for i in range(len(state_hotels)):
		state_hotels[i] += find_region(state_hotels[i], points)
	
	return [hotel + [site, matched_region[0]]] + state_hotels

	

if __name__ == "__main__":
	print "Do not run from main program"
	points = [[0,0],[0,5],[5,5],[5,0]]
	
	p = [10, 5]
	cnt = 0
	
	for edge in edges(points):
		print edge