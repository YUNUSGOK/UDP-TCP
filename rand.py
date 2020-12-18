import random
def decision(p):
    return random.random() < p

t1 = 0
t2 = 0
for i in range(1000):
    d = decision(10/100)
    if(d):
        t1 = t1+1
print(t1)