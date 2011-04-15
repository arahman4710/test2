import sys
import re
import MySQLdb

# 1  Open file and determine what to accept (do all, do specific, or invalid args)
#
input = open("output/citychanges.txt", "r").read()
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
	
	# 3a  Delete the update request in the input file and update the table
	#
	input = re.sub("\s*%s\s*" % lines[Do - 1], "", input)
	line = re.split(";", lines[Do - 1])
	c.execute("UPDATE pricelineregions SET latitude = '%s', longitude = '%s' WHERE regionname = '%s'" % (line[2], line[3], line[0]))
	
	
# 4  Commit the changes to the database and update the changes text file
#
open("output/citychanges.txt", "w").write(input)
db.commit()