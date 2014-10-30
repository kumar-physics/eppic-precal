#!/usr/bin/python
'''
Created on Oct 28, 2014

@author: baskaran_k
'''

from re import findall
from commands import getoutput
from datetime import date
from os import system

class TopupEPPIC:
    
    t=date.today()
    eppicpath='/home/eppicweb/software/bin/eppic'
    topuppath='/home/eppicweb/topup'
    eppicconf='/home/eppicweb/.eppic.conf'
    pdbrepopath='/data/dbs/pdb'
    database='eppic_2014_09'
    def parsePDBrsyncfile(self):
        f=open(self.rsyncfile,'r').read()
        self.deletedPDB=findall(r'deleting\s*mmCIF/\S+/(\S+).cif.gz\s+',f ,)
        self.newPDB=findall(r'mmCIF/\S+.cif.gz -> ../../divided/mmCIF/\S+/(\S+).cif.gz\s+', f)
        self.allPDB=list(set(findall(r'mmCIF/\S+/(\S+).cif.gz\s+', f)))
        self.updatedPDB=[i for i in self.allPDB if i not in self.newPDB and i not in self.deletedPDB]
        return [self.newPDB,self.updatedPDB,self.deletedPDB]
    
    def getLatestRsyncLogfile(self):
        self.rsyncfile="%s/%s"%(self.pdbrepopath,getoutput('ls -tr %s'%(self.pdbrepopath)).split("\n")[-1])
        return self.rsyncfile
    
    def writePDBlists(self):
     
        self.inputpath="%s/input"%(self.topuppath)
        self.pdbinput="%s/pdbinput_%s.list"%(self.inputpath,str(self.t))
        fo=open(self.pdbinput,'w')
        fo.write("%s\n"%("\n".join(self.newPDB+self.updatedPDB)))
        fo.close()
        fo=open("%s/newPDB_%s.list"%(self.inputpath,str(self.t)),'w')
        fo.write("%s\n"%("\n".join(self.newPDB)))
        fo.close()
        fo=open("%s/updatedPDB_%s.list"%(self.inputpath,str(self.t)),'w')
        fo.write("%s\n"%("\n".join(self.updatedPDB)))
        fo.close()
        fo=open("%s/deletedPDB_%s.list"%(self.inputpath,str(self.t)),'w')
        fo.write("%s\n"%("\n".join(self.deletedPDB)))
        fo.close()
    
    def checkNumbers(self):
        self.okFlag = 1
        if (len(self.newPDB)==0 and len(self.updatedPDB)==0 and len(self.deletedPDB)==0):
            self.okFlag=0
        elif len(self.newPDB)>1000 or len(self.updatedPDB)>1000:
            self.okFlag=-1
        else:
            self.okFlag=1
        return self.okFlag
        
    def writeQsubscript(self):
        self.qsubpath="%s/qsubscript"%(self.topuppath)
        self.outputpath="%s/output/%s"%(self.topuppath,str(self.t))
	system("mkdir -p %s/logs"%(self.outputpath))
        self.qsubscript="%s/topup_%s.sh"%(self.qsubpath,str(self.t))
        fo=open(self.qsubscript,'w')
        fo.write("#!/bin/sh\n\n")
        fo.write("#$ -N topup\n#$ -q topup.q\n#$ -e %s/logs\n#$ -o %s/logs\n#$ -t 1-%d\n#$ -l s_rt=12:00:00,h_rt=12:00:30\n"%(self.outputpath,self.outputpath,len(self.newPDB)+len(self.updatedPDB)))
        fo.write("pdb=`grep -v \"^#\"  %s | sed \"s/\(....\).*/\\1/\" | sed \"${SGE_TASK_ID}q;d\"`\n"%(self.pdbinput))
        fo.write("# Cut the middle letters of pdb code for making directory in divided\n")
        fo.write("mid_pdb=`echo $pdb | awk -F \"\" '{print $2$3}'`\n")
        fo.write("# Check is directory is not present\n")
        fo.write("if [ ! -d %s/data/divided/$mid_pdb ]; then mkdir -p %s/data/divided/$mid_pdb; fi\n"%(self.outputpath,self.outputpath))
        fo.write("if [ ! -d %s/data/divided/$mid_pdb/$pdb ]; then mkdir -p %s/data/divided/$mid_pdb/$pdb; fi\n"%(self.outputpath,self.outputpath))
        fo.write("if [ ! -d %s/data/all ]; then mkdir  %s/data/all; fi\n"%(self.outputpath,self.outputpath))
        fo.write("cd %s/data/all/\n"%(self.outputpath))
        fo.write("ln -s ../divided/$mid_pdb/$pdb $pdb\n")
        fo.write("%s -i $pdb -a 1 -s -o %s/data/divided/$mid_pdb/$pdb -l -w -g %s\n"%(self.eppicpath,self.outputpath,self.eppicconf))
        fo.write("cp %s/logs/topup.e${JOB_ID}.${SGE_TASK_ID} %s/data/divided/$mid_pdb/$pdb/$pdb.e\n"%(self.outputpath,self.outputpath))
        fo.write("cp %s/logs/topup.o${JOB_ID}.${SGE_TASK_ID} %s/data/divided/$mid_pdb/$pdb/$pdb.o\n"%(self.outputpath,self.outputpath))
        fo.close()
    
    def submitJob(self):
        system("source /var/lib/gridengine/default/common/settings.sh;qsub %s"%(self.qsubscript))
        #print "qsub %s"%(self.qsubscript)
        mailmessage="%d new entries\n%d updated entries\n%d deleted deleted entries\n%d jobs submitted successfully"%(len(self.newPDB),len(self.updatedPDB),len(self.deletedPDB),len(self.newPDB)+len(self.updatedPDB))
        #print mailmessage
        mailcmd="mail -s \"EPPIC topup started\" \"eppic@systemsx.ch\" <<< \"%s\""%(mailmessage)
        system(mailcmd)

    def previousStatistics(self):
        statcmd1="python /home/eppicweb/bin/eppic_stat_2_1_0_prev.py %s"%(self.database)
        system(statcmd1)

if __name__=="__main__":
    p=TopupEPPIC()
    p.getLatestRsyncLogfile()
    p.parsePDBrsyncfile()
    p.writePDBlists()
    if p.checkNumbers():
        p.writeQsubscript()
        p.submitJob()
	p.previousStatistics()
