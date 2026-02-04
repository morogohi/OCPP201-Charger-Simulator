#!/usr/bin/env python3
"""간단한 OCPP 연결 테스트"""

import asyncio
import websockets
import json

async def test_connection():
    """간단한 연결 테스트"""
    try:
        print("서버에 연결 중...")
        uri = "ws://127.0.0.1:9000/test_charger_01"
        
        async with websockets.connect(uri, subprotocols=["ocpp2.0.1"]) as websocket:
            print("✅ 서버 연결 성공!")
            
            # BootNotification 전송
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
            
            await websocket.send(json.dumps(message))
            print("📤 BootNotification 전송")
            
            # 응답 대기
            print("응답 대기 중...")
            response = await asyncio.wait_for(websocket.recv(), timeout=5)
            print(f"📥 응답 수신: {response}")
            
    except asyncio.TimeoutError:
        print("❌ 타임아웃: 서버에서 응답이 없습니다")
    except Exception as e:
        print(f"❌ 오류: {e}")

if __name__ == "__main__":
    asyncio.run(test_connection())
