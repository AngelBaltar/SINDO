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

	def fill_from_csv_line(self,csv_line):
		params=csv_line.split(';')
		self._dt=datetime.strptime(params[0],"%Y-%m-%d %H:%M:%S")
		self._op=float(params[1].replace(',','.'))
		self._cls=float(params[2].replace(',','.'))
		self._div=(int(params[3])==1)

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

	def to_csv(self):
		dt=str(self.get_date())
		o=str(self.get_open()).replace('.',',')
		c=str(self.get_close()).replace('.',',')
		d='1' if self.is_dividend() else '0'
		return "%s;%s;%s;%s\n"%(dt,o,c,d)

class StockHistoricMeasure(object):

	def __init__(self,date_start,date_end,idx):
		self._date_start=date_start
		self._date_end=date_end
		self._idx=idx
		self._st_datas=[]

	def __init__(self,idx,datas):
		self._st_datas=datas
		self.sort()
		self._date_start=self._st_datas[0].get_date()
		self._date_end=self._st_datas[-1].get_date()
		self._idx=idx
		

	@classmethod
	def get_csv_str(self):
		return "index;Date start;Date end"

	def __str__(self):
		return "%s;%s;%s"%(self._idx,str(self._date_start),str(self._date_end))

	def get_start_date(self):
		return self._date_start

	def get_end_date(self):
		return self._date_end

	def get_idx(self):
		return self._idx

	def sort(self):
		self._st_datas.sort(key=lambda s:s.get_date())

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

	def __add__(self,o):
		if(not o):
			return self
		if(self.get_idx()!=o.get_idx()):
			raise Exception("Adding %s with %s"%(self.get_idx(),o.get_idx()))
		return StockHistoricMeasure(self.get_idx(),self._st_datas+o._st_datas)

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
			time.sleep(0.2)
			hist = msft.history(period=per)

		for i in range(0,len(hist['Open'])):
			dt=datetime.strptime(str(hist.axes[0][i]), "%Y-%m-%d %H:%M:%S")
			stock=StockDaykMeasure(self._idx,dt,hist['Open'][i],hist['Close'][i],(hist['Dividends'][i]!=0.0))
			self._st_datas.append(stock)
			#print stock

	def print_to_csv(self,f_out):
		f_out.write("Date;Open;Close;Dividend\n")
		for k in self:
			f_out.write("%s"%(k.to_csv()))
