#!/usr/bin/python

import sys
import os
import urllib2
import re
from pymongo import MongoClient
from werkzeug import secure_filename
from nltk import tokenize
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../clioinfra.js/modules')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from storage import data2store, readdata
from core.xmlprocessor import *

pid = "ddd:010285299:mpeg21:a0213"
dbname = "kbstorage"

data = readdata(dbname, 'pid', pid)
for item in data:
    item['fulltext'] = ''
    main = item

client = MongoClient()
db = client.get_database(dbname)
collection = db.data
pipe = [ { '$group': { '_id': { 'publisher': "$publisher", 'year': "$year"}, 'observations': { '$sum': 1 } } } ]
result = db.data.aggregate(pipeline=pipe)
for x in result:
    print "%s %s" % (str(x['_id']), x['observations'])
