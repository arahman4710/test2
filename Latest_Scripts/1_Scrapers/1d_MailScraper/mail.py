from imaplib import *
import re
from decimal import *
import MySQLdb

def PLcheck(msg):
	#code to extract information from the email
	booknum = re.search('(?is)Confirmation\s*?\#.*?[a-z0-9]+', msg)
	roomcost = re.search('(?is)Room\s*?Cost.*?\$[0-9.]+', msg)
	numrooms = re.search('(?is)Number\s*?of\s*?Rooms.*?[0-9.]+', msg)
	numnights = re.search('(?is)Number\s*?of\s*?Nights.*?[0-9.]+', msg)
	subtotal = re.search('(?is)Room\s*?Subtotal:.*?\$[0-9.]+', msg)
	taxes = re.search('(?is)Taxes\s*?and\s*?Fees.*?\$[0-9.]+', msg)
	totalcost = re.search('(?is)Total\s*?Room\s*?Cost.*?\$[0-9.]+', msg)
	out = ''
	if (booknum and roomcost and numrooms and numnights and subtotal and taxes and totalcost):
		booknum = re.search('[0-9]+', booknum.group())
		roomcost = re.search('(?<=\$)[0-9.]+', roomcost.group())
		numrooms = re.search('[0-9.]+', numrooms.group())
		numnights = re.search('[0-9.]+', numnights.group())
		subtotal = re.search('(?<=\$)[0-9.]+', subtotal.group())
		taxes = re.search('(?<=\$)[0-9.]+', taxes.group())
		totalcost = re.search('(?<=\$)[0-9.]+', totalcost.group())
		if (booknum and roomcost and numrooms and numnights and subtotal and taxes and totalcost):
			booknum = booknum.group()
			roomcost = roomcost.group()
			numrooms = numrooms.group()
			numnights = numnights.group()
			subtotal = subtotal.group()
			taxes = taxes.group()
			totalcost = totalcost.group()
			#checks that the values are within an acceptable range
			test1 = (0.1 > (Decimal(roomcost) * Decimal(numrooms) * Decimal(numnights)) - Decimal(subtotal))
			test2 = (0.1 > (Decimal(subtotal) + Decimal(taxes)) - Decimal(totalcost))	
			if (test1 and test2):
				#checks that the booking number (and the rest of the email) isn't already in our database
				c = db.cursor()
				print '\n'
				c.execute("SELECT id FROM bids WHERE id=" + booknum)
				a = c.fetchone()
				print a
				if (a == None):
					#if not already done insert into database
					c.execute("INSERT INTO bids VALUES (%s, %s, %s, %s, %s, %s, %s)", (booknum, roomcost, numrooms, numnights, subtotal, taxes, totalcost))
					return True
				else:
					return False
		else:
			print 'error parsing message ' + index + 'in second step'
	else:
		print 'error parsing message ' + index + 'in first step'
	return False

def HWcheck(msg):
	booknum = re.search('(?is)Hotwire\s*?Itinerary.*?[0-9]+', msg)
	roomcost = re.search('(?is)Hotel\s*?rate.*?\$[0-9.]+', msg)
	numrooms = re.search('(?is)Rooms:.*?[0-9.]+', msg)
	numnights = re.search('(?is)Nights:.*?[0-9.]+', msg)
	subtotal = re.search('(?is)Subtotal:.*?\$[0-9.]+', msg)
	taxes = re.search('(?is)Tax.*?Fees:.*?\$[0-9.]+', msg)
	totalcost = re.search('(?is)Total\s*?price:.*?\$[0-9.]+', msg)
	out = ''
	if (booknum and roomcost and numrooms and numnights and subtotal and taxes and totalcost):
		booknum = re.search('[0-9]+', booknum.group())
		roomcost = re.search('(?<=\$)[0-9.]+', roomcost.group())
		numrooms = re.search('[0-9.]+', numrooms.group())
		numnights = re.search('[0-9.]+', numnights.group())
		subtotal = re.search('(?<=\$)[0-9.]+', subtotal.group())
		taxes = re.search('(?<=\$)[0-9.]+', taxes.group())
		totalcost = re.search('(?<=\$)[0-9.]+', totalcost.group())
		if (booknum and roomcost and numrooms and numnights and subtotal and taxes and totalcost):
			booknum = booknum.group()
			roomcost = roomcost.group()
			numrooms = numrooms.group()
			numnights = numnights.group()
			subtotal = subtotal.group()
			taxes = taxes.group()
			totalcost = totalcost.group()
			out = '\nHW Booking: ' + booknum + '\nRoom Cost: ' + roomcost + '\nRooms: ' + numrooms + '\nNights: ' + numnights + '\nSubtotal: ' + subtotal + '\nTaxes: ' + taxes + '\nTotal: ' + totalcost
			test1 = (0.1 > (Decimal(roomcost) * Decimal(numrooms) * Decimal(numnights)) - Decimal(subtotal))
			test2 = (0.1 > (Decimal(subtotal) + Decimal(taxes)) - Decimal(totalcost))	
			if (test1 and test2):
				return out
		else:
			print 'error parsing message ' + index + 'in second step'
	else:
		print 'error parsing message ' + index + 'in first step'
	return False


global db
db = MySQLdb.connect(user='root', passwd='charles', db='acuity')



server = IMAP4_SSL('imap.gmail.com', 993)
server.login('track@fetchopia.com', 'track786')
boxes = server.list()[1]
inbox = server.select('INBOX')
data = server.search(None, '()')
print data
data = data[1][0].split(' ')
#loops through to see who the email is probably from, then parses it
#the commented code is for moving the emails to different boxes
#currently commented to make testing easier, should be removed when implemented
try:
	for index in data:
		int(index)
		message = server.fetch(index, '(BODY[TEXT])')
		message = message[1][0][1]
		if (re.search('(?i)priceline', message)):
			success = 'test'
			success = PLcheck(message)
			if (success):
				# server.copy(index, 'PROCESSED')
				print success
				# open('output.txt', 'a').write(success + '\n')
			# else:
				# server.copy(index, 'FAILED')
		elif (re.search('(?i)hotwire', message)):
			success = 'test'
			success = HWcheck(message)
			if (success):
				# server.copy(index, 'PROCESSED')
				print success
				# open('output.txt', 'a').write(success + '\n')
			# else:
				# server.copy(index, 'FAILED')
		# else:
			# server.copy(index, 'FAILED')
	# for index in data:
		# int(index)
		# server.store(index, '+FLAGS', '\\Deleted')
except ValueError:
	None

