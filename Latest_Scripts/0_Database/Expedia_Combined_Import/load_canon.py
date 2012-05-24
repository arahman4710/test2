import re
import string
from canon_hotel import *
from hotel_data import *

def printable(str):
    control = "".join(map(unichr, range(0,127)))
    control = re.escape(control)
    return re.sub("[^%s]" % control, "", str)

na, ct = ('US','CA'), 'Country'

def filter_na ():
    x, sp, g = open (expedia), '|', {}
    a = x.readline()
    s = map (string.strip,string.split(a,sp))

    idx = {}
    for a in s: idx[a], g[a] = s.index(a), []
    i = s.index (ct)
    for a in x:
        s = map (string.strip,string.split(a,sp))
        if s[i] in na:
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
        g['hotel_name']     = printable(y['Name'][i])
        g['address']        = printable(y['Address1'][i])
        g['city']           = y['City'][i]
        g['state_code']     = y['StateProvince'][i]
        g['country_code']   = y['Country'][i]
        g['postal_code']    = y['PostalCode'][i]
        g['currency_code']  = y['NativeCurrency'][i]
        g['latitude']       = y['Latitude'][i]
        g['longitude']      = y['Longitude'][i]
        g['property_type']  = y['PropertyType'][i]
        g['chain_name']     = y['GDSChaincodeName'][i]
        g['check_in']       = y['CheckInTime'][i]
        g['check_out']      = y['CheckOutTime'][i]
        g['status']         = 'expedia'
        g['expedia_id']     = y['HotelID'][i]
        g['combined_id']    = None
        CanonicalHotel (g)

    return

main ()
x = session.query(CanonicalHotel).filter_by(country_code='CA').first()
print x.hotel_name
print x.check_in


