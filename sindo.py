from datetime import timedelta
from datetime import datetime
from StockDataAnalysis import *
from StockMeasure import *
from all_index_nasdaq import *
from SindoDatabase import *
import multiprocessing
import argparse
import sys
import time

version="v0.2"

def analizer(idx):
	td=datetime.now()
	h=get_data(td-timedelta(days=configuration.hist_days),td,idx)
	kk=DividendAnalysis()
	if(h):
		kk.set_hist(h)
		kk.analyze()
		h.free_memory()
		return kk
	return StockDataAnalysis()
	

		
if __name__ == "__main__":

	parser = argparse.ArgumentParser()
	parser.add_argument('-idx',required=False,metavar='N',nargs='+',dest='index_file_list')
	parser.add_argument('-list_idx',required=False,metavar='<list_idx>',dest='list_idx')
	parser.add_argument('-version',required=False,nargs='?',type=bool,const=True,metavar='<version>',dest='version')
	parser.add_argument('-hist',required=False,metavar='<history_days>',type=int,dest='hist_days')
	parser.add_argument('-o',required=True,metavar='<out_file>',dest='out_file')
	configuration = parser.parse_args()

	if(configuration.version):
		print version
		sys.exit(0)
	if(configuration.list_idx):
		execfile(configuration.list_idx)
		idx_list=stock_list
	elif(configuration.index_file_list):
		idx_list=configuration.index_file_list
	else:
		print "argument error no index list"
		sys.exit(1)
	
	start=time.time()
	

	analisys_list=[]
	print "working..."

	p = multiprocessing.Pool(max(multiprocessing.cpu_count(),2))
	

	print_list=[]
	
	print_list=p.map(analizer,idx_list)
	p.close()
	p.join()

	fo=open(configuration.out_file+".csv",'w')
	fo.write(DividendAnalysis.get_csv_str())
	fpy=open(configuration.out_file+".py",'w')

	# for k in idx_list:
	#  	print_list.append(analizer(k))
	print_list.sort(reverse=True)
	stock_list=[]
	for k in print_list:
		if(k):
			fo.write(str(k))
			if(k.get_score()>0):
				stock_list.append(k.get_idx())
				print(str(k))

	fo.close()
	fpy.write(str(stock_list))
	fpy.close()
	end=time.time()
	print "elapsed time %f"%(end-start)
