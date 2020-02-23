import string, re


#				print 'pvalvarnam:%s, pvalrecnmbr:%s, pvalalt:%s, pvalrepl:%s, pvalvarnamrepl:%s, pobjid:%s<br>' % (pvalvarnam, pvalrecnmbrint, pvalalt, pvalrepl, pvalvarnamrepl, pobjid)
#				print '<b>Mojo Jo Jo</b> %s end %s<br>' % (vardict[pvalvarnam], pobjid)

#	update vardict
# if I update the dictionary, I can simply grab the value out of the dictionary as I find the pval. 
# find tag <pval.id.....>...</pval>
#	get varname, pvalrec#, pvalalt, pvalrepl (list)
#	if vardict.has_key[varname] get vardictrcd
#		if pvaltag has row id get vardictrcd row id.
#			replace pval data with vardict:vardictrcd   OR  with alt tag data  OR   just delete pval
#	
#	if records == ():
#		#do replacement routine
#	else:
#		if len(records[0]) >= len(varlist):
#			#record count is GE to varlist count
#			#varlist matching by number ok.
#			


def do_valstring(valstring):		
#take a valstring like <pval.pobjid.varnam.recnmbr>here is some data #varnam# data<palt>alternate data</palt>smurf</pval>
#note, the "smurf" following </palt> will get lost.
	
	pvalvarnam = ''			#here default values are set.
	pvalrecnmbr =''
	pvalalt = ''
	pvalrepl = ''		#this is the default value.  pvalrepl is blank if no #...# value is found inside it 
#	pvalvarnamrepl = ''		#this is when there is a #varname# value is found between the pval open/close tags 
	
	v1 = string.find(valstring, '>', 5)		#find ">" after "<pval"
	if v1 <> -1:										# does pval have closing >?
		valtag = valstring[0:v1+1]				#<pval.pobjid.varnam.recnmbr>
		valtaglist = re.split('\.', valtag)		#split out the valtag into it's bits
		if len(valtaglist) == 4:
			pvalvarnam = valtaglist[2]
			pvalrecnmbr = str(valtaglist[3])[0:len(str(valtaglist[3])) - 1]		#get rid of ending '>'
			if pvalrecnmbr == '':
				pvalrecnmbr = '*'
			pvaldata = valstring[v1+1:len(valstring) - 7]								#here we strip out "</pval>"
			
			pvaldatasplit = re.split('<palt>', pvaldata)									#break out the pvaldatarepl and the pvalalt
			pvaldatarepl = pvaldatasplit[0]
			if len(pvaldatasplit) > 1:
				valalt = re.split('</palt>', pvaldatasplit[1])
				pvalalt = valalt[0]
			
			if pvalvarnam[0] == '*':			#e.g. <pval.pobjid.*.*>
				pvalvarnamrepl = ''					#default value if pvalvarnam = *
				vn1 = string.find(pvaldatarepl, '#')
				if vn1 <> -1:
					vn2 = string.find(pvaldatarepl, '#', vn1+1)
					if vn2 <> -1:
						if string.find(pvaldatarepl[vn1:vn2+1], '#-') == -1:			#does the pvaldatarepl string subset contain #-  used for minuslist (subsets of varlist)
							if string.find(pvaldatarepl[vn1:vn2+1], '#*#') == -1:	#does the string contain #*#...meaning get whole list.
								pvalvarnamrepl = '###'		# #*# not found.  Data string has at least one value between # #, that is not #*# and not #-.....#
							else:
								pvalvarnamrepl = '#*#'		#  #*# found.  Pvalvarnamrepl is set to #*#, this is used later for testing and searching.
						else:
							pvalvarnamrepl = '#*-#'		#if pvaldatarepl has a "#-......#" then the pvalvarnamrepl is set to #*-#, this is used later for testing and searching. for minuslists-subsets of the varlists
						pvalrepl = pvaldatarepl
			else:			#e.g. <pval.pobjid.varnam.0> or <pval.pobjid.varnam.*>
				pvalvarnamrepl = '#%s#' % (pvalvarnam)
				r1 = string.find(pvaldatarepl, pvalvarnamrepl)		#test for a valid pvalrepl string. 
				if r1<> -1:															#a valid pvalrepl string has a #varnam# value in it, or it has #.....# somewhere in it which is tested for above. 
					pvalrepl = pvaldatarepl
		else:
			pvalrepl = 'Error with pval - does not have 4 bits eg. pval.pobj.varnam.row::: %s' % (valtag[1:len(valtag)-1] )
			pvalvarnamrepl = pvalrepl
#notice that the pvalrepl value is only changed from '' if it meets criteria.
##	print 'output of do_valstring: pvalvarnam:%s, pvalrecnmbr:%s, pvalalt:%s, pvalrepl:%s, pvalvarnamrepl:%s<br>' % (pvalvarnam, pvalrecnmbr, pvalalt, pvalrepl, pvalvarnamrepl)
	return pvalvarnam, pvalrecnmbr, pvalalt, pvalrepl, pvalvarnamrepl

def clearpval(file):
	repldata = ''
	pvalbeg = '<pval.'
	p1 = 0
	p2 = 0
	while p1 <> -1:
		p1 = 0
		p2 = 0
		p1 = string.find(file, pvalbeg, p2)
		if p1 <> -1:					#found a matching pval
			p2 = string.find(file, '</pval>', p1)
			if p2 <> -1:				#found a pval closing tag matching the pval.
				#right here is where to add nested pval testing.  we clear out nested pvals safely. nested pvals can be processed safely by properly sequenced pobjs.
				nestp1 = string.find(file[p1+5:p2], pvalbeg)
				while nestp1 != -1:		#find the innermost starting pval 
#					print "nestp1: %s" % (str(nestp1))
					p1 = p1 + 4 + nestp1
					nestp1 = string.find(file[p1+5:p2], pvalbeg)
				
				valstring = file[p1:p2+7]
				v1 = string.find(valstring, '>', 5)
				if v1 <> -1:			# does pval have closing >?
					valtag = valstring[0:v1+1]
#					print  'blah' + valstring + 'blah<br>'		#testing for error with pval inside a pval
					has_pval_inside = string.find(valstring[3:p2], '<pval')
#nest					if has_pval_inside == -1:
					varnam, pvalrec, pvalalt, pvalrepl, varnamrepl = do_valstring(valstring)
#nest					else:
#nest						print '<b>****Pval  has pval string inside it!****</b> <br>Pval= %s<br><br>' % (valstring[1:p2])
					repldata = pvalalt		#use alt tag for missing pobj pval
#repl data using comments is bad in forms!
#						repldata = '<!-- Missing POBJ for %s -->  %s' % (valtag[1:len(valtag)-1], pvalalt)
#					else:
#						repldata = '<!-- Missing POBJ for pval.%s -->' % (valtag[1:len(valtag)-1])
				else:
					repldata = '<!-- Missing POBJ for pval.%s... -->' % (file[p1+1:p1+10])
				file = string.replace(file, valstring, repldata, 1)
	return file

def do_pvalonevar(pvalvarnam, pvalrecnmbrint, pvalalt, pvalrepl, pvalvarnamrepl, vardict, varlist, pobjid):				#e.g. <pval.pobjid.varnam.3>   an actual pvalvarnam with a pvalrecnmbr integer
	if vardict.has_key(pvalvarnam):									#for this pval, the varnam has a matching vardict key
		vardictrec = vardict[pvalvarnam]								#get one columns/vars data
		if len(vardictrec) >= pvalrecnmbrint + 1:						#if the number of records for that var is greater than the pval record number ie, there is row# matching the pvalrecnmbr
			rec = vardictrec[pvalrecnmbrint]							#get the record
			if rec == '' or rec == None or rec == 'None' or rec == 'none' or rec == 'NONE' or rec == () or rec ==[]:
				repldata = pvalalt					#if rec is blank or none, use pvalalt
			else:
				if pvalrepl == '':						#if pvalrepl is '' (that is it has no pvalvarnamrepl in it), the repldata is the record
					repldata = str(rec)
				else:										#otherwise if the pvalrepl is not '' (that is it has #varnam# in it), do string replace to keep the tagdata filling in the varnam/row value
					repldata = string.replace(pvalrepl, pvalvarnamrepl, str(rec))
		else:
			repldata = pvalalt
	else:
		repldata = pvalalt
	
	return repldata

def do_manytype(manytype, data1, data2, dataset):	
	#Data1/2 is for handling formats/br/commas/rows between data...Dataset is for handling, rowbr/table/tableheader leave one blank.
#	print 'dataset=%s, data1=%s, data2=%s, manytype=%s' % (dataset, data1, data2, manytype.upper())
	if dataset == '':
		returndata = data1 + data2
		
		if manytype.upper()[0:7] == '*LISTBR' or manytype.upper()[0:3] == '*BR' or manytype.upper()[0:11] == '*BRHEADER' or manytype.upper()[0:11] == '*LISTHEADER':
			returndata = data1 + data2 + '<br>'
		elif  manytype.upper()[0:10] == '*LISTCOMMA' or manytype.upper()[0:6] == '*COMMA':
			if data1 <> '':
				returndata = data1 + ', ' + data2
			else:
				returndata = data2
		elif  manytype.upper()[0:6] == '*SPACE':
			if data1 <> '':
				returndata = data1 + data2 + ' '
			else:
				returndata = data2
		elif manytype.upper()[0:6] == '*TABLE' or manytype.upper()[0:5] == '*ROWS':
			if data2 == '':
				returndata = '<tr><td>%s</td></tr>' % (data1)		#this is for pvalonevarlist - every row for that var has a tr and td
			else:
				returndata = data1 + '<td>%s</td>' % (data2)			#this is for allvarlists - every col has a td, the tr is handled in do_row
		else:
			returndata = data1 + data2
		
	else:			#here we do the dataset
		returndata = dataset
		
		if string.find(manytype.upper(), 'ROWBR') <> -1:
			returndata = dataset + '<br>'
		elif manytype.upper() == '*TABLEHEADER':		#for tableheader, get the header from data1.
			header = '<tr>%s</tr>' % (data1)		#use data one for the header row.
			returndata = header + dataset
			returndata = '<table>' + returndata + '</table>'
		elif manytype.upper()[0:12] == '*LISTHEADER':		#for listheaderr, get the header from data1.
			header = data1													#use data one for the header row.
			returndata = '<br>' + header +'<br>' + dataset
		elif manytype.upper() == '*TABLE':
			returndata = '<table>' + dataset + '</table>'
		
	
	return returndata


def do_row(rowlist, rowlistdata, manytype):
	row = ''
	n = 0
	for i in rowlist:
		rowdata = rowlistdata[n]
		row = do_manytype(manytype, row, rowdata, '')
		n = n + 1
	
	if string.find(manytype.upper(), 'ROWBR') <> -1:			#I don't do this with do_manytype because manytype would do the table bits too!, so I handle rowbr here.
		row = row + '<br>'
	
	if manytype.upper()[0:6] == '*TABLE' or manytype.upper()[0:5] == '*ROWS':
		row = '<tr>%s</tr>' % (row)		#this is for pvalallvarlist - every row needs tr added to it.
	
	return row

def get_minuslist(varlist, pvalrepl):
	minuslist = (varlist[0:len(varlist)])
	
#	print '<br>Here is opening pvalrepl=%s <br>' % (pvalrepl)
	minusstring = '#*-#'		#because this is a minus list (pvalvarnamrepl = #*-#), the minus lists should always be loaded below.
	
	dominuslist1 = string.find(pvalrepl, '#-')										#this whole section is to deal with pvalrepl that have #-var1-var2-var4#
	if dominuslist1 <> -1:
		dominuslist2 = string.find(pvalrepl, '#', dominuslist1 + 2)
		if dominuslist2 <> -1:
			splitstring =  pvalrepl[dominuslist1+1:dominuslist2]
			minusstring = pvalrepl[dominuslist1:dominuslist2 + 1]		#this is used to do replaces in the other modules
			minussplit = re.split('-', splitstring)
			minussplit.remove('')
			n = 0
			for i in minussplit:
				try:
					minuslist.remove(minussplit[n])
					n = n + 1
				except ValueError:
					n = n + 1
	return minuslist, minusstring


def do_pvalonevarlist(pvalvarnam, pvalrecnmbr, pvalalt, pvalrepl, pvalvarnamrepl, vardict, varlist):			#e.g. <pval.pobjid.varnam.*>
	
	repldata = ''			#because this is a list, the replace data becomes a string where each row of the varnam is added to.
	
	if vardict.has_key(pvalvarnam):									#for this pval, the varnam has a matching vardict key
		vardictrec = vardict[pvalvarnam]								#get one columns/vars data
		n = 0
		for a in vardictrec:
			if vardictrec[n] == '' or vardictrec[n] == None or vardictrec[n] == 'None' or vardictrec[n] == 'none' or vardictrec[n] == 'NONE' or vardictrec[n] == () or vardictrec[n] ==[]:
				rec = pvalalt					#if the record is blank or none, use pvalalt
			else:
				if pvalrepl == '':						#if pvalrepl is '' (that is it has no pvalvarnamrepl in it), the repldata is the record
					rec =str(vardictrec[n])
				else:										#otherwise if the pvalrepl is not '' (that is it has #varnam# in it), do string replace to keep the tagdata filling in the varnam/row value
					rec =string.replace(pvalrepl, pvalvarnamrepl, str(vardictrec[n]))
			
			if pvalrecnmbr <> '*':		#that is it's '*comma' or '*table' etc.
				rec = do_manytype(pvalrecnmbr, rec, '', '')		#manytype process for data			(do list, listbr, comma, space, table datarows (for lists) etc)
			repldata = repldata + rec
			n = n + 1
		
		if pvalrecnmbr <> '*':																		#manytype process for dataset	(process rowbr, table, tableheader etc)
			repldata = do_manytype(pvalrecnmbr, pvalvarnam, '', repldata)		#pvalvarnam is data1 for getting  a header row.
		
	else:
		repldata = pvalalt		#this is because the pvalvarnam is not in the vardict.
		
	return repldata


def do_pvallistonerow(pvalvarnam, pvalrecnmbrint, pvalalt, pvalrepl, pvalvarnamrepl, vardict, varlist):		#
#pval.pobjid.*.3   or pval.pobjid.*comma.0  No funky formatting is allowed except between varnams because this can not really produce a table of records (and I'm having a hard time getting it to work!!!!!)
#if special formatting is desired, do it inside the pvalrepl

	
	manytype = pvalvarnam
	replrow = pvalalt				#if replrow does not get reset, it will be pvalalt
#	print '<b>Mojo jo jo<br>pvalvarnamrepl=%s, pvalvarnam=%s, pvalrecnmbrint=%s, pvalrepl=%s</b><br>' % (pvalvarnamrepl, pvalvarnam, pvalrecnmbrint, pvalrepl)
	
	if len(vardict[varlist[0]]) >= pvalrecnmbrint + 1:		#make sure there is a vardict entry for the recnmbr.
		
		if pvalrepl <> '' and pvalvarnamrepl == '###':		#the pvalrepl has specific #varnam# values...<pval.pobjid.*.3>smurf loves #smurfname# and hates gargamel<palt>No such smurf</palt></pval>
			repllist = []														#create a list of the used varnams
			n = 0
			for i in varlist:
				varlistnrepl = '#%s#' % (varlist[n])
				if string.find(pvalrepl, varlistnrepl) <> -1:		#If varlist[n] is found in pvalrepl add it to the replace list (repllist)
					repllist.append(varlist[n])
				n = n + 1
			if repllist == []:				#that is, no vars were found
				pvalrepl = ''				#so clear the pvalrepl as it contains bogus data, this will cause it to be processed with all varnams below
			else:
				row = pvalrepl
				n = 0
				for r in repllist:					#for each entry of the replace list
					repldata = (str(vardict[repllist[n]][pvalrecnmbrint]))
					replstring =  '#%s#' % (repllist[n])
					row = string.replace(row, replstring, repldata)			#here an individual row has #varnam# replaced with actual data
					n = n + 1
				replrow = row
				
		#------- minuslist section
		if pvalvarnamrepl == '#*-#':			#pval.pobjid.*.3 where pvalrepl has #-varnam-varnam# inside it.
			replrow = ''
			minuslist, minusstring = get_minuslist(varlist, pvalrepl)
			if minuslist <> []:				#it is possible to minus everything, in which case what?...it will fallout as a pvalalt at the end?
				minuslistdata = []
				n = 0
				for i in minuslist:
					minuslistdata.append(str(vardict[minuslist[n]][pvalrecnmbrint]))
					n = n + 1
				row = do_row(minuslist, minuslistdata, manytype)		#here we make the row for the minus list, a varlist minus the #-var1-var2# etc.
				if pvalrepl == '':					#if pvalrepl = blank the row is replrow, else, replace #-varnam-varnam# with row.
					replrow = row
				else:
					replrow = string.replace(pvalrepl, minusstring, row, 1)
			else:									#If the minuslist is [] use pvalalt
				replrow = pvalalt
		#------- minuslist section end
		
		#------- get all vars for row, use table if requested section
		if pvalvarnamrepl == '#*#' or  pvalvarnamrepl == '' and pvalvarnam[0] == '*':		#get all vars for this recnmbr
			varlistdata = []
			n = 0
			for i in varlist:
				varlistdata.append(str(vardict[varlist[n]][pvalrecnmbrint]))
				n = n + 1
			row = do_row(varlist, varlistdata, manytype)					#go get the row for #*# or for an empty pvalrepl, this is the replrow, not just another row.
			if pvalrepl == '':
				replrow = row
			else:
				replrow = string.replace(pvalrepl, '#*#', row, 1)
	
	
	return replrow


def do_pvallistallvar(pvalvarnam, pvalrecnmbr, pvalalt, pvalrepl, pvalvarnamrepl, vardict, varlist):
#	print '<b>varlist=%s, pvalrepl=%s, pvalvarnamrepl=%s, pvalvarnam=%s, pvalrecnmbr=%s</b><br>' % (str(varlist), pvalrepl, pvalvarnamrepl, pvalvarnam, pvalrecnmbr)
	repldata = pvalalt
	rownmbr = 0
	manytype = pvalrecnmbr		#eg *TABLE, *COMMAROWBR
	
	if pvalrepl <> '' and pvalvarnamrepl == '###':		#the pvalrepl has specific #varnam# values headers don't work for this.
		
		repllist = []							#create a list of the used varnams
		n = 0
		for i in varlist:
			varlistnrepl = '#%s#' % (varlist[n])
			if string.find(pvalrepl, varlistnrepl) <> -1:
				repllist.append(varlist[n])
			n = n + 1
		
		if repllist == []:		#that is, no vars were found
			pvalrepl = ''		#so clear the pvalrepl as it contains bogus data this will cause it to be processed with all varnams below
		else:						#otherwise continue processing
			rownmbr = 0
			replrow = ''
			for r in vardict[varlist[0]]:		#for each entry of vardict entry 0, (so for every record returned) 
				varnmbr = 0
				row = pvalrepl
				for i in repllist:
					repldata = (str(vardict[repllist[varnmbr]][rownmbr]))
					replstring =  '#%s#' % (repllist[varnmbr])
					row = string.replace(row, replstring, repldata)			#here an individual row has #varnam# replaced with actual data
					varnmbr = varnmbr + 1
				replrow = replrow + row															#here is where the replrow is made
				rownmbr = rownmbr + 1
			
			repldata = replrow
	
	
	if pvalrepl <> '' and pvalvarnamrepl == '#*-#':		#handle gettting the minustable/list
		replrow = ''
		minuslist, minusstring = get_minuslist(varlist, pvalrepl)
		if minuslist == []:				#it is possible to minus everything, or have no valid minus values
			pvalrepl = ''
		else:
			rownmbr = 0
			replrow = ''
			for r in vardict[varlist[0]]:		#for each entry of vardict entry 0, (so for every record returned) 
				minuslistdata = []
				n = 0
#				print '<b>varlist=%s, pvalrepl=%s, pvalvarnamrepl=%s, pvalvarnam=%s, pvalrecnmbr=%s</b><br>' % (str(varlist), pvalrepl, pvalvarnamrepl, pvalvarnam, pvalrecnmbr)
				for i in minuslist:					#create the minuslistdata list for getting the row data.
					minuslistdata.append(str(vardict[minuslist[n]][rownmbr]))
					n = n + 1
				row = do_row(minuslist, minuslistdata, manytype)		#here we make the row for the minus list, a varlist minus the #-var1-var2# etc.
				row = string.replace(pvalrepl, minusstring, row)
				replrow = replrow + str(row)
				rownmbr = rownmbr + 1
			header = do_row(minuslist, minuslist, manytype)			#get the minuslist header using the minuslist
			header = string.replace(pvalrepl, minusstring, header)
			repldata = do_manytype(pvalrecnmbr, header, '', replrow)		#manytype process for data			(do list, listbr, comma, space, table datarows (for lists) etc)
	
	if pvalrepl <> '' and pvalvarnamrepl == '#*#' or pvalrepl == '':		#the pvalrepl has no specific #varnam# or #-varnams
		rownmbr = 0
		replrow = ''
		for i in vardict[varlist[0]]:		#for each entry of vardict entry 0, (so for every record returned) 
			varlistdata = []
			n = 0
			for i in varlist:					#create the varlistdata list for getting the row data.
				varlistdata.append(str(vardict[varlist[n]][rownmbr]))
				n = n + 1
			row = do_row(varlist, varlistdata, manytype)		#here we make the row for each varlist
			if pvalvarnamrepl == '#*#':
				row = string.replace(pvalrepl, pvalvarnamrepl, row)
			replrow = replrow + str(row)
			rownmbr = rownmbr + 1
		header = do_row(varlist, varlist, manytype)		#here we make the header row
		repldata = do_manytype(pvalrecnmbr, header, '', replrow)	
#		print '<b>manytype=%s, header=%s replrow=%s, repldata=%s</b>end<br>' % (manytype, header, replrow, repldata)
	
	return repldata



def dopval(file, records, pobjid, rowcount, vardict, varlist, startrec, nextrecnmbr):
	
	testtuple = ('a', 'b', 'c')
	testlist = ['a', 'b', 'c']
	teststring = 'abc'
	testint = 1
	
###	update vardict with values from returned records
	vn = 0
	if records <> ():					#no empty set records
		for n in varlist:						#the varlist is the same as the column list from the query -> vars = columns
			if len(records) >= 1:			#list records
				rn = 0							# rn = recnmbr
				vardictdata = []			#create a list to hold the column data from each record.
				for n in records:
					try:
						vardictdata.append(records[rn][vn])			#add the records numbers column data to vardictdata
					except IndexError:										#i'm guessing this exception is to catch empty column/record values.
						vardictdata.append('')
					rn = rn + 1				#add to get next recnmbr
				vardict[varlist[vn]] = vardictdata						#put all the vardictdata (the list of all record data for that column) into the vardict.
##				print 'FOR POBJID: %s<br>THE VARDICT:%s<br>' % (pobjid, str(vardict))
				
#			elif len(records) == 1:		#one record only
#				print 'FOR POBJID: %s<br>THE VARDICT:%s<br>' % (pobjid, str(vardict))
#				vardict[varlist[vn]] = records[0][vn]
			vn = vn + 1												#add 1 to vn for loop to next var
	#else:
		# do nothing leaving vardict with blanks for empty set records.
	
	repldata = ''
	pvallist = []
	pvalbeg = '<pval.%s.' % (pobjid)
	p1 = 0
	p2 = 0
	while p1 <> -1:		# for all the pvals for that pobjid
		p1 = string.find(file, pvalbeg, p2)
		if p1 <> -1:					#found a matching pval
			p2 = string.find(file, '</pval>', p1)
			
			#nested pvals are processed by matching up beginning and end values
			if p2 <> -1:				#found a pval closing tag matching the pval.
				pvalinside = file[p1+5:p2].find('<pval')
				if pvalinside != -1:		#check and process pval nesting
					while len(file[p1:p2+7].split('<pval')) != len(file[p1:p2+7].split('</pval>')) and p2 != -1:
						p2 = file.find('</pval>', p2+7)		#p2 is set to -1 if no end /pval tag is found.
					
				
			
			if p2 <> -1:				#found a pval closing tag matching the pval.
				valstring = file[p1:p2+7]
#nest				has_pval_inside = string.find(valstring[3:p2], '<pval')
#nest				if has_pval_inside == -1:
				pvallist.append(valstring)
				pvalvarnam, pvalrecnmbr, pvalalt, pvalrepl, pvalvarnamrepl = do_valstring(valstring)
#nest				else:
#nest					print '<b>****Pval has Unprocessed pval string inside it!****  Nested pvals must be processed by prior pobjs</b> <br>Pval= %s<br><br>' % (valstring[1:p2])
#------- 
				###below are the testing lines.   Insert them anywhere to see if that bit of code is getting hit, and what the values of things are. 
				###print 'pvalvarnam:%s, pvalrecnmbr:%s, pvalalt:%s, pvalrepl:%s, pvalvarnamrepl:%s, pobjid:%s<br>' % (pvalvarnam, pvalrecnmbr, pvalalt, pvalrepl, pvalvarnamrepl, pobjid)
				###print '<br>valstring:%s <br>' % (valstring)
#replval = 'Mojo JoJo needs a haircut!'
#print "<b>Mojo Jo Jo</b><br>"

#------- 
				if pvalvarnam[0] == '*':
					if pvalrecnmbr[0] == '*':			#this is  <pval.pobjid.*.*>
						repldata = do_pvallistallvar(pvalvarnam, pvalrecnmbr, pvalalt, pvalrepl, pvalvarnamrepl, vardict, varlist)
					elif pvalrecnmbr.upper() == 'PIO_LAST':
						try:
							pvalrecnmbrint = rowcount -1		#pval rec becomes a number
							if pvalrecnmbrint < 0:
								pvalrecnmbrint = 0
							repldata = do_pvallistonerow(pvalvarnam, pvalrecnmbrint, pvalalt, pvalrepl, pvalvarnamrepl, vardict, varlist)
						except ValueError:		#since pvalrecnmbr is not a number and does not start with an *
							repldata = pvalalt
					elif pvalrecnmbr.upper() == 'PIO_FIRST':
						try:
							pvalrecnmbrint = startrec 		#pval rec becomes a number
							repldata = do_pvallistonerow(pvalvarnam, pvalrecnmbrint, pvalalt, pvalrepl, pvalvarnamrepl, vardict, varlist)
						except ValueError:		#since pvalrecnmbr is not a number and does not start with an *
							repldata = pvalalt
					else:											#this is  <pval.pobjid.*.5>
						try:
							pvalrecnmbrint = string.atoi(pvalrecnmbr)		#pval rec becomes a number
							repldata = do_pvallistonerow(pvalvarnam, pvalrecnmbrint, pvalalt, pvalrepl, pvalvarnamrepl, vardict, varlist)
						except ValueError:		#since pvalrecnmbr is not a number and does not start with an *
							repldata = pvalalt
						
				elif pvalvarnam.upper() == 'PIO_ROW':		#get row/record count information for next/previous/rowcount/rowposition.
				#return information to pvals like <pval.pobjid.Pio_row.count></pval> or <pval.pobjid.Pio_row.position></pval>
					if pvalrecnmbr.upper() == 'COUNT' or pvalrecnmbr.upper() == 'RETURNED':
						if pvalrepl == '':
							repldata = str(len(records))
						else:
							repldata = string.replace(pvalrepl, pvalvarnamrepl, str(len(records)))
						
					elif pvalrecnmbr.upper() == 'NUMBER' or pvalrecnmbr.upper() == 'POSITION':
						repldata = str(startrec + len(records))
						if pvalrepl <> '':
							repldata = string.replace(pvalrepl, pvalvarnamrepl, str(startrec + len(records)))
						
					elif pvalrecnmbr.upper() == 'NEXT':
						next = startrec + len(records)
						if nextrecnmbr <= rowcount:		
							next = 0
						repldata = str(next)
						if pvalrepl <> '':
							repldata = string.replace(pvalrepl, pvalvarnamrepl, str(next))
						
					elif pvalrecnmbr.upper() == 'PREVIOUS' or pvalrecnmbr.upper() == 'LAST':
						previous = startrec - rowcount
						if previous <= 0:
							previous = 0
						repldata = str(previous)
						if pvalrepl <> '':
							repldata = string.replace(pvalrepl, pvalvarnamrepl, str(previous))
						
				else:			#pvalvarnam is not and * and not "Pio_row"
					if pvalrecnmbr == '' or pvalrecnmbr[0] == '*':
						repldata = do_pvalonevarlist(pvalvarnam, pvalrecnmbr, pvalalt, pvalrepl, pvalvarnamrepl, vardict, varlist)
					else:			#pvalrecnmbr should be an integer, if it's not, then it's bogus....This is where I could add a call to piopref and let the user execute there own code....
						try: 
							pvalrecnmbrint = string.atoi(pvalrecnmbr)		#pval rec becomes a number
							repldata = do_pvalonevar(pvalvarnam, pvalrecnmbrint, pvalalt, pvalrepl, pvalvarnamrepl, vardict, varlist, pobjid)
						except ValueError:		#since pvalrecnmbr is not a number and not *...
							repldata = pvalalt
						
					
#-----				
				file = string.replace(file, valstring, repldata, 1)
			
			else: 		#pval has no closing tag before end of file
				valstring = file[p1:len(file)]
				repldata = '<b>pval has no closing tag before end of file.  Please check your source and correct the error! %s</b>' % (pvalbeg.strip('<'))
				file = string.replace(file, valstring, repldata, 1)
				p1 = -1 		#set p1 to -1 to break loop
			
		p2 = 0		#start loop over at 0
	
	
	
#	part0 = 'pvallist: %s varnam: %s<br>' % (str(pvallist), varnam)
#	part1 = 'records: %s <br>' % (str(records))
#	part2 =  'pobjid: %s <br>' % (pobjid)
#	part3 = 'rowcount: %s <br>' % (rowcount)
#	part4 = 'vardict: %s <br>' % (str(vardict))
#	part5 = 'varlist: %s <br>' % (str(varlist))
#	
#	file = file +part0 + part1 + part2 + part3 + part4 + part5 + part6
	return file
