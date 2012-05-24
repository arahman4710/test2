import re
from sqlalchemy import * 
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base


from city_table2 import CityTable_canadian
from priceline_regions_canada_table import PricelineRegionTable_canada
from priceline_city_region_canada_map import PricelineCityRegionMap_canada


engine = create_engine('postgresql://postgres:areek@localhost:5432/acuity', echo=False)
Session = scoped_session(sessionmaker(bind=engine))
session = Session()
Base = declarative_base(bind=session) 
metadata = Base.metadata

#### This script stores city to region relationship for priceline Canada
#### use the citytoregion.txt file from the priceline_region_scraper

f = open("citytoregion.txt", "r")

city = ""
region_name = ""
state = ""


for line in f.readlines():
    input = line
    input = re.sub("\n", "", input)
    items = re.split("HAS", input)
    city_state = items[0]
    region_name = items[1]
    region_name = region_name[1:-1]
#    region_name = re.search('\w.*\w', region_name).group()
    city_state = re.split("\,", city_state)
    city = city_state[0]
    state = city_state[1]
    state = state[:-1]

    region_entry = session.query(PricelineRegionTable_canada).filter(PricelineRegionTable_canada.state == state).filter(PricelineRegionTable_canada.city == city).filter(PricelineRegionTable_canada.name == region_name).first()
    city_entry = session.query(CityTable_canadian).filter(CityTable_canadian.state == state).filter(CityTable_canadian.name == city).first()
    

    
    if region_entry and city_entry:
	    entry = PricelineCityRegionMap_canada(city_entry.uid, region_entry.uid)
	    session.add(entry)
	    session.commit()
	
    
    

    
    
                    
            
        

            

