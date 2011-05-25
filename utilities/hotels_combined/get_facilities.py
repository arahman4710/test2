import sys
import codecs 

# not a scraper, so in utilities 
# should be changed to reflect current location for the hotwire sqlalchemy tables 
sys.path.insert(0, "/work/jeff/backend/sql/alchemy")

from facilities import *

import csv 

def main() :
    if len(sys.argv) < 2 :
        print "Usage : %s csv-filename" % sys.argv[0] 
        exit(0) 

    f = open(sys.argv[1])
    h = f.read(3)
    if h[0] != chr(0xef) : # seen byte order mark, we're good 
        print "did not get byte order mark, resetting" 
        f.close()
        f = open(sys.argv[1]) 
    cr = csv.reader(f)
    cr.next() # skip headers 
    for l in cr : 
        entry = Facility(int(l[0]), l[1]) 


main()
