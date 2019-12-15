import unittest
from SindoDatabase import *
from StockDataAnalysis import *
from StockMeasure import *
from all_index_nasdaq import *
from datetime import datetime

class SindoTest(unittest.TestCase):

	def test_benefit(self):
		import all_index_nasdaq
		time_now=datetime.now()
		time_now_past=time_now-timedelta(days=600)
		perc_mean_benefit=0
		count=0
		#stock_list=['AAPL','T']
		for tck in stock_list:
			h=get_data(time_now_past-timedelta(days=300),time_now_past,tck)
			if not h:
				continue
			kk=DividendAnalysis()
			kk.set_hist(h)
			kk.analyze()
			if(kk.get_score()>0):
				h_fut=get_data(kk.get_date_buy()-timedelta(days=1),kk.get_date_sell()+timedelta(days=1),tck)
				try:
					real_benefit=h_fut[kk.get_date_sell()].get_close()-h_fut[kk.get_date_buy()].get_close()
					
					perc_benefit=real_benefit/h_fut[kk.get_date_buy()].get_close()
					print "%s %f euros per stock benefit"%(tck,real_benefit)
					print "%s %f perc benefit"%(tck,perc_benefit)
					perc_mean_benefit+=perc_benefit
					count+=1
					self.assertTrue(perc_benefit>(kk.get_score()-10))
				except:
					pass

		perc_mean_benefit/=count
		print "perc_mean_benefit=%f"%perc_mean_benefit
		self.assertTrue(perc_mean_benefit>2)

if __name__ == '__main__':
    unittest.main()