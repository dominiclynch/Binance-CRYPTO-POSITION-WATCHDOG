#!/usr/bin/env python3
"""Quick script to check current open orders and their ages."""

import asyncio
import os
from datetime import datetime
from binance import AsyncClient

async def check_orders():
    api_key = os.getenv("BINANCE_API_KEY")
    api_secret = os.getenv("BINANCE_API_SECRET")
    
    client = await AsyncClient.create(api_key, api_secret)
    orders = await client.futures_get_open_orders()
    
    now_ms = int(datetime.utcnow().timestamp() * 1000)
    
    print(f"Found {len(orders)} open orders:")
    for order in orders:
        create_time = int(order.get("createTime", order["updateTime"]))
        update_time = int(order["updateTime"])
        age_min = (now_ms - create_time) / 60000
        last_update_min = (now_ms - update_time) / 60000
        
        print(f"  {order['symbol']} | ID: {order['orderId']} | Age: {age_min:.1f}min | LastUpdate: {last_update_min:.1f}min")
    
    await client.close_connection()

if __name__ == "__main__":
    asyncio.run(check_orders())
