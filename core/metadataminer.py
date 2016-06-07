#!/usr/bin/python
# Copyright (C) 2016 International Institute of Social History.
# @author Vyacheslav Tykhonov <vty@iisg.nl>
#
# This program is free software: you can redistribute it and/or  modify
# it under the terms of the GNU Affero General Public License, version 3,
# as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# As a special exception, the copyright holders give permission to link the
# code of portions of this program with the OpenSSL library under certain
# conditions as described in each individual source file and distribute
# linked combinations including the program with the OpenSSL library. You
# must comply with the GNU Affero General Public License in all respects
# for all of the code used other than as permitted herein. If you modify
# file(s) with this exception, you may extend this exception to your
# version of the file(s), but you are not obligated to do so. If you do not
# wish to do so, delete this exception statement from your version. If you
# delete this exception statement from all source files in the program,
# then also delete it in the license file.
import sys
import json
import os
import urllib2
import re
from xmlprocessor import *
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../clioinfra.js/modules')))
from cliocore.configutils import Configuration, Utils, DataFilter
from storage import data2store, readdata

def parse_metadata(stringmeta):
    metadata = {}
    titles = {}
    pages = {}
    contents = stringmeta.split('</didl:Component>')

    for item in contents:
        result = re.findall(r'<\S+\:(\w+).*?>(.+?)<\/\w+', item, re.MULTILINE)
	#print item
	j = 0
	metadata = {}
        for i in result:
	    j+=1
            metadata[i[0]] = i[1]
	if 'recordRights' in metadata:
	    titles = metadata
	else:
	    pages[j] = metadata
    return (titles, pages)

def request_kbmetadata(pid):
    metadata = ''
    url = "%s?verb=GetRecord&identifier=%s&metadataPrefix=didl" % (c.config['oaiservice'], pid)
    xml_string = request_xml(url)
    (title, metadata) = parse_metadata(xml_string)
    return title

def request_kbmetadata_fromweb(c, pid):
    metadata = {}
    url = "%s/view?coll=ddd&identifier=%s" % (c.config['delpher'], pid)

    web_string = request_xml(url)
    web = re.sub('\n|\r', ' ', web_string)
    info = web.split('</dd>')
    for item in info:
        items = re.findall(r'<dt>(.+?)<\/dt>.+<li title\=\"(.+?)\"', item, re.MULTILINE)
	if len(items) > 0:
	    metadata[items[0][0]] = items[0][1]
    return metadata
