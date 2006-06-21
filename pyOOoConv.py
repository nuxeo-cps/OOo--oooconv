# -*- coding: iso-8859-15 -*-
#    
import uno, unohelper
from com.sun.star.beans import PropertyValue

from com.sun.star.connection import NoConnectException
from com.sun.star.lang import DisposedException
from com.sun.star.uno import RuntimeException

from mailer import processMail

#needed for zipping file
import zipfile
import os
import locale
import shutil
import time

# pyOOoConv supported filters - dictionary
from filters import Filters
    
class OOoConv:
    
    def __init__(self,oooserver_host='localhost', oooserver_port='2002'):
        #Connect to OOo
        self.ctx=self._connectOOo(oooserver_host, oooserver_port)
        self.oooserver_host = oooserver_host
        self.oooserver_port = oooserver_port
        if self.ctx is not None:
            self.smgr = self.ctx.ServiceManager
            self.desktop = self.smgr.createInstanceWithContext(
                                        'com.sun.star.frame.Desktop',
                                         self.ctx)
            self.convertedFilesList = []
            # chain all - export/zip if needed - send mail
            self.autoProcess = True
            print "init fin"
        return
        
    def _connectOOo_ini(self, oooserver_host, oooserver_port):
        """Connects to a listening OOo - returns the context
        """
    
        #Connect to OOo
    
        # get the uno component context from the PyUNO runtime
        localContext = uno.getComponentContext()
        # create the UnoUrlResolver
        resolver = localContext.ServiceManager.createInstanceWithContext(
                                    'com.sun.star.bridge.UnoUrlResolver',
                                    localContext )
    
        # connect to the running office
        try:
            #print "Connecting to server %s:%s ..." % (oooserver_host,
            #                                          oooserver_port)
            while ctx is None:
                ctx = resolver.resolve(
                    'uno:socket,host=%s,port=%s;urp;StarOffice.ComponentContext'
                    % (oooserver_host, oooserver_port))
            print "connection ok"    
        except NoConnectException:
            print "Unable to connect to OpenOffice.org instance"
            ctx = None
                    
        return ctx

    def _connectOOo(self, oooserver_host, oooserver_port):
        """Connects to a listening OOo - returns the context
        """
    
        #Connect to OOo
    
        # get the uno component context from the PyUNO runtime
        localContext = uno.getComponentContext()
        # create the UnoUrlResolver
        resolver = localContext.ServiceManager.createInstanceWithContext(
                                    'com.sun.star.bridge.UnoUrlResolver',
                                    localContext )
    
        # connect to the running office
        print "Connecting to server %s:%s ..." % (oooserver_host,
                                                  oooserver_port)
        ctx = None
   
        while ctx is None:
            try:
                print " try %s %s" % (oooserver_host, oooserver_port)
                ctx = resolver.resolve(
                    'uno:socket,host=%s,port=%s;urp;StarOffice.ComponentContext'
                    % (oooserver_host, oooserver_port))
                print " conencted %s %s" % (oooserver_host, oooserver_port)
            except NoConnectException:
                time.sleep(1)
                print " sleep %s %s" % (oooserver_host, oooserver_port)
            except RuntimeException:
                print "error runtime"
                # get the uno component context from the PyUNO runtime
                print "--> local context"
                localContext = uno.getComponentContext()
                # create the UnoUrlResolver
                print "--> resolver"
                resolver = localContext.ServiceManager.createInstanceWithContext(
                                    'com.sun.star.bridge.UnoUrlResolver',
                                    localContext )                
        
        print "connection ok"    
                    
        return ctx
                            
    def echo(self, message):
        """a debugging purpise echo"""
        return message
                
    def export(self, sourceFileName, destFileName, targetFormat):
        status = 'ok'
        #open doc

        args = (PropertyValue('Hidden', 0, True, 0),)
        url = unohelper.systemPathToFileUrl(sourceFileName)
        sourceDoc = self.desktop.loadComponentFromURL(url, '_blank', 0, args)
                
        #get filter name and params
        docType = self._getDocumentType(sourceDoc)
        
        #Filters = getSupportedFilters()
        if Filters.get(docType).has_key(targetFormat): 
            filterParams = Filters.get(docType).get(targetFormat)
        else:
            return targetFormat + " : unsupported target format"
        
        zipMe = filterParams['zipMe']
        if zipMe:
            self.convertedFilesList=[]
        

        if filterParams['isGraphical']:
            oGraphic=self.smgr.createInstanceWithContext(
                                    'com.sun.star.drawing.GraphicExportFilter',
                                     self.ctx)
            for pageIndex in range(sourceDoc.DrawPages.Count):
                #getByIndex ensures to retreive slides in correct order 
                #Not getByName
                page = sourceDoc.DrawPages.getByIndex(pageIndex) 
                url = unohelper.systemPathToFileUrl( destFileName + '-'+
                                                     str(pageIndex) + '.' +
                                                     filterParams['Extension'])
                oGraphic.setSourceDocument(page)
                args = (PropertyValue('URL', 0,url , 0),
                        PropertyValue('MediaType', 0, 
                                      filterParams['FilterName'], 0),
                        )
                oGraphic.filter(args) 
                self.convertedFilesList.append(unohelper.fileUrlToSystemPath(url))           
        else:
            if zipMe:
                #Probably an hTML like file 
                #(TODO: take also take care of TEX files)
                aPath, aFileName = os.path.split(destFileName)
                rootFilename = os.path.join(destFileName,aFileName)
            else:
                rootFilename = destFileName 
                
            url = unohelper.systemPathToFileUrl(rootFilename + '.' +
                                                     filterParams['Extension'])
                                                                 
            args = (PropertyValue('FilterName', 0, 
                                   filterParams['FilterName'], 0),)
            sourceDoc.storeToURL(url,args)
            self.convertedFilesList.append(unohelper.fileUrlToSystemPath(url))
            
        sourceDoc.close(True)
        
        if self.autoProcess:
            if zipMe:
                zipFileName = destFileName + '.zip'
                self.zipFiles(self.convertedFilesList, zipFileName)
                self.convertedFilesList = []
                self.convertedFilesList.append(zipFileName)
                destFileName = zipFileName
            else:
                destFileName = unohelper.fileUrlToSystemPath(url)
        else:
            destFileName = unohelper.fileUrlToSystemPath(url)
                
        status = rootFilename + '.' + filterParams['Extension']
        
        return status   
        
    def _getDocumentType(self, aDoc):
        """check the OOo supported service
        """
        theDocType=''
        
        #Order matters as PresentationDocument also supports DrawingDocumen
        # (same for webDocument and TextDocument)
        if aDoc.supportsService('com.sun.star.text.TextDocument'):
            theDocType = 'writer'
        elif aDoc.supportsService(' com.sun.star.sheet.SpreadsheetDocument'):
            theDocType = 'calc'
        elif aDoc.supportsService('com.sun.star.presentation.PresentationDocument'):
            theDocType = 'impress'
        elif aDoc.supportsService('com.sun.star.drawing.DrawingDocument'):
            theDocType = 'draw' 
        
        return theDocType

            
    def zipFiles(self, theList, targetFile):
    
        """ Zip a file list"""
    
        pref_enc = locale.getpreferredencoding()
        theZipFile = zipfile.ZipFile(targetFile,
                                'w',
                                zipfile.ZIP_DEFLATED)
        for aFile in theList:
            if os.path.isfile(aFile):
                (filepath, filename) = os.path.split(aFile)
                theZipFile.write(aFile,filename.encode(pref_enc))
                os.remove(aFile)
            else:
            #Zip directory
                (base,dummy) = os.path.split(targetFile)
                #Caution : this is not recusrsive
                for dirFile in os.listdir(aFile):
                    archiveName = os.path.join(aFile[len(base)+1:], dirFile)
                    fileToZip = os.path.join(aFile, dirFile)
                    theZipFile.write(fileToZip ,archiveName.encode(pref_enc))
                shutil.rmtree(aFile)

        theZipFile.close()
        
        return                           


def testMe():
    
    theSourceFile="/home/lgodard/dvlpt/Manex/Manex/Manex/Manex BRIT AIR partie A/A.00.00.doc"
    #please note, NO extension
    theTargetFile="/home/lgodard/dvlpt/Manex/Manex/Manex/sxw/Manex BRIT AIR partie A/A.00.00" 
    theFormat = "PDF"
    sendTo = "lgodard@indesko.com"
    
    myConverter = OOoConv ()
    isOk = myConverter.export(theSourceFile,theTargetFile,theFormat)
    
    #if isOk == 'ok':
        #print "Sending mail with attachments " + str(myConverter.convertedFilesList)
        #processMail(sendTo, myConverter.convertedFilesList)
        #print "mail sent"
    #else:
    #    print isOk

    return        
        
if __name__ == '__main__':                
    #run it for testing   
    # need OOo runing in listen mode
    #'./soffice "-accept=socket,host=localhost,port=2002;urp;"'     
    testMe()