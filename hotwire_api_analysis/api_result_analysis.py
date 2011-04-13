import sys
import os
import MySQLdb
import time, datetime

class Connection():
	database = MySQLdb.connect(user='root', passwd='areek', db='acuity')
	cursor = database.cursor()

class res2ult_analyser():
    indexed_records = {}
    log_file = open('res2/log.csv','w')
    def dic_print(self,current):
        myform='res2/%Y-%m-%d_%H-%M.csv'
        log=self.log_file
        for one in current.items():
            # @type one dict
            log.write( one[0]+'\n')
            #x=''
            #y=''

            c=0
            for inner in sorted(one[1].items(), key=lambda ent: ent[0]):
                #c+=1
                #x+=str(c)+','#str(inner[0])+','
                #y+=str(inner[1]).strip()+','
                if c:
                    if prev != inner[1][2]:
                        diff = inner[0]-prev_d
                        if inner[1][0] == prev_cont[0] and inner[1][6] == prev_cont[6] and inner[1][7] == prev_cont[7]:
                            #time diff, old_price, new_price, old_date, new_date
                            log.write(str(diff).replace(',',' ')+','+str(prev)+' , '+str(inner[1][2])+' , '+str(prev_d)+' , '+str(inner[0])+'\n')
                        #c=0
                        else:
                            temp_ar_new = inner[1][6:]
                            temp_ar_new.append(inner[1][0])
                            temp_ar_old = prev_cont[6:]
                            temp_ar_old.append(prev_cont[0])

                            log.write(str(diff).replace(',',' ')+' , '+str(prev)+' , '+str(inner[1][2])+' , '+str(prev_d)+' , '+str(inner[0])+',')
                            if temp_ar_new[0] != temp_ar_old[0]:
                                log.write( 'Recommandation changed:'+str(temp_ar_new[0]).strip()+'||'+str(temp_ar_old[0]).strip()+',')
                            else:
                                log.write(',')
                            if temp_ar_new[1] != temp_ar_old[1]:
                                log.write( 'Tripadvisor rating changed:'+str(temp_ar_new[1]).strip()+'||'+str(temp_ar_old[1]).strip()+',')
                            else:
                                log.write(',')
                                #print str(temp_ar_new[1]).strip()+', '+str(temp_ar_old[1]).strip()
                            if temp_ar_new[2].strip() != temp_ar_old[2].strip():
                                dif_tmp=[str(x) for x in temp_ar_new[2].split('|') if x not in temp_ar_old[2].split('|')]
                                if not dif_tmp:
                                    dif_tmp=[str(x) for x in temp_ar_old[2].split('|') if x not in temp_ar_new[2].split('|')]
                                log.write(str(dif_tmp).replace(',','|').replace('[','').replace(']','')+',')
                            else:
                                log.write(',')
                                #print temp_ar_new[2] +', '+temp_ar_old[2]
                            #print temp_ar_old
                            #print temp_ar_new
                            log.write('\n')


                        prev_cont = inner[1]
                        prev=inner[1][2]
                        prev_d = inner[0]
                else:
                    c=1
                    prev_cont = inner[1]
                    prev=inner[1][2]
                    prev_d = inner[0]
               # print ' '+str(inner[0])
               # print '  '+str(inner[1])
                

            #x=x[:-1]
            #y=y[:-1]
           # content = 'http://chart.apis.google.com/chart?chtt='+one[0]+'&chs=600x500'+'&chd=t:'+x+'|'+y+'&cht=lxy&chxt=x,y&chxl=0:|'+x.replace(",","|")+'|1:|0|'+str(sorted(one[1].items(), key=lambda ent: ent[1])[-1][1]).strip()
           # print content
            log.write('\n')
        log.close()

    def find_files(self):
        for one in os.listdir('res2/'):
            if '.csv' in one:
                self.index_hotwire_hotels('res2/'+one)
        self.dic_print(self.indexed_records)


    def index_hotwire_hotels(self,filename):
        f = open(filename,'r')
        f.readline()
        # @type f file
        myform='res2/%Y-%m-%d_%H-%M.csv'
        for line in f.readlines():
            parts = line.split(',')
            unique_key = parts[2]+','+parts[4]
            if not self.indexed_records.has_key(unique_key):
                self.indexed_records[unique_key] = {}
            self.indexed_records[unique_key][datetime.datetime.fromtimestamp(time.mktime(time.strptime(filename,myform)))]=parts[3:]
            #unique parts 2,4,5,9,10
        f.close()


def main():
    res2ult = res2ult_analyser()
    res2ult.find_files()


if __name__ == '__main__':
        main()