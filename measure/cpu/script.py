#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  scrpit1.py
#  
#  Copyright 2015 talal <talal@Alharbi>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  
import subprocess
from scapy.all import ARP, send, Ether, sendp
from time import *
import time 

def main():
	
	return 0

def str_to_bool (s):
	s = str(s).lower()
	try:
		r = 10
		if s.startswith("0x"):
			s = s[2:]
			r = 16
			i = int(s, r)
		if i != 0:
			return s
	except:
		pass
		return s

if __name__ == '__main__':
	main()

t_end = time.time()+240
while time.time() < t_end:
    source = '10.0.0.1'
    smac = ("00:00:00:00:00:01")
    for i in range(2,65):
    		
        #dmac = ("00:00:00:00:00:0")+str_to_bool(hex(i))
    	destination = '10.0.0.%r'%i
    	#print "Source IP:", source, "----->", "Destination IP:", destination,"(",mac,")"
    	#arp = ARP(op = 1, psrc=source, pdst=destination, hwsrc=smac, hwdst=dmac)
	#arp =(Ether(dst= dmac)/ARP(psrc=source, pdst = destination))
	arp =(Ether(dst='ff:ff:ff:ff:ff:ff')/ARP(psrc=source, hwsrc=smac, pdst = destination))
    	sendp(arp)
	#send(arp)
    	sleep(0.005)


'''
for i in range(1,5):
	for j in range (1,5):
		if i == j:
			pass 
		else
			
			#print ("10.0.0.%r") %i, "ARP--------->", ("10.0.0.%r") %j
			mac = ("00:00:00:00:00:0")+str_to_bool(hex(j))
			source = '10.0.0.%r'%i
			destination = '10.0.0.%r'%j
			print "Source IP:", source, "----->", "Destination IP:", destination,"(",mac,")"
		 
			arp = ARP(op = 1, psrc=source, pdst=destination, hwdst=mac)
			send(arp)

for i in range(2,65):
		
        mac = ("00:00:00:00:00:0")+str_to_bool(hex(i))
    	source = '10.0.0.1'
    	destination = '10.0.0.%r'%i
    	print "Source IP:", source, "----->", "Destination IP:", destination,"(",mac,")"
    	arp = ARP(op = 1, psrc=source, pdst=destination, hwdst=mac)
    	send(arp)
        sleep(1)
'''
