import numpy as np
from scipy.stats import norm

def black_scholes_call(S: float, K, sigma, t: float, r: float):
    """
    S: spot price of the underlying asset
    K: strike price of the option
    T: time to expiration (in years)
    r: risk-free interest rate (annual rate, expressed in terms of continuous compounding)
    sigma: volatility of the underlying asset (annual standard deviation of the asset's returns)
    """
    with np.errstate(divide='ignore'):
        d1 = np.divide(1, sigma * np.sqrt(t)) * (np.log(S/K) + (r+sigma**2 / 2) * t)
        d2 = d1 - sigma * np.sqrt(t)
    return np.multiply(norm.cdf(d1),S) - np.multiply(norm.cdf(d2), K * np.exp(-r * t))

def black_scholes_put(S: float, K, sigma, t: float, r: float):
    """
    S: spot price of the underlying asset
    K: strike price of the option
    T: time to expiration (in years)
    r: risk-free interest rate (annual rate, expressed in terms of continuous compounding)
    sigma: volatility of the underlying asset (annual standard deviation of the asset's returns)
    """
    with np.errstate(divide='ignore'):
        d1 = np.divide(1, sigma * np.sqrt(t)) * (np.log(S/K) + (r+sigma**2 / 2) * t)
        d2 = d1 - sigma * np.sqrt(t)
    return np.multiply(norm.cdf(-d2), K * np.exp(-r * t)) - np.multiply(norm.cdf(-d1),S) 

def call_vega(S, K, sigma, t=0, r=0):
    with np.errstate(divide='ignore'):
        d1 = np.divide(1, sigma * np.sqrt(t)) * (np.log(S/K) + (r+sigma**2 / 2) * t)
    return np.multiply(S, norm.pdf(d1)) * np.sqrt(t)

def bs_iv(price, S, K, t=0, r=0, precision=1e-4, initial_guess=0.2, max_iter=1000, verbose=False):
    iv = initial_guess
    for _ in range(max_iter):
        P = black_scholes_call(S, K, iv, t, r)
        diff = price - P
        if abs(diff) < precision:
            return iv
        grad = call_vega(S, K, iv, t, r)
        iv += diff/grad     
    if verbose:
        print(f"Did not converge after {max_iter} iterations")
    return iv 

def bs_iv_bulk(prices, strikes, S, t=0, r=0):
    num_contracts = len(strikes)
    iv = [None] * num_contracts
    for i in range(num_contracts):
        iv[i] = bs_iv(price=prices[i], K=strikes[i], S=S, t=t, r=r, max_iter=500)
    return iv