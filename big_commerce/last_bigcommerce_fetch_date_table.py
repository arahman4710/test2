
from sqlalchemy import *
from alchemy_session import get_alchemy_info
(engine, session, Base, metadata) = get_alchemy_info ()

debug_level = 0

#   This table keeps track of the last date that data was fetched. In the case of fetching new data, use this date as a tool to fetch only data beyond this date

class Last_BCom_Fetch_Date(Base) :

    __tablename__ = 'last_bigcommerce_fetch_date'

    uid = Column(Integer, primary_key=True)
    date = Column(String())  #   last date that data was fetched from bigcommerce for order -> shipping_address/customer/billing_address information


    def __init__(self, date) :

        #   Assign the params to the member variables
        self.date = date

    def __str__(self) :

        #   pretty printing

        return "%s" % (self.date)


metadata.create_all(engine)
