import pandas as pd
from scipy.interpolate import interp1d
from scipy.ndimage import gaussian_filter1d
import matplotlib.pyplot as plt
from black_scholes import *

def pdf2(Krange, S, vol_surface: interp1d, t=0, r=0):
    Crange = black_scholes_call(S, Krange, vol_surface(Krange), t, r)
    first_deriv = np.gradient(Crange, Krange, edge_order=0)
    second_deriv = np.gradient(first_deriv, Krange, edge_order=0)
    return np.exp(r * t) * second_deriv

def pdf_from_IV(strikes, vols, S, t, r):
    """
    Interpolates vol then breeden-litzenberger to find option implied distribution.
    NOTE we interpolate vol and NOT price because interpolating in price space can lead to arbitrages.
    """
    vol_surface = interp1d(strikes, vols, kind="cubic", fill_value="extrapolate")
    strike_range = np.arange(strikes.min(), strikes.max(), 0.1)
    plot_vol_smile(strikes, vols, strike_range, vol_surface, S)
    return (strike_range, pdf2(Krange=strike_range, S=S, vol_surface=vol_surface, t=t, r=r), black_scholes_call(S, strike_range, vol_surface(strike_range), t, r))

def plot_vols(strikes, vols, S):
    plt.plot(strikes, vols, "bx")
    plt.axvline(S, color="k", linestyle="--")
    plt.legend(["smoothed IV"], loc="best")
    plt.xlabel("Strike")
    plt.ylabel("IV")
    plt.tight_layout()
    plt.show()

def plot_vol_smile(strikes, vols, Krange, vol_surface, S):
    plt.plot(strikes, vols, "bx", Krange, vol_surface(Krange), "k-")
    plt.axvline(S, color="k", linestyle="--")
    plt.legend(["smoothed IV", "fitted smile"], loc="best")
    plt.xlabel("Strike")
    plt.ylabel("IV")
    plt.tight_layout()
    plt.show()

def plot_pdf_and_prices(Krange, prices, pdf, S):
    print(pdf)
    fig, ax1 = plt.subplots(figsize=(9,6))
    col="blue"
    ax1.set_xlabel('Strike')
    ax1.set_ylabel('Call price', color=col)
    ax1.plot(Krange, prices, color=col)
    ax1.tick_params(axis='y', labelcolor=col)
    ax1.axvline(S, color="k", linestyle="--")
    ax2 = ax1.twinx()
    col="red"
    ax2.set_ylabel('f(K)', color=col)
    ax2.plot(Krange, pdf, color=col)
    ax2.tick_params(axis='y', labelcolor=col)
    fig.tight_layout()
    plt.show()
    

if __name__ == "__main__":
    # for testing to match with source
    calls = pd.read_excel("SPY_191020exp_290920.xlsx", sheet_name="call")
    calls["midprice"] = (calls.bid + calls.ask)/2
    calls = calls[calls.midprice > 0]
    calls["iv"] = calls.apply(lambda row: bs_iv(row.midprice, 332, row.strike, 3/52, max_iter=500), axis=1)
    calls = calls.dropna()
    calls.iv = gaussian_filter1d(calls.iv, 3)
    calls = calls[(calls.strike > 300) & (calls.strike < 375)]

    Krange, pdf, prices = pdf_from_IV(calls.strike, calls.iv, S = 332, t = 3/52, r = 0)

    plot_pdf_and_prices(Krange, prices, pdf, 332)
    
