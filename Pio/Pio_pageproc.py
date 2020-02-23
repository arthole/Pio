import string, re

count = 0

def cleaner(cleanme):	#cleans up the inserted text
	cleanme = re.sub(' =', '=', cleanme, count=999)	#remove blanks around = 
	cleanme = re.sub('= ', '=', cleanme, count=999)	#remove blanks around = 
	cleanme = re.sub("'", '"', cleanme, count=999)	#convert quotes to doubles
	cleanme = re.sub('",', '"', cleanme, count=999)	#remove dbl quote commans 
	cleanme = re.sub('=" ', '"', cleanme, count=999)	#remove dbl quote space after = 
	return cleanme

def parseobjvars(vars):
#this parses the vars list from a pobj tag.  
	s1 = 0
	vardict = {}
	varlist = []
	vars = re.sub(', ', ',', vars, count = 99) # remove spaces after commas
	vars = re.sub(' ,', ',', vars, count = 99) # remove spaces before commas
	vars = re.sub('  ' , ' ', vars, count = 99) # convert 2 spaces to 1 space 
	vars = re.sub(' ', ',', vars, count = 99) # convert 1 space to commas
	vars = re.sub(',,', ',', vars, count = 99) # convert ,, to 1 comma
	endloop = 0
	while endloop == 0:
		try:
			s2 = string.index(vars, ',', s1) # error out to end loop
			var = vars[s1:s2]
			vardict[var] = ''
			varlist.append(var)
			s1 = s2+1
		except ValueError:
			if s1 >= 0:	#get only one var element or last var element (slice it)
				vardict[vars[s1:len(vars)]] = ''
				varlist.append(vars[s1:len(vars)])
				endloop = 1
			else:		
				endloop = 1
	return vardict, varlist


def parseobjtag(tagdata):
# take a tag like this: <pobj id="1" name="qry" vars="stmt" rowcount="1" startrec="0">select * from artist where artist = #pinp.artist</pobj>
# and turn it into a dictionary like this: {'id': '1', 'input': 'select * from artist where artist = #pinp.artist', 'vars': 'stmt', 'name': 'qry', 'startrec': 0, 'rowcount': 1}
# this method is called by getpobjtag only
# startrec...these can be used with pinp codes inserted into the pobj tag, as can rowcount
	
	b = 5
	b1 = string.find(tagdata, '>', b)
	e = string.find(tagdata, '</pobj>', b1 + 1)
	info = tagdata[b1+1:e]
	tagerr = string.find('<pobj', tagdata[6:b1])
	if tagerr == -1:
		tag = cleaner(tagdata[6:b1])
		try:
			t1 = string.index(tag, 'id="') + 4
			id = tag[t1:(string.index(tag, '"', t1))]
			t1 = string.index(tag, 'name="') + 6
			name = tag[t1:(string.index(tag, '"', t1))]
			t1 = string.index(tag, 'vars="') + 6
			vars = tag[t1:(string.index(tag, '"', t1))]
			
			try:		#get row count, if no rowcount, make rowcount = 1
				t1 = string.index(tag, 'rowcount="') + 10
				try:
					rowcount = string.atoi(tag[t1:(string.index(tag, '"', t1))])
				except ValueError:
					rowcount = tag[t1:t1+3]
					print "ERROR: rowcount is not a number rowcount = %s" % (rowcount)
					rowcount = 1
			except ValueError:		# rowcount is not found, therefore set rowcount to 0
				rowcount = 0
			try:
				t1 = string.index(tag, 'startrec="') + 10	#the startrec value can be a pinp value so it carries from page to page.
				try:
					startrec = string.atoi(tag[t1:(string.index(tag, '"', t1))])
				except ValueError:
					print "ERROR: startrec is not a number"
			except ValueError:		# startrec is not found, therefore set startrec to 0
				startrec = 0
			
			pobjdict = {"id" : id, "name" : name, "vars" : vars, "rowcount" : rowcount, "startrec" : startrec, "input" : info}
#			pobjdict = {"id" : id, "name" : name, "vars" : vars, "rowcount" : rowcount, "input" : info}
		except ValueError, err:
			print 'ERROR: missing pobj tag attribute for pobj %s <br>' % (tagdata[1:len(tagdata)-1])
	else:
		print "ERROR: we have bad data in pobj tag:  %s <br>" % (tagdata[1:len(tagdata)-1])
	return id, pobjdict


def getpobjtag(page):
#take a page and extract a single pobj tag, so it can be processed prior to getting the next pobj tag.
	err = ''
	b = 0
	e = 0
	
	b = string.find(page, '<pobj', e)
	if b <> -1:
		e = string.find(page, '</pobj>', b) + 7
		if e == -1:
			err = err + "error in getpobjtag - no end pobj tag"
		else:
			tagdata = page[b:e]
			id, tagdict = parseobjtag(tagdata)
	else:
		err = err + "error in getpobjtag - no pobj tag"
		id = ''
		tagdict = {}
		tagdata = ''
	return id, tagdict, tagdata, err


def parsetag(tagdata):
# take a tag like this: name="year" value="1999"
# and return a pinpval of the correct type and the default value
# this is called by getpinp and getppref
	
	error = ''
	
	tag = cleaner(tagdata)
	tag = string.replace(tag, 'default=', 'value=')
	namevalue = ''
	try:
		t1 = string.index(tag, 'name="') + 6
		name = tag[t1:(string.index(tag, '"', t1))]
		t1 = string.index(tag, 'value="') + 7
		defaultvalue = tag[t1:(string.index(tag, '"', t1))]
		if string.find(defaultvalue, '.') <> -1:	#if decimal use float, else use long int.
			try:
				namevalue =  string.atof(defaultvalue)
			except ValueError:
				namevalue = defaultvalue
		else:
			try:
				namevalue =  string.atol(defaultvalue)
			except ValueError:
				namevalue = defaultvalue
	except ValueError:
		print 'Pio_pageproce.parsetag: pinp/ppref ERROR name or value for %s' % (tagdata[1:len(tagdata)-2])
	return name, namevalue, error


def getpinp(page, showtag):
# take a page and extract all <pinp> tag data into a dictionary and list
# here is a sample: <pinp name="year" default="1999">  - note a type attribute is not yet implemented - loose typing.
	b = 0
	e = 0
	pinpdict = {}
	pinplist = []
	pinphaspinp_dict = {}
	haspinpentry = []
	while b > -1:
		b = string.find(page, '<pinp ', e)
		if b <> -1:
			e = string.find(page, '>', b + 6)
			if e == -1:
				print "error no end to pinp tag"
			elif e > b:
				tagdata = page[b:e]
				pinpname, pinpvalue, parseerror = parsetag(tagdata)
				while string.find(str(pinpvalue), '#pinp.') != -1:
					n = string.find(pinpvalue, '#pinp.')
					n1 = string.find(pinpvalue, '#', n + 1) +1
					if n1 != -1 and pinpvalue[n:n1] == '#pinp.*#':
						pinpvalue = string.replace(pinpvalue, '#pinp.*#', 'INVALID PINP in PINP TAG - pinp.* not allowed')
					elif n1== 0:
						pinpvalue = string.replace(pinpvalue, '#pinp.', 'MANGLED PINP PLACE TAG')
					else:
						haspinpentry.append(pinpvalue[n+6:n1-1] )
						pinpvalue = string.replace(pinpvalue, pinpvalue[n:n1], '#replacepinp.'+pinpvalue[n+6:n1-1] + '#')		#make #pinp.entryl# = #replacepinp.entry#
					
				if haspinpentry != []:
					pinphaspinp_dict[pinpname] = haspinpentry
					haspinpentry = []
				
				pinpdict[pinpname] = pinpvalue
				pinpdict[pinpname+'.quote'] = '"%s"' % (pinpvalue)		#add quoted dictionary entry
				pinplist.append(pinpname)
				pinplist.append(pinpname+'.quote')							#add quote entry
				tag = page[b:e+1]
				if showtag.upper() == 'YES':
					xtag = '<x' + tag[1:len(tag)]
					page = string.replace(page, tag, xtag)
				else:
					page = string.replace(page, tag, '')
				e = 0
	return pinpdict, pinplist, pinphaspinp_dict, page

def getppref(page, showtag):
# take a page and extract all <ppref> tag data into a dictionary
# here is a sample: <ppref pref="pobjautherror" value="ignore">  - note a type attribute is not yet implemented - loose typing.
	b = 0
	e = 0
	pprefdict = {}
	ppreflist = []
	while b > -1:
		b = string.find(page, '<ppref ', e)
		e = string.find(page, '>', b + 7)
		if b > -1 and e == -1:
			print "error no end to ppref tag"
		elif b > -1 and e > b:
			tagdata = page[b:e]
			pprefname, pprefvalue, parseerror = parsetag(tagdata)
			pprefdict[pprefname] = pprefvalue
			ppreflist.append(pprefname)
			tag = page[b:e+1]
			if pprefdict.has_key('showppref'):			#note, if showppref isn't first, it won't control if prior pprefs show or hide.
				if pprefdict["showppref"].upper() == 'YES':
					showtag = 'yes'
				else:
					showtag = 'no'
			
			if showtag.upper() == 'YES':
				xtag = '<x' + tag[1:len(tag)]
				page = string.replace(page, tag, xtag)
			else:
				page = string.replace(page, tag, '')
			e = 0
	return pprefdict, ppreflist, page



#debug stuff
#page = open('testpage.html').read()
#pinpdict, pinplist = getpinp(page)
#id, tagdict = getpobjtag(file)

