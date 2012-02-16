import MySQLdb
import re
import time


# Input is in the format "(region;regionid;cityid;latitude;longitude$)(point$)*"
# Line are separated by $
# Cities are separated by #


# 1  Open the file and split into cities, initialize the mysql connection
#
input = open("output/process.txt", "r").read()
input = input[1:]
regions = re.split("#", input)
output_detection = open("output/detection.txt","a")
db_log = open("output/db_log.txt","a")
db = MySQLdb.connect(user='root', passwd='areek', db='acuity_backup')
c = db.cursor()

# 2  Iterate through the cities and lines
#    Skip the first city and last line because of formatting of input (they're empty)
#

#added
c.execute('Select * from regionscitiesmap')
existing_content = {}
table_content = c.fetchall()

if table_content:
        for existing in table_content:
            if int(existing[0]) not in existing_content.keys():
                existing_content[int(existing[0])] = [int(existing[1])]
            else:
                existing_content[int(existing[0])].append(int(existing[1]))
#edit ended
                
for region in regions:

        # 3  Initialize necessary variables and perform required splits
        #
        is_in_db=0
        region = region[:-1] # Remove an empty item at the end
        lines = re.split("\$", region)
        area = ''
        for index in range(len(lines)):
                lines[index] = re.split(";", lines[index])

        if len(lines[0]) == 6:
            [name, id, star_aval, cityid, lat, lng] = lines[0]
        else:
            [area, name, id, star_aval, cityid, lat, lng] = lines[0]
   

        if area:
           
            if area.find('located within the ')!=-1:
                area = area[area.find('located within the ')+19:area.find('region')].strip()
            
            c.execute('''Select Priceline_area_id from priceline_area WHERE Name ='%s' ''' % area)

            area_result = c.fetchall()

            if not area_result:

                c.execute("INSERT INTO `priceline_area` ( `Name` ) VALUES ( '"+area+"');")
                db.commit()
                c.execute('''Select Priceline_area_id from priceline_area WHERE Name = '%s' ''' % area)
                area_id = str(c.fetchall()[0][0])
                c.execute("INSERT INTO `priceline_area_city` ( `area_id`,`city_id` ) VALUES ( '"+area_id+"','"+cityid+"');")
                db.commit()

            else:
                area_result = str(area_result[0][0])
                c.execute("Select * from priceline_area_city where area_id = %s and city_id = %s" % (area_result,cityid))
                if not c.fetchall():
                    c.execute("INSERT INTO `priceline_area_city` ( `area_id`,`city_id` ) VALUES ( '"+area_result+"','"+cityid+"');")
                    db.commit()


        
        print [area, name, id, star_aval, cityid, lat, lng]


        
        lines = lines[1:] # Put the list of points into line (element 0 is info outlined above)
        c.execute('''Select * from pricelineregions WHERE pricelineid=%s ''' % id)
        result = c.fetchall()
        if not result:
            output_detection.write('Region name: '+str(name)+ ' Not Found!')
            is_in_db=0
        else:
            for one in result:

                #   region does not have star_availibility information
                #

                if not one[7] and star_aval:
                    c.execute("UPDATE `acuity_backup`.`pricelineregions` SET `Star_availibility` = '"+star_aval+"' WHERE `pricelineid` = '"+id+"' ;")
            is_in_db = 1

        if not is_in_db:
                # 4b Inserts the new region and gets its regionid for use with the points
                #
                c.execute('''INSERT INTO pricelineregions (regionname, pricelineid, cities_cityid, latitude, longitude, active, Star_availibility) VALUES
                ("%s",'%s','%s','%s','%s',%s)''' % (name, id, cityid, lat, lng, 1,star_aval))
                c.execute("SELECT pricelineregionid FROM pricelineregions ORDER BY pricelineregionid DESC LIMIT 1")
                regionid = c.fetchone()[0]
                
                # 6c Inserts the new points into the table if there aren't any others for that region
                #
                for i in range(len(lines)):
                        line = lines[i]
                        plat = line[2]
                        plng = line[3]
                        c.execute('''INSERT INTO pricelinepoints (pricelineregions_pricelineregionid, orderid, latitude, longitude) VALUES
                        ("%s","%s","%s","%s")'''% (regionid, i, plat, plng))
        #edited
                c.execute('''INSERT INTO `regionscitiesmap` (`cities_cityid`, `priceline_regionid`)VALUES('%s', '%s');''' %(cityid,id))
                db.commit()
        
        else:
                if int(cityid) in existing_content.keys():
                        if int(id) not in existing_content[int(cityid)]:
                                c.execute('''INSERT INTO `regionscitiesmap` (`cities_cityid`, `priceline_regionid`)VALUES('%s', '%s');''' %(cityid,id))
                                db.commit()
                else:
                        c.execute('''INSERT INTO `regionscitiesmap` (`cities_cityid`, `priceline_regionid`)VALUES('%s', '%s');''' %(cityid,id))
                        db.commit()
		