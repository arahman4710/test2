from collections import namedtuple
from pprint import pprint as pp
import MySQLdb
import sys
 
class Connection_to():
	database = MySQLdb.connect(user='root', passwd='areek', db='acuity_backup')
	cursor = database.cursor()


Pt = namedtuple('Pt', 'x, y')               # Point
Edge = namedtuple('Edge', 'a, b')           # Polygon edge from a to b
Poly = namedtuple('Poly', 'name, edges')    # Polygon
 
_eps = 0.00001
_huge = sys.float_info.max
_tiny = sys.float_info.min



def rayintersectseg(p, edge):
    ''' takes a point p=Pt() and an edge of two endpoints a,b=Pt() of a line segment returns boolean
    '''
    a,b = edge
    if a.y > b.y:
        a,b = b,a
    if p.y == a.y or p.y == b.y:
        p = Pt(p.x, p.y + _eps)
 
    intersect = False
 
    if (p.y > b.y or p.y < a.y) or (
        p.x > max(a.x, b.x)):
        return False
 
    if p.x < min(a.x, b.x):
        intersect = True
    else:
        if abs(a.x - b.x) > _tiny:
            m_red = (b.y - a.y) / float(b.x - a.x)
        else:
            m_red = _huge
        if abs(a.x - p.x) > _tiny:
            m_blue = (p.y - a.y) / float(p.x - a.x)
        else:
            m_blue = _huge
        intersect = m_blue >= m_red
    return intersect
 
def _odd(x): return x%2 == 1
 
def ispointinside(p, poly):
    ln = len(poly)
    return _odd(sum(rayintersectseg(p, edge)
                    for edge in poly.edges ))


def polypp(poly):
    print "\n  Polygon(name='%s', edges=(" % poly.name
    print '   ', ',\n    '.join(str(e) for e in poly.edges) + '\n    ))'
 
if __name__ == '__main__':
    region_dict = {}
    region_object = {}
    Connection_to.cursor.execute("SELECT * FROM pricelinepoints WHERE PricelineRegions_PricelineRegionId IN (SELECT PricelineRegionId FROM pricelineregions\
    WHERE cities_cityid IN (SELECT cityid FROM cities WHERE state IN ('Utah')))")

    for records in Connection_to.cursor.fetchall():
        #print records
        if records[1] not in region_dict.keys():
            region_dict[records[1]]=[Pt(x=records[3], y=records[4])]
        else:
            region_dict[records[1]].append(Pt(x=records[3], y=records[4]))

    
    for point_set in region_dict.keys():
        if region_dict[point_set][0] != region_dict[point_set][-1]:
           region_dict[point_set].append(region_dict[point_set][0])
          # print region_dict[point_set]
          # print '__________________'
        #else:
           # print 'NAAICE'
    

    for region in region_dict.keys():
        t_region =[]
        for i in range(len(region_dict[region])-1):
            t_region.append(Edge(region_dict[region][i],region_dict[region][i+1]))


        region_object[region] = Poly(name= region, edges=t_region)

    for reg in region_object.keys():
        if ispointinside(Pt(x=37.182667, y=-113.002598),region_object[reg]):
            print reg

    #print region_object
    '''
    for latlng in latlngs:
        cordins = latlng.split(',')
        lat = float(cordins[0])
        lng = float(cordins[1])
        point_latlng.append(Pt(x=lat, y=lng))
        for i in range(len(point_latlng)-1):
            temp_edges.append(Edge(a=point_latlng[i], b=point_latlng[i+1]))
    tmp_name='exagon'
    tmp_edges =[
        Edge(a=Pt(x=3, y=0), b=Pt(x=7, y=0)),
        Edge(a=Pt(x=7, y=0), b=Pt(x=10, y=5)),
        Edge(a=Pt(x=10, y=5), b=Pt(x=7, y=10)),
        Edge(a=Pt(x=7, y=10), b=Pt(x=3, y=10)),
        Edge(a=Pt(x=3, y=10), b=Pt(x=0, y=5)),
        Edge(a=Pt(x=0, y=5), b=Pt(x=3, y=0))]
    testign= Poly(name= tmp_name, edges=tmp_edges)
    polys = [
      Poly(name='square', edges=(
        Edge(a=Pt(x=0, y=0), b=Pt(x=10, y=0)),
        Edge(a=Pt(x=10, y=0), b=Pt(x=10, y=10)),
        Edge(a=Pt(x=10, y=10), b=Pt(x=0, y=10)),
        Edge(a=Pt(x=0, y=10), b=Pt(x=0, y=0))
        )),
      Poly(name='square_hole', edges=(
        Edge(a=Pt(x=0, y=0), b=Pt(x=10, y=0)),
        Edge(a=Pt(x=10, y=0), b=Pt(x=10, y=10)),
        Edge(a=Pt(x=10, y=10), b=Pt(x=0, y=10)),
        Edge(a=Pt(x=0, y=10), b=Pt(x=0, y=0)),
        Edge(a=Pt(x=2.5, y=2.5), b=Pt(x=7.5, y=2.5)),
        Edge(a=Pt(x=7.5, y=2.5), b=Pt(x=7.5, y=7.5)),
        Edge(a=Pt(x=7.5, y=7.5), b=Pt(x=2.5, y=7.5)),
        Edge(a=Pt(x=2.5, y=7.5), b=Pt(x=2.5, y=2.5))
        )),
      Poly(name='strange', edges=(
        Edge(a=Pt(x=0, y=0), b=Pt(x=2.5, y=2.5)),
        Edge(a=Pt(x=2.5, y=2.5), b=Pt(x=0, y=10)),
        Edge(a=Pt(x=0, y=10), b=Pt(x=2.5, y=7.5)),
        Edge(a=Pt(x=2.5, y=7.5), b=Pt(x=7.5, y=7.5)),
        Edge(a=Pt(x=7.5, y=7.5), b=Pt(x=10, y=10)),
        Edge(a=Pt(x=10, y=10), b=Pt(x=10, y=0)),
        Edge(a=Pt(x=10, y=0), b=Pt(x=2.5, y=2.5))
        )),
      testign,
      ]
    testpoints = (Pt(x=5, y=5), Pt(x=5, y=8),
                  Pt(x=-10, y=5), Pt(x=0, y=5),
                  Pt(x=10, y=5), Pt(x=8, y=5),
                  Pt(x=10, y=10))
 
    print "\n TESTING WHETHER POINTS ARE WITHIN POLYGONS"
    for poly in polys:
        polypp(poly)
        print '   ', '\t'.join("%s: %s" % (p, ispointinside(p, poly))
                               for p in testpoints[:3])
        print '   ', '\t'.join("%s: %s" % (p, ispointinside(p, poly))
                               for p in testpoints[3:6])
        print '   ', '\t'.join("%s: %s" % (p, ispointinside(p, poly))
                               for p in testpoints[6:])
        '''