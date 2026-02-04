#!/usr/bin/env python3
"""Very simple connection test"""

import asyncio
import websockets

async def test():
    """Simple connection"""
    try:
        print("Connecting...")
        async with websockets.connect("ws://127.0.0.1:9000/test") as ws:
            print("Connected!")
            await ws.send("hello")
            resp = await ws.recv()
            print(f"Response: {resp}")
    except Exception as e:
        print(f"Error: {type(e).__name__}: {e}")

asyncio.run(test())
