OOoConv 

author : Laurent Godard <lgodard@indesko.com> 
version : 0.1


Purpose
-------
pyOOoConv is a document converter based on OOo remote scripting
Sending a document and a target format to the converter will transform it
Multiple output files are zipped and result may be sent by e-mail

It is designed to be a standalone python class that can be used inside Zope and CPS 
Nevertheless, it can be used as a standalone script as command line or called by an other application

Prerequisites
-------------
a running instance of OOo in listening mode (localhost, port 2002)

./soffice "-accept=socket,host=localhost,port=2002;urp;"

the filters are designed for OOo2 but are suitable for OOo1.1.x
Be carefull that OpenDocument filters won't work with OOo1.1.x

Starting
--------

For this first version, edit the file and adapt
    theSourceFile="/home/lgodard/myFile.odp"
    theTargetFile="/home/lgodard/tmp/pyOOoConv/myResult" #please note, NO extension
    theFormat = "PDF"
    sendTo = "lgodard@indesko.com"

then, run pyOOoConv

Note: all readable files can be submitted as source.
This means that a doc file can theorically be a source and transformed to, say PDF

XML-RPC server mode
-------------------

-server parameters
    - in server.py, modify the paths for the OOo instances in loadParameters()

launch server.py --> listens on port 11117
to stop the server : server-stop.py
run an example : see client-go.py


Supported Exports
----------------- 

see Filters dictionary 
for the moment   

TODO
----

a lot : TODO fill this section

- external parameters for smtp
- mime types not based under file extension
- handle TEX files (see sxw2latex) 
- log
- command line arguments
- an automatic mode (chain conversion, zipping, sending mail)
- overload zip directive for multipart outpout
- list supported format (a method)
- export MS Powerpoint 97 is broken
- store filters as XML


'------------------
' xml-rpc server version
'-------------------

s = xmlrpclib.Server('http://localhost:11117/')

callable Methods through xml-rpc
--------------------------------


    
    - s.stop(delay) : shutsdown the server
        delay : 'now' stops even if remaining jobs in the queue. Other value (default) , wait for queue is empty. Do no accept any Job any more
    
    - s.ping() : is the server alive ?
        return : 'pong'
    
    - s.getJobByIndex(Id) : gives Job informations dictionary
        Id : the Job Id
        return : the Job dict, Empty dict if Id do not exists
    
     - s.addJob(parameters) : adds in the queue
        parametres: depends on the engine
        return : the JobID, -1 if job rejected due to planned shutdown
    
     - s.removeJobByIndex(Id) : removes a Job
        Id : the Job Id
        return : 'removed', if successful
                 'No such ID', if Id do not exists 
          
     - s.getJobsByStatus(status) : get jobs dictionary meeting the status
        status : 'done", 'waiting'
        return : list of job dictionary
     
     - s.getJobsCountByStatus(status) : : number of jobs meeting the status
        status : 'done', 'waiting'
        return : number of job    
    
     - s.getOOoInstanceByName(instanceName = None) : the OOo instance dictionary information
        instanceName : Name of the OOo instance to retreive
        return : the OOo instance dict, all dicts if instanceName is None 

     - s.getOOoInstanceByStatus(status) : the OOo instance dictionary information meeting the status
        status : 'sleepping', 'converting'
        return : list of OOo instance dictionary
     
     - s.getOOoInstanceCountByStatus(status) : the number of OOo instances meeting the status
        status : 'sleepping', 'converting'
        return : number of OOo instances
     
     - s.addOOoInstance(ooo) : adds an OOo instance as a worker
        ooo : minimal OOo instance dictionary
        returns :   'ok, instance added' if successfull
                    'fail, Instance Name already exists' and list of existing OOo instances dictionaries
          
     - s.killOOoInstanceByName(instanceName) :
        instanceName : begining of the name of the instance. Works as a jocker
        returns : list of the name of the suppressed instances 
    
        
Dictionaries
-----------------------

   - OOo Instance
   
   [{'name': 'Instance #3'
    'status': 'sleeping', 
    'queueID': '0',
    'maxRuns': 750,
    'curRuns': 4,
    'commandLine': 'DISPLAY=":50.0"  nice -n 10 /home/lgodard/OpenOffice.org1.1.5_test/program/soffice -env:UserInstallation=file:///home/lgodard/OOoPool/user3 -norestore -headless  -accept="socket,host=localhost,port=2004;urp;StarOffice.ServiceManager;"', 
    'queuedConversion': {}, 
    'PID': 14247, 
    'userEnv': '-env:UserInstallation=file:///home/lgodard/OOoPool/user3', 
    'path': '/home/lgodard/OpenOffice.org1.1.5_test/program/soffice', 
    'Xserver-pid': 14241, 
    'Xserver': '50',
    'host': 'localhost', 
    'port': '2004'}]
 
    queuedConversion contient le dictionanire du Job #N en cours quand le status est "converting #N"    
 
   - minimal OOo Instance
   
        {'name': 'my New instance',
         'maxRuns': 750,
         'userEnv': '-env:UserInstallation=file:///home/lgodard/OOoPool/user4', 
         'path': '/home/lgodard/OpenOffice.org1.1.5_test/program/soffice', 
         'host': 'localhost', 
         'port': '2005'}  
      
   - a Job
   
   {'id': 5, 
   'status': 'done', 
   'end': '1131641371.28', 
   'start': '1131641369.39', 
   'duration': 1.8899998664855957,   
   'compression': 0, 
   'format': ['PDF'], 
   'resultat': '/home/lgodard/Indesko/dvlpt/messager/Messager2/MSGOOoEngine/resultat-', 
   'modele': '/home/lgodard/Indesko/dvlpt/messager/Messager2/MSGOOoEngine/document.sxw', 
   'datas': [{'champ5': 'leChamp numero 2', 
              'champ4': 'leChamp numero 1', 
              'champ7': 'leChamp numero 1', }]
    }

   

setup on a server
----------------
$ Xvfb :2 &
$ export DISPLAY=":2.0"
$ ./setup -r ~/tmp/OOoresponseFile.txt


