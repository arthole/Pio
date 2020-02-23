#Pio_log.py
#creates a log entry into the database for each qrystmt

import MySQLdb

def addentry(ipaddr, browser, requrl, qrystring, sqluser, sqldb, sqlhost, mysqlc):
	
	qrystring = MySQLdb.escape_string(qrystring)
	requrl = MySQLdb.escape_string(requrl)
	
	sqlstmt = "insert into piolog set ipaddr = '%s', browser = '%s', requrl = '%s', qrystring='%s'" % (ipaddr, browser, requrl, qrystring)
	
	mysqlc.execute(sqlstmt)
	
	return
