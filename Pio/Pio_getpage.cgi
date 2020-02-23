#!/usr/local/bin/python

import os, sys, Pio_getpage


ipaddr = os.environ['REMOTE_ADDR'] 
qrystring = os.environ['QUERY_STRING']
webpath = os.environ['DOCUMENT_ROOT']
requestedurl = os.environ['REQUEST_URI']
levelcount = 0
uploadfiles = {}

##new
requestmethod = os.environ['REQUEST_METHOD']

if 	requestmethod.upper() == 'POST':		#post is the only way to upload files
	qrystring = ''
	import cgi
	form = cgi.FieldStorage()
	for name in form.keys():		#this creates the qrystring anew from the form...regardless of post/get method after clearing piopass
		try:
			if qrystring == '':
				if form[name].filename == None:
					qrystring = "%s=%s" % (name, form[name].value)
				else:
					qrystring = "%s=%s" % (name, form[name].filename)
					if form[name].filename != '' and form[name].value != '':
						uploadfiles[name] = [form[name].filename, form[name].value]		#dict entry for field with filename/file tuple -- {fieldname:[filename, file]}
			else:
				if form[name].filename == None:
					qrystring = "%s&%s=%s" % (qrystring, name, form[name].value)
				else:
					qrystring = "%s&%s=%s" % (qrystring, name, form[name].filename)
					if form[name].filename != '' and form[name].value != '':
						uploadfiles[name] = [form[name].filename, form[name].value]		#dict entry for field with filename/file tuple 
		except AttributeError:	#for chkbox and slctmulti
			n = 0
			for i in form[name]:
				mini_value = form[name][n].value
				if qrystring == '':
					qrystring = "%s=%s" % (name, mini_value)
				else:
					qrystring = "%s&%s=%s" % (qrystring, name, mini_value)
				n = n + 1
##	print os.environ
	os.environ['QUERY_STRING'] =  qrystring
	os.environ['REQUEST_METHOD'] =  'GET'		##I really wish I understood how post worked. 
##	print os.environ

if qrystring.find('piobinary=') == -1:
	print "Content-type: text/html\n"	#necessary cgi line

#print "Content-type: text/html\n"	#necessary cgi line
file, mimetype = Pio_getpage.getpage(qrystring, ipaddr, levelcount, webpath, requestedurl, uploadfiles)

sys.stdout.write(mimetype)
sys.stdout.write(file)

##print '<p>' + str(os.environ)
##print 'uploadfiles: %s' % (uploadfiles)
