import yfinance as yf
from datetime import timedelta
from datetime import datetime
import time

def get_price_value(tck):
    try:
        td=datetime.now()
        msft = yf.Ticker(tck)
        today = msft.info
        ret= today["ask"]
        print tck+"="+str(ret)
        return ret
    except Exception as e:
        print print tck+"=download error"
        return -1

class StockMeas:
    def __init__(self,tck):
        self._buy_price=0
        self._n_ticks=0
        self._tck=tck
        self._prev_prices=[-1,-1,-1,-1,-1,-1,-1]
        self._idx=0

    def _get_deriv(self):
        deriv=[]
        i=self._idx
        off=(i-1)%len(self._prev_prices)
        while(off!=self._idx):
            diff=self._prev_prices[i]-self._prev_prices[off]
            deriv.append(diff)
            i=off
            off=(i-1)%len(self._prev_prices)
        deriv.reverse()
        return deriv

    def _sell_check(self):
        state_init=0
        state_up=1
        state_down=2
        state_fail=3

        pc=self._prev_prices[self._idx]

        deriv=self._get_deriv()
        state=state_down
        print "---"
        for k in deriv:
            print k
            if(state==state_init):
                if k<0:
                    state=state_fail
                elif k>0:
                    state=state_up
                    
            if(state==state_up):
                if(k<=0):
                    state=state_down
        if(state==state_down):
            print "sell at %f"%pc
        print "\n"


    def _buy_check(self):
        state_init=0
        state_down=1
        state_zero=2
        state_fail=3

        pc=self._prev_prices[self._idx]

        deriv=self._get_deriv()
        state=state_down
        print "---"
        for k in deriv:
            print k
            if(state==state_init):
                if k<0:
                    state=state_down
                else:
                    state=state_fail
            if(state==state_down):
                if(k>=0):
                    state=state_zero
        if(state==state_zero):
            print "buy at %f"%pc
            self._buy_price=pc
            self._tck=int(500/pc)
        print "\n"

    def update_tck(self):
        pc=get_price_value(self._tck)
        if(pc==-1):
            return
        self._prev_prices[self._idx]=pc

        if(-1 in self._prev_prices):
            pass
        elif(self._buy_price>0):
            self._sell_check()
        else:
            self._buy_check()

        self._idx=(self._idx+1)%len(self._prev_prices)

if __name__ == '__main__':
    list_st=[StockMeas('TSLA')]
    while True:
        #try:
        for k in list_st:
            k.update_tck()
        time.sleep(60)
        #except Exception as e:
        #    print e
        #    break