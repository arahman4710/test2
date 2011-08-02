# this is a test program and an example.   in a scrapy context I'd be using
# the scrapy xpath stuff, but since I wanted to read from a file i'm using libxml
import sys 
import libxml2
import datetime 

import json
import urllib2
import pika
import StringIO 
import logging

from sqlalchemy import * 
from sqlalchemy.sql import and_, func
from sqlalchemy.orm import sessionmaker

# local imports 
sys.path.insert(0,'/work/jeff/backend/sql/alchemy/') 
from sqlalchemy.ext.declarative import declarative_base
from point import Point, find_point, PointList
from amenity import Amenity, AmenityString, get_amenity_string
from hotwire_tables import *

channel = None  # to establish scope 

debug_level = 10 

# base_query_format = "http://api.hotwire.com/v1/search/hotel?apikey=%(api_key)s&dest=%(city)s&rooms=%(rooms)s&adults=%(adults)s&children=%(children)s&startdate=%(start_date)s&enddate=%(end_date)s"

base_query_format = "http://localhost/fetch/hotwire_api/hotwire_api/hotwire_api/spiders/data/raw/1302724956" 

def fix_date(d) : 
    x = d.split('/')
    return "-".join([x[2], x[0], x[1]]) 
        
def simple_extract(name, ctxt) : 
    print "simple extract : ", name, ctxt 
    res = ctxt.xpathEval(".//%s/text()"% name)[0].get_content() 
    print "       extracts :", res 
    return res
 
# many of the results come in simple enough format that this utility
# routine simplifies extracting them and saving them
# the names to be found in the xml are the keys and the names they
# translate to as columns are the values 

def dict_extract(name_dict, ctxt) :  
    result_dict = {}
    for i in name_dict :
       if debug_level > 4 :  
          print "finding <<%s>> in xml" % i 
       result_dict[name_dict[i]] = simple_extract(i, ctxt) 
    return result_dict 

# and here are the dictionaries that dict_extract uses

amenities_element_dict = {"Name":"name", "Code":"code", "Description":"description"} 

neighborhood_element_dict = {"Id":"id", "Name":"name", "City":"city", "State":"state", "Country":"country", "Centroid":"centroid"} 

hotel_element_dict = {'TotalPrice': 'total_price', 'CheckOutDate': 'checkout_date', 'HWRefNumber': 'hw_ref_number', 'AveragePricePerNight': 'average_price_per_night', 'ResultId': 'result_id', 'CurrencyCode': 'currency_code', 'TaxesAndFees': 'taxes_and_fees', 'StarRating': 'star_rating', 'LodgingTypeCode': 'lodging_type_code', 'Rooms': 'rooms', 'NeighborhoodId': 'neighborhood_id', 'DeepLink': 'deep_link', 'SubTotal': 'subtotal', 'CheckInDate': 'checkin_date'}

def parse_result (s) : 
    doc = libxml2.parseDoc(s)
    print doc.name

    ctxt = doc.xpathNewContext()
    amenities = ctxt.xpathEval("//Hotwire/MetaData/HotelMetaData/Amenities/Amenity")
    amenities_dict = do_amenities(amenities) 
    session.commit()

    neighborhoods = ctxt.xpathEval("//Hotwire/MetaData/HotelMetaData/Neighborhoods/Neighborhood") 
    neighborhoods_dict = do_neighborhoods(neighborhoods) 
    session.commit() 

    hotels = ctxt.xpathEval("//Hotwire/Result/HotelResult") 
    hotels_list = do_hotels(hotels) 
    session.commit() 
    return (amenities_dict, neighborhoods_dict, hotels_list) 
    
def do_neighborhoods(neighborhoods) :
    return [do_one_neighborhood(i) for i in neighborhoods] 

def do_one_neighborhood(nb) : 
    print "do one neighborhood" 
    result_dict = dict_extract(neighborhood_element_dict, nb)  
    nresult = session.query(Neighborhood).filter_by(id=result_dict['id']).all() 
    if nresult :   # we have it already 
        return nresult[0]
     
    [clat, clong] = map(float, result_dict["centroid"].split(",")) 
    result_dict['centroid'] = find_point(clat, clong).uid 
    
    points = nb.xpathEval(".//Shape/LatLong")
    # print points 
    point_list = [] 
    for i in enumerate(points) :
        [point_lat, point_long] = map(float, i[1].get_content().split(",")) 
        point_list.append((i[0], point_lat, point_long)) 
    result_dict["point_list"] = PointList(point_list).uid 
    return Neighborhood(result_dict) 

def do_hotels(hotel_list) :
    return [do_hotel(h) for h in hotel_list] 

def do_hotel(hotel) :
    dict = dict_extract(hotel_element_dict, hotel) 
    amenity_codes_raw = hotel.xpathEval(".//AmenityCodes/Code/text()") 
    if debug_level > 9 : 
        logging.info("raw amenity codes: %s" % amenity_codes_raw)
    amenity_codes = [i.get_content() for i in amenity_codes_raw]
    if debug_level > 9 : 
        logging.info( "amenity codes=%s" % amenity_codes) 
    dict['amenity_codes'] = amenity_codes 
    x = HotWireHotelInfo(dict, {} )
    session.add(x) 
    session.commit()
    return x 

def do_amenities(amenities) :
    return [do_amenity(i) for i in amenities ] 
    
def do_amenity(amenity) : 
    if debug_level > 5 : 
        logging.info( "do_amenity :%s" % amenity) 
    info = dict_extract(amenities_element_dict, amenity) 
    if debug_level > 5 : 
        logging.info("amenity info : %s" % info) 
    am = session.query(Amenity).filter_by(code=info['code']).all() 
    if am :
        return am[0]
    am = Amenity(info) 
    return am 

def get_end_date(startdate, nights) :
   start = datetime.strptime("%m/%d/%Y", startdate)
   end = start+datetime.timedelta(days=nights)
   return end.strftime("%m/%d/%Y")

def gen_date(offset, nights) : 
    """
    given an offset (number of days in the future to check) this returns a pair of strings
    (start_date, end_date) that is that number of days into the future and the day after
    that.
    Use the datetime module to manage this instead of time. 
    """ 

    today = datetime.date.today()
    start_date = today+datetime.timedelta(days=offset) 
    end_date = today+datetime.timedelta(days=offset+nights) 
    
    # I don't know if this will take other formats for dates.  
    return (start_date.strftime("%m/%d/%Y"), end_date.strftime("%m/%d/%Y"))

def encode_response(request_dict, hotel_info) :
   resp_dict = {}
   resp_dict['response_to'] = request_dict['message_id']
   resp_dict['service'] = 'h'
   resp_dict['start_date'] = hotel_info.checkin_date.strftime("%m/%d/%Y")
   resp_dict['end_date'] = hotel_info.checkout_date.strftime("%m/%d/%Y")
   resp_dict['location'] = "%s" % hotel_info.neighborhood_id
   resp_dict['total_price'] = hotel_info.total_price
   resp_dict['adults'] = hotel_info.adults 
   resp_dict['amenities'] = get_amenity_string(hotel_info.amenity_codes) 
   return json.dumps(resp_dict) 

def do_hotwire_query_response(ch, method, properties, body):
   print "Received request"
   print body
   request_dict = json.loads(body)
   request_dict['api_key'] = 'eupzwn43dwtmgxhmkw5pbta7'
   print request_dict 

   if 'rooms' not in request_dict :
       request_dict['rooms'] = 1 
   if 'enddate' not in request_dict : 
      enddate = get_end_date(request_dict['startdate'], 1) 
      request_dict['enddate'] = enddate 

   request_url = base_query_format % request_dict
   print "request_url : ", request_url 
   x = urllib2.urlopen(request_url)
   data = x.read()
   (adict, ndict, hlist) = parse_result(data)
   for hotel_dict in hlist :
      channel.basic_publish(exchange='',
                            routing_key='info_response',
                            body = encode_response(request_dict, hotel_dict), 
                            properties=pika.BasicProperties(
                               delivery_mode = 2, # make message persistent
                               ))
   ch.basic_ack(delivery_tag = method.delivery_tag)

def main():
   global channel 
   logging.basicConfig(filename='/home/jefu/fetch/test/rabbit-hotwire/rh.log',level=logging.DEBUG)

   connection = pika.BlockingConnection(pika.ConnectionParameters(
      host='localhost'))
   channel = connection.channel()

   channel.queue_declare(queue='info_request',  durable=True)
   channel.queue_declare(queue='info_response', durable=True)

   logging.info('Rabbit waiting for messages') 

   channel.basic_qos(prefetch_count=1)

   channel.basic_consume(do_hotwire_query_response,
                         queue='info_request')

   channel.start_consuming()

main()
