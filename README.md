# Binance Crypto Position Watchdog

Automated stale-order cleaner for Binance Futures positions.

## What It Does

- Polls open futures orders every 5 minutes via the Binance API
- Cancels LIMIT/STOP orders older than a configurable threshold (default: 20 min)
- Runs as a persistent async loop suitable for systemd deployment

## Tech Stack

- **Python:** asyncio, python-binance
- **Testing:** pytest

## Setup

```bash
pip install -r requirements.txt
export BINANCE_API_KEY=your_key
export BINANCE_API_SECRET=your_secret
python bot/cleaner.py
```

Set `BINANCE_TESTNET=true` to run against the testnet.

## License

MIT
