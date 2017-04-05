#!/usr/bin/python
#program to calculate the following features:
# 1. top 10 user
# 2. top 10 bandwidth
# 3. top 10 busiest 60 mins
# 4. block use for 5 mins, if they fail to login within 20 sec

import sys
import csv
import datetime


def get_key(dict):
    # to get the dict value for sort
    return dict[1]

def sorted_dict(dict):
    # to sort the dict based on value
    sorted_dict = sorted(dict.items(), key=get_key, reverse=True)
    return sorted_dict

def cleanInput(data):
    #clean the input data for feature 2 
    if len(data) > 8:
        for i in range(5,len(data)):
            if data[i].startswith("HTTP"):
                data[5] = " ".join(data[5:i+1])
        data[6] = data[-2]
        data[7] = data[-1]
    if data[7] == "-" or data[5] == "/":
        data[7] = 0
    return data[:8]

def readFile(filename):
    # read file into columes using csv package
    file = open(filename,'r')
    contents = csv.reader(file,delimiter=" ")
    data = [row for row in contents]
    return data


'''
 Feature 1: top 10 most active IP/hosts
 Solution: use dict to store pair of IP/hosts and occurrence
 	   then sort the value (occurrence) to find out the top 10 most active IP/hosts
'''

def top_user(data, outFile):
    # use dict to store the pair of user and occurrence
    dict_topuser={}

    # calculate the number of occurrence
    for i in range(len(data)):
        if data[i][0] in dict_topuser:
            dict_topuser[data[i][0]] += 1
        else:
            dict_topuser[data[i][0]] = 1

    # sort by value
    sortedDict = sorted_dict(dict_topuser)

    # write to output file
    out1 = open(outFile ,'w')
    for user in range(10):
        out1.write("%s,%s\n" % (sortedDict[user][0],sortedDict[user][1]))
    out1.close()


'''
Feature 2: top 10 resources consume the most bandwidth
Solution: add the used bandwidth in each access for same IP/host

'''

def top_bandwidth(data, outFile):
    # use dict to store the pair of item and bandwidth
    dict_bd={}

    # clean the data first, then store the pair of IP/host and total bandwidth
    for i in range(len(data)):
        clean_data = cleanInput(data[i])
	if clean_data[5] == "/":
	    clean_data[7] = 0
        if clean_data[5] in dict_bd:
            dict_bd[clean_data[5]] += int(clean_data[7])
        else:
            dict_bd[clean_data[5]] = int(clean_data[7])

    # sort by the value to find out the top 10 resources consuming most bandwidth
    sortedDict = sorted_dict(dict_bd)
	
    # write to output file
    out2 = open(outFile ,'w')
    for items in range(10):
        web = sortedDict[items][0].split()
        out2.write("%s\n" % (web[1]))
    out2.close()


'''
Feature 3: top 10 busiest 60 minutes
Solution: maintain a list to contain accesses within 60min from 1st element in list;
	  when changing start time of 60min,
	      remove elements in list which are earlier than start time
	      add elements which are within 60min period from start time
	  before each changes of start time, return:
	      current start time
	      length of the current list
'''

def check_start(list, starttime):
    # to compare the front of list with starttime, pop out them if less than starttime
    if len(list) != 0 and list[0] < starttime :
        list.pop(0)
        check_start(list,starttime)
    return list

def conv_time(data):
    # convert time to timestamp format
    data_time = datetime.datetime.strptime(data[3][1:], "%d/%b/%Y:%H:%M:%S")
    return data_time

def delta_sec(time1, time2):
    # calculate the difference between two timestamps
    deltas = (time1 - time2).total_seconds()
    return deltas


def top_60m(data, outFile):
    # firstly, convert time to timestamp format
    Stamp = []
    for time in range(len(data)):
        data_time = conv_time(data[time])
        Stamp.append(data_time)

    # prep
    starttime = Stamp[0]
    windowlist = []
    outdict = {}

    # main body
    for i in range(len(Stamp)):
        deltaInSec = delta_sec(Stamp[i],starttime)

        # for element within 60min, and not the last element in input
        if deltaInSec <= 3599 and i != len(Stamp)-1:
            windowlist.append(Stamp[i])

        # for element within 60min, and IS the last element in input
        elif deltaInSec <= 3599 and i == len(Stamp)-1:
            while len(windowlist) > 1:
                outdict[starttime]=len(windowlist)
                starttime += datetime.timedelta(seconds=1)
                check_start(windowlist, starttime)

        # for element outside 60min, return current results, move start time
        elif deltaInSec > 3599:
            outdict[starttime]=len(windowlist)
            starttime += datetime.timedelta(seconds=1)
            check_start(windowlist, starttime)

    # sort by value
    sortedDict = sorted_dict(outdict)

    # write to output file
    out3 = open(outFile ,'w')
    for items in range(10):
	out3.write("%s,%s\n" % (sortedDict[items][0],sortedDict[items][1]))
    out3.close()


'''
Feature 4: block user for 5 min, if they fail to login 3 times within 20 sec
Solution: use multiple values dict to store: {IP/host: [time, fail No.]}
	  Check several situations:
	    1. Fail:
		a. if in dict? check time and fail No. : add to dict 
		b. if larger than 20s? update time : b1/b2
			b1. if fail No. < 3? update fail No.
			b2. if fail No. == 3 and within 5min? block : update time and fail No. 
	    2. Success:
		a. if in dict? b : continue
		b1. if fail No. < 3? delete record
		b2. if fail No. == 3 and within 5min? block : delete record
'''

def blockUser(data, outFile):
    # convert time to timestamp format
    Stamp = []
    for i in range(len(data)):
        data[i][3] = conv_time(data[i])

    #prep
    dict_block={}
    starttime = data[0][3]

    # main body
    out4 = open(outFile,'w')
    for i in range(len(data)):
	# for login marked as success
        if data[i][6] == "200":

            if data[i][0] not in dict_block:
                continue

            elif data[i][0] in dict_block and dict_block[data[i][0]][1] < 3:
                del dict_block[data[i][0]]

            elif data[i][0] in dict_block and dict_block[data[i][0]][1] == 3:
	        deltaInSec = delta_sec(data[i][3], dict_block[data[i][0]][0])

		if deltaInSec <= 300:
                    data[i][3] = str(data[i][3])
                    out4.write("%s\n" % " ".join(data[i]))

		elif deltaInSec > 300:
                    del dict_block[data[i][0]]

	# for login marked as fail
        if data[i][6] == "401":

            if data[i][0] not in dict_block:
                dict_block[data[i][0]] = [data[i][3], 1]
	   
            elif data[i][0] in dict_block and dict_block[data[i][0]][1] < 3:
	        deltaInSec = delta_sec(data[i][3], dict_block[data[i][0]][0])

		if deltaInSec <= 20:
                    dict_block[data[i][0]][1] += 1
                else:
                    dict_block[data[i][0]][0] = data[i][3]
                    dict_block[data[i][0]][1] = 1


            elif data[i][0] in dict_block and dict_block[data[i][0]][1] == 3:
	        deltaInSec = delta_sec(data[i][3], dict_block[data[i][0]][0])

		if deltaInSec <= 300:
                    data[i][3] = str(data[i][3])
                    out4.write("%s\n" % " ".join(data[i]))
                else:
                    dict_block[data[i][0]][1] = 1
                    dict_block[data[i][0]][0] = data[i][3]

    out4.close()


def main():
    if len(sys.argv) != 6:
        print 'usage: python src.py log.txt hosts.txt resources.txt hours.txt blocks.txt'
        sys.exit(1)

    inputFile = sys.argv[1]
    hostsOut = sys.argv[2]
    resourceOut = sys.argv[3]
    hoursOut = sys.argv[4]
    blockOut = sys.argv[5]	

    data = readFile(inputFile)

    top_user(data, hostsOut)
    top_bandwidth(data,  resourceOut )
    top_60m(data,  hoursOut )
    blockUser(data,  blockOut )

if __name__ == '__main__':
        main()

