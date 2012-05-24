from sqlalchemy import *
from alchemy_session import get_alchemy_info
(engine, session, Base, metadata) = get_alchemy_info ()

class BigCommerce_shipments(Base) :
	
	__tablename__ = 'bigcommerce_shipments_table'
	
	
	uid = Column(Integer, primary_key=True)
	shipment_id = Column(Integer())
	date_created = Column(String())
	tracking_number = Column(String())
	shipping_method = Column(String())
	order_id = Column(Integer())
	order_date = Column(String())
	comments = Column(String())
	
	
	def __init__(self, a1, a2, a3, a4, a5, a6, a7):
		
		self.shipment_id = a1
		self.date_created = a2
		self.tracking_number = a3
		self.shipping_method = a4
		self.order_id = a5
		self.order_date = a6
		self.comments = a7
		
	
