from sqlalchemy import * 
from sqlalchemy.orm import sessionmaker, scoped_session

# I think this will do the Right Thing - create a single session
# that is shared among all the python files that load this module
# and run get_engine_session 

engine = None
session = None
Session = None 

def get_engine_session(echo=False) : 
    global engine, Session, session 
    if engine == None : 
        engine = create_engine('postgresql:///testing', echo=echo)
        Session = scoped_session(sessionmaker(bind=engine))
        session = Session()
    return (engine, session) 
