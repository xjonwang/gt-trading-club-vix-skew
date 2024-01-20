import requests
import pandas as pd
import numpy as np
import datetime as dt
from enum import Enum


class Security(Enum):
    OPTION = 'option'
    EQUITY = 'stock'

    
class Req(Enum):
    TRADE = 'trade'
    QUOTE = 'quote'
    OI = 'open_interest'


class Right(Enum):
    CALL = 'C'
    PUT = 'P'


class ThetaDataAPI:
    def __init__(self):
        self.base_url = 'http://127.0.0.1:25510/'

    def _get_req(self, url: str, headers: dict, params: dict=None):
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Request failed with status code {response.status_code}")
            print(response.text)

    def get_roots(self, security_type: Security=Security.OPTION):
        url = f'{self.base_url}list/roots?sec={security_type.value}'
        headers = {'Accept': 'application/json'}
        return self._get_req(url=url, headers=headers)

    def get_expirations(self, root:str):
        url = f'{self.base_url}list/expirations?root={root}'
        headers = {'Accept': 'application/json'}
        return self._get_req(url=url, headers=headers)
    
    def get_strikes(self, root: str, exp: str):
        url = f'{self.base_url}list/strikes?root={root}&exp={exp}'
        headers = {'Accept': 'application/json'}
        return self._get_req(url=url, headers=headers)
    
    def get_dates(self, root: str, security_type: Security=Security.OPTION, exp: str=None, strike_right: tuple[str, Right]=None):
        url = f'{self.base_url}list/dates/{security_type.value}/quote'
        url_params = {}
        url_params["root"] = root
        if exp is not None:
            url_params["exp"] = exp
        if strike_right is not None:
            url_params["strike"] = strike_right[0]
            url_params["right"] = strike_right[1].value
        headers = {'Accept': 'application/json'}
        return self._get_req(url=url, headers=headers, params=url_params)
    
    """
    NOTE this function has a 750ms overhead 
    """
    def get_contracts(self, date: str, req: Req=Req.TRADE):
        url = f'{self.base_url}list/contracts/option/{req.value}?start_date={date}'
        headers = {'Accept': 'application/json'}
        return self._get_req(url=url, headers=headers)
        
    def get_eod_prices(self, root: str, security_type: Security, start_date: str, end_date: str, exp: str=None, strike: str=None, right: Right=None):
        url = None
        if security_type == Security.EQUITY:
            url = f'{self.base_url}hist/{security_type.value}/eod?root={root}&start_date={start_date}&end_date={end_date}'
        elif security_type == Security.OPTION:
            url = f'{self.base_url}hist/{security_type.value}/eod?root={root}&start_date={start_date}&end_date={end_date}&strike={strike}&exp={exp}&right={right.value}'
        headers = {'Accept': 'application/json'}
        print(url)
        return self._get_req(url=url, headers=headers)

    def get_hist_quotes(self, root: str, start_date: str, end_date: str, exp: str, strike: str, right: Right, ivl: str=None):
        url = f'{self.base_url}hist/option/quote?root={root}&start_date={start_date}&end_date={end_date}&strike={strike}&exp={exp}&right={right.value}&ivl={0 if ivl is None else ivl}'
        headers = {'Accept': 'application/json'}
        return self._get_req(url=url, headers=headers)

    def get_ohlc(self, root: str, start_date: str, end_date: str, exp: str, strike: str, right: Right, ivl: str):
        url = f'{self.base_url}hist/option/ohlc?root={root}&start_date={start_date}&end_date={end_date}&strike={strike}&exp={exp}&right={right.value}&ivl={ivl}'
        headers = {'Accept': 'application/json'}
        return self._get_req(url=url, headers=headers)
    
    def get_hist_oi(self, root: str, start_date: str, end_date: str, exp: str, strike: str, right: Right, ivl: str):
        url = f'{self.base_url}hist/option/open_interest?root={root}&start_date={start_date}&end_date={end_date}&strike={strike}&exp={exp}&right={right.value}&ivl={ivl}'
        headers = {'Accept': 'application/json'}
        return self._get_req(url=url, headers=headers)
    
    def get_hist_trades(self, root: str, start_date: str, end_date: str, exp: str, strike: str, right: Right):
        url = f'{self.base_url}hist/option/trade?root={root}&start_date={start_date}&end_date={end_date}&strike={strike}&exp={exp}&right={right.value}'
        headers = {'Accept': 'application/json'}
        return self._get_req(url=url, headers=headers)
    
    def get_hist_iv(self, root: str, start_date: str, end_date: str, exp: str, strike: str, right: Right, ivl: str):
        url = f'{self.base_url}hist/option/implied_volatility?root={root}&start_date={start_date}&end_date={end_date}&strike={strike}&exp={exp}&right={right.value}&ivl={ivl}'
        headers = {'Accept': 'application/json'}
        return self._get_req(url=url, headers=headers)
    
    def get_hist_iv_verbose(self, root: str, start_date: str, end_date: str, exp: str, strike: str, right: Right, ivl: str):
        url = f'{self.base_url}hist/option/implied_volatility_verbose?root={root}&start_date={start_date}&end_date={end_date}&strike={strike}&exp={exp}&right={right.value}&ivl={ivl}'
        headers = {'Accept': 'application/json'}
        return self._get_req(url=url, headers=headers)
    
    def get_eod_greeks(self, root: str, exp: str, start_date: str, end_date: str):
        url = f'{self.base_url}bulk_hist/option/eod_trade_greeks?root={root}&exp={exp}&start_date={start_date}&end_date={end_date}'
        headers = {'Accept': 'application/json'}
        return self._get_req(url=url, headers=headers)