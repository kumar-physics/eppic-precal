'''
Pymol plugin to load EPPIC interface files


Installation:
copy this file to /modules/pmg_tk/startup/ in the pymol installation path

Usage:
just entering pdbid will load all interfaces
entering pdbid-interfaceid will load specific interface

Author : Kumaran Baskaran

Date   : 10.04.2014

'''


from Tkinter import *
from pymol import cmd
from string import atoi
import os
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
		fetchurl="http://eppic-web.org/ewui/ewui/fileDownload?type=interface&id=%s&interface=%d"%(pdbid,ifaceid)
		request=urllib2.Request(fetchurl)
		request.add_header('Accept-encoding', 'gzip')
		opener=urllib2.build_opener()
		f=opener.open(request)
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





