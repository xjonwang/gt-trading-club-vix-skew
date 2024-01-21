import yfinance as yf
from pandas_datareader import data as pdr
yf.pdr_override()
import datetime as dt
import numpy as np
import math
from scipy.stats import gaussian_kde
from scipy.integrate import quad

from ThetaDataClient import Right

class Model:
    def __init__(self, root: str, start_date: dt.date):
        """
        Initializes KDE model for options pricing

        Arguments:
        root: ticker for security
        start_date: lookback period for model
        """
        price = pdr.get_data_yahoo([root], start_date, dt.date.today())['Adj Close']
        daily_returns = np.log(price/price.shift(1))
        self.kde = self.generate_kde(daily_returns)

    def generate_kde(self, data):
        min_return = data.min()
        max_return = data.max()
        kde = gaussian_kde(data.dropna())
        xrange = np.linspace(2*min_return, 2*max_return, data.size - 1)
        return kde
    
    def call_pdf_creator(self, strike: float, spot: float):
        def pdf(x):
            return self.kde.evaluate(x) * max(0, spot * math.exp(x) - strike)
        return pdf
    
    def put_pdf_creator(self, strike: float, spot: float):
        def pdf(x):
            return self.kde.evaluate(x) * max(0, strike - spot * math.exp(x))
        return pdf
    
    def call_theo(self, strike: float, spot: float) -> float:
        pdf = self.call_pdf_creator(strike=strike, spot=spot)
        result, error = quad(pdf, -2, 2)
        if error > 1e-3:
            print(f"WARNING (call): error on integration > 1e-3 = {error}")
        return result
    
    def put_theo(self, strike: float, spot: float):
        pdf = self.put_pdf_creator(strike=strike, spot=spot)
        result, error = quad(pdf, -2, 2)
        if error > 1e-3:
            print(f"WARNING (put): error on integration {error} > 1e-3")
        return result

    # returns 1 for long, 0 for no signal, -1 for short
    def signal(self, strike: float, spot: float, bid: float, ask: float, right: Right):
        """
        Run the model to determine if there's a signal.

        Returns:
        +1 for long
        0 for no signal
        -1 for short
        """
        print(f"strike: {strike}, spot: {spot}")
        if right == Right.CALL:
            theo = self.call_theo(strike=strike, spot=spot)
            return int(theo > ask) - int(theo < bid)
        else:
            theo = self.put_theo(strike=strike, spot=spot)
            return int(theo > ask) - int(theo < bid)