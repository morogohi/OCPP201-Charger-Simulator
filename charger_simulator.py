"""
OCPP 2.0.1 충전기 시뮬레이터
"""
import asyncio
import websockets
import json
import uuid
import logging
import os
from datetime import datetime
from typing import Optional, Dict, Any
from ocpp_messages import OCPPMessage, OCPPv201RequestBuilder

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 상세 프로토콜 로깅 활성화 여부
PROTOCOL_DEBUG = os.getenv('OCPP_PROTOCOL_DEBUG', 'false').lower() == 'true'


class ChargerSimulator:
    """OCPP 2.0.1 충전기 시뮬레이터"""

    def __init__(
        self,
        charger_id: str,
        server_url: str = "ws://localhost:9000",
        charger_model: str = "EVBox Home",
        charger_vendor: str = "EVBox",
        num_connectors: int = 1
    ):
        self.charger_id = charger_id
        self.server_url = server_url
        self.charger_model = charger_model
        self.charger_vendor = charger_vendor
        self.num_connectors = num_connectors
        self.websocket = None
        self.connected = False
        self.pending_requests: Dict[str, dict] = {}
        self.transaction_id = str(uuid.uuid4())
        self.is_charging = False
        self.meter_value = 0.0
        self.charge_rate = 0.1  # kWh per second
        self.current = 0.0
        self.voltage = 400.0

    async def connect(self):
        """서버에 연결"""
        try:
            uri = f"{self.server_url}/{self.charger_id}"
            logger.info(f"충전기 {self.charger_id} 서버에 연결 중: {uri}")
            
            self.websocket = await websockets.connect(uri, subprotocols=["ocpp2.0.1"])
            self.connected = True
            logger.info(f"충전기 {self.charger_id} 서버에 연결됨")
            
            # 부팅 알림 전송
            await self.send_boot_notification()
            
            # 메시지 수신 태스크 시작
            asyncio.create_task(self.receive_messages())
            
            # 하트비트 태스크 시작
            asyncio.create_task(self.heartbeat_loop())
            
            # 충전 시뮬레이션 태스크 시작
            asyncio.create_task(self.charging_loop())
            
        except Exception as e:
            logger.error(f"연결 실패: {e}")
            self.connected = False
            raise

    async def send_boot_notification(self):
        """부팅 알림 전송"""
        try:
            message = OCPPv201RequestBuilder.boot_notification(
                charger_model=self.charger_model,
                charger_vendor=self.charger_vendor,
                charger_serial=self.charger_id,
                reason="PowerUp"
            )
            await self.send_message(message)
            logger.info(f"부팅 알림 전송: {self.charger_id}")
        except Exception as e:
            logger.error(f"부팅 알림 전송 실패: {e}")

    async def send_message(self, message: str):
        """메시지 전송"""
        if self.websocket and self.connected:
            try:
                if PROTOCOL_DEBUG:
                    logger.debug(f"[CHARGER-SEND] {self.charger_id}: {message}")
                await self.websocket.send(message)
            except Exception as e:
                logger.error(f"메시지 전송 실패: {e}")
                self.connected = False

    async def receive_messages(self):
        """메시지 수신"""
        try:
            while self.connected and self.websocket:
                try:
                    message = await asyncio.wait_for(
                        self.websocket.recv(),
                        timeout=30.0
                    )
                    await self.handle_message(message)
                except asyncio.TimeoutError:
                    logger.warning(f"메시지 수신 타임아웃: {self.charger_id}")
                except websockets.exceptions.ConnectionClosed:
                    logger.warning(f"연결 종료: {self.charger_id}")
                    self.connected = False
                    break
        except Exception as e:
            logger.error(f"메시지 수신 오류: {e}")
            self.connected = False

    async def handle_message(self, message: str):
        """메시지 처리"""
        try:
            if PROTOCOL_DEBUG:
                logger.debug(f"[CHARGER-RECV] {self.charger_id}: {message}")
            
            message_type, message_id, action, payload = OCPPMessage.parse_message(message)
            
            if message_type == OCPPMessage.CALLRESULT:
                # 응답 처리
                if message_id in self.pending_requests:
                    logger.info(f"응답 수신: {action}, ID: {message_id}")
                    del self.pending_requests[message_id]
            
            elif message_type == OCPPMessage.CALL:
                # 요청 처리
                logger.info(f"요청 수신: {action}")
                await self.handle_request(message_id, action, payload)
            
            elif message_type == OCPPMessage.CALLERROR:
                logger.error(f"오류 응답: {action} - {payload}")
                if message_id in self.pending_requests:
                    del self.pending_requests[message_id]
                    
        except Exception as e:
            logger.error(f"메시지 처리 오류: {e}")

    async def handle_request(self, message_id: str, action: str, payload: Dict[str, Any]):
        """요청 처리"""
        try:
            if action == "RequestStartTransaction":
                await self.handle_request_start_transaction(message_id, payload)
            elif action == "RequestStopTransaction":
                await self.handle_request_stop_transaction(message_id, payload)
            elif action == "SetChargingProfile":
                await self.handle_set_charging_profile(message_id, payload)
            else:
                logger.warning(f"처리되지 않은 요청: {action}")
                response = OCPPMessage.create_call_error(
                    message_id, "NotImplemented", f"Action {action} not implemented"
                )
                await self.send_message(response)
        except Exception as e:
            logger.error(f"요청 처리 오류: {e}")

    async def handle_request_start_transaction(self, message_id: str, payload: Dict[str, Any]):
        """거래 시작 요청 처리"""
        try:
            self.is_charging = True
            self.transaction_id = str(uuid.uuid4())
            self.current = 16.0  # 16A로 시작
            
            logger.info(f"거래 시작: {self.transaction_id}")
            
            response = {
                "status": "Accepted",
                "transactionId": self.transaction_id
            }
            message = OCPPMessage.create_call_result(message_id, response)
            await self.send_message(message)
            
            # 거래 시작 이벤트 전송
            await self.send_transaction_event(
                event_type="Started",
                meter_value=0.0
            )
        except Exception as e:
            logger.error(f"거래 시작 처리 오류: {e}")

    async def handle_request_stop_transaction(self, message_id: str, payload: Dict[str, Any]):
        """거래 중지 요청 처리"""
        try:
            self.is_charging = False
            logger.info(f"거래 중지: {self.transaction_id}")
            
            response = {
                "status": "Accepted"
            }
            message = OCPPMessage.create_call_result(message_id, response)
            await self.send_message(message)
            
            # 거래 종료 이벤트 전송
            await self.send_transaction_event(
                event_type="Ended",
                meter_value=self.meter_value
            )
            
            self.meter_value = 0.0
            self.current = 0.0
        except Exception as e:
            logger.error(f"거래 중지 처리 오류: {e}")

    async def handle_set_charging_profile(self, message_id: str, payload: Dict[str, Any]):
        """충전 프로필 설정 처리"""
        try:
            logger.info("충전 프로필 설정됨")
            response = {"status": "Accepted"}
            message = OCPPMessage.create_call_result(message_id, response)
            await self.send_message(message)
        except Exception as e:
            logger.error(f"충전 프로필 설정 오류: {e}")

    async def send_transaction_event(self, event_type: str, meter_value: float):
        """거래 이벤트 전송"""
        try:
            message = OCPPv201RequestBuilder.transaction_event(
                event_type=event_type,
                transaction_id=self.transaction_id,
                evse_id=1,
                connector_id=1,
                meter_value=meter_value,
                voltage=self.voltage,
                current=self.current
            )
            await self.send_message(message)
            logger.info(f"거래 이벤트 전송: {event_type}, 에너지: {meter_value} kWh")
        except Exception as e:
            logger.error(f"거래 이벤트 전송 오류: {e}")

    async def heartbeat_loop(self):
        """하트비트 루프"""
        while self.connected:
            try:
                await asyncio.sleep(30)  # 30초마다 하트비트
                message = OCPPv201RequestBuilder.heartbeat()
                await self.send_message(message)
                logger.debug(f"하트비트 전송: {self.charger_id}")
            except Exception as e:
                logger.error(f"하트비트 전송 오류: {e}")

    async def charging_loop(self):
        """충전 시뮬레이션 루프"""
        while self.connected:
            try:
                if self.is_charging:
                    self.meter_value += self.charge_rate
                    
                    # 5초마다 거래 업데이트 이벤트 전송
                    await self.send_transaction_event(
                        event_type="Updated",
                        meter_value=self.meter_value
                    )
                
                await asyncio.sleep(5)
            except Exception as e:
                logger.error(f"충전 루프 오류: {e}")

    async def disconnect(self):
        """서버에서 연결 해제"""
        self.connected = False
        if self.websocket:
            await self.websocket.close()
        logger.info(f"충전기 {self.charger_id} 연결 해제됨")


async def main():
    """메인 함수"""
    charger = ChargerSimulator(
        charger_id="charger_001",
        server_url="ws://localhost:9000",
        charger_model="EVBox Home",
        charger_vendor="EVBox"
    )
    
    try:
        await charger.connect()
        
        # 충전기가 계속 실행되도록 유지
        while charger.connected:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        logger.info("충전기 시뮬레이터 종료 중...")
    finally:
        await charger.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
