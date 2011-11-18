import sys 
sys.path.insert(0, '/work/jeff/backend/sql/alchemy') 

import csv 
from sqlalchemy import * 
from sqlalchemy.ext.declarative import declarative_base

from alchemy_session import get_alchemy_info
from hotwire_tables import HotWireHotelInfo, Neighborhood 

(engine, session, Base, metadata) = get_alchemy_info () 

# this does essentially the same thing as the get_pricing_info.psql file
# but in sqlalchemy - more or less as a test to see how it all works

outf = open("prices.csv", "w") 
cr = csv.writer(outf, delimiter=",") 
res = session.query(HotWireHotelInfo, Neighborhood).filter(HotWireHotelInfo.neighborhood_uid == Neighborhood.uid) 
for i in res :
    hwi = i.HotWireHotelInfo
    cr.writerow([hwi.subtotal, hwi.taxes_and_fees,hwi.total_price, hwi.average_price_per_night, hwi.star_rating, hwi.rooms, hwi.adults, hwi.nights, hwi.date_offset, i.Neighborhood.city] ) 
    
