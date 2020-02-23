import string, Pio_dbsql, Pio_getpage, os

def pgm(pobjpgm, pobjstmt, startrec, rowcount, levelcount, ipaddr, webpath, requestedurl, pobjauth, piouser, prefsdict, mysqlc):

	nextrecnmbr = 0
	records = ()
	rcdserr = ''
	rcdsautherr = ''
	
	if pobjpgm == 'Pio_qry' or pobjpgm == 'Pio_dbselect' or pobjpgm == 'dbselect':		#Pio_qry is old code...SELECT
		if pobjauth['dbselect'] == 'F':
			records, rcdserr, nextrecnmbr = Pio_dbsql.dbselect(pobjstmt, startrec, rowcount, mysqlc)
		elif pobjauth['dbselect'] == 'R':
			recordwherestmt = 'piouser = "%s"' % (piouser)
			r = string.find(pobjstmt, recordwherestmt)
			if r >= 0:
				records, rcdserr, nextrecnmbr= Pio_dbsql.dbselect(pobjstmt, startrec, rowcount, mysqlc)
			else:
				rcdsautherr = 'Pobj Auth: %s<br>Unable to execute pobj select, pobj authorization failed - no valid piouser where statement for %s' % (str(pobjauth), pobjstmt)
		else:
			rcdsautherr = 'Not Authorized to perform pobj select'
	
	elif pobjpgm == 'Pio_dbdescribe' or pobjpgm == 'dbdescribe':		#get a description of a file, must have full access to table.
		if pobjauth['dbselect'] == 'F' and pobjauth['dbupdate'] == 'F' and pobjauth['dbdelete'] == 'F' and pobjauth['dbinsert'] == 'F':
			records, rcdserr, nextrecnmbr = Pio_dbsql.dbdescribe(pobjstmt, mysqlc)
		else:
			rcdsautherr = 'Not Authorized to perform db describe'
	
	elif pobjpgm == 'Pio_dbupdate' or pobjpgm == 'dbupdate':		#											UPDATE
		if pobjauth['dbupdate'] == 'F':
			records, rcdserr = Pio_dbsql.dbupdate(pobjstmt, startrec, rowcount, mysqlc)
		elif pobjauth['dbupdate'] == 'R':
			recordwherestmt = 'piouser = "%s"' % (piouser)
			r = string.find(pobjstmt, recordwherestmt)
			if r >= 0:
				records, rcdserr = Pio_dbsql.dbupdate(pobjstmt, startrec, rowcount, mysqlc)
			else:
				rcdsautherr = 'Pobj Auth: %s<br>Unable to execute pobj update, pobj authorization failed - no valid piouser(%s) where statement for %s:%s' % (str(pobjauth), piouser, pobjstmt, recordwherestmt)
		else:
			rcdsautherr = 'Not Authorized to perform pobj update'
	
	elif pobjpgm == 'Pio_dbdelete' or pobjpgm == 'dbdelete':		#											DELETE
		if pobjauth['dbdelete'] == 'F':
			records, rcdserr = Pio_dbsql.dbdelete(pobjstmt, startrec, rowcount, mysqlc)
		elif pobjauth['dbdelete'] == 'R':
			recordwherestmt = 'piouser = "%s"' % (piouser)
			r = string.find(pobjstmt, recordwherestmt)
			if r >= 0:
				records, rcdserr = Pio_dbsql.dbdelete(pobjstmt, startrec, rowcount, mysqlc)
			else:
				rcdsautherr = 'Pobj Auth: %s<br>Unable to execute pobj delete, pobj authorization failed - no valid piouser(%s) where statement for %s' % (str(pobjauth), piouser, pobjstmt)
		else:
			rcdsautherr = 'Not Authorized to perform pobj delete'
	
	elif pobjpgm == 'Pio_dbinsert' or pobjpgm == 'dbinsert':		#											INSERT
		if pobjauth['dbinsert'] == 'F':
			records, rcdserr = Pio_dbsql.dbinsert(pobjstmt, startrec, rowcount, mysqlc)
		elif pobjauth['dbinsert'] == 'R':
			recordwherestmt = 'piouser = "%s"' % (piouser)
			r = string.find(pobjstmt, recordwherestmt)
			if r >= 0:
				records, rcdserr = Pio_dbsql.dbinsert(pobjstmt, startrec, rowcount, mysqlc)
			else:
				rcdsautherr = 'Pobj Auth: %s<br>Unable to execute pobj insert, pobj authorization failed - no valid piouser(%s) where statement for %s' % (str(pobjauth), piouser, pobjstmt)
		else:
			rcdsautherr = 'Not Authorized to perform pobj insert'
	
	elif pobjpgm == 'Pio_getpage' or pobjpgm == 'Pio_getpage' or pobjpgm == 'Pio_getpage.cgi' or pobjpgm == 'Pio_getpage.cgi':
		nextrecnmbr = 0
		if levelcount <= 5:
			levelcount = levelcount + 1
			os.environ['REMOTE_ADDR'] =ipaddr
			os.environ['QUERY_STRING'] = pobjstmt
##			print 'pobjstmt: %s<br>webpath: %s <br>requestedurl: %s <br>' % (pobjstmt, webpath, requestedurl)
			outfile, mimetype = Pio_getpage.getpage(pobjstmt, ipaddr, levelcount, webpath, requestedurl, {})		# the {} is for uploadfiles...there are none for includes
			records = (('%s' % (outfile),),)
			rcdserr = ''
		else:
			rcdserr = 'too many levels of getpage calls'
	else:
		import Pio_userpobj
		records, rcdserr, rcdsautherr, nextrecnmbr = Pio_userpobj.pgm(pobjpgm, pobjstmt, startrec, rowcount, levelcount, ipaddr, webpath, requestedurl, pobjauth, piouser, prefsdict, mysqlc)
		
	
	return records, rcdserr, rcdsautherr, nextrecnmbr
	
