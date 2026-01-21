#!/usr/bin/env python3
"""Updated simple test with subprotocol"""

import asyncio
import websockets
import json

async def test_connection():
    """Test with subprotocol"""
    try:
        print("Connecting to ws://127.0.0.1:9000/emart_jeju_01...")
        # CRITICAL: Must specify subprotocol
        async with websockets.connect(
            "ws://127.0.0.1:9000/emart_jeju_01",
            subprotocols=["ocpp2.0.1"]  # CRITICAL for OCPP 2.0.1
        ) as ws:
            print("[OK] Connected!")
            
            # Send BootNotification
            message = [
                2,  # CALL
                "boot_001",
                "BootNotification",
                {
                    "chargingStation": {
                        "model": "Simulator",
                        "vendorName": "Python",
                        "serialNumber": "SN-test-001",
                        "firmwareVersion": "1.0.0"
                    },
                    "reason": "PowerUp"
                }
            ]
            
            await ws.send(json.dumps(message))
            print("[SEND] BootNotification sent")
            
            # Wait for response
            print("[WAIT] Waiting for response...")
            response = await asyncio.wait_for(ws.recv(), timeout=5)
            print(f"[RECV] Response: {response}")
            print("[SUCCESS] Test successful!")
            
    except asyncio.TimeoutError:
        print("[TIMEOUT] No response from server")
    except Exception as e:
        print(f"[ERROR] {type(e).__name__}: {e}")

if __name__ == "__main__":
    asyncio.run(test_connection())

