import MySQLdb
import re
import sys

db = MySQLdb.connect(user='root', passwd='charles', db='acuity')
c = db.cursor()

city = sys.argv[1]
city = re.sub("[^a-zA-Z\s]", "", city)
city = city.strip()
state = sys.argv[2]
state = state.strip()
state = re.sub("[^a-zA-Z\s]", "", state)

c.execute("SELECT cityid FROM cities WHERE city=\"%s\" AND state=\"%s\"" % (city, state))
r = c.fetchone()
if r:
	open("output/city_id.txt", "w").write(str(r[0]))
else:
	c.execute("INSERT INTO cities (city, state, country) VALUES (\"%s\", \"%s\", \"%s\")" % (city, state, 'United States'))
	c.execute("SELECT max(cityid) FROM cities")
	city_id = c.fetchone()[0]
	open("output/city_id.txt", "w").write(str(city_id))