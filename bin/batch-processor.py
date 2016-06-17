#!/usr/bin/python

from pymongo import MongoClient
import sys
import os
import urllib2
import re
import numpy
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../clioinfra.js/modules')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../clioinfra.js')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
from werkzeug import secure_filename
from nltk import tokenize
from core.xmlprocessor import *
from core.donlp import *

projectname = "sentiments"
projectname = "cruyff"

dbname = "source%s" % projectname
resultname = "%s%s" % (projectname, 'result')
trackdb = "%s%s" % (projectname, 'track')

client = MongoClient()
db = client.get_database(dbname)
dbresult = client.get_database(resultname)
dbresult.data.drop()
dbtrack = client.get_database(trackdb)
dbtrack.data.drop()

collection = db.data
#q = {"keyword" : "industrialisatie"}
#result = db.data.find(q).limit(50)

q = {"projectname" : projectname}
result = db.data.find(q)
newspapers = {}
aggregated = []
for item in result:
    query = item['keyword']
    print query
    fulltext = item['fulltext']

    data = {}
    if fulltext:
        (sem, sentences) = minesentiments(fulltext, query)
	if sem:
	    if 'kbKrantentitel' in item:
	        newspaper = item['kbKrantentitel']
	    else:
	 	newspaper = item['source']
	    year = item['year']
	    if year:
		newspaper+=" [%s]" % str(year)
	    if 'kbPlaats van uitgave' in item:
	        location = item['kbPlaats van uitgave']
	    else:
		location = 'NA'
	    url = "\nhttp://www.delpher.nl/nl/kranten/view?coll=ddd&identifier=%s" % item['pid']
#	    print "%s\n%s %s %s\n" % (url, newspaper, year, location)
	    pol = []
	    subj = []
	    for id in sem:
		w = sem[id].split(',') 
		pol.append(float(w[0]))
		subj.append(float(w[1]))
		
	    # {8: '0.2,0.35', 9: '0.183333333333,0.725', 24: '0.6,0.95'} 
	    pol.sort()
	    subj.sort()

	    data['kbtitle'] = newspaper
	    data['kbspatial'] = location
	    data['url'] = url
	    data['semantic'] = str(sem)
	    data['year'] = year
	    data['sentences'] = str(sentences)
	    if pol:
	        data['pol'] = pol
	        data['subj'] = subj

	    if data['pol']:
	        aggregated.append(data)
                newspapers[newspaper] = data

# aggregation
pol = {}
subj = {}
finalpol = {}
finalsubj = {}
for kbtitle in newspapers:
    polaggr = []
    subjaggr = []
    for data in aggregated:
#	print "%s %s" % (kbtitle, str(data['pol']))
	if kbtitle == data['kbtitle']:
	    #data['sentiment'] = data['meanpol']
	    if kbtitle in finalpol:
		curpol = finalpol[kbtitle]
		for politem in data['pol']:
	            curpol.append(politem)
		    finalpol[kbtitle] = curpol
		for subjitem in data['subj']:
		    finalsubj[kbtitle].append(subjitem)
	    else:
		# New newspaper title
		curpol = []
		cursubj = []
		for politem in data['pol']:
		    curpol.append(politem)
		finalpol[kbtitle] = curpol

		for subjitem in data['subj']:
		    cursubj.append(subjitem)
		finalsubj[kbtitle] = cursubj
	   
for data in aggregated:
    kbtitle = data['kbtitle']
    if kbtitle in finalpol:
	print "%s %s" % (str(finalpol[kbtitle]), kbtitle)
	data['kbtitle'] = re.sub(r'\s+\[\d{4}\]', '', data['kbtitle'])
        data['polarity'] = "%.3f" % numpy.average(finalpol[kbtitle])
        data['subjectivity'] = "%.3f" % numpy.average(finalsubj[kbtitle])
	track = {}
	track['kbtitle'] = data['kbtitle']
	track['spatial'] = data['kbspatial']
	track['year'] = data['year']
	track['subjvector'] = finalsubj[kbtitle]
	track['polvector'] = finalpol[kbtitle]

        result = dbresult.data.insert(data)
	trackrecord = dbtrack.data.insert(track)
