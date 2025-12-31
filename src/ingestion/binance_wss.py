import asyncio
import websockets
import json
import time

class BinanceStreamer:
    def __init__(self, symbols, callback):
        """
        symbols: list of trading pairs, e.g., ['btcusdt', 'ethusdt']
        callback: async function to call with new data
        """
        self.symbols = [s.lower() for s in symbols]
        self.callback = callback
        # Construct stream URL for multiple streams
        # Format: <symbol>@bookTicker
        streams = '/'.join([f"{s}@bookTicker" for s in self.symbols])
        self.url = f"wss://fstream.binance.com/stream?streams={streams}"
        self.running = False

    async def start(self):
        self.running = True
        print(f"Connecting to {self.url}...")
        async with websockets.connect(self.url) as ws:
            print("Connected to Binance Future Stream!")
            while self.running:
                try:
                    msg = await ws.recv()
                    data = json.loads(msg)
                    # Payload structure: {'stream': 'btcusdt@bookTicker', 'data': {...}}
                    if 'data' in data:
                        # Add receive timestamp for latency tracking
                        data['data']['rcv_time'] = time.time() * 1000 
                        await self.callback(data['data'])
                except Exception as e:
                    print(f"WebSocket Error: {e}")
                    break
    
    def stop(self):
        self.running = False

if __name__ == "__main__":
    # Test stub
    async def handler(msg):
        # Calculate latency: Binance 'T' is transaction time, 'E' is event time.
        # rcv_time is our local time.
        # Note: clocks might not be synced, so 'E' vs 'rcv_time' is rough estimate.
        latency = msg['rcv_time'] - msg['E']
        print(f"[{msg['s']}] Bid: {msg['b']} Ask: {msg['a']} | Latency: {latency:.2f}ms")

    streamer = BinanceStreamer(symbols=['btcusdt'], callback=handler)
    
    try:
        asyncio.run(streamer.start())
    except KeyboardInterrupt:
        print("Stopping...")
