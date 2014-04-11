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
import sys

if sys.platform!="darwin": # Tk module excluded fro mac

	from Tkinter import *
	from pymol import cmd
	from string import atoi
	import tkSimpleDialog
	import tkMessageBox
	import urllib2,StringIO,gzip
	import gzip
	import os


	def __init__(self):
		# Simply add the menu entry and callback
		self.menuBar.addmenuitem('Plugin', 'command', 'EPPIC Interface Loader',
				label = 'EPPIC Interface Loader',
				command = lambda s=self : FetchEPPIC(s))



	class FetchEPPIC:
		def __init__(self, app):
			fetchpath=cmd.get('fetch_path')
			pdbCode = tkSimpleDialog.askstring('EPPIC Loader Service',
					'Please enter a 4-digit pdb code:',
					parent=app.root)
			if pdbCode:
				if len(pdbCode)>4:
					pdbid=pdbCode.split("-")[0]
					ifaceid=atoi(pdbCode.split("-")[1])
					filename=os.path.join(fetchpath, "%s-%d.pdb"%(pdbid,ifaceid))
					check_fetch=self.fetch_eppic(pdbid,ifaceid,filename)
					if check_fetch:
						cmd.load(filename,pdbCode)
					else:
						tkMessageBox.showinfo('Loading failed for %s'%(pdbCode),
								'No Interface found\n(or)\nPDB not found')
				else:
					ifaceid=1
					pdbid=pdbCode
					while(1):
						filename=os.path.join(fetchpath, "%s-%d.pdb"%(pdbid,ifaceid))
						check_fetch=self.fetch_eppic(pdbid,ifaceid,filename)
						if check_fetch:
							cmd.load(filename,"%s-%d"%(pdbid,ifaceid))
							ifaceid+=1
						else:
							if ifaceid==1:
								tkMessageBox.showinfo('Loading failed for %s'%(pdbCode),
										'No Interface found\n(or)\nPDB not found')
							else:
								tkMessageBox.showinfo('Loading Completed',
										'%d interfaces loaded'%(ifaceid-1))
							break
	
		def fetch_eppic(self,pdbid,ifaceid,filename):
			return load_eppic(pdbid,ifaceid,filename)



from pymol import cmd
from string import atoi
import urllib2,StringIO,gzip
import gzip
import os

def fetch_eppic(pdbCode):
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
	fetchpath=cmd.get('fetch_path')
	if pdbCode:
		if len(pdbCode)>4:
			pdbid=pdbCode.split("-")[0]
			ifaceid=atoi(pdbCode.split("-")[1])
			filename=os.path.join(fetchpath, "%s-%d.pdb"%(pdbid,ifaceid))
			check_fetch=load_eppic(pdbid,ifaceid,filename)
			if check_fetch:
				cmd.load(filename,pdbCode)
			else:
				print "No PDB (or) Interface Found"

		else:
			ifaceid=1
			pdbid=pdbCode
			while(1):
				filename=os.path.join(fetchpath, "%s-%d.pdb"%(pdbid,ifaceid))
				check_fetch=load_eppic(pdbid,ifaceid,filename)
				if check_fetch:
					cmd.load(filename,"%s-%d"%(pdbid,ifaceid))
					ifaceid+=1
				else:
					if ifaceid==1:
						print "No PBD (or) Interface Found"
					else:
						print "%d Interfaces Loaded"%(ifaceid-1)
					break
def load_eppic(pdbid,ifaceid,filename):	
		fetchurl="http://eppic-web.org/ewui/ewui/fileDownload?type=interface&id=%s&interface=%d"%(pdbid,ifaceid)
		request=urllib2.Request(fetchurl)
		request.add_header('Accept-encoding', 'gzip')
		opener=urllib2.build_opener()
		try:
			f=opener.open(request)
		except urllib2.HTTPError:
			return 0
		compresseddata = f.read()
		if len(compresseddata)>0:
			compressedstream = StringIO.StringIO(compresseddata)
			gzipper = gzip.GzipFile(fileobj=compressedstream)
			data = gzipper.read()
			open(filename,'w').write(data)
			is_done=1
		else:
			is_done=0
		return is_done

cmd.extend("fetch_eppic",fetch_eppic)
