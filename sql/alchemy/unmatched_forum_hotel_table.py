
from sqlalchemy import *
from alchemy_session import get_alchemy_info
(engine, session, Base, metadata) = get_alchemy_info ()

debug_level = 0

#   Database Mapper Class for unmatched_forum_hotel_table table

#   This table will keep track of unmatched forum hotels that were not matched satisfactorily when the matching algorithm was applied

class UnmatchedForumHotelTable(Base) :

    __tablename__ = 'unmatched_forum_hotel_table'

    uid = Column(Integer, Sequence('unmatched_forum_hotel_sequence'), primary_key=True)
    name = Column(String()) #   name of the hotel from the forum that has not yet been matched
    city_id = Column(Integer, ForeignKey('city.uid')) #   primary key of the city/area that the unmatched hotel is believed to be located  (can be priceline or hotwire, depanding on the source_forum field)
    region_id = Column(Integer())   #   primary key of the region (can be priceline or hotwire, depanding on the source_forum field) where the hotel is believed to be located in
    source_forum = Column(String()) #   name of the fourm the hotel was originally scraped from
    target_site = Column(String())  #   name of the site the forums were referring to for this hotel
    source_url = Column(String())   #   the address of the page where this entry was originally scraped from
    matched = Column(Integer, ForeignKey('hotel.uid'))   #   can be either blank or may have the primary key of the internal hotel it was matched with after

    def __init__(self, uid, name, city_id, region_id, source_forum, target_site, source_url, matched) :

        #   Assign the params to the member variables

        self.uid = uid
        self.name = name
        self.city_id = city_id
        self.region_id  = region_id
        self.source_forum = source_forum
        self.target_site = target_site
        self.source_url = source_url
        self.matched = matched

    def __str__(self) :

        #   pretty printing

        return "< unmatched_hotel_table name=%s source_forum=%s matched=%s >" % (self.name, self.source_forum,self.matched)


metadata.create_all(engine)