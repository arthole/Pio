
#Pio_prefs

prefsdict = {
	
###modify or add preferences below
	
	#below are the database preferences.
	"sqluser" : "user",
	"sqldb" : "database",
	"sqlhost" : "127.0.0.1",
	
	#authorization must come from same address - extra security
	#valid values yes/no
	"staticip" : "no",  
	
	#below is to do logging of qrystmts.
	"piolog" : "yes",
	
	#below are the show pobj and the show pinp preferences.  
	#pobj's get converted to <xpobj and pinp get converted to <xpinp and ppref get converted to <xppref
	#any value other than yes is a no.
	#ppref's of showpobj and showppref can be included in html.  (showpinp is ignored because pprefs are actually processed after pinp, pifs.
	#for ppref tag to override the value below, it must be the first ppref...otherwise it will only the show value for it and any following ppref
	#example: <ppref name="showpobj" value="no">
	
	"showpobj" : 'no',
	"showpinp" : 'no',
	"showppref" : 'no',
	
	#below are the error preferences
	#values for pobjerror are "bottom", "top", "" or "ignore", or a page, as in "error.html" 
	#bottom places errors at the end of the page, top at the begining, "" or ignore shows no error
	#and a page (indicated with a ".") will open that return that page.
	#example: <ppref name="pobjerror" value="ignore">
	
	"pobjerror" : "bottom",
	"pobjautherrorfile" : "Pio_login.html",
	"pobjautherror" : "top",
	"piosiderrorfile" : "none",
	"piosiderror" : "bottom",
	"loginerror" : "Pio_login.html",
	
	#below is the administrator email
	"pioadminemail" : "user@yourdomain.com",
	
	#below is the upload folder 
	"uploadpath" : "/Library/WebServer/Documents/upload/",
	
	#below is the 404 file not found preference
	"pio404" : 'Pio_404.html',
	#below is the error code for when an include file is not found
	#if the value is "comment" the program will show the error as a comment in html, otherwise it will show it as normal text
	"include404" : "nocomment",
	
	#below are special user preferences you can include in your own programs
	"dictionarykey" : "value"
	
	
###modify or add preferences above
##
##prefs can be overridden on a page by including a tag such as <ppref pref="pobjautherror" value="ignore'>
}


def gimme(dictkey):
	
	if prefsdict.has_key(dictkey):
		returnvalue = prefsdict[dictkey]
	else:
		returnvalue = ""
	
	return 	returnvalue


def gimmedict():
	return prefsdict


