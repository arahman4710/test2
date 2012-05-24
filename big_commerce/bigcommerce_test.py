import api

def recent_orders_info():
	
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
			print customers
	
		shipping_addresses = api.Orders.get_shipping_address(order.id)
		for address in shipping_addresses:
			##store shipping address
			pass
	
def get_uncomplete_orders():
	
	for order in all_orders_in_db:
	
		shipments = get_shipment_info(order.id) ##all shipments for a particular order
	
		if not shipments: ##no shipments yet
			pass
	
		else:
			product_shipped_list = [] ##initialize variable for a list of products shipped already
			for shipment in shipments:
				for item in shipment:
					quantity = item.quantity
					product_id = item.product_id
					pair = (product_id, quantity)
					product_shipped_list.append(pair)
		
			products_in_order = api.Orders.get_products_info(order.id) ## all products ordered by customer for a particular order
			product_in_order_list = []
		
			for product in products_in_order:
				pair = (product.product_id, product.quantity)
				product_in_order_list.append(pair)
			
		
			for product in product_in_order_list: ##iterate through each product ordered, to see if its full quantity ordered is fulfilled
		
				product_shipped = False
			
				for shipped in product_shipped_list:
				
					if shipped[0] == product[0]: ## detected this product id has been shipped
					
						product_shipped = True
					
						current_shipped_item = shipped[0]
						total_shipped_item_quantity = 0
					
						for shipped in product_shipped_list: ## find out for all shipments, the quantity of this product added together
							if shipped[0] == current_shipped_item:
								total_shipped_item_quantity += shipped[1]
					
						if total_shipped_item_quantity != product[1]:
							##some amount not shipped, record the unfulfilled order in db
							break
			
				if product_shipped = False:
					## a product not shipped at all, record unfulfilled order to db
					pass
						
				

						
			
		


	

    
