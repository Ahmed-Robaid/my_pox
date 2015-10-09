
import collections
import threading
import time
import datetime


class TimeExpiredDict:
    """
TimeExpiredDict. Implemented only IN,LEN,STR  operators !!
    """
    def __init__(self, timeout):
        self.lock = threading.Lock()
        self.timeout = timeout
        self.container = {}

    def add(self,item):
        """Add event time
        """
        if item in self.container:
            print "Cant process the same request from %s in short time (%s sec)" % (item, self.timeout)
            return False #return False, that item was not added, because in deque exists the same

        with self.lock:
            self.container[item] = True
            threading.Timer(self.timeout, self.expire_func, args=(item, )).start()  #staring timer which will be executed on timeout
            return True  #return True, that item was sucessfully added

    def __len__(self):
        """Return number of active events
        """
        with self.lock:
            return len(self.container)

    def expire_func(self, remove_item):
        """What should we do when value expires
        Remove any expired items
        """
        with self.lock:
            val = self.container.pop(remove_item)  #removing
        

    def __str__(self):
        with self.lock:
            return 'Container: %s' % str(self.container.keys())

    # def __contains__(self, val):
    #     with self.lock:
    #         return val in self.container



c = TimeExpiredDict(timeout=1)
assert(len(c) == 0) #blank dict
print(c)

c.add((1,2))
c.add((1,2)) #Bob will be added only once , here you will see error message

time.sleep(0.75) #sleep less then timeout, Bob is still in dict
c.add('SANDY') #add new client
assert(len(c) == 2) #check we have both clients in dict
print(c)

time.sleep(0.75) # Here Bob should leave dict, because it is 1.5 sec since he was added
assert(len(c) == 1) #check that only Sandy in dict
print(c)

time.sleep(0.3) #Here Sandy should leave dict, because it is 1.05 sec since Sandy was added
assert(len(c) == 0)
print(c)
