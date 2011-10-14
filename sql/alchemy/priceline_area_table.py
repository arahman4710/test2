
from sqlalchemy import *

from alchemy_session import get_alchemy_info


(engine, session, Base, metadata) = get_alchemy_info ()

debug_level = 0

#   Database Mapper Class for priceline_area table

#   This table contains information about priceline areas

class PricelineAreaTable(Base) :

    __tablename__ = 'priceline_area_table'

    uid = Column(Integer, Sequence('priceline_area_sequence'), primary_key=True)  #   primary key
    name = Column(String(500)) #   name of the area


    def __init__(self, uid, name) :

        #   Assign params to member variables

        self.uid = uid
        self.name = name


    def __str__(self) :

        #   pretty printing

        return "< priceline_area name = %s >" % (self.name)


metadata.create_all(engine)