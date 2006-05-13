import xmlrpclib

s = xmlrpclib.Server('http://localhost:11117/', allow_none = True)

#print s.getQueueInfo()
result = s.killOOoInstanceByName('Instance #1')
print result