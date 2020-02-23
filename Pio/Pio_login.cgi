#!/usr/local/bin/python

import os, Pio_getpage, cgi, Pio_auth, sys

def main():
	page = ''
	piouser = ''
	piopass = ''
	loginpage = 'Pio_login.html'
	loginerror = 'Failed to login'
	
	piopassnew = ''
	piopassnew2 = ''
	passwordupdate_msg = ''
	passwordupdate_error = ''
	
	ipaddr = os.environ['REMOTE_ADDR'] 
#	qrystring = os.environ['QUERY_STRING']		#usable only with the get method.
	qrystring = ''
	webpath = os.environ['DOCUMENT_ROOT']
	requestedurl = os.environ['REQUEST_URI']
	requestmethod = os.environ['REQUEST_METHOD']
	levelcount = 0
	uploadfiles = {}
	
	form = cgi.FieldStorage()
	if form.has_key("page"):	# consider different 'page' strings =>or form.has_key("Page") or form.has_key("PAGE"):	
		page = form["page"].value
	if form.has_key("loginpage"):	
		loginpage = form["loginpage"].value
	
	if form.has_key("piouser"):	
		piouser = form["piouser"].value
	if form.has_key("piopass"):	
		piopass = form["piopass"].value
		form['piopass'].value = ''		#blank the password so it doesn't go onto Pio_getpage.
	
	if form.has_key("piopassnew"):	
		piopassnew = form["piopassnew"].value
		form['piopassnew'].value = ''		#blank the password so it doesn't go onto Pio_getpage.
	if form.has_key("piopassnew2"):	
		piopassnew2 = form["piopassnew2"].value
		form['piopassnew2'].value = ''		#blank the password so it doesn't go onto Pio_getpage.
	
	#make call to authentication program
	piosid, loginerror = Pio_auth.login(piouser, piopass, ipaddr)
	if loginerror == '':
		qrystring = 'piosid=%s' % (piosid)
		if piopassnew != '' and piopassnew2 != '':		#if piopassnew and new2 exist change them.
			passwordupdate_msg, passwordupdate_err = Pio_auth.updatepass(piouser, piopass, piopassnew, piopassnew2, ipaddr, piosid)
			if passwordupdate_error == '':
				qrystring = qrystring + '&passwordupdate_msg=%s' % (passwordupdate_msg)
				
			else:		#for failure on password change go back to loginpage (all password change pages should be their own login pages)
				form['page'].value = loginpage
				qrystring = qrystring + '&passwordupdate_msg=%s' % (passwordupdate_msg)
			
	else:
		form['page'].value = loginpage
		qrystring = 'loginerror=%s' % (loginerror)
		
	
	for name in form.keys():		#this creates the qrystring anew from the form...regardless of post/get method after clearing piopass
		try:
			if qrystring == '':
				if form[name].filename == None:
					qrystring = "%s=%s" % (name, form[name].value)
				else:
					qrystring = "%s=%s" % (name, form[name].filename)
					if form[name].filename != '' and form[name].value != '':
						uploadfiles[name] = [form[name].filename, form[name].value]		#dict entry for field with filename/file tuple
			else:
				if form[name].filename == None:
					qrystring = "%s&%s=%s" % (qrystring, name, form[name].value)
				else:
					qrystring = "%s&%s=%s" % (qrystring, name, form[name].filename)
					if form[name].filename != '' and form[name].value != '':
						uploadfiles[name] = [form[name].filename, form[name].value]		#dict entry for field with filename/file tuple  --{fieldname:[filename, file]}
		except AttributeError:	#for chkbox and slctmulti
			n = 0
			for i in form[name]:
				mini_value = form[name][n].value
				if qrystring == '':
					qrystring = "%s=%s" % (name, mini_value)
				else:
					qrystring = "%s&%s=%s" % (qrystring, name, mini_value)
				n = n + 1
	
#	print os.environ		## print environ before change
	
	os.environ['QUERY_STRING'] =  qrystring
	os.environ['REQUEST_METHOD'] =  'GET'		##I really wish I understood how post worked. 
	
#	print os.environ			##print environ after change
##	print qrystring
	
	if qrystring.find('piobinary=') == -1:
		print "Content-type: text/html\n"	#necessary cgi line
	
#	print str(uploadfiles)		#testing uploadfiles get loaded into pio as pinp
	
	#print "Content-type: text/html\n"	#necessary cgi line
	file, mimetype = Pio_getpage.getpage(qrystring, ipaddr, levelcount, webpath, requestedurl, uploadfiles)
	
	sys.stdout.write(mimetype)
	sys.stdout.write(file)
	
	
#	print qrystring
#	print '<br>' + requestedurl
#	print 'uploadfiles: %s' % (uploadfiles)
	
main()
