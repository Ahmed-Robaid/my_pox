TODO list:
1) Recognize all ARP packets -> also reqs, need to send them to the controller to do revNat
	DONE

2) Send them to the controller
	DONE  

3) Controller has to swap ARP source with safe new source  
	- Keep track of sources given and which reqs are still pending  
	  use table [psrc, hwsrc, pnew, hwnew] if OP = who-has  
	DONE  

4) send natted arp request to the destination  
	DONE  

5) receive back the reply, swap back the destination with the correct one, 
	- handle replies  
	DONE  

	```  
		if op == is-at:  
			if [hwdst,pdst] is in table as [hwnew, pnew]:  
				swap [hwdst,pdst] with [hwsrc,psrc]  
				sendto(hwsrc,psrc)  
			else:  
				flood()  
	```  
	- delete (?) the entry from the table, in order not to keep posoned entries (maybe keep for a while)  
  
6) Write report on controller and check possible interactions with host_tracker component  
