import xmlrpclib

s = xmlrpclib.Server('http://localhost:11117/', allow_none = True)

result = s.getJobsByStatus('done')
print result
result = s.getJobsCountByStatus('done')
print result
result = s.getJobsByStatus('waiting')
print result
result = s.getJobsCountByStatus('waiting')
print result