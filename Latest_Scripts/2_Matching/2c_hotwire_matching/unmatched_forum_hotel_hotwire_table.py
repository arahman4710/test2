
from sqlalchemy import *
from alchemy_session import get_alchemy_info

from processed_forum_data_hotwire import ProcessedRawForumData_hotwire
#from processed_forum_data6_test import ProcessedRawForumData

(engine, session, Base, metadata) = get_alchemy_info ()

debug_level = 0

#   Database Mapper Class for unmatched_forum_hotel_table table

#   This table will keep track of unmatched forum hotels that were not matched satisfactorily when the matching algorithm was applied

class UnmatchedForumHotelTable(Base) :

    __tablename__ = 'unmatched_forum_hotel_hotwire_table'

    uid = Column(Integer, Sequence('unmatched_forum_hotel_sequence'), primary_key=True)
    forum_hotel_id = Column(Integer, ForeignKey('processed_raw_forum_data_hotwire.uid')) #   record id for the processed forum raw data
    city_id = Column(Integer()) #   primary key of the city that the unmatched hotel is believed to be located  (can be priceline or hotwire, depanding on the source_forum field)
    area_id = Column(Integer()) #   primary key of the area that the unmatched hotel is beleived to be located
    region_id = Column(Integer())   #   primary key of the region (can be priceline or hotwire, depanding on the source_forum field) where the hotel is believed to be located in
    source_forum = Column(String(500)) #   name of the fourm the hotel was originally scraped from
    target_site = Column(String(500))  #   name of the site the forums were referring to for this hotel
    source_url = Column(String(500))   #   the address of the page where this entry was originally scraped from
    matched = Column(Integer())   #   can be either blank or may have the primary key of the internal hotel it was matched with after

    def __init__(self, forum_hotel_id, city_id,area_id, region_id, source_forum, target_site, source_url, matched = 0) :

        #   Assign the params to the member variables

        self.forum_hotel_id = forum_hotel_id
        self.city_id = city_id
        self.area_id = area_id
        self.region_id  = region_id
        self.source_forum = source_forum
        self.target_site = target_site
        self.source_url = source_url
        self.matched = matched

    def __str__(self) :

        #   pretty printing

        return "< unmatched_hotel_table name=%s source_forum=%s matched=%s >" % (self.name, self.source_forum,self.matched)


metadata.create_all(engine)
