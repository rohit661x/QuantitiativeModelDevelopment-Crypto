import pandas as pd
import numpy as np

def calculate_z_score(series, window=20):
    """
    Calculates the rolling Z-score of a series.
    """
    mean = series.rolling(window=window).mean()
    std = series.rolling(window=window).std()
    z_score = (series - mean) / std
    return z_score

def calculate_returns(series):
    """
    Calculates log returns of a series.
    """
    return np.log(series / series.shift(1))

def calculate_volatility(returns, window=20):
    """
    Calculates rolling volatility (standard deviation of returns).
    """
    return returns.rolling(window=window).std()

def calculate_rsi(series, window=14):
    """
    Calculates Relative Strength Index (RSI).
    """
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi
