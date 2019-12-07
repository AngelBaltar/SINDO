import unittest
from SindoDatabase import *
from StockDataAnalysis import *
from StockMeasure import *
from all_index_nasdaq import *
from datetime import datetime

class SindoTest(unittest.TestCase):
	def test_benefit(self):
		time_now=datetime.now()
		time_now_past=time_now-timedelta(days=600)
		print time_now_past
		h=get_data(time_now_past-timedelta(days=1200),time_now_past,'AAPL')
		kk=DividendAnalysis()
		print h
		kk.set_hist(h)
		kk.analyze()
		h_fut=get_data(time_now_past,datetime.now(),'AAPL')
		print kk.get_date_buy()
		print kk.get_date_sell()
		real_benefit=h_fut[kk.get_date_sell()].get_close()-h_fut[kk.get_date_buy()].get_close()
		perc_benefit=real_benefit/h_fut[kk.get_date_buy()].get_close()
		self.assertTrue(perc_benefit>(kk.get_score()-10))
		print perc_benefit

if __name__ == '__main__':
    unittest.main()