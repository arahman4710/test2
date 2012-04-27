import re
from sqlalchemy import *


from priceline_regions_table import PricelineRegionTable
from priceline_area_table import PricelineAreaTable
from priceline_area_city_table import PricelineAreaCityTable
from city_table import CityTable


from alchemy_session import get_alchemy_info





(engine, session, Base, metadata) = get_alchemy_info()
#### This script stores region, area, area to city relationships for priceline US
#### input file from priceline_region_scraper


f = open("process_US_p2.txt", "r")

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
                existing_entry = session.query(PricelineRegionTable).filter(PricelineRegionTable.state == state).filter(PricelineRegionTable.city == city).filter(PricelineRegionTable.name == region_name).count()
                if existing_entry == 0:
                	entry = PricelineRegionTable(region_name, city, state, lat, lng, points)
                	session.add(entry)
                	session.commit()


            elif len(lines[0]) == 5:
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
                existing_area_entry = session.query(PricelineAreaTable).filter(PricelineAreaTable.name == area).count()
                if existing_area_entry == 0:
                	entry = PricelineAreaTable(area)
                	session.add(entry)
#                	session.commit()
                city_table_entry = session.query(CityTable).filter(CityTable.state == state).filter(CityTable.name == city)
                if city_table_entry.count() == 0:
                	continue
                area_entry = session.query(PricelineAreaTable).filter(PricelineAreaTable.name == area).first()
                entry_to_area_city_table = PricelineAreaCityTable(area_entry.uid, city_table_entry.first().uid)
                existing_entry = session.query(PricelineRegionTable).filter(PricelineRegionTable.state == state).filter(PricelineRegionTable.city == city).filter(PricelineRegionTable.name == region_name).count()
                if existing_entry == 0:
                	entry_to_region_table = PricelineRegionTable(region_name, city, state, lat, lng, points)
                	session.add(entry_to_region_table)
                session.add(entry_to_area_city_table)
                session.commit()
                    
            
        

            

