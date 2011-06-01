import sys

if '/work/jeff/backend/sql/alchemy' not in sys.path :
   sys.path.insert(0,'/work/jeff/backend/sql/alchemy')

from sqlalchemy import * 

from alchemy_session import get_alchemy_info
from point import Point 

(engine, session, Base, metadata) = get_alchemy_info () 

debug_level = 10 

class Amenity(Base) : 
   __tablename__ = 'amenity'    # set the table name 
 
   # variables declared in a class using "Column"
   # these are going to be reflected in the table built
   # other variables in the class will not 
   uid = Column(Integer, Sequence('amenity_uid_sequence'), primary_key=True) 
   name = Column(String())                     # name 
   code = Column(String())   # two character code 
   description = Column(String())              # long description. 

   def __init__(self, namesdict) : 
       for i in namesdict : 
           self.__setattr__(i, namesdict[i]) 
       session.add(self) 
       session.commit() 

class AmenityString(Base) :
    __tablename__ = 'amenity_string' 

    uid = Column(Integer, Sequence('amenity_string_sequence'), primary_key=True)  # unique id 
    amenity_string = Column(String()) 

    def __init__(self, amenitylist) : 
        self.amenity_string = get_amenity_string(amenitylist)
        session.add(self) 
        session.commit() 
            
def get_amenity_string(al) :
    return "|".join(sorted(al)) 

def find_amenity_string(al) :
    norm_al = get_amenity_string(al) 
    amenity = session.query(AmenityString).filter_by(amenity_string=norm_al).scalar()   
    if amenity :
       return amenity.uid 
    else :
       return AmenityString(al).uid 
    
def get_amenity(c) : 
    amenity = session.query(Amenity).filter_by(code='code').one()
    return amenity 

metadata.create_all(engine)
