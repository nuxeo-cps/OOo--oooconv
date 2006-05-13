import xmlrpclib
import sys

s = xmlrpclib.Server('http://localhost:11117/')

arg =int(sys.argv[1])

print "Job N° " + str(arg) 
result = s.getJobByIndex(arg)
print result
