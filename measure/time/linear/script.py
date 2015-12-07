import re
f = open('l2.dat','r')
sum = 0
for line in f:
    #line = line[:-1]
    if 'ARP' in line:
        x=1
    elif re.match(r'\s', line):
        print float(sum)/20
        sum = 0
    else:
        sum = sum + float(line)
    
print float(sum)/20
