from datetime import timedelta
from datetime import datetime
from StockDataAnalysis import *
from all_index_nasdaq import *
from multiprocessing import Pool
import argparse
import sys
import time


def analizer(stock_analisys):
	stock_analisys.analyze()
	return stock_analisys

def data_filler(stock_historic_meas):
	pass
		
if __name__ == "__main__":

	parser = argparse.ArgumentParser()
	parser.add_argument('-idx',required=False,metavar='N',nargs='+',dest='index_file_list')
	parser.add_argument('--all_nasdaq',required=False,nargs='?',type=int,const=1,metavar='<all_nasdaq>',dest='all_nasdaq')
	parser.add_argument('-hist',required=True,metavar='<history_days>',type=int,dest='hist_days')
	configuration = parser.parse_args()

	if(configuration.all_nasdaq):
		idx_list=all_index_nasdaq
	elif(configuration.index_file_list):
		idx_list=configuration.index_file_list
	else:
		print "argument error no index list"
		sys.exit(1)
	start=time.time()
	td=datetime.now()
	analisys_list=[]
	count=0
	print "Retrieving data..."
	for i in idx_list:
		kk=DividendAnalysis(td-timedelta(days=configuration.hist_days),td,i)
		analisys_list.append(kk)
		count+=1
		sys.stdout.write("\r%02d%%"%(count*100/len(idx_list)))
		sys.stdout.flush()

	print "\nAnalyzing data..."
	p = Pool(2)
	analisys_list=p.map(analizer, analisys_list)
	p.close()
	p.join()

	# count=0
	# for a in analisys_list:
	# 	a.analyze()
	# 	count+=1
	# 	sys.stdout.write("\r%02d%%"%(count*100/len(analisys_list)))
	# 	sys.stdout.flush()

	analisys_list.sort(reverse=True)
	count=0
	for i in analisys_list:
		print i
		count+=1
		if(count>20):
			break
	end=time.time()
	print "elapsed time %f"%(end-start)
