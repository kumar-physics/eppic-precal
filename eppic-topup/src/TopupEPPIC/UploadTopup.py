#!/usr/bin/python

'''
Created on Oct 28, 2014

@author: baskaran_k
'''

from re import findall
from commands import getoutput
from datetime import date
from os import system




class UploadTopup:
    
    t=date.today()
    uniprotVersion='2014_10'
    database="eppic_%s"%(uniprotVersion)
    eppicpath='/home/eppicweb/software/bin/eppic'
    topuppath='/home/eppicweb/topup'
    eppicconf='/home/eppicweb/.eppic.conf'
    pdbrepopath='/data/dbs/pdb'
    datapath='/data/webapps/files_%s'%(uniprotVersion)
    
    def rsyncFolder(self):
        rsynccmd="rsync -az %s/output/%s/data/divided %s/"%(self.topuppath,str(self.t),self.datapath) 
        #print rsynccmd
        system(rsynccmd)
    
    def createSymlink(self):
        newPdblist=open("%s/input/newPDB_%s.list"%(self.topuppath,str(self.t)),'r').read().split("\n")[:-1]
        for pdb in newPdblist:
            symlinkcmd="cd %s;ln -s divided/%s/%s"%(self.datapath,pdb[1:3],pdb)
            #print symlinkcmd
            system(symlinkcmd)

    def uploadFiles(self):
        uploadcmd="/home/eppicweb/software/jars/eppic-dbtools.jar -D %s  -d %s/ -f %s/input/pdbinput_%s.list -F -o > /dev/null"%(self.database,self.datapath,self.topuppath,str(self.t))
        #print uploadcmd
        system(uploadcmd)
    def removeObsolete(self):
        if self.deletedEntries()<20:
            delcmd="/home/eppicweb/software/jars/eppic-dbtools.jar -D %s -d %s/ -f %s/input/deletedPDB_%s.list -r -o > /dev/null"%(self.database,self.datapath,self.topuppath,str(self.t))
            system(delcmd)
        else:
            sendmail="mail -s \"EPPIC topup warning\"  \"eppic@systemsx.ch\" <<< \"More than 20 obsolete entries found. Please check and delete manually\""
            system(sendmail)
        
    def previousStatistics(self):
        statcmd1="python /home/eppicweb/bin/eppic_stat_2_1_0_prev.py %s"%(self.database)
        print statcmd1
        #system(statcmd1)
        
    def newEntries(self):
        return len(open("%s/input/newPDB_%s.list"%(self.topuppath,str(self.t)),'r').read().split("\n")[:-1])
    def allEntries(self):
        return len(open("%s/input/pdbinput_%s.list"%(self.topuppath,str(self.t)),'r').read().split("\n")[:-1])
    def deletedEntries(self):
        return len(open("%s/input/deletedPDB_%s.list"%(self.topuppath,str(self.t)),'r').read().split("\n")[:-1])
    def updatedEntries(self):
        return len(open("%s/input/updatedPDB_%s.list"%(self.topuppath,str(self.t)),'r').read().split("\n")[:-1])
    
    def getStatistics(self):
        rsyncfile=getoutput('ls -tr /data/dbs/pdb').split("\n")[-1]
        statcmd2="python /home/eppicweb/bin/eppic_stat_2_1_0_diff2.py %s %d %d %d %s %s %s"%(self.database,self.allEntries(),self.newEntries(),self.deletedEntries(),self.uniprotVersion,rsyncfile,str(self.t))
        #print statcmd2
        system(statcmd2)
    def checkJobs(self):
        self.runningJobs=findall(r'\s+\d+\s+\S+\s+topup\s+eppicweb\s+\S\s+\S+\s+\S+\s+\S+\s+\d+\s+(\d+)\n',getoutput('source /var/lib/gridengine/default/common/settings.sh;qstat -u eppicweb'))
        return self.runningJobs
    
    def topupOver(self):
        try:
            n=len(open("%s/statistics_%s.html"%(self.topuppath,str(self.t)),'r').read().split("\n")[:-1])
        except IOError:
            n=0
        return n
    
    def sendMessage(self):
        mailmessage="Job Ids %s are running "%(" ".join(self.runningJobs))
	msg2=mailmessage+"\nMemory info (GB)\n"+getoutput('free -g')
        #print mailmessage
        mailcmd="mail -s \"EPPIC topup running\" \"eppic@systemsx.ch\" <<< \"%s\""%(msg2)
        system(mailcmd)

    def sendReport(self):
        mailmessage2="All jobs finished successfully. Please see the attachment"
	#mailmessage2="This is a test"
        #print mailmessage
        mailcmd2="mail -s \"EPPIC topup finished\" -a \"%s/statistics_%s.html\" \"eppic@systemsx.ch\" <<< \"%s\""%(self.topuppath,str(self.t),mailmessage2)
	cpcmd="cp %s/statistics_%s.html /data/webapps/ewui/statistics.html"%(self.topuppath,str(self.t))
        system(cpcmd)
        system(mailcmd2)


if __name__=="__main__":
    p=UploadTopup()
    try:
        p.newEntries()
        runningjob=p.checkJobs()
        if len(runningjob)!=0 and p.topupOver()==0:
            p.sendMessage()
        else:
	    if p.topupOver()==0:	
            	p.rsyncFolder()
            	p.createSymlink()
            	p.uploadFiles()
                p.removeObsolete()
            	p.getStatistics()
	   	p.sendReport()
    except IOError:
        pass
