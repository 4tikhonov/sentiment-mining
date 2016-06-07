#!/usr/bin/python
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

