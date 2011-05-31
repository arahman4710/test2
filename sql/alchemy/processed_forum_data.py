
from sqlalchemy import *

from alchemy_session import get_alchemy_info


(engine, session, Base, metadata) = get_alchemy_info ()

debug_level = 0

#   Database Mapper Class for processed_raw_forum_data table

#   This table will store the raw scraped data from the forum

class ProcessedRawForumData(Base) :

    __tablename__ = 'processed_raw_forum_data'

    uid = Column(Integer, Sequence('processed_raw_forum_data_sequence'), primary_key=True)  #   Primary key
    hotel_name = Column(String())   #   name of the hotel from the forum
    city_area = Column(String())    #   city/area information for the particular hotel from the forum
    region = Column(String())   #   region name from the forum
    star = Column(String())  #   star rating of the hotel according to that forum
    state = Column(String())    #   name of the state the hotel is from
    url = Column(String())  #   address to the page it was scraped from
    target_site = Column(String())   #  the target site is the site the forum is referring to (priceline, hotwire etc)
    source_forum = Column(String()) #   the name of the forum the data has been scraped from (bb, bft)

    def __init__(self, uid, hotel_name, city_area,region, star, url, state, target, source):

        #   In the initialization, just assign all the member variables (fields) of the table to the supplied params

        self.uid = uid
        self.hotel_name = hotel_name
        self.city_area = city_area
        self.region = region
        self.star  = star
        self.url = url
        self.state = state
        self.target_site = target
        self.source_forum = source

    def __str__(self) :

        #   A more informative print for the class

        return "< processed_raw_forum hotel_name = %s city_area = %s region = %s state = %s source_forum = %s taget_site = %s >" % (self.hotel_name, self.city_area,self.region,self.state,self.source_forum,self.target_site)


metadata.create_all(engine)