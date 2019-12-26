import unittest
from SindoDatabase import *
from StockDataAnalysis import *
from StockMeasure import *
from all_index_nasdaq import *
from datetime import datetime,date
import multiprocessing


def analize_for_test(args):
	tck=args[0]
	start_date=args[1]
	end_date=args[2]
	h=get_data(start_date,end_date,tck)
	if not h:
		return 0
	kk=DividendAnalysis()
	kk.set_hist(h)
	kk.analyze()
	if(kk.get_score()>0):
		try:
			h_fut=get_data(kk.get_date_buy()-timedelta(days=1),kk.get_date_sell()+timedelta(days=1),tck)
			real_benefit=h_fut[kk.get_date_sell()].get_close()-h_fut[kk.get_date_buy()].get_close()
			
			perc_benefit=real_benefit/h_fut[kk.get_date_buy()].get_close()
			td=kk.get_date_sell()-kk.get_date_buy()
			perc_benefit=perc_benefit*365/td.days
			return perc_benefit
		except:
			return 0
	return 0

class SindoTest(unittest.TestCase):

	def test_benefit(self):
		import all_index_nasdaq

		today = date.today()
		time_now = datetime(
		    year=today.year, 
		    month=today.month,
		    day=today.day,
		)

		#print time_now
		time_now_past=time_now-timedelta(days=600)
		perc_mean_benefit=0
		count=0

		p = multiprocessing.Pool(max(multiprocessing.cpu_count()-1,2))

		
		stock_list=['AAPL','T']
		args_list=[[tck,time_now_past-timedelta(days=300),time_now_past] for tck in stock_list]
		benefits_list=p.map(analize_for_test,args_list)
		p.close()
		p.join()
		benefits_list.sort(reverse=True)
		for k in range(0,len(benefits_list)):
			benefit=benefits_list[k]
			if(benefit!=0):
				count+=1
				perc_mean_benefit+=benefit
				print "stock %s %f%% benefit"%(args_list[k][0],benefit)
		perc_mean_benefit/=count
		self.assertTrue(perc_mean_benefit>5,"benefit > 5")

if __name__ == '__main__':
    unittest.main()