from datetime import timedelta
from datetime import datetime
import yfinance as yf
import argparse
from all_index_nasdaq import *
import sys
import math
from multiprocessing import Pool
import time


def mean(l):
	m=0
	for k in l:
		m+=k
	if(len(l)>0):
		m/=len(l)
	return m

def st_dev(l,m=None):
	if m==None:
		m=mean(l)
	dev=0
	for k in l:
		dev+=(k-m)*(k-m)
	if(len(l)>0):
		dev/=len(l)
	dev=math.sqrt(dev)
	return dev

#stock investment network data organizer
class StockDaykMeasure(object):

	def __init__(self,idx,dt,op,cls,div):
		self._dt=dt
		self._op=op
		self._cls=cls
		self._div=div
		self._idx=idx

	def __str__(self):
		ret=self._idx+" at "+str(self.get_date())
		ret+=" Open: %02.02f Close: %02.02f"%(self.get_open(),self.get_close())
		ret+=" Div: "+str(self.is_dividend())
		return ret

	def get_close(self):
		return self._cls

	def get_open(self):
		return self._op

	def is_dividend(self):
		return self._div

	def get_index(self):
		return self._idx

	def get_date(self):
		return self._dt

	def get_grad(self):
		return get_close()-get_open()

class StockHistoricMeasure(object):

	def __init__(self,date_start,date_end,idx):
		self._date_start=date_start
		self._date_end=date_end
		self._idx=idx
		self._st_datas={}
		self.fill_data()

	def __str__(self):
		return "%s [%s]->[%s]"%(self._idx,str(self._date_start),str(self._date_end))

	def get_start_date(self):
		return self._date_start

	def get_end_date(self):
		return self._date_end

	def get_idx(self):
		return self._idx

	def __iter__(self):
		return self._st_datas.__iter__()

	def __next__(self):
		k=self._st_datas.__next__()
		print k
		return k

	def __getitem__(self, index):
		try:
			return self._st_datas[str(index)]
		except:
			return None


	def fill_data(self):
		#fill
		#self._st_datas
		msft = yf.Ticker(self._idx)

		tot_time=self._date_end-self._date_start
		per=str(tot_time.days)+"d"
		#print per
		# get historical market data
		try:
			hist = msft.history(period=per)
		except:
			time.sleep(4)
			hist = msft.history(period=per)

		for i in range(0,len(hist['Open'])):
			dt=datetime.strptime(str(hist.axes[0][i]), "%Y-%m-%d %H:%M:%S")
			stock=StockDaykMeasure(self._idx,dt,hist['Open'][i],hist['Close'][i],(hist['Dividends'][i]!=0.0))
			self._st_datas[str(stock.get_date())]=stock
			# print stock


class StockDataAnalysys(object):
	
	def __init__(self):
		self._score=0
		self._hist=None

	def __init__(self,date_start,date_end,idx):
		self._score=0
		self._hist=StockHistoricMeasure(date_start,date_end,idx)

	def __str__(self):
		return "%s:%f"%(str(self._hist),self.get_score())

	def get_score(self):
		return self._score

	def _set_score(self,s):
		self._score=s

	def _get_hist(self):
		return self._hist

	def __cmp__(self,obj):
		return cmp(self.get_score(),obj.get_score())
		
	
	def analyze(self):
		raise Exception("analyze shall be override on lowe class")

class DividendAnalysis(StockDataAnalysys):

	def __init__(self):
		self._div_dates=[]
		self._dividend_period=0
		self._days_buy=[]
		self._days_sell=[]
		self._benefits=[]
		self._date_buy=None
		self._date_sell=None
		self._benefit_mean=0
		self._std_dev_day_buy=0
		self._std_dev_day_sell=0
		super(DividendAnalysis,self).__init__()

	def __init__(self,date_start,date_end,idx):
		self._div_dates=[]
		self._dividend_period=0
		self._days_buy=[]
		self._days_sell=[]
		self._benefits=[]
		self._date_buy=None
		self._date_sell=None
		self._benefit_mean=0
		self._std_dev_day_buy=0
		self._std_dev_day_sell=0
		super(DividendAnalysis,self).__init__(date_start,date_end,idx)

	def __str__(self):
		ret=super(DividendAnalysis,self).__str__()+"\n"
		ret+="Buy date:"+str(self._date_buy)+"\n"
		ret+="Sell date:"+str(self._date_sell)+"\n"
		ret+="Benefit mean:"+str(self._benefit_mean)+"\n"
		ret+="buy deviation:"+str(self._std_dev_day_buy)+"\n"
		ret+="sell deviation:"+str(self._std_dev_day_sell)+"\n"
		return ret

	def _calc_dividend_dates(self):
		hist=self._get_hist()
		for k in hist:
			if(hist[k].is_dividend()):
				self._div_dates.append(hist[k].get_date())

	def _get_next_dividend_date(self):
		if(self._dividend_period==0):
			return None

		td=timedelta(days=self._dividend_period)
		return(self._div_dates[len(self._div_dates)-1]+td)

	def _calc_dividend_period(self):

		if (len(self._div_dates)<2):
			self._dividend_period=0
		else:
			l=len(self._div_dates)
			self._dividend_period=(self._div_dates[l-1]-self._div_dates[l-2]).days
		#print "period:",self._dividend_period

	def _calc_segment(self,date_start,date_div,date_end):
		curr_d=date_start

		hist=self._get_hist()
		delta_t=timedelta(days=1)
		min=9999999
		min_date=date_start
		min_st=hist[curr_d]
		while(curr_d<date_div):
			st=hist[curr_d]
			if (st!=None) and (st.get_close()<min):
				min=st.get_close()
				min_date=curr_d
				min_st=st
			curr_d=curr_d+delta_t

		curr_d=min_date
		max=0
		max_date=min_date
		max_st=hist[curr_d]
		while(curr_d<date_end):
			st=hist[curr_d]
			if (st!=None) and (st.get_close()>max):
				max_date=curr_d
				max_st=st
				max=st.get_close()

			curr_d=curr_d+delta_t

		if(max_st==None or min_st==None):
			return

		benefit=100*(max_st.get_close()-min_st.get_close())/min_st.get_close()
		days_min=(min_date-date_div).days
		days_max=(max_date-date_div).days
		# print "---------------------------------------------------------"
		# print "date min:",min_date
		# print "price min:",min_st.get_close()
		# print "date max:",max_date
		# print "price max:",max_st.get_close()
		# print "days_min:",days_min
		# print "days_min:",days_max
		# print "benefit:",benefit,"%"
		# print "---------------------------------------------------------"

		self._days_buy.append(days_min)
		self._days_sell.append(days_max)
		self._benefits.append(benefit)


	def analyze(self):
		self._calc_dividend_dates()
		self._calc_dividend_period()
		if(self._dividend_period==0):
			#print "skipping %s no dividends"%self._idx
			return
		dt_range=timedelta(days=10)
		for k in self._div_dates:
			self._calc_segment(k-dt_range,k,k+dt_range)

		day_buy_mean=mean(self._days_buy)
		day_sell_mean=mean(self._days_sell)
		self._benefit_mean=mean(self._benefits)

		#print "buy mean:",day_buy_mean
		#print "sell mean:",day_sell_mean

		self._std_dev_day_buy=st_dev(self._days_buy,day_buy_mean)
		self._std_dev_day_sell=st_dev(self._days_sell,day_sell_mean)


		next_dividend=self._get_next_dividend_date()
		td_buy=timedelta(days=day_buy_mean)
		td_sell=timedelta(days=day_sell_mean)

		self._date_buy=next_dividend+td_buy
		self._date_sell=next_dividend+td_sell

		score=(self._std_dev_day_sell+1)*(self._std_dev_day_buy+1)
		self._set_score(score)


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
	for i in idx_list:
		kk=DividendAnalysis(td-timedelta(days=configuration.hist_days),td,i)
		analisys_list.append(kk)
		count+=1
		sys.stdout.write("\r%02d%%"%(count*100/len(idx_list)))
		sys.stdout.flush()

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

	analisys_list.sort()
	count=0
	for i in analisys_list:
		print i
		count+=1
		if(count>5):
			break
	end=time.time()
	print "elapsed time %f"%(end-start)
