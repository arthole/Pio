import string, os, whrandom

#webpath = '/Library/WebServer/Documents'		#for testing purposes
#pobjstmt = 'pxlane'
#startrec = 0
#rowcount = 10


##here is an example of records that should be returned:
##((field1, "field2", "field3"), (field1, "field2", "field3"), (field1, "field2", "field3"), (field1, "field2", "field3"))

def getrandomobj(pobjpgm, pobjstmt, startrec, rowcount, levelcount, ipaddr, webpath, requestedurl, pobjauth, piouser, prefsdict):
	
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
		randnmbr = whrandom.randint(0, objlistlen -1)
		
		objname = objlist[randnmbr]
		objnamepath = objpath +objname
		edot = string.find(objname, '.')			# this is to find the object extension, it gets returned along with objectname and objectpathname
		if  edot <> -1:
			objext = str(objname[edot+1:len(objname)])
		else:
			objext = ''
		records.append([objnamepath, objname, objext, randnmbr])
		
	except OSError, e:
		rcdserr = "Pio_getrandomobj.getrandomobj: no directory /<i>serverpath</i>%s" % (objpath)
	
	return records, rcdserr, rcdsautherr, nextrecnmbr
	
	

