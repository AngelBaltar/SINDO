from StockMeasure import *
from datetime import timedelta
from datetime import datetime
import math

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

class StockDataAnalysis(object):
	
	def __init__(self):
		self._score=0
		self._hist=None

	def set_hist(self,h):
		self._hist=h

	@classmethod
	def get_csv_str(self):
		return "%s;score"%(StockHistoricMeasure.get_csv_str())

	def __str__(self):
		return "%s;%s"%(str(self._hist),str(self.get_score()).replace('.',','))

	def get_score(self):
		return self._score

	def _set_score(self,s):
		self._score=s

	def get_hist(self):
		return self._hist

	def __cmp__(self,obj):
		return cmp(self.get_score(),obj.get_score())
		
	
	def analyze(self):
		raise Exception("analyze shall be override on lowe class")

class DividendAnalysis(StockDataAnalysis):

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

	def get_date_buy(self):
		return self._date_buy

	def get_date_sell(self):
		return self._date_sell

	@classmethod
	def get_csv_str(self):
		ret=super(DividendAnalysis,self).get_csv_str()+";"
		ret+="Date Buy;"
		ret+="Date Sell;"
		ret+="Benefit mean;"
		ret+="Buy deviation;"
		ret+="Sell deviation\n"
		return ret

	def __str__(self):
		ret=super(DividendAnalysis,self).__str__()+";"
		ret+=str(self._date_buy)+";"
		ret+=str(self._date_sell)+";"
		ret+=str(self._benefit_mean).replace('.',',')+";"
		ret+=str(self._std_dev_day_buy).replace('.',',')+";"
		ret+=str(self._std_dev_day_sell).replace('.',',')+"\n"
		return ret

	def _calc_dividend_dates(self):
		hist=self.get_hist()
		for k in hist:
			if(k.is_dividend()):
				self._div_dates.append(k.get_date())
		#print len(self._div_dates)

	def _get_next_dividend_date(self):
		if(self._dividend_period==0):
			return None

		#print self._div_dates[len(self._div_dates)-1]
		#print self._dividend_period
		td=timedelta(days=self._dividend_period)
		return(self._div_dates[-1]+td)

	def _calc_dividend_period(self):

		if (len(self._div_dates)<2):
			self._dividend_period=0
		else:
			self._dividend_period=abs((self._div_dates[-2]-self._div_dates[-1]).days)
		#print "period:",self._dividend_period

	def _calc_segment(self,date_start,date_div,date_end):
		curr_d=date_start

		hist=self.get_hist()
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
		if(len(self._div_dates)<2):
			print "skipping %s no enough dividends"%self.get_hist().get_idx()
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
		if(next_dividend==None):
			return
		#print "next dividend ",next_dividend
		td_buy=timedelta(days=day_buy_mean)
		td_sell=timedelta(days=day_sell_mean)

		self._date_buy=next_dividend+td_buy
		while(self._date_buy.weekday()==5) or ((self._date_buy.weekday()==6)):
			self._date_buy+=timedelta(days=1)
		
		self._date_sell=next_dividend+td_sell
		while(self._date_sell.weekday()==5) or ((self._date_sell.weekday()==6)):
			self._date_sell-=timedelta(days=1)
		
		score=self._benefit_mean/(self._std_dev_day_buy+1)
		self._set_score(score)