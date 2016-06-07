#!/usr/bin/python
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
