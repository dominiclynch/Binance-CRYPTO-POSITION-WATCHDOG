import asyncio
import logging
import os
from datetime import datetime
from typing import Dict, List

try:
    from binance import AsyncClient
except ImportError:
    AsyncClient = None

# ----------------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------------
CHECK_INTERVAL_SECONDS: int = 5 * 60  # run every 5 minutes
ORDER_STALE_MINUTES: int = 20         # cancel orders older than this
LOG_FORMAT = "%(asctime)s | %(levelname)s | %(message)s"

logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
logger = logging.getLogger("stale-cleaner")

# ----------------------------------------------------------------------------
# Core logic
# ----------------------------------------------------------------------------
async def _ensure_client() -> "AsyncClient":
    if AsyncClient is None:
        raise RuntimeError(
            "python-binance not installed. Run `pip install python-binance`"
        )

    api_key = os.getenv("BINANCE_API_KEY")
    api_secret = os.getenv("BINANCE_API_SECRET")
    if not api_key or not api_secret:
        raise RuntimeError("Missing BINANCE_API_KEY / BINANCE_API_SECRET env vars")

    # Use testnet if BINANCE_TESTNET env var is set to "true"
    testnet = os.getenv("BINANCE_TESTNET", "false").lower() == "true"
    client = await AsyncClient.create(api_key, api_secret, testnet=testnet)
    
    if testnet:
        logger.info("Connected to Binance TESTNET")
    else:
        logger.info("Connected to Binance MAINNET")
    
    return client


async def clean_stale_orders(client=None) -> None:
    """Cancel stale LIMIT/STOP orders that have been open longer than ORDER_STALE_MINUTES."""
    if client is None:
        client = await _ensure_client()
        _owned_client = True
    else:
        _owned_client = False

    cancelled = 0
    open_orders: List[Dict] = await client.futures_get_open_orders()
    now_ms = int(datetime.utcnow().timestamp() * 1000)
    threshold_ms = ORDER_STALE_MINUTES * 60 * 1000

    for order in open_orders:
        # Use createTime (order placement time) instead of updateTime 
        # to catch truly old orders that may have been "touched" recently
        create_time = int(order.get("createTime", order["updateTime"]))
        age_ms = now_ms - create_time
        
        if age_ms < threshold_ms:
            continue  # still fresh

        sym = order["symbol"]
        order_id = order["orderId"]

        try:
            await client.futures_cancel_order(symbol=sym, orderId=order_id)
            logger.info("STALE_ORDER_CANCELLED | %s | id=%s | age=%.1f min", 
                       sym, order_id, age_ms / 60000)
            cancelled += 1
        except Exception as e:
            logger.error("Failed to cancel order %s: %s", order_id, e)

    logger.info("cleaner → cancelled %d stale orders", cancelled)

    if _owned_client:
        await client.close_connection()


# ----------------------------------------------------------------------------
# Entry point (when run as a script)
# ----------------------------------------------------------------------------
async def _loop() -> None:
    client = await _ensure_client()
    while True:
        start = datetime.utcnow()
        try:
            await clean_stale_orders(client)
        except Exception as exc:
            logger.exception("Cleaner error: %s", exc)
        # Wait until exactly the next multiple of CHECK_INTERVAL_SECONDS
        elapsed = (datetime.utcnow() - start).total_seconds()
        await asyncio.sleep(max(0, CHECK_INTERVAL_SECONDS - elapsed))


if __name__ == "__main__":
    asyncio.run(_loop())
