class amenities (Base) :

    __tablename__ = 'amenities'

    AmenityName = Column(varchar()) 
    AmenityId = Column(int(),primary_key=True) 

    def __init__(self) : 
        pass

class bbhotwireposts (Base) :

    __tablename__ = 'bbhotwireposts'

    Rating = Column(int()) 
    Nights = Column(int()) 
    CheckInDate = Column(int()) 
    TopicNumber = Column(int()) 
    HotelName = Column(varchar()) 
    BbHotwirePostId = Column(int(),primary_key=True) 
    KEY = Column(fk()) 
    Replies = Column(int()) 
    Price = Column(int()) 
    HotwireId_HotwireId = Column(int()) 

    def __init__(self) : 
        pass

class bbpricelineposts (Base) :

    __tablename__ = 'bbpricelineposts'

    BbPricelinePostId = Column(int(),primary_key=True) 
    Nights = Column(int()) 
    Rating = Column(int()) 
    CheckInDate = Column(int()) 
    TopicNumber = Column(int()) 
    HotelName = Column(varchar()) 
    KEY = Column(fk()) 
    Replies = Column(int()) 
    PricelineId_PricelineId = Column(int()) 
    Price = Column(int()) 

    def __init__(self) : 
        pass

class bftposts (Base) :

    __tablename__ = 'bftposts'

    BftPostId = Column(int(),primary_key=True) 
    Rating = Column(int()) 
    Nights = Column(int()) 
    CheckInDate = Column(int()) 
    TopicNumber = Column(int()) 
    HotelName = Column(varchar()) 
    KEY = Column(fk()) 
    Replies = Column(int()) 
    PricelineId_PricelineId = Column(int()) 
    Price = Column(int()) 

    def __init__(self) : 
        pass

class cities (Base) :

    __tablename__ = 'cities'

    CityId = Column(int(),primary_key=True) 
    City = Column(varchar()) 
    State = Column(varchar()) 
    Country = Column(varchar()) 

    def __init__(self) : 
        pass

class hotelamenities (Base) :

    __tablename__ = 'hotelamenities'

    HotelAmenityId = Column(int(),primary_key=True) 
    Amenities_AmenityId = Column(int()) 
    Hotels_HotelId = Column(int()) 
    KEY = Column(fk()) 
    UpdatedAt = Column(int()) 
    CreatedAt = Column(int()) 

    def __init__(self) : 
        pass

class hotelnames (Base) :

    __tablename__ = 'hotelnames'

    Rating = Column(int()) 
    HotelName = Column(varchar()) 
    WinRate = Column(int()) 
    KEY = Column(fk()) 
    PricelineId_PricelineId = Column(int()) 
    Id = Column(int(),primary_key=True) 

    def __init__(self) : 
        pass

class hotels (Base) :

    __tablename__ = 'hotels'

    HotelFileName = Column(varchar()) 
    Rating = Column(varchar()) 
    Cities_CityId = Column(int()) 
    HotelId = Column(int(),primary_key=True) 
    Longitude = Column(double()) 
    HotelName = Column(varchar()) 
    KEY = Column(fk()) 
    HotelsCombinedId = Column(int()) 
    Latitude = Column(double()) 
    HotelAddress = Column(varchar()) 

    def __init__(self) : 
        pass

class hotwire_amenity_hotel (Base) :

    __tablename__ = 'hotwire_amenity_hotel'

    KEY = Column(FK()) 
    Amenity_id = Column(int()) 
    Hotel_id = Column(int()) 
    CONSTRAINT = Column(FK()) 

    def __init__(self) : 
        pass

class hotwire_hotel_review_description (Base) :

    __tablename__ = 'hotwire_hotel_review_description'

    User_rating = Column(text()) 
    Posted_date = Column(text()) 
    Review_id = Column(int(),primary_key=True) 
    User_information = Column(text()) 
    CONSTRAINT = Column(FK()) 
    Review_content = Column(text()) 
    Hotel_id = Column(int()) 
    Reviewer_location = Column(text()) 
    Review_rating = Column(float()) 
    Review_title = Column(text()) 
    Reviewer_TripType = Column(text()) 
    KEY = Column(FK()) 
    Review_url = Column(text()) 

    def __init__(self) : 
        pass

class hotwire_hotel_review_overview (Base) :

    __tablename__ = 'hotwire_hotel_review_overview'

    Hotel_url = Column(text()) 
    NumberOfReview = Column(int()) 
    City = Column(text()) 
    Hotel_star = Column(float()) 
    Hotel_popularity_overall = Column(text()) 
    Hotel_recommendation_percentage = Column(float()) 
    Hotel_popularity_specific = Column(text()) 
    Hotel_id = Column(int(),primary_key=True) 
    Hotel_rating = Column(float()) 
    Hotel_name = Column(text()) 

    def __init__(self) : 
        pass

class hotwirebids (Base) :

    __tablename__ = 'hotwirebids'

    HotwireBidId = Column(int(),primary_key=True) 
    Nights = Column(int()) 
    TaxesFees = Column(double()) 
    RoomCost = Column(double()) 
    CheckIn = Column(int()) 
    Rooms = Column(int()) 
    KEY = Column(fk()) 
    Total = Column(double()) 
    Subtotal = Column(double()) 
    HotwireId_HotwireId = Column(int()) 

    def __init__(self) : 
        pass

class hotwireid (Base) :

    __tablename__ = 'hotwireid'

    HotwireId = Column(int(),primary_key=True) 
    Active = Column(int()) 
    HotwireRegions_HotwireRegionId = Column(int()) 
    KEY = Column(fk()) 
    Hotels_HotelId = Column(int()) 

    def __init__(self) : 
        pass

class hotwirepoints (Base) :

    __tablename__ = 'hotwirepoints'

    OrderId = Column(int()) 
    Longitude = Column(double()) 
    PointId = Column(int(),primary_key=True) 
    KEY = Column(fk()) 
    Latitude = Column(double()) 
    HotwireRegions_HotwireRegionId = Column(int()) 

    def __init__(self) : 
        pass

class hotwireregions (Base) :

    __tablename__ = 'hotwireregions'

    Cities_CityId = Column(int()) 
    Longitude = Column(double()) 
    HotwireId = Column(varchar()) 
    Active = Column(int()) 
    KEY = Column(fk()) 
    Latitude = Column(double()) 
    HotwireRegionId = Column(int(),primary_key=True) 
    RegionName = Column(varchar()) 

    def __init__(self) : 
        pass

class internal_tripadvisor_hotel (Base) :

    __tablename__ = 'internal_tripadvisor_hotel'

    Tripadvisor_hotel_id = Column(int()) 
    Internal_hotel_id = Column(int()) 
    KEY = Column(FK()) 
    CONSTRAINT = Column(FK()) 

    def __init__(self) : 
        pass

class kayakhotels (Base) :

    __tablename__ = 'kayakhotels'

    KayakId = Column(int(),primary_key=True) 
    KayakName = Column(varchar()) 
    KEY = Column(fk()) 
    Hotels_HotelId = Column(int()) 

    def __init__(self) : 
        pass

class possible_match_table (Base) :

    __tablename__ = 'possible_match_table'

    CONSTRAINT = Column(FK()) 
    percentage_match = Column(varchar()) 
    possible_match_id = Column(int(),primary_key=True) 
    hotel_id = Column(int()) 
    unmatched_entry_id = Column(int()) 
    KEY = Column(FK()) 

    def __init__(self) : 
        pass

class priceline_area (Base) :

    __tablename__ = 'priceline_area'

    Priceline_area_id = Column(int(),primary_key=True) 
    Name = Column(varchar()) 

    def __init__(self) : 
        pass

class priceline_area_city (Base) :

    __tablename__ = 'priceline_area_city'

    city_id = Column(int()) 
    area_id = Column(int()) 

    def __init__(self) : 
        pass

class priceline_hotel_review_description (Base) :

    __tablename__ = 'priceline_hotel_review_description'

    Rating = Column(float()) 
    Positive_review = Column(text()) 
    Review = Column(text()) 
    Negative_review = Column(text()) 
    Reviewer = Column(text()) 
    Hotel_name = Column(text()) 
    PostedDate = Column(text()) 

    def __init__(self) : 
        pass

class priceline_hotel_review_description_temp (Base) :

    __tablename__ = 'priceline_hotel_review_description_temp'

    Rating = Column(float()) 
    Positive_review = Column(text()) 
    Review = Column(text()) 
    Negative_review = Column(text()) 
    Reviewer = Column(text()) 
    Hotel_name = Column(text()) 
    PostedDate = Column(text()) 

    def __init__(self) : 
        pass

class priceline_hotel_review_overview (Base) :

    __tablename__ = 'priceline_hotel_review_overview'

    City = Column(text()) 
    Star = Column(float()) 
    Rating = Column(float()) 
    Hotel = Column(Dining()) 
    Overall = Column(Rating()) 
    NumberOfReviews = Column(int()) 
    Location = Column(of()) 
    Hotel_name = Column(text()) 

    def __init__(self) : 
        pass

class priceline_hotel_review_overview_temp (Base) :

    __tablename__ = 'priceline_hotel_review_overview_temp'

    City = Column(text()) 
    Star = Column(float()) 
    Rating = Column(float()) 
    Hotel = Column(Dining()) 
    Overall = Column(Rating()) 
    NumberOfReviews = Column(int()) 
    Location = Column(of()) 
    Hotel_name = Column(text()) 

    def __init__(self) : 
        pass

class pricelinebids (Base) :

    __tablename__ = 'pricelinebids'

    Nights = Column(int()) 
    TaxesFees = Column(double()) 
    RoomCost = Column(double()) 
    CheckIn = Column(int()) 
    PricelineBidId = Column(int(),primary_key=True) 
    Rooms = Column(int()) 
    KEY = Column(fk()) 
    PricelineId_PricelineId = Column(int()) 
    Total = Column(double()) 
    Subtotal = Column(double()) 

    def __init__(self) : 
        pass

class pricelineid (Base) :

    __tablename__ = 'pricelineid'

    Active = Column(int()) 
    PricelineRegions_PricelineRegionId = Column(int()) 
    PricelineId = Column(int(),primary_key=True) 
    KEY = Column(fk()) 
    Hotels_HotelId = Column(int()) 

    def __init__(self) : 
        pass

class pricelinepoints (Base) :

    __tablename__ = 'pricelinepoints'

    OrderId = Column(int()) 
    PricelineRegions_PricelineRegionId = Column(int()) 
    Longitude = Column(double()) 
    PointId = Column(int(),primary_key=True) 
    KEY = Column(fk()) 
    Latitude = Column(double()) 

    def __init__(self) : 
        pass

class pricelineregions (Base) :

    __tablename__ = 'pricelineregions'

    Cities_CityId = Column(int()) 
    PricelineId = Column(varchar()) 
    Longitude = Column(double()) 
    PricelineRegionId = Column(int(),primary_key=True) 
    Active = Column(int()) 
    Star_availibility = Column(varchar()) 
    KEY = Column(fk()) 
    Latitude = Column(double()) 
    RegionName = Column(varchar()) 

    def __init__(self) : 
        pass

class processed_raw_bb_forum (Base) :

    __tablename__ = 'processed_raw_bb_forum'

    star = Column(decimal()) 
    target = Column(varchar()) 
    url = Column(varchar()) 
    region = Column(varchar()) 
    source = Column(varchar()) 
    state = Column(varchar()) 
    city_area = Column(varchar()) 
    hotel_name = Column(varchar()) 

    def __init__(self) : 
        pass

class region_hotel (Base) :

    __tablename__ = 'region_hotel'

    pl_region_id = Column(int()) 
    hotel_id = Column(int()) 

    def __init__(self) : 
        pass

class regionscitiesmap (Base) :

    __tablename__ = 'regionscitiesmap'

    priceline_regionid = Column(varchar()) 
    cities_cityid = Column(int()) 

    def __init__(self) : 
        pass

class tesa (Base) :

    __tablename__ = 'tesa'

    Hotel_url = Column(text()) 
    NumberOfReview = Column(int()) 
    City = Column(text()) 
    Hotel_star = Column(float()) 
    Hotel_popularity_overall = Column(text()) 
    Hotel_recommendation_percentage = Column(float()) 
    Hotel_popularity_specific = Column(text()) 
    Postal_code = Column(text()) 
    Hotel_id = Column(int(),primary_key=True) 
    Hotel_rating = Column(float()) 
    Address = Column(text()) 
    Hotel_name = Column(text()) 

    def __init__(self) : 
        pass

class travelpost_hotel_review_description (Base) :

    __tablename__ = 'travelpost_hotel_review_description'

    rating = Column(text()) 
    review_id = Column(int()) 
    hotel_id = Column(text()) 
    Source = Column(text()) 
    link = Column(text()) 
    reviewerType = Column(text()) 
    reviewContent = Column(text()) 
    postedDate = Column(text()) 

    def __init__(self) : 
        pass

class travelpost_hotel_review_overview (Base) :

    __tablename__ = 'travelpost_hotel_review_overview'

    hotelurl = Column(text()) 
    hotelname = Column(text()) 
    numberofreviews = Column(int()) 
    hotelid = Column(int()) 
    averagerating = Column(double()) 

    def __init__(self) : 
        pass

class tripadvisor_amenity_hotel (Base) :

    __tablename__ = 'tripadvisor_amenity_hotel'

    Amenity_id = Column(int()) 
    Hotel_id = Column(int()) 

    def __init__(self) : 
        pass

class tripadvisor_hotel_review_description (Base) :

    __tablename__ = 'tripadvisor_hotel_review_description'

    User_rating = Column(text()) 
    Posted_date = Column(text()) 
    Review_id = Column(int()) 
    User_information = Column(text()) 
    Review_content = Column(text()) 
    Hotel_id = Column(text()) 
    Reviewer_location = Column(text()) 
    Review_rating = Column(float()) 
    Review_title = Column(text()) 
    Reviewer_TripType = Column(text()) 
    Review_url = Column(text()) 

    def __init__(self) : 
        pass

class tripadvisor_hotel_review_overview (Base) :

    __tablename__ = 'tripadvisor_hotel_review_overview'

    Hotel_url = Column(text()) 
    NumberOfReview = Column(int()) 
    Hotel_star = Column(float()) 
    Hotel_popularity_overall = Column(text()) 
    Hotel_recommendation_percentage = Column(float()) 
    Hotel_popularity_specific = Column(text()) 
    Hotel_id = Column(int()) 
    Hotel_rating = Column(float()) 
    Hotel_name = Column(text()) 

    def __init__(self) : 
        pass

class unmatched_hotel_table (Base) :

    __tablename__ = 'unmatched_hotel_table'

    target_site = Column(text()) 
    city = Column(int()) 
    area = Column(int()) 
    region = Column(int()) 
    source_url = Column(text()) 
    unmatched_entry_id = Column(int(),primary_key=True) 
    source_forum = Column(text()) 
    hotel_name = Column(text()) 
    matched = Column(int()) 

    def __init__(self) : 
        pass

