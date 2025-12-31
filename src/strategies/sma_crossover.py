import pandas as pd
import numpy as np
from .base_strategy import BaseStrategy

class SMACrossover(BaseStrategy):
    def __init__(self, short_window=50, long_window=200):
        super().__init__("SMA Crossover")
        self.short_window = short_window
        self.long_window = long_window

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        """
        Returns a series of signals: 1 (long), 0 (neutral) based on SMA Crossover.
        Note: For simplicity, we are returning a position target (1 for long), not just trade executions.
        """
        signals = pd.DataFrame(index=df.index)
        signals['signal'] = 0.0

        signals['short_mavg'] = df['close'].rolling(window=self.short_window, min_periods=1, center=False).mean()
        signals['long_mavg'] = df['close'].rolling(window=self.long_window, min_periods=1, center=False).mean()

        # Create signal: 1 when short > long, 0 otherwise
        signals['signal'][self.short_window:] = np.where(signals['short_mavg'][self.short_window:] > signals['long_mavg'][self.short_window:], 1.0, 0.0)
        
        # If we wanted shorts, we could use -1.0
        
        return signals['signal']
