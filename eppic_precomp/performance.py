import sys,os,commands
from string import atoi,atof
from math import sqrt


def get_TP(database,dataset,method,cutoff):
	cmd="mysql -h localhost -u root -ppasswd -B -N -e 'select count(*) from %s.%s_bio where %sScore<=%f and %s not like \"nopred\"'"%(database,dataset,method,cutoff,method)
	return commands.getoutput(cmd)
def get_TN(database,dataset,method,cutoff):
        cmd="mysql -h localhost -u root -ppasswd -B -N -e 'select count(*) from %s.%s_xtal where %sScore>%f and %s not like \"nopred\"'"%(database,dataset,method,cutoff,method)
        return commands.getoutput(cmd)
def get_P(database,dataset,method,includeNopred):
	if includeNopred==1:
		cmd="mysql -h localhost -u root -ppasswd -B -N -e 'select count(*) from %s.%s_bio;'"%(database,dataset)
	else:
		cmd="mysql -h localhost -u root -ppasswd -B -N -e 'select count(*) from %s.%s_bio where %s not like \"nopred\";'"%(database,dataset,method)
	return commands.getoutput(cmd)
def get_N(database,dataset,method,includeNopred):
        if includeNopred==1:
                cmd="mysql -h localhost -u root -ppasswd -B -N -e 'select count(*) from %s.%s_xtal;'"%(database,dataset)
        else:
                cmd="mysql -h localhost -u root -ppasswd -B -N -e 'select count(*) from %s.%s_xtal where %s not like \"nopred\";'"%(database,dataset,method)
        return commands.getoutput(cmd)


def get_performance(database,dataset,method,cutoff,includeNopred):
	TP=atof(get_TP(database,dataset,method,cutoff))
	TN=atof(get_TN(database,dataset,method,cutoff))
	P=atof(get_P(database,dataset,method,includeNopred))
	N=atof(get_N(database,dataset,method,includeNopred))
	FN=P-TP
	FP=N-TN
	p=TP+FP
	n=TN+FN
	sen=TP/P
	spe=TN/N
	acc=(TP+TN)/(P+N)
	mcc=(TP*TN-FP*FN)/sqrt(P*N*p*n)
	return [sen,spe,acc,mcc]


def get_full_performance(database,dataset,method,includeNopred,cmin,cmax,dc):
	P=atof(get_P(database,dataset,method,includeNopred))
        N=atof(get_N(database,dataset,method,includeNopred))
	cutoff=cmin
	while (cutoff<cmax):
		TP=atof(get_TP(database,dataset,method,cutoff))
        	TN=atof(get_TN(database,dataset,method,cutoff))
		FN=P-TP
        	FP=N-TN
        	p=TP+FP
        	n=TN+FN
		#print P,TP,N,TN,p,n
        	sen=TP/P
        	spe=TN/N
        	acc=(TP+TN)/(P+N)
		if p>0 and n>0:
        		mcc=((TP*TN)-(FP*FN))/sqrt(P*N*p*n)
		else:
			mcc=0
		if mcc<0:mcc=0
		#print P,TP,N,TN,p,n
		print "%.4f\t%.4f\t%.4f\t%.4f\t%.4f"%(cutoff,sen,spe,acc,mcc)
		cutoff+=dc



if __name__=="__main__":
	database=sys.argv[1]
	dataset=sys.argv[2]
	method=sys.argv[3]
	includeNopred=atoi(sys.argv[4])
	cmin=atof(sys.argv[5])
	cmax=atof(sys.argv[6])
	dc=atof(sys.argv[7])
	get_full_performance(database,dataset,method,includeNopred,cmin,cmax,dc)
