import pandas as pd
import numpy as np
import os
import sys

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from ingestion.fetcher import CryptoDataFetcher
from strategies.sma_crossover import SMACrossover
from backtest.simple_backtester import VectorBacktester

def main():
    symbol = 'BTC/USDT'
    exchange = 'binance'
    timeframe = '1h'
    
    # 1. Fetch Data (Load from CSV if exists, else fetch)
    csv_path = f"data/{symbol.replace('/', '_')}_{exchange}_{timeframe}.csv"
    if os.path.exists(csv_path):
        print(f"Loading data from {csv_path}...")
        df = pd.read_csv(csv_path)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
    else:
        print("Fetching new data...")
        fetcher = CryptoDataFetcher(exchange_id=exchange, timeframe=timeframe)
        df = fetcher.fetch_ohlcv(symbol, limit=2000)
        fetcher.save_to_csv(df, symbol)

    # 2. Define Strategy
    strategy = SMACrossover(short_window=20, long_window=50)
    
    # 3. Generate Signals
    print("Generating signals...")
    # Need to import numpy in simple_backtester as well if not already good
    signals = strategy.generate_signals(df)
    
    # 4. Run Backtest
    print("Running backtest...")
    backtester = VectorBacktester(signals, df['close'], initial_capital=10000.0)
    results = backtester.run()
    
    # 5. Show Results
    summary = backtester.summary(results)
    print("\n--- Backtest Summary ---")
    for k, v in summary.items():
        print(f"{k}: {v}")
        
    print(f"\nLast Signal: {signals.iloc[-1]}")

if __name__ == "__main__":
    main()
