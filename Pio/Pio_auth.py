import MySQLdb, string, _mysql_exceptions, time, crypt, re, Pio_prefs

sqluser = Pio_prefs.gimme('sqluser')
sqldb = Pio_prefs.gimme('sqldb')
sqlhost = Pio_prefs.gimme('sqlhost')
staticip = Pio_prefs.gimme('staticip')

def tableauth(pioclass, pobjstmt, mysqlc):
	
	autherr = ''
	table = ''
	authsort = ['N', 'R', ' ', '', 'F']
	tblauth = [' ', ' ', ' ', ' ']
	
	if pobjstmt[0] == "'" or pobjstmt[0] == '"':
		autherr = 'pobjstmt begins with quotes...triple quote individual column values to escape correctly<br>'
	
	pobjsplit = re.split(' ', pobjstmt.lstrip())
	if pobjsplit[0].lower() == 'insert'  or pobjsplit[0].lower() == 'replace':		#handle replaces as inserts
		n = 1
		while n < 4 and table == '':
			if pobjsplit[n].lower() == 'into' or pobjsplit[n].lower() == 'ignore':
				n = n + 1
			else:
				table = pobjsplit[n].lower()
		if n >= 4:
			autherr = 'insert cannot find table - failed to authorize table'
			
#		print 'table=' + table		#used to test the auth values
		
	elif pobjsplit[0].lower() == 'update':
		n = 1
		while n < 4 and table == '':
			if pobjsplit[n].lower() == 'low_priority' or pobjsplit[n].lower() == 'ignore':
				n = n + 1
			else:
				table = pobjsplit[n].lower()
		if n >= 4:
			autherr = 'update cannot find table - failed to authorize table'
		
	elif pobjsplit[0].lower() == 'delete':
		try:
			table = pobjsplit[pobjsplit.index('from') + 1]
		except ValueError:
			try:
				table = pobjsplit[pobjsplit.index('FROM') + 1]
			except ValueError:
				autherr = 'delete missing "from" cannot find table - failed to authorize table'
		
	elif pobjsplit[0].lower() == 'select':
		f1 = string.find(pobjstmt.upper(), ' FROM ')
		if f1 <> -1:
			w1 = string.find(pobjstmt.upper(), ' WHERE ')
			if w1 <> -1:
				whereval = pobjstmt[w1+1:w1+6]
			else:
				whereval = ''
			
			f2 = pobjsplit.index(pobjstmt[f1+1:f1+5])			#FROM index#
			while f2 - 1 > -1:												#eliminate everything before the FROM
				pobjsplit.remove(pobjsplit[f2-1])
				f2 = pobjsplit.index(pobjstmt[f1+1:f1+5])
			table = pobjsplit[f2+1]
			if table[len(table)-1:] == ',':
				table = table[0:len(table) -1]
			as1 = 0
			while as1 <> -1:												#eliminate "AS" and the following value
				as1 = string.find(str(pobjsplit).upper(), ' AS ')
				if as1 <> -1:
					as2 = pobjsplit.index(str(pobjsplit)[as1:as1+4])
					pobjsplit.remove(pobjsplit[as2])
					pobjsplit.remove(pobjsplit[as2])			#because index shifts over, as2 is now value after "AS".
				
			jn1 = string.find(str(pobjsplit).upper(), ' JOIN ')
			if jn1 <> -1:
				while jn1 > -1:
					jn2 = pobjsplit.index(str(pobjsplit)[jn1:jn1+6])
					table = table + ',' + pobjsplit[jn2+1]
					pobjsplit.remove(pobjsplit[jn2])
					jn1 = string.find(str(pobjsplit).upper(), ' JOIN ', jn1 + 1)
			else:
				if whereval <> '':
					fwdiff = pobjsplit.index(whereval) - f2
					if fwdiff > 2:
						fwdiff = fwdiff -1
						while fwdiff > 1:
							if table[len(table)-1:] == ',':
								table = table + pobjsplit[fwdiff]
							else:
								table = table + ',' + pobjsplit[fwdiff]
							fwdiff = fwdiff -1
			if table[len(table)-1:] == ',':
				table = table[0:len(table) -1]
	#	else:
	#		autherr = 'Select has no "FROM" - cannot find table - failed to authorize table'
	#selects can do more than get stuff from tables, so a select with no from my be allowable.
		
	if table <> '':
		tablelist = re.split(',', table)
		n = 0
##		db = MySQLdb.connect(db=sqldb, user=sqluser, host= sqlhost)
##		mysqlc. = db.cursor()
		for i in tablelist:
			sqlstmt = 'select pioclass, dbtable, dbinsert, dbupdate, dbdelete, dbselect from pioclasstable'
			sqlstmt = sqlstmt + ' where pioclass = "%s" and dbtable = "%s"' % (pioclass, tablelist[n])
			sqlstmt = sqlstmt + ' or pioclass = "" and dbtable = "%s"' % (tablelist[n])
			sqlstmt = sqlstmt + ' order by pioclass DESC, dbtable DESC'
			mysqlc.execute(sqlstmt)
			
			if mysqlc.rowcount == 0:
				#insert, update, delete, select (Full, Record, None, '')
				tmpauth = [' ', ' ', ' ', ' ']
			else:
				tmpauth = [string.upper(mysqlc._rows[0][2]), string.upper(mysqlc._rows[0][3]), string.upper(mysqlc._rows[0][4]),string.upper(mysqlc._rows[0][5])]
				if n == 0:
					tblauth = tmpauth
				else:
					if authsort.index(tmpauth[0]) < authsort.index(tblauth[0]):
						tblauth[0] = tmpauth[0]
					if authsort.index(tmpauth[1]) < authsort.index(tblauth[1]):
						tblauth[1] = tmpauth[1]
					if authsort.index(tmpauth[2]) < authsort.index(tblauth[2]):
						tblauth[2] = tmpauth[2]
					if authsort.index(tmpauth[3]) < authsort.index(tblauth[3]):
						tblauth[3] = tmpauth[3]
			
			n = n + 1
	return tblauth, autherr, table


def pioauth(piosid, ipaddr, mysqlc):
##	db = MySQLdb.connect(db=sqldb, user=sqluser, host=sqlhost)
##	c = db.cursor()
	
	thesalt = 'thesalt'
	sidreset = 0
	sidtmout = 10000
	newsid = ''
	autherr = ''
	pioclass = ''
	piouser = ''
	ct = time.localtime(time.time())
	tmstamp = string.atol(time.strftime('%y%m%d%H%M%S', ct))	
	# long int of formatted current time
	
	b = string.find(piosid, '_')
	if b == -1:
		autherr = 'Authorization Error: Invalid Session ID format'
	else:
		siduser = piosid[b+1:len(piosid)]
		sqlstmt = 'select tmstamp, ipaddr, pioclass, piouser, sidreset, sidtmout from pioauth where piosid = "%s"' % (piosid)
		mysqlc.execute(sqlstmt) 
		
		if mysqlc.rowcount <>1:
			autherr = 'Authorization Error: Invalid Session ID'
		else:
			if mysqlc._rows[0][5] > 0:
				sidtmout = mysqlc._rows[0][5]
			timediff = tmstamp - mysqlc._rows[0][0]
			
			if staticip == 'yes':
				if ipaddr <> mysqlc._rows[0][1]:
					autherr = 'Authorization Error: Invalid IP Address'
				
			if timediff >= sidtmout:
				autherr = 'Authorization Error: Inactivity time out'
			else:
				if mysqlc._rows[0][4] > 0:
					sidreset = mysqlc._rows[0][4]
				if sidreset <> 0 and timediff > sidreset:
					newsid = crypt.crypt(str(tmstamp)[len(str(tmstamp))-9:len(str(tmstamp))-1], thesalt)
					newsid = newsid + '_' + piouser
					#changing sess id every time increases security...makes the backbutton rather ineffective though.
				else:
					newsid = piosid
				
				pioclass = mysqlc._rows[0][2]		#returns only a good pioclass after time/piosid/ipaddr checks.
				piouser = mysqlc._rows[0][3]
				
				sqlstmt = 'update pioauth set piosid="%s", tmstamp= %s where piosid = "%s"' % (newsid, tmstamp, piosid)
				mysqlc.execute(sqlstmt) 
				if mysqlc.rowcount == 1:
					autherr = ''
				elif mysqlc.rowcount == 0 and mysqlc.connection.info() == 'Rows matched: 1  Changed: 0  Warnings: 0':		#usually no change after init login.
					autherr = ''
				else:
					autherr = 'Authorization Error: Authorization failed on update (%s)' % (mysqlc.connection.info())
		
	#try if pioauth fails (producing an autherr) then piosid should be set to blank, 
	#to prevent piosid dependent pages/data from being displayed, even though no harm would come from it. 
	return (newsid, autherr, tmstamp, pioclass, piouser)
#	if newsid == '':
#		return (piosid, autherr, tmstamp, pioclass, piouser)
#	else:
#		return (newsid, autherr, tmstamp, pioclass, piouser)


def login(piouser, piopass, ipaddr):
	loginerr = ''
	piosid = ''
	db = MySQLdb.connect(db=sqldb, user=sqluser, host=sqlhost)
	mysqlc = db.cursor()
	
	ct = time.localtime(time.time())
	tmstamp = string.atol(time.strftime('%y%m%d%H%M%S', ct))	
	# long int of formatted current time
	
	sqlstmt = 'select piouser from pioauth where piouser  = "%s"' % (piouser)
	mysqlc.execute(sqlstmt) 
	
	if mysqlc.rowcount == 0:
		loginerr = "Invalid User"
	else: 
		piosid = crypt.crypt(str(tmstamp)[len(str(tmstamp))-9:len(str(tmstamp))-1], 'sparklingfresh42') + '_' + piouser
#		piosid = crypt.crypt(str(tmstamp), 'MtnDew7!') + '_' + piouser
		sqlstmt = 'update pioauth set piosid="%s", tmstamp= %s, ipaddr="%s" where piouser  = "%s" and "%s" = aes_decrypt(piopass, "$EnCrYpTiOnKey$")' % (piosid, tmstamp, ipaddr, piouser, piopass)
		mysqlc.execute(sqlstmt) 
		if mysqlc.rowcount == 1:
			loginerr = ''
		else:
			loginerr = 'Invalid Password'
	
	db.close()
	return (piosid, loginerr)


def updatepass(piouser, piopass, piopassnew, piopassnew2, ipaddr, piosid):
	#we always authenticate the user so no matter how this method gets called it performs the right authentication.
	db = MySQLdb.connect(db=sqldb, user=sqluser, host=sqlhost)
	mysqlc = db.cursor()
	
	passwordupdate_msg = ''
	passwordupdate_error = ''
	newsid, autherr, pioclass, tmstamp, piouser2 = pioauth(piosid, ipaddr, mysqlc)
	if autherr == '':
		if piouser == piouser2:			#make sure the piouser matches the piosid to the piouser being changed.
			if piopassnew == piopassnew2:
				sqlstmt = 'update pioauth set piopass= aes_encrypt("%s", "$EnCrYpTiOnKey$") where piouser  = "%s" and "%s" = aes_decrypt(piopass, "$EnCrYpTiOnKey$") ' % (piopassnew, piouser, piopass)
				mysqlc.execute(sqlstmt) 
				if mysqlc.rowcount <> 1:
					passwordupdate_msg = 'Update Password Error: Update statement error %s.' % (mysqlc.connection.info())
				else:
					if mysqlc.connection.info() == 'Rows matched: 1  Changed: 1  Warnings: 0':
						passwordupdate_msg = 'Password Changed Successfully for %s' % (piouser)
					elif mysqlc.connection.info()[0:27] == 'Rows matched: 1  Changed: 1':
						passwordupdate_msg = 'Password Changed Successfully with Warnings for %s' % (piouser)
					elif mysqlc.connection.info() == 'Rows matched: 1  Changed: 0  Warnings: 0':
						passwordupdate_msg = 'Password Not Changed.  Old and New Password is the Same for %s' % (piouser)
						passwordupdate_error = 'error'
			else:
				passwordupdate_msg = 'Update Password Error: New Passwords Do Not Match'
				passwordupdate_error =  'error'
		else:
			passwordupdate_msg = 'piouser does match database'
			passwordupdate_error =  'error'
	else:
		passwordupdate_msg = autherr
		passwordupdate_error = 'error'
	
	db.close()
	return (passwordupdate_msg, passwordupdate_error)
	


def pobjauth(pioclass, pobjid, page, pobjstmt, mysqlc):
	
	authsort = ['N', 'R', 'F', ' ', '']		# '' and ' ' get treated as 'N' in processpobj.
	tblauth, tblautherr, table = tableauth(pioclass, pobjstmt, mysqlc)		#get table authorization
	outputauth = tblauth
	origtblauth = (tblauth[0], tblauth[1], tblauth[2], tblauth[3])
	
##	db = MySQLdb.connect(db=sqldb, user=sqluser, host=sqlhost)
##	c = db.cursor()
	sqlstmt = 'select pioclass, pobjid, page, dbinsert, dbupdate, dbdelete, dbselect from pioclasspobj'
	sqlstmt = sqlstmt + ' where pioclass = "%s" and pobjid = "%s" and page = "%s"' % (pioclass, pobjid, page)
	sqlstmt = sqlstmt + ' or pioclass = "" and pobjid = "%s" and page = "%s"' % (pobjid, page)
	sqlstmt = sqlstmt + ' or pioclass = "" and pobjid = "%s" and page = ""' % (pobjid)
	sqlstmt = sqlstmt + ' or pioclass = "" and pobjid = "" and page = ""'
	sqlstmt = sqlstmt + ' or pioclass = "%s" and pobjid = "%s" and page = ""' % (pioclass, pobjid)
	sqlstmt = sqlstmt + ' or pioclass = "%s" and pobjid = "" and page = ""' % (pioclass)
	sqlstmt = sqlstmt + ' order by pioclass DESC, pobjid DESC, page DESC'
	mysqlc.execute(sqlstmt)
	if mysqlc.rowcount == 0:
		#insert, update, delete, select (Full, Record, None)
		pobjauthl = ['N', 'N', 'N', 'N']
		mysqlc._rows = (('', '', '', 'N', 'N', 'N', 'N'),)
	else:
		pobjauthl = [string.upper(mysqlc._rows[0][3]), string.upper(mysqlc._rows[0][4]), string.upper(mysqlc._rows[0][5]),string.upper(mysqlc._rows[0][6])]
		#I really don't care what records after the first there are, because it's the first one that tells me what the authorization is
		#the later records are more general authorizations, the earlier records are more specific.
	
	#tblauth is more authoritative than pobjauth.  except in the following situations.
	#note-A blank pobjid, means the pobjauthl is a defaul list.  
	#outputauth gets overwritten by a more restrictive pobjauth, not a more restrictive DEFAULT pobjauth value.
	#if the outputauth is blank, it will get the default pobjauth values.  
	
	try:		#this tested a failure on mysqlc._rows.  where mysqlc._rows == (), since corrected by setting mysqlc._rows value where mysqlc.rowcount = 0 above
		#if pobjid auth is less than outputauth use outputauth values.  except for blank pobjid
		if authsort.index(pobjauthl[0]) < authsort.index(outputauth[0]) and mysqlc._rows[0][1] <> '':		
			outputauth[0] = pobjauthl[0]
	except IndexError:
		print 'tableauth' + str(outputauth) + 'pobjauthl' + str(pobjauthl) + 'authsort'+ str(authsort)+'mysqlc._rows' + str(mysqlc._rows) + 'rowcount-' + str(mysqlc.rowcount)
		print 'pioclass' + pioclass + 'pobjid' + pobjid + '<br><br>'
	
	if authsort.index(pobjauthl[1]) < authsort.index(outputauth[1]) and mysqlc._rows[0][1] <> '':
		outputauth[1] = pobjauthl[1]
	
	if authsort.index(pobjauthl[2]) < authsort.index(outputauth[2]) and mysqlc._rows[0][1] <> '':
		outputauth[2] = pobjauthl[2]
	
	if authsort.index(pobjauthl[3]) < authsort.index(outputauth[3])  and mysqlc._rows[0][1] <> '':
		outputauth[3] = pobjauthl[3]
	
	if outputauth[0] == '' or outputauth[0] == ' ':		#if outputauth is blank, use pobjauth regardless
		outputauth[0] = pobjauthl[0]
	
	if outputauth[1] == '' or outputauth[1] == ' ':
		outputauth[1] = pobjauthl[1]
	
	if outputauth[2] == '' or outputauth[2] == ' ':
		outputauth[2] = pobjauthl[2]
	
	if outputauth[3] == '' or outputauth[3] == ' ':
		outputauth[3] = pobjauthl[3]
	
	pobjauth = {'dbinsert':outputauth[0], 'dbupdate':outputauth[1], 'dbdelete':outputauth[2], 'dbselect':outputauth[3]}
	
	return (pobjauth, tblautherr, origtblauth, pobjauthl)









