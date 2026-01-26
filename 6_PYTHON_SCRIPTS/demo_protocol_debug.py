"""
OCPP 프로토콜 디버그 로깅 데모
프로토콜 수준의 상세 메시지를 확인할 수 있습니다.
"""
import asyncio
import logging
import os
from ocpp_server import OCPPServer
from charger_simulator import ChargerSimulator
from logging_config import setup_logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def main():
    """프로토콜 디버그 데모"""
    
    # 프로토콜 디버그 로깅 활성화
    os.environ['OCPP_PROTOCOL_DEBUG'] = 'true'
    
    # 로깅 설정
    setup_logging(
        level='DEBUG',
        enable_protocol_debug=True,
        log_file='ocpp_protocol_debug.log'
    )
    
    logger.info("=" * 70)
    logger.info("OCPP 2.0.1 프로토콜 디버그 데모 시작")
    logger.info("=" * 70)
    logger.info("이 데모는 모든 OCPP 메시지를 상세히 로깅합니다.")
    logger.info("로그 파일: ocpp_protocol_debug.log")
    logger.info("=" * 70)
    
    # 서버 생성 및 시작
    server = OCPPServer(host="localhost", port=9000)
    server_task = asyncio.create_task(server.start())
    
    # 서버가 시작될 때까지 대기
    await asyncio.sleep(1)
    
    # 충전기 생성
    charger = ChargerSimulator(
        charger_id="charger_debug_001",
        server_url="ws://localhost:9000",
        charger_model="Debug Charger",
        charger_vendor="TestVendor"
    )
    
    try:
        logger.info("\n[1] 충전기 연결 중...")
        await charger.connect()
        
        logger.info("\n연결 후 2초 대기 (부팅 알림 처리)...")
        await asyncio.sleep(2)
        
        logger.info("\n[2] 거래 시작 요청...")
        await server.request_start_transaction("charger_debug_001", evse_id=1, connector_id=1)
        
        logger.info("\n1초 대기...")
        await asyncio.sleep(1)
        
        logger.info("\n[3] 충전 시뮬레이션 (3초)...")
        charger.is_charging = True
        
        for i in range(3):
            await asyncio.sleep(1)
            logger.info(f"   충전 중... ({charger.meter_value:.2f} kWh)")
        
        logger.info("\n[4] 거래 중지 요청...")
        charger.is_charging = False
        await server.request_stop_transaction("charger_debug_001")
        
        logger.info("\n1초 대기...")
        await asyncio.sleep(1)
        
        logger.info("\n" + "=" * 70)
        logger.info("프로토콜 디버그 데모 완료!")
        logger.info("=" * 70)
        logger.info(f"\n로그 파일에서 다음 항목을 확인할 수 있습니다:")
        logger.info("  - [OCPP-CALL-SEND]   : 전송하는 Call 메시지")
        logger.info("  - [OCPP-PAYLOAD-SEND]: 전송 페이로드 (JSON)")
        logger.info("  - [OCPP-CALL-RECV]   : 수신하는 Call 메시지")
        logger.info("  - [OCPP-PAYLOAD-RECV]: 수신 페이로드 (JSON)")
        logger.info("  - [CHARGER-SEND]     : 충전기에서 전송하는 원본 메시지")
        logger.info("  - [CHARGER-RECV]     : 충전기가 수신하는 원본 메시지")
        logger.info("  - [SERVER-SEND]      : 서버에서 전송하는 원본 메시지")
        logger.info("  - [SERVER-RECV]      : 서버가 수신하는 원본 메시지")
        logger.info(f"\n자세한 내용은 'ocpp_protocol_debug.log' 파일을 확인하세요.")
        
    except KeyboardInterrupt:
        logger.info("\n사용자가 중단함")
    
    except Exception as e:
        logger.error(f"오류 발생: {e}", exc_info=True)
    
    finally:
        logger.info("\n정리 중...")
        await charger.disconnect()
        logger.info("프로그램 종료")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("프로그램 중단됨")
