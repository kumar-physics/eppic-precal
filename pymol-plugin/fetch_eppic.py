# -*- coding: utf-8 -*-
# vim:noet ts=4 sw=4 ff=unix fenc=utf-8
'''
PyMOL plugin to load EPPIC interface files

DESCRIPTION

	EPPIC (www.eppic-web.org) stands for Evolutionary Protein-Protein Interface
	Classifier (Duarte et al, BMC Bionformatics, 2012).

	EPPIC mainly aims at classifying the interfaces present in protein crystal
	lattices in order to determine whether they are biologically relevant or
	not.

	For more information or queries please contact us at eppic@systemsx.ch. Our
	team web page is: http://www.psi.ch/lbr/capitani_-guido

INSTALLATION

	To install from within pymol, from the Plugins menu, choose 'Manage
	Plugins>Install...' and select fetch_eppic.py from your hard drive.

	To install manually, copy fetch_eppic.py to 'PYMOLPATH/modules/pmg_tk/startup/' and
	restart pymol.

	After installation you will have an additional entry called "Eppic Interface Loader" in Plugin menu.

	Note: Users of MacPyMol.app do not have a plugins menu, and should use the fetch_eppic command.

USAGE--PLUGIN MENU

	Entering a pdb code will load all interfaces for a given pdbid
	Example: 2gs2

	Entering pdbid-interfaceid will load only a specified interface (as
	numbered by EPPIC, which sorts interfaces by their area)
	Example: 2gs2-2


USAGE--COMMAND LINE
	fetch_eppic pdbid[-interfaceid] [,name [,state [,async]]]

ARGUMENTS
	Arguments mirror arguments to fetch

	pdbid = string: Either a PDB ID or an EPPIC interface in the format XXXX-N,
	where XXXX is the pdb id and N is the interface number. {required}

	name = string: name of the PyMOL object to lave to {default: pdbid}

	state = integer: number of the state into which the content should be
	loaded, or 0 for append {default: 0}

	async = integer: 0 to force synchronous execution {default:1}

	Other arguments will be passed directly to load.

EXAMPLES

	#Load all the interface files for 2gs2
	fetch_eppic 2gs2

	#Load only the second interface
	fetch_eppic 2gs2-2

	#Load all interfaces as states of a single object
	fetch_eppic 2gs2, name=2gs2_eppic

	#Load synchronously for chaining commands
	fetch_eppic 2gs2-1, name=interface, async=0; show cartoon, interface

	Interface ids are those listed in the EPPIC server output


Author : Kumaran Baskaran
Date   : 10.04.2014

'''
import sys, os, thread
import urllib2,StringIO,gzip
import pymol
from pymol import cmd
from string import atoi


def hasTk():
	""" Make an educated guess as to whether Tk is installed,
	hopefully without triggering any installation on Macs
	"""
	#use of internal variable endorsed by Thomas Holder
	return pymol._ext_gui



# If we're in a Tkinter environment, register with the plugins menu
# Otherwise, only use command line version
if hasTk():

	try:
		from Tkinter import *
		import tkSimpleDialog
		import tkMessageBox


		def __init__(self):
			#print self.root.wm_title()

			# Simply add the menu entry and callback
			self.menuBar.addmenuitem('Plugin', 'command', 'EPPIC Interface Loader',
					label = 'EPPIC Interface Loader',
					command = lambda s=self : fetch_eppic_plugin(s))

		# Tk plugin version.
		def fetch_eppic_plugin(app):
			def errorfn(msg):
				tkMessageBox.showinfo('EPPIC Loader Service', msg,parent=app.root)
			#get user input
			pdbCode = tkSimpleDialog.askstring('EPPIC Loader Service',
					'Please enter a 4-digit pdb code:',
					parent=app.root)

			# Tk isn't thread safe, so we run synchronously.
			# We could also use events to communicate errors to the mainloop,
			# but this seems like too much work for a minor feature
			#thread.start_new_thread(fetch_eppic_sync, (pdbCode,None,0,errorfn))
			fetch_eppic_sync(pdbCode,logfn=errorfn)
	except ImportError:
		pass #no Tk




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

	    EPPIC (www.eppic-web.org) stands for Evolutionary Protein-Protein Interface
	    Classifier (Duarte et al, BMC Bionformatics, 2012).

	    EPPIC mainly aims at classifying the interfaces present in protein crystal
	    lattices in order to determine whether they are biologically relevant or not.

	    For more information or queries please contact us at eppic@systemsx.ch.
	    Our team web page is: http://www.psi.ch/lbr/capitani_-guido

	    fetch_eppic is a command line tool to download interface files from
	    EPPIC server to open in pymol

	USAGE--COMMAND LINE
	    fetch_eppic pdbid[-interfaceid] [,name [,state [,async]]]

	ARGUMENTS
	    Arguments mirror arguments to fetch

	    pdbid = string: Either a PDB ID or an EPPIC interface in the format XXXX-N,
	    where XXXX is the pdb id and N is the interface number.  The interface ids
	    are listed in EPPIC server (eppic-web.org). {required}

	    name = string: name of the pymol object to lave to {default: pdbid}

	    state = integer: number of the state into which the content should be
	    loaded, or 0 for append {default: 0}

	    async = integer: 0 to force synchronous execution {default:1}

	    Other arguments will be passed directly to load.

	EXAMPLES

	    #Load all the interface files for 2gs2
	    fetch_eppic 2gs2

	    #Load only the second interface
	    fetch_eppic 2gs2-2

	    #Load all interfaces as states of a single object
	    fetch_eppic 2gs2, name=2gs2_eppic

	    #Load synchronously for chaining commands
	    fetch_eppic 2gs2-1, name=interface, async=0; show cartoon, interface

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
			if len(pdbCode.split("-"))==2:
				pdbid=pdbCode.split("-")[0]
				ifaceid=pdbCode.split("-")[1]
				filename=os.path.join(fetchpath, "%s-%s.pdb"%(pdbid,ifaceid))
				if name is None:
					name = pdbCode
				check_fetch=load_eppic(pdbid,ifaceid,filename,logfn)
				if check_fetch:
					cmd.load(filename,name,state,format="pdb",**kwargs)
					cmd.util.color_chains()
				else:
					logfn("No PDB or Interface Found")
			elif len(pdbCode.split("-"))==3:
				pdbid=pdbCode.split("-")[0]
				ifaceid=pdbCode.split("-")[1]
				chain=pdbCode.split("-")[2]
				filename=os.path.join(fetchpath, "%s-%s.pdb"%(pdbid,ifaceid))
				if name is None:
					name = pdbCode
					name2 = "%s_%s_%s"%(pdbid,ifaceid,chain)
				check_fetch=load_eppic(pdbid,ifaceid,filename,logfn)
				if check_fetch:
					cmd.load(filename,name,state,format="pdb",**kwargs)
					cmd.show_as('cartoon','%s'%(name))
					cmd.util.color_chains("%s"%(name))
					cmd.extract('%s'%(name2),"%s//%s//"%(name,chain))
					cmd.show_as('surface',"%s"%(name2))
					cmd.spectrum(expression='b',palette='rainbow',selection='%s'%(name2),minimum=0.0,maximum=3.3219280948873626)
					#cmd.color('salmon','%s'%(name))
					
				else:
					logfn("No PDB or Interface Found")
			else:
				logfn("Input not in right format example : pdb,id,chain")

		else:
			ifaceid=1
			pdbid=pdbCode
			while True:
				filename=os.path.join(fetchpath, "%s-%d.pdb"%(pdbid,ifaceid))
				if name is None:
					objname = "%s-%d"%(pdbid,ifaceid)
				else:
					objname = name
				check_fetch=load_eppic(pdbid,ifaceid,filename)
				if check_fetch:
					cmd.load(filename,objname,state,format="pdb",**kwargs)
					ifaceid+=1
				else:
					if ifaceid==1:
						logfn( "No PBD or Interface Found")
					else:
						logfn( "%d Interfaces Loaded"%(ifaceid-1) )
						cmd.util.color_chains()
					break
	else: #no pdbcode
		logfn( "No PDB or Interface given")

def load_eppic(pdbid,ifaceid,filename,logfn=None):
	"""Download the interface from eppic
	return whether the download was successfull
	"""
	fetchurl="http://eppic-web.org/ewui/ewui/fileDownload?type=interface&id=%s&interface=%s"%(pdbid,ifaceid)

	is_done=False

	if logfn is None:
		def logfn(m):
			print(m)

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
			try:
				open(filename,'w').write(data)
				is_done=True
			except IOError:
				logfn( "Error writing to "+filename)
	except urllib2.HTTPError:
		pass
	except IOError:
		pass
	return is_done

cmd.extend("fetch_eppic",fetch_eppic)
