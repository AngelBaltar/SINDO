from datetime import timedelta
from datetime import datetime
import yfinance as yf
import argparse

#stock investment network data organizer
class StocDaykMeasure(object):

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

class StockDataAnalysys(object):
	def __init__(self,date_start,date_end,idx):
		self._st_datas=[]
		self._div_dates=[]
		self._dividend_period=0
		self._analyze(date_start,date_end,idx)

	def _get_stock_measure(self,date):
		for k in self._st_datas:
			if(k.get_date()==date):
				return k
		return None

	def _do_analysis(self):
		print "not implemented"
		pass

	def _analyze(self,date_start,date_end,idx):
		#fill
		#self._st_datas
		msft = yf.Ticker(idx)

		tot_time=date_end-date_start
		per=str(tot_time.days)+"d"
		print per
		# get historical market data
		hist = msft.history(period=per)

		for i in range(0,len(hist['Open'])):
			dt=datetime.strptime(str(hist.axes[0][i]), "%Y-%m-%d %H:%M:%S")
			stock=StocDaykMeasure(idx,dt,hist['Open'][i],hist['Close'][i],(hist['Dividends'][i]!=0.0))
			self._st_datas.append(stock)
			print stock
		self._do_analysis()

class DividendAnalysis(StockDataAnalysys):

	def __init__(self,date_start,date_end,idx):
		self._div_dates=[]
		self._dividend_period=0
		self._days_buy=[]
		self._days_sell=[]
		self._benefits=[]
		super(DividendAnalysis,self).__init__(date_start,date_end,idx)

	def _calc_dividend_dates(self):
		for k in self._st_datas:
			if(k.is_dividend()):
				self._div_dates.append(k.get_date())

	def _get_next_dividend_date(self):
		if(self._dividend_period==0):
			raise Exception("No divindend dates")

		td=timedelta(days=self._dividend_period)
		return(self._div_dates[len(self._div_dates)-1]+td)		

	def _calc_dividend_period(self):
		
		if (len(self._div_dates)<2):
			self._dividend_period=0
		else:
			l=len(self._div_dates)
			self._dividend_period=(self._div_dates[l-1]-self._div_dates[l-2]).days
		print "period:",self._dividend_period

	def _calc_segment(self,date_start,date_div,date_end):
		curr_d=date_start

		delta_t=timedelta(days=1)
		min=9999999
		min_date=date_start
		min_st=None
		while(curr_d<date_div):
			st=self._get_stock_measure(curr_d)
			if (st!=None) and (st.get_close()<min):
				min=st.get_close()
				min_date=curr_d
				min_st=st
			curr_d=curr_d+delta_t

		max=0
		max_date=min_date
		max_st=None
		while(curr_d<date_end):
			st=self._get_stock_measure(curr_d)
			if (st!=None) and (st.get_close()>max):
				max_date=curr_d
				max_st=st
				max=st.get_close()

			curr_d=curr_d+delta_t

		benefit=100*(max_st.get_close()-min_st.get_close())/min_st.get_close()
		days_min=(min_date-date_div).days
		days_max=(max_date-date_div).days
		print "---------------------------------------------------------"
		print "date min:",min_date
		print "price min:",min_st.get_close()
		print "date max:",max_date
		print "price max:",max_st.get_close()
		print "days_min:",days_min
		print "days_min:",days_max
		print "benefit:",benefit,"%"
		print "---------------------------------------------------------"

		self._days_buy.append(days_min)
		self._days_sell.append(days_max)
		self._benefits.append(benefit)


	def _do_analysis(self):
		self._calc_dividend_dates()
		self._calc_dividend_period()
		dt_range=timedelta(days=10)
		for k in self._div_dates:
			self._calc_segment(k-dt_range,k,k+dt_range)

		day_buy_mean=0
		day_sell_mean=0
		if(len(self._days_buy)!=len(self._days_sell)):
			raise Exception("(len(self._days_buy)!=len(self._days_sell))")
		for i in range(0,len(self._days_buy)):
			day_sell_mean+=self._days_sell[i]
			day_buy_mean+=self._days_buy[i]

		day_buy_mean/=len(self._days_buy)
		day_sell_mean/=len(self._days_buy)
		print "buy mean:",day_buy_mean
		print "sell mean:",day_sell_mean

		next_dividend=self._get_next_dividend_date()
		td_buy=timedelta(days=day_buy_mean)
		td_sell=timedelta(days=day_sell_mean)

		date_buy=next_dividend+td_buy
		date_sell=next_dividend+td_sell
		print "Investment Advice:"
		print "Buy date:",date_buy
		print "Sell date:",date_sell


if __name__ == "__main__":

	parser = argparse.ArgumentParser()
	parser.add_argument('-idx',required=True,metavar='N',nargs='+',dest='index_file_list')
	parser.add_argument('-history',required=True,metavar='N',type=int,nargs='+',dest='hist_days_list')
	configuration = parser.parse_args()
	if(len(configuration.index_file_list)!=len(configuration.hist_days_list)):
		print "index and historics do not match"
		sys.exit(1)

	td=datetime.now()-timedelta(days=30)
	for i in range(0,len(configuration.index_file_list)):
		kk=DividendAnalysis(td-timedelta(days=configuration.hist_days_list[i]),td,configuration.index_file_list[i])
