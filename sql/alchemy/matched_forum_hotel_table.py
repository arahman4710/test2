<<<<<<< HEAD
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


=======
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


>>>>>>> b9293a11ec4d93846942852d46a86453f0c09cb0
metadata.create_all(engine)