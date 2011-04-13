'''
-first get the whole city list from db
-make dictionary of key: foreign_cities and value: array of foreign_hotels in that city
-get foreign_cities to match
-find em out through binary search
-fuzzy needed (should be incorporated in binary search implementation)
-match up all foreign_city with db_cities
-generate sql specific to cities to match hotels for a particular city (so hotel matching will be relatively faster and more accurate)
-then match foreign_hotels with internal hotel list
'''
import matcher_for_bb_bft





import MySQLdb
import Levenshtein
import re
import time
import ray_casting
from collections import namedtuple
Pt = namedtuple('Pt', 'x, y')    

def print_timing(func):
    def wrapper(*arg):
        t1 = time.time()
        res = func(*arg)
        t2 = time.time()
        print '%s took %0.3f ms' % (func.func_name, (t2-t1)*1000.0)
        return res
    return wrapper


class BinarySearch:
        NOT_FOUND = -1
        def binarySearch(self, arr, searchValue, left, right):
                if (right < left):
                        return self.NOT_FOUND

                mid = (left + right) / 2
                if (searchValue > arr[mid]):
                        return self.binarySearch(arr, searchValue, mid + 1, right)
                elif (searchValue < arr[mid]):
                        return self.binarySearch(arr, searchValue, left, mid - 1)
                else:
                        return mid

        def search(self, arr, searchValue):
                left = 0
                right = len(arr)
                return self.binarySearch(arr, searchValue, left, right)

class Connection():
	database = MySQLdb.connect(user='root', passwd='areek', db='acuity')
	cursor = database.cursor()

def test_area():
    f = open('area_list.csv').readlines()
    temp_lst  = []
    count = 0
    for line in f:
        if line.split(',')[0].strip():
            temp_lst.append(line.split(',')[0].strip())
    dict = csv_format('hotels-bbpl2','~','#','output/hotels-bbpl2',3,1,2)
    print len(dict.keys())
    for one in city_match(dict.keys(),temp_lst):
        for o in one:
            if o[2]==-1:
                count+=1
    print count

def delete_duplicate(mylist):
    mylist=sorted(mylist, key=lambda item: item[2])
    last = mylist[-1][2]
    for i in range(len(mylist)-2, -1, -1):
        if last == mylist[i][2]:
            del mylist[i]
        else:
            last = mylist[i][2]
    return mylist


'''

-search by city and region

'''
'''
def init_region(city_param):
    Connection.cursor.execute("Select hotelname,latitude,longitude from hotels where cities_cityid = "% city_param)
    for int_hotel in  Connection.cursor.fetchall():
'''

def query_db(city):
    Connection.cursor.execute("SELECT hotelid,hotelname,city,cityid,latitude,longitude FROM hotels JOIN cities ON cities.CityId = hotels.Cities_CityId WHERE cities.city LIKE '%"+re.sub('''(['"])''', r'\\\1',str(city.strip().replace('St ','Saint ').replace('St.','Saint ')))+"%' ")
    result = Connection.cursor.fetchall()
    if result:
        return result
    city_parts = city.split('-')
    if len(city_parts)>1:
        sql ="SELECT hotelid,hotelname,city,cityid,latitude,longitude FROM hotels JOIN cities ON cities.CityId = hotels.Cities_CityId WHERE "
        for ea in city_parts:
            sql+= " cities.city LIKE '%"+re.sub('''(['"])''', r'\\\1',str(ea.strip()))+"%' OR"
                #print sql[:-2]
        Connection.cursor.execute(sql[:-2])
        result = Connection.cursor.fetchall()
        if result:
            return result
    city_parts=city.split()
    if len(city_parts)>1:
        sql ="SELECT hotelid,hotelname,city,cityid,latitude,longitude FROM hotels JOIN cities ON cities.CityId = hotels.Cities_CityId WHERE "
        for ea in city_parts:
            sql+= " cities.city LIKE '%"+re.sub('''(['"])''', r'\\\1',str(ea.strip()))+"%' OR"
                #print sql[:-2]
        Connection.cursor.execute(sql[:-2])
        result = Connection.cursor.fetchall()
        if result:
            return result
        
       # else:
            #    print 'not aval for '+ str(city)
   # else:
     #   print 'not aval for '+ str(city)
        
    return None

def city_match(foreign_list,internal_list):
    matches = []

    for foreign_list_item in foreign_list:
        indiv_match =[]
        temp_name = []
        temp_name_space = []

        if '-' in foreign_list_item:
            temp_name = foreign_list_item.split('-')
        if ' ' in foreign_list_item:
            temp_name_space = foreign_list_item.split()
        for list_item in internal_list:
            temp=Levenshtein.ratio(str(foreign_list_item).lower().strip().replace('/',' ').replace('-',' ').replace('saint ','st ').replace(' area','').replace(' city','').replace('fort ','ft. '),str(list_item).lower().strip().replace(' city','').replace('/',' ').replace('-',' ').replace(' area','').replace('saint ','st ').replace('fort ','ft. '))
            if temp > 0.90:
                indiv_match.append([foreign_list_item,list_item,temp])
                

        if not indiv_match:
            for list_item in internal_list:
                if list_item.strip() and foreign_list_item.strip():
                    if list_item.lower() in foreign_list_item.lower() or foreign_list_item.lower() in list_item.lower():
                        temp=1.0
                        indiv_match.append([foreign_list_item,list_item,temp])
            

        if not indiv_match and temp_name:
            
            for list_item in internal_list:
                is_in = 0
                for one in temp_name:
                    if  one != ' 'and one!= '' and  one.lower() != 'south' and one.lower() != 'north' and one.lower() != 'west' and one.lower() != 'east':
                      temp=Levenshtein.ratio(str(one).lower().strip().replace('/',' ').replace('-',' ').replace(' area','').replace('saint ','st ').replace(' city','').replace('fort ','ft. '),str(list_item).lower().strip().replace(' city','').replace('/',' ').replace('-',' ').replace(' area','').replace('saint ','st ').replace('fort ','ft. '))
                      if temp > 0.9:
                          is_in = 1
                for a in temp_name:
                    if a in list_item and a != ' 'and a!= '' and a!='-' and a!='/' and a.lower() != 'south'and a.lower() != 'north'and a.lower() != 'west' and a.lower() != 'east':
                        temp =1.0
                        is_in = 1
                        break
                if is_in:
                    indiv_match.append([foreign_list_item,list_item,1.0])

        if not indiv_match and temp_name_space:
            
            for list_item in internal_list:
                is_in = 0
                for one in temp_name_space:
                    if  one != ' 'and one!= '' and  one.lower() != 'south' and one.lower() != 'north'and one.lower() != 'west' and one.lower() != 'east':
                        temp=Levenshtein.ratio(str(one).lower().strip().replace('/',' ').replace('-',' ').replace(' area','').replace('saint ','st ').replace(' city','').replace('fort ','ft. '),str(list_item).lower().strip().replace(' city','').replace('/',' ').replace('-',' ').replace(' area','').replace('saint ','st ').replace('fort ','ft. '))
                        if temp > 0.9:
                            is_in = 1
                for a in temp_name_space:
                    if a in list_item and a != ' 'and a!= '' and a!='-' and a!='/' and a.lower() != 'south'and a.lower() != 'north'and a.lower() != 'west' and a.lower() != 'east':
                        temp =1.0
                        is_in = 1
                        break
                if is_in:
                    indiv_match.append([foreign_list_item,list_item,1.0])

        if not indiv_match:
            matches.append([[foreign_list_item,foreign_list_item,-1.0]])
        else:
            matches.append(sorted(indiv_match,key=lambda x:x[2],reverse=True))

    return matches


def entity_match(foreign_list,internal_list):      #feed list of foreign cities
    matches = []
    #print map(lambda x:str(x),foreign_hotel_list)
    for foreign_list_item in foreign_list:
        max = 0.0
        found = ''
        ratio=0.0
        for list_item in internal_list:
            #.replace('hotel','').replace(str(for_city).lower(),'').replace("&amp;","").replace(" and ","&")
            temp=Levenshtein.ratio(str(foreign_list_item).lower().strip().replace('/',' ').replace('-',' ').replace('(','').replace(')','').replace('saint ','st ').replace(' city','').replace('fort ','ft. '),str(list_item).lower().strip().replace('(','').replace(')','').replace(' city','').replace('/',' ').replace('-',' ').replace('saint ','st ').replace('fort ','ft. '))
            if temp>max:
                max = temp
                found = list_item
                ratio = temp

        if ratio < 0.8:
            for list_item in internal_list:
                if foreign_list_item.lower().strip().replace('/',' ').replace('-',' ').replace('(','').replace(')','').replace('saint ','st ').replace(' city','').replace('fort ','ft. ') in list_item.lower().strip().replace('/',' ').replace('-',' ').replace('(','').replace(')','').replace('saint ','st ').replace(' city','').replace('fort ','ft. ') and foreign_list_item.strip() != '':
                    temp =1.0
                    break

        matches.append([foreign_list_item,found,ratio])

    return matches



def normalize(name,city,region):
    city = city.lower()
    region = region.lower()
    name = name.lower()
    temp = ['(',')',',']
    if '-' in city: temp.extend(city.split('-'))
    if '-' in region: temp.extend(region.split('-'))
    temp.extend(city.split())
    temp.extend(region.split())
    temp_name = name
    
    for all in temp:
        temp_name=temp_name.replace(all.strip(),'')
        
    if not temp_name.strip():
        temp = ['(',')',',']
        for all in temp:
            name=str(name).replace(all.strip(),'')
    else:
        name = temp_name

    return name.replace('/','').replace('-','').replace('saint ','st ').replace(' city','').replace('fort ','ft. ').replace('hotel ','').replace(' hotel','').replace(' and ',' & ').lower().strip()



def hotel_name_match(foreign_list,internal_list,city_name,region_name,state_name):      #feed list of foreign cities

    #check if every word in foreign list is present in any hotel it is a match
    #break down the city - region name and clean up all the pieces from all hotel names
    #remove 'at' and 'by' 'and' 'spa'
    #get rid of state names as well
    region_name = " ".join(map(lambda x:x.strip(),region_name.split('-')))
    city_name = " ".join(map(lambda x:x.strip(),city_name.split('-')))
    city_name += ' '+state_name+ ' at '+' by '+' spa '+' and '+ ' on '+' not yet reported '
    matches = []
    #print map(lambda x:str(x),foreign_hotel_list)
    for foreign_list_item in foreign_list:
        max = 0.0
        found = ''
        ratio=0.0
        for list_item in internal_list:
            #.replace('hotel','').replace(str(for_city).lower(),'').replace("&amp;","").replace(" and ","&")
            temp=Levenshtein.ratio(normalize(foreign_list_item,city_name,region_name),normalize(list_item,city_name,region_name))
            if temp>max:
                max = temp
                found = list_item
                ratio = temp

        if ratio < 0.83:

            for list_item in internal_list:
                
                temp_list_item = normalize(list_item,city_name,region_name)
                flag = 0
                foregein_part = normalize(foreign_list_item,city_name,region_name).split()
                for every_part in foregein_part:
                    
                    for internal_hotel_part in temp_list_item.split():
                        if Levenshtein.ratio(every_part,internal_hotel_part) > 0.87:
                            flag += 1
                            break
                    

                if len(foregein_part) == flag:
                    found = list_item
                    ratio = 1.0
                    break

        matches.append([foreign_list_item,found,ratio])

    return matches

def spacial_cases(city_name,matches):
    city_name = city_name.strip().lower()
    if city_name =='strip south':
        return 'Las Vegas Strip Vicinity South'
    if city_name == 'airport midway mdw area':
        return 'Midway Airport North'
    if city_name == 'airport - south portland':
        return 'South Portland - Scarborough'
    if city_name == 'steamboat':
        return 'Steamboat Springs'
    if city_name == 'lansing - hammond':
        matches.append([city_name,'Hammond IN',1.0])
        return 'Holland - Lansing IL'
    if city_name == 'suffern - nanuet':
        return 'Mahwah - Ramsey - Allendale'
    return ''


def name_match(foreign_list,internal_list,city_name,region_name):      #feed list of foreign cities
    matches = []
    #print map(lambda x:str(x),foreign_hotel_list)
    for foreign_list_item in foreign_list:
        max = 0.0
        found = ''
        ratio=0.0
        temp = 0.0

        special = spacial_cases(foreign_list_item,matches)
        
        if special:
            matches.append([foreign_list_item,special,1.0])
            continue

        for list_item in internal_list:
                #.replace('hotel','').replace(str(for_city).lower(),'').replace("&amp;","").replace(" and ","&")
            temp=Levenshtein.ratio(normalize(foreign_list_item,city_name,region_name),normalize(list_item,city_name,region_name))
            if temp>max:
                    max = temp
                    found = list_item
                    ratio = temp

        if ratio < 0.7:
            for list_item in internal_list:
                #.replace('hotel','').replace(str(for_city).lower(),'').replace("&amp;","").replace(" and ","&")
                if normalize(foreign_list_item,city_name,region_name) and normalize(list_item,city_name,region_name) and (normalize(foreign_list_item,city_name,region_name) in normalize(list_item,city_name,region_name) or normalize(list_item,city_name,region_name) in normalize(foreign_list_item,city_name,region_name)):
                        temp=1.0
                        found = list_item
                        ratio = temp
                        break
                if normalize(foreign_list_item,'',region_name) and normalize(list_item,'',region_name) and (normalize(foreign_list_item,'',region_name) in normalize(list_item,'',region_name) or normalize(list_item,'',region_name) in normalize(foreign_list_item,'',region_name)):
                        temp=1.0
                        found = list_item
                        ratio = temp
                        break

        if ratio != 1.0:
            max = 0.0
            for list_item in internal_list:
                if 'airport' in normalize(foreign_list_item,city_name,region_name) and 'airport' in normalize(list_item,city_name,region_name):
                    temp=Levenshtein.ratio(normalize(foreign_list_item,city_name,region_name),normalize(list_item,city_name,region_name))
                    if temp>max:
                        max = temp
                        found = list_item
                        ratio = 1.0

                    
        matches.append([foreign_list_item,found,ratio])

    return matches


def get_citylist_db():
    Connection.cursor.execute("Select Cityid, City from cities order by 2")
    return Connection.cursor.fetchall()

def csv_format_new(name,delemiter_record,delemiter_field,file_name,hotel_index,state_index,city_index,region_index):

    return_dict={}
    
    for line in extract_content(file_name).split(delemiter_record):
        parts = line.split(delemiter_field)

        city = str(re.sub(', [A-Za-z][A-Za-z]', '', parts[city_index].lower().strip()))
        state = parts[state_index].lower().strip()
        region = str(re.sub(', [A-Za-z][A-Za-z]', '', parts[region_index].lower().strip()))
        hotel = parts[hotel_index].lower().strip().replace(' previously','')


        if state == 'dc':
            state = 'district of columbia'


        if return_dict.has_key(state) and state:
            if return_dict[state].has_key(city) and city:
                if return_dict[state][city].has_key(region.strip()):
                    return_dict[state][city][region.strip()].append(hotel)
                else:
                    return_dict[state][city][region.strip()]= [hotel]
            else:
                return_dict[state][city] = {}
                return_dict[state][city][region.strip()]= [hotel]
        else:
            return_dict[state]={}
            return_dict[state][city] = {}
            return_dict[state][city][region.strip()]= [hotel]
    
    matcher(return_dict)


def csv_format_test(name,delemiter_record,delemiter_field,file_name,hotel_index,state_index,city_index,region_index):
    return_dict={}
    count = 0
    for line in extract_content(file_name).split(delemiter_record):
        parts = line.split(delemiter_field)

        city = str(re.sub(', [A-Za-z][A-Za-z]', '', parts[city_index].lower().strip()))
        state = parts[state_index].lower().strip()
        region = str(re.sub(', [A-Za-z][A-Za-z]', '', parts[region_index].lower().strip()))
        hotel = parts[hotel_index].lower().strip().replace(' previously','')

        
        if state == 'dc':
            state = 'district of columbia'


        if return_dict.has_key(state) and state:
            if return_dict[state].has_key(city) and city:
                if return_dict[state][city].has_key(region.strip()):
                    return_dict[state][city][region.strip()].append(hotel)
                    count+=1
                else:
                    return_dict[state][city][region.strip()]= [hotel]
                    count+=1
            else:
                return_dict[state][city] = {}
                return_dict[state][city][region.strip()]= [hotel]
                count+=1
        else:
            return_dict[state]={}
            return_dict[state][city] = {}
            return_dict[state][city][region.strip()]= [hotel]
            count+=1
    print "Total Hotels to Match::" +str(count)
    return return_dict

    '''
    for state in return_dict.keys():
        print state
        for city in return_dict[state].keys():
            print '         '+str(city)
            for region in return_dict[state][city].keys():
                print '                 '+str(region)
              #  print '                         '+str(return_dict[state][city][region])
   '''

def csv_format(name,delemiter_record,delemiter_field,file_name,hotel_index,city_index,region_index):
    return_dict={}

    for line in extract_content(file_name).split(delemiter_record):
        parts = line.split(delemiter_field)
        if return_dict.has_key(parts[city_index]) and parts[city_index]:
        
            if return_dict[parts[city_index]].has_key(parts[region_index]) and parts[city_index]:
                return_dict[parts[city_index]][parts[region_index]].append(parts[hotel_index].replace(' previously',''))
            else:
                return_dict[parts[city_index]][parts[region_index]]= [parts[hotel_index].replace(' previously','')]
        else:
            return_dict[parts[city_index]]={}
            if parts[region_index] not in return_dict[parts[city_index]].keys():
                
                return_dict[parts[city_index]][parts[region_index]]= [parts[hotel_index].replace(' previously','')]

    #return dictionary for hotel list with city
    #return_dict is a dictionary of dictionaries going from [cities][regions] which stores the name of the hotels NOTE: ' ' - gives blank regions, '' - gives blank cities
    
    #match_results_new(return_dict,name)
      
           # print ' ----->> '+str(regions)
           # print '                     '+str(return_dict[cities][regions])
    return return_dict
   # match_results_new(return_dict,name)

def extract_content(file_name):
    f = open(file_name)
    content = f.read()
    f.close()
    return content

def get_regions_for_city(cityid,regions_dictionary):
    
    Connection.cursor.execute(''' SELECT DISTINCT PricelineRegionId,regionname FROM pricelineregions JOIN regionscitiesmap
        ON regionscitiesmap.priceline_regionid = pricelineregions.PricelineId
        WHERE regionscitiesmap.cities_cityid = %s
        '''% str(cityid))
    points_keys = Connection.cursor.fetchall()
    for p_key in points_keys:
        Connection.cursor.execute(''' SELECT * FROM pricelinepoints
            WHERE PricelineRegions_PricelineRegionId = %s  ''' % str(p_key[0]))
            #p_key[1] region name
        temp_list = delete_duplicate(map(list,Connection.cursor.fetchall()))
        if p_key[1] not in regions_dictionary.keys():
            regions_dictionary[p_key[1]] = ray_casting.make_region(p_key[1],map(lambda x:x[-2:], temp_list))

    return regions_dictionary

'''
get a dictiory of cities-regions-hotels
get all cityid
get all region name

'''

def retrive_hotel(hotelid_list):
    sql = "Select * from hotels where hotelid in "+str(map(str,hotelid_list)).replace('[','(').replace(']',')')
  #  print sql
    Connection.cursor.execute(sql)
    return Connection.cursor.fetchall()


def retrive_hotel_by_cityid(city_id):
    sql = "Select * from hotels where cities_cityid = "+str(city_id)
  #  print sql
    Connection.cursor.execute(sql)
    return Connection.cursor.fetchall()

def match_results_new(city_region_hotel,name):
 #   matched_file = open('output/'+str(name)+'_sucess.csv','w')
 #   unmatched_file = open('output/'+str(name)+'_failed.csv','w')
 #   result = {}

    

    # 1) Getndatabase cursors and setup
    #
    regions_dictionary ={}
    Connection.cursor.execute("Select * from pricelineregions")
    priceline_regions = Connection.cursor.fetchall()
    Connection.cursor.execute("Select * from region_hotel")
    region_hotel_mapper ={} #key region_id with value being hotels id

    # 2) Create map   RegionID -> HotelID
    #
    for region_hotel in Connection.cursor.fetchall():
        if region_hotel[1] in region_hotel_mapper.keys():
            region_hotel_mapper[region_hotel[1]].append(region_hotel[0])
        else:
            region_hotel_mapper[region_hotel[1]]=[region_hotel[0]]

    city_region_mapper={}   #key cities_id lists regionid
    Connection.cursor.execute("Select * from regionscitiesmap")

    # 3) Create map    CityID -> RegionID
    #
    for region_hotel in Connection.cursor.fetchall():
        if region_hotel[0] in city_region_mapper.keys():
            city_region_mapper[region_hotel[0]].append(region_hotel[1])
        else:
            city_region_mapper[region_hotel[0]]=[region_hotel[1]]

    # incorporate regionmapcities table in the implementation

    # 4) Region map   RegionName -> RegionID
    #  (original priceline regionname)
    #
    region_name_id = {}
    for regions in priceline_regions:
        if regions[2] in region_name_id.keys():
            region_name_id[regions[2]].append(regions[0])
        else:
            region_name_id[regions[2]]=[regions[0]]

    # 5) Region details maps   RegionID -> Region record (name,id, long,lat)
    #
    for regions in priceline_regions:
        if regions[1] in regions_dictionary.keys():
            regions_dictionary[regions[1]].append(regions)
        else:
            regions_dictionary[regions[1]]=[]
            regions_dictionary[regions[1]].append(regions)
    #print regions_dictionary.keys()
    #dictioanry of regions by regionid
    Connection.cursor.execute("Select * from cities")
    city_list = Connection.cursor.fetchall()
    city_dictionary ={}

    for city in city_list:
        if city[1] in city_dictionary.keys():
            city_dictionary[city[1]].append(city)
        else:
            city_dictionary[city[1]]=[city]

   # print city_dictionary
    matched ={}
    #dictionary of city

    write_log=open('output/matched_result.csv','w')
    unmatched_foreign_hotel_list = []

    # 7) For all cities in the input generate a
    #    match of possible cities
    #
    #
    for possible_matches in city_match(city_region_hotel.keys(),map(lambda x:x[1],city_list)):
        got_it = 0
        count = 0
        print 'GET ONE CITY '

        
        # 7b) 
        #
        for matched_city in possible_matches:
           print 'Testing City -- '
           print matched_city[1]
           needs_matching_region =[]
           needs_matching_city =[]
           temp_regions_list=[]
           print 'No. of regions in input'
           print len(city_region_hotel[matched_city[0]].keys())
           print city_region_hotel[matched_city[0]].keys()
           if matched_city[2] > 0.82 and matched_city[0]:
                for one in city_dictionary[matched_city[1]]:
                    if one[0] in city_region_mapper.keys():
                        for each_region in city_region_mapper[one[0]]:
                            temp_regions_list.extend( map(lambda x:x[2],regions_dictionary[ each_region  ]))
                print '     ' + str(temp_regions_list)
                
                for matched_regions in entity_match(city_region_hotel[matched_city[0]].keys(),temp_regions_list):
                    if matched_regions[2] > 0.82 and matched_regions[0]:
                        print 'MATCHED-->              '+ str(matched_regions)
                
                        for one in region_name_id[matched_regions[1]]:
                            if int(one) in region_hotel_mapper.keys():
                                hotel_list = map(lambda x:x[1],retrive_hotel(region_hotel_mapper[int(one)]))
                                if hotel_list:
                                    got_it =1
                                    for match_hotel in hotel_name_match(city_region_hotel[matched_city[0]][matched_regions[0]],hotel_list,matched_city[1],matched_regions[1]):
                                        #print match_hotel
                                        if match_hotel[0]+' , '+matched_city[0]+' , '+matched_regions[0] in matched.keys():
                                            if matched[match_hotel[0]+' , '+matched_city[0]+' , '+matched_regions[0]][0][2] ==1.0:
                                                continue
                                            if matched[match_hotel[0]+' , '+matched_city[0]+' , '+matched_regions[0]][-1][2] <= match_hotel[2]:
                                                if match_hotel not in matched[match_hotel[0]+' , '+matched_city[0]+' , '+matched_regions[0]]:
                                                    matched[match_hotel[0]+' , '+matched_city[0]+' , '+matched_regions[0]].append(match_hotel)
                                                        #print match_hotel
                                        else:
                                            if match_hotel[2]>0.83:
                                                if match_hotel in unmatched_foreign_hotel_list:
                                                    unmatched_foreign_hotel_list.pop(match_hotel)
                                                matched[match_hotel[0]+' , '+matched_city[0]+' , '+matched_regions[0]] = [match_hotel]
                                                       # print match_hotel
                                                           # write_log.write(','+ str(match_hotel).replace('[','').replace(']','')+ '\n')
                                            else:
                                                if match_hotel not in unmatched_foreign_hotel_list:
                                                    unmatched_foreign_hotel_list.append(match_hotel)
                                                not_matched = 1
                                else:
                                    not_matched = 1
                                            #print 'No hotels!!'
                                            #print str(matched_regions[0])+'--'+str(matched_city[0])
                                            #no hotels returned for the matched region
                            else:
                                not_matched = 1
                                        #print 'No Regions!!'
                                    #print str(matched_city[0])
                                    #City does not have regions associated with it
                    else:
                             # print matched_regions
                                #region cant be matched, so try with city only
                                #print 'Regions Not Matched!!'
                                #print str(matched_regions[0])+'--'+str(matched_city[0])
                        not_matched = 1
                       #City does not have regions associated with it
                if not_matched:
                    foreign_hotel_list = []
                     # print city_dictionary[matched_city[1]]
                       #temp_list = lambda x:city_region_hotel[matched_city[0]][x] ,city_region_hotel[matched_city[0]]
                    for reg in city_region_hotel[matched_city[0]].keys():
                        foreign_hotel_list.extend(city_region_hotel[matched_city[0]][reg])
                           #foreign_hotel_list.extend(temp_list)ched.keys()
                        for one in city_dictionary[matched_city[1]]:
                             for s_match in hotel_name_match(foreign_hotel_list,map(lambda x:x[1],retrive_hotel_by_cityid(one[0])),matched_city[1],''):
                                   if s_match[0]+' , '+matched_city[0] in matched.keys():
                                        if matched[s_match[0]+' , '+matched_city[0]][0][2] ==1.0:
                                            continue
                                        if matched[s_match[0]+' , '+matched_city[0]][-1][2] <= s_match[2]:
                                            if s_match not in matched[s_match[0]+' , '+matched_city[0]]:
                                                matched[s_match[0]+' , '+matched_city[0]].append(s_match)

                                   else:
                                        if s_match[2]>0.83:
                                            if s_match in unmatched_foreign_hotel_list:
                                                unmatched_foreign_hotel_list.pop(s_match)
                                            matched[s_match[0]+' , '+matched_city[0]] = [s_match]
                                        else:
                                            if s_match not in unmatched_foreign_hotel_list:
                                                unmatched_foreign_hotel_list.append(s_match)


                        not_matched = 0
                        needs_matching_city.append(matched_city[0])


         #  else:
                #no matched cities for hotel
          #      print matched_city[0]
       #         if matched_city[0]:
        #            for reg in city_region_hotel[matched_city[0]]:
        #                unmatched_foreign_hotel_list.append([city_region_hotel[matched_city[0]][reg],matched_city[0],reg])

    ##
    #    for entries in matched.keys():
    #        print('\n'+entries+'\n')
    #        for matching in matched[entries]:
    #            print matching
    ##
     #   if got_it!=1:
     #       print 'GOT___IT'
     #       print possible_matches

    for entries in matched.keys():
        #write_log.write('\n'+entries+'\n')
        for matching in matched[entries]:
            write_log.write(',,'+ str(matching).replace('[','').replace(']','')+ '\n')

    write_log.write('\n\n\n\n\n NOT MATCHED \n\n\n\n\n')
    for not_matched in unmatched_foreign_hotel_list:
        write_log.write(',,'+ str(not_matched).replace('[','').replace(']','')+ '\n')

    write_log.close()
            
        #print 'No. of regions matched'
        #print count

def match_hotels(region_id,foreign_hotel_list,present_internal_city,present_internal_region,state,log_write_hotels):

    count = 0
   # log_write_hotels = open('output/hotel_matches.csv','a')
    hotels_in_all_regions = region_hotel_finder(region_id)

    hotel_match_array = hotel_name_match(foreign_hotel_list,map(lambda x:x[1],hotels_in_all_regions),present_internal_city,present_internal_region,state)

    for hotel_matches in hotel_match_array:

        if hotel_matches[2] > 0.83 and hotel_matches[1]:
            log_write_hotels.write(',,,'+str(",".join(hotel_matches[:-1]))+'\n')
        else:
            print '\t\t\t\t' + str(hotel_matches)
            count+=1

         #   not_matched_hotel.append(hotel_matches[0])
   # log_write_hotels.write(',,,'+str(",".join(hotel_matches[:-1]))+'\n')
    log_write_hotels.write('\n,,,'+str('Hotel Matched : ' + str(len(hotel_match_array) - count)))
    log_write_hotels.write(','+str('Hotel Not Matched : ' + str(count))+'\n\n')
    print '\t\t\t\t Hotel Matched : ' + str(len(hotel_match_array) - count)
    print '\t\t\t\t Hotel Not Matched : ' + str(count)
    return count


    #current hotel

def test_matcher():

    test_log = open('output/hotel_matches.csv','w') #output/test_log222.txt

  #  print_log = open('output/db_city-region_pl.txt','a')

    [area_dictionary,exclude_city_list,state_region] = pl_area()

    [internal_state_city_region,state_region] = state_city(area_dictionary,exclude_city_list,state_region)


    '''
    for state in internal_state_city_region.keys():
        print_log.write( str(state)+'\n')
        for city in internal_state_city_region[state].keys():
            print_log.write( '\t'+str(city)+'\n')
            for region in internal_state_city_region[state][city].keys():
                print_log.write('\t\t'+str(region)+'\n')
            print_log.write('\n')
        print_log.write('\n')

    '''

    not_matched_regions_list = []
    not_matched_hotels_list = 0

    input = csv_format_test('hotels-bbpl4','~','#','output/hotels-bbpl3',3,0,1,2)

    # match every state

    for possible_matchs in entity_match(input.keys(),internal_state_city_region.keys()):

        test_log.write(str(possible_matchs[0])+'\n')

        #match cities
        print possible_matchs

        for possible_cities in city_match(input[possible_matchs[0]].keys(),internal_state_city_region[possible_matchs[1]].keys()):
            
            found_city = 0

            print '\t\t' + str(possible_cities)

            for cities in possible_cities:

                if found_city: break

                if cities[2] > 0.8:

                    test_log.write(','+str(cities[0])+'\n')

                    # if no regions match the city with the regions

                    if '' not in input[possible_matchs[0]][cities[0]].keys():

                        #match regions

                        for regions in name_match(input[possible_matchs[0]][cities[0]].keys(),internal_state_city_region[possible_matchs[1]][cities[1]].keys(),cities[1],possible_matchs[1]):

                            if regions[2] < 0.7:

                                if str(regions[0])+' '+str(cities[0])+' '+str(possible_matchs[0]) not in not_matched_regions_list:
                                    not_matched_regions_list.append(str(regions[0])+' '+str(cities[0])+' '+str(possible_matchs[0]))

                            else:
                                found_city = 1
                                if str(regions[0])+' '+str(cities[0])+' '+str(possible_matchs[0]) in not_matched_regions_list:
                                    not_matched_regions_list.remove(str(regions[0])+' '+str(cities[0])+' '+str(possible_matchs[0]))

                                region_id = internal_state_city_region[possible_matchs[1]][cities[1]][regions[1]]
                                foreign_hotel_list = input[possible_matchs[0]][cities[0]][regions[0]]
                                print "\t\t\t" +str(regions)
                                test_log.write(',,'+str(regions[0])+'\n')
                                not_matched_hotels_list += match_hotels(region_id,foreign_hotel_list,cities[1],possible_matchs[1],regions[1],test_log)
                               # not_matched_hotels_list.extend(teemp_not_hotel_list)

                            

                    else:

                        for f_regions in input[possible_matchs[0]][cities[0]].keys():

                            if f_regions:

                                temeeee = 0
                                if f_regions == 'airport okc':
                                    temeee = 1

                                for regions in name_match([f_regions],internal_state_city_region[possible_matchs[1]][cities[1]].keys(),cities[1],possible_matchs[1]):

                                    if regions[2] < 0.7:

                                        if str(regions[0])+' '+str(cities[0])+' '+str(possible_matchs[0]) not in not_matched_regions_list:
                                            not_matched_regions_list.append(str(regions[0])+' '+str(cities[0])+' '+str(possible_matchs[0]))

                                    else:
                                        found_city = 1
                                        if str(regions[0])+' '+str(cities[0])+' '+str(possible_matchs[0]) in not_matched_regions_list:
                                            not_matched_regions_list.remove(str(regions[0])+' '+str(cities[0])+' '+str(possible_matchs[0]))

                                        region_id = internal_state_city_region[possible_matchs[1]][cities[1]][regions[1]]
                                        foreign_hotel_list = input[possible_matchs[0]][cities[0]][regions[0]]
                                        print "\t\t\t" +str(regions)
                                        test_log.write(',,'+str(regions[0])+'\n')
                                        not_matched_hotels_list += match_hotels(region_id,foreign_hotel_list,cities[1],possible_matchs[1],regions[1],test_log)
                            else:
                                #acquare the hotel list

                                foreign_hotel_list = input[possible_matchs[0]][cities[0]][f_regions]

                                # when db has only one region for the specified city match it with it
                                if len(internal_state_city_region[possible_matchs[1]][cities[1]].keys()) == 1:

                                    temp_internal_region = internal_state_city_region[possible_matchs[1]][cities[1]].keys()[0]

                                    region_id = internal_state_city_region[possible_matchs[1]][cities[1]][temp_internal_region]

                                    match_hotels(region_id,foreign_hotel_list,cities[1],possible_matchs[1],'',test_log)

                                #if many region then match the region closet to the city name and then match the hotel list
                                else:

                                    for regions in name_match([cities[0]],internal_state_city_region[possible_matchs[1]][cities[1]].keys(),'',possible_matchs[1]):

                                        if regions[2] < 0.7:

                                            if str(regions[0])+' '+str(cities[0])+' '+str(possible_matchs[0]) not in not_matched_regions_list:
                                                not_matched_regions_list.append(str(regions[0])+' '+str(cities[0])+' '+str(possible_matchs[0]))

                                        else:
                                            found_city = 1
                                            if str(regions[0])+' '+str(cities[0])+' '+str(possible_matchs[0]) in not_matched_regions_list:
                                                not_matched_regions_list.remove(str(regions[0])+' '+str(cities[0])+' '+str(possible_matchs[0]))

                                            region_id = internal_state_city_region[possible_matchs[1]][cities[1]][regions[1]]
                                            foreign_hotel_list = input[possible_matchs[0]][cities[0]][f_regions]
                                            print "\t\t\t" +str(regions)
                                            test_log.write(',,'+str(regions[0])+'\n')
                                            not_matched_hotels_list += match_hotels(region_id,foreign_hotel_list,cities[1],possible_matchs[1],regions[1],test_log)



                                #no region for city in the input
                                #check how many regions are there for the corrosponding matched city in db
                                #if only one region, match the hotel list with that region

                            

                                
                else:
                    #city not matched
                    for possible_matches in city_match([cities[0]],state_region[possible_matchs[1]].keys()):

                        test_log.write(',,'+str(cities[0])+'\n')
                        for city_to_state_match in possible_matches:

                            print '\t\t\t' + str(city_to_state_match)

                            if city_to_state_match[2] > 0.7:

                                foreign_hotel_list = []

                                regions_string = ''

                                for all_region in  input[possible_matchs[0]][cities[0]].keys():
                                    foreign_hotel_list.extend(input[possible_matchs[0]][cities[0]][all_region])
                                    regions_string+=' '+str(all_region)

                                region_id = state_region[possible_matchs[1]][city_to_state_match[1]]
                                match_hotels(region_id,foreign_hotel_list,city_to_state_match[1],possible_matchs[1],regions_string,test_log)





        test_log.write('\n')

    print not_matched_regions_list
    print not_matched_hotels_list



def match_results(city_region_hotel,name):
 #   matched_file = open('output/'+str(name)+'_sucess.csv','w')
 #   unmatched_file = open('output/'+str(name)+'_failed.csv','w')
 #   result = {}
    regions_dictionary ={}
    Connection.cursor.execute("Select * from pricelineregions")
    priceline_regions = Connection.cursor.fetchall()
    Connection.cursor.execute("Select * from region_hotel")
    region_hotel_mapper ={} #key region_id with value being hotels id

    for region_hotel in Connection.cursor.fetchall():
        if region_hotel[1] in region_hotel_mapper.keys():
            region_hotel_mapper[region_hotel[1]].append(region_hotel[0])
        else:
            region_hotel_mapper[region_hotel[1]]=[region_hotel[0]]

    city_region_mapper={}   #key cities_id lists regionid
    Connection.cursor.execute("Select * from regionscitiesmap")

    for region_hotel in Connection.cursor.fetchall():
        if region_hotel[0] in city_region_mapper.keys():
            city_region_mapper[region_hotel[0]].append(region_hotel[1])
        else:
            city_region_mapper[region_hotel[0]]=[region_hotel[1]]

    # incorporate regionmapcities table in the implementation
    region_name_id = {}
    for regions in priceline_regions:
        region_name_id[regions[2]]=regions[0]

    for regions in priceline_regions:
        if regions[1] in regions_dictionary.keys():
            regions_dictionary[regions[1]].append(regions)
        else:
            regions_dictionary[regions[1]]=[]
            regions_dictionary[regions[1]].append(regions)
    #print regions_dictionary.keys()
    #dictioanry of regions by regionid
    Connection.cursor.execute("Select * from cities")
    city_list = Connection.cursor.fetchall()
    city_dictionary ={}

    for city in city_list:
        city_dictionary[city[1]]=city

    matched ={}
    #dictionary of city

    write_log=open('output/matched_result.csv','w')
    unmatched_foreign_hotel_list = []
    '''
    for possible_matches in city_match(city_region_hotel.keys(),map(lambda x:x[1],city_list)):
        if possible_matches:
           # write_log.write('\n\n'+str(possible_matches[0][0])+'\n')
            print 'START______'
            for matched_city in possible_matches:
        #   if matched_city[2] > 0.82 and matched_city[0]:
                write_log.write('Matched City::,'+str(matched_city[0])+','+str(matched_city[1])+','+str(matched_city[2])+'\n')
                temp_regions_list=[]
                print 'CITY:: '+str(matched_city[1])
                if city_dictionary[matched_city[1]][0] in city_region_mapper.keys():
                    for each_region in city_region_mapper[city_dictionary[matched_city[1]][0]]:
                        temp_regions_list.extend( map(lambda x:x[2],regions_dictionary[ each_region  ]))
                    print '     REGIONS:: '+str(temp_regions_list)
                    print city_region_hotel[matched_city[0]].keys()
                    for matched_regions in entity_match(city_region_hotel[matched_city[0]].keys(),temp_regions_list):
                        if matched_regions[2] >= 0.83:
                            print '         Matched Regions:' + str(matched_regions)
                            write_log.write( '\n REGIONS-->,,'+str(matched_regions[0])+','+str(matched_regions[1])+'\n')
            print '______END'
    write_log.close()
    
               got_it =1
               print matched_city
        if got_it !=1:
            print 'FAILEDDD'
            print possible_matches
        count+=1
        got_it = 0
    print count
    '''
   # print len(city_region_hotel.keys())
    
    for possible_matches in city_match(city_region_hotel.keys(),map(lambda x:x[1],city_list)):
        got_it = 0
        count = 0
      
        for matched_city in possible_matches:
           
           needs_matching_region =[]
           needs_matching_city =[]
           temp_regions_list=[]
           if matched_city[2] > 0.82 and matched_city[0]:
                if city_dictionary[matched_city[1]][0] in city_region_mapper.keys():
                    for each_region in city_region_mapper[city_dictionary[matched_city[1]][0]]:
                        temp_regions_list.extend( map(lambda x:x[2],regions_dictionary[ each_region  ]))
                    for matched_regions in entity_match(city_region_hotel[matched_city[0]].keys(),temp_regions_list):
                        if matched_regions[2] > 0.82 and matched_regions[0]:
                            
    
              # write_log.write('\n'+matched_city[1].replace(',','')+'\n')
               
                        #write_log.write('\n'+matched_city[1].replace(',','')+','+matched_regions[1].replace(',','')+'\n')
                       
                            #print region_name_id[matched_regions[1]]
                            #print region_hotel_mapper.keys()
                            if int(region_name_id[matched_regions[1]]) in region_hotel_mapper.keys():
                                hotel_list = map(lambda x:x[1],retrive_hotel(region_hotel_mapper[int(region_name_id[matched_regions[1]])]))
                                if hotel_list:
                                    got_it =1
                                    for match_hotel in hotel_name_match(city_region_hotel[matched_city[0]][matched_regions[0]],hotel_list,matched_city[1],matched_regions[1]):
                                        #print match_hotel
                                        if match_hotel[0]+' , '+matched_city[0]+' , '+matched_regions[0] in matched.keys():
                                            if matched[match_hotel[0]+' , '+matched_city[0]+' , '+matched_regions[0]][0][2] ==1.0:
                                                continue
                                            if matched[match_hotel[0]+' , '+matched_city[0]+' , '+matched_regions[0]][-1][2] <= match_hotel[2]:
                                                if match_hotel not in matched[match_hotel[0]+' , '+matched_city[0]+' , '+matched_regions[0]]:
                                                    matched[match_hotel[0]+' , '+matched_city[0]+' , '+matched_regions[0]].append(match_hotel)
                                                #print match_hotel
                                        else:
                                            if match_hotel[2]>0.83:
                                                if match_hotel in unmatched_foreign_hotel_list:
                                                    unmatched_foreign_hotel_list.pop(match_hotel)
                                                matched[match_hotel[0]+' , '+matched_city[0]+' , '+matched_regions[0]] = [match_hotel]
                                               # print match_hotel
                                                   # write_log.write(','+ str(match_hotel).replace('[','').replace(']','')+ '\n')
                                            else:
                                                if match_hotel not in unmatched_foreign_hotel_list:
                                                    unmatched_foreign_hotel_list.append(match_hotel)
                                                not_matched = 1
                                else:
                                    not_matched = 1
                                    #print 'No hotels!!'
                                    #print str(matched_regions[0])+'--'+str(matched_city[0])
                                    #no hotels returned for the matched region
                            else:
                                not_matched = 1
                                #print 'No Regions!!'
                                #print str(matched_city[0])
                                #City does not have regions associated with it
                        else:
                           # print matched_regions
                            #region cant be matched, so try with city only
                            #print 'Regions Not Matched!!'
                            #print str(matched_regions[0])+'--'+str(matched_city[0])
                            not_matched = 1
                   #City does not have regions associated with it
                if not_matched:
                   foreign_hotel_list = []
                  # print city_dictionary[matched_city[1]]
                   #temp_list = lambda x:city_region_hotel[matched_city[0]][x] ,city_region_hotel[matched_city[0]]
                   for reg in city_region_hotel[matched_city[0]].keys():    
                        foreign_hotel_list.extend(city_region_hotel[matched_city[0]][reg])
                   #foreign_hotel_list.extend(temp_list)ched.keys()
                   for s_match in hotel_name_match(foreign_hotel_list,map(lambda x:x[1],retrive_hotel_by_cityid(city_dictionary[matched_city[1]][0])),matched_city[1],''):
                       if s_match[0]+' , '+matched_city[0] in matched.keys():
                            if matched[s_match[0]+' , '+matched_city[0]][0][2] ==1.0:
                                continue
                            if matched[s_match[0]+' , '+matched_city[0]][-1][2] <= s_match[2]:
                                if s_match not in matched[s_match[0]+' , '+matched_city[0]]:
                                    matched[s_match[0]+' , '+matched_city[0]].append(s_match)
                                
                       else:
                            if s_match[2]>0.83:
                                if s_match in unmatched_foreign_hotel_list:
                                    unmatched_foreign_hotel_list.pop(s_match)
                                matched[s_match[0]+' , '+matched_city[0]] = [s_match]
                            else:
                                if s_match not in unmatched_foreign_hotel_list:
                                    unmatched_foreign_hotel_list.append(s_match)

                                
                   not_matched = 0
                   needs_matching_city.append(matched_city[0])
         #  else:
                #no matched cities for hotel
          #      print matched_city[0]
       #         if matched_city[0]:
        #            for reg in city_region_hotel[matched_city[0]]:
        #                unmatched_foreign_hotel_list.append([city_region_hotel[matched_city[0]][reg],matched_city[0],reg])

    ##
    #    for entries in matched.keys():
    #        print('\n'+entries+'\n')
    #        for matching in matched[entries]:
    #            print matching
    ##
     #   if got_it!=1:
     #       print 'GOT___IT'
     #       print possible_matches
        
    for entries in matched.keys():
        #write_log.write('\n'+entries+'\n')
        for matching in matched[entries]:
            write_log.write(',,'+ str(matching).replace('[','').replace(']','')+ '\n')

    write_log.write('\n\n\n\n\n NOT MATCHED \n\n\n\n\n')
    for not_matched in unmatched_foreign_hotel_list:
        write_log.write(',,'+ str(not_matched).replace('[','').replace(']','')+ '\n')

    write_log.close()
    
                      #exernal hotel list
                #else:
                 #   print 'FAIILLED'
           # for matched_regions in entity_match(city_region_hotel[matched_city[0]].keys(),):
           #     if matched_regions[2] > 0.82:
           #         print '__________'
           #         print matched_regions
           #         print '__________'
           # count+=1
           # print matched_city         full+=1
  #  print full
  #  print full - count
   # for cities in city_region_hotel.keys():
        #if cities:
           # print entity_match(city_region_hotel[cities].keys(),map(lambda x:x[2],priceline_regions))
            #for regions in city_region_hotel[cities].keys():
            #    if regions != ' ':


            
    '''

            out_city_list = query_db(cities)
            for city_list in out_city_list:
                regions_dictionary = get_regions_for_city(city_list[3],regions_dictionary)
            tantative_list = []
            for external_region in city_region_hotel[cities].keys():
                for our_region in regions_dictionary.keys():
                    print our_region
                    print external_region
                    if Levenshtein.ratio(our_region.lower(),external_region.lower()) > 0.7:
                        print '__PASSED__'
                        for our_list in out_city_list:
                            #print our_list
                            #print '________----------_________'
                            if ray_casting.ispointinside(Pt(x=our_list[4], y=our_list[5]),regions_dictionary[our_region]):
                                tantative_list.append(our_list)
                             #   print our_list

              #  print hotel_match(city_region_hotel[cities][external_region],tantative_list,cities)


    for city_htl in city_hotel.items():
        our_city_list = query_db(city_htl[0])
        if our_city_list:
            result[city_htl[0]]=hotel_match(city_htl[1],our_city_list,city_htl[0])

    for res_htl_city in result.keys():
        for lst in result[res_htl_city]:
            if lst[2] > 0.7:
                matched_file.write(lst[0].replace(',','')+','+lst[1].replace(',','')+','+str(lst[2])+'\n')
            else:
                unmatched_file.write(lst[0].replace(',','')+','+lst[1].replace(',','')+','+str(lst[2])+'\n')

    matched_file.close()
    unmatched_file.close()
    '''

def region_hotel_finder(region_id):

    Connection.cursor.execute("Select hotel_id from region_hotel where pl_region_id ="+ str(region_id))
    hotel_ids = Connection.cursor.fetchall()
    hotels = []

    hotel = '('
    for hotel_id in hotel_ids:
        hotel+=str(hotel_id[0])+','
    hotel=hotel[:-1]+')'
    

    if len(hotel)>1:
        Connection.cursor.execute("Select * from hotels where hotelid in "+str(hotel))

        for one in Connection.cursor.fetchall():
            hotels.append(one)
    
    return hotels


def find_state_by_city_id(city_id):

     Connection.cursor.execute("Select state from cities where cityid = "+str(city_id))

     return Connection.cursor.fetchall()[0][0]


def city_region_finder(cityid):     # Given a cityid this function returns an array of regions for the provided cityid (helper method for state_city())

    #1  get the regionids for a city
    Connection.cursor.execute("Select priceline_regionid from regionscitiesmap where cities_cityid ="+ str(cityid))
    region_ids = Connection.cursor.fetchall()
    region_hotel = {}

    #2  Iterate through the regionids to get the region name

    for region_id in region_ids:
        Connection.cursor.execute("Select Regionname,PricelineRegionId from pricelineregions where pricelineid = "+str(region_id[0]))

        #2a Construct an array of regions information for all the regionids in a city

        for one in Connection.cursor.fetchall():
            region_hotel[str(re.sub(', [A-Za-z][A-Za-z]', '', one[0]))]=one[1]
    
    return region_hotel


def get_city_regions_from_area(area_id):

    #dictionary to store area-region relationship

    area_region_dictionary = {}

    #a list of all the areas associated with the area

    area_city_list = []

    #a list of all states the area falls in

    area_state_list = []

    #1  get cities associated with the area_id

    Connection.cursor.execute("Select city_id from priceline_area_city where area_id ="+ str(area_id))

    #2  iterate through all the cities in the area

    for city_id in Connection.cursor.fetchall():

        city_id = city_id[0]

        #   2a update master dictionary with regions from each cities associated with it

        area_region_dictionary.update(city_region_finder(city_id).items())

        #   2b  keep a list of all the cities associated with the area

        area_city_list.append(city_id)

        #   2c  get all states the area is associated with (through city association)

        state = find_state_by_city_id(city_id)

        if state.lower() not in area_state_list:

            area_state_list.append(state.lower())

    return [area_region_dictionary,area_city_list,area_state_list]


def pl_area():

    #dictionary to store state-area relationship

    state_area_dictionary = {}

    #master city list that are associated with areas

    master_area_city_list = []

    #relate regions to states

    state_region = {}

    #1  get all the area from db

    Connection.cursor.execute("Select * from priceline_area")
    
    #2  iterate through all the area

    for area in Connection.cursor.fetchall():

        #for each area, get all the associated cities

        area_id = area[0]
        area_name = str(re.sub(', [A-Za-z][A-Za-z]', '', area[1])).lower()

        [area_dictionary_content,area_city_list,area_state_list] = get_city_regions_from_area(area_id)

        #store cities for each area iteration

        master_area_city_list.extend(area_city_list)

        #insert area_dictionary to appropriate state dictionary

        for state in area_state_list:

            state = state.lower()

            if state not in state_area_dictionary.keys():
                state_area_dictionary[state] = {}

            state_area_dictionary[state][area_name] = area_dictionary_content

            if state not in state_region.keys():
                state_region[state] = {}
            state_region[state].update(area_dictionary_content.items())

    return [state_area_dictionary,master_area_city_list,state_region]

def find_cities_not_in_pl():

    pl_city_list = []

    result_list = []

    Connection.cursor.execute("SELECT DISTINCT cities_cityid FROM regionscitiesmap UNION SELECT DISTINCT city_id FROM priceline_area_city")

    for city_id in Connection.cursor.fetchall():
        pl_city_list.append(str(city_id[0]))

    Connection.cursor.execute("select cityid from cities")

    for city_id in Connection.cursor.fetchall():
        if str(city_id[0]) not in pl_city_list:
            result_list.append(str(city_id[0]))

    return result_list


@print_timing
def state_city(area_dictionary,excluded_city_id,state_region):       #0  Function returns two dictionaries in an array one being the state_city dictionary and the other being a dictionary for city ids

    #1  state_city dictionary has states with many cities containing many regions from the internal db

    state_city=area_dictionary

    #2  city_id dictionary has city id needed for later processing accessable through the key format 'state_name|city_name'



    #3  area_city gives of city name and state info provided a city id

    area_city = {}

    #4  exclude cities already covered by in areas and not in pl

    cities_not_in_pl = find_cities_not_in_pl()

    excluded_city_id.extend(cities_not_in_pl)

    exclude_city_list = str(map(str,excluded_city_id)).replace('[','(').replace(']',')')

    Connection.cursor.execute("Select * from cities where cityid not in "+ exclude_city_list)

    for one in Connection.cursor.fetchall():
        #3a get all the cities information from db
        if one[2].lower() in state_city.keys():
            if one[1].lower() not in state_city[one[2].lower()].keys():

                #b  get all the regions in the value for the state-city dictionary

                state_city[one[2].lower()][one[1].lower()] = city_region_finder(one[0])

                area_city[one[0]] = str(one[2])+'|'+str(one[1])
                #c  store city id for later processing hashing 'state_name|city_name' key
                
        else:

            state_city[one[2].lower()] = {}
            state_city[one[2].lower()][one[1].lower()] = city_region_finder(one[0])
            area_city[one[0]] = str(one[2])+'|'+str(one[1])

        if one[2].lower() not in state_region.keys():
            state_region[one[2].lower()] = {}
        state_region[one[2].lower()].update(state_city[one[2].lower()][one[1].lower()].items())

    return [state_city,state_region]



def matcher(input):     #input is a dictionary of states containing many cities containing many regions containing many hotels


    log_write = open('output/bb-hotels.csv','a')
    log_write_hotels = open('output/hotel_match_list','a')
    #retrieve area-region information in a dictionary format and get a list of cities not to include (as already associated with certain area)

    [area_dictionary,exclude_city_list,state_region] = pl_area()

    [internal_state_city_region,city_ids] = state_city(area_dictionary,exclude_city_list,state_region)
    
    count=0
     #first iterate through the content for a single state

    for one in entity_match(input.keys(),internal_state_city_region.keys()):

        #the 'one' is an array in the format of [foreign_state,internal_state,match_ratio]
        
        present_foreign_state = one[0]
        present_internal_state = one[1]

        #assigning current state dictionaries for the internal and foreign state to local variables

        foreign_city_dictionary = input[present_foreign_state]

        #for the present state, grab cities and regions from the database

        internal_city_dictionary = internal_state_city_region[present_internal_state]

        #match all the cities in the state with the foreign city list in the present state

        for possible_cities in entity_match(foreign_city_dictionary.keys(),internal_city_dictionary.keys()):

            #possible_matches is a list of possible city matches with each foreign city
            
            if possible_cities[2]>0.83:
            #for matched_city in possible_cities:
                
                #matched_city is an array of one possible match for a particular foreign city in the format [foreign_city, internal_city, match_ratio], where match_ratio = -1 means no match

                #if any possible matches are found

            #    if matched_city[2] != -1.0:

                    #assigning current city dictionaries for the internal and foreign city to local variables
                    
                    present_foreign_city = possible_cities[0]#matched_city[0]
                    present_internal_city = possible_cities[1]#matched_city[1]
                    
                    internal_region_dictionary = internal_city_dictionary[present_internal_city]
                    foreign_region_dictionary = foreign_city_dictionary[present_foreign_city]


                    #if matched, try region matching
                    
                    for possible_regions in name_match(foreign_region_dictionary.keys(),internal_region_dictionary.keys(),present_internal_city,''):

                        hotels_in_all_regions = []
                        foreign_hotel_list=[]


                        if possible_regions[2]>0.65 and possible_regions[0]:
                        #for matched_region in possible_regions:

                        #    if matched_region[2] != -1.0:

                                present_foreign_region = possible_regions[0]#matched_region[0]
                                present_internal_region = possible_regions[1]#matched_region[1]

                                foreign_hotel_list = foreign_region_dictionary[present_foreign_region]
                                region_id = internal_region_dictionary[present_internal_region]
                                hotels_in_all_regions.extend(region_hotel_finder(region_id))

                                for hotel_matches in hotel_name_match(foreign_hotel_list,map(lambda x:x[1],hotels_in_all_regions),present_internal_city,present_internal_region):

                                    if hotel_matches[2] > 0.83 and hotel_matches[1]:
                                        log_write_hotels.write(str(hotel_matches)+'\n')
                                        count+=1

                        else:
                            if not possible_regions[0]:
                                for possible_regions in name_match([present_foreign_city],internal_region_dictionary.keys(),present_internal_city,''):
                                    hotels_in_all_regions = []
                                    foreign_hotel_list=[]


                                    if possible_regions[2]>0.65 and possible_regions[0]:
                                    #for matched_region in possible_regions:

                                    #    if matched_region[2] != -1.0:

                                            present_foreign_region = possible_regions[0]#matched_region[0]
                                            present_internal_region = possible_regions[1]#matched_region[1]

                                            foreign_hotel_list = foreign_region_dictionary['']
                                            region_id = internal_region_dictionary[present_internal_region]
                                            hotels_in_all_regions.extend(region_hotel_finder(region_id))

                                            for hotel_matches in hotel_name_match(foreign_hotel_list,map(lambda x:x[1],hotels_in_all_regions),present_internal_city,present_internal_region):

                                                if hotel_matches[2] > 0.83 and hotel_matches[1]:
                                                    log_write_hotels.write(str(hotel_matches)+'\n')
                                                    count+=1

                                    else:
                                        
                                        log_write.write( 'REGION NOT FOUND:: '+str(possible_regions)+'  in area/city(internal) '+str(present_internal_city)+' in area/city(external) '+str(present_foreign_city)+'\n')
                                        log_write.write( 'REGION NOT FOUND:: '+str(internal_region_dictionary.keys())+'\n')
                            else:
                                log_write.write( 'REGION NOT FOUND:: '+str(possible_regions)+'  in area/city(internal) '+str(present_internal_city)+' in area/city(external) '+str(present_foreign_city)+'\n')
                                log_write.write( 'REGION NOT FOUND:: '+str(internal_region_dictionary.keys())+'  in state '+str(present_internal_state)+'\n')
                                #No region matches
                        

                    
            else:
                log_write.write('CITY NOT FOUND:: '+str(possible_cities)+'\n')
                    #No City matches were Found

                        #grab hotels in the region and then match the hotels

                    #if region matching failed, try matching with all the hotels in the city

                    #if unsucessful, move onto next phase

                #if failed, try matching region name from the input with the cities and regions in db

    print count

#3348

    
@print_timing
def main():
  #  test_dictionary()
  # print pl_area()
   #print get_city_regions_from_area(16)
   #proceesed_matching()
    #get_regions_for_city(168)
   # test_area()
    #csv_format('bbhw-hotels','~',';','output/bbhw-hotels',2,0)
    #csv_format('bbpl-hotels','~',';;','output/bbpl-hotels',2,0,1)
  # print matcher_for_bb_bft.name_match(['yakima','wenatchee'], ['Yakima','Ellensburg','Wenatchee'], 'wenatchee - yakima', 'washington')
    normalize('hyatt regency boston financial','quincy market - faneuil hall - financial','Boston Massachusetts')
    test_matcher()
  #  csv_format_new('hotels-bbpl2','~','#','output/hotels-bbpl2',3,0,1,2)
    #csv_format('bftpl-hotels','~',';;','output/bbpl-hotels',2,0)

def word_specific_matcher(hotel_to_match,match_list,log_file):

    hotel_name = hotel_to_match[2]
    hotel_words = hotel_name.lower().split()
    hotel_words.extend(hotel_to_match[1].lower().replace('&amp;','').split())
    match_result=[]
    log_file.write(str(hotel_to_match[2]).replace(',',' ')+' -- '+str(hotel_to_match[1]).replace(',',' ')+'\n')
    log_file.write('Choices::\n')
    for match in match_list:
        words_to_match = match.split(';;')[1].lower().replace('&amp;','').split()
        region =  match.split(';;')[6]
        if 'No region match' not in region:
            words_to_match.extend(region.lower().split())
        score=0.0
        for words in hotel_words:
            max=0.0
            for match_word in words_to_match:
                tmp = Levenshtein.ratio(words,match_word)
                if tmp > max:
                    max=tmp
            score+=max
        match_result.append([match.split(';;')[1],hotel_name,score/len(hotel_words),region])
        
        log_file.write(','+str(match.split(';;')[1]).replace(',',' ')+' -- '+str(region).replace(',',' ')+'\n')
    
    res = sorted(match_result,key=lambda x: x[2],reverse=True)[0]
    if res[2] > 0.6:
        log_file.write('Resulting Match: '+str(res[0]).replace(',',' ')+' -- '+ str(res[3]).replace(',',' ')+'\n\n')
    else:
        log_file.write('??not matching with:  '+str(res[0]).replace(',',' ')+' -- '+ str(res[3]).replace(',',' ')+'\n\n')
   # print '_____RESULT______'
   # print hotel_to_match
    return res


def proceesed_matching():
    content = extract_content('output/hotel_choices')
    log_file=open('output/refined_matching.csv','w')
    for every_match in content.split('@'):
        hotel_info=every_match.split('~')
        if hotel_info:
            foreign_hotel = hotel_info[0].split(';;')
            probable_hotel = hotel_info[1:]
            if foreign_hotel and probable_hotel:
               # print '_____TEST___'
               # print str(foreign_hotel[2]) + ' -- '+str(foreign_hotel[1])
               # print probable_hotel
                print word_specific_matcher(foreign_hotel,probable_hotel,log_file)
              #  print '___END____'
    log_file.close()


def test_dictionary():

    file_write = open('output/city-region','a')
    [area_dictionary,exclude_city_list,state_region] = pl_area()

    [internal_state_city_region,state_region] = state_city(area_dictionary,exclude_city_list,state_region)


    for states in internal_state_city_region.keys():
        file_write.write(str(states)+'\n')
        for cities in internal_state_city_region[states].keys():
            file_write.write( '     '+str(cities)+'\n')
            for regions in internal_state_city_region[states][cities].keys():
                file_write.write('         '+str(regions)+'\n')

@print_timing
def old_main():
    fi = open('output/bbhw-hotels')
    matched_file = open('sucess.csv','w')
    unmatched_file = open('failed.csv','w')
    line = fi.read().split('~')
    #cities = []
    city_hotel = {}
    for l in line:
        parts = l.split(';')
        #if parts[0] not in cities:
         #   cities.append(parts[0])
        #print parts
        if parts[2] != 'REVIEW' and parts[2] != 'OR' and parts[2]:
            if city_hotel.has_key(parts[0]) and parts[0]:
                city_hotel[parts[0]].append(parts[2].replace(' previously',''))
            else:
                if parts[0]:
                    city_hotel[parts[0]]= [parts[2].replace(' previously','')]

    
    result = {}
    for city_htl in city_hotel.items():
        our_city_list = query_db(city_htl[0])
        if our_city_list:
            #print our_city_list[2]
            #try:
           # print city_htl
            result[city_htl[0]]=hotel_match(city_htl[1],our_city_list,city_htl[0])
            #except:
             #  print our_city_list
    
    for res_htl_city in result.keys():
       # print res_htl_city
        for lst in result[res_htl_city]:
            if lst[2] > 0.7:
                matched_file.write(lst[0].replace(',','')+','+lst[1].replace(',','')+','+str(lst[2])+'\n')
            else:
                unmatched_file.write(lst[0].replace(',','')+','+lst[1].replace(',','')+','+str(lst[2])+'\n')
       # print '\n'

    matched_file.close()
    unmatched_file.close()
    #print count
            #print 'not aval for '+ str(city)
    


if __name__ == '__main__':
        main()