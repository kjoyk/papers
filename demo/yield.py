#coding:utf-8
class item():
    def __init__(self):
        self.data=[]
        self.strs=[]

def yield1(y):
    x=0
    for i in range(1,y):        
        yield i

def yield2():
    a=['a','b','c','d','e']
    for y in yield1(10):
        yield y
    print x
    for x in a:
        yield x

def caller(call,*argu):
    for c in call(*argu):
        print c

caller(yield2)

