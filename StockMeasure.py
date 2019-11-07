import yfinance as yf
from datetime import datetime

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
		self._st_datas=[]
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
		return k

	def __getitem__(self, index):
		for k in self:
			if k.get_date()==index:
				return k
			if(k.get_date()==str(index)):
				return k
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
			time.sleep(1)
			hist = msft.history(period=per)

		for i in range(0,len(hist['Open'])):
			dt=datetime.strptime(str(hist.axes[0][i]), "%Y-%m-%d %H:%M:%S")
			stock=StockDaykMeasure(self._idx,dt,hist['Open'][i],hist['Close'][i],(hist['Dividends'][i]!=0.0))
			self._st_datas.append(stock)
			#print stock
