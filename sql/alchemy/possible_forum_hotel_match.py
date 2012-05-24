
from sqlalchemy import *

from alchemy_session import get_alchemy_info

from unmatched_forum_hotel_table import  UnmatchedForumHotelTable
from hotel import Hotel

(engine, session, Base, metadata) = get_alchemy_info ()

debug_level = 0
#   Database Mapper Class for possible_forum_hotel_match_table table

#   This table will keep track of possible matches for the unmatched forum hotel entries. These matches will be generated automatically by the forum hotel matching algorithm while trying to come up with hotel matches

class PossibleForumHotelMatchTable(Base):

    __tablename__ = 'possible_forum_hotel_match_table'

    uid = Column(Integer, Sequence('possible_forum_hotel_match_sequence'), primary_key=True)   #   primary key
    unmatched_entry_id = Column(Integer, ForeignKey('unmatched_forum_hotel_table.uid')) #   primary key for the umatched forum hotel entry that the record is related to
    hotel_id = Column(Integer, ForeignKey('hotels.hotel_id'))    #   primary key of an internal hotel that is considered to be a possible match for the unmatched forum hotel in question
    percentage_match = Column(Float()) #   measures how close the internal hotel matched with the unmatched forum hotel entry in question


    def __init__(self, unmatched_entry_id,hotel_id,percentage_match):

        #   assign params to member variables

      self.unmatched_entry_id = unmatched_entry_id
      self.hotel_id = hotel_id
      self.percentage_match = percentage_match

    
	
    def __str__(self) :

	return "< possible_match_table hotel_id=%s percentage_match=%s >" % (self.hotel_id, self.percentage_match)

metadata.create_all(engine)