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
from storage import data2store, readdata
from core.metadataminer import request_kbmetadata, request_kbmetadata_fromweb
from core.configutils import Configuration

c = Configuration()
uPID = c.config['testpid'] 
#title = request_kbmetadata(uPID)
title = request_kbmetadata_fromweb(uPID)
print str(title)
