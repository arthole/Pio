#!/usr/local/bin/python

import os, cgi, sys, string, whrandom
import Image

printw = sys.stdout.write 

qrystring = os.environ['QUERY_STRING']
ipaddr = os.environ['REMOTE_ADDR'] 
webpath = os.environ['DOCUMENT_ROOT']
requestedurl = os.environ['REQUEST_URI']

imgsize = 128

form = cgi.FieldStorage()
if form.has_key("size"):		# get thumbnail size if specified	
	imgsize = string.atoi(form["size"].value)
	sizestring = 'size=%s' % (imgsize)
if form.has_key("path"):	
	dirpath = form["path"].value		#This is the directory of objects to get one from.
if form.has_key("image"):	
	imgname = form["image"].value
else:
	imgname = qrystring

# I copied this code from Pio_getrandomobj.py
if dirpath[0] == "/" and dirpath[len(dirpath)-1:len(dirpath)-1] == "/":
	objdir = str(webpath) + str(dirpath)
	objpath = str(dirpath)
elif dirpath[0] == "/" and dirpath[len(dirpath)-1:len(dirpath)-1] <> "/":
	objdir = str(webpath) + str(dirpath) + '/'
	objpath = str(dirpath) + '/'
elif dirpath[0] <> "/" and dirpath[len(dirpath)-1:len(dirpath)-1] == "/":
	objdir = str(webpath) + '/' + str(dirpath)
	objpath = '/' + str(dirpath)
else:
	objdir = str(webpath) + '/' + str(dirpath)+ '/'
	objpath = '/' + str(dirpath)+ '/'
try:
	objlist = os.listdir(objdir)	#list of directory objects
	objlistlen = len(objlist)	#number of dir objects
	randnmbr = whrandom.randint(0, objlistlen -1)
	
	objname = objlist[randnmbr]
	objnamepath = objpath +objname
	
except OSError, e:
	rcdserr = "Pio_getrandomobj.getrandomobj: no directory /<i>serverpath</i>%s" % (objpath)



im = Image.open(webpath + objnamepath)
im.thumbnail((imgsize, imgsize))

printw('Content-type: image/jpeg\r\n')
printw('\r\n')
im.save(sys.stdout, "JPEG")

