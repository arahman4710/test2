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
db = MySQLdb.connect(user='root', passwd='charles', db='acuity')
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
            if existing[0] not in existing_content.keys():
                existing_content[existing[0]] = [existing[1]]
            else:
                existing_content[existing[0]].append(existing[1])
#edit ended
                
for region in regions:

        # 3  Initialize necessary variables and perform required splits
        #
        region = region[:-1] # Remove an empty item at the end
        lines = re.split("\$", region)
        for index in range(len(lines)):
                lines[index] = re.split(";", lines[index])
                
        [name, id, cityid, lat, lng] = lines[0]
        lines = lines[1:] # Put the list of points into line (element 0 is info outlined above)

        if not c.execute('''SELECT * FROM pricelineregions WHERE pricelineid=%s ''' % id):
                # 4b Inserts the new region and gets its regionid for use with the points
                #
                c.execute('''INSERT INTO pricelineregions (regionname, pricelineid, cities_cityid, latitude, longitude, active) VALUES
                ("%s",'%s','%s','%s','%s',%s)''' % (name, id, cityid, lat, lng, 1))
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
                if cityid in existing_content.keys():
                        if id not in existing_content[cityid]:
                                c.execute('''INSERT INTO `regionscitiesmap` (`cities_cityid`, `priceline_regionid`)VALUES('%s', '%s');''' %(cityid,id))
                                db.commit()
                else:
                        c.execute('''INSERT INTO `regionscitiesmap` (`cities_cityid`, `priceline_regionid`)VALUES('%s', '%s');''' %(cityid,id))
                        db.commit()
