from sqlalchemy import * 
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
import sys

sys.path.insert(0, "/home/areek/Documents/fetchopia/backend_git/sql/alchemy/" )

from canon_hotel import CanonicalHotel
from kayak_hotels import kayak_hotels
from kayak_internal_table import kayak_internal_table

kayak_hotels = session.query(kayak_hotels).all()

##maps canonical hotels to kayak hotels
def internal_kayak_matcher():
	
	for instance in kayak_hotels:
		#match either has same name or same address
		match_name = session.query(CanonicalHotel).filter(CanonicalHotel.hotel_name == instance.name).first() 
		match_address = session.query(CanonicalHotel).filter(CanonicalHotel.address == instance.address).first()
	
		if match_name:
			canonical_id = match_name.uid
			kayak_id = instance.uid
			entry = kayak_internal_table(canonical_id, kayak_id)
			session.add(entry)
			session.commit()
	
		elif match_address:
			canonical_id = match_address.uid
			kayak_id = instance.uid
			entry = kayak_internal_table(canonical_id, kayak_id)
			session.add(entry)
			session.commit()
		

if __name__ == "__main__":
    
   
    internal_kayak_matcher()
