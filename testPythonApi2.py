import api2
import csv

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

def allCategories():      #checks categories listed
    categories = store_categories.get()
    allCategories = []
    for category in categories:
        allCategories.append(category.name)
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
        print category.name
    

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
        print "created:", order.date_created
        #print "modified:", order.date_modified
        #order.status = 'Refunded'

def createProduct(name,category,price,weight,typ='physical',availability='available'):
    newProduct = store_products.add({"name":name,'categories':category,
                                     "price":price,"is_visible":True,
                                     "type":typ,'weight':weight,
                                     'availability':availability})

def deleteProductID(ID):
    product = store_products.get_by_id(ID)
    product.delete()



def updateProductID(ID,image):
    product = store_products.get_by_id(ID)
    product.images = image
    product.update()

def checkIfCommon(c1,categories):#compares categories listed with all categories
    for category in categories:
        for categoryListed in c1:
            if categoryListed in category:
                return (True,category)
            elif category in categoryListed:
                return (True,category)
    return (False,None)

def addFromCsv():       #adds from CSV file (currently only adds one product)
    with open('dealextreme.csv','rb') as f:
        reader = csv.reader(f)
        count = 0
        for product in reader:  #each product is stored as a list with details
            name = product[13]      #index 13 is title
            categoriesListed = product[10].split(",")
            categories = allCategories()
            if checkIfCommon(categoriesListed,allCategories())[0]:
                category = checkIfCommon(categoriesListed,allCategories())[1]
                categoryIndex = categories.index(category)
            price = product[5][1:] #gets rid of dollar sign
            specifications = product[3]
            count += 1
            if count == 1:
                continue
            index = specifications.index("Weight")
            weight = specifications[index+8:]
            image = "http://" + product[8].split(",")[0]  #gets rid of space
            #print name
            #print categoryIndex
            #print price
            #print weight
            #print image
            lastProductID = allProductsClass()[-1].id
            if count == 3:      #TEMPORARY (stops after one product)
                break
            if name in allProducts():
                continue
            createProduct(name,[categoryIndex],price,weight)
            lastProductID = allProductsClass()[-1].id
            images = store_images.create(lastProductID,{"image_file":image})
            #print lastProductID
            if count == 3:      #TEMPORARY (stops after one product)
                break
            

            
def readCsv():      #reads from csv file
    with open('dealextreme.csv','rb') as f:
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
        
