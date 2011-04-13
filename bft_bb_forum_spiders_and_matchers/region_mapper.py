import MySQLdb
import ray_casting
from collections import namedtuple
Pt = namedtuple('Pt', 'x, y')

def delete_duplicate(mylist):
    mylist=sorted(mylist, key=lambda item: item[2])
    last = mylist[-1][2]
    for i in range(len(mylist)-2, -1, -1):
        if last == mylist[i][2]:
            del mylist[i]
        else:
            last = mylist[i][2]
    return mylist

class Connection():
	database = MySQLdb.connect(user='root', passwd='areek', db='acuity')
	cursor = database.cursor()


def region_finder():
    regions_dictionary ={}
    Connection.cursor.execute('''
    CREATE TABLE IF NOT EXISTS `region_hotel` (
  `hotel_id` int(11) DEFAULT NULL,
  `pl_region_id` int(11) DEFAULT NULL) ENGINE=InnoDB DEFAULT CHARSET=latin1
    ''')
    Connection.cursor.execute("Select * from pricelineregions")
    for regions in Connection.cursor.fetchall():
        Connection.cursor.execute(''' SELECT * FROM pricelinepoints
            WHERE PricelineRegions_PricelineRegionId = %s  ''' % str(regions[0]))
        temp_list = delete_duplicate(map(list,Connection.cursor.fetchall()))
        regions_dictionary[regions[0]] = ray_casting.make_region(regions[1],map(lambda x:x[-2:], temp_list))
    return regions_dictionary


def region_mapper(regions_dictionary):
    Connection.cursor.execute("Select * from hotels")
    hotels = Connection.cursor.fetchall()
    for hotel in hotels:
        for region in regions_dictionary.keys():
             if ray_casting.ispointinside(Pt(x=hotel[4], y=hotel[5]),regions_dictionary[region]):
                Connection.cursor.execute("Select * from region_hotel where hotel_id="+str(hotel[0])+" and pl_region_id = "+str(region)+"")
                if not Connection.cursor.fetchall():
                    Connection.cursor.execute("INSERT INTO `region_hotel` \
                    (`hotel_id`, `pl_region_id`) VALUES ('"+str(hotel[0])+"', '"+str(region)+"');")
                    Connection.database.commit()

def city_region_finder(cityid):
    Connection.cursor.execute("Select priceline_regionid from regionscitiesmap where cities_cityid ="+ str(cityid))
    region_ids = Connection.cursor.fetchall()
    region_name = []
    for region_id in region_ids:
       # print region_id[0]
        Connection.cursor.execute("Select Regionname from pricelineregions where pricelineid = "+str(region_id[0]))
        for one in Connection.cursor.fetchall():
            region_name.append(one[0])
    return region_name

def state_city():
    state_city={}
    Connection.cursor.execute("Select * from cities")
    for one in Connection.cursor.fetchall():
        if one[2].lower() in state_city.keys():
            if one[1].lower() not in state_city[one[2].lower()].keys():
                state_city[one[2].lower()][one[1].lower()] = city_region_finder(one[0])
        else:
            state_city[one[2].lower()] = {}
            state_city[one[2].lower()][one[1].lower()] = city_region_finder(one[0])
    
    return state_city


if __name__ == "__main__":
    '''
    print matcher_for_bb_bft.city_match(['Washington'],['washington d.c.'])
    
    intermal_state_city = state_city()
    external_state_city = matcher_for_bb_bft.csv_format_new('hotels-bbpl2','~','#','output/hotels-bbpl2',3,0,1,2)

    for state_matches in matcher_for_bb_bft.entity_match(external_state_city.keys(), intermal_state_city.keys()):
        print state_matches[1]
        #if state_matches[1] =='district of columbia':
        #    print  intermal_state_city[state_matches[1]].keys()
        #    print external_state_city[state_matches[0]].keys()
        #    print intermal_state_city[state_matches[1]].keys()
        for possible_city_matches in matcher_for_bb_bft.city_match(external_state_city[state_matches[0]].keys(), intermal_state_city[state_matches[1]].keys()):

            for city_matches in possible_city_matches:
               # print city_matches
                if city_matches[2]==-1.0:
                    print 'NOT MATCHED  '+ city_matches[1]
                else:
                    
                    for possible_region_matches in matcher_for_bb_bft.city_match(external_state_city[state_matches[0]].keys(), intermal_state_city[state_matches[1]].keys()):

                        for region_matches in possible_region_matches:
                            if region_matches[2] == -1.0:
                                print '         NOT MATCHED  '+ region_matches[1]

    '''
    region_mapper(region_finder())
