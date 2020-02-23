import cgi, string, re, Pio_pageproc, sys, Pio_processpobj, Pio_processpval, Pio_pif, Pio_auth, Pio_prefs, os, MySQLdb


def setmime_getbinary(piobinary, outfile):
	mimetype = "Content-type: text/html\n\n"	#necessary cgi line - if piobinary value = ''
	
	if piobinary != "":
		mimetype = piobinary.replace('\n', '')
		if mimetype[0:14] != 'Content-type: ':
			mimetype = 'Content-type: ' + mimetype
		mimetype = mimetype + '\n\n'
		
		#new pbinary tag <pbinary name="#blobname#">#theblob#</pbinary>
		pb = outfile.find('<pbinary')
		if pb != -1:
			pba = outfile.find('>', pb+8)
			if pba != -1:
				pbinarytag = outfile[pb:pba+1]
#				print pbinarytag
				pb1 = outfile.find('</pbinary>', pba+1)
				if pb1 != -1:
					outfile = outfile[pba+1:pb1]
				else:
					outfile = 'No closing &lt;/pbinary&gt; tag for binary data' + outfile
				
				#append name (content disposition) to mimetype
				n1 = pbinarytag.find('name=')
				if n1 != -1:
					n1 = n1 + 5
					na = pbinarytag.find('"', n1)
					nb = -1
					if na != -1:
						nb = pbinarytag.find('"', na+1)
					if na == -1 or nb == -1:
						outfile = 'no quotes found for binary name'
					else:
						pbinaryname = pbinarytag[na+1:nb]
						contentdisp = 'Content-Disposition:attachment;filename=%s\n\n' % (pbinaryname)
						if mimetype != "Content-type: text/html\n\n":
							mimetype = contentdisp + mimetype
					
				else:
					outfile = 'no name provided for pbinary file  (pbinary name="#blobname#") \n %s' % (pbinarytag)
			else:
				outfile = 'No closing &gt; tag for pbinary tag' + outfile
			
		
	return mimetype, outfile


def processfile(pagename, form, levelcount, webpath, requestedurl, error, prefsdict, uploadfiles, qrystring):
	tail = ''
	try:
		file = open(pagename).read()
	except IOError, e:
		if prefsdict.has_key('pio404'):
			filename404 = prefsdict['pio404']
		else:
			filename404 = ''
		if levelcount == 0:			#error reading in initial file.
			import Pio_404
			if error <> '':
				error = 'Missing "%s" page due to error' % (pagename) + error
			file = Pio_404.file404(webpath, requestedurl, error, filename404)
		else:				#error with include file
			error = 'Include404 Error - Missing "%s"' % (pagename) + error
			if prefsdict.has_key('include404') and prefsdict['include404'].upper() == 'COMMENT':
				file = "<!-- %s -->" % (error)
			else:
				file = error
	
	cgikeys = form.keys()
	
	if prefsdict.has_key('showpinp') and prefsdict["showpinp"].upper() == 'YES':
		showtag = 'yes'
	else:
		showtag = 'no'
	
	pinpdict, pinplist, pinphaspinp_dict, file = Pio_pageproc.getpinp(file, showtag)	# get the input dictionary and list for page
	
	
	#uploadresults are added to the pinpdict here  They get no quotes because like errors they are returns from the program. 
	if uploadfiles != {}:		#uploadfiles look like this: {fieldname:[filename, file]}
		uf = 0
		for i in uploadfiles:
			#uploadfiles.keys()[uf] are pinps that need to update the pinpdict dictionary.  each uploaded file should make/match 
			# 2 pinp.  the pinp where the value is the upload file name and another pinp pinp_file which is the file data.
			#eg.  		<pinp name="uploadfile" default="">		<pinp name="uploadfile_file" default="">

			#only update if filename and file are both not blank.
			uploadpinp_name = uploadfiles.keys()[uf]
			uploadpinpfile_name = uploadfiles.keys()[uf] + '_file'
			uploadpinp_data = uploadfiles[uploadpinp_name][0]
			uploadpinpfile_data = uploadfiles[uploadpinp_name][1]
			
			pinpdict[uploadpinp_name] = uploadpinp_data
			if uploadpinpfile_data != '':
				pinpdict[uploadpinpfile_name] = uploadpinpfile_data
			else:
				pinpdict[uploadpinpfile_name] = 'NO DATA'
				
			uf = uf + 1
	
	
	###tail = tail + '<br> here is pinpdict and pinplist from Pio_pageproc.getpinp(file) => ' + str(pinpdict), str(pinplist)
	# use cgi key to replace the pinp dictionary with defaults with cgi values.
	n = 0
	for a in cgikeys:
	###tail = tail + '<br> here are the values from the cgi input => ' + cgikeys[n]
		if cgikeys[n].upper() == "PIOPASS":		#don't put in piopass into the dictionary for security reasons.
			n = n + 1
		else:
	###		tail = tail + '<br> cgikey value => ' + str(form[cgikeys[n]].value) ##not the Page values
				#should I allow cgi form data to generate a pinp?...it could open a hole where outside code gets executed on the system....a pinp could be a pobj.
			try:
				pinpdict[cgikeys[n]] = form[cgikeys[n]].value	#update pinp dictionary with input values
				pinpdict[cgikeys[n] + '.quote'] = '"%s"' % (str(form[cgikeys[n]].value))	#update pinp dictionary with quoted input values
				n = n + 1
			except AttributeError:		#this is where a list is happening for a cgikey eg. selectmulti, checkbox
				fcdlist = cgi.FormContentDict()[cgikeys[n]]
				fn = 0
				fcdlstr = ''
				for a in fcdlist:
					if fn == 0:
						fcdlstr = fcdlist[fn]
						fcdlstrquote = '"%s"' % (fcdlist[fn])
						pinpdict[cgikeys[n] + '.' + str(fn)] = fcdlist[fn]	#update pinp dictionary with input values
					else:
						fcdlstr = fcdlstr + ', ' + fcdlist[fn]
						fcdlstrquote = fcdlstrquote + ', "%s"' % (fcdlist[fn])
						pinpdict[cgikeys[n] + '.' + str(fn)] = fcdlist[fn]	#update pinp dictionary with input values
					fn = fn + 1
				pinpdict[cgikeys[n]] = fcdlstr
				pinpdict[cgikeys[n] + '.quote'] = fcdlstrquote
	##			tail = tail + '<br>' + fcdlstr + ':' + fcdlstrquote
				n = n + 1		
	#process pinphaspinp_list
	if pinphaspinp_dict != {}:
		n = 0
		for i in pinphaspinp_dict.keys():
			n1  = 0
			pinphaspinp = pinphaspinp_dict.keys()[n]
			for j in pinphaspinp_dict[pinphaspinp]:
				rplstring = '#replacepinp.%s#' % (str(pinphaspinp_dict[pinphaspinp][n1] ) )
				pinpdict[pinphaspinp] = string.replace(pinpdict[pinphaspinp], rplstring, str(pinpdict[pinphaspinp_dict[pinphaspinp][n1] ]) )
				pinpdict[pinphaspinp+'.quote'] = string.replace(pinpdict[pinphaspinp], rplstring, str(pinpdict[pinphaspinp_dict[pinphaspinp][n1] ]) )
				n1 = n1 + 1
			n = n + 1
	
	#add qrystring as a pinp object itself for calls to includes, excluding the page:
	if string.upper(qrystring)[0:4] == 'PAGE':			#page is first part of qrystring
		rempagen = 0
	else:
		rempagen = string.find(string.upper(qrystring), '&PAGE=', 0)
	rempagen1 = string.find(qrystring, '&', rempagen + 1)
	if rempagen1 == -1:				#page is last part of qrystring with no following &
		rempagen1 = len(qrystring)
	pageless_qrystring = qrystring[0:rempagen] + qrystring[rempagen1:len(qrystring)]
	pinpdict['pio_qrystring'] = pageless_qrystring
	
	
	pinpdictlist = pinpdict.keys()
	###show the dictionary
	##tail = tail + '<p>cgikeys:' + str(cgikeys)
	##tail = tail + '<p>pinpdict:' + str(pinpdict)
	##tail = tail + '<p>pinplist:' + str(pinplist)
	##tail = tail + '<p>pinpdictlist:' + str(pinpdictlist)
	
	# update #pinp.value# elements in the html file to use real values from pinp dictionary elements
	n = 0
	for aa in pinpdictlist:
		rplstring = '#pinp.%s#' % (str(pinpdictlist[n]))
		file = string.replace(file, rplstring, str(pinpdict[pinpdictlist[n]]))
		n = n + 1
#	file = re.sub('#pinp.*#', str(pinpdict), file)
	file = string.replace(file, '#pinp.*#', str(pinpdict))		#this tag "#pinp.*#"  exists just to get show an easy list of the pinps available in the browser
	
	if string.find(file, '<pmath') <> -1:		#process pmath statements after getting all the pinp values loaded to file
		file = Pio_pif.processpmath(file, 'begin')		#the begin value is used to process pinp, later we do pmaths again after pvals are processed.
	file = Pio_pif.processpif(file)		#process pif statements after getting all the pinp values loaded to file
	file = file + tail
	
	if prefsdict.has_key('showppref') and prefsdict["showppref"].upper() == 'YES':
		showtag = 'yes'
	else:
		showtag = 'no'
	
	pprefdict, ppreflist, file = Pio_pageproc.getppref(file, showtag)		#update the prefsdict after processing pinp and pif's
	pd =  0
	for a in ppreflist:
		prefsdict[ppreflist[pd]] = pprefdict[ppreflist[pd]]
		pd = pd + 1
	
	return file, prefsdict


def getpage(qrystring, ipaddr, levelcount, webpath, requestedurl, uploadfiles):
	sys.stderr = sys.stdout
	err = ''
	pioclass = ''
	piouser = ''
	piosiderr = ''
	tmstamp = 0
	pref_pobjerror = ''
	pref_pobjautherror = ''
	pref_piosiderror = ''
	piosiderrcount = 0
	tail = ''		# I've started using this as debug to throw stuff at the bottom of the html for testing as well as where to put errors.
	nose = ''		#this is for putting errors at the top
	uploadresults = {}		#if there is no valid piosid used then there can be no uploads and hence no results to load into pinps
	
	prefsdict = Pio_prefs.gimmedict()
	form = cgi.FieldStorage()
	
#	if os.environ.has_key('HTTP_USER_AGENT'):		#I think apache deals with this, so I remmed it.
	browser = os.environ['HTTP_USER_AGENT']
#	else:
#		browser = 'unknown browser'
	
	sqluser = Pio_prefs.gimme('sqluser')
	sqldb = Pio_prefs.gimme('sqldb')
	sqlhost = Pio_prefs.gimme('sqlhost')
	if sqlhost == "":
		sqlhost = "127.0.0.1"
	
	db = MySQLdb.connect(db=sqldb, user=sqluser, host=sqlhost)
	mysqlc = db.cursor()
	
	if string.upper(prefsdict['piolog']) == 'YES' or string.upper(prefsdict['piolog']) == 'Y':
		import Pio_log
		Pio_log.addentry(ipaddr, browser, requestedurl, qrystring, prefsdict['sqluser'], prefsdict['sqldb'], prefsdict['sqlhost'], mysqlc)
	
	###debug lines
	###tail = str(cgi.FormContent())
	###tail = tail + '<br>' + str(os.environ)
	###print 'form:  <br><br>%s<br><br><br>qrystring:<br><br>%s' % (form, qrystring)
	###print '<br>IP Address: %s <br><br>' % (ipaddr)
	
	if form.has_key("page") :	
		page = form["page"].value
	elif form.has_key("piopage"):
		page = form["page"].value
	else:
		err = err + '<br>Missing Page Key in CGI'
		page = ''
	if form.has_key("piosid"):
		piosid = form["piosid"].value
		newsid, piosiderr, tmstamp, pioclass, piouser = Pio_auth.pioauth(piosid, ipaddr, mysqlc)		
		# authorize the session id...if it fails, show the error, but later pobjauths will still run with a blank pioclass (if allowed in database file pioclasspobj).
		# pioauth returns a blank pioclass if the authorization fails (tmstamp/ipaddr/piosid)
		piosid = newsid
		form["piosid"].value = newsid
		##if piosiderr <> '':			#rolled into error testing in while statement below.
		##	err = err + '<br>' + piosiderr
		##tail = tail + '<br>newsid:%s, piosiderr:%s, tmstamp:%s, pioclass:%s, piouser:%s' % (newsid, piosiderr, tmstamp, pioclass, piouser)
		##tail = tail + '<br>ipaddr:' + ipaddr
		
#		#process uploaded files here inside the piosid process...only authorized users allowed to upload files. 
#		#Pio_staticclient takes the uploadfiles dict, with sharedfolder(removed..needs to be rewritten)
#		# and shoots them to the little socket server Pio_static.py which loads them into sharefolder/file.
#		###print uploadfiles			#uploadfiles look like this: {fieldname:[filename, file]}
#		if piosiderr == '' and uploadfiles <> {}:		#no errors with piosid processing, load uploadfiles to the Pio_static process.
#			import Pio_staticclient
#			sharedfolder ==''		#shared folder needs to be removed on rewrite of binary uploads to check user/dict file for auth.	
#			if sharedfolder == '':		#no sharedfolder data returned by pioauth
#				sharedfolder = prefsdict['uploadpath']
#			#upload results have to be passed onto getpage.processfile where they are added to the pinpdict.
#			uploadresults = Pio_staticclient.processupload(uploadfiles, sharedfolder, "Pio_getpage")	
	
	
	p1 = string.find(page, '.')
	if p1 == -1:
		pagename = '%s.html' % (page)		#add .html if file is just a name. 
	else:
		pagename = page		#allows using any type of page for processing (.htm, .txt etc.)
	
	# tagdict keys are id, input, vars, name, startrec, rowcount
	# process the pobj tags in sequence, eliminating them as you go.
	# uses the method Pio_processpval.dorcds (process records) to work with records, vars, rowcount#s and fixes the file.
	
	
	file, prefsdict = processfile(pagename, form, levelcount, webpath, requestedurl, err, prefsdict, uploadfiles, qrystring)
	
	fn = string.find(file, '<pobj', 0)
	tailn = 0
	newfile = 'yes'
	
	while fn <> -1:	# check that a pobj tag was found before doing pobj tag stuff.
		
		if newfile == 'yes':
			if prefsdict.has_key('piosiderror'):
				pref_piosiderror = prefsdict['piosiderror']
			if prefsdict.has_key('pobjerror'):
				pref_pobjerror = prefsdict['pobjerror']
			if prefsdict.has_key('pobjautherror'):
				pref_pobjautherror = prefsdict['pobjautherror']
			newfile = 'no'
		
		pobjid, tagdict, tagdata, pobjerr = Pio_pageproc.getpobjtag(file)
		#right now I'm doing nothing with pobjerr...I could add in a generic page error.
		
		vardict, varlist = Pio_pageproc.parseobjvars(tagdict['vars'])
		#add rownumber to vardict and varlist as pio_row
		vardict['pio_row'] = ''
		varlist.append('pio_row')
		#end add or rownumber var
		rowcount = tagdict['rowcount']
		startrec = tagdict['startrec']
		
		#execute pobjtag program using input statement.
		#eg do qry program, and qrygetimg program.
		#get records
		records, rcdserr = (), ''
		pobjpgm = tagdict['name']
		pobjstmt = tagdict['input']
		
##		print 'pioclass: %s<br> pobjid: %s<br> pagename:%s<br> pobjstmt: %s<br>' % (pioclass, pobjid, pagename, pobjstmt)
##		print '***pobjstmt: ' + pobjstmt
		if pobjstmt != '':
			pobjauth, pobjautherr, origtblauth, pobjauthl =  Pio_auth.pobjauth(pioclass, pobjid, pagename, pobjstmt, mysqlc)
		else:
			pobjauth= ''
			pobjautherr = ''
			origtblauth = ''
			pobjauthl = ()
		## note: pioadmin is generically authorized to all pobj, so tables are not authorized for pioadmin
	##	tail = tail + '<br>tblauth %s --pobjauthl %s  pobjid: %s %s' % (origtblauth, pobjauthl, pobjid, str(pobjauth))
		records, rcdserr, rcdsautherr, nextrecnmbr = Pio_processpobj.pgm(pobjpgm, pobjstmt, startrec, rowcount, levelcount, ipaddr, webpath, requestedurl, pobjauth, piouser, prefsdict, mysqlc)
		#I'm adding row numbers per row in the below code (1st row starts at 0 )
		n = 0
		records = list(records)
		for r in records:
			records[n] = list(records[n])
			records[n].append(n)
			n += 1
		#end addition of row numbers
		
##		print 'pobjauth: %s<br> pobjautherr: %s<br> rcdserr:%s<br> pobjauthl: %s<br>' % (pobjauth, pobjautherr, rcdserr, pobjauthl)
			
	##---test begin
	##	tail = tail + 'pobjpgm, pobjstmt, startrec, rowcount<br>%s:%s:%s:%s<br>' % (pobjpgm, pobjstmt, startrec, rowcount)
	##	tail = tail + 'records, rcdserr<br>%s:%s<br><br>' % (records, rcdserr)
	##	tail = tail + 'vardict--%s<br>varlist--%s<br><br>' % (vardict, varlist)
	##	print 'tailnumber-%s %s' % (tailn, tail)
	##	tailn = tailn +1		used to show how many times this while statement is being processed.
	## ---test end
		
		file = Pio_processpval.dopval(file, records, pobjid, rowcount, vardict, varlist, startrec, nextrecnmbr)
		##file, fn2 =  re.subn(str(tagdata), '', str(file), count=1)		#remove pobj tag before doing loop.
		##print '<br>the tagdata: %s <br> fn2: %s <br>' % (tagdata[1:len(tagdata)-1], fn2)		# used to find loop error with ?
		
		if prefsdict.has_key('showpobj'):
			if prefsdict["showpobj"].upper() == 'YES':
				xtagdata = '<x' + tagdata[1:len(tagdata)]
				file = string.replace(file, tagdata, xtagdata, 1)
			else:
				file = string.replace(file, tagdata, '', 1)
		else:
			file = string.replace(file, tagdata, '', 1)
		
		#below we test for piosid, pobj, pobjauth errors and then execute according to prefs, or pprefs from page.
		if piosiderr == '' or piosiderr <> '' and piosiderrcount > 0:
			if pobjautherr == '' and rcdsautherr == '':			#for no pobjautherr and no rcdsautherr test rcdserr (bad sql)
				if rcdserr <> '':
					errortext = ':For pobj "%s" --%s' % (pobjid, rcdserr)
					err = err + '<p>' + errortext
					if string.find(pref_pobjerror, '.') == -1:
						if string.find(pref_pobjerror.upper(), 'TOP') <> -1:
							nose = nose + '<p>' + errortext
						elif string.find(pref_pobjerror.upper(), 'BOTTOM') <> -1 or pref_pobjerror == '':
							tail = tail + '<p>' + errortext
					else:
						newfile = 'yes'
						pagename = pref_pobjerror
						levelcount = 0
						err = err + '<br><br>Failing Error = "%s"' % (errortext)
						file, prefsdict = processfile(pagename, form, levelcount, webpath, requestedurl, err, prefsdict, uploadfiles, qrystring)
						tail = ''
						nose = ''
			else:																	#do pobjautherr/rcdsautherr (which amounts to much the same thing)
				errortext = ':For pobj "%s" --%s' % (pobjid, rcdsautherr)
				err = err + '<br>' + pobjautherr + '<br>' + rcdsautherr
				if prefsdict.has_key('pobjautherrorfile'):
					pref_pobjautherrorfile = prefsdict['pobjautherrorfile']
				else:
					pref_pobjautherrorfile = 'none'
				
				if string.find(pref_pobjautherrorfile, '.') == -1 or pref_pobjautherrorfile.upper() == 'NONE' or pref_pobjautherrorfile == "":
					if string.find(pref_pobjautherror.upper(), 'TOP') <> -1:
						nose = nose + '<p>' + errortext
					elif string.find(pref_pobjautherror.upper(), 'BOTTOM') <> -1 or pref_pobjautherror == '':
						tail = tail + '<p>' + errortext
				else:
					print err
					newfile = 'yes'
					pagename = pref_pobjautherrorfile
					levelcount = 0
					err = err + '<br><br>Failing Error = "%s"' % (errortext)
					file, prefsdict = processfile(pagename, form, levelcount, webpath, requestedurl, err, prefsdict, uploadfiles, qrystring)
					if string.find(pref_pobjautherror.upper(), 'TOP') <> -1:
						nose = nose + '<p>' + errortext
					elif string.find(pref_pobjautherror.upper(), 'BOTTOM') <> -1 or pref_pobjautherror == '':
						tail = tail + '<p>' + errortext
		else:
			piosiderrcount = 1
			errortext = ':For pioSID "%s" --%s' % (piosid, piosiderr)
			err = err + '<p>' + errortext
			if prefsdict.has_key('piosiderrorfile'):
				pref_piosiderrorfile = prefsdict['piosiderrorfile']
			else:
				pref_piosiderrorfile = 'none'
			
			if string.find(pref_piosiderrorfile, '.') == -1 or pref_piosiderrorfile.upper() == 'NONE' or pref_piosiderrorfile == "":
				if string.find(pref_piosiderror.upper(), 'TOP') <> -1:
					nose = nose + '<p>' + errortext
				elif string.find(pref_piosiderror.upper(), 'BOTTOM') <> -1 or pref_piosiderror == '':
					tail = tail + '<p>' + errortext
			else:
				newfile = 'yes'
				pagename = pref_piosiderrorfile
				levelcount = 0
				err = err + '<br><br>Failing Error = "%s"' % (errortext)
				file, prefsdict = processfile(pagename, form, levelcount, webpath, requestedurl, err, prefsdict, uploadfiles, qrystring)
				tail = ''
				nose = ''
			
		
		fn = string.find(file, '<pobj', 0)	#do the find to load up fn for next loop
		
		
	# end of the while statement processing pobj tags
	file = Pio_processpval.clearpval(file)		#clear blank pvals
	if string.find(file, '<pmath') <> -1:		#process pmath statements after getting loading all the pvals to file
		file = Pio_pif.processpmath(file, 'end')		#the begin value is used to process pval's and clear the pmaths
	file = Pio_pif.processpvif(file)					#process pvif statements
	
	
	#process pstring
	if string.find(file, '<pstring') != -1:		#process pstring statements after loading all the pvals to file
		file = Pio_pif.pstring(file)
	
	
	##tail = tail + '<br>pioclass: "%s"' % (pioclass)
	##tail = tail + webpath
	
	#here is where we write the static webpage out with Pio_static
	#then we append the result/error message to the nose and tail of the page returned to the browser
	#uploadfiles format: {fieldname:[filename, file]}
#	if form.has_key("piostaticpage") and form.has_key("piostaticpath") and pioclass.upper() == 'PIOADMIN':
#		filename = form["piostaticpage"].value
#		filepath = form["piostaticpath"].value
#		uploadfiles = {filename:[filename, str(nose) + str(file) + str(tail)]}
#		import Pio_staticclient
#		uploadresults = Pio_staticclient.processupload(uploadfiles, filepath, "Pio_getpage-process static page")	
#		nose = str(uploadresults) + ':::' + nose
#		tail =tail + ':::' + str(uploadresults)
	
	outfile = str(nose) + str(file) + str(tail)
	
	db.close()
	
	piobinary = ""
	if form.has_key("piobinary"):	
		piobinary = form["piobinary"].value
		mimetype, outfile = setmime_getbinary(piobinary, outfile)
	else:
		mimetype = ""	#Pio_getpage.cgi does a print "Content-type: text/html\n\n"	if no 'piobinary=' value in qrystring
	
	return outfile, mimetype
#	return outfile

