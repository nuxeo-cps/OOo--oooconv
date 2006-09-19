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

import xmlrpclib

s = xmlrpclib.Server('http://localhost:11117/')
result = s.stop()
print result