
from sqlalchemy import *
from alchemy_session import get_alchemy_info
(engine, session, Base, metadata) = get_alchemy_info ()
from processed_forum_data_hotwire import ProcessedRawForumData_hotwire
#from processed_forum_data6_test import ProcessedRawForumData
debug_level = 0

#   Database Mapper Class for unmatched_forum_hotel_table table

#   This table will keep track of unmatched forum hotels that were not matched satisfactorily when the matching algorithm was applied

class MatchedForumHotelTable(Base) :

    __tablename__ = 'matched_forum_hotel_hotwire_table'

    uid = Column(Integer, primary_key=True)
    forum_hotel_id = Column(Integer, ForeignKey('processed_raw_forum_data_hotwire.uid'))  #   id of the processed forum hotel table, that was matched
    hotel_id = Column(Integer())   #   id of the internal hotel that was matched with the corrosponding forum hotel
    match_ratio = Column(Float())   #   match ratio of the forum, internal hotel pair


    def __init__(self, forum_hotel_id, hotel_id,match_ratio) :

        #   Assign the params to the member variables
        self.forum_hotel_id = forum_hotel_id
        self.hotel_id = hotel_id
        self.match_ratio = match_ratio

    def __str__(self) :

        #   pretty printing

        return "< matched_forum_hotel_table forum_hotel_id=%s hotel_id=%s >" % (self.forum_hotel_id, self.hotel_id)


metadata.create_all(engine)
