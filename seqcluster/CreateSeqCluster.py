'''
Script to create SeqCluster Table
Author : Kumaran Baskaran
Date   : 08.04.2014

Seq Clusters are calculated using cd-hid

Last step transfer the file to /tmp dir of the mysql hosting server
then use this command in mysql

load data infile '/tmp/SeqCluster.tab' into table SeqCluster(pdbCode,repChain,c100,c95,c90,c80,c70,c60,c50,chainCluster_uid);
''''


import sys,os
from string import atoi,atof


def convert_fasta(fname):
	f=open(fname,'r').read().split("\n")[:-1]
	fo=open("all.fasta",'w')
	for l in f:
		w=l.split("\t")
		if w[-1] != "\N":
			seq=w[-1].replace("-","")
			fo.write(">%s\n"%(w[0]))
			fo.write("%s\n"%(seq))
	fo.close()


def run_cdhit(base):
	cmd="cd-hit -i all.fasta -o %s100 -c 1.0 -n 5 -M 2000 -aS .9 -aL .9 > %s100.log"%(base,base)
	os.system(cmd)
	cmd="cd-hit -i all.fasta -o %s95 -c 0.95 -n 5 -M 2000 -aS .9 -aL .9 > %s95.log"%(base,base)
	os.system(cmd)
	cmd="cd-hit -i all.fasta -o %s90 -c 0.9 -n 5 -M 2000 -aS .9 -aL .9 > %s90.log"%(base,base)
	os.system(cmd)
	cmd="cd-hit -i all.fasta -o %s80 -c 0.8 -n 5 -M 2000 -aS .9 -aL .9 > %s80.log"%(base,base)
	os.system(cmd)
	cmd="cd-hit -i all.fasta -o %s70 -c 0.7 -n 5 -M 2000 -aS .9 -aL .9 > %s70.log"%(base,base)
	os.system(cmd)
	cmd="cd-hit -i all.fasta -o %s60 -c 0.6 -n 4 -M 2000 -aS .9 -aL .9 > %s60.log"%(base,base)
	os.system(cmd)
	cmd="cd-hit -i all.fasta -o %s50 -c 0.5 -n 3 -M 2000 -aS .9 -aL .9 > %s50.log"%(base,base)
	os.system(cmd)

def parse_output(fname):
	f=open(fname,'r').read().split("\n")[:-1]
	fo=open("SeqCluster.tab",'w')
	for l in f:
		w=l.split("\t")
		if w[-1] != "\N":
			uid=">%s..."%(w[0])
			c100=get_clusterid(uid,"cls100.clstr")
			c95=get_clusterid(uid,"cls95.clstr")
			c90=get_clusterid(uid,"cls90.clstr")
			c80=get_clusterid(uid,"cls80.clstr")
			c70=get_clusterid(uid,"cls70.clstr")
			c60=get_clusterid(uid,"cls60.clstr")
			c50=get_clusterid(uid,"cls50.clstr")
			fo.write("%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n"%(w[1],w[2],c100,c95,c90,c80,c70,c60,c50,w[0]))
	fo.close()
	


def get_clusterid(uid,fname):
	f=open(fname,'r').read().split(">Cluster")
	n=[]
	for x in f:
		if uid in x:
			n.append(f.index(x))
	if len(n)==0:
		n.append(-1)
	if len(n)!=1:
		print "There is problem ",len(n)
	return n[0]

def get_seq_data(dbname):
	cmd="mysql %s -B -N -e \"select uid,pdbCode,repChain,msaAlignedSeq from ChainCluster where msaAlignedSeq is not null limit 1000;\" > seq.dat"%(dbname)
	os.system(cmd)

def create_table(dbname):
	cmd="mysql %s -B -N -e \"create table SeqCluster(uid int(11) not null auto_increment,pdbCode varchar(4),repChain varchar(4),c100 int(11),c95 int(11),c90 int(11),c80 int(11),c70 int(11),c60 int(11),c50 int(11),chainCluster_uid int(11),primary key (uid));\""%(dbname)
	os.system(cmd)

if __name__=="__main__":
	dbname=sys.argv[1]
	get_seq_data(dbname)
	convert_fasta("seq.dat")
	run_cdhit("cls")
	parse_output("seq.dat")
	create_table(dbname)
