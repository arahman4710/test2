from sqlalchemy import * 
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
import pdb
import sys
import Levenshtein
sys.path.insert(0, "/home/areek/Documents/fetchopia/backend_git/sql/alchemy/" )
from alchemy_session import get_alchemy_info

(engine, session, Base, metadata) = get_alchemy_info ()
from canon_hotel import CanonicalHotel
from kayak_hotels import kayak_hotels
from kayak_internal_table import kayak_internal_table
import logging
logging.basicConfig(filename='kayak_internal_matcher.log',filemode='w',level=logging.DEBUG)


def find_htl_name_match_ratio(name_1,name_2):
	return Levenshtein.ratio(normalize_name(name_1),normalize_name(name_2))

def find_htl_address_match_ratio(add_1,add_2):
	return Levenshtein.ratio(normalize_address(add_1),normalize_address(add_2)) 
    
def normalize_name(name):
	
	cleaned_name = name.replace(" and ","&").replace(" And ","&").replace("&amp;", "&").replace("Hotel","").strip().lower()
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
		
		max_ratio = 0
		max_match_tuple = ()
		
		match_name = session.query(CanonicalHotel).filter(CanonicalHotel.hotel_name == kayak_name).first() 
		match_address = session.query(CanonicalHotel).filter(CanonicalHotel.address == kayak_address).first()
		hit_last_case = 0
	
		if match_name:
			canonical_id = match_name.uid
			kayak_id = instance.uid
			entry = kayak_internal_table(canonical_id, kayak_id)
			session.add(entry)
			session.commit()
##			logging.info("PERFECT MATCH:: %s" % match_name.hotel_name)
			continue
		
		elif match_address:
			canonical_id = match_address.uid
			kayak_id = instance.uid
			entry = kayak_internal_table(canonical_id, kayak_id)
			session.add(entry)
			session.commit()
#			logging.info("PERFECT MATCH:: %s" % match_address.address)
			continue

		else:
			possible_match = session.query(CanonicalHotel).filter(CanonicalHotel.postal_code == kayak_postal)		
			
			if possible_match.count() > 0:

				for match in possible_match.all():
				
					name_ratio = find_htl_name_match_ratio(match.hotel_name, kayak_name) 
					address_ratio = find_htl_address_match_ratio(match.address,kayak_address)
					
					if address_ratio > float(0.98):
						address_ratio = 2
					
					if name_ratio > float(0.95):
						name_ratio = 2
				
					ratio = name_ratio + address_ratio
				
					if max_ratio < ratio:
						max_ratio = ratio
						max_match_tuple = (match, name_ratio, address_ratio)
				
				(match, name_ratio, address_ratio) = max_match_tuple

				if max_ratio > 1.35:
					canonical_id = match.uid
					kayak_id = instance.uid
					entry = kayak_internal_table(canonical_id, kayak_id)
					session.add(entry)					
					session.commit()
					logging.info("MAX MATCHED:: kayak_name: %s canon_name: %s with RATIO: %f" % (kayak_name, match.hotel_name, name_ratio))
					logging.info("MAX MATCHED:: kayak_address: %s canon_address: %s with RATIO: %f" % (kayak_address, match.address, address_ratio))
				
				else:
					logging.info("UNMATCHED:: kayak_name: %s canon_name: %s with RATIO: %f" % (kayak_name, match.hotel_name, name_ratio))
					logging.info("UNMATCHED:: kayak_address: %s canon_address: %s with RATIO: %f" % (kayak_address, match.address, address_ratio))
					
			
			else:
				logging.info("ZERO MATCHES:: kayak_name: %s kayak_address: %s" % (kayak_name, kayak_address))
				continue ## no match for this kayak hotel case

			
				
				
	
				
				
				
			
			
		

if __name__ == "__main__":
    
   
    internal_kayak_matcher()
