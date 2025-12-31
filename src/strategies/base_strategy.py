from abc import ABC, abstractmethod
import pandas as pd
import numpy as np

class BaseStrategy(ABC):
    def __init__(self, name):
        self.name = name

    @abstractmethod
    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Takes a DataFrame with OHLCV data and returns a DataFrame with signals.
        Signals should be 1 (buy), -1 (sell), or 0 (hold).
        """
        pass

    def run_backtest(self, df: pd.DataFrame, initial_capital=10000.0):
        """
        Simple vectorized backtest.
        Assumes we trade at the 'close' price of the signal candle (simplification)
        or the 'open' of the next.
        """
        # This is a placeholder for a real backtester.
        # For rapid iteration, we might just look at signal returns.
        pass
