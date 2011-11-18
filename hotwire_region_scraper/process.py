import MySQLdb
import re
import time

# Input is in the format "region;id;latitude;longitude"
# Line are separated by $
# Cities are separated by #


# 1  Open the file and split into cities, initialize the mysql connection
#
input = open("output/process.txt", "r").read()
input = input[1:]
regions = re.split("#", input)
db = MySQLdb.connect(user='root', passwd='charles', db='acuity')
c = db.cursor()
city = open("output/city_id.txt", "r").read()

if not regions:
	raise Exception()

# 2  Iterate through the cities and lines
#    Skip the first city and last line because of formatting of input (they're empty)
#
for region in regions:

	# 3  Initialize necessary variables and perform required splits
	#
	region = region[:-1]
	lines = re.split("\$", region)
	vars = re.split(";", lines[0])
	for index in range(0, len(lines)):
		lines[index] = re.split(";", lines[index])
	lines = lines[1:]
	
	# 4  Check if the region is already in the database and has changed, output a notice if so
	#    Otherwise adds the new region to the database, and outputs a notification
	#
	c.execute("SELECT * FROM hotwireregions WHERE regionname = \"%s\"" % vars[0])
	region = c.fetchone()
	if region:
		if not (round(float(vars[2]), 3) == round(float(region[2]), 3) and round(float(vars[3]), 3) == round(float(region[3]), 3)):
			open("output/citychanges.txt", "a").write("%s;%s;%s\n" % (vars[0], vars[2], vars[3]))
		regionid = region[0]
	else:
		c.execute("INSERT INTO hotwireregions (regionname, cities_cityid, latitude, longitude, active) VALUES (\"%s\",\"%s\",\"%s\",\"%s\",\"%s\")" % (vars[0], city, vars[2], vars[3], 1))
		c.execute("SELECT hotwireregionid FROM hotwireregions WHERE regionname=\"%s\" AND active='1'" % vars[0])
		regionid = c.fetchone()
		regionid = regionid[0]
		open("output/cityadditions.txt", "a").write("%s;%s;%s\n" % (vars[0], vars[2], vars[3]))
	
	
	# 6  Check if there's a new set of points or not, if so insert the new ones
	#    Compare each point in order, and compare the lengths
	#
	c.execute("SELECT * FROM hotwirepoints WHERE hotwireregions_hotwireregionid = '%s'" % regionid)
	points = c.fetchall()
	diff = False
	if len(points) == len(lines):
		for a in range(0, len(points)):
			if not (round(points[a][3], 3) == round(float(lines[a][2]), 3)):
				diff = True
				break
	
	if diff == True:
		# 6a  Accumulate the list of changes
		#
		output = ""
		for line in lines:
			output += "%s;%s;%s$" % (line[0], line[2], line[3])
		
		# 6b  Remove the final $ from the string and add a newline
		#
		output = output[:-1]
		output += "\n"
		open("output/pointchanges.txt", "a").write(output)
		
	elif len(points) == 0:
		
		# 6c  Inserts the new points into the hotwire points table
		#
		order = 0
		output = ""
		for line in lines:
			c.execute("INSERT INTO hotwirepoints (hotwireregions_hotwireregionid, orderid, latitude, longitude) VALUES ('%s','%s','%s','%s')" % (regionid, order, line[2], line[3]))
			order += 1
			output += "%s;%s;%s;%s\n" % (regionid, order, line[2], line[3])
		open("output/pointadditions.txt", "a").write(output)
	output = ""
	