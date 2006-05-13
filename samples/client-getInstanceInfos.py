import xmlrpclib

s = xmlrpclib.Server('http://localhost:11117/', allow_none = True)

result = s.getOOoInstanceByName()
print result
result = s.getOOoInstanceByName('Instance #1')
print result
result = s.getOOoInstanceByStatus('sleeping')
print result
result = s.getOOoInstanceCountByStatus('sleepping')
print result
result = s.getOOoInstanceCountByStatus('converting')
print result
result = s.getOOoInstanceByStatus('converting')
print result

