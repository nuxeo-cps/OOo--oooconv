import xmlrpclib

s = xmlrpclib.Server('http://localhost:11117/', allow_none = True)

#print s.getQueueInfo()

ooo = {'name': 'Instance Added',
    'maxRuns': 750,
    'userEnv': '-env:UserInstallation=file:///home/lgodard/OOoPool/user4', 
    'path': '/home/lgodard/OpenOffice.org1.1.5_test/program/soffice', 
    'host': 'localhost', 
    'port': '2005'}

result = s.addOOoInstance(ooo)
print result