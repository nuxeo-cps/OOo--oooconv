import xmlrpclib

s = xmlrpclib.Server('http://localhost:11117/')

param={
    'source':"/home/lgodard/tmp/avirer.sxc",
    'dest':"/home/lgodard/tmp/avirer",
    'format':"PDF",
    #these info are optional - defaults are applied - can be deleted
    'mail': "lgodard@indesko.com",
    'deleteSourceAfterProcessing': False,
    'deleteDestAfterProcessing': False,
    'mailer':{'messageSubject':u'pyOOoConv : Conversion Result',
              'from':'pyOOoConv <lgodard@indesko.com>',
              'messageBody':u"Please find the transformed file you requested...\n",
              'SMTPaddress': 'smtp.wanadoo.fr',
              'SMTPport':'25',
              'SMTPhost': 'localhost' ,
                }
}

result = s.addJob(param)
print result
