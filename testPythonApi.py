import api2
import csv
import datetime
import time
from email.utils import formatdate

#API_HOST = 'https://store-1eaef.mybigcommerce.com'
API_HOST = 'https://store-cbfd8.mybigcommerce.com'
API_PATH = '/api/v2'
API_USER = 'admin'
#API_KEY  = '0270f4680ac3eb5796ab3f9fe5a0e46299fe14cd'
API_KEY = 'e3a4804855753b8981e4787115c65edbccd339df'
conn = api2.Connection(API_HOST,API_PATH,API_USER,API_KEY)
store_categories = api2.Categories(client=conn)
store_products = api2.Products(client=conn)
store_orders = api2.Orders(client=conn)
store_images = api2.Image(client=conn)
store_shipments = api2.Shipments(client=conn)
store_orderProducts = api2.OrderProduct(client=conn)

def allCategories():      #checks categories listed
    categories = store_categories.get()
    allCategories = []
    for category in categories:
        allCategories.append(category.name)
    return allCategories

def allCategoriesClass():
    categories = store_categories.get()
    allCategories = []
    for category in categories:
        allCategories.append(category)
    return allCategories

def allProducts():      #returns all products in a list with names
    products = store_products.get()
    allProducts = []
    for product in products:
        allProducts.append(product.name)
    return allProducts

def allProductsClass():     #returns all products in a list as a class
    products = store_products.get()
    allProducts = []
    for product in products:
        allProducts.append(product)
    return allProducts

def checkCategories(): #checks categories listed
    categories = store_categories.get()
    allcategories = []
    for category in categories:
        print category.name,category.id
    

def checkProducts():        #checks all products listed
    products = store_products.get()
    for product in products:
        print "Name:", product.name
        print "ID:",product.id
        #print "SKU:", product.sku
        #print "Price:", product.price

def checkOrders():      #checks orders
    orders = store_orders.get()
    for order in orders:
        print "order", store_orders.get_by_id(order.id)
        print "created:", store_orders.getOrderProductName(order.id)
        #print "modified:", order.date_modified
        #order.status = 'Refunded'

def storeOrdersWithID():
    orders = store_orders.get()
    ordersWithID = dict()
    for order in orders:
        ordersWithID[order.products['url']] = order.id
    return ordersWithID

def storeProductsWithID():
    products = store_products.get()
    productsWithID = dict()
    for product in products:
        productsWithID[product.name] = product.id
    return productsWithID

def storeCategoriesWithID():
    categories = store_categories.get()
    categoriesWithID = dict()
    for category in categories:
        categoriesWithID[category.name] = category.id
    return categoriesWithID

def convertDateToRfc(lastUpdated):
    #'25-May-2012'
    monthToNumber = {"January":1,"Jan":1,"February":2,"Feb":2,"March":3,"Mar":3,
                     "April":4,"Apr":4,"May":5,"Jun":6,"Jul":7,"August":8,
                     "Aug":8,"Sep":9,"Oct":10,"Nov":11,"Dec":12}
    timeSplit = lastUpdated.split("-") #[Day,Month,Year]
    (day,month,year) = int(timeSplit[0]),timeSplit[1],int(timeSplit[2])
    monthNumber = monthToNumber[month]
    if (year < 13):     #current year
        year = 2000 + year
    else:
        year = 1900 + year
    time_tuple = (year,monthNumber,day,0,0,0,0,0,0)
    timeStamp = time.mktime(time_tuple)
    return formatdate(timeStamp)
    
def createShipments(ID,orderAddressID,trackingNumber,
                    comments,orderProductID,quantity):    
    #order = store_orders.get_by_id(ID)
    #productsWithID = storeProductsWithID()
    #productName = store_orders.getOrderProductName(ID)
    #orderProduct = store_orderProducts.orderProductget_by_id(ID)
    print orderProductID
    shipment = store_shipments.create(ID,{"order_address_id":orderAddressID,
                                          "tracking_number":trackingNumber,
                                          "comments":comments,
                                          "items":[{u'order_product_id': orderProductID,
                                                    u'quantity': quantity}]})
    
    

def addProduct(name,category,price,weight,description,visible,
               lastUpdated,typ='physical',availability='available'):
    rfcLastUpdated = convertDateToRfc(lastUpdated)
    newProduct = store_products.add({"name":name,'categories':category,
                                     "price":price,"is_visible":visible,
                                     "date_modified":rfcLastUpdated,
                                     "description":description,
                                     "type":typ,'weight':weight,
                                     'availability':availability})

def deleteProductID(ID):
    product = store_products.get_by_id(ID)
    product.delete()

def updateOrderWithID(ID,billingAddress,shippingAddress):
    order = store_orders.get_by_id(ID)
    order.update_field("status",u'Shipped')
    #order = store_or
    #order.update_field("billing_address",billingAddress)
    #order.update_field("shippingAddress",shippingAddress)

def updateProductWithID(ID,name,category,price,weight,
                        description,visible,lastUpdated,typ='physical',
                        availability='available'): #updates product
    product = store_products.get_by_id(ID)
    product.update_field("name",name)
    product.update_field("categories",category)
    product.update_field("price",price)
    product.update_field("weight",weight)
    product.update_field("description",description)
    product.update_field("is_visible",visible)
    #print "dateMOD:", lastUpdated
    product.update_field("date_modified",convertDateToRfc(lastUpdated))

def addCategory(newCategories):
    count = 0 
    for newCategory in newCategories:   
        if count == 0:      #adds Parent (first) category
            print newCategory
            newCategory = store_categories.add({"name":newCategory})
            print "newCategory:",newCategory
            newCategoryID = newCategory.get("id")
        else:   #for Sub-Categories
            newCategory = store_categories.add({"name":newCategory,
                                                "parent_id": newCategoryID})
            subCategoryID = newCategory.get("id")
        count += 1
    return subCategoryID


def addSubCategory(newCategories,categoryID):  #if category exists, but not subcategory
    count = 0
    for newCategory in newCategories:
        count += 1
        if count == 1:  #skips Parent (first) category
            newCategory = store_categories.get_by_id(categoryID)
            #print "newCat:", newCategory
            newCategoryID = newCategory.id
        else:
            newCategory = store_categories.add({"name":newCategory,
                                                "parent_id":newCategoryID})
            subCategoryID = newCategory.get("id")
    return subCategoryID

def findSubCategory(newCategories): #from most specific sub category
    #print "newCat:", newCategories
    categoriesWithID = storeCategoriesWithID()
    subCategoryID = categoriesWithID[newCategories[-1]]
    return subCategoryID


def checkIfCommon(c1,categories):#compares categories listed with all categories
    for category in categories:
        for categoryListed in c1:
            #print "categoryListed:", categoryListed
            #print "category.name:", category.name
            if categoryListed == category.name:
                return (True,category.name,category.id)
    return (False,None,0)

def currentDay():
    now = datetime.datetime.now()
    time = str(now.day)+"-"+now.strftime("%B")+"-"+str(now.year)[-2:]
    return time


def addFromCsv():       #adds from CSV file (currently only adds one product)
    with open('DealExtreme_Small_DateUpdatedColumn.csv','rb') as f:
        reader = csv.reader(f)
        count = 0
        productsWithID = storeProductsWithID()#dictionary with product name and id
        categoriesWithID = storeCategoriesWithID()
        for product in reader:  #each product is stored as a list with details
            try:
                count += 1
                if count == 1:      #first row with name of details (title,weight,etc)
                    continue
                name = product[13]      #index 13 is title
                print "name:", name
                price = product[5][1:] #gets rid of dollar sign
                specifications = product[3]
                index = specifications.index("Weight")
                weight = specifications[index+8:]
                description = product[4]
                visible = product[19]
                if visible == "yes":
                    visible = True
                else:
                    visible = False
                lastUpdated = product[20]
                image = "http://" + product[8].split(",")[0]  #gets rid of space
                if (name in allProducts()) and (lastUpdated != currentDay()):
                    #product exists and updated
                    continue
                categoriesListed = product[10].split(",")
                categories = allCategoriesClass()
                if checkIfCommon(categoriesListed,categories)[0]: #category exists
                    categoryID = checkIfCommon(categoriesListed,categories)[2]
                    if len(categories) == 1:
                        categoryIndex = findSubCategory(categoriesListed)
                    if checkIfCommon(categoriesListed[1:],categories)[0]:
                        #subCategory exists
                        category = checkIfCommon(categoriesListed,categories)[1]
                        #print name,category
                        categories = allCategoriesClass() #updated categories                    
                        #categoryIndex = checkIfCommon(categoriesListed,
                        #                              categories)[2]
                        categoryIndex = findSubCategory(categoriesListed)
                    else:
                        #adding subCategory
                        categoryIndex = addSubCategory(categoriesListed,categoryID)
                        categories = allCategoriesClass()
                    #Category identity
                else:       #if categoryListed doesn't match those of site category
                    categoryIndex = addCategory(categoriesListed)
                    category = checkIfCommon(categoriesListed,categories)[1]
                    categories = allCategoriesClass() #updated categories after adding
                    assert (checkIfCommon(categoriesListed,categories)[0] == True)
                    #print "new"
                    #print name,category
                    #Category identity
                #print categoryIndex
                #print price
                #print weight
                #print image
                if (name in allProducts()) and (lastUpdated == currentDay()):
                    #product exists and not updated
                    updateProductWithID(productsWithID[name],name,[categoryIndex],
                                        price,weight,description,visible,lastUpdated)
                    continue
                addProduct(name,[categoryIndex],price,weight,description,visible,
                           lastUpdated)
                lastProductID = allProductsClass()[-1].id
                images = store_images.create(lastProductID,{"image_file":image})
                #print lastProductID
                if count == 1000:      #TEMPORARY (stops after one product)
                    break
            except:
                print "skipped:"
                

            
def readCsv():      #reads from csv file
    with open('DealExtreme_Small_DateUpdatedColumn.csv','rb') as f:
        reader = csv.reader(f)
        count = 0 
        for row in reader:
            print row
            count +=1
            if count == 4:
                break

def writecsv():     #writes a file as a csv file
    with open('some.csv', 'wb') as f:
        try:
            writer = csv.writer(f)
            writer.writerow(('Height','Width','Length'))
            for i in xrange(5):
                writer.writerow((i,i*2,i/3))
        finally:
            f.close
    print open('some.csv','rt').read()
        
