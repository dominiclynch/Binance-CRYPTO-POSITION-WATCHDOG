# CRYPTO – Stale Position Cleaner

Periodically reconciles Binance Futures positions with the internal `position_tracker` DB and force-closes any leftovers that can block new trades.

### Why?
* Binance sometimes leaves dust-sized positions (`< $1` notional) after a full exit.
* Our DB may occasionally think a trade is *CLOSED* while the exchange still shows size, or vice-versa.
* These discrepancies skew risk stats and prevent fresh entries. Fixing them in a separate lightweight service keeps the main trading loop lean.

### How it works
1. Every 5 min the cleaner pulls `futures_position_information`.
2. For each symbol:
   * If `|positionAmt|` × `markPrice` < `$1` → send **MARKET** order with `reduceOnly=true` (reason `DUST_CLEANUP`).
   * If DB says *CLOSED* but Binance size ≠ 0 → close at market (`DB_MISMATCH`).
   * If DB says *OPEN* but Binance size = 0 → mark DB row closed (`EXCHANGE_CLOSED`).
3. Writes a single summary line, e.g.:
   ```text
   cleaner → closed 2 dust, fixed 1 mismatch
   ```

### Deployment
Same `.env` as the trading bot – no extra credentials.

**Systemd/Cron** (every 5 min):
```cron
*/5 * * * * /usr/bin/python3 /opt/bot/cleaner.py
```
Replace `/opt/bot` with the actual path.

---
MIT License © 2025
