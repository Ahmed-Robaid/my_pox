filename = raw_input("Enter filename: ")
f = open(filename, 'r')

sum = 0
for line in f.readlines():
	asd = line.split()
	sum = float(asd[1]) + sum
	
print sum/40
