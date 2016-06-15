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
import os
import urllib2
import re
from werkzeug import secure_filename
from nltk import tokenize
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../clioinfra.js/modules')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../clioinfra.js')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
from storage import data2store, readdata
from core.configutils import Configuration
from core.metadataminer import request_kbmetadata, request_kbmetadata_fromweb
from core.xmlprocessor import *

def get_full_text(c, pid):
    if pid:
        ocrurl = "%s?identifier=%s&coll=ddd&operation=download" % (c.config['ocrservice'], pid)
        response = urllib2.urlopen(ocrurl)
        text = response.read()
 	return text
    return ''

def kb_explorer(c, query, projectname, dbname):
    if query:
        squery = query
        squery = re.sub(r'\s+', ' and ', query)
    print query
    url = "%s?version=1.2&maximumRecords=1000&operation=searchRetrieve&startRecord=1&recordSchema=dcx&x-collection=DDD_artikel&query=%s AND spatial =\"Regionaal/lokaal\"" % (c.config['jsruservice'], squery)
    try:
        xml_string = request_xml(url)
    except:
	xml_string = ''
    items = make_dict_from_tree(xml.etree.ElementTree.fromstring(xml_string))
    records = convertrecords(items)
    for item in records:
        pid = re.search(r'urn\=((\S+)\:mpeg21\:\S+)\:', item['identifier'])
        if pid:
            PID = pid.group(2)
            fullPID = pid.group(1)
        ocrurl = "%s?identifier=%s&coll=ddd&operation=download" % (c.config['ocrservice'], fullPID)
        scanurl = "%s/view?coll=ddd&identifier=%s" % (c.config['delpher'], fullPID)

	fulltext = get_full_text(c, fullPID)
	item['keyword'] = query
	item['pid'] = fullPID

	item['fulltext'] = fulltext
	if 'date' in item:
	    item['publishdate'] = item['date']
	    year = re.match(r'(\d{4})\/', item['publishdate'])
	    if year.group(0):
		item['year'] = int(year.group(1)) 
	item['projectname'] = projectname

	# Find newspaper metadata
	uID = re.match(r"(.+)\:", fullPID)
	if uID.group(0):
	    uPID = "DDD:%s" % uID.group(1)
            #title = request_kbmetadata(uPID)
	    title = request_kbmetadata_fromweb(c, uID.group(1))

            for titleitem in title:
                titlename = "kb%s" % titleitem
                item[titlename] = title[titleitem]
	data2store(dbname, item)
    return records

project = "sentiments"
project = "cruyff"
prefix = "kbs"
kbdata = "%s%s" % (prefix, project)
data = readdata('projects', 'uri', project)
c = Configuration()
for item in data:
    projectname = item['uri']
    print projectname
    keywords = item['keywords'].split('\r\n')
    for keyword in keywords:
	if keyword:
	    print keyword
	    info = kb_explorer(c, keyword, projectname, kbdata)	
	
