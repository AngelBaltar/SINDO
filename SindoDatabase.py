from StockMeasure import *
import time
import yfinance as yf
from datetime import timedelta
import os
import sys

def _fetch_data_from_yf(idx,t_init,t_end):

	while(t_init.weekday()==5) or ((t_init.weekday()==6)):
			t_init-=timedelta(days=1)

	while(t_end.weekday()==5) or ((t_end.weekday()==6)):
		t_end+=timedelta(days=1)

	#print "fetch from yf %s %s %s"%(idx,t_init,t_end)
	msft = yf.Ticker(idx)

	tot_time=t_end-t_init
	per=str(tot_time.days)+"d"
	#print per
	# get historical market datas
	sys.stdout = open(os.devnull, "w") #avoid printing

	try:
		hist = msft.history(start=t_init.strftime('%Y-%m-%d'),end=t_end.strftime('%Y-%m-%d'))
	except Exception as e:
		sys.stdout = sys.__stdout__
		#print e
		return None
	sys.stdout = sys.__stdout__
	datas=[]
	last_dt=t_init
	for i in range(0,len(hist['Open'])):
		dt=datetime.strptime(str(hist.axes[0][i]), "%Y-%m-%d %H:%M:%S")
		
		while((i>0) and (last_dt<dt)):#fill the gap with the last data
			stock=StockDaykMeasure(idx,last_dt,hist['Open'][i-1],hist['Close'][i-1],(hist['Dividends'][i-1]!=0.0))
			datas.append(stock)
			last_dt+=timedelta(days=1)

		last_dt=dt
		stock=StockDaykMeasure(idx,dt,hist['Open'][i],hist['Close'][i],(hist['Dividends'][i]!=0.0))
		datas.append(stock)

	if(len(datas)>0):
		sm=StockHistoricMeasure(idx,datas)
		return sm
	else:
		return None

def _fetch_from_file_sys(idx,t_init=None,t_end=None):
	try:
		f_data=open("SINDODB/%s.csv"%idx,'r')
		datas=[]
		ln=f_data.readline()
		ln=f_data.readline()
		while(ln):
			st=StockDaykMeasure(idx,'','','','')
			st.fill_from_csv_line(ln)
			if(t_init==None and t_end==None) or ((st.get_date()>=t_init) and ((st.get_date()<=t_end))):
				datas.append(st)
			ln=f_data.readline()
		f_data.close()
		if(len(datas)>0):
			return StockHistoricMeasure(idx,datas)
		else:
			return None
	except IOError:
		return None

def _fetch_data_from_database(idx,t_init,t_end):
	
	sm=_fetch_from_file_sys(idx,t_init,t_end)
	if(sm==None):
		sm=_fetch_data_from_yf(idx,t_init,t_end)
	else:
		datas_init=sm.get_start_date()
		datas_end=sm.get_end_date()
		if(t_init<datas_init):
			sm=sm+_fetch_data_from_yf(idx,t_init,datas_init-timedelta(days=1))
		if(t_end>datas_end):
			sm=sm+_fetch_data_from_yf(idx,datas_end+timedelta(days=1),t_end)
	return sm

def _refill_database(sm):
	#TODO
	all_file=_fetch_from_file_sys(sm.get_idx())
	incr=None
	if(all_file==None):
		incr=sm
	else:
		incr_start_date=all_file.get_start_date()
		incr_end_date=all_file.get_end_date()

		if(all_file.get_end_date()<sm.get_end_date()):
			incr_end_date=sm.get_end_date()
		
		if(all_file.get_start_date()>sm.get_start_date()):
			incr_start_date=sm.get_start_date()

		delta_t=timedelta(days=1)
		datas=[]
		while(incr_start_date<=incr_end_date):
			st=sm[incr_start_date]
			if(st==None):
				st=all_file[incr_start_date]
			if(st!=None):
				datas.append(st)
			incr_start_date=incr_start_date+delta_t
		if len(datas)>0:
			incr=StockHistoricMeasure(sm.get_idx(),datas)

	if(incr):
		f_data=open("SINDODB/%s.csv"%sm.get_idx(),'w')
		
		incr.print_to_csv(f_data)
		f_data.close()

def get_data(t_init,t_end,idx):
	sm=_fetch_data_from_database(idx,t_init,t_end)
	#print "fetch done"
	if sm:
		_refill_database(sm)
	#print "refill done"
	# hist=sm
	# for k in hist:
	# 	print k.get_date()
	return sm
