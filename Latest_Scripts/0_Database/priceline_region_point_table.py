
from sqlalchemy import *

from alchemy_session import get_alchemy_info
from priceline_regions_table import PricelineRegionTable

(engine, session, Base, metadata) = get_alchemy_info ()

debug_level = 0

#   Database Mapper Class for priceline_region_point_table table

#   This table keeps information about all the points that make up all the priceline region polygons


class PricelineRegionPointTable(Base):

    __tablename__ = 'priceline_region_point_table'

    uid = Column(Integer, Sequence('priceline_region_point_sequence'), primary_key=True)   #   primary key
    priceline_region_id =  Column(Integer, ForeignKey('priceline_region_table.uid'))  #   foreign key pointing to a particular priceline region, to which the set of points belong to
    order_id =  Column(Integer())  #   sequence # of points, the order in which the points make up a region
    latitude = Column(Float())    #   latitude of the point
    longitude = Column(Float())    #   longitude of the point


    def __init__(self, uid, priceline_region_id, order_id,latitude,longitude) :

        #   Assign params to member variables

        self.uid = uid
        self.priceline_region_id = priceline_region_id
        self.order_id = order_id
        self.latitude = latitude
        self.longitude = longitude



    def __str__(self) :

        #   pretty printing

        return "< priceline_region priceline_region_id = %s position = (%s, %s) >" % (self.priceline_region_id,self.latitude,self.longitude)

    
metadata.create_all(engine)