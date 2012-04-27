import re
from sqlalchemy import *

from priceline_regions_canada_table import PricelineRegionTable_canada
from priceline_area_canada_table import PricelineAreaTable_canada
from priceline_area_city_canada_table import PricelineAreaCityTable_canada
from city_table2 import CityTable_canadian


from alchemy_session import get_alchemy_info





(engine, session, Base, metadata) = get_alchemy_info()

#### This script stores region, area, area to city relationships for priceline Canada
#### input file from priceline_region_scraper


f = open("process_canada_input.txt", "r")

for line in f.readlines():
    input = line
    regions = re.split("#", input)
    for region in regions:
        region = region[:-1]
        lines = re.split("\$", region)
        for index in range(len(lines)):
            lines[index] = re.split(";", lines[index])

        if len(lines) == 1: ## case of empty line, ignore it
            pass
        else:
            if len(lines[0]) == 4:
                [region_name, city_state, lat, lng] = lines[0]
                points = []
                lines = lines[1:] ## only points in the line in line now
                for i in range(len(lines)):
                    if len(lines[i]) == 1:
                        pass
                    else:
                        line = lines[i]
                        plat = line[2]
                        plat = float(plat)
                        plng = line[3]
                        plng = float(plng)
                        pair = (plat, plng)
                        points.append(pair)
                points = str(points)
                city = re.search(".*\,", city_state).group()
                city = re.sub("\,", "", city)
                state = re.search("\,.*", city_state).group()
                state = re.sub("\,", "", state)
                existing_entry = session.query(PricelineRegionTable_canada).filter(PricelineRegionTable_canada.state == state).filter(PricelineRegionTable_canada.city == city).filter(PricelineRegionTable_canada.name == region_name).count()
                if existing_entry == 0:
                	entry = PricelineRegionTable_canada(region_name, city, state, lat, lng, points)
                	session.add(entry)
                	session.commit()


            else:
                [area, region_name, city_state, lat, lng] = lines[0]
                points = []
                lines = lines[1:]
                for i in range(len(lines)):
                    if len(lines[i]) == 1:
                        pass
                    else:
                        line = lines[i]
                        plat = line[2]
                        plat = float(plat)
                        plng = line[3]
                        plng = float(plng)
                        pair = (plat, plng)
                        points.append(pair)
                points = str(points)
                city = re.search(".*\,", city_state).group()
                city = re.sub("\,", "", city)
                state = re.search("\,.*", city_state).group()
                state = re.sub("\,", "", state)
                existing_area_entry = session.query(PricelineAreaTable_canada).filter(PricelineAreaTable_canada.name == area).count()
                if existing_area_entry == 0:
                	entry = PricelineAreaTable_canada(area)
                	session.add(entry)
#                	session.commit()
                city_table_entry = session.query(CityTable_canadian).filter(CityTable_canadian.state == state).filter(CityTable_canadian.name == city).first()
                area_entry = session.query(PricelineAreaTable_canada).filter(PricelineAreaTable_canada.name == area).first()
                entry_to_area_city_table = PricelineAreaCityTable_canada(area_entry.uid, city_table_entry.uid)
                existing_entry = session.query(PricelineRegionTable_canada).filter(PricelineRegionTable_canada.state == state).filter(PricelineRegionTable_canada.city == city).filter(PricelineRegionTable_canada.name == region_name).count()
                if existing_entry == 0:
                	entry_to_region_table = PricelineRegionTable_canada(region_name, city, state, lat, lng, points)
                	session.add(entry_to_region_table)
                session.add(entry_to_area_city_table)
                session.commit()
                    
            
        

            

