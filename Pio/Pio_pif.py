import string, re

def processpif(file):
	n = 0
	remembern = 0		#used for nested tags
	while n <> -1:
		piferr = ''		#clear out these fields so they don't carry over.
		pifelse = ''
		
		n = string.find(file, "<pif ", n)
		if n <> -1:
			n2 = string.find(file, "</pif>", n) + 6
			if n2 <> -1:
				#right here is where to add nested pif testing.
				nestn = string.find(file[n+4:n2], "<pif ")
				remembern = 0 + n
				while nestn != -1:		#find the innermost starting pif 
					n = n + 4 + nestn
					nestn = string.find(file[n+4:n2], "<pif ")
					
				piftag = file[n:n2]
#				print 'the piftag:%s\n<br>\n the file-remembern:n2: %s \n<br>\n' % (piftag, file[remembern:n2])
				s1 = string.find(piftag, 'stmt="', 0)
				s2 = string.find(piftag, '">', s1)
				if s2 == -1:
					s2 = string.find(piftag, '" >', s1)		# this adds a space after the dbl quote
				if s1 == -1:
					piferr = piferr + 'parse error: no stmt=" found in pif'
				elif s2 == -1:
					piferr = piferr + 'parse error: pif tag has no close eg. stmt="blahblah"&gt:'
				
				pifstmt = piftag[s1+6:s2]				
				#test for import here - do other security tests to prevent unauthorized code execution
				if string.find(pifstmt, 'import') != -1 or string.find(pifstmt, 'os.') != -1 or pifstmt[0:2] != 'if':
					piferr = "PIF statement error - reserved word (eg. import, ':')"
				
				if piferr == '':
					pifdata = file[n+s2+2:n2-6]
					i = string.find(pifdata, '<pelse>')
					if i <> -1:
						i1 = string.find(pifdata, '</pelse>', i)
						if i1 <> -1:
							pifelse = pifdata[i+7:i1]
							pifdata = string.replace(pifdata, pifdata[i:i1+8], '')
						else:
							piferr = piferr + 'parse error: pif-pelse has no closing /pelse tag:'
					
					answer = 'n'
					pifexec = pifstmt + ':  '  + 'answer = "y"'		
					try:
						exec pifexec
						if answer == 'y':
							file = string.replace(file, piftag, pifdata)
						else:
							file = string.replace(file, piftag, pifelse)
					except SyntaxError:
						piferr = piferr + '<br>error with pif stmt: %s ' % (pifstmt)
						piferr =  piferr + '<br>try making it more like this: "if 9 <= 10" where you replace the 9 or 10 with a #pinp.value# <br> Remember python if = is if =='
						file = string.replace(file, piftag, piferr)
					except NameError:
						piferr = piferr + '<br>error with pif stmt: %s ' % (pifstmt)
						piferr = piferr + '<br>You may not be putting your pif in qoutes...."#pif#"'
						file = string.replace(file, piftag, piferr)
				else:
					file = string.replace(file, piftag, piferr)
#					file = re.sub(piftag, piferr, file, count = 1)
				n = 0 + remembern
			else:
				piferr = piferr + '<b>pif has no closing tag &lt;/pif&gt;<b>'
				file = file[0:n] + piferr + file[n:len(file)]
				n = 0 + remembern
#			print 'n = %s \n<br>\n' % (n)
	return file

def processpvif(file):
	n = 0
	remembern = 0		#used for nested tags
	while n <> -1:
		pviferr = ''
		pvifelse = ''
		pvifdata = ''
		
		n = string.find(file, "<pvif ", n)
		if n <> -1:
			n2 = string.find(file, "</pvif>", n) + 7
			if n2 <> -1:
				#right here is where to add nested testing.
				nestn = string.find(file[n+5:n2], "<pvif ")
				remembern = 0 + n
				while nestn != -1:		#find the innermost starting pvif 
					n = n + 5 + nestn
					nestn = string.find(file[n+5:n2], "<pvif ")
					
				pviftag = file[n:n2]
				s1 = string.find(pviftag, 'stmt="', 0)
				if s1 == -1:
					pviferr = pviferr + 'parse error: no stmt=" found in pvif'
				else:
					s2 = string.find(pviftag, '">', s1)
					if s2 == -1:
						s2 = string.find(pviftag, '" >', s1)		# this adds a space after the dbl quote
					elif s2 == -1:
						pviferr = pviferr + 'parse error: pvif tag has no close eg. stmt="blahblah"&gt:'
				
				pvifstmt = pviftag[s1+6:s2]
				#test for import here - do other security tests to prevent unauthorized code execution
				if string.find(pvifstmt, ':') != -1 or string.find(pvifstmt, 'import') != -1 or string.find(pvifstmt, 'os.') != -1 or pvifstmt[0:2] != 'if':
					piferr = "PVIF statement error - reserved word (eg. import, ':') or does not begin with if"
				
				if pviferr == '':
					pvifdata = file[n+s2+2:n2-7]
					i = string.find(pvifdata, '<pvelse>')
					if i <> -1:
						i1 = string.find(pvifdata, '</pvelse>', i)
						if i1 <> -1:
							pvifelse = pvifdata[i+8:i1]
							pvifdata = string.replace(pvifdata, pvifdata[i:i1+9], '')		#blank out the pvelse part of pvifdata
						else:
							pviferr = pviferr + 'parse error: pvif-pvelse has no closing /pvelse tag:'
					
					answer = "n"
					pvifexec = pvifstmt + ':  '  + 'answer = "y"'		
					try:
						exec pvifexec
						if answer == 'y':
							file = string.replace(file, pviftag, pvifdata)
						else:
							file = string.replace(file, pviftag, pvifelse)
					except SyntaxError:
						pvifstmtfix = string.replace(pvifstmt, '<', '&lt')
						pvifstmtfix = string.replace(pvifstmt, '>', '&gt')
						pviferr = pviferr + '<br>SyntaxError with pvif stmt: %s ' % (pvifstmtfix)
						pviferr = pviferr + '<br>try making it more like this: "if 9 &lt= 10" where you replace the 9 or 10 with a pval.pobjid.var.no <br>'
						pviferr = pviferr + 'other things to consider, is your pval returning a string instead of a number (or vice versa)?<br>'
						pviferr = pviferr + 'Remember python if = is if =='
						file = string.replace(file, pviftag, pviferr, 1)
					except NameError:
						pviferr = pviferr + '<br>error with pvif stmt: %s ' % (pvifstmt)
						pviferr =  pviferr + '<br>You may not be putting your pvar in qoutes...."#pvar#"'
						file = string.replace(file, pviftag, pviferr, 1)
				else:
					file = string.replace(file, pviftag, pviferr, 1)
				n = 0 + remembern
			else:
				pviferr = pviferr + '<b>pvif has no closing tag &lt;/pvif&gt;<b>'
				file = file[0:n] + pviferr + file[n:len(file)]
				n = 0 + remembern
	return file

def processpmath(file, end):
	n = 0
	while n <> -1:
		pmatherr = ''		#clear out these fields so they don't carry over.
		
		n = string.find(file, "<pmath ", n)
		if n <> -1:
			
			n2 = string.find(file, ">", n )+ 1
			if n2 <> -1:
				pmathtag = file[n:n2]
				if string.find(pmathtag, '<pval') == -1 and string.find(pmathtag, '#') == -1:		#this is to get passed pmaths with pvals in them.
	#				print 'pval?' + str(string.find(pmathtag, '<pval')) +pmathtag[1:len(pmathtag)-1] + "end:" + end			#testing line
					s1 = string.find(pmathtag, 'stmt="', 0)
					s2 = string.find(pmathtag, '">', s1)
					if s2 == -1:
						s2 = string.find(pmathtag, '" >', s1)		# this adds a space after the dbl quote
					if s1 == -1:
						pmatherr = pmatherr + 'parse error: no stmt=" found in pmath'
					elif s2 == -1:
						pmatherr = pmatherr + 'parse error: pmath tag has no close eg. stmt="blahblah"&gt '
					
					if pmatherr == '':
						pmathstmt = pmathtag[s1+6:s2]
	#					print pmathstmt									#testing line
						answer = "Error"
						pmathexec = 'answer = (' + pmathstmt + ')'	
						try:
							exec pmathexec
							if answer <> 'Error':
								file = string.replace(file, pmathtag, str(answer))
							else:
								file = string.replace(file, pmathtag, 'pio Error in pmath')
						except SyntaxError:
							if end.upper() == 'END':
								pmatherr = pmatherr + '<br>error with pmath stmt: %s ' % (pmathstmt)
#								file = re.sub(pmathtag, pmatherr, file, count = 1)
								file = string.replace(file, pmathtag, pmatherr)
						except NameError:
							if end.upper() == 'END':
								pmatherr = pmatherr + '<br>error with pmath stmt: %s ' % (pmathstmt)
								file = string.replace(file, pmathtag, pmatherr)
#								file = re.sub(pmathtag, pmatherr, file, count = 1)
						except TypeError:
							if end.upper() == 'END':
								pmatherr = pmatherr + '<br>error with pmath stmt: %s ...possible empty values' % (pmathstmt)
								file = string.replace(file, pmathtag, pmatherr)
								file = re.sub(pmathtag, pmatherr, file, count = 1)
#					else:
#						file = re.sub(pmathtag, pmatherr, file, count = 1)
						file = string.replace(file, pmathtag, pmatherr)
			else:
				pmatherr = pmatherr + '<b>pmath has no closing tag &lt;/pmath&gt;<b>'
				file = file[0:n] + pmatherr + file[n:len(file)]
			
			n = n + 6		#to get next pmathtag...if looping...look here at the file re.subs - string.replaces (re sucks and breaks)
	return file

def pstring(file):
	#pstring must be formatted like <pstring function="replace('sometext', 'newtext')">the string to run a string function</pstring>
	#the <pstring> tag is processed and leaves in the resulting value in it's place
	#it should be possible to nest pstrings, so <pstring> tags can contain <pstring> tags. It looks bad in the html, but it should work just fine.
	#pstrings are processed at the end of page processing
	n = 0
	remembern = 0		#used for nested tags
	while n <> -1:
		ptagerr = ''
		pstringfunction = ''
		pstring = ''
		
		n = string.find(file, "<pstring ", n)
		if n <> -1:
			n2 = string.find(file, "</pstring>", n) + 10
			if n2 <> -1:
				#right here is where to add nested testing.
				nestn = string.find(file[n+8:n2], "<pstring ")
				remembern = 0 + n
				while nestn != -1:		#find the innermost starting pstring 
					n = n + 8 + nestn
					nestn = string.find(file[n+8:n2], "<pstring ")
					
				ptag = file[n:n2]
				s1 = string.find(ptag, 'function="', 0)
				if s1 == -1:
					ptagerr = ptagerr + 'parse error: no function=" found in pstring'
				else:
					s2 = string.find(ptag, '">', s1)
					if s2 == -1:
						s2 = string.find(ptag, '" >', s1)		# this adds a space after the dbl quote
					elif s2 == -1:
						ptagerr = ptagerr + 'parse error: pstring tag has no close "&gt:"  eg. function="blahblah"&gt:'
				
				pstringfunction = ptag[s1+10:s2]
				
				if ptagerr == '':
					pstring = file[n+s2+2:n2-10]
					
					newpstring = ''
					pstringexec =  'newpstring = pstring.' + pstringfunction 
					try:
						exec pstringexec
						file = string.replace(file, ptag, newpstring)
					except SyntaxError:
						ptagerr = ptagerr + '<br>SyntaxError with pstring function: %s ' % (pstringfunction)
						ptagerr = ptagerr + '<br>try your function in python and see if it works.'
						file = string.replace(file, ptag, ptagerr, 1)
					except AttributeError, e:
						ptagerr = ptagerr + '<br>AttributeError with pstring function: %s ' % (pstringfunction)
						ptagerr = ptagerr + '<br>%s ' % str(e) 
						file = string.replace(file, ptag, ptagerr, 1)
				else:
					file = string.replace(file, ptag, ptagerr, 1)
				n = 0 + remembern
			else:
				ptagerr = ptagerr + '<b>pstring has no closing tag &lt;/pstring&gt;<b>'
				file = file[0:n] + ptagerr + file[n:len(file)]
				n = 0 + remembern
	return file

