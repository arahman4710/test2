import string 
import sys 
import datetime 

from sqlalchemy import * 
from sqlalchemy.orm import sessionmaker, scoped_session
# the declarative stuff lets you use objects with defined columns
# instead of creating the tables using DDL or the like
from sqlalchemy.ext.declarative import declarative_base

sys.path.insert(0, "/home/jefu/fetch/backend/sql/alchemy/" )
from alchemy_session import get_alchemy_info

(engine, session, Base, metadata) = get_alchemy_info ()

debug_level = 0 

#
# city geography info from hotels_combined 
# 
class HC_City(Base) :
    __tablename__ = 'hc_city'
    uid = Column(Integer(), primary_key=True)
    city_filename = Column(String())
    city_name = Column(String())
    city_center_location = Column(Integer, ForeignKey('point.uid'))
    state_id = Column(Integer())   # what does this do?
    state_filename = Column(String())
    state_name = Column(String())
    country_code = Column(String())
    country_filename = Column(String())
    country_name = Column(String()) 

    def __init__(self, dict) :
        for i in dict :
            self.__setattr__(i, dict[i]) 
        if self.state_id == '' :
            self.state_id = 0 
        session.add(self)
        session.commit()

metadata.create_all(engine) 
