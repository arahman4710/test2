from hotel_data import *
from BeautifulSoup import BeautifulStoneSoup
from hotel_expedia import *
import re

def printable(str):
    control = "".join(map(unichr, range(0,127)))
    control = re.escape(control)
    return re.sub("[^%s]" % control, "", str)

na, ct = ('US','CA'), 'Country'
fn, sp = expedia, '|'
def filter_na ():
    x, g = open (expedia), {}
    a = x.readline()
    s = map (string.strip,string.split(a,sp))

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
    x, sp, g = open (expedia_facility), '\t', {}
    a = x.readline()
    s = map (string.strip,string.split(a,sp))

    idx = {}
    for a in s: idx[a], g[a] = s.index(a), []

    for a in x:
        s = map (string.strip,string.split(a,sp))

        for b in g: g[b].append(s[idx[b]])
    x.close()
    return g
def table_facility ():
    x, sp, g = open (expedia_facility), '\t', {}
    a = x.readline()
    s = map (string.strip,string.split(a,sp))

    g = {}
    for a in x:
        s = map (string.strip,string.split(a,sp))

        g[s[1]] = s[0]
    x.close()
    return g
'''
g = table_facility()
for a in g: print a, g[a]

x = filter_na()
print len(x[x.keys()[0]])
'''

def parse_desc (s):
    p, q, r, t = '', '', '', ''
    soup = BeautifulStoneSoup(printable (s))
    a = soup.findAll ('b')
    b = soup.findAll ('br')
    c = soup.findAll ('strong')
    if len(a) == 0: return p,q,r,t
    if len(a) == 1:
        if 'Locat' in a[0].contents[0]: p = b[0].contents[0]
    if len(a) == 3:
        if len(b[0]): p = b[0].contents[0]
        if len(b[1]): q = b[1].contents[0]
        if len(b[2]): r = b[2].contents[0]
    if len(c):
        d = b[-1].findAll ('li')
        if len(d) == 0: t = ''
        else:
            s = []
            for a in d: s.append (a.contents[0])
            t = string.join (s,'|')
    return map(str,(p, q, r, t))
def parse_nearby (x):
    t = BeautifulStoneSoup(printable (x)).findAll ('br')
#    for a in t: print a
    s = ["Distances are calculated in a straight line from the property's location to the point of interest or attraction, and may not reflect actual travel distance."]
    for a in t:
        if len(a.contents):
            for b in a.contents:
                if len(b) == 0: continue
                if len(b) > 1:
                    s.append(b)
                    continue

                q = BeautifulStoneSoup (str(b)).findAll ('p')
                if len(q) > 0: s.append(q[0].contents[0])
    return string.join (s,'|')
def main ():
    y = filter_na ()
    n = len(y[y.keys()[0]])

    ft = table_facility()
#    print n
#    n = 1000
    for i in xrange (n):
        g = {}
        g['expedia_id']    = y['HotelID'][i]
        g['hotel_name']    = printable(y['Name'][i])
        g['low_rate']      = y['LowRate'][i]
        g['high_rate']     = y['HighRate'][i]
        g['num_floors']    = y['NumberOfFloors'][i]
        g['num_rooms']     = y['NumberOfRooms'][i]
        g['num_suites']    = y['NumberOfSuites'][i]
        g['country_code']  = y['Country'][i]

        p, q, r, t = parse_desc (y['PropertyDescription'][i])
        g['desp_location']    = p
        g['desp_facility']    = q
        g['desp_guestroom']   = r
        g['desp_fees_etc']    = t
        s = []
        for a in ft:
            if y[a][i] == 'Y': s.append (ft[a])
        g['facilities'] = string.join (s,'|')
        g['desp_nearby_attr'] = parse_nearby(printable(y['NearbyAttractions'][i]))

        Hotel_Expedia (g)

    y = load_facility()
    n = len(y[y.keys()[0]])
    for i in xrange(n):
        g = {}
        g['facility_id']   = y['facility_id'][i]
        g['facility_name'] = y['facility'][i]
        g['facility_type'] = y['type'][i]
        Facility_Expedia (g)

    return

main()
x = session.query(Hotel_Expedia).filter_by(country_code='US').first()
print x.hotel_name
print x.facilities,'\n\n'
print x.desp_location,'\n\n'
print x.desp_facility,'\n\n'
print x.desp_guestroom,'\n\n'
print x.desp_nearby_attr,'\n\n'





