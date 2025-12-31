import asyncio
import time
import numpy as np
from collections import defaultdict
from ingestion.deribit_manager import DeribitManager

class OptionsHeatmapEngine:
    def __init__(self, currency='BTC'):
        """
        Initializes the Heatmap Engine.
        :param currency: The currency symbol to track (default: BTC).
        """
        self.manager = DeribitManager(currency, self.on_tick)
        
        # State Map: Strike -> Metrics
        self.strikes = defaultdict(lambda: {
            'call_oi': 0.0, 'put_oi': 0.0, 
            'call_gamma': 0.0, 'put_gamma': 0.0
        })
        
        self.spot_price = 0.0
        self.last_update = time.time()
        self.tick_count = 0

    async def on_tick(self, tick):
        """
        Deribit Ticker Update
        tick: {instrument_name, open_interest, greeks: {gamma, delta...}, mark_price, ...}
        """
        # Safety check
        if 'instrument_name' not in tick:
            # Could be index update: {"index_name": "btc_usd", "price": ...}
            if 'index_name' in tick and 'price' in tick:
                 self.spot_price = tick['price']
            return

        name = tick['instrument_name']
        
        # Update Spot (approximate from any ticker's index_price or specific index stream)
        if 'index_price' in tick:
            self.spot_price = tick['index_price']
            
        # Parse Instrument: BTC-29DEC23-40000-C
        parts = name.split('-')
        if len(parts) < 4:
            return # Skip perp or future if any
            
        strike = float(parts[2])
        opt_type = parts[3] # 'C' or 'P'
        
        # 1. Update Metrics
        # Open Interest
        oi = tick.get('open_interest', 0.0)
        
        # Gamma (Deribit gives gamma per contract)
        # GEX = Gamma * OI * Spot
        # Note: Deribit Gamma is usually "Change in Delta per $1 move" or "per 1% move"? 
        # API Docs: "gamma": 0.00002. 
        # Standard GEX formula: Gamma * OI * Spot.
        gamma = tick.get('greeks', {}).get('gamma', 0.0)
        if gamma is None: gamma = 0.0
            
        # Store
        if opt_type == 'C':
            self.strikes[strike]['call_oi'] = oi
            self.strikes[strike]['call_gamma'] = gamma
        else:
            self.strikes[strike]['put_oi'] = oi
            self.strikes[strike]['put_gamma'] = gamma
            
        self.tick_count += 1
        
        # 2. Periodic Reporting (every 1s)
        if time.time() - self.last_update > 1.0:
            self.print_heatmap()
            self.last_update = time.time()

    def print_heatmap(self):
        if self.spot_price == 0: return
        
        # Clear Screen (ANSI)
        print("\033[H\033[J")
        
        print(f"--- ⚡ DERIBIT LIVE HEATMAP (Spot: ${self.spot_price:,.2f}) ---")
        print(f"{'Strike':<10} | {'Net GEX ($M)':<15} | {'Total OI (BTC)':<15} | {'Sentiment'}")
        print("-" * 60)
        
        heatmap = []
        for strike, data in self.strikes.items():
            # Filter: Only show strikes within +/- 15% of spot to reduce noise
            if abs(strike - self.spot_price) / self.spot_price > 0.15:
                continue
                
            call_gex = data['call_gamma'] * data['call_oi'] * self.spot_price
            put_gex = data['put_gamma'] * data['put_oi'] * self.spot_price
            net_gex = (call_gex - put_gex) / 1_000_000 # In Millions
            total_oi = data['call_oi'] + data['put_oi']
            
            heatmap.append((strike, net_gex, total_oi))
            
        # Sort by Strike
        heatmap.sort(key=lambda x: x[0])
        
        # Colorama Helpers (manually using ANSI for speed)
        RESET = "\033[0m"
        RED = "\033[91m"
        GREEN = "\033[92m"
        YELLOW = "\033[93m"
        WHITE = "\033[97m"
        
        for strike, gex, oi in heatmap:
            # Color logic
            # High OI = Bright White / Yellow
            # Positive GEX = Green (Dealer Long Gamma / Stability)
            # Negative GEX = Red (Dealer Short Gamma / Volatility)
            
            gex_str = f"{gex:+.2f}M"
            color = WHITE
            if gex > 0.5: color = GREEN
            elif gex < -0.5: color = RED
            
            # Highlight Strikes with massive OI
            oi_marker = ""
            if oi > 500: oi_marker = "⬅ WALL"
            if oi > 1000: oi_marker = f"{YELLOW}⬅🔥 SUPER WALL{RESET}"
            
            # Highlight ATM
            if abs(strike - self.spot_price) < 250:
                print(f"{YELLOW}>> {strike:<7.0f} | {color}{gex_str:<15}{RESET} | {oi:<15.0f} {oi_marker}{RESET}")
            else:
                print(f"   {strike:<7.0f} | {color}{gex_str:<15}{RESET} | {oi:<15.0f} {oi_marker}{RESET}")

    async def start(self):
        await self.manager.start_stream()

if __name__ == "__main__":
    engine = OptionsHeatmapEngine()
    try:
        asyncio.run(engine.start())
    except KeyboardInterrupt:
        pass
