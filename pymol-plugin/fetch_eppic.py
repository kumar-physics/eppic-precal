# -*- coding: utf-8 -*-
'''
PyMOL plugin to load EPPIC interface files

DESCRIPTION

EPPIC:
	EPPIC (www.eppic-web.org) stands for Evolutionary Protein-Protein Interface Classifier (Duarte et al, BMC Bionformatics, 2012). 
	EPPIC mainly aims at classifying the interfaces present in protein crystal lattices in order to determine whether they are 
	biologically relevant or not.  
	For more information or queries please contact us at eppic@systemsx.ch. Our team web page is: http://www.psi.ch/lbr/capitani_-guido

Installation:
copy this file to /modules/pmg_tk/startup/ in the pymol installation path
restart pymol, now you will have additional entry called "Eppic Interface Loader" in Plugin menu


Usage:
Entering a pdb code will load all interfaces for a given pdbid
Example: 2gs2
Entering pdbid-interfaceid will load only a specified interface (as numbered by EPPIC, which sorts interfaces by their area) 
Example: 2gs2-2


Command line:
load_eppic is the command line tool for this plugin.


Usage:
	Method 1:
	load_eppic <pdbid> 
	This command will load all the interface files for a given pdbid
	Example:
	load_eppic 2gs2

	Method 2:
	load_eppic <pdbid-interfaceid>
	This command will load only a specified interface
	Example:
	load_eppic 2gs2-2

	Interface ids are those listed in the EPPIC server output


Author : Kumaran Baskaran

Date   : 10.04.2014

'''
import sys, os
import urllib2,StringIO,gzip
from pymol import cmd
from string import atoi


def hasTk():
	# Verified cases
	# True if:
	#  - Linux, Windows
	#  - calling name contains X11, eg 'PyMOLX11Hybrid.app'
	# False if:
	#  - Mac and name is 'MacPyMol.app'
	#  - import Tkinter throws an exception

	#sys.platform!="darwin": # Tk module excluded fro mac
	return True

# If we're in a Tkinter environment, register with the plugins menu
# Otherwise, only use command line version
if hasTk():

	from Tkinter import *
	import tkSimpleDialog
	import tkMessageBox


	def __init__(self):
		# Simply add the menu entry and callback
		self.menuBar.addmenuitem('Plugin', 'command', 'EPPIC Interface Loader',
				label = 'EPPIC Interface Loader',
				command = lambda s=self : FetchEPPIC(s))

	# Tk plugin version.
	def fetch_eppic_plugin(app):
		def errorfn(msg):
			tkMessageBox.showinfo('EPPIC Loader Service', msg)
		#get user input
		pdbCode = tkSimpleDialog.askstring('EPPIC Loader Service',
				'Please enter a 4-digit pdb code:',
				parent=self._app.root)

		#load asynchronously
		thread.start_new_thread(fetch_eppic_sync, (pdbCode),{'logfn':errorfn})




from pymol import cmd
from string import atoi
import urllib2,StringIO,gzip
import gzip
import os

# Main command line version
def fetch_eppic(pdbCode,name=None,state=0,async=1, **kwargs):
	'''
	===========================================================================
	DESCRIPTION
	-----------
	EPPIC:
	------
	EPPIC (www.eppic-web.org) stands for Evolutionary Protein-Protein Interface 
	Classifier (Duarte et al, BMC Bionformatics, 2012). 

	EPPIC mainly aims at classifying the interfaces present in protein crystal 
	lattices in order to determine whether they are biologically relevant or not. 
 
	For more information or queries please contact us at eppic@systemsx.ch. 
	Our team web page is: http://www.psi.ch/lbr/capitani_-guido

	load_eppic is a command line tool to download interface files from 
	EPPIC server to open in pymol

	Usage:
	------
	Method 1:
	fetch_eppic <pdbid> 
	This command will load all the interface files for a given pdbid
	example:
	fetch_eppic 2gs2

	Method 2:
	fetch_eppic <pdbid-interfaceid>
	This command will load only specified interface
	example:
	fetch_eppic 2gs2-2

	The interface ids are listed in EPPIC server

	Author : Kumaran Baskaran
	Date   : 11.04.2014
	===========================================================================
	'''
	if int(async):
		thread.start_new_thread(fetch_eppic_sync, (pdbCode,name,state),kwargs)
	else:
		fetch_eppic_sync(pdbCode,name,state,**kwargs)

# Helper version, does all the work
def fetch_eppic_sync(pdbCode,name=None,state=0,logfn=None,**kwargs):
	"Synchronously fetch eppic interface(s)"
	fetchpath=cmd.get('fetch_path')
	if logfn is None:
		def logfn(m):
			print(m)

	if pdbCode:
		if len(pdbCode)>4:
			pdbid=pdbCode.split("-")[0]
			ifaceid=atoi(pdbCode.split("-")[1])
			filename=os.path.join(fetchpath, "%s-%d.pdb"%(pdbid,ifaceid))
			check_fetch=load_eppic(pdbid,ifaceid,filename)
			if check_fetch:
				cmd.load(filename,pdbCode)
			else:
				logfn("No PDB or Interface Found")

		else:
			ifaceid=1
			pdbid=pdbCode
			while True:
				filename=os.path.join(fetchpath, "%s-%d.pdb"%(pdbid,ifaceid))
				check_fetch=load_eppic(pdbid,ifaceid,filename)
				if check_fetch:
					cmd.load(filename,"%s-%d"%(pdbid,ifaceid))
					ifaceid+=1
				else:
					if ifaceid==1:
						logfn( "No PBD or Interface Found")
					else:
						logfn( "%d Interfaces Loaded"%(ifaceid-1) )
					break
	else: #no pdbcode
		logfn( "No PDB or Interface given")

def load_eppic(pdbid,ifaceid,filename):
	"""Download the interface from eppic
	return whether the download was successfull
	"""
	fetchurl="http://eppic-web.org/ewui/ewui/fileDownload?type=interface&id=%s&interface=%d"%(pdbid,ifaceid)

	is_done=False

	request=urllib2.Request(fetchurl)
	request.add_header('Accept-encoding', 'gzip')
	opener=urllib2.build_opener()
	try:
		f=opener.open(request)
		compresseddata = f.read()
		if len(compresseddata)>0:
			compressedstream = StringIO.StringIO(compresseddata)
			gzipper = gzip.GzipFile(fileobj=compressedstream)
			data = gzipper.read()
			open(filename,'w').write(data)
			is_done=True
	except urllib2.HTTPError:
		pass
	except IOError:
		print "Error writing to "+filename
		pass
	return is_done

cmd.extend("fetch_eppic",fetch_eppic)
