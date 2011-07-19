import re
import MySQLdb
import string

def main():
	db = MySQLdb.connect(user="root", passwd="areek", db="acuity_backup")
	c = db.cursor()

	infile = open("output/hotel_choices").read()
	input = re.split("@", infile)

	print "\n" * 5
	rem = []
	inserted = []
	no_match = []

	for line in input:
		if len(line) > 0:
			hotels = re.split("~", line)
			main = hotels[0]
			[city, region, hotel, star, site, region_id] = re.split(";;", main)
			
			hotels = hotels[1:]
			for i in range(len(hotels)):
				hotels[i] = re.split(";;", hotels[i])
			
			print "\t" + hotel 
			if region != "":
				print "\t" + region
			print "\t" + city
			print 
			print
			
			for i in range(len(hotels)):
				print "   " + str(i + 1) + "\t" + hotels[i][1]
				print "\t" + hotels[i][6]
				if str(hotels[i][2] == "-1"):
					print "\tNEW"
				print

			print 
			print "\t1 to x for hotel choice"
			print "\tn for no match"
			print "\tq to quit (and remove choices from input file)"
			print
	
			response = raw_input("Choice: ")

			while not response in ["q", "n", "s"] + map(str, range(1, len(hotels) + 1)):
				response = raw_input("Invalid option:")

			if response in map(str, range(1, len(hotels) + 1)) and hotels[int(response) - 1][2] != -1:
				c.execute('''INSERT INTO %sid (hotels_hotelid, %sregions_%sregionid, active)
				VALUES ("%s","%s","%s")''' % (site, site, site, hotels[int(response) - 1][0], region_id, 1))
				inserted += [line]
				rem += [line]

				
			elif response == "q":
				break
					
			elif response == "n":
				no_match += [line]
				rem += [line]
				
			print "\n" * 10
	
	print infile
	for line in rem:
		print len(infile)
		infile = string.replace(infile, line, "")
		print len(infile)
		infile = re.sub("@{2,}", "@", infile)
		infile = re.sub("(^@)|(@$)", "", infile)
		open("output/hotel_choices", "w").write(infile)
		
		open("output/inserted", "a").write("@".join(inserted))
		open("output/no_match", "a").write("@".join(no_match))
			
if __name__ == "__main__":
	main()