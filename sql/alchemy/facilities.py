import string 
import sys 
import datetime 

from sqlalchemy import * 
from sqlalchemy.orm import sessionmaker, scoped_session
# the declarative stuff lets you use objects with defined columns
# instead of creating the tables using DDL or the like
from sqlalchemy.ext.declarative import declarative_base

sys.path.insert(0, "/home/jefu/fetch/backend/sql/alchemy/" )
from alchemy_session import get_engine_session 

(engine, session) = get_engine_session () 


debug_level = 0 

# set up base class for sqlalchemy 
# all our classes that mirror the database will have this as a base 

Base = declarative_base() 
metadata = Base.metadata
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
