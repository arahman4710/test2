from hotelnames_spider import *
import os


def main():
    old_file = "c:/users/areek/desktop/fechopia/concept/"+file.yesterday+".csv"
    new_file = "C:/Users/Areek/Desktop/fechopia/concept/"+file.today+".csv"
    log_file = file.yesterday+"-"+file.today+".txt"
    if os.path.isfile(old_file):
        old_file_content = [line.strip() for line in open(old_file).readlines()]
        new_file_content = [line.strip() for line in open(new_file).readlines()]
        new_list = {}
        old_list = {}

        for line in old_file_content:
            temp_list = line.split(",")
            old_list[temp_list[3]+","+temp_list[2]+","+temp_list[0]+","+temp_list[1].strip()]=float(temp_list[-1][0:-1])
        for line in new_file_content:
            temp_list = line.split(",")
            new_list[temp_list[3]+","+temp_list[2]+","+temp_list[0]+","+temp_list[1].strip()]=float(temp_list[-1][0:-1])

        log = open(log_file,'w')

        for new_hotel in new_list.iterkeys():
            if new_hotel in old_list.keys():
                if new_list[new_hotel]!=old_list[new_hotel]:
                    log.write ("Hotel Name: "+str(new_hotel)+" winning probability changed from "+str(old_list[new_hotel])+ " to " + str(new_list[new_hotel]) + "\n")
            else:
                log.write ("Newly Added hotel Name: "+str(new_hotel)+\
                    "with a winning probability of "+str(new_list[new_hotel])+ "\n")

        for old_hotel in old_list.iterkeys():
            if old_hotel not in new_list.keys():
                log.write ("Not Found: Hotels " + str(old_hotel+"\n"))
        log.close()

"""

        if old_file_content==new_file_content:
            print "file not changed"
        else:
            for new_line in new_file_content:
                found =0
                temp_new = new_line.split(',')
                for old_line in old_file_content:
                    temp_old = old_line.split(',')
                    if len(temp_new)==len(temp_old):
                        if temp_old != temp_new:
                            if temp_old[:-1]==temp_new[:-1]:
                                old_win_p = float(temp_old[-1][0:-1])
                                new_win_p = float(temp_new[-1][0:-1])
                                if old_win_p != new_win_p:
                                    found = 1
                                    print "For hotel"+ str(temp_new[-2])+"in region "+str(temp_new[-3])+" winning probability changed from "+temp_old[-1]+" to "+temp_new[-1]
                        else:
                            found = 1
                            break
                if found==0:
                    print "new hotel added "+ str(temp_new[-2]+ " in "+ str(temp_new[-3]))

    else:
        print "file not found"

"""
if __name__ == "__main__":
    main()

