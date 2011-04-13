import MySQLdb

db = MySQLdb.connect(user="root", passwd="charles", db="acuity")
c = db.cursor()
c.execute("SELECT city, state FROM cities WHERE cityid IN (SELECT DISTINCT cities_cityid FROM pricelineregions)")
rows = c.fetchall()

dbcities = []
for row in rows:
	dbcities.append("%s, %s" % (row[0], row[1]))

open("found_cities", "w").write("\n".join(dbcities))