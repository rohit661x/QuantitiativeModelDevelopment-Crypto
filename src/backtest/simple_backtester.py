import pandas as pd
import numpy as np

class VectorBacktester:
    def __init__(self, signals, price, initial_capital=10000.0, fee_pct=0.001):
        """
        signals: Series of 1 (long), -1 (short), 0 (flat)
        price: Series of asset prices (e.g. Close)
        """
        self.signals = signals
        self.price = price
        self.initial_capital = initial_capital
        self.fee_pct = fee_pct

    def run(self):
        """
        Run the backtest.
        """
        # align signals and price
        df = pd.DataFrame({'price': self.price, 'signal': self.signals})
        df = df.dropna()
        
        # Calculate positions (1 for long, 0 for cash/neutral - assuming long-only for now or 1/-1 for long/short)
        # Assuming signal indicates target position
        df['position'] = df['signal'].shift(1) # enter on next candle's open/close (simplification: use current close)
        # Actually, usually you calculate signal at Close, and enter at Next Open.
        # Here we simplify: Signal at t, enters at t+1.
        
        df['returns'] = df['price'].pct_change()
        df['strategy_returns'] = df['position'] * df['returns']
        
        # Transaction costs
        df['trades'] = df['position'].diff().abs()
        df['fees'] = df['trades'] * self.fee_pct
        
        df['strategy_returns_net'] = df['strategy_returns'] - df['fees']
        
        df['cumulative_returns'] = (1 + df['strategy_returns_net']).cumprod()
        df['equity_curve'] = self.initial_capital * df['cumulative_returns']
        
        return df

    def summary(self, df):
        total_return = df['cumulative_returns'].iloc[-1] - 1
        sharpe = df['strategy_returns_net'].mean() / df['strategy_returns_net'].std() * np.sqrt(252*24) # assuming hourly
        max_drawdown = (df['cumulative_returns'] / df['cumulative_returns'].cummax() - 1).min()
        
        return {
            'Total Return': total_return,
            'Sharpe Ratio': sharpe,
            'Max Drawdown': max_drawdown,
            'Final Equity': df['equity_curve'].iloc[-1]
        }
