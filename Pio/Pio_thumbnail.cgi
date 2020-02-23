#!/usr/local/bin/python

#Pio_thumbnail.cgi

import os, cgi, sys, string
import Image

printw = sys.stdout.write 

qrystring = os.environ['QUERY_STRING'] #- the cgi can take a single input value which gets treated as the image name&path below. if no "image=somefile.jpg" exists
imgsize = 128		#this is the default thumbnail size.  it is set to "size=300" in the example below.  if size does not exist in the the cgi, 128 is used.

form = cgi.FieldStorage()
if form.has_key("size"):		# get thumbnail size if specified	
	imgsize = string.atoi(form["size"].value)
	sizestring = 'size=%s' % (imgsize)
if form.has_key("image"):	
	imgname = form["image"].value
else:
	imgname = qrystring


webpath = os.environ['DOCUMENT_ROOT']
im = Image.open(webpath + imgname)
im.thumbnail((imgsize, imgsize))

printw('Content-type: image/jpeg\r\n')
printw('\r\n')
im.save(sys.stdout, "JPEG")


###example html: notice the cgi is in the same directory as the image in the first example.  the image tag is surrounded by an anchor to display the full image on click.
#<a href="apartment.jpg"><img src="Pio_thumbnail.cgi?image=apartment.jpg&size=300" alt="" border="0"></a>
#here is the second example with the simple form of this cgi where only the name of the image is used(incl. a path) and it defaults to 128 in the cgi for size
#for this example I'm using absolute paths in the cgi.
#<a href="apartment.jpg"><img src="http://www.thearthole.net/arthole/Pio_thumbnail.cgi?/arthole/paintings/apartment.jpg" alt="" border="0"></a>