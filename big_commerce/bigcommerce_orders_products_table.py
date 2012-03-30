from sqlalchemy import *
from alchemy_session import get_alchemy_info
(engine, session, Base, metadata) = get_alchemy_info ()


## this table has all the products info for all orders
##orders map to products table is where the relationship for which products belong to what order id


class BigCommerce_Orders_Products(Base) :

    __tablename__ = 'bigcommerce_orders_products_table'

    uid = Column(Integer, Sequence('bigcommerce_products_sequence'), primary_key=True)  #   Primary key
    cost_price_tax = Column(Float())
    cost_price_ex_tax = Column(Float())
    product_options = Column(String())
    weight = Column(Float())
    parent_order_product_id = Column(String())
    refund_amount = Column(Float())
    option_set_id = Column(Integer())
    price_ex_tax = Column(Float())
    base_wrapping_cost = Column(Float())
    bin_picking_number = Column(String())
    id = Column(Integer())
    sku = Column(String())
    price_tax = Column(Float())
    wrapping_cost_inc_tax = Column(Float())
    base_total = Column(Float())
    cost_price_inc_tax = Column(Float())
    event_name = Column(String())
    fixed_shipping_cost = Column(Float())
    order_address_id = Column(Float())
    event_date = Column(String())
    wrapping_cost_tax = Column(Float())
    product_type = Column(String())
    total_tax = Column(Float())
    wrapping_message = Column(String())
    is_refunded = Column(String())
    quantity_shipped = Column(Integer())
    product_id = Column(Integer())
    base_cost_price = Column(Float())
    applied_discounts = Column(Float())
    name = Column(String())
    price_inc_tax = Column(Float())
    wrapping_name = Column(String())
    configurable_fields = Column(String())
    total_inc_tax = Column(Float())
    quantity = Column(Integer())
    total_ex_tax = Column(Float())
    base_price = Column(Float())
    
    
    def __init__(self, a1, a2, a3, a4, a5, a6, a6, a7, a8, a9, a10, a11, a12, a13, a14, a15, a16, a17, a18, a19, a20, a21, a22, a23, a24, a25, a26, a27, a28, a29, a30, a31, a32, a33, a34, a35, a36, a37):
    
	    self.cost_price_tax = a1
	    self.cost_price_ex_tax = a2
	    self.product_options = a3
	    self.weight = a4
	    self.parent_order_product_id = a5
	    self.refund_amount = a6
	    self.option_set_id = a7
	    self.price_ex_tax = a8
	    self.base_wrapping_cost = a9
	    self.bin_picking_number = a10
	    self.id = a11
	    self.sku = a12
	    self.price_tax = a13
	    self.wrapping_cost_inc_tax = a14
	    self.base_total = a15
	    self.cost_price_inc_tax = a16
	    self.event_name = a17
	    self.fixed_shipping_cost = a18
	    self.order_address_id = a19
	    self.event_date = a20
	    self.wrapping_cost_tax = a21
	    self.product_type = a22
	    self.total_tax = a23
	    self.wrapping_message = a24
	    self.is_refunded = a25
	    self.quantity_shipped = a26
	    self.product_id = a27
	    self.base_cost_price = a28
	    self.applied_discounts = a29
	    self.name = a30
	    self.price_inc_tax = a31
	    self.wrapping_name = a32
	    self.configurable_fields = a33
	    self.total_inc_tax = a34
	    self.quantity = a35
	    self.total_ex_tax = a36
	    self.base_price = a37
    	
    	 
   
    
