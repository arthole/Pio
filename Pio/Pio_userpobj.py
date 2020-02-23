import string

##here is an example of records:
##((field1, "field2", "field3"), (field1, "field2", "field3"), (field1, "field2", "field3"), (field1, "field2", "field3"))

def pgm(pobjpgm, pobjstmt, startrec, rowcount, levelcount, ipaddr, webpath, requestedurl, pobjauth, piouser, prefsdict, mysqlc):
	
	records = []
	rcdserr = 'Pio_userpobj -- Unknown Program: %s' % (pobjpgm)
	rcdsautherr = ''
	nextrecnmbr = 0
	
	#if pobjpgm == "Pio_showobj" will return all the values sent to a pobj for processing.
	if pobjpgm == "Pio_showpobj":
		one_column = []
		one_column.append('each record in this pobj shows the standard pobj input values, the returned record data, and the data available to the pobj module')
		one_column.append('pobjpgm: %s' % (pobjpgm) )
		one_column.append('pobjstmt: %s' % (pobjstmt) )
		one_column.append('startrec: %s' % (startrec) )
		one_column.append('rowcount: %s' % (rowcount) )
		one_column.append('levelcount: %s' % (levelcount) )
		one_column.append('ipaddr: %s' % (ipaddr) )
		one_column.append('webpath: %s' % (webpath) )
		one_column.append('requestedurl: %s' % (requestedurl) )
		one_column.append('pobjauth: %s' % (str(pobjauth) ) )
		one_column.append('piouser: %s' % (piouser) )
		one_column.append('prefsdict: %s' % (str(prefsdict) ) )
		one_column.append('each pobj program must return the following types of objects to the calling module (--> Pio_processpobj --> Pio_getpage): tuple/list, string, string and integer')
		one_column.append('other returned values are:\nrcdserr: Not Applicable on Demo pobj -- A sample message is: %s' % (rcdserr) )
		one_column.append('rcdsautherr: %s' % ('Not Applicable on Demo pobj') )
		one_column.append('nextrecnmbr: %s' % (0) )
		one_column.append('This concludes the lst of inputs/outputs available to write your own pobj')
		
		for i in one_column:
			records.append([i])
		rcdserr = ''
	
	if pobjpgm == "Pio_getrandomobj":
		import Pio_getrandomobj
		records, rcdserr, rcdsautherr, nextrecnmbr =  Pio_getrandomobj.getrandomobj(pobjpgm, pobjstmt, startrec, rowcount, levelcount, ipaddr, webpath, requestedurl, pobjauth, piouser, prefsdict)
	elif pobjpgm == "Pio_getobjlist":
		import Pio_getobjlist
		records, rcdserr, rcdsautherr, nextrecnmbr =  Pio_getobjlist.getobjlist(pobjpgm, pobjstmt, startrec, rowcount, levelcount, ipaddr, webpath, requestedurl, pobjauth, piouser, prefsdict)
	
	#note doing a little code edit as I screwed up typing it so many times!
	if pobjpgm == 'Pio_convertohtml': pobjpgm = 'Pio_converttohtml'
	if pobjpgm == 'Pio_convertotext': pobjpgm = 'Pio_converttotext'
	if pobjpgm == "Pio_converttohtml" or pobjpgm == "Pio_converttotext":
		import Pio_converttext
		records, rcdserr, rcdsautherr, nextrecnmbr =  Pio_converttext.converttext(pobjpgm, pobjstmt)
	
	
	
	
	
#insert your own imports to get an pobj here
#each program must return the following types of objects: list(records), string(rcdserr), string(rcdsautherr) and integer(nextrecnmbr)
	
	
	
	
	
	
	
	return records, rcdserr, rcdsautherr, nextrecnmbr


