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
# See ``COPYING`` for more information
#
# $Id$
from email import message_from_string, Message
from email import base64MIME
import os.path
import mimetypes
import smtplib

defaultSMTPaddress = 'localhost'
encoding = 'ISO-8859-15'

def processMail (toAddress, attachList = [],
           SendingParameters = {} ):

    #default parameters
    if not SendingParameters.has_key('messageBody'):        
            SendingParameters['messageBody'] = "Please find the transformed file you requested...\n"    
    if not SendingParameters.has_key('messageSubject'):        
            SendingParameters['messageSubject'] = "pyOOoConv : Conversion Result"
    if not SendingParameters.has_key('SMTPaddress'):        
            SendingParameters['SMTPaddress'] = defaultSMTPaddress
    if not SendingParameters.has_key('SMTPport'):        
            SendingParameters['SMTPport'] = '25'
    if not SendingParameters.has_key('SMTPhost'):        
            SendingParameters['SMTPhost'] = 'localhost'
    if not SendingParameters.has_key('from'):        
            SendingParameters['from'] = 'pyOOoConv <lgodard@indesko.com>'
    if not SendingParameters.has_key('encoding'):        
            SendingParameters['encoding'] =  'ISO-8859-15'
     
    
    message = Message.Message()
    
    #message['Content-type'] = 'text/plain; charset=iso-8859-15'
    message['Content-transfer-encoding'] = '7bit'    
    message ['From'] = SendingParameters['from']
    message ['To'] = toAddress
    message ['Subject'] = SendingParameters['messageSubject'].encode( SendingParameters['encoding'])

    message['User-Agent'] = 'Nuxeo/InDesko pyOOoConv'
    message['Content-type'] = 'Multipart/mixed; boundary=---BOUNDARY---'
    message['MIME-version'] = '1.0'
    message.preamble="Mime message\n"
    message.epilogue=""

    
    Body=Message.Message()
    Body["Content-type"]="text/plain; charset=%s" % ( SendingParameters['encoding'])
    Body["Content-transfer-encoding"]="7bit"
    Body.set_payload(SendingParameters['messageBody'].encode( SendingParameters['encoding']))
    message.attach(Body)


    for aFile in attachList:
        part_file = Message.Message()
        dummy, fileName = os.path.split(aFile)
        file=open(aFile,"r")
        data = file.read()
        file.close()
        #TODO: use first bytes to identify mimetype - See CPSMailAccess
        guessedMimeType, dummy = mimetypes.guess_type(aFile,False)
                
        part_file['content-disposition'] = 'attachment; filename= "%s"'\
                                            % fileName
        part_file['Content-transfer-encoding'] = 'base64'
        data = base64MIME.encode(data)
        data = data.replace('\n', '')
        part_file['Content-type'] = '%s; name="%s"' % (guessedMimeType,
                                                        fileName) 
        part_file.set_payload(data)

        message.attach(part_file)

    server=smtplib.SMTP( SendingParameters['SMTPaddress'],
                         SendingParameters['SMTPport'],
                         SendingParameters['SMTPhost'])
    server.sendmail(SendingParameters['from'], toAddress, message.as_string())
    server.quit()
    
    print SendingParameters
    
    return
    

    
    
if __name__ == '__main__':                
    processMail("lgodard@indesko.com",['/home/lgodard/document.sxw'],
                {'messageSubject': "a subject",'messageBody':"the message body" })
