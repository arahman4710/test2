import MySQLdb
import re


'''

    Purpose of this script is to process raw scraped data and insert it to the db for later reference

'''

class Connection():

        #this class sets up the database connection that is being used throughout the matcher code
        #to change the database to aquire information from, change the settings below

	database = MySQLdb.connect(user='root', passwd='areek', db='acuity')
	cursor = database.cursor()


def extract_content(file_name):

    # helper function for csv_format_test, opens the file given as perameter and returns the content of the file

    f = open(file_name)
    content = f.read()
    f.close()
    return content


def insert_raw_data_to_db(record):

    #   this function inserts one record into the table

    db = Connection.database
    c = Connection.cursor

    c.execute('''INSERT INTO `acuity`.`processed_raw_bb_forum` \
	(`hotel_name`, `city_area`, `region`, `star`, `url`, `state`, `source`, `target`) \
	VALUES \
	%s;''' % str(record))

    db.commit()


def create_db_table_for_raw_data():

    # this function creates the table to store the semi-processed data, if table already does not exist

    db = Connection.database
    c = Connection.cursor

    c.execute('''CREATE TABLE IF NOT EXISTS `processed_raw_bb_forum` (
    `hotel_name` varchar(255) DEFAULT NULL, \
    `city_area` varchar(255) DEFAULT NULL, \
    `region` varchar(255) DEFAULT NULL, \
    `star` decimal(10) DEFAULT NULL, \
    `url` varchar(500) DEFAULT NULL, \
    `state` varchar(100) DEFAULT NULL, \
    `target` varchar(100) DEFAULT NULL, \
    `source` varchar(100) DEFAULT NULL \
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8 ''')

    db.commit()


def process_scraped_raw_data(delemiter_record,delemiter_field,file_name,hotel_index,state_index,city_index,region_index,url_index,star_index):

    #helper method for test_matcher function, it organizes the content from the scraped data into dictionaries of dictionaries (State => city_area => Region => hotels)

    return_dict={}
    for lines in extract_content(file_name).split('\n'):

        line_parts = lines.split('@')

        if len(line_parts) < 3: continue

        (records,old_states,target,source) = line_parts

        if records.strip():

            for record in records.split(delemiter_record):

                parts = record.split(delemiter_field)

                city = str(re.sub(', [A-Za-z][A-Za-z]', '', parts[city_index].lower().strip()))
                state = parts[state_index].lower().strip()
                url = parts[url_index].strip()
                star = parts[star_index].strip()
                region = str(re.sub(', [A-Za-z][A-Za-z]', '', parts[region_index].lower().strip()))
                hotel = parts[hotel_index].lower().strip()

                if state == 'dc':
                    state = 'district of columbia'

                db_record = (hotel,city,region,star,url,state,source,target)

                insert_raw_data_to_db(db_record)

    return return_dict


def insert_data_into_db():

    #   this function processes raw scraped data and inserts it into the db

    create_db_table_for_raw_data()

    process_scraped_raw_data('~','#','output/hotels-bbpl4',3,0,1,2,5,4)




if __name__ == "__main__":
    insert_data_into_db()
