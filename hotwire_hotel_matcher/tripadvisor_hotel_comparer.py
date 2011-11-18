import re
import MySQLdb
import Levenshtein
import time


class Connection():
	database = MySQLdb.connect(user='root', passwd='areek', db='acuity')
	cursor = database.cursor()

def print_timing(func):
    def wrapper(*arg):
        t1 = time.time()
        res = func(*arg)
        t2 = time.time()
        print '%s took %0.3f ms' % (func.func_name, (t2-t1)*1000.0)
        return res
    return wrapper

def printable(str):
    control = "".join(map(unichr, range(0,127)))
    control = re.escape( control)
    return re.sub("[^%s]" % control, "", str)

@print_timing
def com_kayak_internal(input):
    Connection.cursor.execute("SELECT hotelName,hotelid,hoteladdress FROM hotels WHERE cities_cityid = 668")
    internal_hotel = []
    internal_hotel = Connection.cursor.fetchall()
    log_file = open("c:/users/areek/desktop/fechopia/database/compared_hotel_kayak_add_by_address.csv",'w')
    log_file2 = open("c:/users/areek/desktop/fechopia/database/compared_hotel_kayak_reject.csv",'w')
    count = 0
    for t_hotel in input:
        max = 0.0
        n_max = 0.0
        add_max =0.0
        max2 = 0.0
        n_max2 = 0.0
        add_max2 =0.0
        match=[]
        match2=[]
        street_no = re.match("^[0-9]+",t_hotel[2])
        for o_hotel in internal_hotel:
            try:
                n_comp = Levenshtein.ratio(normalize(o_hotel[0]),normalize(str(t_hotel[0])))
                add_comp=Levenshtein.ratio(add_norm(o_hotel[2]),add_norm(str(t_hotel[2])))
            except:
                print normalize(t_hotel[0])
                print normalize(o_hotel[0])
                continue
            #print '__________GONE THROUGH________________'

            '''
            n_comp2= n_comp
            add_comp2 = add_comp


            if n_comp2 > n_max2:
                add_max2 = add_comp2
                n_max2 = n_comp2
                max2 = n_max2 + add_max2
                match2 = [o_hotel[0],o_hotel[2],t_hotel[0],t_hotel[2],n_max2,add_max2,max2]

            '''

            if street_no:
                o_hotel_street_no = re.match("^[0-9]+",o_hotel[2])
                if o_hotel_street_no:
                    if o_hotel_street_no.group(0)!=street_no.group(0):
                        continue

            if  add_comp > n_max:
                n_max = n_comp
                add_max = add_comp
                max = n_max + add_max
                match =[o_hotel[0],o_hotel[2],t_hotel[0],t_hotel[2],n_max,add_max,max,o_hotel[1],t_hotel[1]]
                if add_comp ==1.0:
                    #internal_hotel.remove(o_hotel)
                    break



                #threshold more then 1.15 max or add_max 0.8
                #duplicate record check
        #if match[2]>0.8:
        if match:
            if match[6] > 1.15 or (match[5] > 0.7):
                #
                Connection.cursor.execute("INSERT INTO `acuity`.`kayakhotels` (`KayakId`, `Hotels_HotelId`, `KayakName`) VALUES ('"+ str(match[8])+"', '"+str(match[7])+"', '"+printable(re.sub('''(['"])''', r'\\\1',str(match[2])))+"');")
                Connection.database.commit()
                log_file.write(match[0].replace(",","")+', '+match[2].replace(",","")+', '+match[1].replace(",","")+', '+match[3].replace(",","")+', '+str(match[4])+', '+str(match[5])+', '+str(match[6])+'\n')
            else:
                log_file2.write(match[0].replace(",","")+', '+match[2].replace(",","")+', '+match[1].replace(",","")+', '+match[3].replace(",","")+', '+str(match[4])+', '+str(match[5])+', '+str(match[6])+'\n')
        #log_file2.write(match2[0].replace(",","")+', '+match2[2].replace(",","")+', '+match2[1].replace(",","")+', '+match2[3].replace(",","")+', '+str(match2[4])+', '+str(match2[5])+', '+str(match2[6])+'\n')
        #print match[0].replace(",","")+', '+match[2].replace(",","")+', '+match[1].replace(",","")+', '+match[3].replace(",","")+', '+str(match[4])+', '+str(match[5])+', '+str(match[6])
        #else:
        #count += 1
    #print "not shown " + str(count)
    log_file.close()
    log_file2.close()

@print_timing
def comp():
    Connection.cursor.execute("SELECT hotelName,hotelid,hoteladdress FROM hotels WHERE cities_cityid = 668")
    internal_hotel = []
    internal_hotel = Connection.cursor.fetchall()

    Connection.cursor.execute("select hotel_name, hotel_id, address from tripadvisor_hotel_review_overview WHERE city LIKE '%houston%'")
    tripadvisor_hotels=[]
    log_file = open("c:/users/areek/desktop/fechopia/database/compared_hotel_tripadvisor_add_by_address.csv",'w')
    log_file2 = open("c:/users/areek/desktop/fechopia/database/compared_hotel_tripadvisor_reject.csv",'w')
    tripadvisor_hotels=Connection.cursor.fetchall()
    count = 0
    for t_hotel in tripadvisor_hotels:
        max = 0.0
        n_max = 0.0
        add_max =0.0
        max2 = 0.0
        n_max2 = 0.0
        add_max2 =0.0
        match=[]
        match2=[]
        street_no = re.match("^[0-9]+",t_hotel[2])
        for o_hotel in internal_hotel:
            
            n_comp = Levenshtein.ratio(normalize(o_hotel[0]),normalize(t_hotel[0]))
            add_comp=Levenshtein.ratio(add_norm(o_hotel[2]),add_norm(t_hotel[2]))
            
            '''
            n_comp2= n_comp
            add_comp2 = add_comp


            if n_comp2 > n_max2:
                add_max2 = add_comp2
                n_max2 = n_comp2
                max2 = n_max2 + add_max2
                match2 = [o_hotel[0],o_hotel[2],t_hotel[0],t_hotel[2],n_max2,add_max2,max2]

            '''
            
            if street_no:
                o_hotel_street_no = re.match("^[0-9]+",o_hotel[2])
                if o_hotel_street_no:
                    if o_hotel_street_no.group(0)!=street_no.group(0):
                        continue
            
            if  add_comp > n_max:
                n_max = n_comp
                add_max = add_comp
                max = n_max + add_max
                match =[o_hotel[0],o_hotel[2],t_hotel[0],t_hotel[2],n_max,add_max,max,o_hotel[1],t_hotel[1]]
                if add_comp ==1.0:
                    #internal_hotel.remove(o_hotel)
                    break

            

                #threshold more then 1.15 max or add_max 0.8
                #duplicate record check
        #if match[2]>0.8:
        if match[6] > 1.15 or (match[5] > 0.7):
            Connection.cursor.execute("UPDATE `acuity`.`tripadvisor_hotel_review_overview` SET `internal_hotelid` = '"+str(match[7])+"' WHERE `Hotel_id` = '"+ str(match[8])+"' ;")
            Connection.database.commit()
            log_file.write(match[0].replace(",","")+', '+match[2].replace(",","")+', '+match[1].replace(",","")+', '+match[3].replace(",","")+', '+str(match[4])+', '+str(match[5])+', '+str(match[6])+'\n')
        else:
            log_file2.write(match[0].replace(",","")+', '+match[2].replace(",","")+', '+match[1].replace(",","")+', '+match[3].replace(",","")+', '+str(match[4])+', '+str(match[5])+', '+str(match[6])+'\n')
        #log_file2.write(match2[0].replace(",","")+', '+match2[2].replace(",","")+', '+match2[1].replace(",","")+', '+match2[3].replace(",","")+', '+str(match2[4])+', '+str(match2[5])+', '+str(match2[6])+'\n')
        print match[0].replace(",","")+', '+match[2].replace(",","")+', '+match[1].replace(",","")+', '+match[3].replace(",","")+', '+str(match[4])+', '+str(match[5])+', '+str(match[6])
        #else:
        #count += 1
    #print "not shown " + str(count)
    log_file.close()
    log_file2.close()

def add_norm(input):
    return input.lower().replace(".","").replace(" drive"," dr").replace(" parkwy"," pkwy").replace(" boulevard"," blvd").replace("@","at").replace(" street"," st").replace(" &amp; "," & ").replace(" road"," rd").replace(" east"," e").replace(" north"," n").replace(" south"," s").replace(" west"," w").replace(" avenue"," ave").replace(" freeway"," frwy").replace(" fwy"," frwy").replace(" parkway"," pkwy").strip()


"""

add Drive with dr.
asame blvd
remove .
road with rd
small caps

"""
def normalize(input):
    #return input.lower().replace(" (minnesota)","").replace(" bloomington","").replace(" menneapolis","").replace(" and ","&").replace(" And ","&").replace("Hotel","").strip()
    return input.replace("Houston","").replace(" and ","&").replace(" And ","&").replace("Hotel","").strip()

    """
        Connection.cursor.execute("SELECT tempo.hotelName,LEVENSHTEIN_RATIO\
    (tempo.hotelName,'"+re.sub('''(['"])''', r'\\\1', t_hotel[0])+"') AS percent,tempo.hotelid FROM \
    (SELECT hotelName,hotelid FROM hotels WHERE cities_cityid = 668) \
    AS tempo ORDER BY percent DESC LIMIT 1")
        remp = Connection.cursor.fetchall()
        remp[0][0] =remp[0][0].replace("Houston","").replace("and","&")
        print "for "+re.sub('''(['"])''', r'\\\1', t_hotel[0])+' match  ' + str(remp[0][0].replace("Houston","").replace("and","&"))+' with ratio of ' +str(remp[0][1])
        log_file.write( "for "+re.sub('''(['"])''', r'\\\1', t_hotel[0])+' match  ' + str(remp[0][0])+' with ratio of ' +str(remp[0][1])+'\n' )
        if remp[0][1] == 100:
            print "inserted! "+ t_hotel[0]
            Connection.cursor.execute("INSERT INTO `acuity`.`internal_tripadvisor_hotel`(`Internal_hotel_id`, `Tripadvisor_hotel_id`) \
            VALUES ('"+str(remp[0][2])+"' , '"+ str(t_hotel[1])+"');")
            Connection.database.commit()
    log_file.close()

    """

if __name__ == "__main__":
    '''
    Connection.cursor.execute("CREATE TABLE IF NOT EXISTS `internal_tripadvisor_hotel`\
    (`Internal_hotel_id` INT(11) NOT NULL,`Tripadvisor_hotel_id` INT(11) \
    NOT NULL,KEY `FK_internal_tripadvisor_hotel` (`Internal_hotel_id`),\
    KEY `FK_internal_tripadvisor_hotel_tripadvisor` (`Tripadvisor_hotel_id`),\
    CONSTRAINT `FK_internal_tripadvisor_hotel_tripadvisor` FOREIGN KEY (`Tripadvisor_hotel_id`\
    REFERENCES `tripadvisor_hotel_review_overview` (`Hotel_id`),CONSTRAINT `FK_internal_tripadvisor_hotel`\
    FOREIGN KEY (`Internal_hotel_id`) REFERENCES `hotels` (`HotelId`)) ENGINE=INNODB DEFAULT CHARSET=utf8")
    Connection.database.commit()
    '''
    com_kayak_internal([[u'Houston Marriott at the Texas Medical Center', u'41727', u'6580 Fannin Street'], [u'Hotel Derek', u'31787', u'2525 West Loop South'], [u'The Lancaster', u'14175', u'701 Texas St'], [u'Hotel ICON', u'45770', u'220 Main Street'], [u'InterContinental Houston Near The Galleria', u'66162', u'2222 West Loop South'], [u'Club Quarters in Houston', u'115981', u'720 Fannin Street'], [u'Four Points by Sheraton Houston Southwest', u'96691', u'2828 Southwest Freeway'], [u'Alden-Houston', u'35987', u'1117 Prairie Street'], [u'La Quinta Inn &amp; Suites Houston Galleria Area', u'32587', u'1625 West Loop South'], [u'Hyatt Summerfield Suites Houston Galleria', u'3164', u'3440 Sage Road'], [u'The Westin Galleria Houston', u'17513', u'5060 West Alabama'], [u'Hyatt Regency Houston', u'34065', u'1200 Louisiana Street'], [u'Hilton Garden Inn Houston/Galleria Area', u'143359', u'3201 Sage Road'], [u'Extended Stay Deluxe Houston - Med. Ctr. - Reliant Pk. - Braeswood Blvd.', u'35262', u'1301 S. Braeswood Blve'], [u'Sheraton Suites Houston Near The Galleria', u'23092', u'2400 West Loop South'], [u'Crowne Plaza Hotel Houston River Oaks', u'37792', u'2712 Southwest Freeway'], [u'ESA Houston-Galleria Area', u'17249', u'4701 Westheimer Road'], [u'Hilton Houston Post Oak', u'18934', u'2001 Post Oak Blvd.'], [u'Four Points by Sheraton Houston, Memorial City', u'31605', u'10655 Katy Freeway'], [u'Country Inn &amp; Suites By Carlson Houston Hobby Airport', u'33187', u'8778 Airport Blvd'], [u'The St. Regis Houston', u'21161', u'1919 Briar Oaks Lane'], [u'Doubletree Hotel Houston Downtown', u'34351', u'400 Dallas Street'], [u'Sheraton Houston Brookhollow Hotel', u'34469', u'3000 North Loop West Frwy'], [u'Hyatt Place Bush IAH Airport', u'21978', u'300 Ronan Park Place'], [u'Homestead Houston-Med Ctr-Fann', u'66179', u'7979 Fannin Street'], [u'Hyatt Summerfield Suites Houston Energy Corridor', u'6683', u'15405 Katy Freeway'], [u'Houston Airport Marriott at George Bush Intercontinental', u'43164', u'18700 John F. Kennedy Blvd.'], [u'Crowne Plaza Suites Houston Sugar Land', u'45586', u'9090 Southwest Frwy'], [u'Renaissance Houston Greenway Plaza Hotel', u'14825', u'6 Greenway Plaza East'], [u'Holiday Inn Express Hotel &amp; Suites Houston-Dwtn Conv Ctr', u'4076', u'1810 Bell Street'], [u'Houston Marriott South at Hobby Airport', u'36211', u'9100 Gulf Freeway'], [u'Days Inn Houston West', u'70261', u'9535 Katy Freeway'], [u'Crowne Plaza Hotel Houston-Downtown', u'66156', u'1700 Smith Street'], [u'Hilton Americas- Houston', u'40791', u'1600 Lamar'], [u'Courtyard Houston Hobby Airport', u'3065', u'9190 Gulf Freeway'], [u'Crowne Plaza Hotel Houston North - Greenspoint', u'168366', u'425 North Sam Houston Pkwy E'], [u'Crowne Plaza Hotel Houston - Medical Center', u'36207', u'8686 Kirby Drive'], [u'Hampton Inn Houston-Hobby Airport', u'66188', u'8620 Airport Blvd.'], [u'Hampton Inn Houston-Near The Galleria', u'93846', u'4500 Post Oak Parkway'], [u'La Quinta Inn Houston Wilcrest', u'33546', u'11113 Katy Freeway'], [u'Omni Houston Hotel Westside', u'31984', u'13210 Katy Freeway'], [u'Hilton Houston Southwest', u'36558', u'6780 Southwest Freeway'], [u'Magnolia Hotel', u'31981', u'1100 Texas St'], [u'Hilton Houston Westchase', u'16010', u'9999 Westheimer Road'], [u'Clarion Inn Bush Intercontinental Airport', u'35237', u'15615 John F Kennedy Blvd'], [u'Hotel Zaza Houston', u'34356', u'5701 Main Street'], [u'La Quinta Inn &amp; Suites Houston Southwest', u'35695', u'6790 Southwest Freeway'], [u'Courtyard Houston Downtown /Convention Center', u'30982', u'916 Dallas Street'], [u'SpringHill Suites Houston Hobby Airport', u'35680', u'7922 Mosley Road'], [u'Houston Marriott North', u'35766', u'255 N Sam Houston Pkwy East'], [u'Doubletree Guest Suites Houston by the Galleria', u'8', u'5353 Westheimer Road'], [u'Courtyard Houston I-10 West/Energy Corridor', u'66197', u'12401 Katy Freeway (I-10 &amp; Dairy Ashford)'], [u'Drury Inn &amp; Suites Near the Galleria Houston', u'23132', u'1615 W Loop South'], [u'Homewood Suites By Hilton HOU Intercontinental Arpt', u'40209', u'1340 North Sam Houston Pkwy. East'], [u'Embassy Suites Houston - Near the Galleria', u'34355', u'2911 Sage Road'], [u'Hotel Sorella CITYCENTRE', u'244241', u'800 W Sam Houston Pkwy N'], [u'La Quinta Inn &amp; Suites Pearland', u'186909', u'9002 Broadway, Pearland'], [u'The Westin Oaks Houston', u'18870', u'5011 Westheimer at Post Oak'], [u'Courtyard Houston Westchase', u'23097', u'9975 Westheimer Rd'], [u'La Quinta Inn Houston Greenway Plaza', u'35700', u'4015 Southwest Freeway'], [u'JW Marriott Houston', u'44033', u'5150 Westheimer'], [u'Howard Johnson Express Inn - Houston Downtown', u'41108', u'4602 Katy Freeway/I-10'], [u'Hilton Garden Inn Houston Energy Corridor', u'194486', u'12245 Katy Freeway'], [u'The Houstonian Hotel, Club &amp; Spa', u'12942', u'111 North Post Oak Lane'], [u'Hilton Houston North', u'33753', u'12400 Greenspoint Drive'], [u'Courtyard Houston by The Galleria', u'177422', u'2900 Sage Road'], [u'Courtyard Houston Intercontinental Airport', u'20510', u'16500 Hedgecroft Drive'], [u'Homewood Suites by Hilton Houston Near the Galleria', u'151273', u'2950 Sage Road'], [u'Hotel Indigo Houston At The Galleria', u'115694', u'5160 Hidalgo Street'], [u'Holiday Inn Hotel &amp; Suites Houston (Medical Center)', u'12985', u'6800 South Main Street'], [u'Drury Inn &amp; Suites Houston Hobby Houston', u'4024', u'7902 Mosley Road'], [u'La Quinta Inn &amp; Suites Houston Hobby Airport', u'175667', u'8776 Airport Boulevard'], [u'Candlewood Suites Houston By The Galleria', u'35765', u'4900 Loop Central Drive'], [u'Aloft Houston by the Galleria', u'309034', u'5415 Westheimer Road'], [u'La Quinta Inn &amp; Suites Houston Bush IAH South', u'36500', u'15510 J.F.K. Boulevard'], [u'Inn at the Ballpark', u'41050', u'1520 Texas Avenue'], [u'Super 8 Houston/Brookhollow NW', u'38038', u'5655 West 34th Street'], [u'SpringHill Suites Houston Brookhollow', u'39607', u'2750 North Loop West 610'], [u'ESA Houston-Greenway Plaza', u'96980', u'2330 SW Frwy'], [u'MainStay Suites Texas Medical Center/Reliant Park', u'178976', u'3134 Old Spanish Trail'], [u'Comfort Inn Downtown', u'32667', u'5820 Katy Freeway'], [u'Sheraton North Houston at George Bush Intercontinental', u'7207', u'15700 John F. Kennedy Boulevard'], [u'Residence Inn Houston by The Galleria', u'66181', u'2500 McCue Road'], [u'Drury Inn &amp; Suites West Houston', u'4020', u'1000 North Highway 6'], [u'Baymont Inn and Suites Houston Brookhollow', u'36210', u'11002 Northwest Freeway'], [u'Residence Inn Houston Downtown/Convention Center', u'30088', u'904 Dallas Street'], [u'Super 8 IAH West/Greenspoint', u'207305', u'1230 N. Sam Houston Parkway E.'], [u'Sun Suites of Hobby (Clearlake)', u'25948', u'12485 Gulf Freeway'], [u'BEST WESTERN Heritage Inn', u'30355', u'10521 East Freeway'], [u'Sheraton Houston West Hotel', u'199674', u'11191 Clay Road'], [u'Hilton Houston Hobby Airport', u'12094', u'8181 Airport Boulevard'], [u'Baymont Inn and Suites Houston Hobby AP', u'37641', u'9902 Gulf Freeway'], [u'Hampton Inn Houston-Northwest', u'37554', u'20035 Northwest Frwy'], [u'Sun Suites of Westchase', u'66177', u'3100 West Sam Houston Parkway South'], [u'Holiday Inn Express Hotel &amp; Suites Houston Hwy 59s/Hillcroft', u'66195', u'6687 Southwest Freeway'], [u'Doubletree Hotel Houston Intercontinental Airport', u'36598', u'15747 Jfk Boulevard'], [u'Four Seasons Houston', u'185348', u'1300 Lamar Street'], [u'Hilton Garden Inn Houston/Pearland', u'188675', u'12101 Shadow Creek Pkwy, Pearland'], [u'Days Inn Houston-Galleria, TX', u'3978', u'3333 Fountain View Drive'], [u'Red Roof Inn Houston - Brookhollow', u'7376', u'12929 Northwest Fwy'], [u'Embassy Suites Houston - Energy Corridor', u'300200', u'11730 Katy Freeway'], [u'Holiday Inn Express Houston West Energy Corridor', u'66198', u'12323 Katy Freeway'], [u'Wingate by Wyndham Houston / Willowbrook', u'38008', u'9050 Mills Road'], [u'Omni Houston Hotel', u'32462', u'4 Riverway'], [u'Houston Marriott Westchase', u'17248', u'2900 Briarpark Dr.'], [u'Americas Best Value Inn/Houston FM 1960', u'155670', u'609 FM 1960 West Road'], [u'Baymont Inn and Suites Houston I-45 North', u'35102', u'17111 North Freeway'], [u'La Quinta Inn Houston Northwest', u'66204', u'11130 N.W. Freeway'], [u'BEST WESTERN Plaza Hotel &amp; Suites at Medical Center', u'30182', u'6700 S Main Street'], [u'Homestead Houston - Galleria', u'66161', u'2300 West Loop South'], [u'Holiday Inn Houston South Loop', u'13364', u'8111 Kirby Drive'], [u'Hampton Inn &amp; Suites Houston-Bush Intercontinental Aprt', u'197171', u'15831 Jfk Boulevard'], [u'La Quinta Inn Houston Medical / Reliant Center', u'33404', u'9911 Buffalo Speedway'], [u'Element Houston Vintage Park', u'204760', u'14555 Vintage Preserve Parkway'], [u'Americas Best Value Inn Houston Hobby Airport', u'109084', u'8800 Airport Boulevard'], [u"America's Inn near Sugar Land", u'45663', u'10552 SW Freeway'], [u'Country Inn &amp; Suites By Carlson Houston Intercontinental AP South', u'34441', u'15555 B John F Kennedy Blvd'], [u'BEST WESTERN Greenspoint Inn &amp; Suites', u'30378', u'14753 North Freeway'], [u'Greenway Plaza Inn and Suites', u'23698', u'2929 Southwest Freeway'], [u'ESA Houston-Katy Freeway', u'155673', u'11175 Katy Freeway'], [u'Holiday Inn Houston-Hobby Airport', u'12073', u'8611 Airport Boulevard'], [u'Regency Suites Bush Airport', u'168736', u'15420 West Hardy Road'], [u'Hilton Garden Inn Houston/Bush Intercontinental Airport', u'37648', u'15400 John F. Kennedy Boulevard'], [u'ESA Houston-Westchase', u'155674', u'3200 W.Sam Houston Pkwy'], [u'Houston Marriott West Loop by The Galleria', u'38013', u'1750 West Loop South'], [u'Extended Stay Deluxe Houston - Northwest', u'10527', u'5454 Hollister St'], [u'La Quinta Inn Houston East', u'36214', u'11999 East Freeway'], [u"America's Inn Near The Galleria", u'43127', u'8201 SW Freeway'], [u'Park Inn Houston North Hotel &amp; Conference Center, TX', u'12509', u'500 North Sam Houston Pkwy East'], [u'Comfort Inn Hwy. 290/NW', u'23272', u'7887 West Tidwell Road'], [u'Baymont Inn &amp; Suites Houston East', u'13692', u'828 Mercury Drive'], [u'Hampton Inn &amp; Suites Houston-Medical Ctr-Reliant Park', u'66178', u'1715 Old Spanish Trail'], [u'La Quinta Inn &amp; Suites Houston - Westchase', u'177549', u'10850 Harwin Drive'], [u'La Quinta Inn &amp; Suites Willowbrook', u'5543', u'18828 Highway 249'], [u'La Quinta Inn &amp; Suites Houston West Park 10', u'36630', u'15225 Katy Freeway'], [u'Candlewood Suites Beltway 8/Westheimer Road', u'196961', u'11280 Westheimer Road'], [u'Super 8 Houston/Dtwn/I-610', u'100413', u'5550 Homestead Road'], [u'Courtyard Houston Brookhollow', u'4064', u'2504 North Loop West'], [u'Hilton Garden Inn Houston Westbelt', u'102365', u'6855 West Sam Houston Parkway South'], [u'Homestead Houston - Willowbrook', u'16290', u'13223 Champions Centre Drive'], [u'Super 8 Houston East/Channelview Area', u'300265', u'5420 East Sam Houston Parkway North'], [u'La Quinta Inn &amp; Suites Houston Clay Road', u'102519', u'4424 Westway Park Boulevard'], [u'Days Inn and Suites Houston Hobby Airport', u'185495', u'9114 Airport Blvd'], [u'Holiday Inn Houston-InterContinental Arpt', u'65961', u'15222 John F. Kennedy Boulevard, Sam Hous...'], [u'Residence Inn Houston Medical Center/Reliant Park', u'37810', u'7710 South Main Street'], [u'Hampton Inn Houston I-10W/Energy Cor', u'18114', u'11333 Katy Freeway'], [u'Hilton Garden Inn Houston Northwest', u'35719', u'7979 Willow Chase Boulevard'], [u'Ramada Limited - Houston Southwest', u'155677', u'6885 Southwest Freeway'], [u'La Quinta Inn Houston Cy-Fair', u'34796', u'13290 FM 1960 West'], [u'BEST WESTERN Windsor Suites', u'28133', u'13371 FM 1960 Road W'], [u'Homewood Suites by Hilton Houston - Northwest/CY-FAIR', u'199461', u'13110 Wortham Center Drive'], [u'Crowne Plaza Hotel Northwest-Brookhollow', u'21486', u'12801 Northwest Freeway'], [u'Crossland Houston - West Oaks', u'11359', u'2130 Hwy 6 South'], [u'Holiday Inn Express Hotel &amp; Suites Houston - Memorial Park Area', u'174843', u'7625 Katy Freeway'], [u'Crestwood Suites of Houston 290 Galleria', u'37097', u'12925 Northwest Freeway'], [u'Econo Lodge', u'32911', u'6630 Hoover Street U.S. 290 &amp; Bingle Road'], [u'Holiday Inn Express Houston-Hobby Airport', u'66159', u'8730 Gulf Freeway'], [u'Holiday Inn Express Hotel &amp; Suites Houston-Nw(Hwy 290 &amp; Fm 1960)', u'1877', u'12915 FM 1960 West'], [u'La Quinta Inn &amp; Suites Pasadena', u'163238', u'3490 E Sam Houston Parkway South, Pasadena'], [u'Sun Suites at Intercontinental (Greenspoint)', u'155678', u'12010 Kuykendahl Road'], [u'Comfort Suites', u'6100', u'11440 Clay Road'], [u'Courtyard Houston Pearland', u'192253', u'11200 Broadway, Pearland'], [u'Holiday Inn Express Hotel &amp; Suites Houston-Kingwood', u'5466', u'22675 Highway 59 North'], [u'La Quinta Inn &amp; Suites Houston - Normandy', u'258035', u'930 Normandy Street'], [u'CareFree Inn at Medical Center', u'94018', u'10015 South Main Street'], [u'Days Inn And Suites Houston', u'1258', u'10137 North Freeway'], [u'Staybridge Suites Houston Galleria Area', u'38948', u'5190 Hidalgo'], [u'Comfort Suites North', u'15492', u'150 Overland Trail'], [u'Staybridge Suites Houston Willowbrook', u'156393', u'10750 North Gessner Road'], [u'Comfort Suites Bush Intercontinental Airport', u'66168', u'15555 John F. Kennedy Blvd.'], [u'Residence Inn Houston-West University', u'41508', u'2939 Westpark Drive'], [u'Candlewood Suites Houston-Town And Country', u'32040', u'10503 Town &amp; Country Way'], [u'Howard Johnson Houston NASA-Clearlake', u'40399', u'15313 Gulf Freeway'], [u'BEST WESTERN Downtown Inn &amp; Suites', u'23667', u'915 W Dallas Street'], [u'Hampton Inn Houston-Brookhollow', u'18107', u'12909 Northwest Freeway'], [u'Rodeway Inn &amp; Suites Hwy 290 NW', u'35817', u'4760 Sherwood Lane'], [u'SpringHill Suites Houston Medical Center/Reliant Park', u'32029', u'1400 Old Spanish Trail'], [u'Sleep Inn &amp; Suites', u'270745', u'2475 North Freeway'], [u'Studio Plus Houston - Westchase', u'3138', u'2424 W.Sam Houston Pkwy'], [u'Comfort Suites', u'10915', u'17550 Northwest Freeway'], [u'Comfort Inn Greenspoint', u'33657', u'12701 North Freeway'], [u'Hilton University of Houston', u'66207', u'4800 Calhoun Road'], [u'Hampton Inn &amp; Suites Houston-Westchase', u'66194', u'6440 West Sam Houston Parkway South'], [u'ESA Houston-Willowbrook', u'66191', u'16939 Tomball Pkwy'], [u'Candlewood Suites Houston-Westchase', u'35783', u'4033 West Sam Houston Parkway'], [u'BEST WESTERN Fountainview Inn &amp; Suites Near Galleria', u'26577', u'6229 Richmond Avenue'], [u'Super 8 Houston I-10Wand Hwy 6', u'24767', u'15101 Katy Freeway'], [u'Econo Lodge Medical Center', u'12881', u'7905 S Main'], [u'Comfort Suites Hwy 249 at Louetta', u'15680', u'21222 Tomball Pkwy. Highway 249'], [u'Candlewood Suites Houston Medical Center', u'199056', u'10025 Main Street'], [u'Holiday Inn Express Hotel &amp; Suites Houston Medical Center', u'42168', u'8080 Main Street'], [u'TownePlace Suites Houston Northwest', u'155679', u'11040 Louetta Road'], [u'BEST WESTERN Westchase Mini-Suites', u'29778', u'2950 W Sam Houston Pkwy S'], [u'Candlewood Suites Houston Iah / Beltway 8', u'270658', u'1500 North Sam Houston Parkway'], [u'Super 8 Houston/I-10/Federal Road', u'99757', u'1217 Federal Rd'], [u'BEST WESTERN Northwest Inn &amp; Suites', u'35508', u'11611 Northwest Freeway'], [u'Hotel Granduca', u'151262', u'1080 Uptown Park Boulevard'], [u'Courtyard Houston Medical Center', u'331066', u'Houston Medical Center, 7702 Main Street'], [u'BEST WESTERN Sam Houston Inn &amp; Suites', u'102256', u'8049 N Sam Houston Pkwy W'], [u'Courtyard Houston-West University', u'41380', u'2929 Westpark Dr'], [u'Comfort Suites Hobby Airport', u'189889', u'9120 Airport Boulevard'], [u'Fairfield Inn Houston Westchase', u'2026', u'2400 West Sam Houston Parkway South'], [u'Hilton Houston Plaza/Medical Center', u'21195', u'6633 Travis Street'], [u'Super 8 Pasadena', u'66312', u'5400 Vista Rd, Pasadena'], [u'Houston Marriott Energy Corridor', u'315045', u'16011 Katy Freeway'], [u'Comfort Suites Westchase', u'39639', u'2830 Wilcrest Dr. &amp; Westheimer'], [u'Comfort Suites', u'26623', u'1055 McNee Road East of Main Street'], [u'La Quinta Inn &amp; Suites Houston 1960', u'168513', u'415 FM 1960'], [u'Crowne Plaza Hotel Houston I-10 West', u'66199', u'14703 Park Row'], [u'Days Inn and Suites - Sugarland/Houston/Stafford', u'31980', u'4630 Techniplex Drive, Stafford'], [u'La Quinta Inn &amp; Suites Houston Channelview', u'310133', u'5520 East Sam Houston Parkway N'], [u'Courtyard Houston Northwest', u'155672', u'11050 Louetta Road'], [u'Hilton Houston NASA Clear Lake', u'34358', u'3000 Nasa Road One'], [u'Americas Best Value Inn Reliant Park / Texas Medical Center', u'16676', u'9604 South Main Street'], [u'Americas Best Value Inn &amp; Suites', u'5545', u'702 North Sam Houston Parkway East'], [u'Howard Johnson Houston', u'335306', u'2221 Greens Road'], [u'Days Inn Houston Channelview TX', u'105134', u'15765 I-10 East, Channelview'], [u'Homewood Suites by Hilton Houston-Westchase', u'12830', u'2424 Rogerdale Road'], [u'La Quinta Inn &amp; Suites Houston Energy Corridor', u'349762', u'2451 Shadow View Lane'], [u'Knights Inn Houston North/IAH', u'21651', u'12500 North Freeway'], [u'ESA Houston-Stafford', u'38067', u'4726 Sugar Grove Boulevard'], [u'Hampton Inn Houston-Willowbrook Mall', u'7489', u'7645 West FM 1960'], [u'SpringHill Suites Houston Intercontinental Airport', u'323582', u'15840 John F Kennedy Boulevard'], [u'Hilton Garden Inn Houston/The Woodlands', u'66208', u'9301 Six Pines Drive'], [u'Residence Inn Houston Northwest/Willowbrook', u'66192', u'7311 W. Greens Road'], [u'Interstate Motor Lodge Houston', u'91707', u'13213 East Freeway'], [u'Hampton Inn &amp; Suites Houston-Cypress Station', u'66201', u'150 Wagon Point Drive'], [u'Homewood Suites by Hilton Houston West-Energy Corridor', u'172798', u'14450 Park Row'], [u'Days Inn &amp; Suites Houston', u'21524', u'410 FM 1960 East'], [u'Scottish Inn and Suites - Houston', u'194204', u'11130 Telephone Rd.'], [u'Super 8 Houston Hobby Airport South', u'43769', u'10130 Almeda Genoa Road'], [u'Budget Host Hempstead Inn', u'38079', u'12708 Hempstead Hwy'], [u'Holiday Inn Express Hotel &amp; Suites Houston West-InterContinental', u'66170', u'1330 North Sam Houston Parkway East'], [u'Candlewood Suites Houston-Clear Lake', u'34274', u'2737 Bay Area Blvd'], [u'Days Inn Houston', u'185496', u'10801 East Freeway Bldg C'], [u'Residence Inn Houston Clear Lake', u'9729', u'525 Bay Area Boulevard'], [u'Homewood Suites by Hilton Houston-Willowbrook Mall', u'10114', u'7655 West FM 1960'], [u'Candlewood Suites Houston I-10 East', u'331013', u'1020 Maxey Road'], [u'Scott Inn &amp; Suites Houston', u'342438', u'1933 Scott Street'], [u'Staybridge Suites Houston West/Energy Corridor', u'128950', u'1225 Eldridge Enclave Pkwy'], [u'Baymont Inn and Suites Houston- Sam Houston Parkway', u'20501', u'502 N Sam Houston Parkway East'], [u'Super 8 Houston TX', u'2379', u'18836 Highway 249'], [u'Econo Lodge  Inn &amp; Suites North', u'5619', u'7447 I-45 N. Freeway'], [u'Holiday Inn Express Houston N-1960 Champions Area', u'26471', u'4434 FM 1960 West'], [u'Holiday Inn Houston West - Energy Corridor', u'311650', u'1112 Eldridge Parkway'], [u'Residence Inn Houston Westchase on Westheimer', u'44329', u'9965 Westheimer @ Elmside'], [u'Holiday Inn Houston-Sw-Hwy 59s@Beltwy 8', u'16740', u'11160 Southwest Freeway'], [u'ESD Houston Katy Fwy', u'34170', u'15385 Katy Freeway'], [u'Quality Inn &amp; Suites', u'21447', u'9041 Westheimer Road'], [u'Residence Inn Houston Intercontinental Airport at Greenspoint', u'66186', u'655 North Sam Houston Parkway East'], [u'TownePlace Suites Houston Intercontinental Airport', u'284107', u'4015 Interwood North Parkway'], [u'TownePlace Suites Houston Central/Northwest Freeway', u'66176', u'12820 Northwest Freeway'], [u'Comfort Inn East', u'66158', u'1016 Maxey Road'], [u'TownePlace Suites Houston I-10 West/Energy Corridor', u'39595', u'15155 Katy Freeway'], [u'Rodeway Inn &amp; Suites Medical Center', u'66166', u'6712 Morningside Drive'], [u'Homewood Suites by Hilton Houston-Clear Lake', u'66182', u'401 Bay Area Blvd.'], [u'Econo Lodge at NASA', u'21446', u'904 East Nasa Parkway'], [u'Holiday Inn Express Hotel &amp; Suites Houston-Nw (Brookhollow)', u'99650', u'12439 Northwest Freeway'], [u'Residence Inn Houston West/Energy Corridor', u'129343', u'1150 Eldridge Parkway'], [u'Knights Inn Houston', u'151277', u'9638 Plainfield Street'], [u'Comfort Inn &amp; Suites FM1960-Champions', u'10566', u'3555 FM 1960 West'], [u'Esa Houston Nasa/johnson Space Center', u'4931', u'1410 Nasa Road 1'], [u'Knights Inn Houston Hobby Airport', u'5563', u'1505 College Avenue'], [u'Holiday Inn Express Hotel &amp; Suites Houston (Bw 8 North)', u'335326', u'9120 West Road'], [u'Red Roof Inn Houston - Westchase', u'19164', u'2960 West Sam Houston Pkwy South'], [u'TownePlace Suites Houston Clear Lake', u'6813', u'1050 Bay Area Boulevard'], [u'Holiday Inn Express Hotel &amp; Suites Houston East', u'103958', u'11460 East Freeway I-10'], [u'Studio Plus Houston - Greenspoint', u'5793', u'13505 North Frwy'], [u'Holiday Inn Express Hotel &amp; Suites Houston Energy Corridor-W Oaks', u'199104', u'2205 Barker Oaks at Hwy 6'], [u'Microtel Inn &amp; Suites', u'66184', u'1620 Nasa Rd One'], [u'Quality Inn &amp; Suites Reliant Park/Medical Center', u'4632', u'2364 South Loop West'], [u'Quality Inn &amp; Suites', u'95182', u'715 Highway 6 South'], [u'Crossland Houston - Northwest', u'9099', u'5959 Guhn Rd'], [u'Holiday Inn Houston Northwest Willowbrook', u'95760', u'18818 Tomball Parkway'], [u'Comfort Suites - Near the Galleria', u'14222', u'6221 Richmond Ave.'], [u'Super 8 Houston Hobby Arpt I45', u'39993', u'From N Exit 36  From S Exit 38'], [u'Super 8 Houston', u'66183', u'18103 Kings Row'], [u'Quality Inn &amp; Suites', u'40802', u'10155 North Freeway'], [u'Quality Inn &amp; Suites West Chase', u'347347', u'2930 West Sam Houston Pkwy. So'], [u'Motel 6 Houston Hobby', u'9597', u'9005 Airport Boulevard'], [u'Red Roof Inn Houston I-10 West', u'66200', u'15701 Park Ten Pl'], [u'Sleep Inn &amp; Suites Hwy 290/NW Freeway', u'311375', u'5451 Northwest Central Drive'], [u'Studio 6 Houston Northwest', u'10928', u'14255 Northwest Frwy'], [u'Comfort Suites', u'348204', u'1350 N Sam Houston Pkwy East'], [u'Studio 6 Houston - Hobby', u'96233', u'12700 Featherwood'], [u'Candlewood Suites Houston NW - Willowbrook', u'311165', u'8719 Fm 1960 West'], [u'Fairfield Inn &amp; Suites Houston I-10 West/Energy Corridor', u'96150', u'15111 Katy Freeway'], [u'Studio 6 Houston West', u'96236', u'1255 North Highway 6'], [u'Studio 6 Houston - Spring', u'96232', u'220 Bammel Westfield Road'], [u'Fairfield Inn &amp; Suites Houston Intercontinental Airport', u'335316', u'4025 Interwood North Parkway'], [u'Fairfield Inn &amp; Suites Houston I-45 North', u'36016', u'17617 North Freeway'], [u'Country Inn &amp; Suites By Carlson Houston-Intercontinental Airport East, TX', u'17725', u'20611 Highway 59 N, Humble'], [u'La Quinta Inn &amp; Suites Deer Park', u'199638', u'1400 East Boulevard, Deer Park'], [u'La Quinta Inn &amp; Suites Houston Stafford Sugarland', u'13502', u'12727 Southwest Freeway, Stafford'], [u'La Quinta Inn &amp; Suites Houston Bush Intl Airport E', u'315570', u'18201 Kenswick Drive, Humble'], [u'Comfort Suites West Energy Corridor', u'317086', u'7111 Rancho Mission Drive'], [u'La Quinta Inn Houston Baytown West', u'35856', u'4911 Interstate 10 East, Baytown'], [u'La Quinta Inn &amp; Suites Webster - Clearlake', u'129297', u'520 West Bay Area Boulevard, Webster'], [u'La Quinta Inn &amp; Suites Houston NASA Seabrook', u'43502', u'3636 Nasa Road 1, Seabrook'], [u'Drury Inn &amp; Suites Sugar Land Sugar Land', u'14589', u'13770 Southwest Freeway, Sugar Land'], [u'Holiday Inn Express Hotel &amp; Suites Pasadena', u'6729', u'2601 Spencer Highway, Pasadena'], [u'SpringHill Suites Houston Pearland', u'171366', u'1820 Country Place Parkway, Pearland'], [u'Hampton Inn Houston-Pearland', u'26190', u'6515 Broadway Street, Pearland'], [u'Winchester Inn &amp; Suites IAH', u'273483', u'15625 Highway 59 N, Humble'], [u'La Quinta Inn &amp; Suites Houston Baytown East', u'34980', u'5215 I-10 East, Baytown'], [u'BEST WESTERN Sugarland Inn', u'188715', u'6330 E Riverpark Drive, Sugar Land'], [u'Americas Best Value Inn', u'66044', u'15919 I-10 East, Channelview'], [u'Econo Lodge', u'66313', u'823 West Pasadena Freeway, Pasadena'], [u'Holiday Inn Express Hotel &amp; Suites Pearland', u'44797', u'1702 N Main Street, Pearland'], [u'Residence Inn Houston Sugar Land', u'45594', u'12703 Southwest Freeway, Stafford'], [u'BEST WESTERN PLUS Atascocita Inn &amp; Suites', u'127629', u'7730 FM 1960 RD E, Humble'], [u'Comfort Suites', u'5071', u'22223 Highway 59 North, Humble'], [u'SpringHill Suites Houston Clear Lake/Webster', u'308073', u'1101 Magnolia Avenue, Webster'], [u'Humble Executive Suites', u'197170', u'17110 Highway 59 N,, Humble'], [u'Holiday Inn Express Sugar Land', u'37701', u'14444 Southwest Freeway, Sugar Land'], [u'Courtyard Houston Sugar Land', u'66414', u'12655 Southwest Freeway, Stafford'], [u'Hilton Garden Inn Houston/Sugar Land', u'191847', u'722 Bonaventure Way, Sugar Land'], [u'Hampton Inn Houston Deer Park Ship Area', u'172902', u'1450 Center Street, Deer Park'], [u'Holiday Inn Houston-Webster', u'288966', u'302 W Bay Area Boulevard, Webster'], [u'BEST WESTERN Pearland Inn', u'29139', u'1855 N Main Street (Hwy 35), Pearland'], [u'Sleep Inn &amp; Suites', u'270744', u'1908 Country Place Parkway, Pearland'], [u'Hampton Inn &amp; Suites Houston/Clear Lake-Nasa Area', u'66210', u'506 West Bay Area Blvd., Webster'], [u'BEST WESTERN Deer Park Inn &amp; Suites', u'66092', u'1401 Center Street, Deer Park'], [u'SpringHill Suites Houston NASA/Seabrook', u'335360', u'2120 Nasa Parkway, Seabrook'], [u'Hilton Garden Inn Houston/Clear Lake NASA', u'311868', u'750 W.  Texas Avenue, Webster'], [u'Fairfield Inn &amp; Suites Houston Channelview', u'315192', u'15822 East Freeway, Channelview'], [u'Econo Lodge  Inn &amp; Suites Airport', u'5182', u'9821 West FM 1960 Bus. Rd., Humble'], [u'BEST WESTERN Intercontinental Airport Inn', u'37593', u'7114 Will Clayton Pkwy, Humble'], [u'Homewood Suites by Hilton Houston-Stafford', u'162357', u'4520 Techniplex Drive, Stafford'], [u'Rodeway Inn &amp; Suites', u'128067', u'9717 West FM 1960 Bus. Road, Humble'], [u'Regency Inn &amp; Suites Galena Park', u'184893', u'2503 Clinton Drive, Galena Park'], [u'Holiday Inn Kemah (Near Boardwalk)', u'348205', u'805 Harris Avenue, Kemah'], [u'Hampton Inn &amp; Suites Houston/League City', u'341102', u'2320 South Gulf Freeway, League City'], [u'Staybridge Suites Houston-Nasa/Clear Lake', u'196900', u'501 Texas Avenue, Webster'], [u'Quality Inn &amp; Suites', u'38855', u'11206 West Airport Boulevard, Stafford'], [u'Comfort Suites', u'66413', u'4820 Techniplex Dr., Stafford'], [u'Baymont Inn and Suites Houston Intercontinental Airport', u'191887', u'18032 McKay Drive, Humble'], [u'Ramada Houston IAH Airport West', u'286747', u'6115 Will Clayton Parkway, Humble'], [u'Sugar Land Marriott Town Square', u'66417', u'16090 City Walk, Sugar Land'], [u'Comfort Suites', u'40067', u'1501 Center St., Deer Park'], [u'Sleep Inn &amp; Suites', u'128496', u'4810 Alpine Drive, Stafford'], [u'Sun Suites of Sugarland (Stafford)', u'25913', u'11620 Lebon Lane, Stafford'], [u'Extended Stay Deluxe Houston Sugarland', u'155734', u'13420 Southwest Freeway, Sugar Land'], [u'Super 8 Stafford Sugarland Area', u'102520', u'12845 Murphy Road, Stafford'], [u'Passport Inn &amp; Suites Kemah', u'95873', u'601 Texas Aveue, Kemah'], [u'Comfort Suites', u'160654', u'16931 North Texas Avenue, Webster'], [u'Holiday Inn Express Hotel &amp; Suites Deer Park', u'190926', u'201 West X Street, Deer Park'], [u'BEST WESTERN NASA', u'30049', u'889 W Bay Area Boulevard, Webster'], [u'Candlewood Suites Deer Park Tx', u'330934', u'1300 East Blvd, Deer Park'], [u'Quality Inn', u'14806', u'300 S. Hwy 146 Business, Baytown'], [u'Hampton Inn Humble', u'3837', u'20515 Highway 59 North, Humble'], [u'Super 8 Humble/Fm 1960/Hwy 59', u'44790', u'20118 Eastway Village Drive, Humble'], [u'Super 8 Intercontinental Houston TX', u'129353', u'7010 Will Clayton Parkway, Humble'], [u'Quality Inn &amp; Suites Yacht Club Basin', u'109100', u'2720 Nasa Parkway, Seabrook'], [u'Super 8 Deer Park', u'161291', u'846 Center Street, Deer Park'], [u'Fairfield Inn Humble', u'37994', u'20525 Highway 59, Humble'], [u'Candlewood Suites Pearland', u'308810', u'9015 Broadway, Pearland'], [u'Sleep Inn &amp; Suites Intercontinental Airport East', u'343637', u'18150 McKay Drive, Humble'], [u'Comfort Inn &amp; Suites', u'135140', u'2901 Nasa Parkway, Seabrook'], [u'Hampton Inn Houston/Stafford', u'9040', u'4714 Techniplex Dr., Stafford'], [u'Comfort Suites', u'270730', u'5755 Bayport Blvd, Seabrook'], [u'Sleep Inn', u'66019', u'5222 I-10 East, Baytown'], [u'Holiday Inn Express Hotel &amp; Suites Houston InterContinental East', u'25447', u'7014 Will Clayton Parkway, Humble'], [u'Comfort Suites', u'302406', u'323 East Louetta Road, Spring'], [u'Holiday Inn Express Hotel &amp; Suites Houston Space Ctr - Clear Lake', u'311636', u'900 Rogers Court, Webster'], [u'ESA Houston-The Woodlands', u'273173', u'150 Valley Wood Rd, Spring'], [u'Oxford Inn &amp; Suites Webster', u'176029', u'915 West Nasa Rd # 1, Webster'], [u'Super 8 League City', u'24049', u'102 Hobbs Rd, League City'], [u'Knights Inn Houston/Channelview', u'66047', u'16939 I-10 East, Channelview'], [u'Holiday Inn Express Hotel &amp; Suites The Woodlands', u'38910', u'24888 I-45 North, Spring'], [u'Hampton Inn Houston NASA-Johnson Space Center', u'343705', u'3000 Nasa Road One, Seabrook'], [u'Days Inn and Suites Webster NASA-Clear Lake-Houston', u'11579', u'201 N Texas Ave, Webster'], [u'Suburban Extended Stay', u'171368', u'7212 East Point Blvd, Baytown'], [u'Candlewood Suites League City', u'311627', u'2350 Gulf Freeway South, League City'], [u'Candlewood Suites Baytown', u'288938', u'6126 Garth Road, Baytown'], [u'Days Inn and Suites Baytown', u'300227', u'3810 Decker Drive, Baytown'], [u'Comfort Suites', u'104251', u'7209 Garth Rd, Baytown'], [u'BEST WESTERN Baytown Inn', u'30343', u'5021 I-10 East, Baytown'], [u'Super 8 Baytown/Mont Belvieu', u'126785', u'9032 Highway 146 North, Baytown'], [u'Days Inn Kemah TX', u'104261', u'1411 Highway 146, Kemah'], [u'Palace Inn Baytown', u'330819', u'5244 I-10 East, Baytown'], [u'Hampton Inn Houston/Baytown', u'14770', u'7211 Garth Rd., Baytown'], [u'Super 8 Spring TX', u'2380', u'24903 I-45 North, Spring'], [u'Studio 6 Houston - Sugarland', u'96234', u'12827 Southwest Freeway, Stafford'], [u'South Shore Harbour Resort', u'66251', u'2500 S. Shore Blvd., League City'], [u'Palace Inn &amp; Suites - Willowbrook', u'351614', u'14350 Tomball Parkway Highway 249'], [u'Northgate Inn &amp; Suites Houston', u'70262', u'15725 Bammel Village Dr.'], [u'Budget Host Inn and Suites IAH Airport', u'315541', u'17258 Highway 59 North, Humble'], [u'Garden Suites', u'273189', u'14110 Tomball Pky'], [u'Venetian Inn &amp; Suites Houston', u'341680', u'6 North San Houston Parkway East'], [u'Candlewood Suites HOUSTON (THE WOODLANDS)', u'338621', u'17525 St. Lukes Way'], [u'Executive Inn &amp; Suites Houston', u'99077', u'6711 Telephone Rd'], [u'Rodeway Inn &amp; Suites', u'171277', u'2531 FM 1960 Road East'], [u'Hometowne Suites', u'332593', u'6802 Garth Rd, Baytown'], [u'Motel 6 Houston - Westchase', u'129325', u'2900 West Sam Houston Parkway South Beltw...'], [u'Motel 6 Houston - NASA', u'129323', u'1001 West Nasa Road 1, Webster'], [u'Knights Inn Houston - Bush Intercontinental Airport', u'109147', u'15319 Eastex Freeway, Humble'], [u'Super 8 Kemah', u'338581', u'1413 Hwy 146, Kemah'], [u'Motel 6 Houston Reliant Park', u'129328', u'3223 South Loop West I-610 at Buffalo Spe...'], [u'Motel 6 Humble TX', u'191290', u'20145 Eastway Village Dr, Humble'], [u'Motel 6 Houston Northwest', u'129327', u'5555 West 34th Street US 290 at 34th Street'], [u'Motel 6 Houston - Jersey Village', u'129322', u'16884 Northwest Freeway US 290 at Senate ...'], [u'Motel 6 Houston West - Katy', u'129329', u'14833 Katy Freeway I-10 at SR 6, Exit #751'], [u'Motel 6 Pasadena TX', u'311995', u'3010 Pasadena Frwy, Pasadena'], [u'Motel 6 Houston North - Spring', u'109121', u'19606 Cypresswood Court, Spring'], [u'Motel 6 Houston East - Baytown', u'109323', u'8911 State Route 146, Baytown'], [u'Quality Inn Hobby Airport', u'351786', u'7775 Airport Blvd'], [u'Staybridge Suites HOUSTON STAFFORD - SUGAR LAND', u'367174', u'11101 Fountain Lake Drive, Stafford'], [u'Econo Lodge  Inn &amp; Suites', u'350808', u'7420 Garth Road, Baytown'], [u'Best Way Inn Houston', u'312296', u'3100 Holmes Road'], [u'Clarion Inn', u'371725', u'15157 IH 10 East, Channelview'], [u'SpringHill Suites Houston Baytown', u'371636', u'5169 I-10 East, Baytown']])