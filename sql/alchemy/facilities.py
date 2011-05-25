import string 
import sys 
import datetime 

from sqlalchemy import * 
from sqlalchemy.orm import sessionmaker, scoped_session
# the declarative stuff lets you use objects with defined columns
# instead of creating the tables using DDL or the like
from sqlalchemy.ext.declarative import declarative_base

sys.path.insert(0, "/work/jeff/backend/sql/alchemy/" )
from alchemy_session import get_alchemy_info

(engine, session, Base, metadata) = get_alchemy_info() 


debug_level = 0 

#
# facilities descriptions for the hotels_combined facilities information
# 
class Facility(Base) :
    __tablename__ = 'hc_facility'
    uid = Column(Integer(), primary_key=True)
    description = Column(String())

    def __init__(self, id, desc) :
        self.uid = id
        self.description = desc

        session.add(self)
        session.commit()

metadata.create_all(engine) 
