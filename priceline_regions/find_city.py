import MySQLdb
import re
import sys
import difflib

class States():
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
			  
	def fast_match(self, val):
		states = map(lambda x: x.lower(), self.states)
		val = val.lower()
		
		for state in states:
			if state == val:
				return val
		return None
			
	def match(self, val):
		fast = self.fast_match(val)
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
			
def main():
	db = MySQLdb.connect(user='root', passwd='areek', db='acuity_backup')
	c = db.cursor()

	city = sys.argv[1]
	city = re.sub("[^a-zA-Z\s]", " ", city)
	city = re.sub("\s{2,}", " ", city)
	city = city.strip()
	
	state = sys.argv[2]
	state = re.sub("[^a-zA-Z\s]", " ", state)
	state = re.sub("\s{2,}", " ", state)
	state = state.strip()
	state = States.match(States(), state)
	
	
	if state:
		failed = 0
		c.execute('''SELECT cityid FROM cities WHERE city="%s" AND state="%s"''' % (city, state))
		r = c.fetchone()

		if r:
			output = str(r[0])
		else:
			c.execute('''INSERT INTO cities (city, state, country) VALUES ("%s", "%s", "%s")''' % (city, state, 'United States'))
			c.execute("SELECT max(cityid) FROM cities")
			output = str(c.fetchone()[0])
	else:
		failed = 1
		output = ""
	
	open("output/city_id.txt", "w").write(output)
	
	# If the matching failed raise and exception so Ruby knows to output to the error log
	#
	if failed:
		raise
	
	
	
if __name__ == "__main__":
	main()