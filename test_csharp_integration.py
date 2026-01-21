#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OCPP 2.0.1 C#  Python     

  C#    Python   .
"""

import asyncio
import json
import websockets
import uuid
from datetime import datetime
from enum import Enum

class ChargerStatus(Enum):
    """ """
    AVAILABLE = "Available"
    PREPARING = "Preparing"
    CHARGING = "Charging"
    SUSPENDED_EVSE = "SuspendedEVSE"
    SUSPENDED_EV = "SuspendedEV"
    FINISHING = "Finishing"
    RESERVED = "Reserved"
    UNAVAILABLE = "Unavailable"
    FAULTED = "Faulted"

class OCPPTestClient:
    """OCPP 2.0.1  """
    
    def __init__(self, charger_id, server_url="ws://127.0.0.1:9000", max_power=100):
        self.charger_id = charger_id
        self.server_url = server_url
        self.websocket = None
        self.max_power = max_power
        self.current_status = ChargerStatus.AVAILABLE
        self.energy_accumulated = 0.0
        self.current_power = 0.0
        self.transaction_id = None
        self.is_connected = False
        self.is_charging = False
        
    async def connect(self):
        """ """
        try:
            #  ID URL  
            charger_url = f"{self.server_url}/{self.charger_id}"
            print(f"[{self.charger_id}]   ... ({charger_url})")
            # OCPP 2.0.1 subprotocol 
            self.websocket = await websockets.connect(
                charger_url,
                subprotocols=["ocpp2.0.1"]
            )
            self.is_connected = True
            print(f" [{self.charger_id}]   ")
            
            # BootNotification 
            await self.send_boot_notification()
            
            #   
            asyncio.create_task(self._receive_messages())
            
            # Heartbeat 
            asyncio.create_task(self._send_heartbeat())
            
        except Exception as e:
            print(f" [{self.charger_id}]  : {e}")
            self.is_connected = False
    
    async def send_boot_notification(self):
        """BootNotification """
        try:
            message_id = str(uuid.uuid4())[:12]
            message = [
                2,  # CALL
                message_id,
                "BootNotification",
                {
                    "chargingStation": {
                        "model": "Simulator",
                        "vendorName": "Python",
                        "serialNumber": f"SN-{self.charger_id}-001",
                        "firmwareVersion": "1.0.0"
                    },
                    "reason": "PowerUp"
                }
            ]
            
            await self.websocket.send(json.dumps(message))
            print(f" [{self.charger_id}] BootNotification ")
            self.current_status = ChargerStatus.AVAILABLE
            
        except Exception as e:
            print(f" [{self.charger_id}] BootNotification  : {e}")
    
    async def _receive_messages(self):
        """  """
        try:
            while self.is_connected:
                message = await self.websocket.recv()
                print(f" [{self.charger_id}]  : {message[:80]}...")
                
                try:
                    msg_array = json.loads(message)
                    
                    if len(msg_array) >= 2:
                        msg_type = msg_array[0]
                        msg_id = msg_array[1]
                        
                        if msg_type == 3:  # CALLRESULT
                            print(f" [{self.charger_id}] CALLRESULT : {msg_id}")
                        
                        elif msg_type == 2:  # CALL
                            action = msg_array[2]
                            payload = msg_array[3] if len(msg_array) > 3 else {}
                            
                            await self._handle_call(action, msg_id, payload)
                            
                except json.JSONDecodeError:
                    print(f" [{self.charger_id}] JSON  ")
                    
        except websockets.exceptions.ConnectionClosed:
            print(f" [{self.charger_id}]  ")
            self.is_connected = False
        except Exception as e:
            print(f" [{self.charger_id}]  : {e}")
    
    async def _handle_call(self, action, msg_id, payload):
        """CALL  """
        print(f" [{self.charger_id}] CALL : {action}")
        
        if action == "RequestStartTransaction":
            await self._handle_request_start_transaction(msg_id, payload)
        
        elif action == "RequestStopTransaction":
            await self._handle_request_stop_transaction(msg_id, payload)
        
        elif action == "SetChargingProfile":
            await self._handle_set_charging_profile(msg_id, payload)
        
        else:
            #  
            await self._send_call_result(msg_id, {"status": "Accepted"})
    
    async def _handle_request_start_transaction(self, msg_id, payload):
        """RequestStartTransaction """
        try:
            id_token = payload.get("idToken", {}).get("idToken", "unknown")
            print(f" [{self.charger_id}]   : {id_token}")
            
            # 
            await self._send_call_result(msg_id, {"status": "Accepted"})
            
            #  
            await self.start_charging(id_token)
            
        except Exception as e:
            print(f" [{self.charger_id}]   : {e}")
            await self._send_call_result(msg_id, {"status": "Rejected"})
    
    async def _handle_request_stop_transaction(self, msg_id, payload):
        """RequestStopTransaction """
        try:
            print(f" [{self.charger_id}]   ")
            
            # 
            await self._send_call_result(msg_id, {"status": "Accepted"})
            
            #  
            await self.stop_charging()
            
        except Exception as e:
            print(f" [{self.charger_id}]   : {e}")
            await self._send_call_result(msg_id, {"status": "Rejected"})
    
    async def _handle_set_charging_profile(self, msg_id, payload):
        """SetChargingProfile """
        try:
            profile = payload.get("chargingProfile", {})
            periods = profile.get("chargingSchedule", {}).get("chargingSchedulePeriod", [])
            
            if periods:
                max_power = periods[0].get("limit", self.max_power) / 1000
                self.max_power = min(max_power, 100)  #  100kW
                print(f" [{self.charger_id}]  : {self.max_power}kW")
            
            await self._send_call_result(msg_id, {"status": "Accepted"})
            
        except Exception as e:
            print(f" [{self.charger_id}]   : {e}")
            await self._send_call_result(msg_id, {"status": "Rejected"})
    
    async def _send_call_result(self, msg_id, payload):
        """CALLRESULT """
        try:
            message = [
                3,  # CALLRESULT
                msg_id,
                payload
            ]
            
            await self.websocket.send(json.dumps(message))
            print(f" [{self.charger_id}] CALLRESULT : {msg_id}")
            
        except Exception as e:
            print(f" [{self.charger_id}]   : {e}")
    
    async def _send_heartbeat(self):
        """Heartbeat   (30 )"""
        try:
            while self.is_connected:
                await asyncio.sleep(30)
                
                message_id = str(uuid.uuid4())[:12]
                message = [
                    2,  # CALL
                    message_id,
                    "Heartbeat",
                    {
                        "currentTime": datetime.utcnow().isoformat() + "Z"
                    }
                ]
                
                await self.websocket.send(json.dumps(message))
                print(f" [{self.charger_id}] Heartbeat ")
                
        except asyncio.CancelledError:
            pass
        except Exception as e:
            print(f" [{self.charger_id}] Heartbeat : {e}")
    
    async def start_charging(self, id_token="user_token"):
        """ """
        try:
            if self.current_status != ChargerStatus.AVAILABLE:
                print(f" [{self.charger_id}]      ")
                return
            
            self.current_status = ChargerStatus.PREPARING
            self.transaction_id = str(uuid.uuid4())[:8]
            self.energy_accumulated = 0.0
            self.is_charging = True
            
            # TransactionEvent - Started
            await self._send_transaction_event("Started", id_token)
            
            #   
            await asyncio.sleep(2)
            self.current_status = ChargerStatus.CHARGING
            self.current_power = self.max_power
            
            # TransactionEvent - Updated
            await self._send_transaction_event("Updated", id_token)
            
            print(f" [{self.charger_id}]  : {self.transaction_id}")
            
            #  
            asyncio.create_task(self._simulate_charging())
            
        except Exception as e:
            print(f" [{self.charger_id}]   : {e}")
    
    async def stop_charging(self):
        """ """
        try:
            if not self.is_charging:
                print(f" [{self.charger_id}]    ")
                return
            
            self.is_charging = False
            self.current_status = ChargerStatus.FINISHING
            
            # TransactionEvent - Updated
            await self._send_transaction_event("Updated", "user_token")
            
            await asyncio.sleep(1)
            
            # TransactionEvent - Ended
            await self._send_transaction_event("Ended", "user_token")
            
            self.current_status = ChargerStatus.AVAILABLE
            self.current_power = 0.0
            
            print(f" [{self.charger_id}]  : {self.transaction_id} (: {self.energy_accumulated:.2f} kWh)")
            
            self.transaction_id = None
            
        except Exception as e:
            print(f" [{self.charger_id}]   : {e}")
    
    async def _simulate_charging(self):
        """  ( )"""
        try:
            while self.is_charging:
                await asyncio.sleep(5)
                
                #   (  * )
                energy_per_second = (self.current_power / 3600)
                self.energy_accumulated += energy_per_second * 5
                
                # 80%    ( )
                if self.energy_accumulated > 20:
                    self.current_power = self.max_power * 0.7
                
                #   
                if self.is_charging:
                    await self._send_transaction_event("Updated", "user_token")
                    
        except Exception as e:
            print(f" [{self.charger_id}]   : {e}")
    
    async def _send_transaction_event(self, event_type, id_token):
        """TransactionEvent """
        try:
            message_id = str(uuid.uuid4())[:12]
            
            message = [
                2,  # CALL
                message_id,
                "TransactionEvent",
                {
                    "eventType": event_type,
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "triggerReason": "Authorized",
                    "seqNo": 0,
                    "transactionData": {
                        "transactionId": self.transaction_id,
                        "chargingState": self.current_status.value,
                        "timeSpentCharging": 0,
                        "stoppedReason": "Local" if event_type == "Ended" else None,
                        "totalCost": round(self.energy_accumulated * 150, 2),
                        "chargingPeriods": [
                            {
                                "startDateTime": datetime.utcnow().isoformat() + "Z",
                                "dimensions": [
                                    {
                                        "name": "Energy.Active.Import.Register",
                                        "unit": "Wh",
                                        "unitMultiplier": 1,
                                        "value": self.energy_accumulated * 1000
                                    },
                                    {
                                        "name": "Power.Active.Import",
                                        "unit": "W",
                                        "unitMultiplier": 1000,
                                        "value": self.current_power
                                    }
                                ]
                            }
                        ]
                    }
                }
            ]
            
            await self.websocket.send(json.dumps(message))
            print(f" [{self.charger_id}] TransactionEvent  ({event_type}): {self.energy_accumulated:.2f} kWh")
            
        except Exception as e:
            print(f" [{self.charger_id}] TransactionEvent  : {e}")
    
    async def send_status_notification(self):
        """StatusNotification """
        try:
            message_id = str(uuid.uuid4())[:12]
            
            message = [
                2,  # CALL
                message_id,
                "StatusNotification",
                {
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "connectorStatus": self.current_status.value,
                    "evseId": 1,
                    "connectorId": 1
                }
            ]
            
            await self.websocket.send(json.dumps(message))
            print(f" [{self.charger_id}] StatusNotification : {self.current_status.value}")
            
        except Exception as e:
            print(f" [{self.charger_id}] StatusNotification  : {e}")
    
    async def disconnect(self):
        """ """
        try:
            self.is_connected = False
            if self.websocket:
                await self.websocket.close()
            print(f" [{self.charger_id}]  ")
        except Exception as e:
            print(f" [{self.charger_id}]   : {e}")
    
    def get_status(self):
        """  """
        return f"[{self.charger_id}] : {self.current_status.value}, : {self.current_power}kW, : {self.energy_accumulated:.2f}kWh"


async def test_scenario_1():
    """ 1:    BootNotification"""
    print("\n" + "="*80)
    print("[ 1]    BootNotification")
    print("="*80)
    
    charger = OCPPTestClient("emart_jeju_01")
    await charger.connect()
    await asyncio.sleep(5)
    print(charger.get_status())
    await charger.disconnect()


async def test_scenario_2():
    """ 2:  """
    print("\n" + "="*80)
    print("[ 2]   (Start  Charging  Stop)")
    print("="*80)
    
    charger = OCPPTestClient("emart_jeju_01", max_power=100)
    await charger.connect()
    await asyncio.sleep(2)
    
    #  
    await charger.start_charging("token_user_001")
    await asyncio.sleep(15)  # 15 
    
    #  
    await charger.stop_charging()
    await asyncio.sleep(2)
    
    print(charger.get_status())
    await charger.disconnect()


async def test_scenario_3():
    """ 3:  """
    print("\n" + "="*80)
    print("[ 3]    ")
    print("="*80)
    
    chargers = [
        OCPPTestClient("emart_jeju_01", max_power=100),
        OCPPTestClient("emart_jeju_02", max_power=100),
        OCPPTestClient("emart_shinjeju_01", max_power=50),
    ]
    
    # 
    for charger in chargers:
        await charger.connect()
    
    await asyncio.sleep(3)
    
    #  
    print("\n[  ]")
    for charger in chargers:
        await charger.start_charging()
    
    await asyncio.sleep(20)  # 20 
    
    #  
    print("\n[  ]")
    for charger in chargers:
        await charger.stop_charging()
    
    await asyncio.sleep(2)
    
    #  
    for charger in chargers:
        print(charger.get_status())
    
    # 
    for charger in chargers:
        await charger.disconnect()


async def main():
    """ """
    import sys
    
    print("="*80)
    print("  OCPP 2.0.1 Python  ")
    print("="*80)
    
    if len(sys.argv) > 1:
        scenario = sys.argv[1]
    else:
        scenario = "all"
    
    try:
        if scenario == "1" or scenario == "all":
            await test_scenario_1()
        
        if scenario == "2" or scenario == "all":
            await test_scenario_2()
        
        if scenario == "3" or scenario == "all":
            await test_scenario_3()
        
        print("\n   !")
        
    except Exception as e:
        print(f"\n  : {e}")


if __name__ == "__main__":
    asyncio.run(main())
