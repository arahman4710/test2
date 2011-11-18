from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()
from decimal import *



class ProcessedRawForumData(Base) :

    __tablename__ = 'processed_raw_bb_forum'

    hotel_name = Column(String(255))
    city_area = Column(String(255))
    region = Column(String(255))
    star = Column(Float(10))
    url = Column(String(500))
    state = Column(String(100))
    target = Column(String(100))
    source = Column(String(100))

    def __init__(self, hotel_name, city_area,region, star, url, state, target, source) :

        self.hotel_name = hotel_name
        self.city_area = city_area
        self.region = region
        self.star  = star
        self.url = url
        self.state = state
        self.target = target
        self.source = source

    def __str__(self) :

        return "< processed_raw_bb_forum hotel_name=%s city_area=%s region=%s >" % (self.hotel_name, self.city_area,self.region)


class Hotel(Base) :

    __tablename__ = 'hotels'

    uid = Column(Integer, Sequence('hotel_sequence'), primary_key=True)
    name = Column(String(255))
    address = Column(String(255))
    city_id = Column(Integer, ForeignKey('city.uid'))
    latitude = Column(Float())
    longitude = Column(Float())
    rating = Column(String(255))
    hotelcombined_id = Column(Integer())
    file_name = Column(String(255))

    def __init__(self, uid, name, address, city_id, latitude, longitude, rating, hotelcombined_id, file_name):

        self.uid = uid
        self.name = name
        self.address = address
        self.city_id  = city_id
        self.latitude = latitude
        self.longitude = longitude
        self.rating = rating
        self.hotelcombined_id = hotelcombined_id
        self.file_name = file_name

    def __str__(self) :

        return "< hotels name=%s address=%s rating=%s >" % (self.name, self.address,self.rating)


class RegionHotel(Base) :

    __tablename__ = 'region_hotel'

    hotel_id = Column(Integer(11))
    pl_region_id = Column(Integer(11))


    def __init__(self, hotel_id, pl_region_id) :

        self.hotel_id = hotel_id
        self.pl_region_id = pl_region_id


    def __str__(self) :

        return "< region_hotel hotel_id=%s pl_region_id=%s >" % (self.hotel_id, self.pl_region_id)


class City(Base) :

    __tablename__ = 'cities'

    uid = Column(Integer, Sequence('city_sequence'), primary_key=True)
    name = Column(String(255))
    state = Column(String(255))
    country = Column(String(255))


    def __init__(self, uid, name,state, country) :

        self.uid = uid
        self.name = name
        self.state = state
        self.country = country

    def __str__(self) :

        return "< cities name=%s state=%s country=%s >" % (self.name, self.state,self.country)


class CityRegionMap(Base) :

    __tablename__ = 'regionscitiesmap'

    cities_cityid = Column(Integer(11))
    priceline_regionid = Column(Integer(11))


    def __init__(self, cities_cityid, priceline_regionid) :

        self.cities_cityid = cities_cityid
        self.priceline_regionid = priceline_regionid


    def __str__(self) :

        return "< regionscitiesmap cities_cityid=%s cities_cityid=%s >" % (self.cities_cityid, self.cities_cityid)


class UnmatchedHotelTable(Base) :

    __tablename__ = 'unmatched_hotel_table'

    uid = Column(Integer, Sequence('unmatched_hotel_sequence'), primary_key=True)
    name = Column(String(255))
    city_id = Column(Integer(11))
    region_id = Column(Integer(11))
    source_forum = Column(String())
    target_site = Column(String())
    source_url = Column(String())
    matched = Column(Integer(11))

    def __init__(self, uid, name, city_id, region_id, source_forum, target_site, source_url, matched) :

        self.uid = uid
        self.name = name
        self.city_id = city_id
        self.region_id  = region_id
        self.source_forum = source_forum
        self.target_site = target_site
        self.source_url = source_url
        self.matched = matched

    def __str__(self) :

        return "< unmatched_hotel_table name=%s source_forum=%s matched=%s >" % (self.name, self.source_forum,self.matched)


class PossibleMatchTable(Base) :

    __tablename__ = 'possible_match_table'

    uid = Column(Integer(Integer, Sequence('possible_match_sequence'), primary_key=True))
    unmatched_entry_id = Column(Integer, ForeignKey('unmatched_hotel_table.uid'))
    hotel_id = Column(Integer, ForeignKey('hotels.uid'))
    percentage_match = Column(String(100))

    def __init__(self, uid, unmatched_entry_id,hotel_id,percentage_match) :

        self.uid = uid
        self.unmatched_entry_id = unmatched_entry_id
        self.hotel_id = hotel_id
        self.percentage_match = percentage_match

    def __str__(self) :

        return "< possible_match_table hotel_id=%s percentage_match=%s >" % (self.hotel_id, self.percentage_match)



if __name__ == "__main__":
    engine = create_engine('mysql://root:areek@localhost/test', echo=True)

    Session = sessionmaker(bind=engine)
    session = Session()

    metadata = Base.metadata

    metadata.create_all(engine)
    
    print session.query(ProcessedRawForumData).filter_by(star = 2.5).all()[0]
