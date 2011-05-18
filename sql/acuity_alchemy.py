import datetime

from sqlalchemy import *
from sqlalchemy.orm import sessionmaker

from sqlalchemy.ext.declarative import declarative_base

debug_level = 0

Base = declarative_base()

# if echo=True it gives verbose info on the sql
engine = create_engine('postgresql:///acuity', echo=False)

Session = sessionmaker(bind=engine)
session = Session()
Base.metadata.bind = engine

class cities(Base) :

    __tablename__ = 'cities'

    city_id = Column(Integer(),primary_key=True)
    city = Column(String(255))
    state = Column(String(255))
    country = Column(String(255))
    def __init__(self) :
        pass


class hotels(Base) :

    __tablename__ = 'hotels'

    cities__city_id = Column(Integer(),ForeignKey('cities.city_id'))
    rating = Column(String(255))
    hotels_combined_id = Column(Integer())
    u_r_l = Column(String(255))
    longitude = Column(Float())
    hotel_address = Column(String(255))
    hotel_file_name = Column(String(255))
    hotel_id = Column(Integer(),primary_key=True)
    latitude = Column(Float())
    hotel_name = Column(String(255))
    def __init__(self) :
        pass


class kayak_hotels(Base) :

    __tablename__ = 'kayak_hotels'

    kayak_name = Column(String(255))
    hotels__hotel_id = Column(Integer(),ForeignKey('hotels.hotel_id'))
    kayak_id = Column(Integer(),primary_key=True)
    def __init__(self) :
        pass


class priceline_regions(Base) :

    __tablename__ = 'priceline_regions'

    cities__city_id = Column(Integer(),ForeignKey('cities.city_id'))
    region_name = Column(String(255))
    longitude = Column(Float())
    active = Column(Integer())
    latitude = Column(Float())
    priceline_region_id = Column(Integer(),primary_key=True)
    def __init__(self) :
        pass


class priceline_id(Base) :

    __tablename__ = 'priceline_id'

    active = Column(Integer())
    priceline_id = Column(Integer(),primary_key=True)
    hotels__hotel_id = Column(Integer(),ForeignKey('hotels.hotel_id'))
    priceline_regions__priceline_region_id = Column(Integer(),ForeignKey('priceline_regions.priceline_region_id'))
    def __init__(self) :
        pass


class hotwire_regions(Base) :

    __tablename__ = 'hotwire_regions'

    cities__city_id = Column(Integer(),ForeignKey('cities.city_id'))
    region_name = Column(String(255))
    longitude = Column(Float())
    active = Column(Integer())
    hotwire_region_id = Column(Integer(),primary_key=True)
    latitude = Column(Float())
    def __init__(self) :
        pass


class hotwire_id(Base) :

    __tablename__ = 'hotwire_id'

    hotwire_id = Column(Integer(),primary_key=True)
    active = Column(Integer())
    hotels__hotel_id = Column(Integer(),ForeignKey('hotels.hotel_id'))
    hotwire_regions__hotwire_region_id = Column(Integer(),ForeignKey('hotwire_regions.hotwire_region_id'))
    def __init__(self) :
        pass


class priceline_points(Base) :

    __tablename__ = 'priceline_points'

    order_id = Column(Integer())
    latitude = Column(Float())
    point_id = Column(Integer(),primary_key=True)
    priceline_regions__priceline_region_id = Column(Integer(),ForeignKey('priceline_regions.priceline_region_id'))
    longitude = Column(Float())
    def __init__(self) :
        pass


class hotwire_points(Base) :

    __tablename__ = 'hotwire_points'

    order_id = Column(Integer())
    latitude = Column(Float())
    point_id = Column(Integer(),primary_key=True)
    longitude = Column(Float())
    hotwire_regions__hotwire_region_id = Column(Integer(),ForeignKey('hotwire_regions.hotwire_region_id'))
    def __init__(self) :
        pass


class bft_posts(Base) :

    __tablename__ = 'bft_posts'

    bft_post_id = Column(Integer(),primary_key=True)
    rating = Column(Integer())
    nights = Column(Integer())
    topic_number = Column(Integer())
    priceline_id__priceline_id = Column(Integer(),ForeignKey('priceline_id.priceline_id'))
    price = Column(Integer())
    check_in_date = Column(DATE())
    replies = Column(Integer())
    hotel_name = Column(String(255))
    def __init__(self) :
        pass


class bb_priceline_posts(Base) :

    __tablename__ = 'bb_priceline_posts'

    rating = Column(Integer())
    nights = Column(Integer())
    topic_number = Column(Integer())
    priceline_id__priceline_id = Column(Integer(),ForeignKey('priceline_id.priceline_id'))
    price = Column(Integer())
    bb_priceline_post_id = Column(Integer(),primary_key=True)
    check_in_date = Column(DATE())
    replies = Column(Integer())
    hotel_name = Column(String(255))
    def __init__(self) :
        pass


class bb_hotwire_posts(Base) :

    __tablename__ = 'bb_hotwire_posts'

    hotwire_id__hotwire_id = Column(Integer(),ForeignKey('hotwire_id.hotwire_id'))
    rating = Column(Integer())
    nights = Column(Integer())
    topic_number = Column(Integer())
    bb_hotwire_post_id = Column(Integer(),primary_key=True)
    check_in_date = Column(DATE())
    replies = Column(Integer())
    price = Column(Integer())
    hotel_name = Column(String(255))
    def __init__(self) :
        pass


class hotel_names(Base) :

    __tablename__ = 'hotel_names'

    priceline_id__priceline_id = Column(Integer(),ForeignKey('priceline_id.priceline_id'))
    rating = Column(Integer())
    win_rate = Column(Integer())
    id = Column(Integer(),primary_key=True)
    hotel_name = Column(String(255))


    def __init__(self) :
        pass


class priceline_bids(Base) :

    __tablename__ = 'priceline_bids'

    check_in = Column(DATE())
    nights = Column(Integer())
    priceline_id__priceline_id = Column(Integer(),ForeignKey('priceline_id.priceline_id'))
    taxes_fees = Column(Float())
    bid_date = Column(DateTime())
    rooms = Column(Integer())
    total = Column(Float())
    room_cost = Column(Float())
    priceline_bid_id = Column(Integer(),primary_key=True)
    subtotal = Column(Float())
    def __init__(self) :
        pass


class hotwire_bids(Base) :

    __tablename__ = 'hotwire_bids'

    hotwire_id__hotwire_id = Column(Integer(),ForeignKey('hotwire_id.hotwire_id'))
    check_in = Column(DATE())
    nights = Column(Integer())
    hotwire_bid_id = Column(Integer(),primary_key=True)
    rooms = Column(Integer())
    date_fetched = Column(DateTime())
    total = Column(Float())
    room_cost = Column(Float())
    taxes_fees = Column(Float())
    subtotal = Column(Float())
    def __init__(self) :
        pass


class amenities(Base) :

    __tablename__ = 'amenities'
    h_w_amenity_abbreviation = Column(String(2))
    amenity_id = Column(Integer(),primary_key=True)
    amenity_name = Column(String(45))
    def __init__(self) :
        pass


class hotel_amenities(Base) :

    __tablename__ = 'hotel_amenities'

    updated_at = Column(DateTime())
    created_at = Column(DateTime())
    hotels__hotel_id = Column(Integer(),ForeignKey('hotels.hotel_id'))
    hotel_amenity_id = Column(Integer(),primary_key=True)
    amenities__amenity_id = Column(Integer(),ForeignKey('amenities.amenity_id'))
    def __init__(self) :
        pass

Base.metadata.create_all(engine)
