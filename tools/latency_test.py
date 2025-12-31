import asyncio
import time
import numpy as np
from src.ingestion.binance_wss import BinanceStreamer
import sys

latencies = []

async def measure_latency(msg):
    # Binance Event Time (E) is in ms
    # Local Time is in sec
    # We use local receive time captured in binance_wss to be consistent
    # But binance_wss calculates rcv_time = time.time() * 1000
    
    event_time = msg['E']
    rcv_time = msg['rcv_time']
    
    # Simple clock skew check? 
    # If local clock is behind, latency could be negative. 
    # We are looking for "Network + Processing" delay relative to when Binance stamped it.
    
    latency = rcv_time - event_time
    latencies.append(latency)
    
    print(f"Tick: {len(latencies)} | Latency: {latency:.2f}ms")
    
    if len(latencies) >= 100:
        print("\n--- Latency Report (100 Ticks) ---")
        print(f"Min: {np.min(latencies):.2f} ms")
        print(f"Max: {np.max(latencies):.2f} ms")
        print(f"Avg: {np.mean(latencies):.2f} ms")
        print(f"Jitter (StdDev): {np.std(latencies):.2f} ms")
        sys.exit(0)

async def run():
    streamer = BinanceStreamer(['btcusdt'], measure_latency)
    print("Capturing 100 ticks for latency benchmark...")
    await streamer.start()

if __name__ == "__main__":
    try:
        asyncio.run(run())
    except SystemExit:
        pass
    except KeyboardInterrupt:
        pass
