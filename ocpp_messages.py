"""
OCPP 2.0.1 메시지 핸들링
"""
import json
import uuid
import logging
import os
from typing import Dict, Any, Tuple
from datetime import datetime

# 상세 프로토콜 로깅 활성화 여부 (환경변수로 제어)
PROTOCOL_DEBUG = os.getenv('OCPP_PROTOCOL_DEBUG', 'false').lower() == 'true'
logger = logging.getLogger(__name__)


class OCPPMessage:
    """OCPP 메시지 기본 클래스"""

    # 메시지 타입
    CALL = 2
    CALLRESULT = 3
    CALLERROR = 4

    @staticmethod
    def create_call(action: str, payload: Dict[str, Any]) -> str:
        """Call 메시지 생성"""
        message_id = str(uuid.uuid4())
        message = [OCPPMessage.CALL, message_id, action, payload]
        result = json.dumps(message)
        if PROTOCOL_DEBUG:
            logger.debug(f"[OCPP-CALL-SEND] Action: {action}, ID: {message_id}")
            logger.debug(f"[OCPP-PAYLOAD-SEND] {json.dumps(payload, indent=2, ensure_ascii=False)}")
        return result

    @staticmethod
    def create_call_result(message_id: str, payload: Dict[str, Any]) -> str:
        """CallResult 메시지 생성"""
        message = [OCPPMessage.CALLRESULT, message_id, payload]
        result = json.dumps(message)
        if PROTOCOL_DEBUG:
            logger.debug(f"[OCPP-CALLRESULT-SEND] ID: {message_id}")
            logger.debug(f"[OCPP-RESPONSE-SEND] {json.dumps(payload, indent=2, ensure_ascii=False)}")
        return result

    @staticmethod
    def create_call_error(message_id: str, error_code: str, error_message: str) -> str:
        """CallError 메시지 생성"""
        message = [OCPPMessage.CALLERROR, message_id, error_code, error_message]
        result = json.dumps(message)
        if PROTOCOL_DEBUG:
            logger.debug(f"[OCPP-CALLERROR-SEND] ID: {message_id}")
            logger.debug(f"[OCPP-ERROR-SEND] Code: {error_code}, Message: {error_message}")
        return result

    @staticmethod
    def parse_message(message: str) -> Tuple[int, str, str, Dict[str, Any]]:
        """메시지 파싱"""
        try:
            if PROTOCOL_DEBUG:
                logger.debug(f"[OCPP-RAW-RECV] {message}")
            
            data = json.loads(message)
            if not isinstance(data, list) or len(data) < 3:
                raise ValueError("Invalid message format")
            
            message_type = data[0]
            message_id = data[1]
            
            if message_type == OCPPMessage.CALL:
                action = data[2]
                payload = data[3] if len(data) > 3 else {}
                if PROTOCOL_DEBUG:
                    logger.debug(f"[OCPP-CALL-RECV] Action: {action}, ID: {message_id}")
                    logger.debug(f"[OCPP-PAYLOAD-RECV] {json.dumps(payload, indent=2, ensure_ascii=False)}")
                return message_type, message_id, action, payload
            elif message_type == OCPPMessage.CALLRESULT:
                payload = data[2] if len(data) > 2 else {}
                if PROTOCOL_DEBUG:
                    logger.debug(f"[OCPP-CALLRESULT-RECV] ID: {message_id}")
                    logger.debug(f"[OCPP-RESPONSE-RECV] {json.dumps(payload, indent=2, ensure_ascii=False)}")
                return message_type, message_id, "", payload
            elif message_type == OCPPMessage.CALLERROR:
                error_code = data[2]
                error_message = data[3] if len(data) > 3 else ""
                if PROTOCOL_DEBUG:
                    logger.debug(f"[OCPP-CALLERROR-RECV] ID: {message_id}")
                    logger.debug(f"[OCPP-ERROR-RECV] Code: {error_code}, Message: {error_message}")
                return message_type, message_id, error_code, {"errorMessage": error_message}
            else:
                raise ValueError(f"Unknown message type: {message_type}")
        except json.JSONDecodeError as e:
            raise ValueError(f"JSON decode error: {e}")


class OCPPv201RequestBuilder:
    """OCPP 2.0.1 요청 빌더"""

    @staticmethod
    def boot_notification(
        charger_model: str,
        charger_vendor: str,
        charger_serial: str = "CHARGER001",
        reason: str = "PowerUp"
    ) -> str:
        """부팅 알림 요청"""
        payload = {
            "reason": reason,
            "chargingStation": {
                "model": charger_model,
                "vendorName": charger_vendor,
                "serialNumber": charger_serial,
                "firmwareVersion": "1.0.0"
            }
        }
        return OCPPMessage.create_call("BootNotification", payload)

    @staticmethod
    def heartbeat() -> str:
        """하트비트 요청"""
        return OCPPMessage.create_call("Heartbeat", {})

    @staticmethod
    def status_notification(
        evse_id: int,
        connector_id: int,
        status: str = "Available"
    ) -> str:
        """상태 알림 요청"""
        payload = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "connectorStatus": status,
            "evseId": evse_id,
            "connectorId": connector_id
        }
        return OCPPMessage.create_call("StatusNotification", payload)

    @staticmethod
    def transaction_event(
        event_type: str,
        transaction_id: str,
        evse_id: int,
        connector_id: int,
        meter_value: float = 0.0,
        voltage: float = 400.0,
        current: float = 0.0
    ) -> str:
        """트랜잭션 이벤트 요청"""
        payload = {
            "eventType": event_type,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "transactionInfo": {
                "transactionId": transaction_id,
                "chargingState": "Charging"
            },
            "evseId": evse_id,
            "connectorId": connector_id,
            "meterValue": [
                {
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "sampledValue": [
                        {
                            "value": meter_value,
                            "context": "Sample.Periodic",
                            "measurand": "Energy.Active.Import.Register",
                            "unit": "kWh"
                        },
                        {
                            "value": voltage,
                            "measurand": "Voltage",
                            "unit": "V"
                        },
                        {
                            "value": current,
                            "measurand": "Current.Import",
                            "unit": "A"
                        }
                    ]
                }
            ]
        }
        return OCPPMessage.create_call("TransactionEvent", payload)

    @staticmethod
    def authorize(id_token: str) -> str:
        """인증 요청"""
        payload = {
            "idToken": {
                "idToken": id_token,
                "type": "Central"
            }
        }
        return OCPPMessage.create_call("Authorize", payload)
