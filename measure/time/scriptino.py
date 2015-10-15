f1 = open('reslin.dat', 'r')
f2 = open('resarplin.dat','r')

i=1
for line in f1:
    i=i+1
    line2 = f2.readline()
    line = line[:-1]
    line2 = line2[:-1]
    print str(i)+' '+ line + ' ' + line2
