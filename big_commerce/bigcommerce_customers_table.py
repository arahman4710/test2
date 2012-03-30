from sqlalchemy import *
from alchemy_session import get_alchemy_info
(engine, session, Base, metadata) = get_alchemy_info ()

class BigCommerce_Customers(Base) :
	
	__tablename__ = 'bigcommerce_customers_table'
	
	uid = Column(Integer, primary_key=True)
	password = Column(String())
	company = Column(String())
	first_name = Column(String())
	last_name = Column(String())
	email = Column(String())
	phone = Column(String())
	date_created = Column(String())
	date_modified = Column(String())
	store_credit = Column(Float())
	registration_ip_address = Column(String())
	customer_group_id = Column(Integer())
	notes = Column(String())
	
	def __init__(self, a1, a2, a3, a4, a5, a6, a7, a8, a9, a10, a11, a12):
		
		self.password = a1
		self.company = a2
		self.first_name = a3
		self.last_name = a4
		self.email = a5
		self.phone = a6
		self.date_createad = a7
		self.date_modified = a8
		self.store_credit = a9
		self.registration_ip_address = a10
		self.customer_group_id = a11
		self.notes = a12
		
