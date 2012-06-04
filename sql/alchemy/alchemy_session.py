from sqlalchemy import * 
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base

# I think this will do the Right Thing - create a single session
# that is shared among all the python files that load this module
# and run get_engine_session 

engine = None
session = None
Session = None 
Base = None 
metadata = None 
def get_alchemy_info(echo=False) : 
    global engine, Session, session, Base, metadata 
    if engine == None : 
        engine = create_engine('postgresql://postgres:areek@localhost:5432/acuity', echo=echo)# postgresql:///testing
        Session = scoped_session(sessionmaker(bind=engine))
        session = Session()
        Base = declarative_base(bind=session) 
        metadata = Base.metadata 

    return (engine, session, Base, metadata) 
