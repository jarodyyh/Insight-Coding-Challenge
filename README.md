# Insight Code Challenge for Data Engineering
#### Python version
  2.7.5

#### Python default lib used:
  datetime
  csv
  sys

#### Solution:

1. For Feature 1: List the top 10 most active host/IP addresses that have accessed the sites
   Solution:
   	use dict to store pair of IP/hosts and occurrence
        then sort the value (occurrence) to find out the top 10 most active IP/hosts

2. For Feature 2: Identify the 10 resources that consume the most bandwidth on the site
   Solution:
	add the used bandwidth in each access for same IP/host

3. For Feature 3: List the top 10 busiest (or most frequently visited) 60-minute periods
   Solution:
	maintain a list to contain accesses within 60min from 1st element in list;
        when changing start time of 60min,
             1. remove elements in list which are earlier than start time
             2.  add elements which are within 60min period from start time
        before each changes of start time, return:
             1. current start time
             2. length of the current list

4. For Feature 4: Detect patterns of three failed login attempts from the same IP address over 20 seconds so that all further attempts to the site can be blocked for 5 minutes. Log those possible security breaches.
   Solution:
	Use multiple values dict to store: {IP/host: [time, fail No.]}
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


#### Comments:

1. The python script `src.py` is in src folder. It is single file to implements all four features. 

2. To calculate the time difference, timestamp format is used.

