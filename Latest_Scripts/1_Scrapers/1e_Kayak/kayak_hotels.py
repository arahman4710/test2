from sqlalchemy import *

from alchemy_session import get_alchemy_info

(engine, session, Base, metadata) = get_alchemy_info ()

class kayak_hotels(Base) :

    __tablename__ = 'kayak_hotels'

    uid = Column(Integer, primary_key=True)  #   primary key
    name =  Column(String(500))  #   name of the priceline region
    city = Column(String(500))
    state = Column(String(500))
    postal_code = Column(String())
    address = Column(String(500))
    star = Column(Float())    #   latitude of the center of the region
    price = Column(String())    #   longitude of the center of the region
    kayak_id = Column(String())

    def __init__(self, name, city, state, postal_code, address, star, price, kayak_id) :

        #   Assign params to member variables

        self.name = name
        self.city = city
        self.state = state
        self.postal_code = postal_code
        self.address = address
        self.star = star
        self.price = price
        self.kayak_id = kayak_id

    def __str__(self) :

        #   pretty printing

        return "< kayak_hotel name = %s city_state = %s, %s price = %s >" % (self.name, self.city, self.state, self.price)


metadata.create_all(engine)
