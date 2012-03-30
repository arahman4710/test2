from sqlalchemy import *
from alchemy_session import get_alchemy_info
(engine, session, Base, metadata) = get_alchemy_info ()

class BigCommerce_Shipping_Address(Base) :

	__tablename__ = 'bigcommerce_shipping_address_table'
	
	uid = Column(Integer, Sequence('bigcommerce_shipping_address_sequence'), primary_key=True)  #   Primary key
	last_name = Column(String())
	shipping_method = Column(String())
	country_iso2 = Column(String())
	items_total = Column(Integer())
	base_cost = Column(Float())
	cost_tax = Column(Float())
	city = Column(String())
	first_name = Column(String())
	zip = Column(String())
	handling_cost_tax = Column(Float())
	id = Column(Integer())
	state = Column(String())
	items_shipped = Column(Integer())
	base_handling_cost = Column(Float())
	order_id = Column(Integer())
	company = Column(String())
	cost_tax_class_id = Column(Integer())
	street_1 = Column(String())
	street_2 = Column(String())
	handling_cost_ex_tax = Column(Float())
	phone = Column(String())
	country = Column(String())
	cost_inc_tax = Column(Float())
	cost_ex_tax = Column(Float())
	shipping_zone_name = Column(String())
	
	def __init__(self, a1):
		
		self.last_name = a1
		self.shipping_method = a2
		self.country_iso2 = a3
		self.items_total = a4
		self.base_cost = a5
		self.cost_tax = a6
		self.city = a7
		self.first_name = a8
		self.zip = a9
		self.handling_cost_tax = a10
		self.id = a11
		self.state = a12
		self.items_shipped = a13
		self.base_handling_cost = a14
		self.order_id = a15
		self.company = a16
		self.cost_tax_class_id = a17
		self.street_1 = a18
		self.street_2 = a19
		self.handling_cost_ex_tax = a20
		self.phone = a21
		self.country = a22
		self.cost_inc_tax = a23
		self.cost_ex_tax = a24
		self.shipping_zone_name = a25
