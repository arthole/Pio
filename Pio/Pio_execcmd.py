#!/usr/bin/python

#Pio process pioexeccmd file for a single database
#specify sqluser, sqldb, sqlhost.  The sqluser must have authority to 
#lock tables.  it seems a pesky problem.  the user must have authority to mysql db
#as well as the specified db.  

import MySQLdb, sys, string, commands

sys.stderr = sys.stdout

logentry = ''
errormsg = """Pio_execcmd.py 
Missing option:  specify in order sql database, sql user, passwd, and sqlhost
\n
example: Pio_execcmd.py spam montypython parr0ts! localhost \n
"""

if len(sys.argv) < 4:
	print errormsg
else:
#	try:
	sqldb = sys.argv[1]
	sqluser = sys.argv[2]
	sqlpass = sys.argv[3]
	sqlhost = sys.argv[4]
	db = MySQLdb.connect(db=sqldb, user=sqluser, host=sqlhost, passwd = sqlpass)
	mysqlc = db.cursor()
	
	sqlstmt = 'lock tables pioexeccmd_log write'
	mysqlc.execute(sqlstmt)
	
	##get datetime
	sqlstmt = 'select upper(now() + 0)'
	mysqlc.execute(sqlstmt)
	the_now = mysqlc._rows[0][0]
	
	sqlstmt = 'insert into pioexeccmd_log set starttime = %s' % (the_now)
	mysqlc.execute(sqlstmt)
	
	sqlstmt = 'lock tables pioexeccmd write'
	mysqlc.execute(sqlstmt)
	sqlstmt = 'update pioexeccmd set starttime = %s where starttime = 0 and nextexec <= %s' % (the_now, the_now)
	mysqlc.execute(sqlstmt)
	
	sqlstmt = 'unlock tables'
	mysqlc.execute(sqlstmt)
	
	
	sqlstmt = 'select pioexeccmd.piouser, pioexeccmd.cmdname, piousercmd.cmd, piousercmd.outputfile, piousercmd.lastexec from pioexeccmd, piousercmd where pioexeccmd.piouser = piousercmd.piouser and pioexeccmd.cmdname = piousercmd.cmdname and pioexeccmd.starttime = "%s" ' % (the_now)
	processrowcnt = mysqlc.execute(sqlstmt)
	processrows = mysqlc._rows
	
	if processrowcnt < 1:
		#since there is nothing to process, remove the log entry.
		sqlstmt = 'delete from pioexeccmd_log where starttime = "%s"' % (the_now)
		mysqlc.execute(sqlstmt)
	else:
		n = 0
		for i in processrows:
			if processrows[n][3] != '':		#append results to outputfile
				cmdstmt = processrows[n][2] + ' >> ' + processrows[n][3]
				results = commands.getoutput(cmdstmt)
			else:
				cmdstmt = processrows[n][2]
				results = commands.getoutput(processrows[n][2])
			
			logentry = logentry + 'USER: %s  CMDNAME: %s  EXEC: %s  RESULTS: %s' % (processrows[n][0], processrows[n][1], cmdstmt, results)
			sqlstmt = 'delete from pioexeccmd where piouser = "%s" and cmdname = "%s" and starttime = "%s"' % (processrows[n][0], processrows[n][1], the_now)
			sqlrowcount = mysqlc.execute(sqlstmt)
			sqlstmt = 'update piousercmd set lastexec = %s where piouser = "%s" and cmdname = "%s"' % (the_now, processrows[n][0], processrows[n][1])
			mysqlc.execute(sqlstmt)
			n = n + 1
			
		sqlstmt = 'update pioexeccmd_log set log = "%s", endtime = now() where starttime = %s' % (logentry, the_now)
		mysqlc.execute(sqlstmt)

