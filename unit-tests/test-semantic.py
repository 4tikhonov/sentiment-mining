#!/usr/bin/python

import sys
import os
import urllib2
import re
from werkzeug import secure_filename
from nltk import tokenize
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../clioinfra.js/modules')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../clioinfra.js')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
from core.xmlprocessor import *
from core.donlp import *
from core.configutils import Configuration

def get_full_text(c, pid):
    if pid:
        ocrurl = "%s?identifier=%s&coll=ddd&operation=download" % (c.config['ocrservice'], pid)
        response = urllib2.urlopen(ocrurl)
        text = response.read()
        return text
    return ''

c = Configuration()
fulltext = get_full_text(c, c.config['fulltestpid'])
if fulltext:
    (sem, res) = minesentiments(fulltext, c.config['testquery'])
    print sem
