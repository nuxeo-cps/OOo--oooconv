#!/usr/bin/python
# Copyright (c) 2006 Nuxeo SARL <http://nuxeo.com>
# Author: Laurent Godard <lgodard@indesko.com>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License version 2.1 as published by the Free Software Foundation
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
#
#
# See ``COPYING`` for more information
#
# $Id$

# -*- coding: iso-8859-15 -*-
from twisted.web import xmlrpc, server
from twisted.internet import threads
from twisted.internet import reactor, defer

from parameters import XmlConfig
from queue import Queue

from popen2 import Popen4 as Popen

import time
import copy

class OOoConvAsyncServer(xmlrpc.XMLRPC):
    
    def __init__(self, parameters):
        #self.serverParams = self.loadParameters(parameters)
        self.loadParameters(parameters)
        reactor.suggestThreadPoolSize(10+len(self.serverParams['OOoPool']))
        self.queue = Queue(self.serverParams)
        self.startListeningQueue()
        self.startTime = time.time()
        return
       
    def startListeningQueue(self):
        self.queue.keepAlive = True
        #self.deferedQueue = self.queue.startAsyncThread(self.serverParams['OOoPool'])        
        self.queue.startAsyncThread()        
        return    
                
    def loadParameters(self, params):   
    
        self.serverParams={}  
        self.serverParams['OOoPool'] = []
        
        self.serverParams['xvfb'] = myParams.getConfigValueByName('xvfb', 'command')
        if self.serverParams['xvfb'] is not None:
            self.serverParams['xauth'] = myParams.getConfigValueByName('xvfb', 'Xauth')
            self.ScreenNb = long(myParams.getConfigValueByName('xvfb', 'firstXserver'))            
                       
        oooServers = params.getConfigValues('oooserver')
        
        for ooo in oooServers:
            ooo = self.startAnOOo(ooo)
            self.serverParams['OOoPool'].append(ooo)
            
        self.serverParams['statFile'] = myParams.getConfigValueByName('rpc-server',
                                                                 'statfile')  
        #if self.serverParams['statFile'] is not None:
        #    self.loadStats()
                                                                                                                           
        return    

    def startAnOOo(self, ooo):
    
        ooo['curRuns'] = 0
        ooo['PID'] = None
        ooo['maxRuns'] = long(ooo['maxRuns'])
        ooo['stopInstance'] = False   
        if self.serverParams['xvfb'] is not None:
            ooo['Xserver'] = str(self.ScreenNb)
            instanceX = Popen('%s :%s -auth "%s" -screen 0 1024x768x24' % (
                                                                    self.serverParams['xvfb'],
                                                                    ooo['Xserver'],
                                                                    self.serverParams['xauth']))
            ooo['Xserver-pid'] = instanceX.pid
            
            print  'launched %s :%s -auth "%s" -screen 0 1024x768x24 as %s' % (self.serverParams['xvfb'],
                                                                                ooo['Xserver'],
                                                                                self.serverParams['xauth'],
                                                                                str(ooo['Xserver-pid']))   
            self.ScreenNb += 1 

        return ooo 
               
    def shutdown(self):
        stillAlive = True
        OOoPool = self.serverParams['OOoPool']
        while stillAlive:
            stillAlive = False
            for aServer in OOoPool:
                if aServer['PID'] is not None:
                    stillAlive = True
            time.sleep(1)  
        if self.serverParams['statFile'] is not None:
            self.queue.fichier.close()    
            self.queue.fichier = None   
        #self.storeStats()    
        reactor.stop()
        
        return      
            
    def xmlrpc_addJob(self, parameters):
        Id = self.queue.add(parameters)
        if Id == -1:
            print "--> Shutdown planed : Job rejected"
        return Id

    def xmlrpc_stop(self, delay = ''):
        self.queue.stopQueue(delay)
        d = threads.deferToThread(self.shutdown)
        return "ok"
        

    def storeStats(self):
        numberOfInstances = len(self.getOOoInstanceByKey('name', None))
        jobs = self.getJobsByStatus('')
        numberOfJobs =0 
        uptime = 0
        meanDuration =0
        
        return    

    def loadStats(self):
        self.stats = {}
        statFile = open(self.serverParams['statFile'],'r')
        lines = statFile.readlines()
        for line in lines:
            infos = line.split("\t")
            modele = infos[1]
            duration = float(infos[3])
            nbActiveSessions = float(infos[4])
            nbLines = float(infos[5])
            if not self.stats.has_key(modele):
                self.stats[modele] = {}
                self.stats[modele]['nb'] = 0
                self.stats[modele]['speed'] = 0
            
         
            self.stats[modele]['speed'] = (self.stats[modele]['speed']* self.stats[modele]['nb']
                                           + duration/nbActiveSessions/nbLines
                                           )/(self.stats[modele]['nb'] + 1)
            self.stats[modele]['nb'] += 1               
        
        self.serverParams['stats'] = self.stats 
        return     
        
            
                            
    def getOOoInstanceByKey(self, key, value = None):
        
        if value is not None:
            response = [copy.deepcopy(ooo) for ooo in self.serverParams['OOoPool'] if ooo[key] == value]
        else:
            response = self.serverParams['OOoPool']
        
        return response        
        
    def xmlrpc_getOOoInstanceByName(self, instanceName = None):
        OOoInstance = self.getOOoInstanceByKey('name', instanceName)  
        return OOoInstance

    def xmlrpc_getOOoInstanceByStatus(self, status):
        OOoInstance = self.getOOoInstanceByKey('status', status)
        return OOoInstance  
        
    def xmlrpc_getOOoInstanceCountByStatus(self, status):
        OOoInstance = self.getOOoInstanceByKey('status', status)
        return len(OOoInstance)  
                                   
    def xmlrpc_killOOoInstanceByName(self, instanceName):
        """kills OOo instance with the name starting with instanceName"""
        done = []
        size = len(instanceName)
        
        Instances = [ooo for ooo in self.serverParams['OOoPool'] if ooo['name'][0:size] == instanceName]
        for instance in Instances:
            instance['stopInstance'] = True
            done.append(instance['name'])
    
        return done
        
    def xmlrpc_addOOoInstance(self, ooo):
        response = [already for already in self.serverParams['OOoPool'] if already['name'] == ooo['name']]
        if len(response) == 0:
            ooo = self.startAnOOo(ooo)
            self.serverParams['OOoPool'].append(ooo)
            self.queue.startOneInstance(ooo)
            message = 'ok, instance added'
        else:
            message = "fail, Instance Name already exists \n" + str(response)
        
        return message           

    def getJobsByStatus(self, status): 
        jobs = [job for job in self.queue.queuedConversions.values() if job['status'] == status] 
        return jobs 
        
    def xmlrpc_getJobsByStatus(self, status):
        jobs = self.getJobsByStatus(status)
        return jobs 

    
    def xmlrpc_getJobsCountByStatus(self,status):
        jobs = len(self.getJobsByStatus(status))
        return jobs 
                
    def xmlrpc_getJobByIndex(self, Id):
  
        if self.queue.queuedConversions.has_key(Id):            
            JobInfo = self.queue.queuedConversions[Id]
        else:
            JobInfo = {}                   
        return  JobInfo  
             
    def xmlrpc_removeJobByIndex(self, Id):
        done  = '' 
        if self.queue.queuedConversions.has_key(Id):
            del self.queue.queuedConversions[Id]  
            done = 'removed'   
        else:
            done = 'No such ID'
        return  done  
        
                                
    def xmlrpc_ping(self):
        return "pong" 
        
    def xmlrpc_uptime(self):
        currenTime = time.time()
        delta = currentTime - self.startTime
        duration = str(round(delta,2))    
        return duration              
        
        
if __name__ == '__main__':

    #read params
<<<<<<< .mine
    fileName = "pyOOoConv.xml"
=======
    fileName = "./pyOOoConv.xml"
>>>>>>> .r49138
    myParams = XmlConfig(fileName)
    listenPort = myParams.getConfigValueByName('rpc-server', 'port')
    
    r = OOoConvAsyncServer(myParams)
    print "Queue is running ..."
    reactor.listenTCP(long(listenPort), server.Site(r))
    print "Ready to listen incoming requests on port %s..." % (listenPort)
    reactor.run()
    print "Server is now stopped !!! "
