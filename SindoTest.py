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
	start_time = time.time()
	h=get_data(start_date,end_date,tck)
	#print("---%s %s seconds ---" %(tck,(time.time() - start_time)))
	if not h:
		return None
	kk=DividendAnalysis()
	kk.set_hist(h)
	kk.analyze()
	if(kk.get_score()>0):
		kk.get_hist().free_memory()
		return kk
	return None

class SindoTest(unittest.TestCase):

	def test_benefit(self):
		import following_stocks

		date_start=datetime.strptime("2017-01-01","%Y-%m-%d")
		date_end=datetime.strptime("2018-01-01","%Y-%m-%d")

		


		p = multiprocessing.Pool(max(multiprocessing.cpu_count(),2))

		
		#stock_list=['TXG','YI','PIH','PIHPP','TURN','FLWS','BCOW','FCCY','SRCE','VNET','TWOU',
		#'QFIN','JOBS','JFK','JFKKR','JFKKU','JFKKW','EGHT','JFU','AAON','ABEO','ABEOW','ABIL','ABMD']
		args_list=[[tck,date_start,date_end] for tck in stock_list]
		benefits_list=p.map(analize_for_test,args_list)
		p.close()
		p.join()

		perc_mean_benefit=0
		count=0
		for kk in benefits_list:
			try:
				h_fut=get_data(kk.get_date_buy()-timedelta(days=1),kk.get_date_sell()+timedelta(days=1),tck)
				real_benefit=h_fut[kk.get_date_sell()].get_close()-h_fut[kk.get_date_buy()].get_close()
				
				perc_benefit=real_benefit/h_fut[kk.get_date_buy()].get_close()
				td=kk.get_date_sell()-kk.get_date_buy()
				perc_benefit=perc_benefit*365/td.days
				count+=1
				perc_mean_benefit+=perc_benefit
				print "stock %s %f%% benefit"%(args_list[k][0],perc_benefit)
			except:
				pass

		if count>0:
			perc_mean_benefit/=count

		print "benefit mean %f"%perc_mean_benefit
		self.assertTrue(perc_mean_benefit>5,"benefit > 5")

if __name__ == '__main__':
    unittest.main()