from sqlalchemy import * 
from sqlalchemy.ext.declarative import declarative_base

from alchemy_session import get_alchemy_info

(engine, session, Base, metadata) = get_alchemy_info () 

debug_level = 0 

class PointList(Base) :
    __tablename__ = 'point_list'

    uid = Column(Integer, Sequence('point_list_sequence'), primary_key=True) 

    def __init__(self, points) : 
        if debug_level > 5 : 
           print "building point list from :", points 
        session.add(self) 
        session.commit() 
        for (i, lati, longi) in points : 
            pt = find_point(lati, longi) 
            ple = PointListEntry(self.uid, pt.uid, i)
        
class PointListEntry(Base) :
    __tablename__ = 'point_list_entry'
    uid = Column(Integer, Sequence('pointlist_entry_sequence'), primary_key=True) 
    listid = Column(Integer, ForeignKey('point_list.uid'))    # the primary key for the list I'm part of 
    pid = Column(Integer, ForeignKey('point.uid'))            # the primary key for the point I represent 
    index = Column(Integer)                                   # an index used to order the points to make a polygon 

    def __init__(self, listid, pointid, index) :
        if debug_level > 5 : 
            print "point list entry for ", listid, pointid, index 
        self.pid = pointid
        self.listid = listid
        self.index = index 
        session.add(self)    # adds to database
        session.commit()     # commits the add and reads back - for instance the uid 

def find_point(lati, longi) :
    reslist = session.query(Point).filter(and_(Point.latitude==lati, Point.longitude==longi)).all() 
    if reslist :
        if debug_level > 5 : 
            print "find point finds point in db" 
        res = reslist[0]
    else : 
        res = Point(lati, longi) 
    if debug_level > 5 : 
        print "find point for lati=%s longi=%s returns point (%s,%s,%s)" % (lati, longi, res.uid, res.latitude, res.longitude) 
    return res 

class Point(Base) :     
    __tablename__ = 'point'

    uid = Column(Integer, Sequence('point_sequence'), primary_key=True) 
    latitude = Column(Float) 
    longitude = Column(Float) 

    def __init__(self, lati, longi) :
        self.latitude = lati
        self.longitude = longi 
        session.add(self) 
        session.commit() 
        if debug_level > 5 : 
            print "new point uid=%d lat=%s long=%s" % (self.uid, self.latitude, self.longitude)

metadata.create_all(engine) 
