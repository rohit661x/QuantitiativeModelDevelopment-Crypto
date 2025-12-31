# HFT Crypto Quantitative Engine

A high-frequency, event-driven trading system for Crypto (Binance Futures & Deribit Options).
Designed for ultra-low latency (millisecond) utilizing `asyncio`, `websockets`, and `numba` for real-time incremental calculations.

## Architecture

The system is split into two core engines:

1.  **The Sniper (Futures)**: `src/engine.py`
    *   **Source**: Binance USD-M Futures (`@bookTicker`).
    *   **Logic**: Updates 1000+ technical indicators (e.g., SMA windows 10-1010) concurrently on *every single tick*.
    *   **Tech**: Incremental State Machine + Numba JIT Kernels.

2.  **The Radar (Options)**: `src/engine_options.py`
    *   **Source**: Deribit Options Chain.
    *   **Logic**: Aggregates sparse option ticks into a dense "Heatmap".
    *   **Metrics**: Real-time Open Interest Walls & Gamma Exposure (GEX) Profiling.

## Directory Structure
```text
.
├── src/
│   ├── engine.py           # core futures HFT engine
│   ├── engine_options.py   # options heatmap engine
│   ├── math_lib.py         # numba-optimized math kernels
│   └── ingestion/
│       ├── binance_wss.py  # binance websocket client
│       └── deribit_manager.py # deribit websocket client
├── requirements.txt
└── tools/
    └── latency_test.py     # benchmark script
```

## Setup
```bash
# 1. Create venv
python3 -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt
```

## Usage

### Run the Options Heatmap
Visualizes massive OI barriers and Gamma Flip levels.
```bash
python src/engine_options.py
```

### Run the HFT Futures Engine
Processes live ticks for mass-permutation testing.
```bash
python src/engine.py
```

### Check Latency
Benchmarks your network connection to Binance.
```bash
python tools/latency_test.py
```
