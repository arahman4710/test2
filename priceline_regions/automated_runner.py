import os
import time
import win32pipe


def main():
    initial_time = os.path.getmtime("output/process.txt")

    ie_stat = win32pipe.popen('''tasklist /FI "IMAGENAME eq iexplore.exe"''').readlines()
    if not "PID Session Name" in str(ie_stat):
        win32pipe.popen("delete.exe")
        time.sleep(5)
        win32pipe.popen("ruby pl_new.rb")
    
    while True:
        
        time.sleep((60)*15)
        next_time = os.path.getmtime("output/process.txt")
        if(next_time == initial_time):
            win32pipe.popen("delete.exe")
            time.sleep(5)
            win32pipe.popen('taskkill /F /IM iexplore.exe')
            time.sleep(5)
            win32pipe.popen("ruby pl_new.rb")
        else:
            initial_time = next_time

        
        



if __name__ == "__main__":
    
    main()
