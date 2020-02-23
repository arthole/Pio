import string, re,  _mysql_exceptions, Pio_prefs
import warnings
#warnings.filterwarnings('error', category=MySQLdb.Warning)
#add warnings code to individual methods.  (see dbinsert).  warnings get converted into exceptions.

#old mysqlcode
#db = MySQLdb.connect(db=sqldb, user=sqluser, host=sqlhost)
#mysqlc = db.cursor()


#leave this import to do triple quotes
#the mysql cursor/connection object (mysqlc) is handed in from Pio_getpage --> Pio_processpobj.
import MySQLdb


def printme():
	data = "here is the test of Pio_dbselect"
	return data

	#this code takes a triple quoted string from a pobj and formats it for loading to mysql
def triplequote(qrystring):
	tb = string.find(qrystring, '"""')
	te = string.find(qrystring, '"""', tb + 3)+3
	while tb != -1 and te != -1:
		trplqstr = qrystring[tb+3:te-3]
		trplqstr = MySQLdb.escape_string(trplqstr)
#		trplqstr = string.replace(trplqstr, '"', '\"')
#		trplqstr = string.replace(trplqstr, "'", "\'")
#		trplqstr = string.replace(trplqstr, '\', '\\')
		qrystring = string.replace(qrystring, qrystring[tb+1:te-1], trplqstr)
		tb = string.find(qrystring, '"""')
		te = string.find(qrystring, '"""', tb + 3)+3
		
	return qrystring

def dbselect(qrystmt, startrec, rowcount, mysqlc):
	rcdserr = ''
	nextrecnmbr = 0
#	describen = -1			###adding in description information to select works just fine...however, it should probably be more secure so as not to provide table info to hackers.
	
	if rowcount <= 0:
		rowcount = 10
	elif rowcount > 1000:			#this is to limit the possibility of queries become huge system hogs.
		rowcount = 1000
	n = string.find(qrystmt, 'select ', 0, 10)
#	if n == -1:
#		describen = string.find(qrystmt, 'describe ', 0, 10)
#		n = describen
	if n <> -1:		#is a select sqlstmt
#		if describen == -1:			#if it is a describe statement, then don't add limit information.
#			qrystmt = '%s LIMIT %s, %s'  % (qrystmt, startrec, rowcount+1)		#adding 1 to rowcount to deal with the last record = to the rowcount, rolling to nothing.  
		if string.find(qrystmt, ' limit') == -1:
			qrystmt = '%s LIMIT %s, %s'  % (qrystmt, startrec, rowcount+1)		#adding 1 to rowcount to deal with the last record = to the rowcount, rolling to nothing.  
		
		
		try:
			mysqlc.execute(qrystmt)
			#mysqlc._rows should have 1 extra record, because dbsql select/getform adds 1 to the rowcount so that we can determine 
			#here the correct next row value.  
			#If the # of mysqlc._rows is > rowcount, then the next record is the result of startrec+rowcount
			#if the # of mysqlc._rows is less than rowcount, then startrec+len(records) = last record.  and next record is thus 0 (to roll)
			#if the # of mysqlc._rows is = to rowcount then the last record means there are NOT records after rowcount, thus 0 is new startrec.
			nextrecnmbr = mysqlc.rowcount
			if nextrecnmbr > rowcount:		
				mysqlc._rows = mysqlc._rows[0:nextrecnmbr-1]		#this resets the actual records back to the way they should be.
			
			return mysqlc._rows, rcdserr, nextrecnmbr
		except (_mysql_exceptions.ProgrammingError, _mysql_exceptions.OperationalError), e:
			rcdserr = 'Error=%s  Error in statement: (%s)' % (e, qrystmt)
			return (), rcdserr, nextrecnmbr
		except _mysql_exceptions.Warning, e:
			rcdserr = 'Error=%s  Warning Error see statement: (%s)' % (e, qrystmt)
			return (), rcdserr, nextrecnmbr
	else:
		rcdserr = 'Error=(Qry Input Statement is not a select statement)  Error in statement: (%s)' % (qrystmt)
		return (), rcdserr, nextrecnmbr

def dbdescribe(qrystmt, mysqlc):
	rcdserr = ''
	nextrecnmbr = 0
#	describen = -1			###adding in description information to select works just fine...however, it should probably be more secure so as not to provide table info to hackers.
	
	rowcount = 1000		#max number of fields returned from a file (all on one page)
	n = string.find(qrystmt, 'describe ', 0, 10)
	if n <> -1:		#is a describe sqlstmt
		try:
			mysqlc.execute(qrystmt)
			#mysqlc._rows should have 1 extra record, because dbsql select/getform adds 1 to the rowcount so that we can determine 
			#here the correct next row value.  
			#If the # of mysqlc._rows is > rowcount, then the next record is the result of startrec+rowcount
			#if the # of mysqlc._rows is less than rowcount, then startrec+len(records) = last record.  and next record is thus 0 (to roll)
			#if the # of mysqlc._rows is = to rowcount then the last record means there are NOT records after rowcount, thus 0 is new startrec.
			nextrecnmbr = mysqlc.rowcount
			if nextrecnmbr > rowcount:		
				mysqlc._rows = mysqlc._rows[0:nextrecnmbr-1]		#this resets the actual records back to the way they should be.
			
			return mysqlc._rows, rcdserr, nextrecnmbr
		except _mysql_exceptions.ProgrammingError, e:
			rcdserr = 'Error=%s  Error in statement: (%s)' % (e, qrystmt)
			return (), rcdserr, nextrecnmbr
		except _mysql_exceptions.OperationalError, e:
			rcdserr = 'Error=%s  Error in statement: (%s)' % (e, qrystmt)
			return (), rcdserr, nextrecnmbr
	else:
		rcdserr = 'Error=(Qry Input Statement is not a describe statement)  Error in statement: (%s)' % (qrystmt)
		return (), rcdserr, nextrecnmbr

def dbupdate(qrystmt, startrec, rowcount, mysqlc):
	if rowcount == 0:
		rowcount = 1
	elif rowcount > 100:			#this is to limit the possibility of queries become huge system hogs.
		rowcount = 100
	n = string.find(qrystmt, 'update ', 0, 10)
	if n <> -1:		#is a select sqlstmt
		qryupd = '%s LIMIT %s'  % (qrystmt, rowcount)
		n1 = string.find(qrystmt.lower(), 'where')
		if n1 == -1:
			records, rcdserr = 'No Update Occured...No where statement in update!', ''
		else:
			try:
				qryupd = triplequote(qryupd)
				
				mysqlc.execute(qryupd)
				rowcnt = mysqlc.rowcount
				if mysqlc.connection.info() == 'Rows matched: %s  Changed: %s  Warnings: 0' % (rowcnt, rowcnt):
					records, rcdserr = 'Update Successful', ''
				elif mysqlc.connection.info() == 'Rows matched: 0  Changed: 0  Warnings: 0':
					records, rcdserr = 'Record Not Updated - no match found to update', ''
				elif mysqlc.connection.info() == 'Rows matched: %s  Changed: 0  Warnings: 0' % (rowcnt):
					records, rcdserr = 'Record Not Updated - No Change.' + mysqlc.connection.info(), ''
				else:
					r1 = string.find(str(mysqlc.connection.info()), 'Rows matched: %s  Changed: %s' % (rowcnt, rowcnt) )
					if r1 <> -1:
						records, rcdserr = 'Update Successful - contained warnings', ''
					else:
						#when connection info is NoneType, it's because the where on update returns an empty set, so connection info needs to be stringed
						records, rcdserr = 'Record Not Updated - ' + str(mysqlc.connection.info()), ''
			except (_mysql_exceptions.ProgrammingError, _mysql_exceptions.OperationalError), e:
				records, rcdserr = 'Error with Update', 'Error=%s  Error in statement: (%s)' % (e, qryupd)
			except _mysql_exceptions.Warning, e:
				records, rcdserr =  'Error with Update', 'Error=%s  Warning Error in statement: (%s)' % (e, qryupd)
			except _mysql_exceptions.IntegrityError , e:
				records, rcdserr =  'Error with Update', 'Error=%s Error in statement: (%s)' % (e, qryupd)
	else:
		records, rcdserr = (), 'Error: Qry Input Statement is not an update statement'
	return ((records,),), rcdserr

def dbinsert(qrystmt, startrec, rowcount, mysqlc):
	warnings.filterwarnings('error', category=MySQLdb.Warning)
	if rowcount == 0:
		rowcount = 1
	elif rowcount > 100:			#this is to limit the possibility of queries become huge system hogs.
		rowcount = 100
	if string.find(qrystmt, 'insert ', 0, 10) == -1 and string.find(qrystmt, 'replace ', 0, 10) == -1:		#test for insert or replace
		records, rcdserr = (), 'Error: Qry Input Statement is not an insert statement'
	else:
		qrystmt = '%s'  % (qrystmt)
		try:
			qrystmt = triplequote(qrystmt)
			
			mysqlc.execute(qrystmt)
			records, rcdserr = 'Inserted Record', ''
		except _mysql_exceptions.IntegrityError, e:
			records, rcdserr = 'Error on Insert', 'Error=%s  IntegrityError in statement: (%s)' % (e, qrystmt)
		except _mysql_exceptions.ProgrammingError, e:
			records, rcdserr = 'Error on Insert', 'Error=%s  ProgrammingError in statement: (%s)' % (e, qrystmt)
		except _mysql_exceptions.OperationalError, e:
			records, rcdserr = 'Error on Insert', 'Error=%s  OperationalError in statement: (%s)' % (e, qrystmt)
		except _mysql_exceptions.Warning, e:
			records, rcdserr = 'Warning on Insert', 'Warning=%s for statement: (%s)' % (e, qrystmt)
	return ((records,),), rcdserr

def dbdelete(qrystmt, startrec, rowcount, mysqlc):
	if rowcount == 0:
		rowcount = 1
	elif rowcount > 1000:			#this is to limit the possibility of queries become huge system hogs.
		rowcount = 1000				#rem these two lines to use rowcount as passed from page
	n = string.find(qrystmt, 'delete ', 0, 10)
	if n <> -1:		#is an delete sqlstmt
		n1 = string.find(qrystmt.lower(), 'where')
		if n1 == -1:
			records = 'No Deletion Occured...No where statement in delete!', ''
		else:
			qrystmt = '%s LIMIT %s'  % (qrystmt, rowcount)
			try:
				mysqlc.execute(qrystmt)
				if mysqlc.rowcount >= 1:
					records = 'Delete Successful:  %s rows deleted' % (str(mysqlc.rowcount) )
					rcdserr = ''
				elif mysqlc.rowcount < 1:
					records, rcdserr = 'No Deletion Occured...no match found?', ''
			except _mysql_exceptions.IntegrityError, e:
				records, rcdserr = (), 'Error=%s  Error in statement: (%s)' % (e, qrystmt)
			except _mysql_exceptions.ProgrammingError, e:
				records, rcdserr = (), 'Error=%s  Error in statement: (%s)' % (e, qrystmt)
			except _mysql_exceptions.OperationalError, e:
				records, rcdserr = (), 'Error=%s  Error in statement: (%s)' % (e, qrystmt)
	else:
		records, rcdserr = (), 'Error: Qry Input Statement is not an delete statement'
	return ((records,),), rcdserr

