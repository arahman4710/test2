from alchemy_session import get_alchemy_info
from sqlalchemy import *
import canon_hotel 

(engine, session, Base, metadata) = get_alchemy_info ()

debug_level = 0

# Database Mapper Class for reviews table


class ReviewsTable(Base) :

    __tablename__ = 'hotel_reviews'

    uid = Column(Integer, Sequence('hotel_reviews_sequence'), primary_key=True)  #   primary key
    hotel_uid = Column(Integer, ForeignKey('canonical_hotel.uid')) # Foreign Key should point to hotel table uid, for hotels of X City
    review_user = Column(String(500)) # User name of review creator
    review = Column(String(500)) # Entire text of review (raw or processed eliminating html tags??)
    review_short = Column(String(500)) # Short text of review (Like a summary, maybe 80 words?)
    review_date = Column(Time()) # Date of the review, delivers a datetime.date() python object
    rating = Column(Float) 
    norm_rating = Column(Float) # If rating goes from 0 to 10 we normalize from 0 to 5
    review_url_source = Column(String(500))
    reviewer_type = Column(Text()) # Field to comply with travelpost_reviews_spider reviewertype 
    def __init__(self, uid, hotel_uid, review, review_user, review_short, review_date, rating, norm_rating, review_source):

        """
        In the initialization, just assign all the member variables (fields) 
        of the table to the supplied params
        """

        self.uid = uid
        self.hotel_uid = hotel_uid
        self.review_user = review_user
        self.review = review
        self.review_short = review_short
        self.review_date = review_date
        self.rating = rating
        self.norm_rating = norm_rating
        self.review_url_source = review_url_source
        
        session.add(self)
        session.commit()

    def __unicode__(self) :

	return " review user = %s date = %s short = %s rating = %s full review url = %s>" % (self.review_user, self.review_date, self.review_short, self.norm_rating, self.review_url)

metadata.create_all(engine)
