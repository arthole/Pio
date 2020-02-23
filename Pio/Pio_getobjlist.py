import string, os

#webpath = '/Library/WebServer/Documents'		#for testing purposes
#pobjstmt = 'pxlane'
#startrec = 0
#rowcount = 10


##here is an example of records:
##((field1, "field2", "field3"), (field1, "field2", "field3"), (field1, "field2", "field3"), (field1, "field2", "field3"))

def getobjlist(pobjpgm, pobjstmt, startrec, rowcount, levelcount, ipaddr, webpath, requestedurl, pobjauth, piouser, prefsdict):
	
	records = []
	rcdserr = ''
	rcdsautherr = ''
	nextrecnmbr = 0
	
	if pobjstmt[0] == "/" and pobjstmt[len(pobjstmt)-1:len(pobjstmt)-1] == "/":
		objdir = str(webpath) + str(pobjstmt)
		objpath = str(pobjstmt)
	elif pobjstmt[0] == "/" and pobjstmt[len(pobjstmt)-1:len(pobjstmt)-1] <> "/":
		objdir = str(webpath) + str(pobjstmt) + '/'
		objpath = str(pobjstmt) + '/'
	elif pobjstmt[0] <> "/" and pobjstmt[len(pobjstmt)-1:len(pobjstmt)-1] == "/":
		objdir = str(webpath) + '/' + str(pobjstmt)
		objpath = '/' + str(pobjstmt)
	else:
		objdir = str(webpath) + '/' + str(pobjstmt)+ '/'
		objpath = '/' + str(pobjstmt)+ '/'
	
	try:
		objlist = os.listdir(objdir)	#list of directory objects
		objlistlen = len(objlist)	#number of dir objects
		if objlistlen <= rowcount:
			rcdlist = objlist[startrec:objlistlen]
			nextrecnmbr = 0
		elif objlistlen > rowcount and (objlistlen - startrec) <= rowcount:
			rcdlist = objlist[startrec:objlistlen]
			nextrecnmbr = 0
		elif objlistlen > rowcount and (objlistlen - startrec) > rowcount:
			rcdlist = objlist[startrec:(startrec+rowcount)]
			nextrecnmbr = startrec + rowcount + 1
		else:
			rcdlist = objlist
			nextrecnmbr = 0
		
		n = 0
		#objname = objpath + rcdlist[n]
		for i in rcdlist:
			objnamepath = objpath + rcdlist[n]
			objname = rcdlist[n]
			edot = string.find(objname, '.')
			if  edot <> -1:
				objext = str(objname[edot+1:len(objname)])
			else:
				objext = ''
			records.append([objnamepath, objname, objext])
			n = n + 1
	except OSError, e:
		rcdserr = "Pio_getobjlist.getobjlis: no directory /<i>serverpath</i>%s" % (objpath)
	
	return records, rcdserr, rcdsautherr, nextrecnmbr
	
	

