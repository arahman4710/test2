from sqlalchemy import *
from alchemy_session import get_alchemy_info
(engine, session, Base, metadata) = get_alchemy_info ()

debug_level = 0

#   Database Mapper Class for unmatched_forum_hotel_table table

#   This table will keep track of unmatched forum hotels that were not matched satisfactorily when the matching algorithm was applied

class MatchedForumHotel(Base) :

    __tablename__ = 'matched_forum_hotel_table'

    uid = Column(Integer, Sequence('matched_forum_hotel_table_sequence'), primary_key=True)
    forum_hotel_id = Column(Integer, ForeignKey('processed_raw_forum_data.uid'))  #   id of the processed forum hotel table, that was matched
    hotel_id = Column(Integer, ForeignKey('hotels.hotel_id'))   #   id of the internal hotel that was matched with the corrosponding forum hotel

    def __init__(self, forum_hotel_id, hotel_id) :

        #   Assign the params to the member variables
        self.forum_hotel_id = hotel_id
        self.hotel_id = forum_hotel_id

    def __str__(self) :

        #   pretty printing

        return "< matched_forum_hotel_table forum_hotel_id=%s hotel_id=%s >" % (self.forum_hotel_id, self.hotel_id)


metadata.create_all(engine)