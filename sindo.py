from datetime import timedelta
from datetime import datetime
from StockDataAnalysis import *
from StockMeasure import *
from all_index_nasdaq import *
import multiprocessing
import argparse
import sys
import time

version="v0.1"


def analizer(stock_analisys):
	stock_analisys.analyze()
	return stock_analisys

def data_filler(stock_historic_meas):
	stock_historic_meas.fill_data()
	return stock_historic_meas
		
if __name__ == "__main__":

	parser = argparse.ArgumentParser()
	parser.add_argument('-idx',required=False,metavar='N',nargs='+',dest='index_file_list')
	parser.add_argument('-list_idx',required=False,metavar='<list_idx>',dest='list_idx')
	parser.add_argument('-version',required=False,nargs='?',type=bool,const=True,metavar='<version>',dest='version')
	parser.add_argument('-hist',required=False,metavar='<history_days>',type=int,dest='hist_days')
	parser.add_argument('-o',required=False,metavar='<out_file>',dest='out_file')
	parser.add_argument('-print_historics',required=False,nargs='?',type=bool,const=True,metavar='<print_historics>',dest='print_historics')
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

	fo=open(configuration.out_file+".csv",'w')
	fpy=open(configuration.out_file+".py",'w')

	analisys_list.sort(reverse=True)
	count=0
	stock_list=[]
	fo.write(DividendAnalysis.get_csv_str())
	for i in analisys_list:
		if(configuration.print_historics):
			fh=open(configuration.out_file+"_"+str(i.get_hist().get_idx())+".csv",'w')
			i.get_hist().print_to_csv(fh)
			fh.close()
		if i.get_score()>0:
			fo.write(str(i)+"\n")
			stock_list.append(str(i.get_hist().get_idx()))

	
	fpy.write("stock_list=%s"%str(stock_list))
	fpy.close()
	fo.close()
	end=time.time()
	print "elapsed time %f"%(end-start)
