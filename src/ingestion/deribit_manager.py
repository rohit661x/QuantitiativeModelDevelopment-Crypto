import asyncio
import websockets
import json
import aiohttp
import time
import sys

# Increase recursion depth just in case for deep recursions in complex json (rare but safe)
sys.setrecursionlimit(2000)

class DeribitManager:
    def __init__(self, currency='BTC', callback=None):
        self.currency = currency
        self.callback = callback
        self.ws_url = "wss://www.deribit.com/ws/api/v2"
        self.rest_url = "https://www.deribit.com/api/v2"
        self.instruments = []
        self.active_channels = []

    async def fetch_instruments(self):
        """
        Fetch all active option instruments and sort by creation timestamp (proxy for relevance) 
        or we just take a random grab.
        Actually, we can't see volume in 'get_instruments'.
        We'll just create a helper to find a known active expiry.
        """
        async with aiohttp.ClientSession() as session:
            url = f"{self.rest_url}/public/get_instruments?currency={self.currency}&kind=option&expired=false"
            print(f"Fetching instruments from {url}...")
            async with session.get(url) as resp:
                data = await resp.json()
                if 'result' in data:
                    all_inst = data['result']
                    # Sort by creation_timestamp to get newer ones, or just name
                    # Let's try to get a 'near' expiry.
                    # e.g. BTC-29DEC...
                    # We will just take the first 50 to be safe.
                    self.instruments = [i['instrument_name'] for i in all_inst]
                    print(f"Found {len(self.instruments)} active options for {self.currency}.")
                else:
                    print("Error fetching instruments.")

    async def start_stream(self):
        if not self.instruments:
            await self.fetch_instruments()

        # DEBUG: Subscribe to the BTC Index (which always ticks) to prove connection
        # Then subscribe to a few options
        subset = self.instruments[:50]
        chunk_size = 50
        
        async with websockets.connect(self.ws_url) as ws:
            print("Connected to Deribit WebSocket.")
            
            # 1. Subscribe to Index (Heartbeat)
            await ws.send(json.dumps({
                "jsonrpc": "2.0",
                "id": 9999,
                "method": "public/subscribe",
                "params": {"channels": ["deribit_price_index.btc_usd"]}
            }))
            
            # Subscribe loop
            print(f"Subscribing to {len(subset)} option channels...")
            for i in range(0, len(subset), chunk_size):
                chunk = subset[i:i+chunk_size]
                channels = [f"ticker.{name}.100ms" for name in chunk]
                
                msg = {
                    "jsonrpc": "2.0",
                    "id": i,
                    "method": "public/subscribe",
                    "params": {"channels": channels}
                }
                await ws.send(json.dumps(msg))
                await asyncio.sleep(0.02) # Rate limit protection

            print(f"Successfully subscribed to {len(subset)} instruments.")

            print("Subscribed to all channels.")

            # Listen loop
            while True:
                try:
                    msg = await ws.recv()
                    # print(f"RAW: {msg}") 
                    data = json.loads(msg)
                    
                    # DEBUG: Print everything that is NOT a ticker to see errors/confirmations
                    if 'params' not in data:
                        # Likely a response to subscribe
                        # print(f"System Msg: {data}")
                        pass

                    if 'params' in data and 'data' in data['params']:
                        # This is a ticker update
                        tick = data['params']['data']
                        if self.callback:
                            await self.callback(tick)
                    elif 'error' in data:
                        print(f"API Error: {data['error']}")
                            
                except Exception as e:
                    print(f"WS Error: {e}")
                    break

if __name__ == "__main__":
    async def handler(tick):
        # Stub handler for testing
        print(f"[{tick.get('instrument_name')}] Price: {tick.get('mark_price')}")

    manager = DeribitManager()
    try:
        print("Starting Deribit Manager Test...")
        asyncio.run(manager.start_stream())
    except KeyboardInterrupt:
        print("Test Stopped.")
