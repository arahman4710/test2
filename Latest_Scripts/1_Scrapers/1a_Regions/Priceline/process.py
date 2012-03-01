import re
from sqlalchemy import *
from priceline_regions_table2 import PricelineRegionTable

from alchemy_session import get_alchemy_info


(engine, session, Base, metadata) = get_alchemy_info ()

f = open("output/test_input_process.txt", "r")

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
            [name, city_state, lat, lng] = lines[0]
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
            print name, city, state
            print points
            entry = PricelineRegionTable(default, name, city, state, lat, lng, points)
            session.add(entry)
            session.commit()
                    
                    
            
        

            

