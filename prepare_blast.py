import sys,os,re,commands
from string import atoi

def create_blast_chunk(fname):
	f=open(fname,'r').read().split("\n")[:-1]
	fo=open('queries_sorted.list','w')
	seq=[]
	for bfile in f:
		dat=re.findall(r">\S+\s([\S\s]+)\s",open("%s.fa"%(bfile),'r').read())
		fo.write("%s\t%d\n"%(bfile,len(dat[0])-dat[0].count("\n")))
		seq.append([bfile,len(dat[0])-dat[0].count("\n")])
	fo.close()
	seq35=[]
	seq50=[]
	seq85=[]
	seq86=[]
	for s in seq:
		if s[1]<35:seq35.append(s[0])
		elif s[1]>=35 and s[1]<50:seq50.append(s[0])
		elif s[1]>=50 and s[1]<85:seq85.append(s[0])
		else: seq86.append(s[0])
	test=[50,100,200,400,600,800,1000,1200,1400,1600,1800,2000]
	n=max([len(seq35),len(seq50),len(seq85),len(seq86)])
	j=0
	k=0
	p=0
	os.system("rm seq_*")
	for i in range(n):
		if i<len(seq35):
			cmd="cat %s.fa >> seq_35_%d_%d.fa"%(seq35[i],test[j],k)
			os.system(cmd)
		if i<len(seq50):
			cmd="cat %s.fa >> seq_50_%d_%d.fa"%(seq50[i],test[j],k)
			os.system(cmd)
		if i<len(seq85):
			cmd="cat %s.fa >> seq_85_%d_%d.fa"%(seq85[i],test[j],k)
			os.system(cmd)
		if i<len(seq86):
			cmd="cat %s.fa >> seq_86_%d_%d.fa"%(seq86[i],test[j],k)
			os.system(cmd)
		p+=1
		if p%test[j]==0:
			j+=1
			p=0
			if j>=len(test):
				j=j%len(test)
				k+=1
	#path="/gpfs/home/baskaran_k/eppic-precomp-uniprot_2014_06"
	path="/media/baskaran_k/data/eppic_2014_06/eppic-precomp-uniprot_2014_06"
	os.system("ls seq_35_* | sed s/.fa//g >queries35.list")
	os.system("ls seq_50_* | sed s/.fa//g >queries50.list")
	os.system("ls seq_85_* | sed s/.fa//g >queries85.list")
	os.system("ls seq_86_* | sed s/.fa//g >queries86.list")
	write_blast_qsubscript(35,atoi(commands.getoutput("cat queries35.list | wc -l")),"PAM30",path)
	write_blast_qsubscript(50,atoi(commands.getoutput("cat queries50.list | wc -l")),"PAM70",path)
	write_blast_qsubscript(85,atoi(commands.getoutput("cat queries85.list | wc -l")),"BLOSUM80",path)
	write_blast_qsubscript(86,atoi(commands.getoutput("cat queries86.list | wc -l")),"BLOSUM62",path)
		


def write_blast_qsubscript(seqlen,n,mat,path):
	fo=open("%s/blast-%d.sh"%(path,seqlen),'w')
	fo.write("#!/bin/sh\n")
	fo.write("#$ -N pdb-blast\n")
	fo.write("#$ -q all.q\n")
	fo.write("#$ -e %s/logs/blast-cache\n"%(path))
	fo.write("#$ -o %s/logs/blast-cache\n"%(path))
	fo.write("#$ -t 1-%d\n"%(n))
	fo.write("#$ -l ram=16G\n")
	fo.write("#$ -l s_rt=23:40:00,h_rt=24:00:00\n")
	fo.write("query=`sed \"${SGE_TASK_ID}q;d\" %s/unique_fasta/queries%d.list`\n"%(path,seqlen))
	fo.write("matrix=%s\n"%(mat))
	fo.write("time /gpfs/home/baskaran_k/software/packages/ncbi-blast-2.2.29+/bin/blastp -matrix $matrix -db /scratch/baskaran_k/uniprot_2014_06/uniref100.fasta -query %s/unique_fasta/$query.fa -num_threads 12 -outfmt 5 -seg no | gzip > %s/blast_cache_uniprot_2014_05/$query.blast.xml.gz\n"%(path,path))
	fo.close()


if __name__=="__main__":
	create_blast_chunk("queries.list")
	
