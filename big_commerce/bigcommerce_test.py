import api


recent_orders = api.Orders.get()


for order in recent_orders:
	products = api.Orders.get_products_info(order.id)
	for product in products:
		##do something to save product info
		pass
#		print product
	
#	shipments = api.Orders.get_shipments_info(order.id)
	if order.customer_id > 0:
		##store customer info
		customers = api.Customers.get_by_id(order.customer_id)
	
	shipping_addresses = api.Orders.get_shipping_address(order.id)
	for address in shipping_addresses:
		##store shipping address
		print address


	

    
