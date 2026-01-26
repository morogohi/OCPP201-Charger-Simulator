#!/usr/bin/env python3
"""OCPP 2.0.1 Simple Server"""

import asyncio
import websockets
import logging
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def handle_client(websocket, path):
    """Handle client connection"""
    logger.info(f"Client connected: {path}")
    try:
        async for message in websocket:
            logger.info(f"Received: {message[:100]}")
            # Echo the message back
            await websocket.send(message)
            logger.info(f"Sent response")
    except Exception as e:
        logger.error(f"Error: {type(e).__name__}: {e}")
    finally:
        logger.info(f"Client disconnected: {path}")

async def main():
    """Main server"""
    try:
        logger.info("Starting server...")
        async with websockets.serve(
            handle_client,
            "127.0.0.1",
            9000,
            subprotocols=["ocpp2.0.1"]
        ):
            logger.info("Server started on ws://127.0.0.1:9000")
            # Wait forever
            await asyncio.Future()
    except KeyboardInterrupt:
        logger.info("Server stopped")
    except Exception as e:
        logger.error(f"Server error: {type(e).__name__}: {e}", exc_info=True)

if __name__ == "__main__":
    asyncio.run(main())
