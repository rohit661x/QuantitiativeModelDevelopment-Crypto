from numba import jit
import numpy as np

@jit(nopython=True)
def update_incremental_sma(new_price, old_prices, current_sums, windows):
    """
    Updates SMA running sums for many windows in parallel.
    new_price: float
    old_prices: array of floats (prices falling out of window for each model)
    current_sums: array of floats (current running sums)
    windows: array of ints (window sizes)
    """
    n = len(windows)
    smas = np.zeros(n)
    
    for i in range(n):
        # Update sum: add new, subtract old
        current_sums[i] = current_sums[i] + new_price - old_prices[i]
        smas[i] = current_sums[i] / windows[i]
        
    return smas, current_sums

@jit(nopython=True)
def check_signals(smas, current_price, lower_bands, upper_bands):
    """
    Example logic: Buy if price < lower_band (mean reversion)
    """
    n = len(smas)
    signals = np.zeros(n) # 1: Buy, -1: Sell, 0: Hold
    
    for i in range(n):
        if current_price < lower_bands[i]:
            signals[i] = 1
        elif current_price > upper_bands[i]:
            signals[i] = -1
            
    return signals
