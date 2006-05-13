import xmlrpclib

s = xmlrpclib.Server('http://localhost:11117/', allow_none = True)

result = s.getQueueInfo('Instance #1')
print result