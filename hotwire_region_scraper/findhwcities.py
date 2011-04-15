import httplib
import re
import sys

# 1  Connects to the hotwire cities page
#
c = httplib.HTTPConnection("www.hotwire.com")
c.request("GET", "http://www.hotwire.com/pop-up/hotelDestinations.jsp")
page = c.getresponse()
page = page.read()
links = re.findall("(?is)>[^<>]*?</a>", page)
output = ""

for link in links:

	# 2  Checks if the link is in the city format (includes a , somewhere)
	#
	if (re.search(",", link)):
		city = re.search("(?<=>)[^<>]*?(?=<)", link)
		
		if (city):
			output += city.group() + ";"
			
open(sys.argv[1], "w").write(output[:-1])