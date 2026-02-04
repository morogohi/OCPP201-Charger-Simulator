#!/usr/bin/env python3
"""Test server and client in same process"""

import asyncio
import websockets
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def handle_client(websocket):
    """Handle client connection"""
    logger.info(f"Server: Client connected")
    try:
        async for message in websocket:
            logger.info(f"Server: Received: {message[:100]}")
            await websocket.send(message)
            logger.info(f"Server: Sent response")
    except Exception as e:
        logger.error(f"Server: Error: {type(e).__name__}: {e}")
    finally:
        logger.info(f"Server: Client disconnected")

async def test_client():
    """Test client"""
    await asyncio.sleep(1)  # Wait for server to start
    try:
        logger.info("Client: Connecting...")
        async with websockets.connect("ws://127.0.0.1:9000/test", subprotocols=["ocpp2.0.1"]) as ws:
            logger.info("Client: Connected!")
            message = json.dumps([2, "msg_001", "BootNotification", {"test": "data"}])
            await ws.send(message)
            logger.info(f"Client: Sent: {message}")
            resp = await ws.recv()
            logger.info(f"Client: Response: {resp}")
    except Exception as e:
        logger.error(f"Client: Error: {type(e).__name__}: {e}")

async def server():
    """Server"""
    async with websockets.serve(handle_client, "127.0.0.1", 9000, subprotocols=["ocpp2.0.1"]):
        logger.info("Server: Started on ws://127.0.0.1:9000")
        # Run for 10 seconds
        await asyncio.sleep(10)
        logger.info("Server: Shutting down")

async def main():
    """Run both server and client"""
    server_task = asyncio.create_task(server())
    client_task = asyncio.create_task(test_client())
    
    # Wait for both
    await asyncio.gather(server_task, client_task, return_exceptions=True)
    logger.info("Done")

if __name__ == "__main__":
    asyncio.run(main())
