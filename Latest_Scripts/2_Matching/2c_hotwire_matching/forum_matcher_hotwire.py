import Levenshtein
import re
import time
import sys
import pdb

sys.path.insert(0, "/home/areek/Documents/fetchopia/backend_git/sql/alchemy/" )

import logging
logging.basicConfig(filename='forum_matcher.log',filemode='w',level=logging.DEBUG)

from sqlalchemy import distinct
from alchemy_session import get_alchemy_info
'''
from city_table import CityTable
from priceline_city_region_map import PricelineCityRegionMap
from priceline_regions_table import PricelineRegionTable
from priceline_regions_table2 import PricelineRegionTable_update
from priceline_area_city_table import PricelineAreaCityTable
from priceline_area_table import PricelineAreaTable
from processed_forum_data5 import ProcessedRawForumData2
from priceline_region_hotel_map2 import PricelineRegionHotelMap
from unmatched_forum_hotel_table2 import UnmatchedForumHotelTable
from possible_forum_hotel_match2 import PossibleForumHotelMatchTable
from matched_forum_hotel_table2 import MatchedForumHotel2
'''

from hotwire_tables import *

from canon_hotel import CanonicalHotel


(engine, session,Base, metadata) = get_alchemy_info()

INTERNAL_STATE_CITY_REGION_DICT = {}

state_code_dict = {}
with open('us_state_code','r') as f:
	for content in f.read().split('\n'):
		fields = content.split('\t')
		if len(fields) == 2:
			state,code = fields
			state_code_dict[str(code)] = str(state)
	state_code_dict[str('DC')] = str('District of Columbia')

def hotwire_area():
	
	return_dict = []
	
	for record in session.query(Neighborhood).all():
	
		(uid,region_name,city,state) = (record.uid,record.name,record.city,record.state)
		state = str(state)
		city = str(city)
		region_name = str(region_name)
		
		if state not in state_code_dict.keys():
			continue
		
		else:
		
			if return_dict.has_key(state) and state:
				
				if return_dict[state].has_key(city) and city:
					
					return_dict[state][city] = region_name
				
				else:
					
					return_dict[state][city] = region_name
			
			else:
				return_dict[state] = {}
				return_dict[state][city] = region_name
	return return_dict










def print_timing(func):

    #A function that gives the runtime of a function

    def wrapper(*arg):
        t1 = time.time()
        res = func(*arg)
        t2 = time.time()
        print '%s took %0.3f ms' % (func.func_name, (t2-t1)*1000.0)
        return res
    return wrapper

def city_region_finder(cityid):

    # Given a cityid this function returns an array of regions for the provided cityid (helper method for state_city())

    #1  get the regionids for a city

    region_ids = session.query(PricelineCityRegionMap_canada).filter(PricelineCityRegionMap_canada.city_id == int(cityid)).all()
    priceline_region_ids =map(lambda x:x.priceline_region_id,region_ids)# .priceline_region_id
    region_hotel = {}

    #2  Iterate through the regionids to get the region name

    for region_id in priceline_region_ids:

        priceline_region_record = session.query(PricelineRegionTable_canada).filter(PricelineRegionTable_canada.uid == region_id).all()

        #2a Construct an array of regions information for all the regionids in a city

        for one in priceline_region_record:
            region_hotel[str(re.sub(', [A-Za-z][A-Za-z]', '', one.name))]=one.uid

    return region_hotel



def extract_content(file_name):

    # helper function for get_scraped_data_from_db, opens the file given as perameter and returns the content of the file

    f = open(file_name)
    content = f.read()
    f.close()
    return content

def retrive_raw_scraped_from_db():

    return session.query(ProcessedRawForumData_canada).all()



def get_scraped_data_from_db():

    #helper method for test_matcher function, it organizes the content from the scraped data into dictionaries of dictionaries (State => City/Area => Region => hotels)

    return_dict={}

    count = 0

    for record in retrive_raw_scraped_from_db():

        (uid,hotel,city,region,state,url) = (record.uid,record.hotel_name,record.city_area,record.region,record.state,record.url)#map(lambda x:str(x).strip(),line)

        hotel = hotel.replace('previously','').strip()

        if not hotel: continue
        
        if return_dict.has_key(state) and state:

            if return_dict[state].has_key(city) and city:

                if return_dict[state][city].has_key(region.strip()):

                    return_dict[state][city][region.strip()].append((hotel,url,uid))
                    count+=1

                else:

                    return_dict[state][city][region.strip()]= [(hotel,url,uid)]
                    count+=1

            else:

                return_dict[state][city] = {}
                return_dict[state][city][region.strip()]= [(hotel,url,uid)]
                count+=1

        else:

            return_dict[state]={}
            return_dict[state][city] = {}
            return_dict[state][city][region.strip()]= [(hotel,url,uid)]
            count+=1

#    print "Total Hotels to Match::" +str(count)
    return return_dict

def entity_match_normalize(input):

    #helper function for entity_match and city_match functions, it strips out words in city/area/state names, before being matched

    return str(input).lower().strip().replace('/',' ').replace('-',' ').replace('(','').replace(')','').replace('saint ','st ').replace(' city','').replace('fort ','ft. ')

def entity_match(foreign_list,internal_list):

    #helper function for test_matcher function. This function is used to match a list of states.

    #this method is straight-forward, for all given foreign list (from scraped forum data) items it tries to find the best match from the internal list (from db)

    #the entry with the highest ratio is inserted into a list that is returned by this method.

    #if the highest ratio is < 0.8, then it is checked whether the whole name resides in the list of internal entity names, if it does then,
    #it is considered to be a match as well (it is hacked to give a perfect match of 1)

    matches = []
 
    for foreign_list_item in foreign_list:

        max = 0.0
        found = ''
        ratio=0.0

        for list_item in internal_list:

            temp=Levenshtein.ratio(entity_match_normalize(foreign_list_item),entity_match_normalize(list_item))

            if temp>max:

                max = temp
                found = list_item
                ratio = temp

        if ratio < 0.8:

            for list_item in internal_list:

                if entity_match_normalize(foreign_list_item) in entity_match_normalize(list_item) and foreign_list_item.strip() != '':

                    temp =1.0
                    found = list_item
                    break

        matches.append([foreign_list_item,found,ratio])

    return matches


def city_match(foreign_list,internal_list):

    matches = []

    #helper function for test_matcher function. This function is used to match a list of city/area. It is to be noted that one city/area in question, could be matched with multiple city/area from the db

    #1  first check if given foreign list matches closely with the db relevant city list (it is considered a match if an item has a match ratio of more then 0.9)

    #2  if no match is found, then check if the foreign list item is a substring of any city in the relevant db city list

    #3  if still no match is found, then split the foreign city name by ' - ' (if any) and try to look for matches for all portion of the foreign city name

    #4  if no match is found even now, then split the foreign city name into individual words and then try to find a match for individual words in the relevant db city list

    #POTENTIAL BUG! :in 3,4 the area names which have common city names will be considered as matched!

    for foreign_list_item in foreign_list:

        #this contains the matches for each foreign city/area names

        indiv_match =[]

        #this contains the all the word(s) separated by '-' in city/area names

        temp_name = []

        #this contains all individual words in city/area names

        temp_name_space = []

        if '-' in foreign_list_item:
            temp_name = foreign_list_item.split('-')

        if ' ' in foreign_list_item:
            temp_name_space = foreign_list_item.split()

        #1
        for list_item in internal_list:
        
            x = entity_match_normalize(foreign_list_item)
            y = entity_match_normalize(list_item)
            x = unicode(x)
            y = unicode(y)

            temp=Levenshtein.ratio(x,y)

            if temp > 0.90:

                indiv_match.append([foreign_list_item,list_item,temp])

        #2
        if not indiv_match:

            for list_item in internal_list:

                if list_item.strip() and foreign_list_item.strip():

                    if list_item.lower() in foreign_list_item.lower() or foreign_list_item.lower() in list_item.lower():

                        temp=1.0
                        indiv_match.append([foreign_list_item,list_item,temp])


        #This is a list of words not considered to help while doing part by part matching of names

        unwanted_word_list_in_names = ['','-','/','south','north','west','east']

        #3
        if not indiv_match and temp_name:

            for list_item in internal_list:

                is_in = 0

                for one in temp_name:

                    if one.strip() not in unwanted_word_list_in_names:
                      x = entity_match_normalize(one)
                      y = entity_match_normalize(list_item)
                      x = unicode(x)
                      y = unicode(y)

                      temp=Levenshtein.ratio(x,y)

                      if temp > 0.9:

                          is_in = 1

                for a in temp_name:

                    if a in list_item and a not in unwanted_word_list_in_names:

                        temp =1.0
                        is_in = 1
                        break

                if is_in:

                    indiv_match.append([foreign_list_item,list_item,1.0])

        #4
        if not indiv_match and temp_name_space:

            for list_item in internal_list:

                is_in = 0

                for one in temp_name_space:

                    if one not in unwanted_word_list_in_names:
                    	
                    	x = entity_match_normalize(one)
                    	y = entity_match_normalize(list_item)
                    	x = unicode(x)
                    	y = unicode(y)

                        temp=Levenshtein.ratio(x,y)

                        if temp > 0.9:

                            is_in = 1

                for a in temp_name_space:

                    if a in list_item and a not in unwanted_word_list_in_names:

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


def spacial_cases(city_name,matches):
    
    #this function is a helper function for the region name matcher function. this is a list of names which are forced to match with the input.
    
    #this function can be extended in the future to take into accout human input to matching regions

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


def normalize(name,city,region):

    #this function is a helper function for region_name_match, this function normalizes the region names, given its city/area and state name

    #first it splits the region city/area and state names into individual words, then strips out each one of those words from the region name

    #if after striping all the relevant words from the region name, the name does not contain any words at all it is restored back to its original state
    #this occurs when the region name is the same as the name the city/area it is in

    city = city.lower()
    region = region.lower()
    name = name.lower()

    temp = ['(',')',',']

    if '-' in city: temp.extend(city.split('-'))
    temp.extend(city.split())

    if '-' in region: temp.extend(region.split('-'))
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

    return name.replace('/','').replace('-','').replace('saint ','st ').replace(' city','').replace('fort ','ft. ').replace('hotel ','').replace(' hotel','').replace(' and ',' & ').strip()


def region_name_match(foreign_list,internal_list,city_name,state_name):

    #this is a helper function for test_matcher. Given a list of regions, with its city/area and state name, this function returns a list of matched region names

    #1   this method takes into accout for special cases, which forecably matches one entry with a specific region from the db

    #2   At first, each name is normalized to strip out names of city/area or state it belonges to (this ensures more effective string matching). Then it is checked if it matches with any entry in the db region list

    #3   if the maximum match ratio is below 0.7, then probably a correct match was not found

    #4   then it is checked whether a substring of the normalized region name is found in any of the entries from the db list

    #5   the same check is done using parial normalized region name (which does not strip the city/area name of a region), as sometimes a region name can be the same as the name of the city/area it is in

    #6   if the region has 'airport' in its name, then only the region names containing 'airport' from the db is compared to find a match

    matches = []

    for foreign_list_item in foreign_list:

        max = 0.0
        found = ''
        ratio=0.0
        temp = 0.0

        #1

        special = spacial_cases(foreign_list_item,matches)

        if special:

            matches.append([foreign_list_item,special,1.0])
            continue

        #2

        for list_item in internal_list:
            x = normalize(foreign_list_item,city_name,state_name)
            y = normalize(list_item,city_name,state_name)
            x = unicode(x)
            y = unicode(y)	
            temp=Levenshtein.ratio(x,y)

            if temp > max:
                    max = temp
                    found = list_item
                    ratio = temp

        #3

        if ratio < 0.7:

            for list_item in internal_list:

                normalized_foreign_item = normalize(foreign_list_item,city_name,state_name)

                normalized_internal_item = normalize(list_item,city_name,state_name)

                partial_normalized_foreign_item = normalize(foreign_list_item,'',state_name)

                partial_normalized_internal_item = normalize(list_item,'',state_name)

                #4

                if ( normalized_foreign_item and normalized_internal_item ) and ( normalized_foreign_item in normalized_internal_item or normalized_internal_item in normalized_foreign_item ):

                    temp=1.0
                    found = list_item
                    ratio = temp
                    break

                #5

                if ( partial_normalized_foreign_item and partial_normalized_internal_item ) and ( partial_normalized_foreign_item in partial_normalized_internal_item or partial_normalized_internal_item in partial_normalized_foreign_item):

                    temp=1.0
                    found = list_item
                    ratio = temp
                    break

            #6

            if ratio != 1.0:

                max = 0.0

                for list_item in internal_list:

                    if 'airport' in normalize(foreign_list_item,city_name,state_name) and 'airport' in normalize(list_item,city_name,state_name):
                        x = normalize(foreign_list_item,city_name,state_name)
                        y = normalize(list_item,city_name,state_name)
                        x = unicode(x)
                        y = unicode(y)

                        temp=Levenshtein.ratio(x,y)

                        if temp > max:
                            
                            max = temp
                            found = list_item
                            ratio = 1.0


        matches.append([foreign_list_item,found,ratio])

    return matches


def region_hotel_finder(region_id):

    hotel_ids = session.query(PricelineRegionHotelMap_canada.hotel_id).filter(PricelineRegionHotelMap_canada.priceline_region_id == region_id )

    #   extract hotel_ids from query
    
    hotel_ids = tuple(map(lambda x: x[0],hotel_ids))

    region_name = session.query(PricelineRegionTable_canada.name).filter(PricelineRegionTable_canada.uid == region_id).one()[0]

    hotels = ()

    if len(hotel_ids) > 0:

        #	changed
        
        hotels = session.query(CanonicalHotel).filter( CanonicalHotel.uid.in_( hotel_ids ) )
        #hotels = session.query(Hotel).filter( Hotel.hotel_id.in_( hotel_ids ) )

    return (hotels,region_name)




def hotel_name_match(foreign_list,internal_list,city_name,region_name,state_name):      #feed list of foreign cities

    #this function is a helper function the match hotels function.
    
    #Given a list of hotels and their city,region and state name, the function tries to match the hotels up with the corrosponding list in the db

    #1  First the city/area, region and state name are broken down to individual words and some other misleading words are added so that they are striped out of the hotel name

    #2  at first, every foreign hotel is attemped to be matched with one of the entries in the relevant db hotel list

    #3  if the maximum match ratio is less then 0.83, then it is considered that it was not matched properly

    #4  then, each word of the normalized foreign hotel name is attempted to match each word of every hotel in the relevant db hotel list

    #5  if all the individual words of an entity is matched, then it is considered that the foreign hotel is matched

    #1

    region_name = " ".join(map(lambda x:x.strip(),region_name.split('-')))
    city_name = " ".join(map(lambda x:x.strip(),city_name.split('-')))
    city_name += ' '+state_name+ ' at '+' by '+' spa '+' and '+ ' on '+' not yet reported '

    
    matches = []

    for foreign_list_item in foreign_list:

        max = 0.0
        found = ''
        ratio=0.0

        #2

        #   Keep track of all the matches for a hotel

        temporary_match_list = []

        for list_item in internal_list:
	    
	    x = normalize(foreign_list_item,city_name,region_name)
	    y = normalize(list_item,city_name,region_name)
	    x = unicode(x)
	    y = unicode(y)	
            temp=Levenshtein.ratio(x,y)
            temporary_match_list.append([foreign_list_item,list_item,temp])

            if temp>max:

                max = temp
                found = list_item
                ratio = temp

        #3

        if ratio < 0.83:

            temporary_match_list = sorted(temporary_match_list,key=lambda matches: matches[2],reverse=True)

            if len(temporary_match_list) > 4:

                temporary_match_list = temporary_match_list[0:4]


            for list_item in internal_list:

                temp_list_item = normalize(list_item,city_name,region_name)
                flag = 0
                foregein_part = normalize(foreign_list_item,city_name,region_name).split()

                #4

                for every_part in foregein_part:

                    for internal_hotel_part in temp_list_item.split():
                    	every_part = unicode(every_part)
                    	internal_hotel_part = unicode(internal_hotel_part)    

                        if Levenshtein.ratio(every_part,internal_hotel_part) > 0.87:

                            flag += 1
                            break

                #5

                if len(foregein_part) == flag:

                    found = list_item
                    ratio = 1.0
                    break

        matches.append([foreign_list_item,found,ratio,temporary_match_list])

    return matches


def check_entry_listed_as_unmatched(db_record):

    #   checks if a hotel entry was marked as unmatched before

    #   returns true if entry exists or false otherwise

    #   param is a tuple => (input_hotel_name,str(city_id),str(area_id),source_forum,target_site)

    (forum_hotel_id,city_id,area_id,source_forum, target_site) = db_record
    record = session.query(UnmatchedForumHotelTable_canada).filter(UnmatchedForumHotelTable_canada.forum_hotel_id == forum_hotel_id).filter(UnmatchedForumHotelTable_canada.city_id == city_id)\
    .filter(UnmatchedForumHotelTable_canada.area_id == area_id).filter(UnmatchedForumHotelTable_canada.source_forum == source_forum).filter(UnmatchedForumHotelTable_canada.target_site == target_site).first()

    return (record != None)


def fetch_unmatched_entry_list_id(db_record):

    #   fetches the key id for the unmatched entry in question

    #   param is a tuple => (input_hotel_name,city_id,area_id,source_forum,target_site)

    (forum_hotel_id,city_id,area_id,source_forum, target_site) = db_record

    record = session.query(UnmatchedForumHotelTable_canada.uid).filter(UnmatchedForumHotelTable_canada.forum_hotel_id == forum_hotel_id).filter(UnmatchedForumHotelTable_canada.city_id == city_id)\
    .filter(UnmatchedForumHotelTable_canada.area_id == area_id).filter(UnmatchedForumHotelTable_canada.source_forum == source_forum).filter(UnmatchedForumHotelTable_canada.target_site == target_site).first()

    return record[0]


def insert_unmatched_entry_to_db(db_record):

    #   inserts an entry to the unmatched hotel table and returns the row_id for the inserted entry

    #   param format (input_hotel_name, city_id, area_id, region_id,source_forum,target_site,url)

    #global session

    (hotel_name,city_id,area_id,region_id,source_forum,target_site,url) = db_record

    unmatched_record = UnmatchedForumHotelTable_canada(hotel_name,city_id,area_id,region_id,source_forum,target_site,url)

    session.add(unmatched_record)
    session.commit()


def insert_possible_matches_for_unmatched_entries(db_record):

    #   inserts possible matches entry for an unmatched entry

    #   param format (unmatched_entry_id,hotel_id,ratio)
    #global session
    (unmatched_entry_id,hotel_id,ratio) = db_record
    possible_match_record = PossibleForumHotelMatchTable_canada(unmatched_entry_id,hotel_id,ratio)

    session.add(possible_match_record)
    session.commit()

def insert_matched_forum_hotel_entries(db_record):

    (forum_hotel_id,internal_hotel_id,matched_ratio) = db_record

    matched_forum_hotel_record = MatchedForumHotel_canada(forum_hotel_id,internal_hotel_id,matched_ratio)

    session.add(matched_forum_hotel_record)
    session.commit()

def get_area_dict(target_site):

    #returns a dictionary for areas with respect to a target_site (e.g. priceline, hotwire...)

    area_dict = {}

    priceline_area_records = session.query(PricelineAreaTable_canada.uid, PricelineAreaTable_canada.name)

    for id,area_name in priceline_area_records:
        area_name = re.sub(', [A-Za-z][A-Za-z]', '', area_name.lower())
        area_dict[area_name] = id

    return area_dict

def get_city_dict(target_site):

    #   returns a dictionary of cityids organized in state => city => cityid

    #   param is included to differentiate between priceline, hotwire systems

    # !!note: has to be changed to account for handling hotwire entries too!

    exclude_list = None

    get_city_lst = session.query(CityTable_canadian.uid,CityTable_canadian.name,CityTable_canadian.state)

    state_city_dict = {}

#    print 'DEBUGG::'
#    print get_city_lst.all()
    
    for rec in get_city_lst.all():
	cityid,city,state = rec
	if state:
        	state = state.lower().strip()
        if city:
        	city = city.lower().strip()

        if state not in state_city_dict.keys():
            state_city_dict[state] = {}

        state_city_dict[state][city] = cityid
    
    return state_city_dict




def match_hotels(region_id,foreign_hotel_list,present_internal_city,state,present_internal_region,log_write_hotels,current_input_state_name,current_input_city_name,current_input_region_name,area_city_dict):

    #this function is a helper function for the test_matcher function.

    #this function matches a list of hotels, given their city/area, region and state with the corrosponding db hotel list

    #1  first this function, retrives all the hotels from a given region

    #2  feeds the appropriate list of hotels to generate the matches for all foreign hotels

    #this function can be expanded in the future to write the hotel matches to the db
    

    #   lookup internal city,region and state from 

    global INTERNAL_STATE_CITY_REGION_DICT

    intrnl_hotel_index = INTERNAL_STATE_CITY_REGION_DICT

    count = 0

    #1

    (hotels_in_all_regions,region_name) = region_hotel_finder(region_id)

    	

    #2
    
    f_hotel_list = map(lambda x:x[0],foreign_hotel_list)

    (area_dict,city_dict) = area_city_dict

    hotel_url_dict = {} #dictionary to store hotel and their urls (for input hotels)

    hotel_id_dict = {}  #dictionary to store hotel and their ids  (for internal hotels)

    #print foreign_hotel_list

    for htl,url,uid in foreign_hotel_list: hotel_url_dict[htl] = (url,uid)

    for internal_hotel in hotels_in_all_regions: hotel_id_dict[internal_hotel.hotel_name] = internal_hotel.uid #changed hotel_id

    hotel_match_array = hotel_name_match(f_hotel_list,map(lambda x:x.hotel_name,hotels_in_all_regions),present_internal_city,state,present_internal_region)
    
    for hotel_matches in hotel_match_array:

        if hotel_matches:
            (url,forum_hotel_id) = hotel_url_dict[hotel_matches[0]]
        else:
            continue

        if hotel_matches[2] > 0.83 and hotel_matches[1]:

        
            insert_matched_forum_hotel = (forum_hotel_id,hotel_id_dict[hotel_matches[1]],hotel_matches[2])	#changed hotel_id ##modified by david march 12/12

            insert_matched_forum_hotel_entries(insert_matched_forum_hotel)

        else:

            #   get region id, city/area id and state of unmatched hotel entries and input them in the database
            
            input_hotel_name = hotel_matches[0]
            internal_hotel_name = hotel_matches[1]

            if not internal_hotel_name: continue

            internal_htl_id = hotel_id_dict[internal_hotel_name]
            (states,city_area,region_name) = intrnl_hotel_index[internal_htl_id]

            area_id = 0
            city_id = 0
            
            if city_area in area_dict.keys():
                area_id = area_dict[city_area]
            elif city_area in city_dict[states].keys():
                city_id = city_dict[states][city_area]

            source_forum = 'bb'
            target_site = 'priceline'

            db_record = (forum_hotel_id,city_id,area_id,region_id,source_forum,target_site,url)
            db_rec_to_ck = (forum_hotel_id,city_id,area_id,source_forum,target_site)

            if not check_entry_listed_as_unmatched(db_rec_to_ck):

                insert_unmatched_entry_to_db(db_record)
                unmatched_entry_id = fetch_unmatched_entry_list_id(db_rec_to_ck)

                for foreign_htls,irnl_htls,ratio in hotel_matches[3]:

                    db_rec = (unmatched_entry_id,hotel_id_dict[irnl_htls],ratio)
                    insert_possible_matches_for_unmatched_entries(db_rec)
            
            count+=1

#    log_write_hotels.write('\n,,,'+str('Hotel Matched : ' + str(len(hotel_match_array) - count)))
#    log_write_hotels.write(','+str('Hotel Not Matched : ' + str(count))+'\n\n')
#    print '\t\t\t\t Hotel Matched : ' + str(len(hotel_match_array) - count)
#    print '\t\t\t\t Hotel Not Matched : ' + str(count)

    return count


def match_regions(current_input_region_list,current_internal_region_list,current_internal_city_name,current_internal_state_name,current_input_city_name,current_internal_city_dict,current_input_city_dict,current_input_state_name,test_log,not_matched_hotels_list,found_city,not_matched_regions_list,area_city_dict,same_level = 1):

    #helper function for the test_matcher function
    
    #This function attemptes to match regions of the input with that of the respective db regions

    for regions in region_name_match(current_input_region_list,current_internal_region_list,current_internal_city_name,current_internal_state_name):

        current_internal_regions_name = regions[1]
        current_input_region_name = regions[0]

        if regions[2] < 0.7:

            # if region not matched log it

            if str(current_input_region_name)+' '+str(current_input_city_name)+' '+str(current_input_state_name) not in not_matched_regions_list:
                not_matched_regions_list.append(str(current_input_region_name)+' '+str(current_input_city_name)+' '+str(current_input_state_name))

        else:

            #if region is matched, proceed to matching relevant hotels

            found_city = 1

            if str(current_input_region_name)+' '+str(current_input_city_name)+' '+str(current_input_state_name) in not_matched_regions_list:
                not_matched_regions_list.remove(str(current_input_region_name)+' '+str(current_input_city_name)+' '+str(current_input_state_name))

            #get region id for the internal region in question

            region_id = current_internal_city_dict[current_internal_regions_name]

            #get list of relevant foreign hotel names to match, if the matching level is the same (e.g. matching regions with regions instead of regions with city/area)

            if same_level:
                foreign_hotel_list = current_input_city_dict[current_input_region_name]
            else:
                foreign_hotel_list = current_input_city_dict['']

#            print "\t\t\t" +str(regions)
#           test_log.write(',,'+str(current_input_region_name)+'\n')

            #  match the relevant hotel names

            not_matched_hotels_list += match_hotels(region_id,foreign_hotel_list,current_internal_city_name,current_internal_state_name,current_internal_regions_name,test_log,current_input_state_name,current_input_city_name,current_input_region_name,area_city_dict)

    return [found_city,not_matched_hotels_list,not_matched_regions_list]



def test_matcher():

    #this is the main matcher function

    test_log = open('hotel_matches2.csv','w')
    
    #process hotel information from db, exclude irelevant cities and make a structured dictionary of (states => city/area => region => hotels)
#    pdb.set_trace()
    
    ##area_dictionary is states=>
#    [area_dictionary,exclude_city_list,state_region] = pl_area()

#    [internal_state_city_region,state_region] = state_city(area_dictionary,exclude_city_list,state_region)
    

    intrnl_hotel_index = {}
    [internal_state_city_region, state_region = hotwire_area()
#    pdb.set_trace()
    for states in internal_state_city_region.keys():

        for city_area in internal_state_city_region[states].keys():

            for regions in internal_state_city_region[states][city_area]:

                (hotel_list,region_name) = region_hotel_finder(internal_state_city_region[states][city_area][regions])

                for hotels in hotel_list:

                    intrnl_hotel_index[hotels.uid]=(states,city_area,region_name)


    global  INTERNAL_STATE_CITY_REGION_DICT
    INTERNAL_STATE_CITY_REGION_DICT = intrnl_hotel_index
    
    not_matched_regions_list = []
    not_matched_hotels_list = 0

    area_city_dict = (get_area_dict('priceline'),get_city_dict('priceline'))

    #process information from scraped data from the forums and construct a structured dictionary similar to that of the previous

    input = get_scraped_data_from_db()  #'hotels-bbpl4','~','#','output/hotels-bbpl4',3,0,1,2

    #start the actual matching process

    # match state
#    pdb.set_trace()

    for possible_matchs in entity_match(input.keys(),internal_state_city_region.keys()):

        current_internal_state_name = possible_matchs[1]
        current_input_state_name = possible_matchs[0]
        current_input_state_dict = input[possible_matchs[0]]
        current_internal_state_dict = internal_state_city_region[possible_matchs[1]]
        
#        logging.info("current_input_state_name: %s" % current_input_state_name)

#        test_log.write(str(current_input_state_name)+'\n')


        #print possible_matchs

        #match cities

        for possible_cities in city_match(current_input_state_dict.keys(),current_internal_state_dict.keys()):

            found_city = 0

#            print '\t\t' + str(possible_cities)

            #iterate through every possible cities/area matches

            for cities in possible_cities:

                #if a city/area match is found break (match is determined if there is matching regions as well)
                
                if found_city: break

                #check if city/area is relevant in terms of text

                if cities[2] > 0.8:

                    current_internal_city_name = cities[1]
                    current_input_city_name = cities[0]
                    current_internal_city_dict = current_internal_state_dict[current_internal_city_name]
                    current_input_city_dict = current_input_state_dict[current_input_city_name]
                    current_input_region_list = current_input_city_dict.keys()
                    current_internal_region_list = current_internal_city_dict.keys()
                    
#                    logging.info("city_name: %s" % (current_input_city_name))

#                    test_log.write(','+str(cities[0])+'\n')

                    # if the city/area in question has all regions named proceed with region matching

                    if '' not in current_input_city_dict.keys():
			
                        #match regions
    
                        [found_city,not_matched_hotels_list,not_matched_regions_list] = match_regions(current_input_region_list,current_internal_region_list,current_internal_city_name,current_internal_state_name,current_input_city_name,current_internal_city_dict,current_input_city_dict,current_input_state_name,test_log,not_matched_hotels_list,found_city,not_matched_regions_list,area_city_dict)
			
#			logging.info("city_name: %s" % (current_input_city_name))
			
                    else:

                        # if region name is missing

                        for f_regions in current_input_city_dict.keys():

                            if f_regions:

                                #match regions that are in the input with the internal regions

                                [found_city,not_matched_hotels_list,not_matched_regions_list] = match_regions([f_regions],current_internal_region_list,current_internal_city_name,current_internal_state_name,current_input_city_name,current_internal_city_dict,current_input_city_dict,current_input_state_name,test_log,not_matched_hotels_list,found_city,not_matched_regions_list,area_city_dict)

                            else:

                                #acquare the hotel list

                                #when region name is empty

                                foreign_hotel_list = current_input_city_dict[f_regions]

                                # when db has only one region for the specified city match it with the database region

                                if len(current_internal_city_dict.keys()) == 1:

                                    temp_internal_region = current_internal_city_dict.keys()[0]

                                    region_id = current_internal_city_dict[temp_internal_region]

                                    match_hotels(region_id,foreign_hotel_list,current_internal_city_name,'',current_internal_state_name,test_log,current_input_state_name,current_input_city_name,'',area_city_dict)

                                #if many region then match the region closet to the city name and then match the hotel list

                                else:

                                    [found_city,not_matched_hotels_list,not_matched_regions_list] = match_regions([current_input_city_name],current_internal_region_list,'',current_internal_state_name,current_input_city_name,current_internal_city_dict,current_input_city_dict,current_input_state_name,test_log,not_matched_hotels_list,found_city,not_matched_regions_list,area_city_dict,0)


                else:

                    #city not matched
                    #try matching the city name with region names in the same state

                    current_input_city_name = cities[0]
                    current_input_city_dict = current_input_state_dict[current_input_city_name]

                    for possible_matches in city_match([current_input_city_name],state_region[current_internal_state_name].keys()):

#                        test_log.write(',,'+str(current_input_city_name)+'\n')
                        for city_to_state_match in possible_matches:

 #                           print '\t\t\t' + str(city_to_state_match)

                            if city_to_state_match[2] > 0.7:

                                foreign_hotel_list = []

                                regions_string = ''

                                for all_region in current_input_city_dict.keys():

                                    foreign_hotel_list.extend(current_input_city_dict[all_region])
                                    regions_string+=' '+str(all_region)

                                region_id = state_region[current_internal_state_name][city_to_state_match[1]]
                                match_hotels(region_id,foreign_hotel_list,city_to_state_match[1],regions_string,current_internal_state_name,test_log,current_input_state_name,current_input_city_name,'',area_city_dict)

#        test_log.write('\n')

##    print not_matched_regions_list
##    print not_matched_hotels_list


@print_timing
def main():

    #Main matcher function is called
    test_matcher()


if __name__ == '__main__':
        main()
