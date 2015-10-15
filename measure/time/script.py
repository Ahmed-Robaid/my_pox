import re
f = open('fixed_l2arplin20FIX.dat','r')
sum = 0
for line in f:
    line = line[:-1]
    if re.match(r'\s', line) or 'ARP' in line:
        print float(sum)/30
        sum = 0
    else:
        sum = sum + float(line)
    
