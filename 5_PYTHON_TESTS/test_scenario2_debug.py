#!/usr/bin/env python3
"""테스트 시나리오 2 - 에너지 데이터 검증"""

import asyncio
import json
import websockets
from datetime import datetime

async def test_scenario_2_debug():
    """시나리오 2 테스트 (디버그 버전)"""
    try:
        print("="*80)
        print("테스트 시나리오 2: 충전 세션 (에너지 데이터 검증)")
        print("="*80)
        print()
        
        charger_id = "test_charger_001"
        transaction_id = "txn_" + charger_id + "_001"
        
        # 서버 연결
        print(f"[{charger_id}] 서버 연결 중...")
        async with websockets.connect(
            f"ws://127.0.0.1:9000/{charger_id}",
            subprotocols=["ocpp2.0.1"]
        ) as ws:
            print(f"[{charger_id}] 서버 연결 성공!")
            
            # 1. BootNotification
            print("\n[1] BootNotification 전송...")
            boot_msg = [
                2,  # CALL
                "boot_001",
                "BootNotification",
                {
                    "chargingStation": {
                        "model": "Simulator",
                        "vendorName": "Python",
                        "serialNumber": f"SN-{charger_id}",
                        "firmwareVersion": "1.0.0"
                    },
                    "reason": "PowerUp"
                }
            ]
            await ws.send(json.dumps(boot_msg))
            response = await asyncio.wait_for(ws.recv(), timeout=5)
            print(f"응답: {response[:100]}...")
            
            await asyncio.sleep(1)
            
            # 2. TransactionEvent - Started
            print("\n[2] TransactionEvent Started 전송...")
            energy_accumulated = 0.0
            current_power = 100.0
            
            txn_started_msg = [
                2,  # CALL
                "txn_started_001",
                "TransactionEvent",
                {
                    "eventType": "Started",
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "triggerReason": "Authorized",
                    "seqNo": 0,
                    "transactionData": {
                        "transactionId": transaction_id,
                        "chargingState": "Preparing",
                        "timeSpentCharging": 0,
                        "stoppedReason": None,
                        "totalCost": 0,
                        "chargingPeriods": [
                            {
                                "startDateTime": datetime.utcnow().isoformat() + "Z",
                                "dimensions": [
                                    {
                                        "name": "Energy.Active.Import.Register",
                                        "unit": "Wh",
                                        "unitMultiplier": 1,
                                        "value": 0  # Wh
                                    },
                                    {
                                        "name": "Power.Active.Import",
                                        "unit": "W",
                                        "unitMultiplier": 1000,
                                        "value": current_power
                                    }
                                ]
                            }
                        ]
                    }
                }
            ]
            
            print(f"메시지 내용 (Started):")
            print(f"  - Transaction ID: {transaction_id}")
            print(f"  - Energy: 0 Wh (0 kWh)")
            print(f"  - Power: {current_power} W")
            
            await ws.send(json.dumps(txn_started_msg))
            response = await asyncio.wait_for(ws.recv(), timeout=5)
            print(f"응답: {response}")
            
            await asyncio.sleep(2)
            
            # 3. TransactionEvent - Updated (충전 진행)
            print("\n[3] TransactionEvent Updated 전송 (충전 진행)...")
            for i in range(3):
                energy_accumulated += 0.5  # 500Wh 추가
                energy_wh = energy_accumulated * 1000  # kWh to Wh
                
                txn_updated_msg = [
                    2,  # CALL
                    f"txn_updated_{i:03d}",
                    "TransactionEvent",
                    {
                        "eventType": "Updated",
                        "timestamp": datetime.utcnow().isoformat() + "Z",
                        "triggerReason": "MeterValueClock",
                        "seqNo": i + 1,
                        "transactionData": {
                            "transactionId": transaction_id,
                            "chargingState": "Charging",
                            "timeSpentCharging": (i + 1) * 5,
                            "stoppedReason": None,
                            "totalCost": round(energy_accumulated * 150, 2),
                            "chargingPeriods": [
                                {
                                    "startDateTime": datetime.utcnow().isoformat() + "Z",
                                    "dimensions": [
                                        {
                                            "name": "Energy.Active.Import.Register",
                                            "unit": "Wh",
                                            "unitMultiplier": 1,
                                            "value": energy_wh  # Wh
                                        },
                                        {
                                            "name": "Power.Active.Import",
                                            "unit": "W",
                                            "unitMultiplier": 1000,
                                            "value": current_power * 0.8  # 80% power
                                        }
                                    ]
                                }
                            ]
                        }
                    }
                ]
                
                print(f"  [{i+1}] 에너지: {energy_accumulated:.2f} kWh ({energy_wh:.0f} Wh)")
                await ws.send(json.dumps(txn_updated_msg))
                response = await asyncio.wait_for(ws.recv(), timeout=5)
                print(f"      응답: {response}")
                
                await asyncio.sleep(2)
            
            # 4. TransactionEvent - Ended
            print("\n[4] TransactionEvent Ended 전송...")
            total_energy = energy_accumulated
            total_cost = round(total_energy * 150, 2)
            
            txn_ended_msg = [
                2,  # CALL
                "txn_ended_001",
                "TransactionEvent",
                {
                    "eventType": "Ended",
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "triggerReason": "Local",
                    "seqNo": 4,
                    "transactionData": {
                        "transactionId": transaction_id,
                        "chargingState": "Finishing",
                        "timeSpentCharging": 15,
                        "stoppedReason": "Local",
                        "totalCost": total_cost,
                        "chargingPeriods": [
                            {
                                "startDateTime": datetime.utcnow().isoformat() + "Z",
                                "dimensions": [
                                    {
                                        "name": "Energy.Active.Import.Register",
                                        "unit": "Wh",
                                        "unitMultiplier": 1,
                                        "value": total_energy * 1000  # kWh to Wh
                                    },
                                    {
                                        "name": "Power.Active.Import",
                                        "unit": "W",
                                        "unitMultiplier": 1000,
                                        "value": 0
                                    }
                                ]
                            }
                        ]
                    }
                }
            ]
            
            print(f"메시지 내용 (Ended):")
            print(f"  - Transaction ID: {transaction_id}")
            print(f"  - Total Energy: {total_energy:.2f} kWh ({total_energy * 1000:.0f} Wh)")
            print(f"  - Total Cost: {total_cost}")
            
            await ws.send(json.dumps(txn_ended_msg))
            response = await asyncio.wait_for(ws.recv(), timeout=5)
            print(f"응답: {response}")
            
            print("\n" + "="*80)
            print("테스트 완료!")
            print("="*80)
            
    except asyncio.TimeoutError:
        print("타임아웃: 서버 응답 없음")
    except Exception as e:
        print(f"오류: {type(e).__name__}: {e}")

if __name__ == "__main__":
    asyncio.run(test_scenario_2_debug())
