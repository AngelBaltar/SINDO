from StockMeasure import *

def _fetch_data_from_yf(t_init,t_end,idx):

	msft = yf.Ticker(idx)

	tot_time=t_end-t_init
	per=str(tot_time.days)+"d"
	#print per
	# get historical market data
	try:
		hist = msft.history(period=per)
	except:
		time.sleep(0.2)
		hist = msft.history(period=per)

	datas=[]
	for i in range(0,len(hist['Open'])):
		dt=datetime.strptime(str(hist.axes[0][i]), "%Y-%m-%d %H:%M:%S")
		stock=StockDaykMeasure(idx,dt,hist['Open'][i],hist['Close'][i],(hist['Dividends'][i]!=0.0))
		datas.append(stock)

	sm=StockHistoricMeasure(idx,datas)
	return sm

def _fetch_data_from_database(f_data,t_init,t_end,idx):
	datas=[]
	ln=readline(f_data)
	ln=readline(f_data)
	while(ln):
		st=StockMeasure(idx,'','','','')
		st.fill_from_csv_line(ln)
		datas.append()
		ln=readline(f_data)

	datas_init=datas[0].get_date()
	datas_end=datas[-1].get_date()
	sm=StockHistoricMeasure(idx,datas)
	if(t_init<datas_init):
		sm=sm+_fetch_data_from_yf(t_init,datas_init)
	if(t_end>datas_end):
		sm=sm+_fetch_data_from_yf(datas_end,t_end)

	return sm


def get_data(t_init,t_end,idx):
	try:
		f_data=open("SINDODB/%s.csv"%idx,'r')
		sm=_fetch_data_from_database(f_data,t_init,t_end,idx)
		f_data.close()
	except:
		#no data, retrieve it all
		sm=_fetch_data_from_yf(t_init,t_end,idx)

	f_data=open("SINDODB/%s.csv"%idx,'w')
	sm.print_to_csv(f_data)
	f_data.close()
	return sm
