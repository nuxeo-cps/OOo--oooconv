#!/usr/bin/python
# Copyright (c) 2006 Nuxeo SARL <http://nuxeo.com>
# Author: Laurent Godard <lgodard@indesko.com>
# M.-A. Darche (Nuxeo)
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
# See ``COPYING`` for more information
#
# $Id$


from xml.dom import minidom

class XmlConfig:
    """Manipulates an XML configuration file
    
    based on pyOOoConv.xml file"""
    
    def __init__(self, configFile):
        self.configXMLFile = configFile
        self.isValid = True
        self.configElts = self.readXmlConfigFile(self.configXMLFile)
        
        
    def readXmlConfigFile(self, filename):
        """reads the XML File and stores it"""
        configParse = minidom.parse(filename)
        configDocElt = configParse.documentElement
        eltsParse = configDocElt.childNodes
        configElts = []
        for node in eltsParse:
            if node.nodeType == node.ELEMENT_NODE:
                lenAtt = node.attributes.length
                dictAtt = {}
                i = 0
                while i < lenAtt:
                    att = node.attributes.item(i)
                    dictAtt[att.name] = att.value
                    i += 1
                tupleElt = (node.nodeName, dictAtt)
                configElts.append(tupleElt)
                
        return configElts
            
    def getConfigValueByName(self, element, attribute,
                                   nameValue='', nameKey='name',):
        """
        Retreive a property of an element by its name
        """
        value = None
        i = len(self.configElts) - 1
        while i >= 0 :
            elt = self.configElts[i]
            if nameValue != '':
                if elt[0] == element:
                    if elt[1].has_key(nameKey):
                        if elt[1][nameKey] == nameValue:
                            value = elt[1][attribute]
            else:
                # We take the default element
                if elt[0] == element:
                    if elt[1].has_key(attribute):
                        value = elt[1][attribute]
            i = i - 1
        
        return value    

    def getConfigValueByIndex(self, element, attribute, index = 0):
        """
        myParams.getConfigValueByIndex('oooserver', 'name', nb)
        """
        value = None
        count = -1
        
        i = len(self.configElts) - 1
        
        while i >= 0 and count < index :
            
            elt = self.configElts[i]
            
            if elt[0] == element:
                count += 1            
                if count == index:
                    if elt[1].has_key(attribute):
                        value = elt[1][attribute]
                                        
            i = i - 1
        
        return value    
        
    def getConfigValues(self, element, filterAttributeList = None):
        """
            the list of the used ports and hosts by name"        
            myParams.getConfigValues('oooserver', ['name', 'host', 'port'])
            
            all the servers configuration"                
            myParams.getConfigValues('oooserver')           
        """
        value = []
        
        i = len(self.configElts) - 1
        
        while i >= 0:
        
            elt = self.configElts[i]
            if elt[0] == element:
            
                aDic = {}
                if filterAttributeList is None:
                    aDic = elt[1]
                else:                 
                    for key in filterAttributeList:
                        if elt[1].has_key(key):
                            aDic[key] = elt[1][key]
                        
                value.append(aDic)     
                                           
            i = i - 1
        
        return value          
        
        
if __name__ == '__main__':
    
    fileName = "pyOOoConv.xml"
    myParams = XmlConfig(fileName)

    print '---------- getConfigValueByName usage --------------------'
    print         
    print "--> the first host value"
    print myParams.getConfigValueByName('oooserver', 'host')
    print
    
    print "--> the path of the server named Instance #2"
    print myParams.getConfigValueByName('oooserver', 'path', 'Instance #2')
    print

    print "--> the name of the server that uses port 2002"        
    print myParams.getConfigValueByName('oooserver', 'name', '2002', 'port')
    print
    
    print '---------- getConfigValueByIndex usage --------------------'
    print 
    
    nb = 0
    retour = ''
    while retour is not None:
        retour = myParams.getConfigValueByIndex('oooserver', 'name', nb)
        nb += 1
        print retour
        
    print     
    print '---------- myParams.getConfigValues usage --------------------'
    print
    print "--> the list of the used ports and hosts by name"        
    print myParams.getConfigValues('oooserver', ['name', 'host', 'port'])
    print 
    print "--> all the servers configuration"                
    print myParams.getConfigValues('oooserver')    
         