from sqlalchemy import *
from alchemy_session import get_alchemy_info
(engine, session, Base, metadata) = get_alchemy_info ()

debug_level = 0


class BigCommerce_Orders(Base) :

    __tablename__ = 'bigcommerce_orders_table'

    uid = Column(Integer, Sequence('bigcommerce_orders_sequence'), primary_key=True)  #   Primary key
    order_id = Column(Integer()) 
    customer_id = Column(Integer())
    date_created = Column(String())
    date_modified = Column(String())
    subtotal_ex_tax = Column(Float())
    subtotal_inc_tax = Column(Float())
    subtotal_tax = Column(Float())
    total_tax = Column(Float())
    base_shipping_cost = Column(Float())
    shipping_cost_ex_tax = Column(Float())
    shipping_cost_inc_tax = Column(Float())
    shipping_cost_tax = Column(Float())
    shipping_cost_tax_class_id = Column(Integer())
    base_handling_cost = Column(Float())
    handling_cost_ex_tax = Column(Float())
    handling_cost_inc_tax = Column(Float())
    handling_cost_tax = Column(Float())
    handling_cost_tax_class_id = Column(Integer())
    base_wrapping_cost = Column(Float())
    wrapping_cost_ex_tax = Column(Float())
    wrapping_cost_inc_tax = Column(Float())
    wrapping_cost_tax = Column(Float())
    wrapping_cost_tax_class_id = Column(Integer())
    total_ex_tax = Column(Float())
    total_inc_tax = Column(Float())
    status_id = Column(Integer())
    status = Column(String())
    items_total = Column(Integer())
    items_shipped = Column(Integer())
    payment_method = Column(String())
    payment_provider_id = Column(String())
    payment_status = Column(String()) #The status of the payment. A payment status may be one of the following, depending on the payment method used: authorized, captured, refunded, partially refunded, voided
    refunded_amount = Column(Float())
    order_is_digital = Column(String())
    date_shipped = Column(String())
    store_credit_amount = Column(Float())
    gift_certificate_amount = Column(Float())
    ip_address = Column(String())
    geoip_country = Column(String())
    geoip_country_iso2 = Column(String())
    currency_id = Column(Integer())
    currency_code = Column(String())
    default_currency_id = Column(Integer())
    default_currency_code = Column(String())
    currency_exchange_rate = Column(Float())
    staff_notes = Column(String())
    customer_message = Column(String())
    discount_amount = Column(Float())
    shipping_address_count = Column(Integer())
    coupon_discount = Column(Float())
    is_deleted = Column(String())
    
    

    
    
    
    

    def __init__(self, order_id, customer_id, date_created, date_modified, subtotal_ex_tax, subtotal_inc_tax, subtotal_tax, total_tax, base_shipping_cost, shipping_cost_ex_tax, shipping_cost_inc_tax, shipping_cost_tax, shipping_cost_tax_class_id, base_handling_cost, handling_cost_ex_tax, handling_cost_inc_tax, handling_cost_tax, handling_cost_tax_class_id, base_wrapping_cost, wrapping_cost_ex_tax, wrapping_cost_inc_tax, wrapping_cost_tax, wrapping_cost_tax_class_id, total_ex_tax, total_inc_tax, status_id, items_total, items_shipped, payment_method, payment_provider_id, payment_status, refunded_amount, order_is_digital, date_shipped, store_credit_amount, gift_certificate_amount, ip_address, geoip_country, geoip_country_iso2, currency_id, currency_code, default_currency_id, default_currency_code, currency_exchange_rate, staff_notes, customer_message, discount_amount, shipping_address_count, coupon_discount, is_deleted):

        #   In the initialization, just assign all the member variables (fields) of the table to the supplied params

        self.order_id = order_id
        self.customer_id = customer_id
        self.date_created = date_created
        self.date_modified = date_modified
        self.subtotal_ex_tax = subtotal_ex_tax
        self.subtotal_inc_tax = subtotal_inc_tax
        self.subtotal_tax = subtotal_tax
        self.total_tax = total_tax
        self.base_shipping_cost = base_shipping_cost
        self.shipping_cost_ex_tax = shipping_cost_ex_tax
        self.shipping_cost_inc_tax = shipping_cost_inc_tax
        self.shipping_cost_tax = shipping_cost_tax
        self.shipping_cost_tax_class_id = shipping_cost_tax_class_id
        self.base_handling_cost = base_handling_cost
        self.handling_cost_ex_tax = handling_cost_ex_tax
        self.handling_cost_inc_tax = handling_cost_inc_tax
        self.handling_cost_tax = handling_cost_tax
        self.handling_cost_tax_class_id = handling_cost_tax_class_id
        self.base_wrapping_cost = base_wrapping_cost
        self.wrapping_cost_ex_tax = wrapping_cost_inc_tax
        self.wrapping_cost_tax = wrapping_cost_tax
        self.wrapping_cost_tax_class_id = wrapping_cost_tax_class_id
        self.total_ex_tax = total_ex_tax
        self.total_inc_tax = total_inc_tax
        self.status_id = status_id
        self.items_total = items_total
        self.items_shipped = items_shipped
        self.payment_method = payment_method
        self.payment_provider_id = payment_provider_id
        self.payment_status = payment_status
        self.refunded_amount = refunded_amount
        self.currency_exchange_rate = currency_exchange_rate
        self.staff_notes = staff_notes
        self.customer_message = customer_message
        self.discount_amount = discount_amount
        self.shipping_address_count = shipping_address_count
        self.coupon_discount = coupon_discount
        self.is_deleted = is_deleted
        
        
        
        
        
        
        
        
        
        
        
        

    def __str__(self) :

        #   A more informative print for the class

        return "< processed_raw_forum hotel_name = %s city_area = %s region = %s state = %s source_forum = %s taget_site = %s >" % (self.hotel_name, self.city_area,self.region,self.state,self.source_forum,self.target_site)


metadata.create_all(engine)
