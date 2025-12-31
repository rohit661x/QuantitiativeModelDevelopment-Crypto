import asyncio
import numpy as np
import time
from ingestion.binance_wss import BinanceStreamer
import math_lib

class IncrementalEngine:
    def __init__(self, symbols):
        self.symbols = symbols
        self.num_models = 1000
        
        # Models: 1000 SMAs with windows [10...1009]
        self.windows = np.arange(10, 10 + self.num_models).astype(np.int64)
        
        # State
        self.sums = np.zeros(self.num_models, dtype=np.float64)
        
        # History Buffer
        # In production, use a fixed-size RingBuffer (numpy) to avoid memory leaks.
        # Here we use a list but clear it periodically or cap it for prototype safety.
        self.max_window = self.windows.max()
        self.prices = [] 
        
        self.tick_count = 0
        self.start_time = time.time()

    async def on_tick(self, data):
        symbol = data['s']
        mid = (float(data['b']) + float(data['a'])) / 2.0
        
        # 1. Update History
        self.prices.append(mid)
        current_idx = len(self.prices) - 1
        
        # Need enough history
        if current_idx < self.max_window:
            # Just accumulate sums for initialization
            self.sums += mid
            return

        # 2. Get "Old Prices" that are falling out of each window
        # For window W, the price falling out is at index (current_idx - W)
        # We need a vector of old prices. 
        # This part is tricky in vectorization without a proper RingBuffer.
        # SLOW PATH for Prototype:
        old_prices = np.array([self.prices[current_idx - w] for w in self.windows])
        
        # 3. Fast Math (Numba)
        # s_new = s_old + p_new - p_old
        # sma = s_new / w
        self.sums = self.sums + mid - old_prices
        smas = self.sums / self.windows
        
        # 4. Log periodically
        self.tick_count += 1
        if self.tick_count % 50 == 0:
            elapsed = time.time() - self.start_time
            rate = self.tick_count / elapsed
            print(f"[{symbol}] Rate: {rate:.2f} ticks/s | Price: {mid:.2f} | Model 0 (SMA10): {smas[0]:.2f} | Model 999 (SMA1009): {smas[-1]:.2f}")

    async def start(self):
        streamer = BinanceStreamer(self.symbols, self.on_tick)
        print(f"Starting engine with {self.num_models} concurrent models...")
        await streamer.start()

if __name__ == "__main__":
    engine = IncrementalEngine(['btcusdt'])
    try:
        asyncio.run(engine.start())
    except KeyboardInterrupt:
        pass
