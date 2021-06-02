# Python-Ping
Implementation of ping in Python 3.x using raw sockets.

Note that ICMP messages can only be sent from processes running as root (in Windows, you must run this script as 'Administrator').

Based on Python's pyping library

## Usage

### Use as a cli tool:

Python-Ping: sudo python ping.py google.com  

> PYTHON-PING google.com (172.217.163.110): 55 data bytes  
55 bytes from 172.217.163.110: icmp_seq=0 ttl=55 time=74.471 ms  
55 bytes from 172.217.163.110: icmp_seq=1 ttl=55 time=72.693 ms  
55 bytes from 172.217.163.110: icmp_seq=2 ttl=55 time=70.583 ms  
55 bytes from 172.217.163.110: icmp_seq=3 ttl=55 time=70.019 ms  
--- google.com ping statistics ---  
4 packets transmitted, 4 packets received, 0.0% packet loss  
round-trip min/avg/max = 70.019/71.941/74.471 ms  

Python-Ping: sudo python ping.py 127.0.0.1 -c 3  

> PYTHON-PING 127.0.0.1 (127.0.0.1): 55 data bytes    
55 bytes from 127.0.0.1: icmp_seq=0 ttl=64 time=0.088 ms    
55 bytes from 127.0.0.1: icmp_seq=1 ttl=64 time=0.161 ms    
55 bytes from 127.0.0.1: icmp_seq=2 ttl=64 time=0.159 ms    
--- 127.0.0.1 ping statistics ---  
3 packets transmitted, 3 packets received, 0.0% packet loss    
round-trip min/avg/max = 0.088/0.136/0.161 ms  
 
  
#### For positional/optional arguments:
Python-Ping: sudo python ping.py --help  


### Use as a Python library

Copy the repository and then import the file  

import sys  
sys.path.insert(0, './Python-Ping')  
from ping import ping  
ping("google.com") 

> PYTHON-PING google.com (172.217.163.78): 55 data bytes  
55 bytes from 172.217.163.78: icmp_seq=0 ttl=55 time=117.290 ms    
55 bytes from 172.217.163.78: icmp_seq=1 ttl=55 time=115.337 ms   
55 bytes from 172.217.163.78: icmp_seq=2 ttl=55 time=114.380 ms  
55 bytes from 172.217.163.78: icmp_seq=3 ttl=55 time=114.807 ms  
--- google.com ping statistics ---  
4 packets transmitted, 4 packets received, 0.0% packet loss  
round-trip min/avg/max = 114.380/115.453/117.290 ms  

#### Optional Arguments:  
ping("google.com", count=number of packets to be sent, packet_size=packet_size in bytes, timeout=timeout in ms)  
