#!/bin/sh

#$ -N JOBNAME
#$ -q all.q
#$ -e LOGDIR
#$ -o LOGDIR
#$ -t 1-MAXTASK
#$ -l ram=MAXRAM
#$ -l s_rt=TIMEMIN,h_rt=TIMEMAX

maxtries=20
sleeptime=300
hostname=`hostname` 


pdb=`grep -v "^#"  INPUTLIST | sed "s/\(....\).*/\1/" | sed "${SGE_TASK_ID}q;d"`

# Cut the middle letters of pdb code for making directory in divided
mid_pdb=`echo $pdb | awk -F "" '{print $2$3}'`

# Check is directory is not present
if [ ! -d OUTFOLDER/data/divided/$mid_pdb ]; then mkdir -p OUTFOLDER/data/divided/$mid_pdb; fi
if [ ! -d OUTFOLDER/data/divided/$mid_pdb/$pdb ]; then mkdir -p OUTFOLDER/data/divided/$mid_pdb/$pdb; fi
cd OUTFOLDER/data/all/
ln -s ../divided/$mid_pdb/$pdb $pdb

for i in `seq 1 $maxtries`
do
        java -Xmx4g -Xmn512m -version > /dev/null 2>&1
        out="$?"
        if [ "$out" -gt 0 ]
        then
                echo "Java failed to start in $hostname (attempt $i ), will try again in $sleeptime seconds" 1>&2
                sleep $sleeptime
        else
		EPPIC -i $pdb -a 1 -s -o OUTFOLDER/data/divided/$mid_pdb/$pdb -l -w -g CONF
		cp OUTFOLDER/logs/JOBNAME.e${JOB_ID}.${SGE_TASK_ID} OUTFOLDER/data/divided/$mid_pdb/$pdb/$pdb.e
		cp OUTFOLDER/logs/JOBNAME.o${JOB_ID}.${SGE_TASK_ID} OUTFOLDER/data/divided/$mid_pdb/$pdb/$pdb.o
                exit 0
        fi
done 

#EPPIC -i $pdb -a 1 -s -o OUTFOLDER/data/divided/$mid_pdb/$pdb -l -w -g CONF
#cp OUTFOLDER/logs/JOBNAME.e${JOB_ID}.${SGE_TASK_ID} OUTFOLDER/data/divided/$mid_pdb/$pdb/$pdb.e
#cp OUTFOLDER/logs/JOBNAME.o${JOB_ID}.${SGE_TASK_ID} OUTFOLDER/data/divided/$mid_pdb/$pdb/$pdb.o

