import numpy as np
from datetime import datetime as dt

from ThetaDataClient import ThetaDataAPI, Security, Right

class WrapperClient:
    def __init__(self):
        self.thetadata = ThetaDataAPI()
        self.date_format = "%Y%m%d"

    def get_dates_in_range(self, root: str, exp: str, start_date: str, end_date: str):
        dates = self.thetadata.get_dates(root=root, exp=exp)["response"]
        start = start_date if start_date is not None else dates[0]
        end = end_date if end_date is not None else dates[len(dates)-1]
        start_datetime = dt.strptime(str(start), self.date_format)
        end_datetime = dt.strptime(str(end), self.date_format)
        dates = [date for date in dates if start_datetime <= dt.strptime(str(date), self.date_format) <= end_datetime]
        return (start, end, dates)
    
    def get_underlying_over_time(self, root: str, security_type: Security, points, dates: list[str]):
        num_days = len(dates)
        prices = {}
        for point in points:
            prices[point] = [None] * num_days
        data_points = {}
        for i in range(num_days):
            eod_prices = self.thetadata.get_eod_prices(root=root, security_type=security_type, start_date=dates[i], end_date=dates[i])
            header = eod_prices["header"]
            response = eod_prices["response"]
            if not data_points:
                for point in points:
                    data_points[point] = header["format"].index(point)
            for point, index in data_points.items():
                prices[point][i] = response[0][index]
        return prices

    def get_chains_over_time(self, root: str, exp: str, right: Right, points: list[str], start_date: str=None, end_date: str=None):
        start, end, dates = self.get_dates_in_range(root=root, exp=exp, start_date=start_date, end_date=end_date)
        num_days = len(dates)
        strikes = self.thetadata.get_strikes(root=root, exp=exp)["response"]
        num_strikes = len(strikes)
        data = {}
        for point in points:
            data[point] = []
        data_points = {}
        valid_strikes = []
        for i in range(num_strikes):
            eod_prices = self.thetadata.get_hist_quotes(root=root, start_date=start, end_date=end, exp=exp, strike=strikes[i], right=right)
            header = eod_prices["header"]
            if header["error_type"] != "null":
                continue
            response = eod_prices["response"]
            if len(response) > num_days or len(response) < num_days:
                if len(response) > num_days:
                    print(response)
                continue
            valid_strikes.append(strikes[i])
            if not data_points:
                for point in points:
                    data_points[point] = header["format"].index(point)
            for point, index in data_points.items():
                data[point].append([d[index] for d in response])
        for point in points:
            data[point] = np.column_stack(data[point])
        print(data)
        return (dates, valid_strikes, data)


    # Need to address blanks in data
    def get_greeks_chains_over_time(self, root: str, exp: str, points: list[str], start_date: str=None, end_date: str=None):
        start, end, dates = self.get_dates_in_range(root=root, exp=exp, start_date=start_date, end_date=end_date)
        num_days = len(dates)
        eod_greeks = cached_eod_greeks #self.thetadata.get_eod_greeks(root=root, start_date=start, end_date=end, exp=exp)
        header = eod_greeks["header"]
        response = eod_greeks["response"]
        data_points = {}
        calls = {}
        puts = {}
        for point in points:
            data_points[point] = header["format"].index(point)
            calls[point] = {}
            puts[point] = {}
        for eod in response:
            contract = eod["contract"]
            ticks = eod["ticks"]
            for point, index in data_points.items():
                (calls if contract["right"] == "C" else puts)[point][contract["strike"]] = [d[index] for d in ticks]
        for point in points:
            print(list(calls[point].values()))
            # calls[point] = {k: v for k, v in calls[point].items() if len(v)==num_days}
            # calls[point] = (calls[point].keys(), np.column_stack(list(calls[point].values())))
        return (calls, puts)
