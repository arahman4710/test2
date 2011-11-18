import MySQLdb
import sys


def main():

        db = MySQLdb.connect(user='root', passwd='areek', db='acuity_backup')
	c = db.cursor()
	area = str(sys.argv[1]).strip()
        if area.find('located within the ')!=-1:
            area = area[area.find('located within the ')+19:area.find('region')].strip()
        cityid = str(sys.argv[2]).strip()
        c.execute('''Select Priceline_area_id from priceline_area WHERE Name ='%s' ''' % area)

        area_result = c.fetchall()

        if area_result:
            area_result =area_result[0][0]

            #area exists link the city to the area in the db and let ruby know that no more processing is needed
            c.execute("Select * from priceline_area_city where area_id = %s and city_id = %s" % (area_result,cityid))
            if not c.fetchall():
                c.execute("INSERT INTO `priceline_area_city` ( `area_id`,`city_id` ) VALUES ( '"+area_result+"','"+cityid+"');")
                db.commit()

            open("output/optimize.txt", "w").write('1')

        else:
            #let ruby know it needs to be processed
            open("output/optimize.txt", "w").write('0')




if __name__ == "__main__":
	main()