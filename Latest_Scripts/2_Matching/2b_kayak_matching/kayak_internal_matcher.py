from sqlalchemy import * 
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
import sys

sys.path.insert(0, "/home/areek/Documents/fetchopia/backend_git/sql/alchemy/" )
from alchemy_session import get_alchemy_info

(engine, session, Base, metadata) = get_alchemy_info ()
from canon_hotel import CanonicalHotel
from kayak_hotels import kayak_hotels
from kayak_internal_table import kayak_internal_table


def find_htl_name_match_ratio(name_1,name_2):
	return Levenshtein.ratio(normalize_name(name_1),normalize_name(name_2))

def find_htl_address_match_ratio(add_1,add_2):
	return Levenshtein.ratio(normalize_address(add_1),normalize_address(add_2)) 
    
def normalize_name(name):
	
	cleaned_name = name.replace(" and ","&").replace(" And ","&").replace("Hotel","").strip().lower()
	return " ".join(sorted(cleaned_name.split()))

def normalize_address(addr):
	
	cleaned_addr = addr.lower().replace(".","").replace(" drive"," dr")\
        .replace(" parkwy"," pkwy").replace(" boulevard"," blvd").\
        replace("@","at").replace(" street"," st").replace(" &amp; "," & ").\
        replace(" road"," rd").replace(" east"," e").replace(" north"," n").\
        replace(" south"," s").replace(" west"," w").replace(" avenue"," ave").\
        replace(" freeway"," frwy").replace(" fwy"," frwy").replace(" parkway"," pkwy").replace("rue ","st ").replace(" rue"," st")
	
	return cleaned_addr   


##maps canonical hotels to kayak hotels
def internal_kayak_matcher():
	
	all_kayak_hotels = session.query(kayak_hotels).all()
	
	for instance in all_kayak_hotels:
	
		kayak_postal = instance.postal_code
		kayak_name = instance.name
		kayak_address = instance.address
		
		possible_match = session.query(CanonicalHotel).filter(CanonicalHotel.postal_code == kayak_postal).all()
		
		max_ratio = 0
		max_match_tuple = ()
		
		match_name = session.query(CanonicalHotel).filter(CanonicalHotel.hotel_name == kayak_name).first() 
		match_address = session.query(CanonicalHotel).filter(CanonicalHotel.address == kayak_address).first()
	
		if match_name or match_address:
			canonical_id = match_name.uid
			kayak_id = instance.uid
			entry = kayak_internal_table(canonical_id, kayak_id)
			session.add(entry)
			session.commit()
			continue
		else:		

			for match in possible_match:
				
				name_ratio = find_htl_name_match_ratio(match.name, kayak_name) 
				address_ratio = find_htl_address_match_ratio(match.address,kayak_address)
				
				ratio = name_ratio + address_ratio
				
				if max_ratio < ratio:
					max_ratio = ratio
					max_match_tuple = (match, max_ratio)
				
		(match, max_ratio) = max_match_tuple

		if max_ratio > 1.7:
			canonical_id = match.uid
			kayak_id = instance.uid
			entry = kayak_internal_table(canonical_id, kayak_id)
			session.add(entry)
			session.commit()
			
				
				
	
				
				
				
			
			
		

#if __name__ == "__main__":
    
   
#    internal_kayak_matcher()
