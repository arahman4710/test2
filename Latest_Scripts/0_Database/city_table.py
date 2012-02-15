from sqlalchemy import *

from alchemy_session import get_alchemy_info

(engine, session, Base, metadata) = get_alchemy_info ()

debug_level = 0

#   Database Mapper Class for city table

#   This table has information about all internal cities


class CityTable(Base) :

    __tablename__ = 'city'

    uid = Column(Integer, Sequence('city_sequence'), primary_key=True)  #   primary key
    name = Column(String(500))  #   name of the city
    state = Column(String(500)) #   name of the state
    country = Column(String(500))   #   name of the country

    def __init__(self, uid, name,state,country) :

        #   Assign params to member variables

        self.uid = uid
        self.name = name
        self.state = state
        self.country = country

    def __str__(self) :

	return "< city_table name = %s state = %s country = %s >" % (self.name, self.state, self.country)

metadata.create_all(engine)