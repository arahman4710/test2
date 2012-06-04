import sys
import re
import MySQLdb

# 1  Open file and determine what to accept (do all, do specific, or invalid args)
#
input = open("output/pointchanges.txt", "r").read()
lines = re.split("\n", input)
toDo = []
for arg in sys.argv[1:]:
	if arg == "all":
		toDo = range(1, len(lines))
		continue
	elif re.match("^[0-9]+$", arg):
		if 1 <= int(arg) <= len(lines):
			toDo += [int(arg)]
		else:
			raise Exception("Index out of list range")
	else:
		raise Exception("Invalid argument, all arguments must be numeric")


# 2  Initialize the database connection
#
db = MySQLdb.connect(user='root', passwd='charles', db='acuity')
c = db.cursor()

# 3  Go through the items to be accepted and insert them
#    At the same time remove them from the input
#
for Do in toDo:
	points = re.split("\$", lines[Do - 1])
	
	# 3a  Delete all old points for the current city, error if no city is found in hotwire regions
	#
	city = (re.split(";", points[0]))[0]
	c.execute("SELECT hotwireregionid FROM hotwireregions WHERE regionname = '%s'" % city)
	cityid = c.fetchone()
	if cityid:
		cityid = cityid[0]
		c.execute("DELETE FROM hotwirepoints WHERE hotwireregions_hotwireregionid = '%s'" % cityid)
		input = re.sub("\s*%s\s*" % lines[Do - 1], "", input)
	else:
		raise Exception("The city corresponding to those points cannot be found in the table")
	
	
	# 3c  Insert all the new points into the database
	#
	for point in points:
		point = re.split(";", point)
		c.execute("INSERT INTO hotwirepoints (hotwireregions_hotwireregionid, order, latitude, longitude) VALUES ('%s','%s','%s','%s')" % (cityid, order, point[1], point[2]))
		max += 1
		order += 1

# 4  Commit the changes to the database and update the changes text file
#
open("output/pointchanges.txt", "w").write(input)
db.commit()