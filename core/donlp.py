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
import pattern.nl
import json
import urllib2
import urllib
import glob
import csv
import sys
import psycopg2
import psycopg2.extras
import pprint
import getopt
import ConfigParser
import HTMLParser
from subprocess import Popen, PIPE, STDOUT
import simplejson
import re
import os
from werkzeug import secure_filename
from nltk import tokenize

def discourse(item, query):
    bolditem = ''
    words = query.split()
    for keyword in words:
        if bolditem:
            item = bolditem
        matchstring = r"\W(" + re.escape(keyword) + ")"
        pid = re.search(matchstring, item, re.IGNORECASE)
        if pid:
            replacepattern = r"(" + keyword + "\S*)"
            bolditem = re.sub(replacepattern, r"<b>\1</b>", item, flags=re.IGNORECASE)
    return bolditem

def minesentiments(text, query):
    topicline = query
    important = {}
    importantlines = {}
    sentence = {}
    resultline = ''
    semanticline = ''
    ranks = {}
    id = 0
    lines = re.split(r'(?<=[\n.])(?<!\d.)\s', text)
    for item in lines:
        try:
            sentense = tokenize.sent_tokenize(item)
            for s in sentense:
                id+=1
                try:
                    result = pattern.nl.sentiment(s)
                    polarity = str(result[0])
                    subjectivity = str(result[1])
                    boldline = discourse(str(s), query)
                    if boldline:
			rank = "%s,%s" % (polarity, subjectivity)
			if rank != "0.0,0.0":
#			    print "SSS \t[%s] Polarity %s Subjectivity %s\n\t%s\n" % (id, polarity, subjectivity, boldline)
			    sentence[id] = boldline
			    important[id] = rank
                except:
                    resultline+= "None %s<br>" % s
        except:
            skip = 'yes'

    if important:
        active = {}
        diff = 5
        for id in sorted(importantlines, key=lambda i: int(i)):
            for i in range(id-diff, id + diff):
                if i not in active:
                    keywordline = ''
                    if i in importantlines:
                        keywordline = importantlines[i]
                    else:
                        if i in ranks:
                            keywordline = ranks[i]
                    if keywordline:
                        semanticline+="%s" % (keywordline)
                active[i] = 'yes'
        return (important, sentence)
    else:
        return ('', '')

