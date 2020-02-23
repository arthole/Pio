import sys, string, re


def file404(webpath, requestedurl, error, filename404):
	sys.stderr = sys.stdout
	
	url = requestedurl
	urllist = re.split('/', url)
	n = len(urllist)-1
	found404 = 'NOTFOUND!'
	if filename404 == '':
		try:
			import Pio_prefs
			filename404 = Pio_prefs.gimme("pio404")
		except ImportError:
			filename404 = 'Pio_404.html'
	
	while n >= 0 and found404 == 'NOTFOUND!':
#		print url + '<br>'
		if n ==  len(urllist)-1 and url[len(url)-1:] <> '/':
			url = string.replace(url, urllist[n], '')
		else:
			if urllist[n] <> '':
				url = string.replace(url, urllist[n]+'/', '')
		
		path = string.strip(webpath + url + filename404)
		try:
			file = open(path).read()
			found404 = 'y'
		except IOError:
			n = n -1
	#		print 'could not find %s <br>' % (path)
	
	if found404 == 'y':
		file = string.replace(file, '#request_url#', requestedurl)
		file = string.replace(file, '#requested_url#', requestedurl)
		file = string.replace(file, '#error#', error)
	else:
		file = '<html><body><br><b><font size="6">Error 404</b></font><hr noshade><br><br><br>'
		file = file + '<font size="5">The Page you were looking for "%s" could not be found.</font<br><br><br><br><br><br><br><br><br>' % (requestedurl)
		file = file + '<br><br><br><br><br><br><br><br><br><hr noshade><font size="1">Pio_404.cgi could not find Pio_404.html anywhere in path</font>'
		file = file + '</body></html>'
		
#	file = file + path
	return file