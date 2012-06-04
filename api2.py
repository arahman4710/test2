
"""
This module provides an object-oriented wrapper around the BigCommerce V2 API
for use in Python projects or via the Python shell.

"""

import httplib2
import base64
import json
import urllib
#import socks

#API_HOST = 'https://store-1eaef.mybigcommerce.com'
API_HOST = 'https://store-cbfd8.mybigcommerce.com'
API_PATH = '/api/v2'
API_USER = 'admin'
#API_KEY  = '0270f4680ac3eb5796ab3f9fe5a0e46299fe14cd'
API_KEY = 'e3a4804855753b8981e4787115c65edbccd339df'

#'YWRtaW46ZTNhNDgwNDg1NTc1M2I4OTgxZTQ3ODcxMTVjNjVlZGJjY2QzMzlkZg=='

HTTP_PROXY = None
HTTP_PROXY_PORT = 80




class Connection(object):

    def __init__(self, host=API_HOST, base_path=API_PATH, user=API_USER, api_key=API_KEY):
        self.host = host
        self.base_path = base_path
        self.user = user
        self.api_key = api_key
        self.remaining_requests = 0


    def handle_response(self, response):
        pass

    def request_json(self, method, path, data=None):
        response, content = self.request(method, path, data)
        # API is limited by request per hour. Your application code can
        # access the number of remaing request in order to throttle or postpone
        # requests.
        self.remaining_requests = int(response.get('x-bc-apilimit-remaining',0))
        # BigCommerce send back a header with status code 204
        # periodically with the number allowed connections remaining
        if response.status == 204:
            return None
        if response.status == 200 or response.status == 201:
            return json.loads(content)
        else:
            error = "%s %s" % (response, content)
            print error
            raise Exception(response.status)

    def build_request_headers(self):
        auth = base64.b64encode(self.user + ':' + self.api_key)
        return { 'Authorization' : 'Basic ' + auth, 'Accept' : 'application/json' }

    def request(self, method, path, body=None):
        http = httplib2.Http(disable_ssl_certificate_validation=True)
        url = self.host + self.base_path + path
        headers = self.build_request_headers()
        if (body): headers['Content-Type'] = 'application/json'
        return http.request(url, method, headers=headers, body=body)


class Resource(object):
    """Base class representing BigCommerce resources"""

    def __init__(self, fields={}, client=None):
        self.__dict__ = fields
        self.client = client

    def get_fields(self):
        #remove the client object
        #it is not serializable
        fields = self.__dict__.copy()
        del(fields['client'])
        return fields


class Time(Resource):
    """Tests the availability of the API."""

    def get(self):
        """Returns the current time stamp of the BigCommerce store."""
        return self.client.request_json('GET', '/time')


class Products(Resource):
    """The collection of products in a store"""

    def get(self):
        """Returns list of products"""
        products_list = self.client.request_json('GET', '/products')
        return [Product(product) for product in products_list]

    def get_all(self):
        """Returns list of all products"""
        all_products = []
        products_list = self.client.request_json('GET', '/products')
        page = 2 
        while products_list:
            all_products += products_list
            products_list = self.client.request_json('GET', '/products?limit=250&page=' + str(page))
            print page
            page += 1
        return [Product(product) for product in all_products]

    def get_by_id(self, id):
        """Returns an individual product by given ID"""
        product = self.client.request_json('GET', '/products/' + str(id))
        return Product(product, client=self.client)

    def get_by_sku(self, sku):
        """Returns an individual product by given SKU"""
        product = self.client.request_json('GET', '/products?sku=' + str(sku))
        if product is None:
            return None
        # Get with filter returns a list of dicts
        # as we are request by SKU, there should be only
        # one result returned.
        return Product(product.pop(), client=self.client)

    def add(self, fields=None):
        """Adds the product"""
        body = json.dumps(fields)
        product = self.client.request_json('POST', '/products/', body)
        return product


class Product(Resource):
    """An individual product"""

    def update(self):
        """Updates local changes to the product"""
        body = json.dumps(self.get_fields())
        product = self.client.request_json('PUT', '/products/' + str(self.id), body)

    def update_field(self, key, value):
        body = json.dumps({key:value})
        self.client.request_json('PUT', '/products/' + str(self.id), body)

##    def update(self):
##        """Updates local changes to the order"""
##        body = json.dumps(self.get_fields())
##        order = self.client.request_json('PUT', '/orders/' + str(self.id), body)
##
##    def update_field(self, key, value):
##        body = json.dumps({key:value})
##        self.client.request_json('PUT', '/orders/' + str(self.id), body)

    def delete(self):
        """Deletes the product"""
        response, content = self.client.request('DELETE', '/products/' + str(self.id))

##class Orders(Resource):
##    """Orders collection"""
##
##    def get(self):
##        """Returns list of orders"""
##        orders = self.client.request_json('GET', '/orders')
##        return [Order(order) for order in orders]
##
##    def get_by_id(self, id):
##        """Returns an individual order by given ID"""
##        self.client = Connection()
##        order = self.client.request_json('GET', '/orders/' + str(id))
##        #print "getbyid",order
##        self.client = Connection()
##        return Order(order)
##
##    def getOrderProductName(self,id):
##        """Returns name of product of an order by given ID"""
##        order = self.client.request_json('GET', '/orders/' +str(id) + '/products/')
##        return order[0]["name"]
##
##class Order(Resource):
##    """An individual order"""
##
##    def create(self):
##        """Creates a new order"""
##        body = json.dumps(self.get_fields())
##        order = self.client.request_json('PUT', '/orders', body)
##
##    def update(self):
##        """Updates local changes to the order"""
##        body = json.dumps(self.get_fields())
##        order = self.client.request_json('PUT', '/orders/' + str(self.id), body)
##
##    def update_field(self, key, value):
##        body = json.dumps({key:value})
##        print self.id
##        print self.client.request('PUT', '/orders/' + str(self.id))
##
##    def delete(self):
##        """Deletes the order"""
##        response, content = self.client.request('DELETE', '/orders/' + str(self.id))


class Brands(Resource):
    """Brands collection"""

    def get(self):
        """Returns list of brands"""
        brands_list = self.client.request_json('GET', '/brands')
        return [Brand(brand) for brand in brands_list]

    def get_by_name(self, name):
        """Returns an individual brand name"""
        brand = self.client.request_json('GET', '/brands?name=' + urllib.quote(name))
        if brand is None:
            return None
        # return id not Brand object
        return brand.pop()['id']

    def get_by_id(self, id):
        """Returns an individual brand by given ID"""
        brand = self.client.request_json('GET', '/brands/' + str(id))
        return brand(brand)

class Brand(Resource):
    """An individual brand"""

    def create(self):
        """Creates a new brand"""
        body = json.dumps(self.get_fields())
        brand = self.client.request_json('PUT', '/brands', body)

    def update(self):
        """Updates local changes to the brand"""
        body = json.dumps(self.get_fields())
        brand = self.client.request_json('PUT', '/brands/' + str(self.id), body)
        print brand['name']

    def delete(self):
        """Deletes the brand"""
        response, content = self.client.request('DELETE', '/brands/' + str(self.id))

class Customers(Resource):
    """Customers collection"""

    def get(self):
        """Returns list of customers"""
        customers = self.client.request_json('GET', '/customers')
        return [Customer(customer) for customer in customers]

    def get_by_id(self, id):
        """Returns an individual customer by given ID"""
        customer = self.client.fetch_obj('GET', '/customers/' + str(id))
        return Customer(customer)

class Customer(Resource):
    """An individual customer"""

    def create(self):
        """Creates a new customer"""
        body = json.dumps(self.get_fields())
        customer = self.client.request_json('PUT', '/customers', body)

    def update(self):
        """Updates local changes to the customer"""
        body = json.dumps(self.get_fields())
        customer = self.client.request_json('PUT', '/customers/' + str(self.id), body)

    def delete(self):
        """Deletes the customer"""
        response, content = self.client.request('DELETE', '/customers/' + str(self.id))

class Orders(Resource):
    """Orders collection"""

    def get(self):
        """Returns list of orders"""
        orders = self.client.request_json('GET', '/orders')
        return [Order(order) for order in orders]

    def get_by_id(self, id):
        """Returns an individual order by given ID"""
        order = self.client.request_json('GET', '/orders/' + str(id))
        #print "getbyid",order
        print self.client
        return Order(order,client=self.client)


    def getOrderProductName(self,id):
        """Returns name of product of an order by given ID"""
        order = self.client.request_json('GET', '/orders/' +str(id) + '/products/')
        return order[0]["name"]

class Order(Resource):
    """An individual order"""

    def create(self):
        """Creates a new order"""
        body = json.dumps(self.get_fields())
        order = self.client.request_json('PUT', '/orders', body)

    def update(self):
        """Updates local changes to the order"""
        body = json.dumps(self.get_fields())
        order = self.client.request_json('PUT', '/orders/' + str(self.id), body)

    def update_field(self, key, value):
        body = json.dumps({key:value})
        self.client.request_json('PUT', '/orders/' + str(self.id),body)

    def updateShipment_field(self,key,value):
        body = json.dumps({key:value})
        print self.order_id
        self.client.request_json('PUT','/orders/shipments/'+str(self.id),body)

    def delete(self):
        """Deletes the order"""
        response, content = self.client.request('DELETE', '/orders/' + str(self.id))

class OptionSets(Resource):
    """Option sets collection"""

    def get(self):
        """Returns list of option sets"""
        optionsets = self.client.request_json('GET', '/optionsets')
        return [OptionSet(optionset) for optionset in optionsets]

    def get_by_id(self, id):
        """Returns an individual option set by given ID"""
        optionset = self.client.fetch_obj('GET', '/optionsets/' + str(id))
        return OptionSet(optionset)

class OptionSet(Resource):
    """An individual option set"""

    def create(self):
        """Creates a new option set"""
        body = json.dumps(self.get_fields())
        optionset = self.client.request_json('PUT', '/optionsets', body)

    def update(self):
        """Updates local changes to the option set"""
        body = json.dumps(self.get_fields())
        optionset = self.client.request_json('PUT', '/optionsets/' + str(self.id), body)

    def delete(self):
        """Deletes the option set"""
        response, content = self.client.request('DELETE', '/optionsets/' + str(self.id))

class Categories(Resource):
    """Categories collection"""

    def get(self):
        """Returns list of categories"""
        categories = self.client.request_json('GET', '/categories')
        return [Category(category) for category in categories]

    def get_by_id(self, id):
        """Returns an individual category by given ID"""
        category = self.client.request_json('GET', '/categories/' + str(id))
        return Category(category)

    def add(self, fields=None):
        """Adds the product"""
        body = json.dumps(fields)
        category = self.client.request_json('POST', '/categories/', body)
        return category
    

class Category(Resource):
    """An individual category"""

    def create(self):
        """Creates a new category"""
        body = json.dumps(self.get_fields())
        category = self.client.request_json('PUT', '/categories', body)

    def update(self):
        """Updates local changes to the category"""
        body = json.dumps(self.get_fields())
        category = self.client.request_json('PUT', '/categories/' + str(self.id), body)

    def delete(self):
        """Deletes the category"""
        response, content = self.client.request('DELETE', '/categories/' + str(self.id))

class Shipments(Resource):
    """Shipments"""
    def create(self,prod_id,fields=None):
        body = json.dumps(fields)
        shipment = self.client.request_json('POST','/orders/%s/shipments' %prod_id,body)

    #def update(self):
    #    body = json.dumps(self.get_fields())
    #    images = self.client.request_json('PUT', '/orders/%s/shipments' %self.id,body)

    def get_by_id(self, id):
        """Returns an individual shipment for order by given ID"""
        shipment = self.client.request_json('GET', '/orders/' + str(id) + '/shipments/')
        print shipment
        return Order(shipment[0], client=self.client)

    def delete(self):
        """delete shipments"""
        response,content = self.client.request_json('DELETE','/orders/shipments' + str(self.id), body)

class OrderProduct(Resource):

    def get_by_id(self,id):
        orderProduct = self.client.request_json('GET','/orders/'+str(id) + '/products/')
        return Order(orderProduct[0],client=self.client)
    
class Image(Resource):
    """An individual brand"""

    def create(self, prod_id, fields=None):
        """Creates a new image"""
        body = json.dumps(fields)
        brand = self.client.request_json('POST', '/products/%s/images' % prod_id, body)

    def update(self):
        """Updates image for product"""
        body = json.dumps(self.get_fields())
        image = self.client.request_json('PUT', '/products/%s/images%s' % (prod_id, img_id) , body)
        print image

    def delete(self):
        """Deletes image"""
        response, content = self.client.request_json('DELETE', '/products/%s/images%s' % (prod_id, img_id) , body)
