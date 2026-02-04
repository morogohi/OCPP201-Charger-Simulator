"""
OCPP 2.0.1 중앙 서버
"""
import asyncio
import websockets
import logging
import os
import sys
from typing import Dict, Set, Optional, Any
from datetime import datetime

# 프로젝트 루트 경로 추가 (4_PYTHON_SOURCE에서 실행할 때도 지원)
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, '8_DATABASE'))

from ocpp_messages import OCPPMessage, OCPPv201RequestBuilder

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 상세 프로토콜 로깅 활성화 여부
PROTOCOL_DEBUG = os.getenv('OCPP_PROTOCOL_DEBUG', 'false').lower() == 'true'


class ChargerConnection:
    """충전기 연결 관리"""

    def __init__(self, charger_id: str, websocket, path: str):
        self.charger_id = charger_id
        self.websocket = websocket
        self.path = path
        self.connected = True
        self.last_heartbeat = datetime.now()
        self.boot_status = False
        self.transactions: Dict[str, dict] = {}

    async def send(self, message: str):
        """메시지 전송"""
        try:
            if PROTOCOL_DEBUG:
                logger.debug(f"[SERVER-SEND] {self.charger_id}: {message}")
            await self.websocket.send(message)
        except Exception as e:
            logger.error(f"메시지 전송 실패 ({self.charger_id}): {e}")
            self.connected = False

    async def receive(self) -> Optional[str]:
        """메시지 수신"""
        try:
            msg = await asyncio.wait_for(self.websocket.recv(), timeout=60.0)
            if PROTOCOL_DEBUG:
                logger.debug(f"[SERVER-RECV] {self.charger_id}: {msg}")
            return msg
        except asyncio.TimeoutError:
            logger.warning(f"메시지 수신 타임아웃 ({self.charger_id})")
            return None
        except websockets.exceptions.ConnectionClosed:
            logger.warning(f"연결 종료 ({self.charger_id})")
            self.connected = False
            return None
        except Exception as e:
            logger.error(f"메시지 수신 오류 ({self.charger_id}): {e}")
            self.connected = False
            return None


class OCPPServer:
    """OCPP 2.0.1 중앙 서버"""

    def __init__(self, host: str = "0.0.0.0", port: int = 9000):
        self.host = host
        self.port = port
        self.chargers: Dict[str, ChargerConnection] = {}
        self.shutdown_event = asyncio.Event()  # 종료 이벤트
        self.pending_requests: Dict[str, dict] = {}

    async def start(self):
        """서버 시작"""
        # Windows 시스템에서 TIME_WAIT 상태의 포트를 빠르게 재사용하기 위해
        # 소켓 옵션 설정
        async with websockets.serve(
            self.handle_charger_connection,
            self.host,
            self.port,
            subprotocols=["ocpp2.0.1"],
            ping_interval=20,
            ping_timeout=20
        ):
            logger.info(f"OCPP 2.0.1 서버 시작: ws://{self.host}:{self.port}")
            # 종료 이벤트를 기다림 (기본적으로 무한 대기)
            await self.shutdown_event.wait()


    async def handle_charger_connection(self, websocket):
        """충전기 연결 처리"""
        # 경로에서 충전기 ID 추출 (요청 헤더에서)
        path = "/"
        charger_id = None
        charger = None
        
        try:
            # websocket.request는 websockets 라이브러리에서 제공
            path = websocket.request.path if hasattr(websocket, 'request') else "/"
        except Exception as e:
            logger.error(f"경로 추출 오류: {e}")
            path = "/"
        
        charger_id = path.lstrip('/')
        
        if not charger_id or charger_id == "":
            logger.warning("충전기 ID 없음")
            try:
                await websocket.close()
            except:
                pass
            return

        logger.info(f"충전기 연결: {charger_id}")
        
        # 충전기 연결 객체 생성
        charger = ChargerConnection(charger_id, websocket, path)
        self.chargers[charger_id] = charger

        try:
            # 메시지 수신 및 처리 루프
            while charger.connected:
                try:
                    message = await charger.receive()
                    
                    if not message:
                        break

                    try:
                        message_type, message_id, action, payload = OCPPMessage.parse_message(message)
                        logger.debug(f"메시지 파싱 성공: {action}")
                        
                        if message_type == OCPPMessage.CALL:
                            # 요청 처리
                            await self.handle_request(charger, message_id, action, payload)
                        
                        elif message_type == OCPPMessage.CALLRESULT:
                            # 응답 처리
                            await self.handle_response(charger_id, message_id, payload)
                        
                        elif message_type == OCPPMessage.CALLERROR:
                            logger.error(f"오류 응답 ({charger_id}): {action}")
                    
                    except Exception as e:
                        logger.error(f"메시지 처리 오류 ({charger_id}): {type(e).__name__}: {e}", exc_info=True)
                
                except asyncio.CancelledError:
                    logger.info(f"연결 취소됨: {charger_id}")
                    break
                except asyncio.TimeoutError:
                    logger.warning(f"메시지 수신 타임아웃: {charger_id}")
                    continue
                except Exception as e:
                    logger.error(f"메시지 수신 오류 ({charger_id}): {type(e).__name__}: {e}")
                    break

        except Exception as e:
            logger.error(f"연결 처리 오류 ({charger_id}): {type(e).__name__}: {e}", exc_info=True)
        
        finally:
            # 연결 종료
            if charger_id in self.chargers:
                del self.chargers[charger_id]
            logger.info(f"충전기 연결 해제: {charger_id}")

    async def handle_request(self, charger: ChargerConnection, message_id: str, action: str, payload: Dict[str, Any]):
        """요청 처리"""
        logger.info(f"요청 처리 ({charger.charger_id}): {action}")

        try:
            if action == "BootNotification":
                await self.handle_boot_notification(charger, message_id, payload)
            
            elif action == "Heartbeat":
                await self.handle_heartbeat(charger, message_id)
            
            elif action == "StatusNotification":
                await self.handle_status_notification(charger, message_id, payload)
            
            elif action == "TransactionEvent":
                await self.handle_transaction_event(charger, message_id, payload)
            
            elif action == "Authorize":
                await self.handle_authorize(charger, message_id, payload)
            
            else:
                logger.warning(f"처리되지 않은 요청: {action}")
                response = OCPPMessage.create_call_error(
                    message_id, "NotImplemented", f"Action {action} not implemented"
                )
                await charger.send(response)
        
        except Exception as e:
            logger.error(f"요청 처리 오류: {e}")
            response = OCPPMessage.create_call_error(
                message_id, "InternalError", str(e)
            )
            await charger.send(response)

    async def handle_boot_notification(self, charger: ChargerConnection, message_id: str, payload: Dict[str, Any]):
        """부팅 알림 처리"""
        logger.info(f"부팅 알림 수신 ({charger.charger_id}): {payload.get('reason')}")
        
        charger.boot_status = True
        charger.last_heartbeat = datetime.now()
        
        response = {
            "currentTime": datetime.utcnow().isoformat() + "Z",
            "interval": 300,
            "status": "Accepted"
        }
        
        message = OCPPMessage.create_call_result(message_id, response)
        await charger.send(message)
        
        logger.info(f"부팅 알림 응답 전송 ({charger.charger_id})")

    async def handle_heartbeat(self, charger: ChargerConnection, message_id: str):
        """하트비트 처리"""
        charger.last_heartbeat = datetime.now()
        
        response = {
            "currentTime": datetime.utcnow().isoformat() + "Z"
        }
        
        message = OCPPMessage.create_call_result(message_id, response)
        await charger.send(message)
        
        logger.debug(f"하트비트 응답 전송 ({charger.charger_id})")

    async def handle_status_notification(self, charger: ChargerConnection, message_id: str, payload: Dict[str, Any]):
        """상태 알림 처리"""
        logger.info(f"상태 알림 ({charger.charger_id}): {payload.get('connectorStatus')}")
        
        response = {}
        
        message = OCPPMessage.create_call_result(message_id, response)
        await charger.send(message)

    async def handle_transaction_event(self, charger: ChargerConnection, message_id: str, payload: Dict[str, Any]):
        """거래 이벤트 처리"""
        try:
            event_type = payload.get("eventType")
            transaction_data = payload.get("transactionData", {}) or {}
            # 일부 충전기 구현에서 transactionInfo로 전달되는 경우를 지원
            transaction_info = payload.get("transactionInfo", {}) or {}
            transaction_id = transaction_data.get("transactionId") or transaction_info.get("transactionId")
            total_cost = transaction_data.get("totalCost", 0) or transaction_info.get("totalCost", 0) or 0
            
            # chargingPeriods에서 에너지 데이터 추출
            energy_delivered = 0.0
            charging_periods = transaction_data.get("chargingPeriods", []) or transaction_info.get("chargingPeriods", []) or []
            
            if charging_periods:
                for period in charging_periods:
                    dimensions = period.get("dimensions", [])
                    for dimension in dimensions:
                        if dimension.get("name") == "Energy.Active.Import.Register":
                            # value는 Wh단위이므로 kWh로 변환 (unitMultiplier가 1이면 그대로 사용)
                            energy_wh = dimension.get("value", 0)
                            energy_delivered = energy_wh / 1000.0  # Wh to kWh
                            break
            else:
                # fallback: meterValue 구조를 사용하는 메시지 지원
                meter_values = payload.get("meterValue", [])
                for mv in meter_values:
                    for sampled in mv.get("sampledValue", []):
                        if sampled.get("measurand") == "Energy.Active.Import.Register":
                            energy_delivered = float(sampled.get("value", 0))
                            break
            
            logger.info(f"거래 이벤트 ({charger.charger_id}): {event_type}, ID: {transaction_id}, "
                       f"에너지: {energy_delivered:.2f} kWh, 비용: {total_cost}")
            
            # 거래 정보 저장 (Ended 이벤트일 때만)
            if event_type == "Ended" and transaction_id:
                try:
                    charger.transactions[transaction_id] = {
                        "transaction_id": transaction_id,
                        "charger_id": charger.charger_id,
                        "energy_delivered": energy_delivered,
                        "total_cost": total_cost,
                        "timestamp": datetime.now()
                    }
                    logger.info(f"거래 저장 완료: {transaction_id}, 에너지: {energy_delivered:.2f} kWh")
                except Exception as e:
                    logger.error(f"거래 저장 실패: {e}")
            
            response = {}
            message = OCPPMessage.create_call_result(message_id, response)
            await charger.send(message)
            
        except Exception as e:
            logger.error(f"거래 이벤트 처리 오류 ({charger.charger_id}): {e}")
            response = {}
            message = OCPPMessage.create_call_result(message_id, response)
            await charger.send(message)

    async def handle_authorize(self, charger: ChargerConnection, message_id: str, payload: Dict[str, Any]):
        """인증 처리"""
        id_token = payload.get("idToken", {}).get("idToken", "unknown")
        logger.info(f"인증 요청 ({charger.charger_id}): {id_token}")
        
        response = {
            "idTokenInfo": {
                "status": "Accepted",
                "idToken": id_token
            }
        }
        
        message = OCPPMessage.create_call_result(message_id, response)
        await charger.send(message)

    async def handle_response(self, charger_id: str, message_id: str, payload: Dict[str, Any]):
        """응답 처리"""
        logger.debug(f"응답 수신 ({charger_id}), ID: {message_id}")

    async def request_start_transaction(self, charger_id: str, evse_id: int = 1, connector_id: int = 1):
        """거래 시작 요청"""
        if charger_id not in self.chargers:
            logger.error(f"충전기를 찾을 수 없음: {charger_id}")
            return False

        charger = self.chargers[charger_id]
        
        payload = {
            "evseId": evse_id,
            "connectorId": connector_id,
            "idToken": {
                "idToken": "test_token",
                "type": "Central"
            }
        }
        
        message = OCPPMessage.create_call("RequestStartTransaction", payload)
        await charger.send(message)
        
        logger.info(f"거래 시작 요청 전송: {charger_id}")
        return True

    async def request_stop_transaction(self, charger_id: str, transaction_id: str = None):
        """거래 중지 요청"""
        if charger_id not in self.chargers:
            logger.error(f"충전기를 찾을 수 없음: {charger_id}")
            return False

        charger = self.chargers[charger_id]
        
        payload = {
            "transactionId": transaction_id or "default_transaction"
        }
        
        message = OCPPMessage.create_call("RequestStopTransaction", payload)
        await charger.send(message)
        
        logger.info(f"거래 중지 요청 전송: {charger_id}")
        return True

    def get_charger_status(self, charger_id: str = None) -> Dict[str, Any]:
        """충전기 상태 조회"""
        if charger_id:
            if charger_id in self.chargers:
                charger = self.chargers[charger_id]
                return {
                    "charger_id": charger_id,
                    "connected": charger.connected,
                    "boot_status": charger.boot_status,
                    "last_heartbeat": charger.last_heartbeat.isoformat()
                }
            return {"error": f"Charger {charger_id} not found"}
        
        # 모든 충전기 상태
        status = {}
        for cid, charger in self.chargers.items():
            status[cid] = {
                "connected": charger.connected,
                "boot_status": charger.boot_status,
                "last_heartbeat": charger.last_heartbeat.isoformat()
            }
        return status


async def main():
    """메인 함수"""
    import traceback
    server = OCPPServer(host="127.0.0.1", port=9000)
    while True:
        try:
            await server.start()
        except asyncio.CancelledError:
            logger.info("서버가 취소됨")
            break
        except KeyboardInterrupt:
            logger.info("서버 종료됨 (키보드 인터럽트)")
            break
        except Exception as e:
            logger.error(f"메인 함수 오류: {e}")
            traceback.print_exc()
            logger.info("서버가 예외 후 재시작됩니다.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n서버가 종료되었습니다.")






