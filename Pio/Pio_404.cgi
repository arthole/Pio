#!/usr/local/bin/python

import os, Pio_404

print "Content-type: text/html\n"	#necessary cgi line

ipaddr = os.environ['REMOTE_ADDR'] 
qrystring = os.environ['QUERY_STRING']
#referpage = os.environ['HTTP_REFERER']
webpath = os.environ['DOCUMENT_ROOT']
requestedurl = os.environ['REQUEST_URI']

error = ''
filename404 = ''

file = Pio_404.file404(webpath, requestedurl, error, filename404)

print file
