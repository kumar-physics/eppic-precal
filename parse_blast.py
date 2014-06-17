import gzip,os,commands,re,sys
def split_blast_files(fname):
	dat=gzip.open(fname,'rb').read().split("<Iteration>")
	query_def_header=re.search(r"[\Ss]+(BlastOutput_query-def>[\Ss]+</BlastOutput_query-def)[\Ss]+",dat[0]).groups()[0]
	query_len_header=re.search(r"[\Ss]+(BlastOutput_query-len>[\Ss]+</BlastOutput_query-len)[\Ss]+",dat[0]).groups()[0]
	for query in dat[1:]:
		query_def=re.search(r"[\Ss]+Iteration_query-def>([\Ss]+)</Iteration_query-def[\Ss]+",query).groups()[0]
		query_len=re.search(r"[\Ss]+Iteration_query-len>([\Ss]+)</Iteration_query-len[\Ss]+",query).groups()[0]
		header=re.sub(query_len_header,"BlastOutput_query-len>%s</BlastOutput_query-len"%(query_len),re.sub(query_def_header,"BlastOutput_query-def>%s</BlastOutput_query-def"%(query_def),dat[0]))
		body=re.sub(re.search(r"[\Ss]+(Iteration_query-ID>[\Ss]+</Iteration_query-ID)[\Ss]+",query).groups()[0],"Iteration_query-ID>Query_1</Iteration_query-ID",re.sub(re.search(r"[\Ss]+(Iteration_iter-num>[\Ss]+</Iteration_iter-num)[\Ss]+",query).groups()[0],"Iteration_iter-num>1</Iteration_iter-num",query))
		if query==dat[-1]:
			outdat="".join([header,"<Iteration>",body])
		else:
			outdat="".join([header,"<Iteration>",body,"</BlastOutput_iterations>\n</BlastOutput>"])
		gzip.open("%s.blast.xml.gz"%(query_def),'wb').write(outdat)
if __name__=="__main__":
	fname=sys.argv[1]
	split_blast_files(fname)
	
