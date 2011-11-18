import sys

if '/work/jeff/backend/sql/alchemy' not in sys.path :
   sys.path.insert(0,'/work/jeff/backend/sql/alchemy')

from sqlalchemy import * 

from alchemy_session import get_alchemy_info
from amenity import Amenity, find_amenity_string 
from hotwire_tables import HotWireHotelInfo 

(engine, session, Base, metadata) = get_alchemy_info () 

debug_level = 10 

amenity_dict = {} 
acodes = session.query("uid", "code").from_statement("select uid,code from amenity") 
for i in acodes : 
    print i.uid, i.code 
    amenity_dict[i.uid] = i.code 

alists = session.query("uid").from_statement("select uid from amenity_list").all()

for i in alists :
    print i 
    res = session.query("amenity_id").from_statement("select amenity_id from amenity_list_item where amenity_list_id=%s" % i[0]).all()
    for j in res :
        print i, j, amenity_dict[j[0]] 
    al = [amenity_dict[j[0]] for j in res] 
    print al 
    astr = find_amenity_string(al)
    hot = session.query(HotWireHotelInfo).filter_by(amenity_list=i[0]).all()
    for i in hot :
       i.amenity_list = astr
       session.commit() 
