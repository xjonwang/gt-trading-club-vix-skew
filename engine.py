import yfinance as yf
from pandas_datareader import data as pdr
yf.pdr_override()
import datetime as dt

from ThetaDataClient import Right
class Engine:
    def __init__(self, root: str, start_date: dt.date):
        self.pnl = 0
        self.spot_price = pdr.get_data_yahoo([root], start_date, dt.date.today())['Adj Close']

    def pnl_option_to_expiry(self, entry: float, strike: float, exp: dt.date, right: Right, direction: int):
        self.pnl += direction * (max((right==Right.CALL - right==Right.PUT)*(self.spot_price[exp.strftime("%Y-%m-%d")] - strike), 0) - entry) 