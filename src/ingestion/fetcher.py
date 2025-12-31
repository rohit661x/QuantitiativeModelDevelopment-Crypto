import ccxt
import pandas as pd
import os
import time

class CryptoDataFetcher:
    def __init__(self, exchange_id='binance', timeframe='1h'):
        self.exchange_id = exchange_id
        self.timeframe = timeframe
        self.exchange = getattr(ccxt, exchange_id)()
        
    def fetch_ohlcv(self, symbol, limit=1000):
        """
        Fetches OHLCV data for a given symbol.
        """
        print(f"Fetching {limit} candles for {symbol} from {self.exchange_id} ({self.timeframe})...")
        try:
            ohlcv = self.exchange.fetch_ohlcv(symbol, self.timeframe, limit=limit)
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            return df
        except Exception as e:
            print(f"Error fetching data: {e}")
            return None

    def save_to_csv(self, df, symbol, data_dir='data'):
        """
        Saves the DataFrame to a CSV file.
        """
        if df is None:
            return
            
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
            
        # Clean symbol name for filename (e.g., BTC/USDT -> BTC_USDT)
        filename = f"{symbol.replace('/', '_')}_{self.exchange_id}_{self.timeframe}.csv"
        filepath = os.path.join(data_dir, filename)
        
        df.to_csv(filepath, index=False)
        print(f"Data saved to {filepath}")

if __name__ == "__main__":
    # Example usage
    fetcher = CryptoDataFetcher(exchange_id='binance', timeframe='1h')
    symbol = 'BTC/USDT'
    df = fetcher.fetch_ohlcv(symbol, limit=1000)
    fetcher.save_to_csv(df, symbol)
