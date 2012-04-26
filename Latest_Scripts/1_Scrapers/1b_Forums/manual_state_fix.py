from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.crawler import CrawlerProcess
from multiprocessing import Process, Queue
from scrapy.conf import settings
from scrapy import log
from scrapy.http import Request
from libs import *
import re

from sqlalchemy import * 
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
import sys
sys.path.insert(0, "/home/areek/Documents/fetchopia/backend_git/sql/alchemy/" )


from processed_forum_data import ProcessedRawForumData
from processed_forum_data_hotwire import ProcessedRawForumData_hotwire

##establishing connection to the database
engine = create_engine('postgresql://postgres:areek@localhost:5432/acuity', echo=False)
Session = scoped_session(sessionmaker(bind=engine))
session = Session()
Base = declarative_base(bind=session) 
metadata = Base.metadata


### For US state fix
US_hotels = session.query(ProcessedRawForumData_hotwire).filter(ProcessedRawForumData_hotwire.state == "Alabama / Alaska / Arizona / Arkansas")

for instance in US_hotels.all():
	print instance.hotel_name, instance.city_area
	
	correct_state = input("Enter State Number:")
	
	if correct_state == 1:
		instance.state = "Alabama"
		session.commit()
	
	if correct_state == 2:
		instance.state = "Alaska"
		session.commit()
	
	if correct_state == 3:
		instance.state = "Arizona"
		session.commit()
	
	if correct_state == 4:
		instance.state = "Arkansas"
		session.commit()
	
	if correct_state == 0:
		new_state = raw_input("Enter New State Name:")
		instance.state = new_state
		new_star_rating = raw_input("Enter New Star Rating:")
		instance.star = new_star_rating
		new_name = raw_input("Enter New Name:")
		instance.hotel_name = new_name
		session.commit()

### For priceline Canada state entry
canada_hotels = session.query(ProcessedRawForumData_hotwire).filter(ProcessedRawForumData_hotwire.country == "Canada")
for instance in canada_hotels.all():
	print instance.hotel_name, instance.city_area
	
	correct_state = input("Enter State Number:")
	
	if correct_state == 1:
		instance.state = "Ontario"
		session.commit()
	
	if correct_state == 2:
		instance.state = "Quebec"
		session.commit()
	
	if correct_state == 3:
		instance.state = "Nova Scotia"
		session.commit()
	
	if correct_state == 4:
		instance.state = "New Brunswick"
		session.commit()
	
	if correct_state == 5:
		instance.state = "Manitoba"
		session.commit()
	
	if correct_state == 6:
		instance.state = "British Columbia"
		session.commit()
	
	if correct_state == 7:
		instance.state = "Price Edward Island"
		session.commit()
	
	if correct_state == 8:
		instance.state = "Saskatchewan"
		session.commit()
	
	if correct_state == 9:
		instance.state = "Alberta"
		session.commit()
	
	if correct_state == 10:
		instance.state = "Newfoundland and Labrador"
		session.commit()



