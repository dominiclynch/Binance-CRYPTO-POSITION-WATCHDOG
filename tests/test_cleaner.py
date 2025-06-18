import asyncio
from unittest.mock import AsyncMock, patch

import pytest

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))  # add project root

from bot.cleaner import clean_stale_orders



    def __init__(self, status="CLOSED"):
        self.status = status


@pytest.mark.asyncio
async def test_cancel_stale_orders():
    # Mock Binance client
    client = AsyncMock()

    now_ms = 1_700_000_000_000  # arbitrary fixed time
    stale_ms = now_ms - (22 * 60 * 1000)  # 22 minutes old
    fresh_ms = now_ms - (5 * 60 * 1000)   # 5 minutes old

    client.futures_get_open_orders = AsyncMock(
        return_value=[
            {"symbol": "BTCUSDT", "orderId": 1, "updateTime": stale_ms},
            {"symbol": "ETHUSDT", "orderId": 2, "updateTime": fresh_ms},
        ]
    )

    client.futures_cancel_order = AsyncMock()


    # Patch datetime.utcnow to control now_ms
    import bot.cleaner as mod
    class DummyDT:
        @staticmethod
        def utcnow():
            import datetime
            return datetime.datetime.utcfromtimestamp(now_ms/1000)
    
    monkeypatch = None
