
from unmatched_forum_hotel_table import UnmatchedForumHotelTable
from processed_forum_data import ProcessedRawForumData
from priceline_area_table import PricelineAreaTable
from priceline_area_city_table import PricelineAreaCityTable
from priceline_regions_table import PricelineRegionTable
from priceline_city_region_map import PricelineCityRegionMap
from possible_forum_hotel_match import PossibleForumHotelMatchTable
from matched_forum_hotel_table import *
from priceline_region_hotel_map import *
from priceline_region_point_table import *
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()
from alchemy_session import get_alchemy_info
from hotel import Hotel
from city_table import CityTable

(engine, session, Base, metadata) = get_alchemy_info () 
