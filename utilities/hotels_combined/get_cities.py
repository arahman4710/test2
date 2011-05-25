import sys
import codecs 

# not a scraper, so in utilities 
# should be changed to reflect current location for the hotwire sqlalchemy tables 
sys.path.insert(0, "/work/jeff/backend/sql/alchemy")

from point import Point, find_point
from hotwire_tables import *
from city_locations import *


import csv 

# convenience to map names from csv headers into the names used in the table.

namesdict = {
    'CityID':'uid',
    'CityFileName':'city_filename',
    'CityName':'city_name',
    'StateID':'state_id',
    'StateFileName':'state_filename',
    'StateName':'state_name',
    'CountryCode':'country_code',
    'CountryFileName':'country_filename',
    'CountryName':'country_name',
    'CityCenterLatitude':'CityCenterLatitude', 
    'CityCenterLongitude':'CityCenterLongitude'
} 


# reads a csv file from hotelscombined.net (currently the standard table, not the advanced one)
# and uses that to populate the tables in canon_hotel
# pretty simple stuff - the only problem might be missing fields
#
# currently it is also set up to ignore a hotel listing if we have the id already in the table.
# this will have to be removed or set to do an update if we're reloading.  

def main() :    
    if len(sys.argv) < 2 : 
        print "Usage:",sys.argv[0], "csv_filename"
        sys.exit(1)

    f = open(sys.argv[1])
    h = f.read(3)
    if h[0] != chr(0xef) : # seen byte order mark, we're good 
        print "did not get byte order mark, resetting" 
        f.close()
        f = open(sys.argv[1]) 

    csvreader = csv.DictReader(f) 
    for d in csvreader :
        # only take cities in the US or Canada 
        if d['CountryCode'] == 'US' or d['CountryCode'] == 'CA' :
            nd = {}
            for i in d :
                nd[namesdict[i]] = d[i]
            p = None 
            if d['CityCenterLatitude'] != '' : 
                p = find_point(d['CityCenterLatitude'], d['CityCenterLongitude']) 
            else :
                p = find_point(1000,1000) 
            nd['city_center_location'] = p.uid 
            nd.__delitem__('CityCenterLatitude')
            nd.__delitem__('CityCenterLongitude')
            res = HC_City(nd)

main()
