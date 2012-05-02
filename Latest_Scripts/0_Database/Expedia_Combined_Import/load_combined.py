import re
import string
from hotel_combined import *
from hotel_data import *

def printable(str):
    control = "".join(map(unichr, range(0,127)))
    control = re.escape(control)
    return re.sub("[^%s]" % control, "", str)

na, ct = ('US','CA'), 'countryCode'

def filter_na ():
    x, sp, g = open (combined), ',', {}
    a = x.readline()
    s = map (string.strip,string.split(a,sp))
#    if 1: return s
    idx = {}
    for a in s: idx[a], g[a] = s.index(a), []
    i = s.index (ct)

    for a in x:
        s = map (string.strip,string.split(a,sp))
        if s[i] not in na: continue

        for b in g: g[b].append(s[idx[b]])
    x.close()
    return g

def load_facility ():
    x, sp, g = open (combined_facility), '\t', {}
    a = x.readline()
    s = map (string.strip,string.split(a,sp))

    idx = {}
    for a in s: idx[a], g[a] = s.index(a), []

    for a in x:
        s = map (string.strip,string.split(a,sp))

        for b in g: g[b].append(s[idx[b]])
    x.close()
    return g

def main ():
    y = filter_na ()
    n = len(y[y.keys()[0]])
#    print n
#    n = 1000
    for i in xrange (n):
        g = {}
        g['hotel_name']     = printable(y['hotelName'][i])
        g['address']        = printable(y['address'][i])
        g['city']           = y['cityName'][i]
        g['state_code']     = y['stateName'][i]
        g['country_code']   = y['countryCode'][i]

        x = y['minRate'][i]  
        if x == '': g['min_rate'] = None
        else: g['min_rate'] = x

        x = y['ConsumerRating'][i]  
        if x == '': g['consumer_rating'] = None
        else: g['consumer_rating'] = x

        x = y['rating'][i]  
        if x == '': g['rating'] = None
        else: g['rating'] = x

        g['currency_code']  = y['currencyCode'][i]
        g['latitude']       = y['Latitude'][i]
        g['longitude']      = y['Longitude'][i]
        g['property_type']  = y['PropertyType'][i]
        g['chain_id']       = y['ChainID'][i]
        g['combined_id']    = printable(y['\xef\xbb\xbfhotelId'][i])
        g['hotel_image']    = y['imageId'][i]
        g['Facilities']     = y['Facilities'][i]
                                
        Hotel_Combined (g)

    y = load_facility()
    n = len(y[y.keys()[0]])
#    print n
    for i in xrange(n):
        g = {}
        g['facility_id']   = y['facility_id'][i]
        g['facility_name'] = y['facility'][i]
        g['facility_type'] = y['type'][i]
        Facility_Combined (g)
    return

main ()
x = session.query(Hotel_Combined).filter_by(country_code='CA').first()
print x.hotel_name
print x.hotel_image

