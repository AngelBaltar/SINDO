from datetime import timedelta
from datetime import datetime
from StockDataAnalysis import *
from StockMeasure import *
from all_index_nasdaq import *
import multiprocessing
import argparse
import sys
import time


def analizer(stock_analisys):
	stock_analisys.analyze()
	return stock_analisys

def data_filler(stock_historic_meas):
	stock_historic_meas.fill_data()
	return stock_historic_meas
		
if __name__ == "__main__":

	parser = argparse.ArgumentParser()
	parser.add_argument('-idx',required=False,metavar='N',nargs='+',dest='index_file_list')
	parser.add_argument('--all_nasdaq',required=False,nargs='?',type=int,const=1,metavar='<all_nasdaq>',dest='all_nasdaq')
	parser.add_argument('-hist',required=True,metavar='<history_days>',type=int,dest='hist_days')
	parser.add_argument('-o',required=True,metavar='<out_file>',dest='out_file')
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
	data_list=[]
	count=0
	print "Retrieving data..."

	p = multiprocessing.Pool(max(multiprocessing.cpu_count()-2,2))
	
	for i in idx_list:
		h=StockHistoricMeasure(td-timedelta(days=configuration.hist_days),td,i)
		data_list.append(h)

	data_list=p.map(data_filler,data_list)
	
	for i in data_list:
		kk=DividendAnalysis()
		kk.set_hist(i)
		analisys_list.append(kk)

	print "\nAnalyzing data..."
	
	analisys_list=p.map(analizer, analisys_list)
	p.close()
	p.join()

	fo=open(configuration.out_file,'w')
	analisys_list.sort(reverse=True)
	count=0
	for i in analisys_list:
		if i.get_score()>0:
			fo.write(str(i)+"\n")
	end=time.time()
	print "elapsed time %f"%(end-start)
