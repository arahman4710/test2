from sqlalchemy import *

from alchemy_session import get_alchemy_info

(engine, session, Base, metadata) = get_alchemy_info ()
##this table maps kayak hotels to ones in canonical and saves the uid of the matching pair in kayak_internal_table

class kayak_internal_table(Base) :

    __tablename__ = 'kayak_internal_table'

    uid = Column(Integer, primary_key=True)  #   primary key
    canonical_id =  Column(Integer())  #   canonical uid
    kayak_id = Column(Integer())  #  	kayak uid
    

    def __init__(self, canonical_id, kayak_id) :

        #   Assign params to member variables

        self.canonical_id = canonical_id
        self.kayak_id = kayak_id


metadata.create_all(engine)
