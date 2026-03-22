# Binance Crypto Position Watchdog

Stale order cleaner for Binance Futures. Periodically cancels open orders that have been sitting unfilled beyond a configurable age threshold.

## What It Does

- Scans all open Binance Futures orders every 5 minutes
- Cancels any order older than 20 minutes (configurable)
- Uses order creation time (not update time) to catch genuinely stale orders
- Prevents orphaned stop-loss and limit orders from blocking new trades

## Why

Binance sometimes leaves dust-sized positions or unfilled orders after exits. These block fresh entries and skew risk calculations. This service cleans them up automatically.

## Tech Stack

- **Python** — async, python-binance
- **Testing** — pytest with mocked Binance client

## Setup

```bash
pip install -r requirements.txt
export BINANCE_API_KEY=your_key
export BINANCE_API_SECRET=your_secret
python bot/cleaner.py
```

Set `BINANCE_TESTNET=true` to run against the Binance testnet.

## Quick Check

```bash
python check_orders.py  # shows all open orders with their ages
```

## License

MIT