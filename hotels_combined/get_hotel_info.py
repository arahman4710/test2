import sys

# should be changed to reflect current location for the hotwire sqlalchemy tables 
sys.path.insert(0, "/home/jefu/fetch/scraping/hotwire_api/hotwire_api/hotwire_api/spiders/")

from hotwire_tables import *
from canon_hotel import *

import csv 

# convenience to map names from csv headers into the names used in the table.

namesdict = {
    'hotelId':'hotel_id',
    'hotelFileName':'hotel_filename',
    'hotelName':'hotel_name',
    'rating':'rating',
    'cityId':'city_id',
    'cityFileName':'city_filename',
    'cityName':'city_name',
    'stateId':'state_id',
    'stateFileName':'state_filename',
    'stateName':'state_name',
    'countryCode':'country_code',
    'countryFileName':'country_filename',
    'countryName':'country_name',
    'imageId':'image_id',
    'address':'address',
    'minRate':'min_rate',
    'currencyCode':'currency_code',
    'Latitude':'Latitude',
    'Longitude':'Longitude',
    'NumberOfReviews':'number_of_reviews',
    'ConsumerRating':'consumer_rating',
    'PropertyType':'property_type',
    'ChainID':'chain_id',
    'Facilities':'facilities'
    }


# reads a csv file from hotelscombined.net (currently the standard table, not the advanced one)
# and uses that to populate the tables in canon_hotel
# pretty simple stuff - the only problem might be missing fields
#
# currently it is also set up to ignore a hotel listing if we have the id already in the table.
# this will have to be removed or set to do an update if we're reloading.  

def main() :    
    if len(sys.argv) < 1 : 
        print "Usage:",sys.argv[0], "csv_filename"
        print "Don't forget to remove the byte order mark (?) before hotelID or"
        print "   all the hotelId entries will contain that " 
        sys.exit(1)

    csvreader = csv.DictReader(open(sys.argv[1])) 
    for d in csvreader :
        if d['countryCode'] == 'US' or d['countryCode'] == 'CA' : 
            match = get_hotel_by_id(d['hotelId']) 
            if match :  # we have it - eventually this needs to do an update on stuff that changes 
                print "skipping hotel id=", d['hotelId'] 
                continue 
            print d 
            nd = {} 
            for i in namesdict.items() :
                nd[i[1]] = d[i[0]] 

            nd.__delitem__('Latitude')
            nd.__delitem__('Longitude')
            p = None 
            if d['Latitude'] != '' : 
                p = find_point(d['Latitude'], d['Longitude'])
            else :
                p = find_point(1000, 1000)

            nd['location'] = p.uid 

            nd['facilities_list'] = find_facilities_list(d['Facilities']).uid 
            if d['minRate'] != '' : 
                nd['min_rate'] = float(d['minRate']) 
            else :
                nd['min_rate'] = -1

            hotel = CanonicalHotel(nd)            

main()

