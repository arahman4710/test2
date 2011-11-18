import re
import sys
city = sys.argv[1]

# 1  Open file, reformat it, and find all of the regions variables
#
javascript = open("output/parse.txt", "r").read()
javascript = re.findall("(?s)(\s{3})(.*?)(\n)", javascript)
final = ""

for js in javascript:
	final += js[1]
	
regions = re.findall("(?s){OID:.*?}]}", final)

# 2  Find the region id, city name, region name, and a list of vertices
#
out = ""
if not regions:
	raise Exception()

for region in regions:
	
	regionname = re.search("(?<=name:\").*?(?=\")", region) # based on variable name and quotation
	vertices = re.findall("latitude:([-0-9.]*),longitude:([-0-9.]*)", region) #based on variable and number format
	
	# 3  If everything is found output it
	#
	if regionname:
	
		# 3a  Extract the result of the regular expressions
		#
		regionname = regionname.group()
		open("hw.citytoregion", "a").write("%s HAS %s" % (city, regionname))
		
		out = "#"
		for vertex in vertices:
			# 3b  Output the region and vertices
			#
			out += "%s;0;%s;%s;$" % (regionname, vertex[0], vertex[1])
		out = out[:-1]
		out += "\n"
		open("output/process.txt", "a").write(out)