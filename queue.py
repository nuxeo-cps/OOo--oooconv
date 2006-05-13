#!/usr/bin/python
# Copyright (c) 2006 Nuxeo SARL <http://nuxeo.com>
# Author: Laurent Godard <lgodard@indesko.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as published
# by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA
# 02111-1307, USA.
#
# See ``COPYING`` for more information
#
# $Id$
import time
import os, signal, locale

from pyOOoConv import OOoConv
#from MsgOOoEngine import connectOOo as OOoMessager

from twisted.internet import threads, defer

from popen2 import Popen4 as Popen
                
from threading import Lock

class Queue:

    def __init__(self,params):
        self.queuedConversions = {} #[]
        self.queued = -1
        self.processed = -1
        self.keepAlive = True
        self.count = 0
        self.parameters = params
        self.locker = Lock()
        self.stopRequested = False
        self.engine = {}
        
        if self.parameters['statFile'] is not None:
            self.fichier = open(self.parameters['statFile'],'a')
        else:
            self.fichier = None
            
        return
    
#    def startAsyncThread(self, OOoInstances):
    def startAsyncThread(self): 
        for OOoInstance in self.parameters['OOoPool']:
            self.startOneInstance(OOoInstance)
        return   
        
                
    def startOneInstance(self, OOoInstance):    
        self.count += 1
        OOoInstance['queueID'] = str(self.count)
        #OOoInstance['PID'] = None 
        d = threads.deferToThread(self.loopQueue, OOoInstance)
        d.addErrback(self.errBack, OOoInstance)
        return           
         
    def errBack(self, param, OOoInstance):
    
        print "*************** errback ***************************"
        print str(param)
        print OOoInstance
        if OOoInstance['PID'] is not None:
            print "ERROR killing OOo instance #%s" % (OOoInstance['queueID'])     
            self.stopAnInstance(OOoInstance)
            print "ERROR killed instance #%s" % (OOoInstance['queueID']) 
            
        #repost job
            print "add instance"
            if OOoInstance['queuedConversion'] is not None:
                self.add (OOoInstance['queuedConversion'])
            print "ok add"
                      
        #restart
            print "restart"
            OOoInstance['PID'] = None
            OOoInstance['curRuns'] = 0
            self.startOneInstance(OOoInstance)    
            
        print "******************************************************"
    
        return
    
    def loopQueue(self, OOoInstance):
            
        while self.keepAlive and not OOoInstance['stopInstance']:
            #start or restart OOo instance
            if OOoInstance['curRuns'] % OOoInstance['maxRuns'] == 0:
                self.startAnInstance(OOoInstance)                   
            
            toProcess = -1
            self.locker.acquire()
            try:
                if self.queued != self.processed:
                    toProcess = self.processed + 1
                    self.processed += 1
                else:
                    if self.stopRequested:
                        self.keepAlive = False
                        self.stopRequested = False #prevents to be procesed an other time               
            finally:
                self.locker.release()
            
            if toProcess == -1:  
                OOoInstance['status'] = 'sleeping'       
                time.sleep(0.5)
            else:
                if self.queuedConversions.has_key(toProcess):
                    OOoInstance['queuedConversion'] = None                
                    print "Process Job #%s" % (toProcess)
                    self.callOOoConversion(OOoInstance, toProcess)
                else:
                    #the job has been removed from the queue     
                    print "Job #%s has been removed" % (toProcess)
                    OOoInstance['status'] = 'sleeping'       
                    time.sleep(0.5)                    
                
        # the instance stop has been required        
        self.stopAnInstance(OOoInstance)
                
        return     

    def startAnInstance(self, OOoInstance):

        print "\tStarting new OOo instance #%s" % (OOoInstance['queueID'])    
    
        if OOoInstance['PID'] is not None:
            self.stopAnInstance(OOoInstance)
            #relance les xvfb
            if self.parameters['xvfb'] is not None:
                instanceX = Popen('%s :%s -auth "%s" -screen 0 1024x768x24' % (
                                                    self.parameters['xvfb'],
                                                    OOoInstance['Xserver'],
                                                    self.parameters['xauth']))
                OOoInstance['Xserver-pid'] = instanceX.pid   
                print  'launched %s :%s as PID %s' % (
                            self.parameters['xvfb'],
                            OOoInstance['Xserver'],
                            str(OOoInstance['Xserver-pid']))                     
               

        #start new Process
        if self.parameters['xvfb'] is not None:      
            display ='DISPLAY=":%s.0" ' % ( OOoInstance['Xserver']) 
            headless = " -headless "
            
        else:
            display = ''
            headless = ' -headless '
            
        commandLine = display + (" nice -n 10 " +
                            OOoInstance['path'] +  " " + 
                            OOoInstance['userEnv'] +
                            " -norestore" +
                            headless +
                            ' -accept="socket,host=%s,port=%s;urp;StarOffice.ServiceManager;"'
                                % (OOoInstance['host'],OOoInstance['port'])
                            )
                        
        print "\nlaunched command line\n %s \n" %(commandLine)
    
        anInstance = Popen(commandLine )
        
        OOoInstance['PID'] = anInstance.pid
        OOoInstance['curRuns'] += 1
        OOoInstance['commandLine'] = commandLine
        self.engine[OOoInstance['queueID']] = OOoConv(OOoInstance['host'],OOoInstance['port'])
        print "New OOo instance '%s' (ID #%s) started on %s:%s" % ( OOoInstance['name'],
                                                                    OOoInstance['queueID'], 
                                                                    OOoInstance['host'],
                                                                    OOoInstance['port'])
               
        return
        
    def stopAnInstance(self, OOoInstance):
        
        print "killing OOo instance '%s' (ID #%s)" % (OOoInstance['name'], OOoInstance['queueID'])
    
        #OOoInstance['pyOOoConv'] = None    
                
        self.killParentAndChilds(OOoInstance['PID'])
        
        if self.parameters['xvfb'] is not None:
            print "killing associated Xvfb #%s to instance '%s' (ID #%s)" % ( OOoInstance['Xserver'], 
                                                           OOoInstance['name'],OOoInstance['queueID']) 
            self.killParentAndChilds(OOoInstance['Xserver-pid'])
        
        OOoInstance['PID'] = None
        OOoInstance['Xserver-pid'] = None
        
        print "OK killed instance '%s' (ID #%s)" % (OOoInstance['name'], OOoInstance['queueID'])     
        
        return    
  
              
    def killParentAndChilds(self,pid):
    
        """Sends a kill signal to a PID and recursivelly to all its childs"""

        print "\tkilling pid " + str(pid)
        try:
            os.kill (int(pid), signal.SIGKILL)
            # wait for avoiding zombies
            os.waitpid(int(pid),0)
        except:
            pass

        return            
               
    def callOOoConversion(self,activeInstance, JobId):
    
        print "process %s" % (JobId)
    
        
        parameters = self.queuedConversions[JobId] 
        activeInstance['status'] = 'converting'
        parameters['status'] = 'converting'
        parameters['start'] = str(time.time())
        activeInstance['queuedConversion'] = parameters
        engine = self.engine[activeInstance['queueID']]  
        parameters['convertedList'] = [] 
                
        if os.path.isfile(parameters['source']):
            
            parameters['convertedList'] = engine.export(parameters)     
                           
            parameters['sourceSize'] = os.path.getsize(parameters['source'])
            parameters['end'] = str(time.time())    
            
            if len(parameters['convertedList']) > 0:
                parameters['status'] = 'done'
                activeInstance['queuedConversion'] = {}
                parameters['destSize'] = os.path.getsize(parameters['convertedList'][0]) #le premier seulement   
            else:
                parameters['status'] = 'fail'
                #on redemarre OOo car pas normal           
                activeInstance['curRuns'] = activeInstance['maxRuns']

        else:
            print "Source file missing"
            parameters['status'] = 'fail - source missing'
            # dummy values
            parameters['sourceSize'] = 0
            parameters['destSize'] = 1  
            parameters['end'] = str(time.time()+1)

       
        activeInstance['curRuns'] += 1
                    
        parameters['nbRunningInstances'] = len([ooo for ooo in self.parameters['OOoPool'] if ooo['status']=='converting'])
        parameters['duration'] = float(parameters['end'])-float(parameters['start'])
        duree = str(round(parameters['duration'],2))
        print "*%s* JobId=%s OOo=%s durée=%s" %(parameters['status'],str(JobId), activeInstance['queueID'],duree)  


        
        parameters['speed'] = parameters['sourceSize']/parameters['duration']
        parameters['compression'] = float(parameters['sourceSize'])/float(parameters['destSize'])

        #if self.fichier is not None:         
        #    logMe= (str(time.ctime())+'\t'+
        #            parameters['source']+'\t' +
        #            str(parameters['format'])+'\t' +
        #            str(parameters['duration'] ) + "\t" +
        #            str(parameters['nbRunningInstances'] ) + "\t" +
        #            str(parameters['nbChamps']) + "\t" +
        #            str(parameters['sourceSize']) + "\t" +
        #            str(parameters['destSize']) + "\t" +
        #            str(parameters['speed']) + "\t" +
        #            str(parameters['compression'])
        #            )               
        ##    self.fichier.write(logMe+"\n")  
        #    self.fichier.flush() 
        
        print "\t converted JobID #%s to format %s in %s seconds by %s - speed: %s kB/s compression: %s" % ( parameters['id'], str(parameters['format']), str(round(parameters['duration'],2)),
        activeInstance['name'], str(round(parameters['speed']/1024,2)),
         str(round(parameters['compression'],2))
         )
         
         
        if parameters.has_key('deleteSourceAfterProcessing'):
            if parameters['deleteSourceAfterProcessing']:
                if os.path.isfile(parameters['source']):
                    print "delete %s" % (parameters['source']) 
                    os.remove(parameters['source'])
        
        if parameters.has_key('deleteDestAfterProcessing'):
            if parameters['deleteDestAfterProcessing']:
                for aFile in parameters['convertedList']:
                    if os.path.isfile(aFile):
                        print "delete %s" % (aFile) 
                        os.remove(aFile)  
            
        return       
            
        
    def add(self, parameters):
        if not self.stopRequested:
            self.queued += 1
            parameters['id'] = self.queued
            parameters['start'] = str(time.time()) #time.gmtime()
            parameters['end'] = ''
            parameters['status'] = 'waiting'
            #parameters['sourceSize'] = os.path.getsize(parameters['source'])
            #dummy, parameters['source'] = os.path.split(parameters['modele'])
                        
            self.queuedConversions[parameters['id']] = parameters
        else:
            parameters['id'] = -1
            
        return parameters['id']
    
    def stopQueue(self, delay=''):
        if self.keepAlive:
            if delay != 'delay':
                self.stopRequested = False
                self.keepAlive = False        
                print "Queue and OOo Instances are being stopped"
            else:
                #consumes the queue before ending
                self.stopRequested = True
            
        return
        
if __name__ == '__main__':  
    queue = Queue()

        