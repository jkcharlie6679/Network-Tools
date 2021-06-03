# Python-Ping
Implementation of ping in Python 3.9.

Note that ICMP messages can only be sent from processes running as root (in Windows, you must run this script as 'Administrator').

Based on Python's pyping library

## Usage

### Use as a cli tool:

For getting help: `sudo python3 -h`

```
usage: ping.py [-h] [-c [4]] [-t [1000]] [-p [64]] [-i [1]] [--show-time] destination_server

positional arguments:
  destination_server

optional arguments:
  -h, --help          show this help message and exit
  -c [4]              Count of packets
  -t [1000]           Timeout in ms
  -p [64]             Packet size in bytes
  -i [1]              Wait time in s
  --show-time         Show System time
```

Python-Ping: `sudo python3 ping.py google.com`

```
PYTHON-PING google.com (172.217.163.110): 55 data bytes  
55 bytes from 172.217.163.110: icmp_seq=0 ttl=55 time=74.471 ms  
55 bytes from 172.217.163.110: icmp_seq=1 ttl=55 time=72.693 ms  
55 bytes from 172.217.163.110: icmp_seq=2 ttl=55 time=70.583 ms  
55 bytes from 172.217.163.110: icmp_seq=3 ttl=55 time=70.019 ms  
--- google.com ping statistics ---  
4 packets transmitted, 4 packets received, 0.0% packet loss  
round-trip min/avg/max = 70.019/71.941/74.471 ms  
```

Python-Ping: `sudo python3  -c 3 ping.py 127.0.0.1`  

```
PYTHON-PING 127.0.0.1 (127.0.0.1): 55 data bytes    
55 bytes from 127.0.0.1: icmp_seq=0 ttl=64 time=0.088 ms    
55 bytes from 127.0.0.1: icmp_seq=1 ttl=64 time=0.161 ms    
55 bytes from 127.0.0.1: icmp_seq=2 ttl=64 time=0.159 ms    
--- 127.0.0.1 ping statistics ---  
3 packets transmitted, 3 packets received, 0.0% packet loss    
round-trip min/avg/max = 0.088/0.136/0.161 ms  
```
